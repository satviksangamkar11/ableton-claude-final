"""SerumOperation data model.

A SerumOperation is a human-facing synthesis operation that compiles to
one or more state mutations using the existing Mutation representation.

Kinds:

SCALAR
  - Direct parameter value change (float, int, string)
  - Compiles to: single Mutation(path, value)
  - Examples: LFO0.Rate, Filter.Cutoff, Env1.Attack

STATE
  - Direct state field change (nested dict, resource path)
  - Compiles to: single Mutation(path, value)
  - Examples: Oscillator0.Type (dict replacement), Wavetable path

COMPOUND
  - Multiple related mutations under one semantic operation
  - Compiles to: Mutation[] with conflict checking
  - Examples: Modulation.Create, Oscillator.Type.Select, Macro.Assign

RESOURCE
  - Resource resolution + path mutation
  - Compiles to: resource_resolver + Mutation(path_to_resource)
  - Examples: Load.Wavetable, Load.Sample

TOPOLOGY
  - Enables/disables or reorders structural elements
  - Compiles to: Mutation[] with enable/disable semantics
  - Examples: Enable.Oscillator2, Reorder.FX, Enable.Filter

Authority: SerumOperation describes WHAT to do, not WHETHER to do it.
Authority remains in serum2.evidence.admission.AdmissionResult.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum


class OperationKind(Enum):
    """Categories of Serum operations."""
    SCALAR = "scalar"                 # single scalar parameter
    STATE = "state"                   # direct state field
    COMPOUND = "compound"             # multiple coordinated mutations
    RESOURCE = "resource"             # resource resolution + mutation
    TOPOLOGY = "topology"             # enable/disable/reorder


@dataclass(frozen=True)
class OperationParameter:
    """One input parameter to a SerumOperation."""
    name: str                         # e.g. "lfo_index", "amount", "target_param"
    value: Any                        # runtime value
    required: bool = True
    description: str = ""


@dataclass(frozen=True)
class SerumOperation:
    """A human-facing Serum operation that compiles to state mutations.

    This is a PLANNING/COMPILER abstraction, not an execution backend.
    The producer uses this to express intent; the compiler turns it into
    mutations that the existing harness.render_arm() will execute.
    """

    # Identity
    operation_id: str                 # e.g. "lfo_rate_set", "mod_route_create"
    semantic_name: str                # human-readable: "Set LFO 0 rate", etc.

    # Classification
    kind: OperationKind               # SCALAR | STATE | COMPOUND | RESOURCE | TOPOLOGY

    # Input
    parameters: List[OperationParameter] = field(default_factory=list)

    # Context
    semantic_target: Optional[str] = None  # reference to SEMANTIC_TARGETS vocab
    musical_context: Optional[str] = None  # e.g. "bass patch", "pad texture"

    # Measurement
    measurement_metric: Optional[str] = None  # how to verify effect: "tail_rms_db", "spectral_centroid", etc.
    expected_direction: Optional[str] = None  # "increase", "decrease", "presence", "none"

    # Metadata
    requires_context: Dict[str, Any] = field(default_factory=dict)  # prereqs
    requires_resource: Optional[str] = None  # "wavetable" | "sample" | None
    requires_list_index: Optional[int] = None  # for array-like state (FX slots, LFOs)

    notes: str = ""


@dataclass(frozen=True)
class OperationResult:
    """Outcome of a SerumOperation compilation.

    Either compiled_mutations is populated (success) or
    compilation_error is populated (failure).
    """

    operation_id: str
    success: bool

    # On success:
    compiled_mutations: List[Any] = field(default_factory=list)  # Mutation objects
    mutation_description: str = ""

    # On failure:
    compilation_error: Optional[str] = None
    error_detail: str = ""

    # Metadata
    notes: str = ""


@dataclass(frozen=True)
class OperationContext:
    """Runtime context for operation compilation.

    Provides access to current state, indexed structures, and validation.
    """

    body: Dict[str, Any]                      # current v8 state body
    skeleton: Optional[Dict[str, Any]] = None # v8 skeleton for defaults
    available_resources: Dict[str, Any] = field(default_factory=dict)

    # Index resolution (for list-indexed operations like FX, LFOs)
    list_indices: Dict[str, int] = field(default_factory=dict)  # "FX.Chorus" → 2, etc.
