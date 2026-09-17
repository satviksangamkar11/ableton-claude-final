"""OSC3_ACTIVE fixture.

OSC C (Oscillator 3) defaults OFF ('C Enable'=0.0) -- must be explicitly
gated on. Verified via direct VST3 parameter inspection that 'C Enable'/
'C Level' (idx 130/131) structurally mirror 'B Enable'/'B Level' (idx 75/76).
Proven via behavioral_seed_batch.py OSC3.Level (host_param 'C Level'
0.0->1.0, exercise_context=[('C Enable', 1.0)], +8.8 dB, CAUSAL_VERIFIED).
"""

from serum2 import bridge
from serum2.evidence import epoch as epoch_mod

VST3 = epoch_mod.SERUM_VST3

EXERCISE_CONTEXT = [("C Enable", 1.0)]


def OSC3_ACTIVE():
    """Returns (skeleton, exercise_context) for a fresh OSC3-active fixture."""
    skeleton = bridge.capture_v8_skeleton(VST3)
    return skeleton, list(EXERCISE_CONTEXT)
