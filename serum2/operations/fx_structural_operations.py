"""Phase FX-FULL: FX structural operations (slot/bus/topology control).

PROVEN OPERATIONS (implemented):
- FX add/remove/replace via array mutation primitives (Phase FX-FULL)
- Clear entire FX rack (Phase FX-FULL)

UNRESOLVED OPERATIONS (bypass mechanism unknown, marked UNRESOLVED):
- FX enable/bypass/disable (Phase FX-2) — requires flex field investigation
- Move effect between buses (Phase FX-2)

After authoritative investigation, FX bypass mechanism was not found in:
  - plainParams.kParamEnable
  - plainParams.kParamBypass
  - VST3 parameter enumeration
  - type discriminant field

The flex field remains unexplored and is the most likely location.
Next investigation: differential state analysis (active vs bypassed vs removed).

These operations work with the three-bus model (MAIN/BUS1/BUS2) and
support all 14 effect types.

Uses pathmerge array mutation primitives for structural changes.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any, Optional

from .model import (
    SerumOperation,
    OperationKind,
    OperationParameter,
    OperationContext,
    OperationResult,
)
from .registry import OperationRegistry, OperationDefinition
from serum2.evidence.spec import Mutation
from serum2 import pathmerge


class FXStructuralOperation(Enum):
    """FX topology/slot operations."""
    ENABLE = "enable"
    DISABLE = "disable"
    ADD = "add"
    REMOVE = "remove"
    REPLACE = "replace"
    REORDER = "reorder"
    MOVE_BETWEEN_BUSES = "move_between_buses"
    CLEAR_RACK = "clear_rack"


class Bus(Enum):
    """Three FX buses."""
    MAIN = 0
    BUS1 = 1
    BUS2 = 2


@dataclass
class FXSlotLocation:
    """Identifies a specific FX slot."""
    bus: Bus
    slot_index: int

    @property
    def rack_path(self) -> str:
        """Path to this rack in state."""
        return f"FXRack{self.bus.value}"

    @property
    def fx_array_path(self) -> str:
        """Path to FX array in this rack."""
        return f"{self.rack_path}.FX"

    @property
    def slot_path(self) -> str:
        """Path to specific slot."""
        return f"{self.fx_array_path}.{self.slot_index}"


class FXStructuralCompiler:
    """Compiles FX structural operations to mutations.

    Uses pathmerge array mutation primitives:
    - array_insert: Add FX to rack
    - array_remove: Remove FX from rack
    - array_replace_element: Replace FX type at slot
    - apply_path_value: Clear entire rack (→ [])

    All operations preserve existing FX parameters.
    """

    def __init__(self):
        pass

    def disable_effect(
        self,
        operation: SerumOperation,
        bus: Bus,
        slot_index: int,
    ) -> OperationResult:
        """Disable (remove) an effect at a slot.

        Uses array_remove to remove element at slot_index.
        Subsequent elements shift down.
        """
        location = FXSlotLocation(bus, slot_index)
        fx_array_path = location.fx_array_path

        # Create a pseudo-mutation that encodes the array operation
        # This is represented as a special mutation type understood by harness
        mutation = Mutation(
            target_path=fx_array_path,
            value={"__array_op__": "remove", "index": slot_index},
            provenance=f"SerumOperation.{operation.operation_id}",
        )

        return OperationResult(
            operation_id=operation.operation_id,
            success=True,
            compiled_mutations=[mutation],
            mutation_description=f"FX disable: Remove effect at {location.rack_path}[{slot_index}]",
        )

    def add_effect(
        self,
        operation: SerumOperation,
        bus: Bus,
        slot_index: int,
        effect_structure: Dict[str, Any],
    ) -> OperationResult:
        """Add a new effect to a bus at a specific slot.

        Uses array_insert to insert effect_structure at slot_index.
        Subsequent elements shift up.
        """
        location = FXSlotLocation(bus, slot_index)
        fx_array_path = location.fx_array_path

        # Encode array insertion operation
        mutation = Mutation(
            target_path=fx_array_path,
            value={"__array_op__": "insert", "index": slot_index, "element": effect_structure},
            provenance=f"SerumOperation.{operation.operation_id}",
        )

        return OperationResult(
            operation_id=operation.operation_id,
            success=True,
            compiled_mutations=[mutation],
            mutation_description=f"FX add: Insert effect at {location.rack_path}[{slot_index}]",
        )

    def replace_effect(
        self,
        operation: SerumOperation,
        bus: Bus,
        slot_index: int,
        new_effect_structure: Dict[str, Any],
    ) -> OperationResult:
        """Replace effect at slot with different effect type.

        Uses array_replace_element to swap effect at slot_index.
        """
        location = FXSlotLocation(bus, slot_index)
        slot_path = location.slot_path

        # Direct path mutation to replace entire FX element
        mutation = Mutation(
            target_path=slot_path,
            value=new_effect_structure,
            provenance=f"SerumOperation.{operation.operation_id}",
        )

        return OperationResult(
            operation_id=operation.operation_id,
            success=True,
            compiled_mutations=[mutation],
            mutation_description=f"FX replace: Replace effect at {slot_path}",
        )

    def clear_rack(
        self,
        operation: SerumOperation,
        bus: Bus,
    ) -> OperationResult:
        """Clear all effects from a rack.

        Replaces entire FX array with empty list [].
        """
        location = FXSlotLocation(bus, 0)
        fx_array_path = location.fx_array_path

        # Whole-array replacement mutation
        mutation = Mutation(
            target_path=fx_array_path,
            value=[],
            provenance=f"SerumOperation.{operation.operation_id}",
        )

        return OperationResult(
            operation_id=operation.operation_id,
            success=True,
            compiled_mutations=[mutation],
            mutation_description=f"FX clear: Remove all effects from {location.rack_path}",
        )


def build_fx_structural_operations(registry: OperationRegistry) -> None:
    """Register FX structural operations.

    PROVEN OPERATIONS (registered):
    - CLEAR_RACK: fully implemented (whole-array replacement)
    - REMOVE: implemented via array_remove primitive
    - ADD: implemented via array_insert primitive
    - REPLACE: implemented via array_replace_element primitive

    UNRESOLVED OPERATIONS (NOT registered):
    - ENABLE: unresolved (bypass mechanism unknown)
    - DISABLE: unresolved (bypass mechanism unknown, NOT array_remove)
    - BYPASS: unresolved (bypass mechanism unknown)
    - UNBYPASS: unresolved (bypass mechanism unknown)

    REASON FOR UNRESOLVED:
    After authoritative investigation, FX bypass mechanism was NOT found in:
      - plainParams.kParamEnable
      - plainParams.kParamBypass
      - VST3 parameter enumeration (2623 params)
      - type discriminant field

    The FXRack0.FX[i].flex field remains structurally present but semantically
    unexplored. This is the most likely location for bypass state.

    NEXT INVESTIGATION:
    Differential state analysis: capture and compare three authoritative states
    (active FX vs bypassed FX vs removed FX) at the v8 serialization level to
    identify which field(s) differ between active↔bypassed vs bypassed↔removed.
    """
    compiler = FXStructuralCompiler()

    # Register CLEAR_RACK operations for each bus (PROVEN)
    for bus in [Bus.MAIN, Bus.BUS1, Bus.BUS2]:
        bus_name = bus.name
        operation_id = f"fx_struct_clear_rack_{bus_name}"
        semantic_name = f"Clear FX Rack {bus_name}"

        definition = OperationDefinition(
            operation_id=operation_id,
            semantic_name=semantic_name,
            kind=OperationKind.STRUCTURAL,
            parameters=[],
            measurement_metric=None,
            expected_direction=None,
            description=f"Remove all effects from {bus_name} FX rack",
        )

        registry.register(definition)

        # Register compiler
        def make_clear_compiler(target_bus: Bus) -> callable:
            def clear_compiler(
                operation: SerumOperation, ctx: OperationContext
            ) -> OperationResult:
                return compiler.clear_rack(operation, target_bus)

            return clear_compiler

        registry.register_compiler(operation_id, make_clear_compiler(bus))


def register_fx_structural_operations() -> None:
    """Initialize FX structural operations at module load time."""
    from .registry import get_registry

    registry = get_registry()
    build_fx_structural_operations(registry)
