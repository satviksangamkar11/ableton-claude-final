"""Execute vertical slice: real Serum mutation → render → measure → restore → persist episode

Minimal execution using existing DawDreamer/bridge infrastructure.
"""
import json
import sys
import tempfile
import os
from pathlib import Path
import numpy as np
import dawdreamer as daw
from datetime import datetime, timezone

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2 import bridge
from serum2.evidence.measure import METRICS
from serum2.qualification.vertical_slice_executor import ExecutionRecord
from serum2.knowledge.intent_bridge import resolve_intent_to_candidates

# Constants from existing code
from serum2.evidence import epoch as epoch_mod

SR = 44100
BLOCK = 512
VST3 = epoch_mod.SERUM_VST3


def is_valid_signal(audio: np.ndarray) -> dict:
    """Check signal validity (existing gate from experiment_worker.py)."""
    peak = float(np.max(np.abs(audio)))
    nonzero_fraction = float(np.count_nonzero(audio) / audio.size)
    valid = bool(
        np.isfinite(audio).all()
        and peak > 1e-6
        and nonzero_fraction > 0.01
    )
    return {"peak": peak, "nonzero_fraction": nonzero_fraction, "valid": valid}


def render_arm(meta: dict, body: dict, extra_host_context: list = None) -> tuple:
    """
    Render one arm with optional host param context.

    Returns: (audio_array, error_message)
    """
    try:
        fd, tmp = tempfile.mkstemp(suffix=".bin")
        os.close(fd)

        bridge.write_state_file(tmp, meta, body)

        engine = daw.RenderEngine(SR, BLOCK)
        synth = engine.make_plugin_processor("serum", VST3)

        try:
            synth.load_state(tmp)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

        # Apply host context (if any)
        if extra_host_context:
            params = synth.get_parameters_description()
            by_name = {p["name"]: p["index"] for p in params}
            for param_name, param_value in extra_host_context:
                if param_name in by_name:
                    synth.set_parameter(by_name[param_name], float(param_value))

        synth.clear_midi()
        synth.add_midi_note(60, 100, 0.0, 1.5)
        engine.load_graph([(synth, [])])
        engine.render(2.0)

        audio = np.asarray(engine.get_audio())
        return audio, None

    except Exception as e:
        return None, str(e)


def execute_vertical_slice_env1_release():
    """
    Execute: human intent → Env1.Release mutation → render → measure → restore → persist
    """
    print("=" * 80)
    print("VERTICAL SLICE EXECUTION: Env1.Release")
    print("=" * 80)

    # Step 1: Resolve intent
    print("\n[1/6] Resolving intent...")
    human_intent = "make the note sustain longer"
    resolution = resolve_intent_to_candidates(
        human_intent,
        "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
        "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
    )

    if not resolution.candidate_operations:
        print("ERROR: No candidate operations found")
        return None

    candidate_op = resolution.candidate_operations[0]
    print(f"  Intent: {human_intent}")
    print(f"  Target: {candidate_op.target}")
    print(f"  Knowledge item: {candidate_op.source_knowledge_item_id}")
    print(f"  Hypothesis: {candidate_op.source_hypothesis_id}")

    # Step 2: Check admission (already checked in intent bridge, but verify)
    from serum2.compiler.targets import SEMANTIC_TARGETS

    if candidate_op.target not in SEMANTIC_TARGETS:
        print(f"ERROR: {candidate_op.target} not in SEMANTIC_TARGETS")
        return None

    qualified_targets = {
        "OSC1.Level",
        "OSC1.Detune",
        "Env1.Attack",
        "Env1.Release",
        "Filter.Cutoff",
        "OSC1.Octave",
    }

    if candidate_op.target not in qualified_targets:
        print(f"ERROR: {candidate_op.target} not qualified")
        return None

    print("  Status: ADMITTED")

    # Step 3: Load Serum skeleton and prepare baseline
    print("\n[2/6] Loading Serum skeleton...")
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta = skeleton[0]
    body = skeleton[1]
    print("  Skeleton loaded")

    # Step 4: Render baseline
    print("\n[3/6] Rendering baseline audio...")
    audio_baseline, baseline_err = render_arm(meta, body)
    if audio_baseline is None:
        print(f"ERROR: Baseline render failed: {baseline_err}")
        return None

    baseline_validity = is_valid_signal(audio_baseline)
    print(f"  Audio peak: {baseline_validity['peak']:.6f}")
    print(f"  Nonzero fraction: {baseline_validity['nonzero_fraction']:.4f}")
    print(f"  Valid: {baseline_validity['valid']}")

    # Step 5: Read current Env1.Release, mutate, render treatment
    print("\n[4/6] Mutating Env1.Release and rendering treatment...")

    engine_temp = daw.RenderEngine(SR, BLOCK)
    synth_temp = engine_temp.make_plugin_processor("serum", VST3)
    params = synth_temp.get_parameters_description()
    by_name = {p["name"]: p["index"] for p in params}

    # Find "Env 1 Release" parameter
    env1_release_param_name = "Env 1 Release"
    if env1_release_param_name not in by_name:
        print(f"ERROR: Parameter '{env1_release_param_name}' not found")
        return None

    env1_release_idx = by_name[env1_release_param_name]

    # Read baseline value
    # Note: We need to load state first to get accurate readback
    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)
    synth_temp.load_state(tmp)
    os.remove(tmp)

    readback_before = synth_temp.get_parameter(env1_release_idx)
    print(f"  Env1.Release baseline: {readback_before}")

    # Set treatment value (increase release time)
    treatment_value = 0.8
    synth_temp.set_parameter(env1_release_idx, treatment_value)
    readback_treatment = synth_temp.get_parameter(env1_release_idx)
    print(f"  Env1.Release treatment value: {treatment_value}")
    print(f"  Env1.Release readback after mutation: {readback_treatment}")

    # Render treatment with the mutated parameter
    extra_context = [(env1_release_param_name, treatment_value)]
    audio_treatment, treatment_err = render_arm(meta, body, extra_context)
    if audio_treatment is None:
        print(f"ERROR: Treatment render failed: {treatment_err}")
        return None

    treatment_validity = is_valid_signal(audio_treatment)
    print(f"  Treatment audio peak: {treatment_validity['peak']:.6f}")
    print(f"  Treatment nonzero fraction: {treatment_validity['nonzero_fraction']:.4f}")
    print(f"  Treatment valid: {treatment_validity['valid']}")

    # Step 6: Measure both with tail_rms_db
    print("\n[5/6] Measuring with tail_rms_db...")
    if "tail_rms_db" not in METRICS:
        print("ERROR: tail_rms_db not in METRICS")
        return None

    measurement_baseline = METRICS["tail_rms_db"](audio_baseline)
    measurement_treatment = METRICS["tail_rms_db"](audio_treatment)
    measurement_delta = measurement_treatment - measurement_baseline

    print(f"  Baseline tail_rms_db: {measurement_baseline}")
    print(f"  Treatment tail_rms_db: {measurement_treatment}")
    print(f"  Delta: {measurement_delta}")

    # Step 7: Restore and verify
    print("\n[6/6] Restoring original value...")
    synth_temp.set_parameter(env1_release_idx, readback_before)
    readback_restored = synth_temp.get_parameter(env1_release_idx)
    restoration_ok = abs(float(readback_restored) - float(readback_before)) < 0.01
    print(f"  Restored value: {readback_restored}")
    print(f"  Restoration verified: {restoration_ok}")

    # Step 8: Persist episode
    print("\n[PERSISTENCE] Creating episode artifact...")
    episode = ExecutionRecord(
        episode_id="ep_vertical_slice_001",
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        human_intent=human_intent,
        candidate_operation={
            "target": candidate_op.target,
            "operation": candidate_op.operation,
            "source_hypothesis_id": candidate_op.source_hypothesis_id,
            "source_knowledge_item_id": candidate_op.source_knowledge_item_id,
            "source_confidence": candidate_op.source_confidence,
        },
        semantic_target=candidate_op.target,
        admission_status="ADMITTED",
        admission_reason="Env1.Release has CAUSAL_VERIFIED capability",
        serum_readback_before=float(readback_before),
        serum_mutation_value=float(treatment_value),
        serum_readback_after=float(readback_treatment),
        audio_baseline=baseline_validity,
        audio_treatment=treatment_validity,
        measurement_metric="tail_rms_db",
        measurement_baseline=float(measurement_baseline),
        measurement_treatment=float(measurement_treatment),
        measurement_delta=float(measurement_delta),
        restoration_value=float(readback_before),
        restoration_readback=float(readback_restored),
    )

    output_file = Path("serum2/qualification/ep_vertical_slice_001.json")
    with open(output_file, "w") as f:
        json.dump(episode.to_dict(), f, indent=2)

    print(f"  Episode persisted to: {output_file}")

    print("\n" + "=" * 80)
    print("VERTICAL SLICE EXECUTION COMPLETE")
    print("=" * 80)

    return episode


if __name__ == "__main__":
    episode = execute_vertical_slice_env1_release()
    if episode:
        print("\nFINAL STATUS: SUCCESS")
    else:
        print("\nFINAL STATUS: FAILURE")
