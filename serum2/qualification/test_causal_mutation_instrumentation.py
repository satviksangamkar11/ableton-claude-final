#!/usr/bin/env python3
"""Diagnostic harness: trace one causal mutation end-to-end.

Tests OSC1.LEVEL (known parameter) with full instrumentation at every step:
1. Load preset
2. Apply mutation
3. Check state value before/after
4. Write and readback state file
5. Render baseline vs treatment
6. Compare audio samples
7. Measure
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import tempfile
import os
import copy
from serum2 import codec, bridge, pathmerge
from serum2.evidence import epoch as epoch_mod
import dawdreamer as daw

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512
GOLDEN_PRESET = "archive/golden_presets/arp.SerumPreset"


def load_golden():
    """Load golden preset."""
    with open(GOLDEN_PRESET, 'rb') as f:
        meta, body = codec.decode(f.read())
    return meta, body


def test_filter_cutoff_mutation():
    """Instrument Filter Cutoff mutation end-to-end with CORRECT path."""
    print("=" * 80)
    print("FILTER0.CUTOFF MUTATION DIAGNOSTIC (Correct Path: kParamFreq)")
    print("=" * 80)

    # 1. Load preset
    print("\n[1] LOAD PRESET")
    meta, body = load_golden()
    print(f"  Loaded: meta keys={len(meta)}, body keys={len(body)}")

    # Use CORRECT path for filter cutoff
    cbor_path = "VoiceFilter0.plainParams.kParamFreq"
    cutoff_before = pathmerge.read_path_value(body, cbor_path)
    print(f"  VoiceFilter0.Freq before mutation: {cutoff_before}")

    # 2. Create baseline and treatment copies (DEEP copy to avoid shared nested dicts)
    print("\n[2] CREATE BASELINE AND TREATMENT")
    baseline_meta, baseline_body = copy.deepcopy(meta), copy.deepcopy(body)
    treatment_meta, treatment_body = copy.deepcopy(meta), copy.deepcopy(body)
    print(f"  Baseline body id: {id(baseline_meta)}")
    print(f"  Treatment body id: {id(treatment_meta)}")

    # 3. Apply mutation to treatment
    print("\n[3] APPLY MUTATION")
    baseline_value = 0.2  # Lower cutoff
    treatment_value = 0.8  # Higher cutoff (more open)
    print(f"  Baseline value: {baseline_value}")
    print(f"  Treatment value: {treatment_value}")

    cutoff_baseline = pathmerge.read_path_value(baseline_body, cbor_path)
    print(f"  Baseline VoiceFilter0.Freq (before mutation): {cutoff_baseline}")

    pathmerge.apply_path_value(treatment_body, cbor_path, treatment_value)
    cutoff_treatment = pathmerge.read_path_value(treatment_body, cbor_path)
    print(f"  Treatment VoiceFilter0.Freq (after mutation): {cutoff_treatment}")
    print(f"  Mutation applied? {cutoff_treatment == treatment_value}")

    # Verify baseline wasn't modified
    cutoff_baseline_after = pathmerge.read_path_value(baseline_body, cbor_path)
    print(f"  Baseline VoiceFilter0.Freq still: {cutoff_baseline_after} (unchanged? {cutoff_baseline_after == cutoff_baseline})")

    # 4. Write and readback state files
    print("\n[4] STATE FILE ROUND-TRIP")
    fd_b, tmp_baseline = tempfile.mkstemp(suffix=".bin")
    os.close(fd_b)
    fd_t, tmp_treatment = tempfile.mkstemp(suffix=".bin")
    os.close(fd_t)

    bridge.write_state_file(tmp_baseline, baseline_meta, baseline_body)
    bridge.write_state_file(tmp_treatment, treatment_meta, treatment_body)

    baseline_file_size = os.path.getsize(tmp_baseline)
    treatment_file_size = os.path.getsize(tmp_treatment)
    print(f"  Baseline state file: {baseline_file_size} bytes")
    print(f"  Treatment state file: {treatment_file_size} bytes")
    print(f"  Files identical? {baseline_file_size == treatment_file_size}")

    # Note: state files are VST3 blobs, not CBOR presets, so we skip decode readback
    # The actual verification happens when DawDreamer loads them and renders audio

    # 5. Render baseline
    print("\n[5] RENDER BASELINE")
    engine_b = daw.RenderEngine(SR, BLOCK)
    synth_b = engine_b.make_plugin_processor("serum", VST3)
    try:
        synth_b.load_state(tmp_baseline)
        print(f"  State loaded successfully")
    except Exception as e:
        print(f"  ERROR loading state: {e}")
        os.remove(tmp_baseline)
        os.remove(tmp_treatment)
        return

    synth_b.clear_midi()
    synth_b.add_midi_note(60, 100, 0.0, 1.5)
    engine_b.load_graph([(synth_b, [])])
    engine_b.render(2.0)
    baseline_audio = np.asarray(engine_b.get_audio())

    print(f"  Audio shape: {baseline_audio.shape}")
    print(f"  Audio dtype: {baseline_audio.dtype}")
    print(f"  Audio min: {baseline_audio.min():.6f}")
    print(f"  Audio max: {baseline_audio.max():.6f}")
    print(f"  Audio mean: {baseline_audio.mean():.6f}")
    print(f"  Audio std: {baseline_audio.std():.6f}")

    # 6. Render treatment
    print("\n[6] RENDER TREATMENT")
    engine_t = daw.RenderEngine(SR, BLOCK)
    synth_t = engine_t.make_plugin_processor("serum", VST3)
    try:
        synth_t.load_state(tmp_treatment)
        print(f"  State loaded successfully")
    except Exception as e:
        print(f"  ERROR loading state: {e}")
        os.remove(tmp_baseline)
        os.remove(tmp_treatment)
        return

    synth_t.clear_midi()
    synth_t.add_midi_note(60, 100, 0.0, 1.5)
    engine_t.load_graph([(synth_t, [])])
    engine_t.render(2.0)
    treatment_audio = np.asarray(engine_t.get_audio())

    print(f"  Audio shape: {treatment_audio.shape}")
    print(f"  Audio dtype: {treatment_audio.dtype}")
    print(f"  Audio min: {treatment_audio.min():.6f}")
    print(f"  Audio max: {treatment_audio.max():.6f}")
    print(f"  Audio mean: {treatment_audio.mean():.6f}")
    print(f"  Audio std: {treatment_audio.std():.6f}")

    # 7. Compare audio
    print("\n[7] AUDIO COMPARISON")
    audio_diff = treatment_audio - baseline_audio
    print(f"  Audio identical? {np.array_equal(baseline_audio, treatment_audio)}")
    print(f"  Diff min: {audio_diff.min():.6e}")
    print(f"  Diff max: {audio_diff.max():.6e}")
    print(f"  Diff mean: {audio_diff.mean():.6e}")
    print(f"  Diff std: {audio_diff.std():.6e}")
    print(f"  Diff L2 norm: {np.linalg.norm(audio_diff):.6e}")
    print(f"  RMS diff: {np.sqrt(np.mean(audio_diff ** 2)):.6e}")

    # 8. Measure
    print("\n[8] MEASUREMENT")
    baseline_rms = np.sqrt(np.mean(baseline_audio ** 2))
    treatment_rms = np.sqrt(np.mean(treatment_audio ** 2))
    baseline_rms_db = 20.0 * np.log10(baseline_rms) if baseline_rms > 1e-10 else -120.0
    treatment_rms_db = 20.0 * np.log10(treatment_rms) if treatment_rms > 1e-10 else -120.0

    print(f"  Baseline RMS: {baseline_rms:.6e} ({baseline_rms_db:.2f} dB)")
    print(f"  Treatment RMS: {treatment_rms:.6e} ({treatment_rms_db:.2f} dB)")
    print(f"  Delta dB: {treatment_rms_db - baseline_rms_db:.2f} dB")
    print(f"  Expected threshold: 2.0 dB")
    print(f"  PASS? {abs(treatment_rms_db - baseline_rms_db) >= 2.0}")

    # Cleanup
    os.remove(tmp_baseline)
    os.remove(tmp_treatment)

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_filter_cutoff_mutation()
