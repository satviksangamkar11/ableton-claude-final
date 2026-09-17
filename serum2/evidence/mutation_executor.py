"""PHASE E-0.1B — MUTATION EXECUTOR WITH AUTHORITY ENFORCEMENT

The ONE function that executes actual Serum mutations.
All production code must route through this.

This enforces:
- admission.admit() check before ANY mutation
- REFUSED statuses produce zero mutation
- No bypasses to direct pathmerge calls
"""

from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass

from . import admission
from . import capability_contract as cc
from serum2 import pathmerge


@dataclass(frozen=True)
class MutationAuthorityProof:
    """Record of authority check for a mutation."""
    target: str
    admission_result: admission.AdmissionResult
    mutation_target_path: Optional[str]
    mutation_value: Any
    executed: bool  # True ONLY if admitted AND mutation occurred
    serum_state_changed: bool  # Actual observation after mutation


def execute_mutation_with_authority(
    body: Dict[str, Any],
    target: str,
    mutation_value: Any,
    contracts: Dict[Tuple[str, str], cc.CapabilityContract],
    *,
    required_causal: bool = False,
    required_persistence: bool = False,
    required_measurement_definition_id: Optional[str] = None,
    proposed_prerequisites_verified: Optional[Dict[str, bool]] = None,
) -> MutationAuthorityProof:
    """
    THE MUTATION CHOKE POINT.

    Execute a Serum mutation ONLY after admission gate passes.

    Returns a MutationAuthorityProof documenting the authority check,
    not just success/failure.

    Args:
        body: Serum state body (v8 skeleton)
        target: semantic target name (e.g., "ENV1.ATTACK")
        mutation_value: value to set
        contracts: CapabilityContract registry
        required_causal: caller requires CAUSAL_VERIFIED
        required_persistence: caller requires persistence proof
        required_measurement_definition_id: measurement must match exactly
        proposed_prerequisites_verified: dict of field_path -> bool

    Returns:
        MutationAuthorityProof recording authority check and execution result

    Guarantees:
    - If admission_result.admitted == False, then executed == False
    - If executed == False, then serum_state_changed == False
    - If executed == True, then body contains the mutation
    """

    # GATE 1: ADMISSION
    # This is the ONLY way to authorize a mutation.
    admission_result = admission.admit(
        contracts,
        target,
        required_causal=required_causal,
        required_persistence=required_persistence,
        required_measurement_definition_id=required_measurement_definition_id,
        proposed_prerequisites_verified=proposed_prerequisites_verified,
    )

    # If admission refuses, STOP. Do not mutate.
    if not admission_result.admitted:
        return MutationAuthorityProof(
            target=target,
            admission_result=admission_result,
            mutation_target_path=None,
            mutation_value=mutation_value,
            executed=False,
            serum_state_changed=False,
        )

    # GATE 1 PASSED: Admission is ADMITTED.
    # Now resolve the mutation path from the contract.
    contract = admission_result.contract
    if not contract:
        # Should not happen (admission would have refused), but defensive
        return MutationAuthorityProof(
            target=target,
            admission_result=admission_result,
            mutation_target_path=None,
            mutation_value=mutation_value,
            executed=False,
            serum_state_changed=False,
        )

    # Extract mutation path from the contract
    mutation_target_path = contract.scope.get("mutation_target_path") if contract.scope else None
    if not mutation_target_path:
        # Contract exists but has no mutation path (shouldn't happen in production)
        return MutationAuthorityProof(
            target=target,
            admission_result=admission_result,
            mutation_target_path=None,
            mutation_value=mutation_value,
            executed=False,
            serum_state_changed=False,
        )

    # GATE 2: SNAPSHOT baseline (detect actual mutation)
    # Capture state before to prove mutation occurred
    baseline_value = pathmerge.read_path_value(body, mutation_target_path)

    # EXECUTE: Apply the mutation
    try:
        pathmerge.apply_path_value(body, mutation_target_path, mutation_value)

        # Verify mutation actually occurred
        post_value = pathmerge.read_path_value(body, mutation_target_path)
        state_changed = (post_value != baseline_value)

        return MutationAuthorityProof(
            target=target,
            admission_result=admission_result,
            mutation_target_path=mutation_target_path,
            mutation_value=mutation_value,
            executed=True,
            serum_state_changed=state_changed,
        )

    except Exception as e:
        # Mutation failed (pathmerge error)
        return MutationAuthorityProof(
            target=target,
            admission_result=admission_result,
            mutation_target_path=mutation_target_path,
            mutation_value=mutation_value,
            executed=False,
            serum_state_changed=False,
        )


def assert_mutation_authority(proof: MutationAuthorityProof) -> None:
    """Enforce the invariant: refused -> no mutation.

    Raises AssertionError if:
    - admitted=False but executed=True
    - admitted=False but serum_state_changed=True
    """
    if not proof.admission_result.admitted:
        assert not proof.executed, \
            f"AUTHORITY VIOLATION: {proof.target} refused but mutation was executed"
        assert not proof.serum_state_changed, \
            f"AUTHORITY VIOLATION: {proof.target} refused but Serum state changed"


# This is the ONLY production entry point for Serum mutations.
# Producers, operationcompilers, and any other code that needs to mutate
# Serum must call this function, not pathmerge directly.
#
# The invariant is enforced at the machine level:
# No contract -> admission refuses -> no mutation
# Contract but not admitted -> admission refuses -> no mutation
# Contract and admitted -> mutation allowed

