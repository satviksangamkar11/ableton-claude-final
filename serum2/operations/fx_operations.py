"""Phase 4: FX structured operation compilers.

set_fx_parameter(rack, slot, effect, parameter, value)
→ Mutation(FXRack{R}.FX.{N}.FX{Type}.plainParams.kParam{Name}, value)
"""

from __future__ import annotations
from typing import Optional

from .model import (
    SerumOperation,
    OperationContext,
    OperationResult,
    OperationParameter,
)
from .fx_resolver import resolve_fx_parameter
from serum2.evidence.spec import Mutation


def compiler_set_fx_parameter(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile set_fx_parameter() to Mutation[].

    Parameters:
      - rack (int): FX rack index (0-2)
      - slot (int): FX slot index within rack
      - effect (str): Effect type (Distortion, EQ, Delay, Reverb, Compressor, Chorus)
      - parameter (str): Parameter name (Drive, Freq1, Feedback, etc.)
      - value (float): Parameter value

    Returns:
      OperationResult with single Mutation(FXRack{R}.FX.{N}.FX{Type}.plainParams.kParam{Name}, value)
    """
    # Extract parameters
    params_dict = {p.name: p.value for p in operation.parameters}

    rack = params_dict.get("rack")
    slot = params_dict.get("slot")
    effect = params_dict.get("effect")
    parameter = params_dict.get("parameter")
    value = params_dict.get("value")

    # Validate required parameters
    if rack is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_RACK",
            error_detail="set_fx_parameter requires rack index",
        )

    if slot is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_SLOT",
            error_detail="set_fx_parameter requires slot index",
        )

    if effect is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_EFFECT",
            error_detail="set_fx_parameter requires effect type",
        )

    if parameter is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_PARAMETER",
            error_detail="set_fx_parameter requires parameter name",
        )

    if value is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_VALUE",
            error_detail="set_fx_parameter requires value",
        )

    # Validate ranges
    if not (0 <= int(rack) <= 2):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_RACK",
            error_detail=f"Rack must be 0-2, got {rack}",
        )

    if int(slot) < 0:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_SLOT",
            error_detail=f"Slot must be non-negative, got {slot}",
        )

    # Resolve FX parameter
    resolved = resolve_fx_parameter(
        effect_type=str(effect),
        parameter_name=str(parameter),
        rack_index=int(rack),
        slot_index=int(slot),
    )

    if resolved is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="UNKNOWN_FX_PARAMETER",
            error_detail=f"Unknown FX parameter: {effect}.{parameter}",
        )

    # Validate value range
    if resolved.value_type == "float" and isinstance(value, (int, float)):
        value_f = float(value)
        if resolved.min_value is not None and value_f < resolved.min_value:
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                compilation_error="VALUE_BELOW_MIN",
                error_detail=f"{effect}.{parameter} minimum is {resolved.min_value}, got {value_f}",
            )

        if resolved.max_value is not None and value_f > resolved.max_value:
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                compilation_error="VALUE_ABOVE_MAX",
                error_detail=f"{effect}.{parameter} maximum is {resolved.max_value}, got {value_f}",
            )

    # Create mutation using resolved path
    mutation = Mutation(
        target_path=resolved.state_path,
        value=float(value) if resolved.value_type == "float" else value,
        provenance=f"SerumOperation.{operation.operation_id}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"FX: Rack{rack}.Slot{slot}.{effect}.{parameter} = {value}",
        notes=f"Path: {resolved.state_path}",
    )
