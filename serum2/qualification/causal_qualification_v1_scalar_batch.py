#!/usr/bin/env python3
"""V1 causal qualification batch: scalar amplitude/cutoff/envelope mutations.

REVISED (v2) after root-cause diagnosis: the original batch used incorrect
CBOR paths (kParamLevel/kParamCutoff/kParamAttackTime — none of which exist
in Serum's body schema) and loaded a static preset with no exercise context,
so mutations never reached the audio engine. All 7 experiments silently
produced 0.0 dB/Hz delta (CAUSAL_BLOCKED/CAUSAL_FAILED), not because Serum/
DawDreamer cannot be causally mutated, but because of two combined bugs:

  1. Shallow copy (`dict.copy()`) let baseline/treatment share nested dicts.
  2. Wrong field names + no exercise context to gate the mutated module.

Root cause proven via serum2/qualification/test_causal_mutation_instrumentation_v2.py,
which reproduces the existing filter_cutoff_pilot.py CAUSAL_VERIFIED result
(463.1 Hz -> 3147.4 Hz) end-to-end with full step tracing.

Corrected methodology (mirrors existing proven pilots):
  - Uses bridge.capture_v8_skeleton() (fresh default state), not a static preset.
  - Uses copy.deepcopy() for baseline/treatment isolation.
  - Uses verified CBOR paths: kParamVolume (osc), kParamFreq (filter),
    kParamAttack (env).
  - Applies exercise_context (host-level gate parameters) via set_parameter()
    to BOTH arms where the module requires activation (filters default OFF).
  - OSC.Level and ENV.Attack need no exercise context (verified: "A Enable"
    defaults to 1.0; Attack has no prerequisites per
    attack_qualified_complete_001_PASS_FULL.json).

Each experiment:
  fresh skeleton -> render baseline (+ exercise context)
                 -> render with ONE capability mutated (+ same exercise context)
                 -> measure audio difference
                 -> compare to attribution threshold
                 -> record CAUSAL_VERIFIED or CAUSAL_FAILED
"""

import sys
import json
import tempfile
import os
import copy
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import dawdreamer as daw
from serum2 import bridge, pathmerge
from serum2.evidence import epoch as epoch_mod
from serum2.evidence.measure import (
    rms_db, spectral_centroid_hz, tail_rms_db, attack_onset_rms_db
)

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512

# Scalar batch: (semantic_id, cbor_path, treatment_value, measurement_names, exercise_context)
# baseline is always the skeleton default (no baseline override) so the
# comparison is "default state" vs "default state + single mutation" —
# matching the proven filter_cutoff_pilot.py / attack_qualified pattern.
SCALAR_BATCH: List[Tuple[str, str, float, List[str], List[Tuple[str, float]]]] = [
    # OSC Volume (verified path: kParamVolume, not kParamLevel).
    # "A Enable" (OSC1's enable) defaults to 1.0 -- no exercise context needed.
    ("OSC1.LEVEL", "Oscillator0.plainParams.kParamVolume", 0.0, ["rms_db"], []),
    ("OSC2.LEVEL", "Oscillator1.plainParams.kParamVolume", 0.0, ["rms_db"], []),
    ("OSC3.LEVEL", "Oscillator2.plainParams.kParamVolume", 0.0, ["rms_db"], []),

    # Filter Cutoff (verified path: kParamFreq, not kParamCutoff).
    # Filter 1/2 On default to 0.0 (OFF) -- exercise context required or the
    # mutation is inert (proven by filter_cutoff_pilot.py CAUSAL_VERIFIED).
    ("FILTER1.CUTOFF", "VoiceFilter0.plainParams.kParamFreq", 0.9,
     ["spectral_centroid_hz"], [("Filter 1 On", 1.0)]),
    ("FILTER2.CUTOFF", "VoiceFilter1.plainParams.kParamFreq", 0.9,
     ["spectral_centroid_hz"], [("Filter 2 On", 1.0)]),

    # Envelope Attack (verified path: kParamAttack, not kParamAttackTime).
    # No prerequisites (attack_qualified_complete_001_PASS_FULL.json).
    ("ENV1.ATTACK", "Env0.plainParams.kParamAttack", 0.8, ["attack_onset_rms_db"], []),
    ("ENV2.ATTACK", "Env1.plainParams.kParamAttack", 0.8, ["attack_onset_rms_db"], []),
]

MEASUREMENT_KERNELS = {
    "rms_db": (rms_db, 2.0),  # 2dB threshold for amplitude
    "tail_rms_db": (tail_rms_db, 1.0),  # 1dB for tail
    "spectral_centroid_hz": (spectral_centroid_hz, 200.0),  # 200Hz threshold
    "attack_onset_rms_db": (attack_onset_rms_db, 1.5),  # 1.5dB for attack
}


def _apply_host_context(synth, context: List[Tuple[str, float]]) -> None:
    """Apply host-level exercise context parameters (same mechanism as
    a3_behavior_harness._apply_exercise_context)."""
    if not context:
        return
    params = synth.get_parameters_description()
    by_name = {p["name"]: p["index"] for p in params}
    for name, value in context:
        if name not in by_name:
            raise KeyError(f"Exercise context: host parameter not found: {name!r}")
        synth.set_parameter(by_name[name], float(value))


def run_causal_experiment(
    semantic_id: str,
    cbor_path: str,
    treatment_value: float,
    measurement_names: List[str],
    exercise_context: List[Tuple[str, float]],
) -> Dict[str, Any]:
    """Run single causal qualification experiment.

    Baseline = fresh skeleton default state (+ exercise context).
    Treatment = fresh skeleton with ONE field mutated (+ same exercise context).

    Returns: {success, semantic_id, measurements, status}
    """
    try:
        skeleton = bridge.capture_v8_skeleton(VST3)
        meta, body = skeleton

        # === BASELINE (skeleton default, no mutation) ===
        baseline_meta, baseline_body = copy.deepcopy(meta), copy.deepcopy(body)
        baseline_value = pathmerge.read_path_value(baseline_body, cbor_path)

        baseline_audio = _render_state(baseline_meta, baseline_body, exercise_context)
        baseline_measurements = {}
        if baseline_audio is not None:
            for meas_name in measurement_names:
                kernel, _ = MEASUREMENT_KERNELS[meas_name]
                baseline_measurements[meas_name] = kernel(baseline_audio)

        # === TREATMENT (single field mutated) ===
        treatment_meta, treatment_body = copy.deepcopy(meta), copy.deepcopy(body)
        pathmerge.apply_path_value(treatment_body, cbor_path, treatment_value)

        treatment_audio = _render_state(treatment_meta, treatment_body, exercise_context)
        treatment_measurements = {}
        if treatment_audio is not None:
            for meas_name in measurement_names:
                kernel, _ = MEASUREMENT_KERNELS[meas_name]
                treatment_measurements[meas_name] = kernel(treatment_audio)

        # === MEASUREMENT COMPARISON ===
        measurements = []
        has_causal_effect = False
        for meas_name in measurement_names:
            baseline_val = baseline_measurements.get(meas_name)
            treatment_val = treatment_measurements.get(meas_name)
            kernel, threshold = MEASUREMENT_KERNELS[meas_name]

            if baseline_val is None or treatment_val is None:
                measurements.append({
                    "name": meas_name,
                    "baseline": baseline_val,
                    "treatment": treatment_val,
                    "delta": None,
                    "threshold": threshold,
                    "status": "NOT_MEASURABLE",
                })
            else:
                delta = abs(treatment_val - baseline_val)
                if delta >= threshold:
                    status = "CAUSAL_EFFECT_OBSERVED"
                    has_causal_effect = True
                else:
                    status = "NO_OBSERVED_EFFECT"

                measurements.append({
                    "name": meas_name,
                    "baseline": baseline_val,
                    "treatment": treatment_val,
                    "delta": delta,
                    "threshold": threshold,
                    "status": status,
                })

        causal_status = "CAUSAL_VERIFIED" if has_causal_effect else "CAUSAL_FAILED"

        return {
            "success": True,
            "semantic_id": semantic_id,
            "cbor_path": cbor_path,
            "baseline_value": baseline_value,
            "treatment_value": treatment_value,
            "exercise_context": exercise_context,
            "measurements": measurements,
            "causal_status": causal_status,
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "semantic_id": semantic_id,
            "error": str(e),
            "error_traceback": traceback.format_exc(),
            "causal_status": "CAUSAL_BLOCKED",
        }


def _render_state(meta, body, exercise_context: Optional[List[Tuple[str, float]]] = None, duration=2.0):
    """Render Serum state to audio. Returns numpy array or None on failure."""
    try:
        fd, tmp = tempfile.mkstemp(suffix=".bin")
        os.close(fd)

        bridge.write_state_file(tmp, meta, body)
        engine = daw.RenderEngine(SR, BLOCK)
        synth = engine.make_plugin_processor("serum", VST3)
        synth.load_state(tmp)
        os.remove(tmp)

        _apply_host_context(synth, exercise_context or [])

        synth.clear_midi()
        synth.add_midi_note(60, 100, 0.0, 1.5)
        engine.load_graph([(synth, [])])
        engine.render(duration)
        audio = np.asarray(engine.get_audio())
        return audio
    except Exception as e:
        import traceback
        import sys as _sys
        print(f"[RENDER ERROR] {str(e)}", file=_sys.stderr)
        traceback.print_exc(file=_sys.stderr)
        return None


def main():
    print("V1 Scalar Batch Causal Qualification (v2 — corrected paths + exercise context)\n")

    results = []
    verified = []
    failed = []
    blocked = []

    for semantic_id, cbor_path, treatment, measurements, exercise_context in SCALAR_BATCH:
        print(f"  {semantic_id}... ", end="", flush=True)
        result = run_causal_experiment(semantic_id, cbor_path, treatment, measurements, exercise_context)
        results.append(result)

        status = result.get("causal_status", "UNKNOWN")
        if status == "CAUSAL_VERIFIED":
            verified.append(semantic_id)
            print(f"[VERIFIED]")
        elif status == "CAUSAL_FAILED":
            failed.append(semantic_id)
            print(f"[FAILED]")
        else:
            blocked.append(semantic_id)
            print(f"[{status}] {result.get('error', '')}")

    print(f"\nResults:")
    print(f"  CAUSAL_VERIFIED: {len(verified)}")
    print(f"  CAUSAL_FAILED: {len(failed)}")
    print(f"  CAUSAL_BLOCKED: {len(blocked)}")

    # Write local evidence
    report_path = Path("serum2/qualification/CAUSAL_QUALIFICATION_V1_SCALAR_BATCH_REPORT.json")
    with open(report_path, "w") as f:
        json.dump({
            "batch": "scalar_amplitude_cutoff_envelope_v2",
            "methodology": "fresh skeleton + deepcopy + verified paths + exercise context",
            "total_experiments": len(SCALAR_BATCH),
            "verified_count": len(verified),
            "failed_count": len(failed),
            "blocked_count": len(blocked),
            "verified_ids": verified,
            "failed_ids": failed,
            "blocked_ids": blocked,
            "detailed_results": results,
        }, f, indent=2)

    print(f"\nReport: {report_path}")


if __name__ == "__main__":
    main()
