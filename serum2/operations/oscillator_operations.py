"""Phase 5: Oscillator structured operation compilers.

Oscillator operations include:
- Type selection (wavetable, sample, multisample, spectral, granular)
- Parameter mutations (semitone, fine, warp, etc.)
- Resource loading (wavetable, sample)
- OSC2/OSC3 activation (if structure supports it)

All operations compile to Mutation[] using existing harness.
"""

from __future__ import annotations
from typing import Optional, List

from .model import (
    SerumOperation,
    OperationKind,
    OperationContext,
    OperationResult,
    OperationParameter,
)
from serum2.evidence.spec import Mutation


# Explicit allowlist of PROVEN resource operation_ids safe for authority
# integration. osc_load_wavetable's state field (Oscillator{N}.WTOsc{N}.
# relativePathToWT) and relative-path convention ("S2 Tables/Default
# Shapes.wav") were verified this session against a real preset. osc_load_
# sample is deliberately EXCLUDED: resource_to_state_path() claims
# Oscillator{N}.SampleOsc{N}.relativePathToSample, but a real granular-
# oscillator preset shows the actual field is GranularOsc{N}.
# samplePathRelative -- a different field entirely, and plain SampleOsc's
# real field has not been independently confirmed. Wiring an unverified
# field name into the authority-gated executor would write a plausible-
# looking but possibly wrong path -- exactly the failure this integration
# work exists to prevent. Multisample uses embedded SFZ text, not a path
# field at all, and is unresolved for the same reason.
PROVEN_RESOURCE_OPERATION_IDS = frozenset({"osc_load_wavetable"})


# Oscillator types supported by Serum v8 state representation
SUPPORTED_OSCILLATOR_TYPES = {
    "wavetable": "WTOsc",
    "sample": "SampleOsc",
    "multisample": "MultiSampleOsc",
    "spectral": "SpectralOsc",
    "granular": "GranularOsc",
}

# Known oscillator parameters that may exist in plainParams
KNOWN_OSCILLATOR_PARAMS = {
    "semitone": {"value_type": "float", "min": -24.0, "max": 24.0},
    "fine": {"value_type": "float", "min": -1.0, "max": 1.0},
    "detune": {"value_type": "float", "min": -100.0, "max": 100.0},
    "level": {"value_type": "float", "min": 0.0, "max": 1.0},
    "volume": {"value_type": "float", "min": 0.0, "max": 1.0},
    "octave": {"value_type": "int", "min": -2, "max": 2},
    "warp_amount": {"value_type": "float", "min": 0.0, "max": 1.0},
    "warp_mode": {"value_type": "int", "min": 0, "max": 5},
    "wavetable_position": {"value_type": "float", "min": 0.0, "max": 1.0},
}


def compiler_set_oscillator_type(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile set_oscillator_type() to Mutation[].

    Parameters:
      - oscillator (int): Oscillator index (0, 1, 2, ...)
      - type (str): Oscillator type (wavetable, sample, multisample, spectral, granular)

    Returns:
      OperationResult with Mutation[] to switch oscillator type.

    Strategy:
    The v8 state represents each oscillator type as a nested dict:
      Oscillator0.WTOsc0
      Oscillator0.SampleOsc0
      Oscillator0.MultiSampleOsc0
      Oscillator0.SpectralOsc0
      Oscillator0.GranularOsc0

    To switch types, we set the active type to its default state and clear
    the inactive ones (or leave them as-is, depending on Serum's behavior).
    """
    params_dict = {p.name: p.value for p in operation.parameters}

    osc_index = params_dict.get("oscillator")
    osc_type = params_dict.get("type")

    # Validate oscillator index
    if osc_index is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_OSCILLATOR_INDEX",
            error_detail="set_oscillator_type requires oscillator index",
        )

    if osc_type is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_TYPE",
            error_detail="set_oscillator_type requires type parameter",
        )

    try:
        osc_idx = int(osc_index)
    except (ValueError, TypeError):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_OSCILLATOR_INDEX",
            error_detail=f"Oscillator index must be integer, got {osc_index}",
        )

    if osc_idx < 0:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="NEGATIVE_OSCILLATOR_INDEX",
            error_detail=f"Oscillator index must be >= 0, got {osc_idx}",
        )

    # Validate oscillator type
    osc_type_str = str(osc_type).lower()
    if osc_type_str not in SUPPORTED_OSCILLATOR_TYPES:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="UNKNOWN_OSCILLATOR_TYPE",
            error_detail=f"Unknown type: {osc_type}. Supported: {list(SUPPORTED_OSCILLATOR_TYPES.keys())}",
        )

    # Check that oscillator exists in context body
    oscillator_key = f"Oscillator{osc_idx}"
    if ctx.body and oscillator_key not in ctx.body:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="OSCILLATOR_NOT_FOUND",
            error_detail=f"Oscillator{osc_idx} not found in state body",
        )

    # Create mutation to set the oscillator type
    # We set the entire oscillator type dict to default/empty state
    # The specific structure depends on Serum's expectations; for now
    # we use a simple {"plainParams": "default"} representation
    osc_type_key = f"{SUPPORTED_OSCILLATOR_TYPES[osc_type_str]}{osc_idx}"
    mutation_path = f"{oscillator_key}.{osc_type_key}"

    mutation = Mutation(
        target_path=mutation_path,
        value={"plainParams": "default"},
        provenance=f"SerumOperation.{operation.operation_id}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"Oscillator type: Oscillator{osc_idx} → {osc_type}",
        notes=f"Path: {mutation_path}",
    )


def compiler_set_oscillator_parameter(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile set_oscillator_parameter() to Mutation[].

    Parameters:
      - oscillator (int): Oscillator index
      - parameter (str): Parameter name (semitone, fine, detune, level, octave, etc.)
      - value: Parameter value

    Returns:
      OperationResult with single Mutation for the parameter.
    """
    params_dict = {p.name: p.value for p in operation.parameters}

    osc_index = params_dict.get("oscillator")
    parameter = params_dict.get("parameter")
    value = params_dict.get("value")

    # Validate required parameters
    if osc_index is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_OSCILLATOR_INDEX",
            error_detail="set_oscillator_parameter requires oscillator index",
        )

    if parameter is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_PARAMETER",
            error_detail="set_oscillator_parameter requires parameter name",
        )

    if value is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_VALUE",
            error_detail="set_oscillator_parameter requires value",
        )

    try:
        osc_idx = int(osc_index)
    except (ValueError, TypeError):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_OSCILLATOR_INDEX",
            error_detail=f"Oscillator index must be integer, got {osc_index}",
        )

    param_lower = str(parameter).lower()
    if param_lower not in KNOWN_OSCILLATOR_PARAMS:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="UNKNOWN_PARAMETER",
            error_detail=f"Unknown parameter: {parameter}. Known: {list(KNOWN_OSCILLATOR_PARAMS.keys())}",
        )

    # Validate range
    param_spec = KNOWN_OSCILLATOR_PARAMS[param_lower]
    try:
        val_num = float(value)
    except (ValueError, TypeError):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_VALUE_TYPE",
            error_detail=f"Parameter {parameter} expects numeric value, got {value}",
        )

    if val_num < param_spec["min"] or val_num > param_spec["max"]:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="VALUE_OUT_OF_RANGE",
            error_detail=f"Parameter {parameter} range [{param_spec['min']}, {param_spec['max']}], got {val_num}",
        )

    # Build the mutation path
    # Assume path is: Oscillator{i}.plainParams.kParam{ParameterName}
    oscillator_key = f"Oscillator{osc_idx}"
    param_camel = "".join(w.capitalize() for w in param_lower.split("_"))
    mutation_path = f"{oscillator_key}.plainParams.kParam{param_camel}"

    mutation = Mutation(
        target_path=mutation_path,
        value=val_num,
        provenance=f"SerumOperation.{operation.operation_id}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"Oscillator parameter: Oscillator{osc_idx}.{parameter} = {val_num}",
        notes=f"Path: {mutation_path}",
    )


def compiler_load_wavetable(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile load_wavetable() to Mutation[].

    Parameters:
      - oscillator (int): Oscillator index (0, 1, 2, ...)
      - resource (str): Resource identifier (name, path, or canonical ID)

    Returns:
      OperationResult with Mutation for wavetable resource path.
    """
    from .resource_resolver import ResourceResolver
    from .resource_model import ResourceAvailability

    params_dict = {p.name: p.value for p in operation.parameters}

    osc_index = params_dict.get("oscillator")
    resource_id = params_dict.get("resource")

    if osc_index is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_OSCILLATOR_INDEX",
            error_detail="load_wavetable requires oscillator index",
        )

    if resource_id is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_RESOURCE",
            error_detail="load_wavetable requires resource identifier",
        )

    try:
        osc_idx = int(osc_index)
    except (ValueError, TypeError):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_OSCILLATOR_INDEX",
            error_detail=f"Oscillator index must be integer, got {osc_index}",
        )

    if osc_idx < 0:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="NEGATIVE_OSCILLATOR_INDEX",
            error_detail=f"Oscillator index must be >= 0, got {osc_idx}",
        )

    # Upper bound: must address a real oscillator in the current state.
    # No check existed here before (found during RESOURCE authority
    # integration audit) -- the real skeleton has Oscillator0-Oscillator4
    # (5 oscillators), verified this session via a live skeleton capture,
    # but that count is runtime/version data, not a hardcoded constant, so
    # validate against ctx.body directly rather than a literal "<=4".
    if ctx.body and f"Oscillator{osc_idx}" not in ctx.body:
        existing = sorted(k for k in ctx.body if k.startswith("Oscillator"))
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_OSCILLATOR_INDEX",
            error_detail=f"Oscillator{osc_idx} does not exist in current state "
                          f"(available: {existing})",
        )

    # Resolve resource
    resolver = ResourceResolver()
    resolution = resolver.resolve_wavetable(str(resource_id))

    if not resolution.success():
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error=f"RESOURCE_{resolution.availability.name}",
            error_detail=resolution.failed_reason(),
            notes=f"Searched: {', '.join(resolution.search_roots)}",
        )

    resource = resolution.resource
    mutation_path = resolver.resource_to_state_path(resource, osc_idx)

    mutation = Mutation(
        target_path=mutation_path,
        value=resource.serum_relative_path,
        provenance=f"SerumOperation.{operation.operation_id}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"Load wavetable: Oscillator{osc_idx} ← {resource.display_name}",
        notes=f"Resource: {resource.canonical_id} (hash: {resource.file_hash}). Path: {mutation_path} = {resource.serum_relative_path}",
    )


def compiler_load_sample(
    operation: SerumOperation,
    ctx: OperationContext,
) -> OperationResult:
    """Compile load_sample() to Mutation[].

    Parameters:
      - oscillator (int): Oscillator index
      - resource (str): Resource identifier (name, path, or canonical ID)

    Returns:
      OperationResult with Mutation for sample resource path.
    """
    from .resource_resolver import ResourceResolver
    from .resource_model import ResourceAvailability

    params_dict = {p.name: p.value for p in operation.parameters}

    osc_index = params_dict.get("oscillator")
    resource_id = params_dict.get("resource")

    if osc_index is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_OSCILLATOR_INDEX",
            error_detail="load_sample requires oscillator index",
        )

    if resource_id is None:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="MISSING_RESOURCE",
            error_detail="load_sample requires resource identifier",
        )

    try:
        osc_idx = int(osc_index)
    except (ValueError, TypeError):
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="INVALID_OSCILLATOR_INDEX",
            error_detail=f"Oscillator index must be integer, got {osc_index}",
        )

    if osc_idx < 0:
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error="NEGATIVE_OSCILLATOR_INDEX",
            error_detail=f"Oscillator index must be >= 0, got {osc_idx}",
        )

    # Resolve resource
    resolver = ResourceResolver()
    resolution = resolver.resolve_sample(str(resource_id))

    if not resolution.success():
        return OperationResult(
            operation_id=operation.operation_id,
            success=False,
            compilation_error=f"RESOURCE_{resolution.availability.name}",
            error_detail=resolution.failed_reason(),
            notes=f"Searched: {', '.join(resolution.search_roots)}",
        )

    resource = resolution.resource
    mutation_path = resolver.resource_to_state_path(resource, osc_idx)

    mutation = Mutation(
        target_path=mutation_path,
        value=resource.serum_relative_path,
        provenance=f"SerumOperation.{operation.operation_id}",
    )

    return OperationResult(
        operation_id=operation.operation_id,
        success=True,
        compiled_mutations=[mutation],
        mutation_description=f"Load sample: Oscillator{osc_idx} ← {resource.display_name}",
        notes=f"Resource: {resource.canonical_id} (hash: {resource.file_hash}). Path: {mutation_path} = {resource.serum_relative_path}",
    )
