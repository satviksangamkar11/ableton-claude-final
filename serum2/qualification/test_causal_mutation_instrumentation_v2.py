#!/usr/bin/env python3
"""Diagnostic v2: trace Filter.Cutoff mutation end-to-end WITH exercise context.

Corrects test_causal_mutation_instrumentation.py's methodology:
  - Uses bridge.capture_v8_skeleton() (fresh default state), not a static preset
  - Applies exercise_context ("Filter 1 On"=1.0) via set_parameter() to BOTH arms
    BEFORE rendering, matching the proven filter_cutoff_pilot.py pattern

This proves the root cause of the null deltas in
causal_qualification_v1_scalar_batch.py: missing exercise context, not a
DawDreamer/Serum limitation.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import tempfile
import os
import copy
from serum2 import bridge, pathmerge
from serum2.evidence import epoch as epoch_mod
import dawdreamer as daw

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512


def _apply_host_context(synth, context):
    if not context:
        return
    params = synth.get_parameters_description()
    by_name = {p["name"]: p["index"] for p in params}
    for name, value in context:
        idx = by_name[name]
        before = synth.get_parameter(idx) if hasattr(synth, "get_parameter") else None
        synth.set_parameter(idx, float(value))
        print(f"    set_parameter({name!r}, {value}) — host param before={before}")


def test_filter_cutoff_with_exercise_context():
    print("=" * 80)
    print("FILTER.CUTOFF DIAGNOSTIC v2 — WITH EXERCISE CONTEXT")
    print("=" * 80)

    cbor_path = "VoiceFilter0.plainParams.kParamFreq"
    baseline_value = None  # use skeleton default (no mutation on baseline)
    treatment_value = 0.9
    exercise_context = [("Filter 1 On", 1.0)]

    # 1. Fresh skeleton (NOT a static preset)
    print("\n[1] CAPTURE FRESH SKELETON")
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton
    cutoff_default = pathmerge.read_path_value(body, cbor_path)
    print(f"  Skeleton VoiceFilter0.Freq default: {cutoff_default}")

    # 2. Build baseline/treatment bodies (deep copy)
    print("\n[2] BUILD ARMS (deepcopy)")
    baseline_meta, baseline_body = copy.deepcopy(meta), copy.deepcopy(body)
    treatment_meta, treatment_body = copy.deepcopy(meta), copy.deepcopy(body)
    pathmerge.apply_path_value(treatment_body, cbor_path, treatment_value)
    print(f"  Baseline kParamFreq: {pathmerge.read_path_value(baseline_body, cbor_path)}")
    print(f"  Treatment kParamFreq: {pathmerge.read_path_value(treatment_body, cbor_path)}")

    # 3. Write state files
    print("\n[3] WRITE STATE FILES")
    fd_b, tmp_baseline = tempfile.mkstemp(suffix=".bin"); os.close(fd_b)
    fd_t, tmp_treatment = tempfile.mkstemp(suffix=".bin"); os.close(fd_t)
    bridge.write_state_file(tmp_baseline, baseline_meta, baseline_body)
    bridge.write_state_file(tmp_treatment, treatment_meta, treatment_body)
    print(f"  Baseline file: {os.path.getsize(tmp_baseline)} bytes")
    print(f"  Treatment file: {os.path.getsize(tmp_treatment)} bytes")

    # 4. Render BASELINE with exercise context applied
    print("\n[4] RENDER BASELINE (with exercise context: Filter 1 On=1.0)")
    engine_b = daw.RenderEngine(SR, BLOCK)
    synth_b = engine_b.make_plugin_processor("serum", VST3)
    synth_b.load_state(tmp_baseline)
    _apply_host_context(synth_b, exercise_context)
    synth_b.clear_midi()
    synth_b.add_midi_note(60, 100, 0.0, 1.5)
    engine_b.load_graph([(synth_b, [])])
    engine_b.render(2.0)
    baseline_audio = np.asarray(engine_b.get_audio())
    print(f"  Audio shape: {baseline_audio.shape}, min={baseline_audio.min():.4f}, "
          f"max={baseline_audio.max():.4f}, mean={baseline_audio.mean():.6f}, std={baseline_audio.std():.4f}")

    # 5. Render TREATMENT with exercise context applied
    print("\n[5] RENDER TREATMENT (with exercise context: Filter 1 On=1.0)")
    engine_t = daw.RenderEngine(SR, BLOCK)
    synth_t = engine_t.make_plugin_processor("serum", VST3)
    synth_t.load_state(tmp_treatment)
    _apply_host_context(synth_t, exercise_context)
    synth_t.clear_midi()
    synth_t.add_midi_note(60, 100, 0.0, 1.5)
    engine_t.load_graph([(synth_t, [])])
    engine_t.render(2.0)
    treatment_audio = np.asarray(engine_t.get_audio())
    print(f"  Audio shape: {treatment_audio.shape}, min={treatment_audio.min():.4f}, "
          f"max={treatment_audio.max():.4f}, mean={treatment_audio.mean():.6f}, std={treatment_audio.std():.4f}")

    # 6. Compare
    print("\n[6] AUDIO COMPARISON")
    diff = treatment_audio - baseline_audio
    identical = np.array_equal(baseline_audio, treatment_audio)
    print(f"  Identical? {identical}")
    print(f"  Diff L2 norm: {np.linalg.norm(diff):.6e}")
    print(f"  Diff RMS: {np.sqrt(np.mean(diff ** 2)):.6e}")

    # 7. Measure
    print("\n[7] MEASUREMENT")
    from serum2.evidence.measure import spectral_centroid_hz, rms_db
    baseline_centroid = spectral_centroid_hz(baseline_audio)
    treatment_centroid = spectral_centroid_hz(treatment_audio)
    print(f"  Baseline spectral centroid: {baseline_centroid:.1f} Hz")
    print(f"  Treatment spectral centroid: {treatment_centroid:.1f} Hz")
    print(f"  Delta: {treatment_centroid - baseline_centroid:+.1f} Hz")
    print(f"  Effect observed (>200 Hz threshold)? {abs(treatment_centroid - baseline_centroid) >= 200.0}")

    os.remove(tmp_baseline)
    os.remove(tmp_treatment)
    print("\n" + "=" * 80)

    assert not identical, "REGRESSION: audio still identical even with exercise context"
    assert abs(treatment_centroid - baseline_centroid) >= 200.0, "No effect observed above threshold"
    print("[PASS] Exercise context resolves the null-delta issue")


if __name__ == "__main__":
    test_filter_cutoff_with_exercise_context()
