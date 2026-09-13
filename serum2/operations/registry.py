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
    """Populate the registry with built-in scalar/state operations.

    This is called once at module initialization.
    Structured operations are registered separately.
    """
    # This function will be expanded in Phase 2 to auto-generate
    # scalar operation definitions from SEMANTIC_TARGETS.
    # For now, it's a placeholder.
    pass
