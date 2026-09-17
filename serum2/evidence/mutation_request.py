"""PHASE E-0.1D.1 — MUTATION REQUEST + TYPE DISPATCH

Authorized mutation abstraction with type-safe dispatch.
Replaces implicit body_path/value extraction with explicit MutationRequest.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class MutationType(str, Enum):
    """Semantic mutation type categories."""
    BODY_STATE = "BODY_STATE"           # Direct Serum state field mutation
    HOST_PARAMETER = "HOST_PARAMETER"   # VST3 host parameter mutation
    TOPOLOGY = "TOPOLOGY"               # FX/module enable/disable/reorder
    COMPOUND = "COMPOUND"               # Multi-target coordinated mutation
    RESOURCE = "RESOURCE"               # Resource resolution + mutation (wavetable/sample load)
    META_STRING = "META_STRING"         # .SerumPreset meta-dict field (presetName/presetAuthor/presetDescription/tags)


@dataclass(frozen=True)
class MutationRequest:
    """
    Authorized mutation request.
    Describes WHAT to mutate and WHY (contract authority).
    Does NOT describe HOW (executor owns execution).

    Immutable: cannot be modified after creation.
    """

    # Semantic identity
    target: str                         # e.g., "ENV1.RELEASE", "OSC1.LEVEL"
    mutation_type: MutationType         # BODY_STATE, HOST_PARAMETER, etc
    value: Any                          # The requested value

    # BODY_STATE mutation path
    # ASSERTION ONLY: Cross-check against contract.execution_binding.body_path
    # Contract is authoritative source of truth, not caller
    body_path: Optional[str] = None     # e.g., "Envelope0.plainParams.kParamRelease"

    # HOST_PARAMETER mutation target
    # ASSERTION ONLY: Cross-check against contract.execution_binding.host_parameter_name
    # Contract is authoritative source of truth; caller assertion for verification only
    # Executor will REFUSE if mismatch between request.host_parameter_name and contract binding
    host_parameter_name: Optional[str] = None  # e.g., "Env 1 Release"

    # META_STRING mutation target
    # ASSERTION ONLY: Cross-check against contract.execution_binding.meta_path
    meta_path: Optional[str] = None     # e.g., "presetName"

    # BODY_STATE resolver payload (used only when
    # contract.execution_binding.resolver_operation_id is set). This is
    # PAYLOAD, not authority: WHICH resolver runs is contract-derived
    # (resolver_operation_id); these are the resolver's own input
    # parameters (e.g. {"rack": 0, "slot": 1, "effect": "EQ",
    # "parameter": "Freq1", "value": 500.0}), analogous to `value` above.
    # The resolver's own validation (range checks, unknown-parameter
    # rejection) is what makes an invalid payload REFUSE -- there is no
    # contract-side value to cross-check these against.
    resolver_parameters: Optional[Dict[str, Any]] = None

    # Authority requirements
    required_causal: bool = False
    required_persistence: bool = False
    required_measurement_definition_id: Optional[str] = None
    proposed_prerequisites_verified: Optional[Dict[str, bool]] = None

    # Contract reference (for authority trace)
    contract_id: Optional[str] = None

    def validate_for_type(self) -> tuple[bool, Optional[str]]:
        """Validate request structure.

        NOTE: body_path and host_parameter_name are ASSERTIONS ONLY, not required.
        Contract.execution_binding provides the authoritative binding.
        Caller assertion is optional; executor will cross-check if supplied.

        TOPOLOGY and COMPOUND pass validation and are refused at executor dispatch.
        """
        # All mutation types are structurally valid at this layer.
        # Executor dispatch handles type-specific refusals (TOPOLOGY/COMPOUND not yet implemented).
        return True, None


@dataclass(frozen=True)
class MutationAuthorityProof:
    """Record of authority check and execution for a mutation."""

    # Request identity
    target: str
    mutation_type: MutationType
    requested_value: Any

    # Authority result
    admission_result: Any  # AdmissionResult

    # Execution record (BODY_STATE)
    body_path: Optional[str] = None
    body_baseline_value: Optional[Any] = None
    body_post_value: Optional[Any] = None

    # Execution record (HOST_PARAMETER)
    host_parameter_name: Optional[str] = None
    host_baseline_value: Optional[Any] = None
    host_post_value: Optional[Any] = None

    # Execution record (META_STRING)
    meta_path: Optional[str] = None
    meta_baseline_value: Optional[Any] = None
    meta_post_value: Optional[Any] = None

    # Execution metrics
    executed: bool = False              # Mutation was attempted
    mutation_succeeded: bool = False    # Value changed as requested
    set_parameter_call_count: int = 0   # Number of synth.set_parameter() calls
    pathmerge_call_count: int = 0       # Number of pathmerge.apply_path_value() calls

    # Failure detail
    detail: Optional[str] = None        # Error message if execution failed

    def is_refused(self) -> bool:
        """True if admission refused this mutation."""
        return not self.admission_result.admitted

    def is_executed_and_changed(self) -> bool:
        """True if mutation was executed AND state changed."""
        return self.executed and self.mutation_succeeded

