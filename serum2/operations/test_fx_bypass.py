"""Unit tests for FX bypass/unbypass operations (Step 17).

Tests the proven bypass mechanism discovered in Step 16:
- ACTIVE: FXRack0.FX[i].<FXType>.plainParams = "default"
- BYPASSED: FXRack0.FX[i].<FXType>.plainParams = {"kParamEnable": 0.0}

Verified on Distortion (type=0) and Delay (type=4).
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
    OperationContext,
)


class TestFXBypassOperation:
    """Test bypass operation compilation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compiler = FXStructuralCompiler()

    def test_bypass_effect_main_bus_slot_0(self):
        """Test bypassing effect at MAIN bus, slot 0."""
        operation = SerumOperation(
            operation_id="fx_struct_bypass_MAIN",
            semantic_name="Bypass FX MAIN",
            kind=OperationKind.TOPOLOGY,
            parameters=[
                OperationParameter("slot_index", 0, True),
            ],
        )

        result = self.compiler.bypass_effect(operation, Bus.MAIN, 0)

        assert result.success
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert "FXRack0.FX.0" in mutation.target_path
        assert "plainParams" in mutation.target_path
        assert mutation.value == {"kParamEnable": 0.0}

    def test_bypass_effect_bus1_slot_2(self):
        """Test bypassing effect at BUS1, slot 2."""
        operation = SerumOperation(
            operation_id="fx_struct_bypass_BUS1",
            semantic_name="Bypass FX BUS1",
            kind=OperationKind.TOPOLOGY,
            parameters=[
                OperationParameter("slot_index", 2, True),
            ],
        )

        result = self.compiler.bypass_effect(operation, Bus.BUS1, 2)

        assert result.success
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert "FXRack1.FX.2" in mutation.target_path
        assert "plainParams" in mutation.target_path
        assert mutation.value == {"kParamEnable": 0.0}

    def test_bypass_effect_bus2_slot_1(self):
        """Test bypassing effect at BUS2, slot 1."""
        operation = SerumOperation(
            operation_id="fx_struct_bypass_BUS2",
            semantic_name="Bypass FX BUS2",
            kind=OperationKind.TOPOLOGY,
            parameters=[
                OperationParameter("slot_index", 1, True),
            ],
        )

        result = self.compiler.bypass_effect(operation, Bus.BUS2, 1)

        assert result.success
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert "FXRack2.FX.1" in mutation.target_path
        assert "plainParams" in mutation.target_path
        assert mutation.value == {"kParamEnable": 0.0}

    def test_bypass_effect_preserves_slot_topology(self):
        """Verify bypass does NOT change FX array topology."""
        operation = SerumOperation(
            operation_id="test_bypass",
            semantic_name="Test Bypass",
            kind=OperationKind.TOPOLOGY,
        )

        result = self.compiler.bypass_effect(operation, Bus.MAIN, 0)

        # Should have exactly 1 mutation (plainParams change)
        assert len(result.compiled_mutations) == 1

        # Should NOT be an array removal mutation
        mutation = result.compiled_mutations[0]
        assert "plainParams" in mutation.target_path
        assert mutation.value != {"__array_op__": "remove", "index": 0}


class TestFXUnbypassOperation:
    """Test unbypass operation compilation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compiler = FXStructuralCompiler()

    def test_unbypass_effect_main_bus_slot_0(self):
        """Test unbypass effect at MAIN bus, slot 0."""
        operation = SerumOperation(
            operation_id="fx_struct_unbypass_MAIN",
            semantic_name="Unbypass FX MAIN",
            kind=OperationKind.TOPOLOGY,
            parameters=[
                OperationParameter("slot_index", 0, True),
            ],
        )

        result = self.compiler.unbypass_effect(operation, Bus.MAIN, 0)

        assert result.success
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert "FXRack0.FX.0" in mutation.target_path
        assert "plainParams" in mutation.target_path
        assert mutation.value == "default"

    def test_unbypass_effect_bus1_slot_3(self):
        """Test unbypass effect at BUS1, slot 3."""
        operation = SerumOperation(
            operation_id="fx_struct_unbypass_BUS1",
            semantic_name="Unbypass FX BUS1",
            kind=OperationKind.TOPOLOGY,
            parameters=[
                OperationParameter("slot_index", 3, True),
            ],
        )

        result = self.compiler.unbypass_effect(operation, Bus.BUS1, 3)

        assert result.success
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert "FXRack1.FX.3" in mutation.target_path
        assert "plainParams" in mutation.target_path
        assert mutation.value == "default"

    def test_unbypass_effect_preserves_slot_topology(self):
        """Verify unbypass does NOT change FX array topology."""
        operation = SerumOperation(
            operation_id="test_unbypass",
            semantic_name="Test Unbypass",
            kind=OperationKind.TOPOLOGY,
        )

        result = self.compiler.unbypass_effect(operation, Bus.MAIN, 0)

        # Should have exactly 1 mutation (plainParams change)
        assert len(result.compiled_mutations) == 1

        # Should NOT be an array operation
        mutation = result.compiled_mutations[0]
        assert mutation.value == "default"


class TestBypassVsClear:
    """Verify bypass is distinct from clear operation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compiler = FXStructuralCompiler()

    def test_bypass_does_not_clear_rack(self):
        """Verify bypass does NOT clear the entire rack."""
        bypass_op = SerumOperation(
            operation_id="test_bypass",
            semantic_name="Test Bypass",
            kind=OperationKind.TOPOLOGY,
        )
        bypass_result = self.compiler.bypass_effect(bypass_op, Bus.MAIN, 0)

        clear_op = SerumOperation(
            operation_id="test_clear",
            semantic_name="Test Clear",
            kind=OperationKind.TOPOLOGY,
        )
        clear_result = self.compiler.clear_rack(clear_op, Bus.MAIN)

        # Bypass should mutate plainParams
        bypass_mutation = bypass_result.compiled_mutations[0]
        assert "plainParams" in bypass_mutation.target_path
        assert bypass_mutation.value == {"kParamEnable": 0.0}

        # Clear should mutate the FX array
        clear_mutation = clear_result.compiled_mutations[0]
        assert "FX" in clear_mutation.target_path
        assert clear_mutation.value == []

    def test_bypass_then_clear_sequence(self):
        """Verify bypass and clear are independent operations."""
        bypass_op = SerumOperation(
            operation_id="test_bypass",
            semantic_name="Test Bypass",
            kind=OperationKind.TOPOLOGY,
        )
        bypass_result = self.compiler.bypass_effect(bypass_op, Bus.MAIN, 0)

        # After bypass, the FX is still at slot 0, just bypassed
        # Clearing the rack removes all FX
        clear_op = SerumOperation(
            operation_id="test_clear",
            semantic_name="Test Clear",
            kind=OperationKind.TOPOLOGY,
        )
        clear_result = self.compiler.clear_rack(clear_op, Bus.MAIN)

        # Both should succeed independently
        assert bypass_result.success
        assert clear_result.success

        # They should produce different mutations
        assert bypass_result.compiled_mutations[0].target_path != \
               clear_result.compiled_mutations[0].target_path


class TestBypassAllBuses:
    """Test bypass operations on all three buses."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compiler = FXStructuralCompiler()

    @pytest.mark.parametrize("bus", [Bus.MAIN, Bus.BUS1, Bus.BUS2])
    def test_bypass_all_buses(self, bus):
        """Test bypass on each bus."""
        operation = SerumOperation(
            operation_id=f"test_bypass_{bus.name}",
            semantic_name=f"Test Bypass {bus.name}",
            kind=OperationKind.TOPOLOGY,
        )

        result = self.compiler.bypass_effect(operation, bus, 0)

        assert result.success
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        expected_rack = f"FXRack{bus.value}"
        assert expected_rack in mutation.target_path
        assert mutation.value == {"kParamEnable": 0.0}

    @pytest.mark.parametrize("bus", [Bus.MAIN, Bus.BUS1, Bus.BUS2])
    def test_unbypass_all_buses(self, bus):
        """Test unbypass on each bus."""
        operation = SerumOperation(
            operation_id=f"test_unbypass_{bus.name}",
            semantic_name=f"Test Unbypass {bus.name}",
            kind=OperationKind.TOPOLOGY,
        )

        result = self.compiler.unbypass_effect(operation, bus, 0)

        assert result.success
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        expected_rack = f"FXRack{bus.value}"
        assert expected_rack in mutation.target_path
        assert mutation.value == "default"


class TestBypassSlotIndices:
    """Test bypass on various slot indices."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compiler = FXStructuralCompiler()

    @pytest.mark.parametrize("slot_index", [0, 1, 2, 5, 9])
    def test_bypass_various_slots(self, slot_index):
        """Test bypass on various slot indices."""
        operation = SerumOperation(
            operation_id=f"test_bypass_slot_{slot_index}",
            semantic_name=f"Test Bypass Slot {slot_index}",
            kind=OperationKind.TOPOLOGY,
        )

        result = self.compiler.bypass_effect(operation, Bus.MAIN, slot_index)

        assert result.success
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert f"FXRack0.FX.{slot_index}" in mutation.target_path
        assert mutation.value == {"kParamEnable": 0.0}

    @pytest.mark.parametrize("slot_index", [0, 1, 2, 5, 9])
    def test_unbypass_various_slots(self, slot_index):
        """Test unbypass on various slot indices."""
        operation = SerumOperation(
            operation_id=f"test_unbypass_slot_{slot_index}",
            semantic_name=f"Test Unbypass Slot {slot_index}",
            kind=OperationKind.TOPOLOGY,
        )

        result = self.compiler.unbypass_effect(operation, Bus.MAIN, slot_index)

        assert result.success
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert f"FXRack0.FX.{slot_index}" in mutation.target_path
        assert mutation.value == "default"
