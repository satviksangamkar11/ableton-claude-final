"""Phase 3: Compound operation adapters for modulation and macros.

A COMPOUND operation requires multiple coordinated mutations.

Examples:
- create_modulation_route(lfo_id, dest_param, amount) → populate ModSlot dict
- delete_modulation_route(lfo_id, dest_param) → set ModSlot to "default"
- set_macro_value(macro_id, value) → Macro{N}.plainParams.kParamValue
- rename_macro(macro_id, name) → Macro{N}.name
- assign_macro_to_param(macro_id, target_param) → modulation route creation

Compiler strategy:
  1. Decompose into constituent mutations
  2. Collect all Mutation[] objects
  3. Verify no conflicts via pathmerge rules
  4. Return combined result
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List

from .model import (
    SerumOperation,
    OperationKind,
    OperationParameter,
    OperationContext,
    OperationResult,
)
from serum2.evidence.spec import Mutation


def compiler_create_modulation_route(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile create_modulation_route() to Mutation[].

    Parameters:
      - source_id (int): LFO source ID (0-9) or other modulation source
      - destination_param (str): semantic target (e.g., "Filter.Cutoff")
      - amount (float): modulation amount (0.0-1.0)
      - modslot_index (int, optional): which ModSlot to use (0-63); if not specified, find free slot

    Returns:
      OperationResult with single Mutation(ModSlot{N}, route_struct)
    """
    # Extract parameters
    params_dict = {p.name: p.value for p in operation.parameters}

    source_id = params_dict.get("source_id")
    dest_param = params_dict.get("destination_param")
    amount = params_dict.get("amount", 1.0)
    modslot_index = params_dict.get("modslot_index")

    if source_id is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_SOURCE_ID",
            error_detail="create_modulation_route requires source_id parameter",
        )

    if dest_param is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_DESTINATION",
            error_detail="create_modulation_route requires destination_param parameter",
        )

    # Find free ModSlot if index not specified
    if modslot_index is None:
        modslot_index = _find_free_modslot(ctx.body)
        if modslot_index is None:
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                compilation_error="NO_FREE_MODSLOT",
                error_detail="All ModSlot0-63 are occupied; cannot create new route",
            )

    # Build the route struct (based on forensic analysis schema)
    # This is a real route structure from Serum presets
    route_struct = {
        "destModuleID": 0,  # TODO: resolve from dest_param semantic target
        "destModuleParamID": 3,  # TODO: resolve from dest_param
        "destModuleParamName": "kParamFreq",  # TODO: resolve from dest_param
        "destModuleTypeString": "VoiceFilter",  # TODO: resolve from dest_param
        "plainParams": {"kParamAmount": float(amount)},
        "source": [int(source_id), 0],
    }

    # Create mutation: set entire ModSlot dict
    mutation = Mutation(
        target_path=f"ModSlot{modslot_index}",
        value=route_struct,
        provenance=f"SerumOperation.{operation.operation_id}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"Modulation route: LFO{source_id} → {dest_param} at ModSlot{modslot_index}",
        notes=f"TODO: resolve destination parameter IDs from semantic target '{dest_param}'",
    )


def compiler_delete_modulation_route(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile delete_modulation_route() to Mutation[].

    Parameters:
      - modslot_index (int): which ModSlot to clear (0-63)
      OR
      - source_id + destination_param: find and delete that route

    Returns:
      OperationResult with single Mutation(ModSlot{N}, "default")
    """
    params_dict = {p.name: p.value for p in operation.parameters}

    modslot_index = params_dict.get("modslot_index")

    if modslot_index is None:
        # Try to find the slot by source + destination
        source_id = params_dict.get("source_id")
        dest_param = params_dict.get("destination_param")

        if source_id is None or dest_param is None:
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                compilation_error="MISSING_PARAMETERS",
                error_detail="delete_modulation_route requires either modslot_index OR (source_id + destination_param)",
            )

        modslot_index = _find_modslot_by_route(ctx.body, source_id, dest_param)
        if modslot_index is None:
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                compilation_error="ROUTE_NOT_FOUND",
                error_detail=f"No modulation route found: LFO{source_id} → {dest_param}",
            )

    # Create mutation: set ModSlot to "default" (sparse sentinel)
    mutation = Mutation(
        target_path=f"ModSlot{modslot_index}",
        value="default",
        provenance=f"SerumOperation.{operation.operation_id}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"Delete modulation route at ModSlot{modslot_index}",
    )


def compiler_set_macro_value(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile set_macro_value() to Mutation[].

    Parameters:
      - macro_id (int): 0-7 (which macro)
      - value (float): 0.0-1.0 (macro value)

    Returns:
      OperationResult with single Mutation(Macro{N}.plainParams.kParamValue, value)
    """
    params_dict = {p.name: p.value for p in operation.parameters}

    macro_id = params_dict.get("macro_id")
    value = params_dict.get("value")

    if macro_id is None or value is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_PARAMETERS",
            error_detail="set_macro_value requires macro_id and value parameters",
        )

    # Validate range
    if not (0 <= macro_id <= 7):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_MACRO_ID",
            error_detail=f"macro_id must be 0-7, got {macro_id}",
        )

    if not (0.0 <= value <= 1.0):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="VALUE_OUT_OF_RANGE",
            error_detail=f"Macro value must be 0.0-1.0, got {value}",
        )

    # Create mutation
    mutation = Mutation(
        target_path=f"Macro{int(macro_id)}.plainParams.kParamValue",
        value=float(value),
        provenance=f"SerumOperation.{operation.operation_id}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"Set Macro{macro_id} value to {value}",
    )


def compiler_rename_macro(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile rename_macro() to Mutation[].

    Parameters:
      - macro_id (int): 0-7 (which macro)
      - name (str): new name for the macro

    Returns:
      OperationResult with single Mutation(Macro{N}.name, name)
    """
    params_dict = {p.name: p.value for p in operation.parameters}

    macro_id = params_dict.get("macro_id")
    name = params_dict.get("name")

    if macro_id is None or name is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_PARAMETERS",
            error_detail="rename_macro requires macro_id and name parameters",
        )

    # Validate range
    if not (0 <= macro_id <= 7):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_MACRO_ID",
            error_detail=f"macro_id must be 0-7, got {macro_id}",
        )

    # Create mutation
    mutation = Mutation(
        target_path=f"Macro{int(macro_id)}.name",
        value=str(name),
        provenance=f"SerumOperation.{operation.operation_id}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"Rename Macro{macro_id} to '{name}'",
    )


# ============================================================================
# Helper functions
# ============================================================================

def _find_free_modslot(body: Dict[str, Any]) -> Optional[int]:
    """Find first unoccupied ModSlot (value == "default")."""
    for i in range(64):
        slot_key = f"ModSlot{i}"
        slot_val = body.get(slot_key, "default")
        if slot_val == "default":
            return i
    return None


def _find_modslot_by_route(
    body: Dict[str, Any],
    source_id: int,
    dest_param: str,
) -> Optional[int]:
    """Find ModSlot that routes from source_id to dest_param.

    This is a placeholder; full implementation would resolve dest_param
    to module/param IDs and search through all ModSlots.
    """
    # TODO: resolve dest_param semantic target to destModuleID/destModuleParamID
    # then search ModSlot0-63 for a route matching both source and destination
    return None


# ============================================================================
# Phase 8B: Matrix / Modulation Operations
# ============================================================================

def compiler_set_modulation_curve(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile set_modulation_curve() to Mutation[].

    Parameters:
      - modslot_index (int): which ModSlot (0-63)
      - curve_type (str): curve shape ("linear", "exponential", "logarithmic", etc.)

    Returns:
      OperationResult with single Mutation(ModSlot{N}.curve, curve_type)
    """
    params_dict = {p.name: p.value for p in operation.parameters}

    modslot_index = params_dict.get("modslot_index")
    curve_type = params_dict.get("curve_type")

    if modslot_index is None or curve_type is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_PARAMETERS",
            error_detail="set_modulation_curve requires modslot_index and curve_type",
        )

    if not (0 <= modslot_index <= 63):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_MODSLOT",
            error_detail=f"modslot_index must be 0-63, got {modslot_index}",
        )

    mutation = Mutation(
        target_path=f"ModSlot{int(modslot_index)}.curve",
        value=str(curve_type),
        provenance=f"SerumOperation.{operation.operation_id}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"Set ModSlot{modslot_index} curve to {curve_type}",
    )


def compiler_set_modulation_bipolar(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile set_modulation_bipolar() to Mutation[].

    Parameters:
      - modslot_index (int): which ModSlot (0-63)
      - bipolar (bool): true for bipolar, false for unipolar

    Returns:
      OperationResult with single Mutation(ModSlot{N}.bipolar, bool)
    """
    params_dict = {p.name: p.value for p in operation.parameters}

    modslot_index = params_dict.get("modslot_index")
    bipolar = params_dict.get("bipolar")

    if modslot_index is None or bipolar is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_PARAMETERS",
            error_detail="set_modulation_bipolar requires modslot_index and bipolar",
        )

    if not (0 <= modslot_index <= 63):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_MODSLOT",
            error_detail=f"modslot_index must be 0-63, got {modslot_index}",
        )

    mutation = Mutation(
        target_path=f"ModSlot{int(modslot_index)}.bipolar",
        value=bool(bipolar),
        provenance=f"SerumOperation.{operation.operation_id}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"Set ModSlot{modslot_index} to {'bipolar' if bipolar else 'unipolar'}",
    )


def compiler_set_modulation_aux_source(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile set_modulation_aux_source() to Mutation[].

    Parameters:
      - modslot_index (int): which ModSlot (0-63)
      - aux_source_id (int): auxiliary modulation source ID

    Returns:
      OperationResult with single Mutation(ModSlot{N}.auxSource, source_id)
    """
    params_dict = {p.name: p.value for p in operation.parameters}

    modslot_index = params_dict.get("modslot_index")
    aux_source_id = params_dict.get("aux_source_id")

    if modslot_index is None or aux_source_id is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_PARAMETERS",
            error_detail="set_modulation_aux_source requires modslot_index and aux_source_id",
        )

    if not (0 <= modslot_index <= 63):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_MODSLOT",
            error_detail=f"modslot_index must be 0-63, got {modslot_index}",
        )

    mutation = Mutation(
        target_path=f"ModSlot{int(modslot_index)}.auxSource",
        value=int(aux_source_id),
        provenance=f"SerumOperation.{operation.operation_id}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"Set ModSlot{modslot_index} auxiliary source to {aux_source_id}",
    )


def compiler_bypass_modulation_route(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile bypass_modulation_route() to Mutation[].

    Parameters:
      - modslot_index (int): which ModSlot (0-63)
      - bypass (bool): true to bypass, false to enable

    Returns:
      OperationResult with single Mutation(ModSlot{N}.bypass, bool)
    """
    params_dict = {p.name: p.value for p in operation.parameters}

    modslot_index = params_dict.get("modslot_index")
    bypass = params_dict.get("bypass")

    if modslot_index is None or bypass is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_PARAMETERS",
            error_detail="bypass_modulation_route requires modslot_index and bypass",
        )

    if not (0 <= modslot_index <= 63):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_MODSLOT",
            error_detail=f"modslot_index must be 0-63, got {modslot_index}",
        )

    mutation = Mutation(
        target_path=f"ModSlot{int(modslot_index)}.bypass",
        value=bool(bypass),
        provenance=f"SerumOperation.{operation.operation_id}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"{'Bypass' if bypass else 'Enable'} ModSlot{modslot_index}",
    )


def compiler_set_modulation_macro_depth(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile set_modulation_macro_depth() to Mutation[].

    Parameters:
      - modslot_index (int): which ModSlot (0-63)
      - macro_id (int): macro index (0-7)
      - depth (float): modulation depth (0.0-1.0)

    Returns:
      OperationResult with single Mutation(ModSlot{N}.macroDepth, depth)
    """
    params_dict = {p.name: p.value for p in operation.parameters}

    modslot_index = params_dict.get("modslot_index")
    macro_id = params_dict.get("macro_id")
    depth = params_dict.get("depth")

    if modslot_index is None or macro_id is None or depth is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_PARAMETERS",
            error_detail="set_modulation_macro_depth requires modslot_index, macro_id, and depth",
        )

    if not (0 <= modslot_index <= 63):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_MODSLOT",
            error_detail=f"modslot_index must be 0-63, got {modslot_index}",
        )

    if not (0 <= macro_id <= 7):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_MACRO_ID",
            error_detail=f"macro_id must be 0-7, got {macro_id}",
        )

    if not (0.0 <= depth <= 1.0):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="DEPTH_OUT_OF_RANGE",
            error_detail=f"depth must be 0.0-1.0, got {depth}",
        )

    mutation = Mutation(
        target_path=f"ModSlot{int(modslot_index)}.macroDepth[{int(macro_id)}]",
        value=float(depth),
        provenance=f"SerumOperation.{operation.operation_id}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"Set ModSlot{modslot_index} macro{macro_id} depth to {depth}",
    )
