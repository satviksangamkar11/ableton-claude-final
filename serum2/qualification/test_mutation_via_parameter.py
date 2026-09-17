#!/usr/bin/env python3
"""Test: apply filter mutation via set_parameter() AFTER load, not via state.

Check if Serum responds to parameter changes via the VST3 parameter API
instead of through state dict mutations.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import tempfile
import os
import copy
from serum2 import codec, bridge
from serum2.evidence import epoch as epoch_mod
import dawdreamer as daw

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512
GOLDEN_PRESET = "archive/golden_presets/arp.SerumPreset"


def test_filter_via_parameter():
    """Apply filter cutoff via set_parameter() after load."""
    print("=" * 80)
    print("FILTER MUTATION VIA set_parameter() (NOT state dict)")
    print("=" * 80)

    # Load golden preset
    with open(GOLDEN_PRESET, 'rb') as f:
        meta, body = codec.decode(f.read())

    print(f"\n[1] Load preset and create identical baseline/treatment states")
    baseline_meta, baseline_body = copy.deepcopy(meta), copy.deepcopy(body)
    treatment_meta, treatment_body = copy.deepcopy(meta), copy.deepcopy(body)

    # Write state files (both identical)
    fd_b, tmp_baseline = tempfile.mkstemp(suffix=".bin")
    os.close(fd_b)
    fd_t, tmp_treatment = tempfile.mkstemp(suffix=".bin")
    os.close(fd_t)

    bridge.write_state_file(tmp_baseline, baseline_meta, baseline_body)
    bridge.write_state_file(tmp_treatment, treatment_meta, treatment_body)

    # Render baseline (no parameter change)
    print(f"\n[2] Render BASELINE")
    engine_b = daw.RenderEngine(SR, BLOCK)
    synth_b = engine_b.make_plugin_processor("serum", VST3)
    synth_b.load_state(tmp_baseline)

    params = synth_b.get_parameters_description()
    print(f"  Serum has {len(params)} parameters")

    # Find filter cutoff parameter
    filter_param = None
    for p in params:
        if 'cutoff' in p['name'].lower() or 'freq' in p['name'].lower():
            print(f"    Found param: {p['name']} (index {p['index']}, min {p['min']}, max {p['max']})")
            if filter_param is None and 'cutoff' in p['name'].lower():
                filter_param = p

    synth_b.clear_midi()
    synth_b.add_midi_note(60, 100, 0.0, 1.5)
    engine_b.load_graph([(synth_b, [])])
    engine_b.render(2.0)
    baseline_audio = np.asarray(engine_b.get_audio())

    baseline_rms_db = 20.0 * np.log10(np.sqrt(np.mean(baseline_audio ** 2)))
    print(f"  Baseline RMS: {baseline_rms_db:.2f} dB")

    # Render treatment (with parameter change via set_parameter)
    print(f"\n[3] Render TREATMENT (with set_parameter change)")
    engine_t = daw.RenderEngine(SR, BLOCK)
    synth_t = engine_t.make_plugin_processor("serum", VST3)
    synth_t.load_state(tmp_treatment)

    # Find "Filter 1 Freq" specifically (not Cutoff Rand)
    filter1_freq = None
    for p in params:
        if p['name'] == 'Filter 1 Freq':
            filter1_freq = p
            break

    if filter1_freq:
        print(f"  Setting {filter1_freq['name']} (index {filter1_freq['index']}) to 100 Hz (very low)")
        synth_t.set_parameter(filter1_freq['index'], 100.0)
    else:
        print(f"  WARNING: Could not find 'Filter 1 Freq' parameter!")

    synth_t.clear_midi()
    synth_t.add_midi_note(60, 100, 0.0, 1.5)
    engine_t.load_graph([(synth_t, [])])
    engine_t.render(2.0)
    treatment_audio = np.asarray(engine_t.get_audio())

    treatment_rms_db = 20.0 * np.log10(np.sqrt(np.mean(treatment_audio ** 2)))
    print(f"  Treatment RMS: {treatment_rms_db:.2f} dB")

    # Compare
    print(f"\n[4] COMPARISON")
    print(f"  Audio identical? {np.array_equal(baseline_audio, treatment_audio)}")
    delta_db = abs(treatment_rms_db - baseline_rms_db)
    print(f"  Delta RMS: {delta_db:.2f} dB")
    print(f"  Effect observed? {delta_db >= 2.0}")

    os.remove(tmp_baseline)
    os.remove(tmp_treatment)
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_filter_via_parameter()
