"""FX parameter resolver: effect + parameter → Serum v8 state path.

Maps human FX operations to the underlying state structures discovered in
serum2/evidence/fixtures.py and FORENSIC_V8_STATE_ANALYSIS.md

FXRack{R}.FX.{N}.FX{Type}.plainParams.kParam{Name}

Example paths (from forensic analysis):
- FXRack0.FX.2.FXDistortion.plainParams.kParamDrive
- FXRack0.FX.N.FXEQ.plainParams.kParamFreq1
"""

from __future__ import annotations
from typing import Optional, Dict, Tuple, Any
from dataclasses import dataclass


@dataclass(frozen=True)
class FXParameterPath:
    """Resolved FX parameter path."""
    rack_index: int
    slot_index: int
    effect_type: str  # "Distortion", "EQ", "Delay", "Reverb", "Compressor", "Chorus"
    parameter_name: str
    state_path: str  # Full dotted path: FXRack0.FX.2.FXDistortion.plainParams.kParamDrive
    value_type: str  # "float", "int", "string", "enum"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: str = ""


# FX parameter catalog (discovered from state analysis)
# Each entry: (effect_type, parameter_name) → (state_path_template, type, min, max)
_FX_PARAMETERS: Dict[Tuple[str, str], Tuple[str, str, Optional[float], Optional[float]]] = {
    # Distortion
    ("Distortion", "Drive"): (
        "FXRack{R}.FX.{N}.FXDistortion.plainParams.kParamDrive",
        "float",
        0.0,
        100.0,
    ),
    ("Distortion", "Tone"): (
        "FXRack{R}.FX.{N}.FXDistortion.plainParams.kParamTone",
        "float",
        0.0,
        100.0,
    ),
    ("Distortion", "LevelOut"): (
        "FXRack{R}.FX.{N}.FXDistortion.plainParams.kParamLevelOut",
        "float",
        0.0,
        100.0,
    ),

    # EQ
    ("EQ", "Freq1"): (
        "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamFreq1",
        "float",
        20.0,
        20000.0,
    ),
    ("EQ", "Freq2"): (
        "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamFreq2",
        "float",
        20.0,
        20000.0,
    ),
    ("EQ", "Reso1"): (
        "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamReso1",
        "float",
        0.1,
        10.0,
    ),
    ("EQ", "Reso2"): (
        "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamReso2",
        "float",
        0.1,
        10.0,
    ),
    ("EQ", "Gain1"): (
        "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamGain1",
        "float",
        -24.0,
        24.0,
    ),
    ("EQ", "Gain2"): (
        "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamGain2",
        "float",
        -24.0,
        24.0,
    ),
    ("EQ", "LevelOut"): (
        "FXRack{R}.FX.{N}.FXEQ.plainParams.kParamLevelOut",
        "float",
        0.0,
        100.0,
    ),

    # Delay (placeholder — structure TBD in actual corpus)
    ("Delay", "Time"): (
        "FXRack{R}.FX.{N}.FXDelay.plainParams.kParamTime",
        "float",
        0.0,
        10000.0,
    ),
    ("Delay", "Feedback"): (
        "FXRack{R}.FX.{N}.FXDelay.plainParams.kParamFeedback",
        "float",
        0.0,
        100.0,
    ),
    ("Delay", "Mix"): (
        "FXRack{R}.FX.{N}.FXDelay.plainParams.kParamMix",
        "float",
        0.0,
        100.0,
    ),

    # Reverb (placeholder)
    ("Reverb", "Time"): (
        "FXRack{R}.FX.{N}.FXReverb.plainParams.kParamTime",
        "float",
        0.1,
        100.0,
    ),
    ("Reverb", "Damping"): (
        "FXRack{R}.FX.{N}.FXReverb.plainParams.kParamDamping",
        "float",
        0.0,
        100.0,
    ),
    ("Reverb", "Mix"): (
        "FXRack{R}.FX.{N}.FXReverb.plainParams.kParamMix",
        "float",
        0.0,
        100.0,
    ),

    # Compressor (placeholder)
    ("Compressor", "Threshold"): (
        "FXRack{R}.FX.{N}.FXCompressor.plainParams.kParamThreshold",
        "float",
        -60.0,
        0.0,
    ),
    ("Compressor", "Ratio"): (
        "FXRack{R}.FX.{N}.FXCompressor.plainParams.kParamRatio",
        "float",
        1.0,
        10.0,
    ),
    ("Compressor", "Attack"): (
        "FXRack{R}.FX.{N}.FXCompressor.plainParams.kParamAttack",
        "float",
        0.0,
        100.0,
    ),
    ("Compressor", "Release"): (
        "FXRack{R}.FX.{N}.FXCompressor.plainParams.kParamRelease",
        "float",
        0.0,
        1000.0,
    ),

    # Chorus
    ("Chorus", "Rate"): (
        "FXRack{R}.FX.{N}.FXChorus.plainParams.kParamRate",
        "float",
        0.1,
        10.0,
    ),
    ("Chorus", "Depth"): (
        "FXRack{R}.FX.{N}.FXChorus.plainParams.kParamDepth",
        "float",
        0.0,
        100.0,
    ),
    ("Chorus", "Mix"): (
        "FXRack{R}.FX.{N}.FXChorus.plainParams.kParamMix",
        "float",
        0.0,
        100.0,
    ),

    # BODE (Frequency Shifter)
    ("BODE", "Frequency"): (
        "FXRack{R}.FX.{N}.FXBODE.plainParams.kParamFrequency",
        "float",
        0.0,
        10000.0,
    ),
    ("BODE", "Range"): (
        "FXRack{R}.FX.{N}.FXBODE.plainParams.kParamRange",
        "float",
        0.0,
        100.0,
    ),
    ("BODE", "Direction"): (
        "FXRack{R}.FX.{N}.FXBODE.plainParams.kParamDirection",
        "int",
        0,
        1,
    ),
    ("BODE", "Mix"): (
        "FXRack{R}.FX.{N}.FXBODE.plainParams.kParamMix",
        "float",
        0.0,
        100.0,
    ),

    # Flanger
    ("Flanger", "Rate"): (
        "FXRack{R}.FX.{N}.FXFlanger.plainParams.kParamRate",
        "float",
        0.1,
        10.0,
    ),
    ("Flanger", "Depth"): (
        "FXRack{R}.FX.{N}.FXFlanger.plainParams.kParamDepth",
        "float",
        0.0,
        100.0,
    ),
    ("Flanger", "Feedback"): (
        "FXRack{R}.FX.{N}.FXFlanger.plainParams.kParamFeedback",
        "float",
        -100.0,
        100.0,
    ),
    ("Flanger", "Phase"): (
        "FXRack{R}.FX.{N}.FXFlanger.plainParams.kParamPhase",
        "float",
        0.0,
        360.0,
    ),
    ("Flanger", "Mix"): (
        "FXRack{R}.FX.{N}.FXFlanger.plainParams.kParamMix",
        "float",
        0.0,
        100.0,
    ),

    # Phaser
    ("Phaser", "Frequency"): (
        "FXRack{R}.FX.{N}.FXPhaser.plainParams.kParamFrequency",
        "float",
        20.0,
        20000.0,
    ),
    ("Phaser", "Feedback"): (
        "FXRack{R}.FX.{N}.FXPhaser.plainParams.kParamFeedback",
        "float",
        -100.0,
        100.0,
    ),
    ("Phaser", "Phase"): (
        "FXRack{R}.FX.{N}.FXPhaser.plainParams.kParamPhase",
        "float",
        0.0,
        360.0,
    ),
    ("Phaser", "Mix"): (
        "FXRack{R}.FX.{N}.FXPhaser.plainParams.kParamMix",
        "float",
        0.0,
        100.0,
    ),

    # Utility
    ("Utility", "Gain"): (
        "FXRack{R}.FX.{N}.FXUtility.plainParams.kParamGain",
        "float",
        -100.0,
        100.0,
    ),
    ("Utility", "Phase"): (
        "FXRack{R}.FX.{N}.FXUtility.plainParams.kParamPhase",
        "float",
        0.0,
        1.0,
    ),
    ("Utility", "Mono"): (
        "FXRack{R}.FX.{N}.FXUtility.plainParams.kParamMono",
        "int",
        0,
        1,
    ),
    ("Utility", "Mix"): (
        "FXRack{R}.FX.{N}.FXUtility.plainParams.kParamMix",
        "float",
        0.0,
        100.0,
    ),

    # Convolve (Convolution Reverb)
    ("Convolve", "IR"): (
        "FXRack{R}.FX.{N}.FXConvolve.plainParams.kParamIR",
        "string",
        None,
        None,
    ),
    ("Convolve", "IRGain"): (
        "FXRack{R}.FX.{N}.FXConvolve.plainParams.kParamIRGain",
        "float",
        -100.0,
        100.0,
    ),
    ("Convolve", "Attack"): (
        "FXRack{R}.FX.{N}.FXConvolve.plainParams.kParamAttack",
        "float",
        0.0,
        1000.0,
    ),
    ("Convolve", "Decay"): (
        "FXRack{R}.FX.{N}.FXConvolve.plainParams.kParamDecay",
        "float",
        0.0,
        10000.0,
    ),
    ("Convolve", "Damping"): (
        "FXRack{R}.FX.{N}.FXConvolve.plainParams.kParamDamping",
        "float",
        0.0,
        100.0,
    ),
    ("Convolve", "Mix"): (
        "FXRack{R}.FX.{N}.FXConvolve.plainParams.kParamMix",
        "float",
        0.0,
        100.0,
    ),

    # Hyper (Dimension)
    ("Hyper", "Rate"): (
        "FXRack{R}.FX.{N}.FXHyper.plainParams.kParamRate",
        "float",
        0.1,
        10.0,
    ),
    ("Hyper", "Unison"): (
        "FXRack{R}.FX.{N}.FXHyper.plainParams.kParamUnison",
        "int",
        1,
        7,
    ),
    ("Hyper", "Detune"): (
        "FXRack{R}.FX.{N}.FXHyper.plainParams.kParamDetune",
        "float",
        0.0,
        100.0,
    ),
    ("Hyper", "Mix"): (
        "FXRack{R}.FX.{N}.FXHyper.plainParams.kParamMix",
        "float",
        0.0,
        100.0,
    ),

    # Filter (as FX)
    ("FilterFX", "Type"): (
        "FXRack{R}.FX.{N}.FXFilterFX.plainParams.kParamType",
        "int",
        0,
        10,
    ),
    ("FilterFX", "Cutoff"): (
        "FXRack{R}.FX.{N}.FXFilterFX.plainParams.kParamCutoff",
        "float",
        20.0,
        20000.0,
    ),
    ("FilterFX", "Resonance"): (
        "FXRack{R}.FX.{N}.FXFilterFX.plainParams.kParamResonance",
        "float",
        0.0,
        100.0,
    ),
    ("FilterFX", "Drive"): (
        "FXRack{R}.FX.{N}.FXFilterFX.plainParams.kParamDrive",
        "float",
        0.0,
        100.0,
    ),
    ("FilterFX", "Mix"): (
        "FXRack{R}.FX.{N}.FXFilterFX.plainParams.kParamMix",
        "float",
        0.0,
        100.0,
    ),
}


def resolve_fx_parameter(
    effect_type: str,
    parameter_name: str,
    rack_index: int = 0,
    slot_index: int = 0,
) -> Optional[FXParameterPath]:
    """Resolve an FX parameter to its state path.

    Args:
        effect_type: "Distortion", "EQ", "Delay", "Reverb", "Compressor", "Chorus"
        parameter_name: Parameter name (e.g., "Drive", "Freq1")
        rack_index: FX rack (0-2)
        slot_index: FX slot within rack (0-...)

    Returns:
        FXParameterPath with full state path, or None if unresolved
    """
    key = (effect_type, parameter_name)

    if key not in _FX_PARAMETERS:
        return None

    path_template, value_type, min_val, max_val = _FX_PARAMETERS[key]
    state_path = path_template.format(R=rack_index, N=slot_index)

    return FXParameterPath(
        rack_index=rack_index,
        slot_index=slot_index,
        effect_type=effect_type,
        parameter_name=parameter_name,
        state_path=state_path,
        value_type=value_type,
        min_value=min_val,
        max_value=max_val,
    )


def list_fx_parameters(effect_type: Optional[str] = None) -> Dict[str, Any]:
    """List all known FX parameters, optionally filtered by effect type."""
    if effect_type is None:
        return {
            f"{eff}/{param}": info
            for (eff, param), info in _FX_PARAMETERS.items()
        }
    else:
        return {
            param: info[0]  # path template
            for (eff, param), info in _FX_PARAMETERS.items()
            if eff == effect_type
        }
