"""Phase 2: Auto-generated scalar operation definitions and compilers.

This module creates SCALAR operation definitions from existing SEMANTIC_TARGETS
and registers compilers for them.

A SCALAR operation is a direct parameter value change that compiles to a
single Mutation using the target_path from the semantic target's contract.

This layer bridges the gap between:
  - human semantic targets (e.g., "LFO0.Rate")
  - existing admission/capability contracts
  - pathmerge mutations
"""

from __future__ import annotations
from typing import Optional, Dict, Any

from .model import (
    SerumOperation,
    OperationKind,
    OperationParameter,
    OperationContext,
    OperationResult,
)
from .registry import OperationRegistry, OperationDefinition
from serum2.evidence.spec import Mutation


def build_scalar_operations_from_targets(
    registry: OperationRegistry,
) -> None:
    """Auto-generate SCALAR operations from SEMANTIC_TARGETS.

    For each semantic target in serum2/compiler/targets.SEMANTIC_TARGETS:
    1. Create an OperationDefinition
    2. Register a compiler function
    3. Add to the registry

    This populates the registry with ~100+ scalar operations covering:
    - Envelope parameters (Attack, Decay, Sustain, Release for Env1-N)
    - LFO parameters (Rate, Shape, Mode for LFO0-9)
    - Macro parameters (Value, Name for Macro0-7)
    - Filter parameters (Cutoff, Resonance, Drive, Type)
    - FX parameters (all EQ, Distortion, Delay, Reverb, Compressor params)
    - Oscillator parameters (Volume, Octave, Detune, etc.)
    - Global parameters (Master Volume, etc.)
    """
    from serum2.compiler.targets import SEMANTIC_TARGETS
    from serum2.evidence.capability_contract import CAUSAL_VERIFIED
    from serum2.evidence import admission as admission_mod

    # For each semantic target in the vocabulary, create a SCALAR operation
    # Deduplicate by capability_key (some targets alias to the same capability)
    seen_keys = set()
    for target_name, target_ref in SEMANTIC_TARGETS.items():
        # Skip if we've already registered this capability_key
        if target_ref.capability_key in seen_keys:
            continue
        seen_keys.add(target_ref.capability_key)

        # Operation identity
        operation_id = f"scalar_{target_ref.capability_key}"
        semantic_name = f"Set {target_name}"

        # Create the operation definition
        definition = OperationDefinition(
            operation_id=operation_id,
            semantic_name=semantic_name,
            kind=OperationKind.SCALAR,
            parameters=[
                OperationParameter(
                    name="value",
                    value=None,  # will be set at runtime by SerumOperation instance
                    required=True,
                    description=f"Value for {target_name}",
                )
            ],
            measurement_metric=None,  # determined by contract
            expected_direction=None,  # determined by contract
            description=f"Direct scalar mutation: {target_name}",
        )

        registry.register(definition)

        # Register the compiler function
        def make_scalar_compiler(tgt_name: str, tgt_ref: Any) -> callable:
            """Closure to capture target for compiler."""
            def scalar_compiler(operation: SerumOperation, ctx: OperationContext) -> OperationResult:
                """Compile a SCALAR operation to a single Mutation."""
                if not operation.parameters:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        compilation_error="MISSING_VALUE",
                        error_detail="SCALAR operation requires value parameter",
                    )

                value = operation.parameters[0].value

                # Look up the semantic target to get the mutation path
                # The path comes from the CapabilityContract associated with this target
                from serum2.compiler.targets import resolve_semantic_target
                from serum2.producer.contract_registry import ContractRegistry

                try:
                    # Get contracts from registry
                    contract_registry = ContractRegistry()
                    contracts_dict = contract_registry.get_contracts_dict()

                    # Resolve the semantic target to get the contract
                    resolution = resolve_semantic_target(tgt_name, contracts_dict)
                    if hasattr(resolution, 'contract') and resolution.contract:
                        # Contract exists; use its scope.mutation_target_path
                        contract = resolution.contract
                        mutation_path = contract.scope.get("mutation_target_path")
                        if not mutation_path:
                            return OperationResult(
                                operation_id=operation.operation_id,
                                success=False,
                                compilation_error="NO_MUTATION_PATH",
                                error_detail=f"Contract for {tgt_name} has no mutation_target_path",
                            )
                    else:
                        # No contract; use the semantic target name as fallback path
                        # This will fail in harness if the path is wrong, but allows
                        # phase 2 to compile operations that are representable but unqualified
                        mutation_path = tgt_name

                    # Create the mutation
                    mutation = Mutation(
                        target_path=mutation_path,
                        value=value,
                        provenance=f"SerumOperation.{operation.operation_id}",
                    )

                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        compiled_mutations=[mutation],
                        mutation_description=f"Scalar: {mutation_path} = {value}",
                    )

                except Exception as e:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        compilation_error="COMPILATION_ERROR",
                        error_detail=str(e),
                    )

            return scalar_compiler

        registry.register_compiler(operation_id, make_scalar_compiler(target_name, target_ref))


def register_scalar_operations() -> None:
    """Initialize scalar operation registry at module load time."""
    from .registry import get_registry
    registry = get_registry()
    build_scalar_operations_from_targets(registry)
