"""Derive a CapabilityBinding (authoritative_binding + status) for a
resolved (semantic_id, execution_family) pair.

Continues work items 5/6 down to a concrete binding, and feeds work item 4's
canonical dedup key.

Precedence (highest confidence first):
  1. An existing, real CapabilityContract with execution_binding (D.1.1/D.1.2
     work -- currently Release/Attack only) -- LIVE_VERIFIED, strongest.
  2. Live re-verification against the CURRENT DawDreamer parameter list for
     HOST_PARAMETER targets with a claimed host_parameter_name -- matches
     Execution Coverage V1's method exactly.
  3. NOT_YET_DERIVED for everything else (BODY_STATE/MATRIX_ROUTE/
     STRUCTURAL/RESOURCE target vocabulary mutation_path is UNKNOWN for all
     396 targets as of V4 -- honestly recorded, not guessed).
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from .schema import ExecutionFamily, MutationPrimitive, FAMILY_TO_PRIMITIVE, BindingStatus, CapabilityBinding
from .canonicalize import canonicalize_host_parameter, compute_capability_id
from .operation_registry import operation_key_for


def derive_binding(
    execution_family: ExecutionFamily,
    target_record: Optional[Dict[str, Any]],
    live_vst3_param_names: set,
    capability_key: Optional[str],
    qualified_contracts: Dict[str, Any],  # capability_key -> CapabilityContract
) -> CapabilityBinding:
    mutation_type = FAMILY_TO_PRIMITIVE[execution_family].value
    operation_key = operation_key_for(mutation_type)

    # Precedence 1: a real, already-qualified contract with execution_binding
    contract = qualified_contracts.get(capability_key) if capability_key else None
    if contract is not None and getattr(contract, "execution_binding", None) is not None:
        eb = contract.execution_binding
        if eb.mutation_type == "HOST_PARAMETER" and eb.host_parameter_name:
            canonical = canonicalize_host_parameter(eb.host_parameter_name)
            cap_id = compute_capability_id(execution_family.value, canonical)
            return CapabilityBinding(
                capability_id=cap_id,
                execution_family=execution_family.value,
                mutation_type=mutation_type,
                operation_key=operation_key,
                authoritative_binding=canonical,
                binding_status=BindingStatus.LIVE_VERIFIED.value,
                binding_provenance=f"CapabilityContract.execution_binding "
                                    f"(source={eb.binding_source}, version={eb.binding_version})",
                binding_version=eb.binding_version,
            )
        # BODY_STATE contracts (e.g. if a future contract carries one) --
        # not present today (Release/Attack are both HOST_PARAMETER via
        # ContractRegistry's D.1.2 derivation) but handled for completeness.
        if eb.mutation_type == "BODY_STATE" and eb.body_path:
            from .canonicalize import canonicalize_body_state
            canonical = canonicalize_body_state(eb.body_path)
            cap_id = compute_capability_id(execution_family.value, canonical)
            return CapabilityBinding(
                capability_id=cap_id,
                execution_family=execution_family.value,
                mutation_type=mutation_type,
                operation_key=operation_key,
                authoritative_binding=canonical,
                binding_status=BindingStatus.LIVE_VERIFIED.value,
                binding_provenance=f"CapabilityContract.execution_binding "
                                    f"(source={eb.binding_source}, version={eb.binding_version})",
                binding_version=eb.binding_version,
            )

    # Precedence 2: live-verify a claimed host_parameter_name (V1 method)
    if execution_family == ExecutionFamily.HOST_PARAMETER and target_record is not None:
        claimed_name = target_record.get("host_parameter_name")
        if claimed_name not in (None, "UNKNOWN"):
            if claimed_name in live_vst3_param_names:
                canonical = canonicalize_host_parameter(claimed_name)
                cap_id = compute_capability_id(execution_family.value, canonical)
                return CapabilityBinding(
                    capability_id=cap_id,
                    execution_family=execution_family.value,
                    mutation_type=mutation_type,
                    operation_key=operation_key,
                    authoritative_binding=canonical,
                    binding_status=BindingStatus.LIVE_VERIFIED.value,
                    binding_provenance="live_dawdreamer_parameter_list (this run)",
                    binding_version=None,
                )
            return CapabilityBinding(
                capability_id=None,
                execution_family=execution_family.value,
                mutation_type=mutation_type,
                operation_key=operation_key,
                authoritative_binding=None,
                binding_status=BindingStatus.NOT_YET_DERIVED.value,
                binding_provenance=f"claimed host_parameter_name {claimed_name!r} "
                                    f"NOT found in live parameter list -- claim stale/unverified",
                binding_version=None,
            )

    # Precedence 3: honest gap -- family known, no binding derivable yet
    return CapabilityBinding(
        capability_id=None,
        execution_family=execution_family.value,
        mutation_type=mutation_type,
        operation_key=operation_key,
        authoritative_binding=None,
        binding_status=BindingStatus.NOT_YET_DERIVED.value,
        binding_provenance=None,
        binding_version=None,
    )
