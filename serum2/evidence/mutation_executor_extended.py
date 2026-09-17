"""PHASE E-0.1D.1 — EXTENDED MUTATION EXECUTOR

Dispatch mutations by type.
Enforce authoritative host-parameter binding.
Prove zero-mutation on refusal.
"""

from typing import Any, Dict, Optional, Tuple

from . import admission
from . import capability_contract as cc
from .mutation_request import MutationRequest, MutationType, MutationAuthorityProof
from serum2 import pathmerge


def execute_mutation_request_with_authority(
    request: MutationRequest,
    body: Dict[str, Any],
    contracts: Dict[Tuple[str, str], cc.CapabilityContract],
    synth: Optional[Any] = None,  # Instrumented synth for HOST_PARAMETER mutations
) -> MutationAuthorityProof:
    """
    THE UNIFIED MUTATION CHOKE POINT.

    Execute a Serum mutation ONLY after:
    1. admission.admit() returns ADMITTED
    2. Authoritative binding validation passes
    3. Mutation type dispatch succeeds

    Args:
        request: MutationRequest describing the desired mutation
        body: Serum state body (for BODY_STATE mutations)
        contracts: CapabilityContract registry
        synth: Instrumented synth object (for HOST_PARAMETER mutations)

    Returns:
        MutationAuthorityProof documenting authority check and execution

    Guarantees:
    - If admission_result.admitted == False → executed == False
    - If executed == False → no actual mutation occurred
    - If executed == True → state changed as requested
    """

    # Validate request structure
    is_valid, error = request.validate_for_type()
    if not is_valid:
        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            admission_result=admission.AdmissionResult(
                admitted=False,
                reason="invalid_mutation_request",
                detail=error or "Invalid request structure",
            ),
            executed=False,
        )

    # GATE 1: ADMISSION
    admission_result = admission.admit(
        contracts,
        request.target,
        required_causal=request.required_causal,
        required_persistence=request.required_persistence,
        required_measurement_definition_id=request.required_measurement_definition_id,
        proposed_prerequisites_verified=request.proposed_prerequisites_verified,
    )

    # If admission refuses, STOP. Zero mutation.
    if not admission_result.admitted:
        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            admission_result=admission_result,
            executed=False,
            set_parameter_call_count=0,
            pathmerge_call_count=0,
        )

    # GATE 1 PASSED: Admission is ADMITTED.
    contract = admission_result.contract
    if not contract:
        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            admission_result=admission_result,
            executed=False,
        )

    # GATE 2: TYPE DISPATCH
    # Each mutation type has different execution semantics.
    # All must go through admission first; all must validate authoritative binding.

    if request.mutation_type == MutationType.BODY_STATE:
        return _execute_body_state_mutation(request, body, contract, admission_result)

    elif request.mutation_type == MutationType.HOST_PARAMETER:
        if not synth:
            return MutationAuthorityProof(
                target=request.target,
                mutation_type=request.mutation_type,
                requested_value=request.value,
                admission_result=admission_result,
                executed=False,
                detail="HOST_PARAMETER requires synth object",
            )
        return _execute_host_parameter_mutation(request, synth, contract, admission_result)

    elif request.mutation_type == MutationType.TOPOLOGY:
        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            admission_result=admission_result,
            executed=False,
            detail="TOPOLOGY mutations not yet implemented",
        )

    elif request.mutation_type == MutationType.COMPOUND:
        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            admission_result=admission_result,
            executed=False,
            detail="COMPOUND mutations not yet implemented",
        )

    else:
        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            admission_result=admission_result,
            executed=False,
            detail=f"Unknown mutation type: {request.mutation_type}",
        )


def _execute_body_state_mutation(
    request: MutationRequest,
    body: Dict[str, Any],
    contract: cc.CapabilityContract,
    admission_result: admission.AdmissionResult,
) -> MutationAuthorityProof:
    """Execute BODY_STATE mutation via pathmerge.

    CRITICAL: Resolve binding from contract.execution_binding, not caller.
    Caller-supplied body_path is assertion-only (cross-check, not authority).
    """

    # AUTHORITATIVE BINDING: contract.execution_binding
    if not contract.execution_binding or contract.execution_binding.mutation_type != MutationType.BODY_STATE.value:
        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            body_path=request.body_path,
            admission_result=admission_result,
            executed=False,
            detail="No BODY_STATE execution binding in contract",
        )

    mutation_target_path = contract.execution_binding.body_path

    # Cross-check caller assertion if supplied
    if request.body_path and request.body_path != mutation_target_path:
        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            body_path=request.body_path,
            admission_result=admission_result,
            executed=False,
            detail=f"Body path mismatch: requested {request.body_path}, contract authorizes {mutation_target_path}",
        )

    if not mutation_target_path:
        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            body_path=request.body_path,
            admission_result=admission_result,
            executed=False,
        )

    # Capture baseline
    baseline_value = pathmerge.read_path_value(body, mutation_target_path)

    try:
        # Execute mutation (always count as 1 invocation, regardless of state change)
        pathmerge.apply_path_value(body, mutation_target_path, request.value)
        actual_call_count = 1  # We called apply_path_value() exactly once

        # Verify change (independent from invocation count)
        post_value = pathmerge.read_path_value(body, mutation_target_path)
        changed = (post_value != baseline_value)

        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            body_path=mutation_target_path,
            body_baseline_value=baseline_value,
            body_post_value=post_value,
            admission_result=admission_result,
            executed=True,
            mutation_succeeded=changed,
            pathmerge_call_count=actual_call_count,  # Always 1 when admission approved
        )

    except Exception as e:
        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            body_path=mutation_target_path,
            admission_result=admission_result,
            executed=False,
            detail=f"pathmerge error: {str(e)}",
        )


def _execute_host_parameter_mutation(
    request: MutationRequest,
    synth: Any,
    contract: cc.CapabilityContract,
    admission_result: admission.AdmissionResult,
) -> MutationAuthorityProof:
    """Execute HOST_PARAMETER mutation via synth.set_parameter().

    CRITICAL: Resolve binding from contract.execution_binding, not caller.
    Caller-supplied host_parameter_name is assertion-only (cross-check, not authority).
    """

    # AUTHORITATIVE BINDING: contract.execution_binding
    if not contract.execution_binding or contract.execution_binding.mutation_type != MutationType.HOST_PARAMETER.value:
        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            host_parameter_name=request.host_parameter_name,
            admission_result=admission_result,
            executed=False,
            detail="No HOST_PARAMETER execution binding in contract",
        )

    host_param_name = contract.execution_binding.host_parameter_name

    if not host_param_name:
        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            host_parameter_name=request.host_parameter_name,
            admission_result=admission_result,
            executed=False,
            detail="Contract execution_binding has no host_parameter_name",
        )

    # Cross-check caller assertion if supplied
    if request.host_parameter_name and request.host_parameter_name != host_param_name:
        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            host_parameter_name=request.host_parameter_name,
            admission_result=admission_result,
            executed=False,
            detail=f"Host parameter mismatch: requested {request.host_parameter_name}, contract authorizes {host_param_name}",
        )

    try:
        # Get parameter index
        params = synth.get_parameters_description()
        by_name = {p["name"]: p["index"] for p in params}

        if host_param_name not in by_name:
            return MutationAuthorityProof(
                target=request.target,
                mutation_type=request.mutation_type,
                requested_value=request.value,
                host_parameter_name=host_param_name,
                admission_result=admission_result,
                executed=False,
                detail=f"Host parameter not found: {host_param_name}",
            )

        param_idx = by_name[host_param_name]

        # Capture baseline
        baseline_value = synth.get_parameter(param_idx)

        # Execute mutation (always count as 1 invocation, regardless of state change)
        synth.set_parameter(param_idx, float(request.value))
        actual_call_count = 1  # We called set_parameter() exactly once

        # Verify change (independent from invocation count)
        post_value = synth.get_parameter(param_idx)
        changed = (post_value != baseline_value)

        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            host_parameter_name=host_param_name,
            host_baseline_value=baseline_value,
            host_post_value=post_value,
            admission_result=admission_result,
            executed=True,
            mutation_succeeded=changed,
            set_parameter_call_count=actual_call_count,  # Always 1 when admission approved
        )

    except Exception as e:
        return MutationAuthorityProof(
            target=request.target,
            mutation_type=request.mutation_type,
            requested_value=request.value,
            host_parameter_name=host_param_name,
            admission_result=admission_result,
            executed=False,
            detail=f"set_parameter error: {str(e)}",
        )

