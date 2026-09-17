"""FILTER1_ACTIVE fixture.

Filter 1 defaults OFF ('Filter 1 On'=0.0) -- must be explicitly gated on.
Proven via filter_cutoff_pilot.py / A_FILTER_CUTOFF_PILOT_EVIDENCE.json
(Filter1.Cutoff: VoiceFilter0.plainParams.kParamFreq -> 0.9,
exercise_context=[('Filter 1 On', 1.0)], +2684.3 Hz, CAUSAL_VERIFIED).
"""

from serum2 import bridge
from serum2.evidence import epoch as epoch_mod

VST3 = epoch_mod.SERUM_VST3

EXERCISE_CONTEXT = [("Filter 1 On", 1.0)]


def FILTER1_ACTIVE():
    """Returns (skeleton, exercise_context) for a fresh Filter1-active fixture."""
    skeleton = bridge.capture_v8_skeleton(VST3)
    return skeleton, list(EXERCISE_CONTEXT)
