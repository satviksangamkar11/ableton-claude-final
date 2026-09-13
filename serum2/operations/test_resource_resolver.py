"""Unit tests for Phase 6: Resource model and resolver."""

import pytest
from .resource_model import (
    ResourceKind,
    ResourceAvailability,
    SerumResource,
    ResourceResolution,
)
from .resource_resolver import ResourceResolver


class TestResourceModel:
    """Test resource data model."""

    def test_serum_resource_creation(self):
        """Test creating a SerumResource."""
        resource = SerumResource(
            kind=ResourceKind.WAVETABLE,
            canonical_id="serum2://wavetable/operator",
            display_name="Operator",
            absolute_path="/path/to/Operator.wav",
            serum_relative_path="Tables/Operator",
            file_hash="abc123def456",
            file_size=65536,
            source="bundled",
        )

        assert resource.kind == ResourceKind.WAVETABLE
        assert resource.canonical_id == "serum2://wavetable/operator"
        assert resource.display_name == "Operator"

    def test_resource_to_dict(self):
        """Test serializing resource to dict."""
        resource = SerumResource(
            kind=ResourceKind.SAMPLE,
            canonical_id="serum2://sample/kick",
            display_name="Kick",
            absolute_path="/path/to/Kick.wav",
            serum_relative_path="Samples/Kick",
        )

        d = resource.to_dict()
        assert d["kind"] == "sample"
        assert d["canonical_id"] == "serum2://sample/kick"

    def test_resource_resolution_success(self):
        """Test successful resource resolution."""
        resource = SerumResource(
            kind=ResourceKind.WAVETABLE,
            canonical_id="serum2://wavetable/test",
            display_name="Test",
            absolute_path="/test.wav",
            serum_relative_path="Tables/Test",
        )

        resolution = ResourceResolution(
            requested_id="test",
            availability=ResourceAvailability.FOUND,
            resource=resource,
        )

        assert resolution.success()
        assert resolution.resource is not None

    def test_resource_resolution_failure(self):
        """Test failed resource resolution."""
        resolution = ResourceResolution(
            requested_id="missing",
            availability=ResourceAvailability.NOT_FOUND,
            error_detail="Resource not found",
        )

        assert not resolution.success()
        assert "not found" in resolution.failed_reason().lower()


class TestResourceResolver:
    """Test resource resolution."""

    def test_resolver_creation(self):
        """Test creating a resolver."""
        resolver = ResourceResolver()
        assert resolver is not None

    def test_resolve_standard_wavetable(self):
        """Test resolving a standard wavetable."""
        resolver = ResourceResolver()
        resolution = resolver.resolve_wavetable("operator")

        assert resolution.success()
        assert resolution.resource.canonical_id == "serum2://wavetable/operator"
        assert resolution.resource.kind == ResourceKind.WAVETABLE

    def test_resolve_standard_wavetable_case_insensitive(self):
        """Test that resolution is case-insensitive."""
        resolver = ResourceResolver()
        resolution = resolver.resolve_wavetable("OPERATOR")

        assert resolution.success()
        assert resolution.resource.display_name == "Operator"

    def test_resolve_standard_sample(self):
        """Test resolving a standard sample."""
        resolver = ResourceResolver()
        resolution = resolver.resolve_sample("drum_kick")

        assert resolution.success()
        assert resolution.resource.kind == ResourceKind.SAMPLE

    def test_resolve_missing_wavetable(self):
        """Test resolving a missing wavetable."""
        resolver = ResourceResolver()
        resolution = resolver.resolve_wavetable("nonexistent_wavetable_xyz")

        assert not resolution.success()
        assert resolution.availability == ResourceAvailability.NOT_FOUND

    def test_resolve_missing_resource_reason(self):
        """Test that missing resource gives clear error reason."""
        resolver = ResourceResolver()
        resolution = resolver.resolve_wavetable("fac3")  # The historical missing resource

        assert not resolution.success()
        reason = resolution.failed_reason()
        assert "fac3" in reason.lower()
        assert "not found" in reason.lower()

    def test_resource_to_state_path_wavetable(self):
        """Test converting wavetable resource to state path."""
        resolver = ResourceResolver()
        resource = SerumResource(
            kind=ResourceKind.WAVETABLE,
            canonical_id="serum2://wavetable/test",
            display_name="Test",
            absolute_path="/test.wav",
            serum_relative_path="Tables/Test",
        )

        path = resolver.resource_to_state_path(resource, 0)
        assert path == "Oscillator0.WTOsc0.relativePathToWT"

    def test_resource_to_state_path_sample(self):
        """Test converting sample resource to state path."""
        resolver = ResourceResolver()
        resource = SerumResource(
            kind=ResourceKind.SAMPLE,
            canonical_id="serum2://sample/kick",
            display_name="Kick",
            absolute_path="/kick.wav",
            serum_relative_path="Samples/Kick",
        )

        path = resolver.resource_to_state_path(resource, 1)
        assert path == "Oscillator1.SampleOsc1.relativePathToSample"

    def test_resource_to_state_path_multisample(self):
        """Test converting multisample resource to state path."""
        resolver = ResourceResolver()
        resource = SerumResource(
            kind=ResourceKind.MULTISAMPLE,
            canonical_id="serum2://multisample/test",
            display_name="Test",
            absolute_path="/test.sfz",
            serum_relative_path="Multisamples/Test",
        )

        path = resolver.resource_to_state_path(resource, 0)
        assert path == "Oscillator0.MultiSampleOsc0.relativePathToMultisample"


class TestResourceOperationIntegration:
    """Test resource operations through SerumOperation."""

    def test_load_wavetable_with_standard_resource(self):
        """Test loading a standard wavetable via SerumOperation."""
        from .model import SerumOperation, OperationKind, OperationParameter, OperationContext
        from .compiler import compile_operation

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

        assert result.success, f"Compilation failed: {result.error_detail}"
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert "relativePathToWT" in mutation.target_path

    def test_load_wavetable_missing_resource(self):
        """Test loading a missing wavetable."""
        from .model import SerumOperation, OperationKind, OperationParameter, OperationContext
        from .compiler import compile_operation

        operation = SerumOperation(
            operation_id="osc_load_wavetable",
            semantic_name="Load Wavetable",
            kind=OperationKind.RESOURCE,
            parameters=[
                OperationParameter("oscillator", 0, True),
                OperationParameter("resource", "fac3", True),  # Historical missing resource
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert not result.success
        assert "NOT_FOUND" in result.compilation_error
        assert "fac3" in result.error_detail.lower()

    def test_load_sample_with_standard_resource(self):
        """Test loading a standard sample via SerumOperation."""
        from .model import SerumOperation, OperationKind, OperationParameter, OperationContext
        from .compiler import compile_operation

        operation = SerumOperation(
            operation_id="osc_load_sample",
            semantic_name="Load Sample",
            kind=OperationKind.RESOURCE,
            parameters=[
                OperationParameter("oscillator", 0, True),
                OperationParameter("resource", "drum_kick", True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert result.success
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert "relativePathToSample" in mutation.target_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
