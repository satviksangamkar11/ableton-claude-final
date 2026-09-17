"""OSC1_ACTIVE fixture.

OSC A (Oscillator 1) is active by default ('A Enable'=1.0) -- no exercise
context is required. Proven via behavioral_seed_batch.py OSC1.Level
(host_param 'A Level' 0.25->1.0, +24.0 dB, CAUSAL_VERIFIED).
"""

from serum2 import bridge
from serum2.evidence import epoch as epoch_mod

VST3 = epoch_mod.SERUM_VST3

EXERCISE_CONTEXT = []


def OSC1_ACTIVE():
    """Returns (skeleton, exercise_context) for a fresh OSC1-active fixture."""
    skeleton = bridge.capture_v8_skeleton(VST3)
    return skeleton, list(EXERCISE_CONTEXT)
