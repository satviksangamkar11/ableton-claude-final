"""ENV1 fixture.

Env0 (Serum UI "Env 1") has no prerequisites and requires no exercise
context. Proven via behavioral_seed_batch.py Env1.Attack
(Env0.plainParams.kParamAttack -> 0.9, -2.2 dB, CAUSAL_VERIFIED) and
attack_qualified_complete_001_PASS_FULL.json.
"""

from serum2 import bridge
from serum2.evidence import epoch as epoch_mod

VST3 = epoch_mod.SERUM_VST3

EXERCISE_CONTEXT = []


def ENV1():
    """Returns (skeleton, exercise_context) for a fresh Env1 fixture."""
    skeleton = bridge.capture_v8_skeleton(VST3)
    return skeleton, list(EXERCISE_CONTEXT)
