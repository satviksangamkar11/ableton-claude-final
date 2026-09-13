"""Unit tests for Phase 5: Oscillator structured operations."""

import pytest
from .model import (
    SerumOperation,
    OperationKind,
    OperationParameter,
    OperationContext,
)
from .compiler import compile_operation
from .registry import get_registry


class TestOscillatorTypeOperations:
    """Test oscillator type selection operations."""

    def test_set_oscillator_type_wavetable(self):
        """Test setting oscillator to wavetable type."""
        operation = SerumOperation(
            operation_id="osc_set_type",
            semantic_name="Set Oscillator Type",
            kind=OperationKind.COMPOUND,
            parameters=[
                OperationParameter("oscillator", 0, True),
                OperationParameter("type", "wavetable", True),
            ],
        )

        ctx = OperationContext(body={"Oscillator0": {}})
        result = compile_operation(operation, ctx)

        assert result.success, f"Compilation failed: {result.error_detail}"
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert "Oscillator0" in mutation.target_path
        assert "WTOsc" in mutation.target_path

    def test_set_oscillator_type_sample(self):
        """Test setting oscillator to sample type."""
        operation = SerumOperation(
            operation_id="osc_set_type",
            semantic_name="Set Oscillator Type",
            kind=OperationKind.COMPOUND,
            parameters=[
                OperationParameter("oscillator", 0, True),
                OperationParameter("type", "sample", True),
            ],
        )

        ctx = OperationContext(body={"Oscillator0": {}})
        result = compile_operation(operation, ctx)

        assert result.success
        mutation = result.compiled_mutations[0]
        assert "SampleOsc" in mutation.target_path

    def test_set_oscillator_type_multisample(self):
        """Test setting oscillator to multisample type."""
        operation = SerumOperation(
            operation_id="osc_set_type",
            semantic_name="Set Oscillator Type",
            kind=OperationKind.COMPOUND,
            parameters=[
                OperationParameter("oscillator", 1, True),
                OperationParameter("type", "multisample", True),
            ],
        )

        ctx = OperationContext(body={"Oscillator1": {}})
        result = compile_operation(operation, ctx)

        assert result.success
        mutation = result.compiled_mutations[0]
        assert "Oscillator1" in mutation.target_path
        assert "MultiSampleOsc" in mutation.target_path

    def test_set_oscillator_type_spectral(self):
        """Test setting oscillator to spectral type."""
        operation = SerumOperation(
            operation_id="osc_set_type",
            semantic_name="Set Oscillator Type",
            kind=OperationKind.COMPOUND,
            parameters=[
                OperationParameter("oscillator", 0, True),
                OperationParameter("type", "spectral", True),
            ],
        )

        ctx = OperationContext(body={"Oscillator0": {}})
        result = compile_operation(operation, ctx)

        assert result.success
        mutation = result.compiled_mutations[0]
        assert "SpectralOsc" in mutation.target_path

    def test_set_oscillator_type_granular(self):
        """Test setting oscillator to granular type."""
        operation = SerumOperation(
            operation_id="osc_set_type",
            semantic_name="Set Oscillator Type",
            kind=OperationKind.COMPOUND,
            parameters=[
                OperationParameter("oscillator", 0, True),
                OperationParameter("type", "granular", True),
            ],
        )

        ctx = OperationContext(body={"Oscillator0": {}})
        result = compile_operation(operation, ctx)

        assert result.success
        mutation = result.compiled_mutations[0]
        assert "GranularOsc" in mutation.target_path

    def test_set_oscillator_type_invalid_type(self):
        """Test error handling for invalid oscillator type."""
        operation = SerumOperation(
            operation_id="osc_set_type",
            semantic_name="Set Oscillator Type",
            kind=OperationKind.COMPOUND,
            parameters=[
                OperationParameter("oscillator", 0, True),
                OperationParameter("type", "invalid_type", True),
            ],
        )

        ctx = OperationContext(body={"Oscillator0": {}})
        result = compile_operation(operation, ctx)

        assert not result.success
        assert result.compilation_error == "UNKNOWN_OSCILLATOR_TYPE"

    def test_set_oscillator_type_oscillator_not_found(self):
        """Test error handling for missing oscillator in context."""
        operation = SerumOperation(
            operation_id="osc_set_type",
            semantic_name="Set Oscillator Type",
            kind=OperationKind.COMPOUND,
            parameters=[
                OperationParameter("oscillator", 5, True),
                OperationParameter("type", "wavetable", True),
            ],
        )

        ctx = OperationContext(body={"Oscillator0": {}})
        result = compile_operation(operation, ctx)

        assert not result.success
        assert result.compilation_error == "OSCILLATOR_NOT_FOUND"


class TestOscillatorParameterOperations:
    """Test oscillator parameter setting operations."""

    def test_set_oscillator_parameter_semitone(self):
        """Test setting oscillator semitone parameter."""
        operation = SerumOperation(
            operation_id="osc_set_parameter",
            semantic_name="Set Oscillator Parameter",
            kind=OperationKind.STATE,
            parameters=[
                OperationParameter("oscillator", 0, True),
                OperationParameter("parameter", "semitone", True),
                OperationParameter("value", 5.0, True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert result.success
        mutation = result.compiled_mutations[0]
        assert "kParamSemitone" in mutation.target_path
        assert mutation.value == 5.0

    def test_set_oscillator_parameter_octave(self):
        """Test setting oscillator octave parameter."""
        operation = SerumOperation(
            operation_id="osc_set_parameter",
            semantic_name="Set Oscillator Parameter",
            kind=OperationKind.STATE,
            parameters=[
                OperationParameter("oscillator", 1, True),
                OperationParameter("parameter", "octave", True),
                OperationParameter("value", 1, True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert result.success
        mutation = result.compiled_mutations[0]
        assert "Oscillator1" in mutation.target_path
        assert "kParamOctave" in mutation.target_path

    def test_set_oscillator_parameter_unknown_parameter(self):
        """Test error handling for unknown parameter."""
        operation = SerumOperation(
            operation_id="osc_set_parameter",
            semantic_name="Set Oscillator Parameter",
            kind=OperationKind.STATE,
            parameters=[
                OperationParameter("oscillator", 0, True),
                OperationParameter("parameter", "unknown_param", True),
                OperationParameter("value", 0.5, True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert not result.success
        assert result.compilation_error == "UNKNOWN_PARAMETER"

    def test_set_oscillator_parameter_out_of_range(self):
        """Test error handling for out-of-range parameter value."""
        operation = SerumOperation(
            operation_id="osc_set_parameter",
            semantic_name="Set Oscillator Parameter",
            kind=OperationKind.STATE,
            parameters=[
                OperationParameter("oscillator", 0, True),
                OperationParameter("parameter", "level", True),
                OperationParameter("value", 2.5, True),  # Max is 1.0
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert not result.success
        assert result.compilation_error == "VALUE_OUT_OF_RANGE"


class TestOscillatorResourceOperations:
    """Test oscillator resource loading operations."""

    def test_load_wavetable(self):
        """Test loading wavetable into oscillator."""
        operation = SerumOperation(
            operation_id="osc_load_wavetable",
            semantic_name="Load Wavetable",
            kind=OperationKind.RESOURCE,
            parameters=[
                OperationParameter("oscillator", 0, True),
                OperationParameter("resource", "operator", True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert result.success
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert "relativePathToWT" in mutation.target_path

    def test_load_sample(self):
        """Test loading sample into oscillator."""
        operation = SerumOperation(
            operation_id="osc_load_sample",
            semantic_name="Load Sample",
            kind=OperationKind.RESOURCE,
            parameters=[
                OperationParameter("oscillator", 1, True),
                OperationParameter("resource", "drum_kick", True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert result.success
        mutation = result.compiled_mutations[0]
        assert "relativePathToSample" in mutation.target_path
        assert "Oscillator1" in mutation.target_path


class TestOscillatorRegistration:
    """Test that oscillator operations are registered."""

    def test_oscillator_operations_in_registry(self):
        """Test that oscillator operations are registered."""
        registry = get_registry()
        ops = registry.all_operations()

        assert "osc_set_type" in ops
        assert "osc_set_parameter" in ops
        assert "osc_load_wavetable" in ops
        assert "osc_load_sample" in ops

    def test_oscillator_compilers_available(self):
        """Test that all oscillator compilers are registered."""
        registry = get_registry()

        assert registry.get_compiler("osc_set_type") is not None
        assert registry.get_compiler("osc_set_parameter") is not None
        assert registry.get_compiler("osc_load_wavetable") is not None
        assert registry.get_compiler("osc_load_sample") is not None

    def test_oscillator_operations_have_correct_kind(self):
        """Test that oscillator operations have correct OperationKind."""
        registry = get_registry()

        type_op = registry.get("osc_set_type")
        assert type_op.kind == OperationKind.COMPOUND

        param_op = registry.get("osc_set_parameter")
        assert param_op.kind == OperationKind.STATE

        wt_op = registry.get("osc_load_wavetable")
        assert wt_op.kind == OperationKind.RESOURCE

        sample_op = registry.get("osc_load_sample")
        assert sample_op.kind == OperationKind.RESOURCE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
