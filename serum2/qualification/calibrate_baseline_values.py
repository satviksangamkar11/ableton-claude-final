"""Calibrate baseline values for seed experiments.

For each control parameter, read its actual value in the default Serum state,
then recommend a treatment value that produces meaningful contrast.
"""

import json
from serum2 import bridge, pathmerge
from serum2.evidence import epoch

# Parameters to probe
PROBES = [
    ("Filter1.Resonance", "VoiceFilter0.plainParams.kParamReso"),
    ("Filter2.Cutoff", "VoiceFilter1.plainParams.kParamFreq"),
    ("OSC1.Level", "VoiceOsc0.plainParams.kParamLevel"),
    ("OSC1.Detune", "VoiceOsc0.plainParams.kParamDetune"),
    ("Env1.Attack", "VoiceEnv0.plainParams.kParamAttackTime"),
    ("Env1.Release", "VoiceEnv0.plainParams.kParamReleaseTime"),
    ("Filter1.Drive", "VoiceFilter0.plainParams.kParamDrive"),
]

def probe_parameter(path):
    """Read actual baseline value for a parameter."""
    skeleton = bridge.capture_v8_skeleton(epoch.SERUM_VST3)
    meta, body = skeleton

    try:
        val = pathmerge.read_path_value(body, path)
        return val
    except Exception as e:
        return None


def recommend_treatment(baseline_val, control_name):
    """Recommend a treatment value that contrasts with baseline.

    Strategy: if baseline is near 0, go to 1.0; if near 1, go to 0.0;
    if in middle, go to opposite extreme.
    """
    if baseline_val is None:
        return None, "baseline unreadable"

    if isinstance(baseline_val, str):
        return None, f"baseline is string: {baseline_val}"

    # Treat as normalized 0-1 parameter
    if baseline_val < 0.3:
        treatment = 0.9
        reason = "baseline low, set to high"
    elif baseline_val > 0.7:
        treatment = 0.1
        reason = "baseline high, set to low"
    else:
        # Mid-range: go opposite direction
        if baseline_val < 0.5:
            treatment = 0.9
            reason = "baseline mid-low, set to high"
        else:
            treatment = 0.1
            reason = "baseline mid-high, set to low"

    return treatment, reason


print("=" * 70)
print("BASELINE VALUE CALIBRATION")
print("=" * 70)
print()

for control_name, cbor_path in PROBES:
    baseline_val = probe_parameter(cbor_path)
    treatment_val, reason = recommend_treatment(baseline_val, control_name)

    print("{:30s}".format(control_name))
    print("  CBOR path:        {}".format(cbor_path))
    print("  Baseline value:   {}".format(baseline_val))
    print("  Recommended treat: {}  ({})".format(treatment_val, reason))
    print()
