"""OperationRegistry: central catalog of all Serum operations.

Each OperationDefinition describes:
- semantic name and identity
- what kind of operation (SCALAR, COMPOUND, RESOURCE, etc.)
- required input parameters
- how to compile it to Mutation[]
- measurement verification strategy
- resource requirements

The registry is the producer's control vocabulary.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any

from .model import OperationKind, OperationParameter, SerumOperation


@dataclass(frozen=True)
class OperationDefinition:
    """Template for one category of Serum operation.

    This is a SCHEMA, not an instance. Instances are SerumOperation objects.
    """

    operation_id: str                         # "lfo_rate_set", "mod_route_create", etc.
    semantic_name: str                        # "Set LFO Rate", "Create Modulation Route"
    kind: OperationKind

    # What parameters does this operation require?
    parameters: List[OperationParameter] = field(default_factory=list)

    # Which measurement kernel validates this operation?
    measurement_metric: Optional[str] = None  # "modulation_frequency_hz", "tail_rms_db", etc.
    expected_direction: Optional[str] = None  # "increase", "decrease", "presence"

    # Does this operation require resources?
    resource_kind: Optional[str] = None       # "wavetable", "sample", None

    # Does this require structural context verification?
    requires_list_index: bool = False
    requires_module_presence: Optional[str] = None  # e.g., "FXRack0.FX[EQ]"

    # Compiler function (set by registry.register_compiler)
    compiler_fn: Optional[Callable] = None

    description: str = ""


class OperationRegistry:
    """Central registry of all Serum operations.

    Populated by:
    1. Built-in scalar/state operations (auto-generated from SEMANTIC_TARGETS)
    2. Structured compound operations (manually defined)
    3. Resource operations (wavetable, sample loaders)
    4. Topology operations (enable/disable, reorder)
    """

    def __init__(self):
        """Initialize empty registry."""
        self._operations: Dict[str, OperationDefinition] = {}
        self._compilers: Dict[str, Callable] = {}

    def register(self, definition: OperationDefinition) -> None:
        """Register an operation definition."""
        if definition.operation_id in self._operations:
            raise ValueError(f"Operation {definition.operation_id} already registered")
        self._operations[definition.operation_id] = definition

    def register_compiler(
        self,
        operation_id: str,
        compiler_fn: Callable,
    ) -> None:
        """Register a compiler function for an operation.

        The function signature is:
          compiler_fn(operation: SerumOperation, ctx: OperationContext) -> OperationResult

        The compiler translates the operation and its parameters into Mutation[].
        """
        if operation_id not in self._operations:
            raise ValueError(f"Cannot register compiler for unknown operation {operation_id}")
        self._compilers[operation_id] = compiler_fn

    def get(self, operation_id: str) -> Optional[OperationDefinition]:
        """Retrieve an operation definition."""
        return self._operations.get(operation_id)

    def get_compiler(self, operation_id: str) -> Optional[Callable]:
        """Retrieve a compiler function."""
        return self._compilers.get(operation_id)

    def all_operations(self) -> Dict[str, OperationDefinition]:
        """Return all registered operations."""
        return dict(self._operations)

    def operations_by_kind(self, kind: OperationKind) -> List[OperationDefinition]:
        """Filter operations by kind."""
        return [op for op in self._operations.values() if op.kind == kind]

    def semantic_names(self) -> List[str]:
        """Return human-readable names of all operations."""
        return [op.semantic_name for op in self._operations.values()]


# Global singleton registry (populated by __init__.py imports at module load)
_global_registry: Optional[OperationRegistry] = None


def get_registry() -> OperationRegistry:
    """Get the global operation registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = OperationRegistry()
        # Auto-populate with built-in operations
        _populate_builtin_operations(_global_registry)
    return _global_registry


def _populate_builtin_operations(registry: OperationRegistry) -> None:
    """Populate the registry with built-in operations.

    Called once at module initialization.
    Phase 2: scalar operations from SEMANTIC_TARGETS
    Phase 3: compound operations (modulation, macro)
    """
    # Phase 2: auto-generate scalar operations from SEMANTIC_TARGETS
    from .scalar_operations import build_scalar_operations_from_targets
    build_scalar_operations_from_targets(registry)

    # Phase 3: compound operations
    from .compound_operations import (
        compiler_create_modulation_route,
        compiler_delete_modulation_route,
        compiler_set_macro_value,
        compiler_rename_macro,
    )

    # Phase 4: FX operations
    from .fx_operations import compiler_set_fx_parameter

    # Modulation route creation
    registry.register(OperationDefinition(
        operation_id="compound_create_modulation_route",
        semantic_name="Create Modulation Route",
        kind=OperationKind.COMPOUND,
        parameters=[
            OperationParameter("source_id", None, True, "LFO or modulation source ID"),
            OperationParameter("destination_param", None, True, "Destination semantic target"),
            OperationParameter("amount", None, True, "Modulation amount (0.0-1.0)"),
            OperationParameter("modslot_index", None, False, "ModSlot index (0-63); auto if not specified"),
        ],
        description="Create a new modulation route from source to destination",
    ))
    registry.register_compiler("compound_create_modulation_route", compiler_create_modulation_route)

    # Modulation route deletion
    registry.register(OperationDefinition(
        operation_id="compound_delete_modulation_route",
        semantic_name="Delete Modulation Route",
        kind=OperationKind.COMPOUND,
        parameters=[
            OperationParameter("modslot_index", None, False, "ModSlot index (0-63) to delete"),
            OperationParameter("source_id", None, False, "LFO source ID (if searching by route)"),
            OperationParameter("destination_param", None, False, "Destination (if searching by route)"),
        ],
        description="Delete an existing modulation route",
    ))
    registry.register_compiler("compound_delete_modulation_route", compiler_delete_modulation_route)

    # Macro value
    registry.register(OperationDefinition(
        operation_id="compound_set_macro_value",
        semantic_name="Set Macro Value",
        kind=OperationKind.COMPOUND,
        parameters=[
            OperationParameter("macro_id", None, True, "Macro index (0-7)"),
            OperationParameter("value", None, True, "Macro value (0.0-1.0)"),
        ],
        description="Set the value of a macro",
    ))
    registry.register_compiler("compound_set_macro_value", compiler_set_macro_value)

    # Macro rename
    registry.register(OperationDefinition(
        operation_id="compound_rename_macro",
        semantic_name="Rename Macro",
        kind=OperationKind.COMPOUND,
        parameters=[
            OperationParameter("macro_id", None, True, "Macro index (0-7)"),
            OperationParameter("name", None, True, "New name for the macro"),
        ],
        description="Rename a macro",
    ))
    registry.register_compiler("compound_rename_macro", compiler_rename_macro)

    # Phase 4: FX operations
    registry.register(OperationDefinition(
        operation_id="fx_set_parameter",
        semantic_name="Set FX Parameter",
        kind=OperationKind.STATE,
        parameters=[
            OperationParameter("rack", None, True, "FX rack index (0-2)"),
            OperationParameter("slot", None, True, "FX slot index within rack"),
            OperationParameter("effect", None, True, "Effect type (Distortion, EQ, Delay, etc.)"),
            OperationParameter("parameter", None, True, "Parameter name (Drive, Freq1, etc.)"),
            OperationParameter("value", None, True, "Parameter value"),
        ],
        description="Set FX parameter value",
    ))
    registry.register_compiler("fx_set_parameter", compiler_set_fx_parameter)
