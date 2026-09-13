"""Unit tests for Phase 3: Compound operation compilation."""

import pytest
from .model import (
    SerumOperation,
    OperationKind,
    OperationParameter,
    OperationContext,
)
from .compiler import compile_operation
from .registry import get_registry


class TestModulationRouteOperations:
    """Test modulation route creation/deletion."""

    def test_create_modulation_route_compilation(self):
        """Test compiling create_modulation_route to mutation."""
        operation = SerumOperation(
            operation_id="compound_create_modulation_route",
            semantic_name="Create Modulation Route",
            kind=OperationKind.COMPOUND,
            parameters=[
                OperationParameter("source_id", 2, True),
                OperationParameter("destination_param", "Filter.Cutoff", True),
                OperationParameter("amount", 0.5, True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert result.success, f"Compilation failed: {result.error_detail}"
        assert len(result.compiled_mutations) == 1, "Should produce one mutation"

        mutation = result.compiled_mutations[0]
        assert mutation.target_path.startswith("ModSlot"), "Should target a ModSlot"
        assert isinstance(mutation.value, dict), "Should be dict replacement (route struct)"
        assert mutation.value.get("source") == [2, 0], "Source should match"

    def test_delete_modulation_route_by_index(self):
        """Test deleting route by explicit index."""
        operation = SerumOperation(
            operation_id="compound_delete_modulation_route",
            semantic_name="Delete Modulation Route",
            kind=OperationKind.COMPOUND,
            parameters=[
                OperationParameter("modslot_index", 5, True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert result.success, f"Compilation failed: {result.error_detail}"
        assert len(result.compiled_mutations) == 1
        assert result.compiled_mutations[0].target_path == "ModSlot5"
        assert result.compiled_mutations[0].value == "default"

    def test_create_route_missing_source(self):
        """Test error handling for missing source_id."""
        operation = SerumOperation(
            operation_id="compound_create_modulation_route",
            semantic_name="Create Modulation Route",
            kind=OperationKind.COMPOUND,
            parameters=[
                OperationParameter("destination_param", "Filter.Cutoff", True),
                OperationParameter("amount", 0.5, True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert not result.success
        assert result.compilation_error == "MISSING_SOURCE_ID"


class TestMacroOperations:
    """Test macro value and name operations."""

    def test_set_macro_value(self):
        """Test compiling set_macro_value."""
        operation = SerumOperation(
            operation_id="compound_set_macro_value",
            semantic_name="Set Macro Value",
            kind=OperationKind.COMPOUND,
            parameters=[
                OperationParameter("macro_id", 3, True),
                OperationParameter("value", 0.75, True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert result.success, f"Compilation failed: {result.error_detail}"
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert mutation.target_path == "Macro3.plainParams.kParamValue"
        assert mutation.value == 0.75

    def test_rename_macro(self):
        """Test compiling rename_macro."""
        operation = SerumOperation(
            operation_id="compound_rename_macro",
            semantic_name="Rename Macro",
            kind=OperationKind.COMPOUND,
            parameters=[
                OperationParameter("macro_id", 1, True),
                OperationParameter("name", "Filter Drive", True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert result.success, f"Compilation failed: {result.error_detail}"
        assert len(result.compiled_mutations) == 1

        mutation = result.compiled_mutations[0]
        assert mutation.target_path == "Macro1.name"
        assert mutation.value == "Filter Drive"

    def test_set_macro_invalid_id(self):
        """Test error handling for invalid macro ID."""
        operation = SerumOperation(
            operation_id="compound_set_macro_value",
            semantic_name="Set Macro Value",
            kind=OperationKind.COMPOUND,
            parameters=[
                OperationParameter("macro_id", 10, True),  # Invalid: > 7
                OperationParameter("value", 0.5, True),
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert not result.success
        assert result.compilation_error == "INVALID_MACRO_ID"

    def test_set_macro_out_of_range_value(self):
        """Test error handling for out-of-range value."""
        operation = SerumOperation(
            operation_id="compound_set_macro_value",
            semantic_name="Set Macro Value",
            kind=OperationKind.COMPOUND,
            parameters=[
                OperationParameter("macro_id", 2, True),
                OperationParameter("value", 1.5, True),  # Invalid: > 1.0
            ],
        )

        ctx = OperationContext(body={})
        result = compile_operation(operation, ctx)

        assert not result.success
        assert result.compilation_error == "VALUE_OUT_OF_RANGE"


class TestRegistryHasCompoundOps:
    """Verify compound operations are registered."""

    def test_registry_has_modulation_ops(self):
        """Test that modulation operations are in registry."""
        registry = get_registry()
        ops = registry.all_operations()

        assert "compound_create_modulation_route" in ops
        assert "compound_delete_modulation_route" in ops

    def test_registry_has_macro_ops(self):
        """Test that macro operations are in registry."""
        registry = get_registry()
        ops = registry.all_operations()

        assert "compound_set_macro_value" in ops
        assert "compound_rename_macro" in ops

    def test_compound_operations_are_correct_kind(self):
        """Test that compound operations have COMPOUND kind."""
        registry = get_registry()

        create_route = registry.get("compound_create_modulation_route")
        assert create_route is not None
        assert create_route.kind == OperationKind.COMPOUND

        set_macro = registry.get("compound_set_macro_value")
        assert set_macro is not None
        assert set_macro.kind == OperationKind.COMPOUND


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
