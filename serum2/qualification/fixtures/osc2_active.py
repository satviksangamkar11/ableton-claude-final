"""OSC2_ACTIVE fixture.

OSC B (Oscillator 2) defaults OFF ('B Enable'=0.0) -- must be explicitly
gated on. Proven via behavioral_seed_batch.py OSC2.Level (host_param
'B Level' 0.0->1.0, exercise_context=[('B Enable', 1.0)], +8.8 dB,
CAUSAL_VERIFIED).
"""

from serum2 import bridge
from serum2.evidence import epoch as epoch_mod

VST3 = epoch_mod.SERUM_VST3

EXERCISE_CONTEXT = [("B Enable", 1.0)]


def OSC2_ACTIVE():
    """Returns (skeleton, exercise_context) for a fresh OSC2-active fixture."""
    skeleton = bridge.capture_v8_skeleton(VST3)
    return skeleton, list(EXERCISE_CONTEXT)
