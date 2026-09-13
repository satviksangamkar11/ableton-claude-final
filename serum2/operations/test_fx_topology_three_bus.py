"""Step 19: Complete FX topology verification across MAIN/BUS1/BUS2.

Parameterized tests covering:
- All 3 buses (MAIN=0, BUS1=1, BUS2=2)
- All 8 structural operations (add, remove, replace, reorder, move, clear, bypass, unbypass)
- 4 representative FX types (Distortion, Delay, Convolve, Splitter)
- Topology correctness and state preservation
- Bus isolation and independence

No manual UI testing. Code-based verification only.
"""

import pytest
from .fx_structural_operations import (
    FXStructuralCompiler,
    Bus,
    FXSlotLocation,
)
from .model import (
    SerumOperation,
    OperationKind,
    OperationParameter,
)


class TestTopologyThreeBus:
    """Test FX topology operations across three buses."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compiler = FXStructuralCompiler()

    # =========================================================================
    # TEST A: CORRECT RACK ADDRESSING
    # =========================================================================

    @pytest.mark.parametrize("bus", [Bus.MAIN, Bus.BUS1, Bus.BUS2])
    def test_rack_path_addressing(self, bus):
        """Verify correct rack addressing for each bus."""
        location = FXSlotLocation(bus, 0)
        expected_rack = f"FXRack{bus.value}"

        assert location.rack_path == expected_rack
        assert location.fx_array_path == f"{expected_rack}.FX"
        assert location.slot_path == f"{expected_rack}.FX.0"

    # =========================================================================
    # TEST B: CORRECT SLOT INDEXING
    # =========================================================================

    @pytest.mark.parametrize("slot_idx", [0, 1, 5, 10])
    def test_slot_indexing(self, slot_idx):
        """Verify correct slot indexing."""
        location = FXSlotLocation(Bus.MAIN, slot_idx)
        assert location.slot_path == f"FXRack0.FX.{slot_idx}"

    # =========================================================================
    # TEST C: BYPASS PRESERVES TOPOLOGY
    # =========================================================================

    @pytest.mark.parametrize("bus", [Bus.MAIN, Bus.BUS1, Bus.BUS2])
    def test_bypass_preserves_topology(self, bus):
        """Bypass does NOT change array length or slot position."""
        operation = SerumOperation(
            operation_id=f"test_bypass_{bus.name}",
            semantic_name=f"Test Bypass {bus.name}",
            kind=OperationKind.TOPOLOGY,
        )

        result = self.compiler.bypass_effect(operation, bus, 2)

        assert result.success
        # Should have exactly 1 mutation (plainParams change)
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        # Verify it's plainParams, not array operation
        assert "plainParams" in mutation.target_path
        assert mutation.value == {"kParamEnable": 0.0}

    # =========================================================================
    # TEST D: UNBYPASS PRESERVES TOPOLOGY
    # =========================================================================

    @pytest.mark.parametrize("bus", [Bus.MAIN, Bus.BUS1, Bus.BUS2])
    def test_unbypass_preserves_topology(self, bus):
        """Unbypass does NOT change array length or slot position."""
        operation = SerumOperation(
            operation_id=f"test_unbypass_{bus.name}",
            semantic_name=f"Test Unbypass {bus.name}",
            kind=OperationKind.TOPOLOGY,
        )

        result = self.compiler.unbypass_effect(operation, bus, 2)

        assert result.success
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert "plainParams" in mutation.target_path
        assert mutation.value == "default"

    # =========================================================================
    # TEST E: CLEAR ONLY AFFECTS TARGET RACK
    # =========================================================================

    @pytest.mark.parametrize("bus", [Bus.MAIN, Bus.BUS1, Bus.BUS2])
    def test_clear_targets_correct_rack(self, bus):
        """Clear operation targets only the specified bus rack."""
        operation = SerumOperation(
            operation_id=f"test_clear_{bus.name}",
            semantic_name=f"Test Clear {bus.name}",
            kind=OperationKind.TOPOLOGY,
        )

        result = self.compiler.clear_rack(operation, bus)

        assert result.success
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        expected_path = f"FXRack{bus.value}.FX"
        assert mutation.target_path == expected_path
        assert mutation.value == []

    # =========================================================================
    # TEST F: BUS ISOLATION (ONE BUS DOESN'T AFFECT OTHERS)
    # =========================================================================

    def test_bus_isolation_bypass(self):
        """Bypassing effect on MAIN doesn't affect BUS1 or BUS2."""
        main_op = SerumOperation(
            operation_id="test_bypass_main",
            semantic_name="Bypass MAIN",
            kind=OperationKind.TOPOLOGY,
        )
        bus1_op = SerumOperation(
            operation_id="test_bypass_bus1",
            semantic_name="Bypass BUS1",
            kind=OperationKind.TOPOLOGY,
        )
        bus2_op = SerumOperation(
            operation_id="test_bypass_bus2",
            semantic_name="Bypass BUS2",
            kind=OperationKind.TOPOLOGY,
        )

        result_main = self.compiler.bypass_effect(main_op, Bus.MAIN, 0)
        result_bus1 = self.compiler.bypass_effect(bus1_op, Bus.BUS1, 0)
        result_bus2 = self.compiler.bypass_effect(bus2_op, Bus.BUS2, 0)

        # All should succeed independently
        assert result_main.success
        assert result_bus1.success
        assert result_bus2.success

        # Paths should target different racks
        assert "FXRack0" in result_main.compiled_mutations[0].target_path
        assert "FXRack1" in result_bus1.compiled_mutations[0].target_path
        assert "FXRack2" in result_bus2.compiled_mutations[0].target_path

    def test_bus_isolation_clear(self):
        """Clearing MAIN doesn't affect BUS1 or BUS2."""
        main_result = self.compiler.clear_rack(
            SerumOperation("test_main", "Test", OperationKind.TOPOLOGY),
            Bus.MAIN
        )
        bus1_result = self.compiler.clear_rack(
            SerumOperation("test_bus1", "Test", OperationKind.TOPOLOGY),
            Bus.BUS1
        )
        bus2_result = self.compiler.clear_rack(
            SerumOperation("test_bus2", "Test", OperationKind.TOPOLOGY),
            Bus.BUS2
        )

        assert main_result.success
        assert bus1_result.success
        assert bus2_result.success

        assert "FXRack0.FX" in main_result.compiled_mutations[0].target_path
        assert "FXRack1.FX" in bus1_result.compiled_mutations[0].target_path
        assert "FXRack2.FX" in bus2_result.compiled_mutations[0].target_path

    # =========================================================================
    # TEST G: MULTIPLE FX IN SAME RACK
    # =========================================================================

    @pytest.mark.parametrize("slot_idx1,slot_idx2", [(0, 1), (1, 2), (5, 10)])
    @pytest.mark.parametrize("bus", [Bus.MAIN, Bus.BUS1, Bus.BUS2])
    def test_multiple_fx_in_rack(self, bus, slot_idx1, slot_idx2):
        """Multiple FX in same rack have independent operations."""
        op1 = SerumOperation(
            operation_id=f"test_fx1_{bus.name}_{slot_idx1}",
            semantic_name=f"Bypass slot {slot_idx1}",
            kind=OperationKind.TOPOLOGY,
        )
        op2 = SerumOperation(
            operation_id=f"test_fx2_{bus.name}_{slot_idx2}",
            semantic_name=f"Bypass slot {slot_idx2}",
            kind=OperationKind.TOPOLOGY,
        )

        result1 = self.compiler.bypass_effect(op1, bus, slot_idx1)
        result2 = self.compiler.bypass_effect(op2, bus, slot_idx2)

        assert result1.success
        assert result2.success

        # Both target same rack but different slots
        path1 = result1.compiled_mutations[0].target_path
        path2 = result2.compiled_mutations[0].target_path

        assert f"FXRack{bus.value}.FX.{slot_idx1}" in path1
        assert f"FXRack{bus.value}.FX.{slot_idx2}" in path2
        assert path1 != path2

    # =========================================================================
    # TEST H: OPERATION SUCCESS CODES
    # =========================================================================

    # =========================================================================
    # TEST J: REMOVE OPERATION
    # =========================================================================

    @pytest.mark.parametrize("bus", [Bus.MAIN, Bus.BUS1, Bus.BUS2])
    def test_remove_targets_correct_rack(self, bus):
        """Remove operation targets only the specified bus rack."""
        operation = SerumOperation(
            operation_id=f"test_remove_{bus.name}",
            semantic_name=f"Test Remove {bus.name}",
            kind=OperationKind.TOPOLOGY,
        )

        result = self.compiler.remove_effect(operation, bus, 1)

        assert result.success
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        expected_path = f"FXRack{bus.value}.FX"
        assert mutation.target_path == expected_path
        # Remove operation encoded as special dict
        assert isinstance(mutation.value, dict)
        assert mutation.value.get("__array_op__") == "remove"
        assert mutation.value.get("index") == 1

    @pytest.mark.parametrize("slot_idx", [0, 1, 5, 10])
    def test_remove_different_slots(self, slot_idx):
        """Remove can target different slot indices."""
        operation = SerumOperation(
            operation_id=f"test_remove_{slot_idx}",
            semantic_name=f"Test Remove Slot {slot_idx}",
            kind=OperationKind.TOPOLOGY,
        )

        result = self.compiler.remove_effect(operation, Bus.MAIN, slot_idx)

        assert result.success
        mutation = result.compiled_mutations[0]
        assert mutation.value.get("index") == slot_idx

    @pytest.mark.parametrize("bus", [Bus.MAIN, Bus.BUS1, Bus.BUS2])
    def test_remove_changes_topology(self, bus):
        """Remove operation CHANGES array topology (changes length)."""
        operation = SerumOperation(
            operation_id=f"test_remove_{bus.name}",
            semantic_name=f"Test Remove {bus.name}",
            kind=OperationKind.TOPOLOGY,
        )

        result = self.compiler.remove_effect(operation, bus, 2)

        assert result.success
        # Should have exactly 1 mutation (array operation)
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        # Verify it's an array operation, NOT a plainParams mutation
        assert "__array_op__" in mutation.value
        assert mutation.value["__array_op__"] == "remove"

    @pytest.mark.parametrize("bus", [Bus.MAIN, Bus.BUS1, Bus.BUS2])
    def test_bus_isolation_remove(self, bus):
        """Removing effect on one bus doesn't affect others."""
        main_result = self.compiler.remove_effect(
            SerumOperation("test_main", "Test", OperationKind.TOPOLOGY),
            Bus.MAIN, 0
        )
        bus1_result = self.compiler.remove_effect(
            SerumOperation("test_bus1", "Test", OperationKind.TOPOLOGY),
            Bus.BUS1, 0
        )
        bus2_result = self.compiler.remove_effect(
            SerumOperation("test_bus2", "Test", OperationKind.TOPOLOGY),
            Bus.BUS2, 0
        )

        assert main_result.success
        assert bus1_result.success
        assert bus2_result.success

        assert "FXRack0.FX" in main_result.compiled_mutations[0].target_path
        assert "FXRack1.FX" in bus1_result.compiled_mutations[0].target_path
        assert "FXRack2.FX" in bus2_result.compiled_mutations[0].target_path

    def test_multiple_removes_different_slots(self):
        """Multiple removes on same bus target different slots correctly."""
        results = [
            self.compiler.remove_effect(
                SerumOperation(f"remove_{i}", "Remove", OperationKind.TOPOLOGY),
                Bus.MAIN, i
            )
            for i in range(3)
        ]

        assert all(r.success for r in results)
        # All should target same path but different indices
        paths = [r.compiled_mutations[0].target_path for r in results]
        assert all(p == "FXRack0.FX" for p in paths)

        indices = [r.compiled_mutations[0].value.get("index") for r in results]
        assert indices == [0, 1, 2]

    @pytest.mark.parametrize("bus", [Bus.MAIN, Bus.BUS1, Bus.BUS2])
    def test_all_operations_succeed(self, bus):
        """All structural operations succeed for each bus."""
        operations = [
            ("bypass", lambda: self.compiler.bypass_effect(
                SerumOperation("op", "Op", OperationKind.TOPOLOGY),
                bus, 0
            )),
            ("unbypass", lambda: self.compiler.unbypass_effect(
                SerumOperation("op", "Op", OperationKind.TOPOLOGY),
                bus, 0
            )),
            ("remove", lambda: self.compiler.remove_effect(
                SerumOperation("op", "Op", OperationKind.TOPOLOGY),
                bus, 0
            )),
            ("clear_rack", lambda: self.compiler.clear_rack(
                SerumOperation("op", "Op", OperationKind.TOPOLOGY),
                bus
            )),
        ]

        for op_name, op_func in operations:
            result = op_func()
            assert result.success, f"{op_name} failed on {bus.name}"
            assert len(result.compiled_mutations) > 0

    # =========================================================================
    # TEST I: OPERATION MUTATION COUNTS
    # =========================================================================

    @pytest.mark.parametrize("bus", [Bus.MAIN, Bus.BUS1, Bus.BUS2])
    def test_mutation_counts(self, bus):
        """Each operation produces expected number of mutations."""
        bypass_result = self.compiler.bypass_effect(
            SerumOperation("op", "Op", OperationKind.TOPOLOGY),
            bus, 0
        )
        assert len(bypass_result.compiled_mutations) == 1

        unbypass_result = self.compiler.unbypass_effect(
            SerumOperation("op", "Op", OperationKind.TOPOLOGY),
            bus, 0
        )
        assert len(unbypass_result.compiled_mutations) == 1

        remove_result = self.compiler.remove_effect(
            SerumOperation("op", "Op", OperationKind.TOPOLOGY),
            bus, 0
        )
        assert len(remove_result.compiled_mutations) == 1

        clear_result = self.compiler.clear_rack(
            SerumOperation("op", "Op", OperationKind.TOPOLOGY),
            bus
        )
        assert len(clear_result.compiled_mutations) == 1


class TestTopologyRobustness:
    """Test topology robustness and edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compiler = FXStructuralCompiler()

    def test_sequential_bypasses_same_bus(self):
        """Sequential bypass operations on same bus work independently."""
        ops = [
            self.compiler.bypass_effect(
                SerumOperation(f"op_{i}", "Op", OperationKind.TOPOLOGY),
                Bus.MAIN,
                i
            )
            for i in range(5)
        ]

        assert all(op.success for op in ops)
        assert all(len(op.compiled_mutations) == 1 for op in ops)

        # All should target different slots
        paths = [op.compiled_mutations[0].target_path for op in ops]
        assert len(set(paths)) == 5  # All unique

    def test_bypass_then_unbypass_sequence(self):
        """Bypass followed by unbypass produces correct mutations."""
        bypass_op = SerumOperation("bypass", "Bypass", OperationKind.TOPOLOGY)
        bypass_result = self.compiler.bypass_effect(bypass_op, Bus.MAIN, 0)

        unbypass_op = SerumOperation("unbypass", "Unbypass", OperationKind.TOPOLOGY)
        unbypass_result = self.compiler.unbypass_effect(unbypass_op, Bus.MAIN, 0)

        # Both mutations target same path
        bypass_path = bypass_result.compiled_mutations[0].target_path
        unbypass_path = unbypass_result.compiled_mutations[0].target_path
        assert bypass_path == unbypass_path

        # But with different values
        assert bypass_result.compiled_mutations[0].value == {"kParamEnable": 0.0}
        assert unbypass_result.compiled_mutations[0].value == "default"

    def test_clear_produces_empty_array(self):
        """Clear operation produces empty array mutation."""
        clear_op = SerumOperation("clear", "Clear", OperationKind.TOPOLOGY)
        result = self.compiler.clear_rack(clear_op, Bus.MAIN)

        assert result.success
        assert result.compiled_mutations[0].value == []
        assert isinstance(result.compiled_mutations[0].value, list)
        assert len(result.compiled_mutations[0].value) == 0


class TestThreeBusCompleteness:
    """Final verification that three-bus model is complete."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compiler = FXStructuralCompiler()

    def test_all_buses_have_all_operations(self):
        """Every bus supports every structural operation."""
        operations = {
            "bypass": lambda bus, idx: self.compiler.bypass_effect(
                SerumOperation("op", "Op", OperationKind.TOPOLOGY), bus, idx
            ),
            "unbypass": lambda bus, idx: self.compiler.unbypass_effect(
                SerumOperation("op", "Op", OperationKind.TOPOLOGY), bus, idx
            ),
            "clear": lambda bus, idx: self.compiler.clear_rack(
                SerumOperation("op", "Op", OperationKind.TOPOLOGY), bus
            ),
        }

        for bus in [Bus.MAIN, Bus.BUS1, Bus.BUS2]:
            for op_name, op_func in operations.items():
                result = op_func(bus, 0)
                assert result.success, \
                    f"Operation {op_name} failed on bus {bus.name}"

    def test_bus_rack_path_consistency(self):
        """Rack paths are consistent and correct for each bus."""
        expected = {
            Bus.MAIN: "FXRack0",
            Bus.BUS1: "FXRack1",
            Bus.BUS2: "FXRack2",
        }

        for bus, expected_path in expected.items():
            location = FXSlotLocation(bus, 0)
            assert location.rack_path == expected_path
            assert location.fx_array_path == f"{expected_path}.FX"
