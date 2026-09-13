"""Unit tests for Phase 4: FX structured operations."""

import pytest
from .model import (
    SerumOperation,
    OperationKind,
    OperationParameter,
    OperationContext,
)
from .compiler import compile_operation
from .registry import get_registry
from .fx_resolver import resolve_fx_parameter


class TestFXResolver:
    """Test FX parameter resolution."""

    def test_resolve_distortion_drive(self):
        """Test resolving Distortion.Drive parameter."""
        resolved = resolve_fx_parameter("Distortion", "Drive", rack_index=0, slot_index=2)

        assert resolved is not None
        assert resolved.state_path == "FXRack0.FX.2.FXDistortion.plainParams.kParamDrive"
        assert resolved.effect_type == "Distortion"
        assert resolved.parameter_name == "Drive"
        assert resolved.min_value == 0.0
        assert resolved.max_value == 100.0

    def test_resolve_eq_parameters(self):
        """Test resolving EQ parameters."""
        freq1 = resolve_fx_parameter("EQ", "Freq1")
        assert freq1 is not None
        assert "FXEQ" in freq1.state_path
        assert "kParamFreq1" in freq1.state_path

        gain2 = resolve_fx_parameter("EQ", "Gain2")
        assert gain2 is not None
        assert "kParamGain2" in gain2.state_path
        assert gain2.min_value == -24.0
        assert gain2.max_value == 24.0

    def test_resolve_unknown_parameter(self):
        """Test that unknown parameters return None."""
        resolved = resolve_fx_parameter("Distortion", "UnknownParam")
        assert resolved is None

    def test_resolve_with_custom_rack_slot(self):
        """Test path generation with custom rack/slot indices."""
        resolved = resolve_fx_parameter("Distortion", "Drive", rack_index=1, slot_index=3)
        assert resolved is not None
        assert resolved.state_path == "FXRack1.FX.3.FXDistortion.plainParams.kParamDrive"


class TestFXOperations:
    """Test FX operation compilation."""

    def test_set_distortion_drive(self):
        """Test setting Distortion.Drive via operation."""
        operation = SerumOperation(
            operation_id="fx_set_parameter",
            semantic_name="Set FX Parameter",
            kind=OperationKind.STATE,
            parameters=[
                OperationParameter("rack", 0, True),
                OperationParameter("slot", 2, True),
                OperationParameter("effect", "Distortion", True),
                OperationParameter("parameter", "Drive", True),
                OperationParameter("value", 65.0, True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert result.success, f"Compilation failed: {result.error_detail}"
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert "FXRack0.FX.2.FXDistortion.plainParams.kParamDrive" in mutation.target_path
        assert mutation.value == 65.0

    def test_set_eq_freq1(self):
        """Test setting EQ.Freq1."""
        operation = SerumOperation(
            operation_id="fx_set_parameter",
            semantic_name="Set FX Parameter",
            kind=OperationKind.STATE,
            parameters=[
                OperationParameter("rack", 0, True),
                OperationParameter("slot", 0, True),
                OperationParameter("effect", "EQ", True),
                OperationParameter("parameter", "Freq1", True),
                OperationParameter("value", 5000.0, True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert result.success, f"Compilation failed: {result.error_detail}"
        mutation = result.compiled_mutations[0]
        assert "FXEQ" in mutation.target_path
        assert "kParamFreq1" in mutation.target_path
        assert mutation.value == 5000.0

    def test_invalid_rack_index(self):
        """Test error handling for invalid rack."""
        operation = SerumOperation(
            operation_id="fx_set_parameter",
            semantic_name="Set FX Parameter",
            kind=OperationKind.STATE,
            parameters=[
                OperationParameter("rack", 5, True),  # Invalid: > 2
                OperationParameter("slot", 0, True),
                OperationParameter("effect", "Distortion", True),
                OperationParameter("parameter", "Drive", True),
                OperationParameter("value", 50.0, True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert not result.success
        assert result.compilation_error == "INVALID_RACK"

    def test_value_out_of_range(self):
        """Test error handling for out-of-range value."""
        operation = SerumOperation(
            operation_id="fx_set_parameter",
            semantic_name="Set FX Parameter",
            kind=OperationKind.STATE,
            parameters=[
                OperationParameter("rack", 0, True),
                OperationParameter("slot", 0, True),
                OperationParameter("effect", "EQ", True),
                OperationParameter("parameter", "Gain1", True),
                OperationParameter("value", 50.0, True),  # Max is 24.0
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert not result.success
        assert result.compilation_error == "VALUE_ABOVE_MAX"

    def test_unknown_effect_parameter(self):
        """Test error handling for unknown effect/parameter combo."""
        operation = SerumOperation(
            operation_id="fx_set_parameter",
            semantic_name="Set FX Parameter",
            kind=OperationKind.STATE,
            parameters=[
                OperationParameter("rack", 0, True),
                OperationParameter("slot", 0, True),
                OperationParameter("effect", "UnknownEffect", True),
                OperationParameter("parameter", "UnknownParam", True),
                OperationParameter("value", 50.0, True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert not result.success
        assert result.compilation_error == "UNKNOWN_FX_PARAMETER"


class TestFXRegistration:
    """Test that FX operations are registered."""

    def test_fx_operation_in_registry(self):
        """Test that FX operation is registered."""
        registry = get_registry()
        ops = registry.all_operations()

        assert "fx_set_parameter" in ops

    def test_fx_operation_has_compiler(self):
        """Test that FX operation has a compiler."""
        registry = get_registry()
        compiler = registry.get_compiler("fx_set_parameter")

        assert compiler is not None


class TestFXParameterCatalog:
    """Test FX parameter catalog."""

    def test_distortion_parameters(self):
        """Test that Distortion has known parameters."""
        dist_drive = resolve_fx_parameter("Distortion", "Drive")
        assert dist_drive is not None

        dist_tone = resolve_fx_parameter("Distortion", "Tone")
        assert dist_tone is not None

    def test_eq_parameters(self):
        """Test that EQ has all expected parameters."""
        for param in ["Freq1", "Freq2", "Reso1", "Reso2", "Gain1", "Gain2", "LevelOut"]:
            resolved = resolve_fx_parameter("EQ", param)
            assert resolved is not None, f"EQ.{param} should be resolved"

    def test_delay_parameters(self):
        """Test that Delay has basic parameters."""
        for param in ["Time", "Feedback", "Mix"]:
            resolved = resolve_fx_parameter("Delay", param)
            assert resolved is not None, f"Delay.{param} should be resolved"

    def test_compressor_parameters(self):
        """Test that Compressor has expected parameters."""
        for param in ["Threshold", "Ratio", "Attack", "Release"]:
            resolved = resolve_fx_parameter("Compressor", param)
            assert resolved is not None, f"Compressor.{param} should be resolved"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
