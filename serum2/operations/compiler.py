"""Serum operation compiler: SerumOperation → Mutation[].

The compiler translates high-level operations into the low-level mutations
that pathmerge + harness already understand.

All compilation outputs EXISTING Mutation objects from serum2.evidence.spec.
No new state transport is created.
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any

from .model import SerumOperation, OperationContext, OperationResult, OperationKind
from .registry import get_registry


class CompilationError(Exception):
    """Raised when a SerumOperation cannot be compiled."""
    pass


def compile_operation(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile a SerumOperation to Mutation[].

    Args:
        operation: the operation to compile
        ctx: runtime context (current state, available resources, etc.)

    Returns:
        OperationResult with either compiled_mutations (success) or
        compilation_error (failure)

    Raises:
        CompilationError: if compilation fails due to invalid input
    """
    registry = get_registry()
    compiler_fn = registry.get_compiler(operation.operation_id)

    if compiler_fn is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="NO_COMPILER",
            error_detail=f"No compiler registered for operation {operation.operation_id}",
        )

    try:
        result = compiler_fn(operation, ctx)
        return result
    except CompilationError as e:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="COMPILATION_FAILED",
            error_detail=str(e),
        )
    except Exception as e:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INTERNAL_ERROR",
            error_detail=f"{type(e).__name__}: {e}",
        )


def compile_scalar_operation(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile a SCALAR operation (single parameter value change).

    For a SCALAR operation:
      1. Extract the value from operation.parameters
      2. Determine the mutation target_path from the operation's metadata
      3. Create a single Mutation(target_path, value)
      4. Return OperationResult with that mutation

    The operation's semantic_target or compile_path metadata specifies where
    the mutation applies in the v8 state.
    """
    # Import here to avoid circular dependency
    from serum2.evidence.spec import Mutation

    if not operation.parameters:
        raise CompilationError(
            f"SCALAR operation {operation.operation_id} requires at least one parameter"
        )

    # For now, assume the first parameter is the value
    # In Phase 2, we'll generalize this with an operation-specific schema
    param = operation.parameters[0]
    value = param.value

    # Determine the mutation target path
    # This will be filled in Phase 2 from operation metadata or SEMANTIC_TARGETS lookup
    target_path = operation.semantic_target or "UNKNOWN_TARGET"

    if target_path == "UNKNOWN_TARGET":
        raise CompilationError(
            f"Cannot determine mutation path for {operation.operation_id}. "
            "semantic_target or metadata missing."
        )

    # Create the mutation
    mutation = Mutation(
        target_path=target_path,
        value=value,
        description=f"{operation.semantic_name}: {param.name}={value}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"Scalar mutation: {target_path} = {value}",
    )


def compile_compound_operation(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile a COMPOUND operation (multiple coordinated mutations).

    For a COMPOUND operation:
      1. Decompose into constituent sub-operations
      2. Compile each sub-operation to Mutation[]
      3. Check conflicts via pathmerge rules
      4. Return combined Mutation[]

    Examples:
      - Create.ModulationRoute → {populate ModSlot, set source, dest, amount}
      - Select.OscillatorType → {clear old type dict, populate new type dict}

    In Phase 3, specific compound operation compilers will be registered.
    This is a placeholder.
    """
    raise CompilationError(
        f"COMPOUND operation {operation.operation_id} compiler not yet implemented. "
        "Registered in Phase 3."
    )


def compile_resource_operation(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile a RESOURCE operation (resource resolver + path mutation).

    For a RESOURCE operation:
      1. Resolve the resource (validate file, get canonical path, etc.)
      2. Create a Mutation setting the resource path in the state
      3. Return OperationResult with that mutation

    In Phase 6, resource resolver will be integrated here.
    This is a placeholder.
    """
    raise CompilationError(
        f"RESOURCE operation {operation.operation_id} compiler not yet implemented. "
        "Registered in Phase 6."
    )


def compile_topology_operation(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile a TOPOLOGY operation (enable/disable/reorder).

    For a TOPOLOGY operation:
      1. Determine what structural change is needed
      2. Translate to state mutations (enable field, dict removal, array reorder, etc.)
      3. Return Mutation[]

    In Phase 5, topology operation compilers will be registered.
    This is a placeholder.
    """
    raise CompilationError(
        f"TOPOLOGY operation {operation.operation_id} compiler not yet implemented. "
        "Registered in Phase 5."
    )
