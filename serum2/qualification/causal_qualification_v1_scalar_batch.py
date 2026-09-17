#!/usr/bin/env python3
"""V1 causal qualification batch: scalar amplitude/cutoff mutations.

Uses existing measure.py kernels + seed experiment structure.
Isolates each capability mutation and measures audio effect.

Highest-yield batch:
  1. OSC1/OSC2/OSC3 Level (amplitude)
  2. Filter1/Filter2 Cutoff (spectral)
  3. Envelope Attack (temporal)
  4. Envelope Release (temporal)

Each experiment:
  fixture → render baseline
        → render with ONE capability mutated
        → measure audio difference
        → compare to attribution threshold
        → record CAUSAL_VERIFIED or CAUSAL_FAILED

Targets deterministic, isolated mutations with clear expected effects.
"""

import sys
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import dawdreamer as daw
from serum2 import bridge, codec, vst3_state, pathmerge
from serum2.evidence import epoch as epoch_mod
from serum2.evidence.measure import (
    rms_db, spectral_centroid_hz, tail_rms_db, attack_onset_rms_db
)
from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512
GOLDEN_PRESET = "archive/golden_presets/arp.SerumPreset"

# Scalar batch: (semantic_id, cbor_path, baseline_value, treatment_value, measurement_kernels)
SCALAR_BATCH = [
    # OSC Level (amplitude mutations should show RMS difference)
    ("OSC1.LEVEL", "Oscillator0.plainParams.kParamLevel", 0.5, 1.0, ["rms_db", "tail_rms_db"]),
    ("OSC2.LEVEL", "Oscillator1.plainParams.kParamLevel", 0.5, 1.0, ["rms_db", "tail_rms_db"]),
    ("OSC3.LEVEL", "Oscillator2.plainParams.kParamLevel", 0.5, 1.0, ["rms_db", "tail_rms_db"]),

    # Filter Cutoff (spectral mutations should show centroid change)
    ("FILTER1.CUTOFF", "VoiceFilter0.plainParams.kParamCutoff", 50.0, 120.0, ["spectral_centroid_hz"]),
    ("FILTER2.CUTOFF", "VoiceFilter1.plainParams.kParamCutoff", 50.0, 120.0, ["spectral_centroid_hz"]),

    # Envelope Attack (temporal mutation, should show attack_onset difference if note covers it)
    ("ENV1.ATTACK", "VoiceEnv0.plainParams.kParamAttackTime", 0.01, 0.5, ["attack_onset_rms_db"]),
    ("ENV2.ATTACK", "VoiceEnv1.plainParams.kParamAttackTime", 0.01, 0.5, ["attack_onset_rms_db"]),
]

MEASUREMENT_KERNELS = {
    "rms_db": (rms_db, 2.0),  # 2dB threshold for amplitude
    "tail_rms_db": (tail_rms_db, 1.0),  # 1dB for tail
    "spectral_centroid_hz": (spectral_centroid_hz, 200.0),  # 200Hz threshold
    "attack_onset_rms_db": (attack_onset_rms_db, 1.5),  # 1.5dB for attack
}


def run_causal_experiment(
    semantic_id: str,
    cbor_path: str,
    baseline_value: float,
    treatment_value: float,
    measurement_names: List[str],
) -> Dict[str, Any]:
    """Run single causal qualification experiment.

    Returns: {success, semantic_id, measurements, status}
    """
    try:
        # Load golden preset directly
        with open(GOLDEN_PRESET, 'rb') as f:
            meta, body = codec.decode(f.read())

        # === BASELINE ===
        baseline_meta, baseline_body = meta.copy(), body.copy()
        pathmerge.apply_path_value(baseline_body, cbor_path, baseline_value)

        baseline_audio = _render_state(baseline_meta, baseline_body)
        baseline_measurements = {}
        if baseline_audio is not None:
            for meas_name in measurement_names:
                kernel, _ = MEASUREMENT_KERNELS[meas_name]
                baseline_measurements[meas_name] = kernel(baseline_audio)

        # === TREATMENT ===
        treatment_meta, treatment_body = meta.copy(), body.copy()
        pathmerge.apply_path_value(treatment_body, cbor_path, treatment_value)

        treatment_audio = _render_state(treatment_meta, treatment_body)
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
            "measurements": measurements,
            "causal_status": causal_status,
        }

    except Exception as e:
        return {
            "success": False,
            "semantic_id": semantic_id,
            "error": str(e),
            "causal_status": "CAUSAL_BLOCKED",
        }


def _render_state(meta, body, duration=2.0):
    """Render Serum state to audio. Returns numpy array or None on failure."""
    try:
        fd, tmp = tempfile.mkstemp(suffix=".bin")
        os.close(fd)

        bridge.write_state_file(tmp, meta, body)
        engine = daw.RenderEngine(SR, BLOCK)
        synth = engine.make_plugin_processor("serum", VST3)
        synth.load_state(tmp)
        os.remove(tmp)

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
    print("V1 Scalar Batch Causal Qualification\n")

    results = []
    verified = []
    failed = []
    blocked = []

    for semantic_id, cbor_path, baseline, treatment, measurements in SCALAR_BATCH:
        print(f"  {semantic_id}... ", end="", flush=True)
        result = run_causal_experiment(semantic_id, cbor_path, baseline, treatment, measurements)
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
            print(f"[{status}]")

    print(f"\nResults:")
    print(f"  CAUSAL_VERIFIED: {len(verified)}")
    print(f"  CAUSAL_FAILED: {len(failed)}")
    print(f"  CAUSAL_BLOCKED: {len(blocked)}")

    # Write local evidence
    report_path = Path("serum2/qualification/CAUSAL_QUALIFICATION_V1_SCALAR_BATCH_REPORT.json")
    with open(report_path, "w") as f:
        json.dump({
            "batch": "scalar_amplitude_cutoff_envelope",
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
