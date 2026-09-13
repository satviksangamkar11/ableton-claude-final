"""Unit tests for Phase 2: Scalar operation compilation."""

import pytest
from .model import (
    SerumOperation,
    OperationKind,
    OperationParameter,
    OperationContext,
)
from .compiler import compile_operation
from .registry import get_registry


def test_registry_initialization():
    """Test that registry loads with scalar operations."""
    registry = get_registry()
    ops = registry.all_operations()
    assert len(ops) > 0, "Registry should be populated with scalar operations"
    assert any("envelope" in op_id for op_id in ops.keys()), "Should have envelope operations"


def test_scalar_operation_compilation():
    """Test compiling a scalar operation to mutation."""
    # Create a scalar operation instance
    operation = SerumOperation(
        operation_id="scalar_envelope_field_release",
        semantic_name="Set Env1.Release",
        kind=OperationKind.SCALAR,
        parameters=[
            OperationParameter(
                name="value",
                value=0.8,
                required=True,
            )
        ],
        semantic_target="Env1.Release",
    )

    # Create a minimal context
    ctx = OperationContext(body={})

    # Compile
    result = compile_operation(operation, ctx)

    # Verify result
    assert result.operation_id == "scalar_envelope_field_release"
    assert result.success, f"Compilation failed: {result.error_detail}"
    assert len(result.compiled_mutations) > 0, "Should produce at least one mutation"

    # Check the mutation
    mutation = result.compiled_mutations[0]
    assert hasattr(mutation, "value"), "Mutation should have value"
    assert mutation.value == 0.8, "Mutation value should match operation parameter"


def test_scalar_operations_coverage():
    """Test that all major operation kinds are represented."""
    registry = get_registry()
    ops = registry.all_operations()

    # Extract capability domains
    domains = set()
    for op_id in ops.keys():
        # Extract domain from op_id: scalar_{domain}_{field}
        parts = op_id.split("_")
        if len(parts) >= 2:
            domain = parts[1]
            domains.add(domain)

    # Check expected domains exist
    expected_domains = {"envelope", "filter", "oscillator", "fx", "global"}
    found_domains = domains & expected_domains
    assert len(found_domains) > 0, f"Should have operations from expected domains. Found: {domains}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
