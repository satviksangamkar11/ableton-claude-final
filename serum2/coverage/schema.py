"""V2 schema: enums, SemanticResolution, CapabilityBinding, and the
invariant validators that make the ontology separation real rather than
documentation-only.

Work items 1-3 of the Execution Coverage V2 milestone.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Tuple


# ---------------------------------------------------------------------------
# Dimension B: resolution state (work item 3)
# ---------------------------------------------------------------------------
class ExecutionResolution(str, Enum):
    """Has this semantic row been resolved to a known execution family?

    RESOLVED here means: we know WHICH execution_family/mutation_type/
    operation_key this capability belongs to (matching the already-frozen
    Phase D family registry's execution_class for 513/908 rows: BODY_STATE_
    FIELD, HOST_PARAMETER, MATRIX_ROUTE, RESOURCE_OPERATION,
    STRUCTURAL_OPERATION). It does NOT by itself mean a concrete
    authoritative_binding has been derived or live-verified -- that is a
    separate, additional fact recorded on CapabilityBinding.binding_status.
    A RESOLVED family with no derivable binding yet still yields
    capability_id=None (see CapabilityBinding.is_bound).
    """
    RESOLVED = "RESOLVED"
    UNRESOLVED_UI_ACTION = "UNRESOLVED_UI_ACTION"
    UNKNOWN_EXECUTION = "UNKNOWN_EXECUTION"


# ---------------------------------------------------------------------------
# Dimension A: execution family
# ---------------------------------------------------------------------------
class ExecutionFamily(str, Enum):
    HOST_PARAMETER = "HOST_PARAMETER"
    BODY_STATE_FIELD = "BODY_STATE_FIELD"
    MATRIX_ROUTE = "MATRIX_ROUTE"
    RESOURCE_OPERATION = "RESOURCE_OPERATION"
    STRUCTURAL_OPERATION = "STRUCTURAL_OPERATION"


# ---------------------------------------------------------------------------
# Dimension C: mutation primitive (what the executor dispatches on)
# ---------------------------------------------------------------------------
class MutationPrimitive(str, Enum):
    SCALAR = "SCALAR"
    STATE = "STATE"
    COMPOUND = "COMPOUND"
    TOPOLOGY = "TOPOLOGY"
    RESOURCE = "RESOURCE"


# Family -> primitive is a fixed, frozen mapping (not per-row data).
FAMILY_TO_PRIMITIVE: Dict[ExecutionFamily, MutationPrimitive] = {
    ExecutionFamily.HOST_PARAMETER: MutationPrimitive.SCALAR,
    ExecutionFamily.BODY_STATE_FIELD: MutationPrimitive.STATE,
    ExecutionFamily.MATRIX_ROUTE: MutationPrimitive.COMPOUND,
    ExecutionFamily.STRUCTURAL_OPERATION: MutationPrimitive.TOPOLOGY,
    ExecutionFamily.RESOURCE_OPERATION: MutationPrimitive.RESOURCE,
}


class BindingType(str, Enum):
    HOST_PARAMETER = "HOST_PARAMETER"
    BODY_STATE = "BODY_STATE"
    FX_PARAMETER = "FX_PARAMETER"       # BODY_STATE sub-kind: identity is
                                         # (effect, parameter); rack/slot is
                                         # runtime placement (request payload,
                                         # via the fx_set_parameter resolver),
                                         # never part of capability identity
    MATRIX_ROUTE = "MATRIX_ROUTE"
    TOPOLOGY = "TOPOLOGY"
    RESOURCE = "RESOURCE"


class BindingStatus(str, Enum):
    """Independent of execution_resolution -- tracks whether a concrete
    authoritative_binding has actually been derived/verified for a
    RESOLVED family, or whether only the family is known so far."""
    NOT_YET_DERIVED = "NOT_YET_DERIVED"
    DERIVED_UNVERIFIED = "DERIVED_UNVERIFIED"
    LIVE_VERIFIED = "LIVE_VERIFIED"


# ---------------------------------------------------------------------------
# SemanticResolution (work item 1)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SemanticResolution:
    semantic_id: str
    technical_target_id: Optional[str]   # nullable: 0 or 1 technical target
    execution_resolution: str            # ExecutionResolution value
    resolution_provenance: str           # where this resolution came from
    resolution_reason: str               # why this resolution was assigned

    def __post_init__(self):
        if self.execution_resolution not in (e.value for e in ExecutionResolution):
            raise ValueError(f"invalid execution_resolution: {self.execution_resolution!r}")


# ---------------------------------------------------------------------------
# CapabilityBinding (work item 2)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CapabilityBinding:
    """Canonical executable capability. Deduplicated across semantic rows.

    capability_id is None whenever binding_status != LIVE_VERIFIED-or-
    DERIVED_UNVERIFIED-with-a-real-binding-object -- i.e. whenever there is
    no concrete authoritative_binding yet, even if execution_family is
    already known (RESOLVED family, unbound capability).
    """
    capability_id: Optional[str]
    execution_family: Optional[str]      # ExecutionFamily value, or None
    mutation_type: Optional[str]         # MutationPrimitive value, or None
    operation_key: Optional[str]         # generic dispatcher import path, or None
    authoritative_binding: Optional[Dict[str, Any]]   # canonical binding object, or None
    binding_status: str                  # BindingStatus value
    binding_provenance: Optional[str]
    binding_version: Optional[str]

    def is_bound(self) -> bool:
        return self.capability_id is not None


# ---------------------------------------------------------------------------
# Invariant validators (work items 1-3 enforcement)
# ---------------------------------------------------------------------------
class InvariantViolation(Exception):
    pass


def validate_v2_1_resolution_gate(resolution: SemanticResolution,
                                    binding: Optional[CapabilityBinding]) -> None:
    """V2-1: UNRESOLVED rows carry no execution family / primitive / operation / binding."""
    if resolution.execution_resolution != ExecutionResolution.RESOLVED.value:
        if binding is not None and (
            binding.execution_family is not None
            or binding.mutation_type is not None
            or binding.operation_key is not None
            or binding.authoritative_binding is not None
        ):
            raise InvariantViolation(
                f"V2-1 violated for {resolution.semantic_id}: "
                f"execution_resolution={resolution.execution_resolution!r} but "
                f"binding fields are populated: {binding!r}"
            )


def validate_v2_3_generic_operation_key(operation_key: Optional[str],
                                          generic_executors: Dict[str, Optional[str]]) -> None:
    """V2-3: operation_key must be one of the fixed set of generic,
    primitive-level dispatchers -- never a target-specific function name."""
    if operation_key is None:
        return
    valid_keys = set(k for k in generic_executors.values() if k is not None)
    if operation_key not in valid_keys:
        raise InvariantViolation(
            f"V2-3 violated: operation_key={operation_key!r} is not one of the "
            f"registered generic executors {sorted(valid_keys)}"
        )


def validate_family_primitive_consistency(execution_family: Optional[str],
                                            mutation_type: Optional[str]) -> None:
    """mutation_type must match the frozen FAMILY_TO_PRIMITIVE mapping -- it
    is derived, never independently chosen per row."""
    if execution_family is None:
        if mutation_type is not None:
            raise InvariantViolation(
                f"mutation_type={mutation_type!r} set without execution_family"
            )
        return
    expected = FAMILY_TO_PRIMITIVE.get(ExecutionFamily(execution_family))
    if expected is None:
        raise InvariantViolation(f"unknown execution_family: {execution_family!r}")
    if mutation_type != expected.value:
        raise InvariantViolation(
            f"family/primitive mismatch: {execution_family!r} must map to "
            f"{expected.value!r}, got mutation_type={mutation_type!r}"
        )
