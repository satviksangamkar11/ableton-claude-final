"""Family derivation: two evidence paths, gated on whether a technical
target exists for a semantic row.

Work items 5 and 6 of the Execution Coverage V2 milestone.

  target exists  -> target vocabulary evidence is primary (parameter_kind,
                     target_source from SERUM2_TARGET_NORMALIZED_V4.json)
  target absent  -> semantic execution evidence is primary (this session
                     REUSES the already-frozen Phase D family registry's
                     execution_class per semantic_id -- not a re-derivation,
                     not reopened semantic discovery)
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple

from .schema import ExecutionFamily, ExecutionResolution, FAMILY_TO_PRIMITIVE

# Phase D execution_class -> V2 (execution_resolution, execution_family)
# RESOLVED classes carry a family; UI_ACTION/UNKNOWN_EXECUTION do not (V2-1).
PHASE_D_CLASS_TO_V2 = {
    "HOST_PARAMETER": (ExecutionResolution.RESOLVED, ExecutionFamily.HOST_PARAMETER),
    "BODY_STATE_FIELD": (ExecutionResolution.RESOLVED, ExecutionFamily.BODY_STATE_FIELD),
    "MATRIX_ROUTE": (ExecutionResolution.RESOLVED, ExecutionFamily.MATRIX_ROUTE),
    "RESOURCE_OPERATION": (ExecutionResolution.RESOLVED, ExecutionFamily.RESOURCE_OPERATION),
    "STRUCTURAL_OPERATION": (ExecutionResolution.RESOLVED, ExecutionFamily.STRUCTURAL_OPERATION),
    "UI_ACTION": (ExecutionResolution.UNRESOLVED_UI_ACTION, None),
    "UNKNOWN_EXECUTION": (ExecutionResolution.UNKNOWN_EXECUTION, None),
}


def derive_family_target_linked(target_record: Dict[str, Any]) -> Optional[ExecutionFamily]:
    """Primary evidence: the 396-target vocabulary's own parameter_kind /
    target_source, exactly as used in Execution Coverage V1."""
    parameter_kind = target_record.get("parameter_kind")
    target_source = target_record.get("target_source")

    if parameter_kind == "VST3_HOST_FIELD":
        return ExecutionFamily.HOST_PARAMETER
    if parameter_kind == "VST3_PLAIN_PARAM":
        return ExecutionFamily.BODY_STATE_FIELD
    if parameter_kind == "ROUTING_SLOT_FIELD" or target_source == "MATRIX_ROUTE":
        return ExecutionFamily.MATRIX_ROUTE
    return None


def derive_resolution_target_less(phase_d_execution_class: Optional[str]
                                    ) -> Tuple[ExecutionResolution, Optional[ExecutionFamily]]:
    """Primary evidence: Phase D's SERUM2_EXECUTION_FAMILY_REGISTRY_FINAL.json
    execution_class for this semantic_id (frozen, reused -- not redone)."""
    if phase_d_execution_class not in PHASE_D_CLASS_TO_V2:
        return ExecutionResolution.UNKNOWN_EXECUTION, None
    return PHASE_D_CLASS_TO_V2[phase_d_execution_class]


def derive(technical_target_id: Optional[str], target_record: Optional[Dict[str, Any]],
           phase_d_execution_class: Optional[str]
           ) -> Tuple[ExecutionResolution, Optional[ExecutionFamily], str, str]:
    """Top-level derivation dispatch. Returns
    (execution_resolution, execution_family, provenance, reason)."""

    if technical_target_id is not None and target_record is not None:
        family = derive_family_target_linked(target_record)
        if family is not None:
            return (
                ExecutionResolution.RESOLVED, family,
                "target_vocabulary:SERUM2_TARGET_NORMALIZED_V4.json",
                f"parameter_kind={target_record.get('parameter_kind')!r} "
                f"target_source={target_record.get('target_source')!r} "
                f"(target-linked path, target evidence primary)",
            )
        # Target exists but its structural fields don't match a known
        # family shape -- fall through to semantic evidence rather than
        # silently guessing.

    resolution, family = derive_resolution_target_less(phase_d_execution_class)
    provenance = "phase_d_family_registry:SERUM2_EXECUTION_FAMILY_REGISTRY_FINAL.json"
    if phase_d_execution_class is None:
        reason = "no Phase D execution_class found for this semantic_id (not in 908-row registry)"
    else:
        reason = (f"Phase D execution_class={phase_d_execution_class!r} "
                  f"(target-less path, semantic evidence primary)")
    return resolution, family, provenance, reason
