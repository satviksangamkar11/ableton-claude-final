"""FX_EQ fixture.

FXEQ has no wet/dry gate in its plainParams (always fully active once
present in the chain) -- no exercise context needed beyond injecting a real
preset's FXRack0 (Altar preset) so both arms share an identical FX chain.
Proven via behavioral_seed_batch.py FXEQ.Freq1
(FXRack0.FX.0.FXEQ.plainParams.kParamFreq1 -> 8000 Hz, +7622.9 Hz,
CAUSAL_VERIFIED).

Reuses the exact injection mechanism already proven in
behavioral_seed_batch.py::_load_fx_skeleton.
"""

import copy

from serum2 import bridge, codec
from serum2.evidence import epoch as epoch_mod

VST3 = epoch_mod.SERUM_VST3

ALTAR_PRESET = r"C:\Users\Satvik\Documents\Xfer\Serum 2 Presets\Presets\Factory\Arp\ARP - Altar.SerumPreset"

EXERCISE_CONTEXT = []


def FX_EQ():
    """Returns (skeleton, exercise_context) for a fresh FX_EQ fixture.

    The skeleton's FXRack0 is replaced with the Altar preset's FXRack0
    (FX[0]=FXEQ, baseline Freq1=56.06 Hz), matching the proven pattern.
    """
    base_skeleton = bridge.capture_v8_skeleton(VST3)
    _, preset_body = codec.load_preset_file(ALTAR_PRESET)
    meta = copy.deepcopy(base_skeleton[0])
    body = copy.deepcopy(base_skeleton[1])
    body["FXRack0"] = copy.deepcopy(preset_body["FXRack0"])
    return (meta, body), list(EXERCISE_CONTEXT)
