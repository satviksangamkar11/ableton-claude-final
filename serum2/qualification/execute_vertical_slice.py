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


def execute_producer_episode(
    human_intent: str,
    semantic_target: str,
    host_param_name: str,
    mutation_value: float,
    measurement_metric: str,
    episode_id: str,
) -> tuple:
    """
    Generic producer execution: intent → target → mutate → render → measure → restore → persist

    Returns: (episode, error_message)
    """
    print("=" * 80)
    print(f"PRODUCER EXECUTION: {semantic_target}")
    print("=" * 80)

    # Step 1: Resolve intent
    print("\n[1/6] Resolving intent...")
    resolution = resolve_intent_to_candidates(
        human_intent,
        "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
        "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
    )

    if not resolution.candidate_operations:
        return None, f"No candidate operations for intent: {human_intent}"

    # Find matching candidate (may not be first)
    candidate_op = None
    for op in resolution.candidate_operations:
        if op.target == semantic_target:
            candidate_op = op
            break

    if not candidate_op:
        return None, f"Intent did not resolve to {semantic_target}"

    print(f"  Intent: {human_intent}")
    print(f"  Target: {candidate_op.target}")
    print(f"  Hypothesis: {candidate_op.source_hypothesis_id}")

    # Step 2: Check admission
    from serum2.compiler.targets import SEMANTIC_TARGETS

    if semantic_target not in SEMANTIC_TARGETS:
        return None, f"{semantic_target} not in SEMANTIC_TARGETS"

    qualified_targets = {
        "OSC1.Level",
        "OSC1.Detune",
        "Env1.Attack",
        "Env1.Release",
        "Filter.Cutoff",
        "OSC1.Octave",
    }

    if semantic_target not in qualified_targets:
        return None, f"{semantic_target} not qualified"

    print("  Status: ADMITTED")

    # Step 3: Load skeleton
    print("\n[2/6] Loading Serum skeleton...")
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta = skeleton[0]
    body = skeleton[1]
    print("  Skeleton loaded")

    # Step 4: Render baseline
    print("\n[3/6] Rendering baseline audio...")
    audio_baseline, baseline_err = render_arm(meta, body)
    if audio_baseline is None:
        return None, f"Baseline render failed: {baseline_err}"

    baseline_validity = is_valid_signal(audio_baseline)
    print(f"  Audio peak: {baseline_validity['peak']:.6f}")
    print(f"  Nonzero fraction: {baseline_validity['nonzero_fraction']:.4f}")
    print(f"  Valid: {baseline_validity['valid']}")

    if not baseline_validity["valid"]:
        return None, "Baseline audio invalid"

    # Step 5: Mutate and render treatment
    print("\n[4/6] Mutating and rendering treatment...")

    engine_temp = daw.RenderEngine(SR, BLOCK)
    synth_temp = engine_temp.make_plugin_processor("serum", VST3)
    params = synth_temp.get_parameters_description()
    by_name = {p["name"]: p["index"] for p in params}

    if host_param_name not in by_name:
        return None, f"Parameter '{host_param_name}' not found"

    param_idx = by_name[host_param_name]

    # Load and read baseline
    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)
    synth_temp.load_state(tmp)
    os.remove(tmp)

    readback_before = synth_temp.get_parameter(param_idx)
    print(f"  {host_param_name} baseline: {readback_before}")

    # Mutate
    synth_temp.set_parameter(param_idx, mutation_value)
    readback_after_mutation = synth_temp.get_parameter(param_idx)
    print(f"  {host_param_name} mutation target: {mutation_value}")
    print(f"  {host_param_name} readback after mutation: {readback_after_mutation}")

    # Render treatment
    extra_context = [(host_param_name, mutation_value)]
    audio_treatment, treatment_err = render_arm(meta, body, extra_context)
    if audio_treatment is None:
        return None, f"Treatment render failed: {treatment_err}"

    treatment_validity = is_valid_signal(audio_treatment)
    print(f"  Treatment audio peak: {treatment_validity['peak']:.6f}")
    print(f"  Treatment nonzero fraction: {treatment_validity['nonzero_fraction']:.4f}")
    print(f"  Treatment valid: {treatment_validity['valid']}")

    if not treatment_validity["valid"]:
        return None, "Treatment audio invalid"

    # Step 6: Measure
    print("\n[5/6] Measuring with metric...")
    if measurement_metric not in METRICS:
        return None, f"Measurement metric '{measurement_metric}' not in METRICS"

    measurement_baseline = METRICS[measurement_metric](audio_baseline)
    measurement_treatment = METRICS[measurement_metric](audio_treatment)
    measurement_delta = measurement_treatment - measurement_baseline

    print(f"  {measurement_metric} baseline: {measurement_baseline}")
    print(f"  {measurement_metric} treatment: {measurement_treatment}")
    print(f"  Delta: {measurement_delta}")

    # Step 7: Restore
    print("\n[6/6] Restoring...")
    synth_temp.set_parameter(param_idx, readback_before)
    readback_restored = synth_temp.get_parameter(param_idx)
    restoration_ok = abs(float(readback_restored) - float(readback_before)) < 0.01
    print(f"  Restored value: {readback_restored}")
    print(f"  Restoration verified: {restoration_ok}")

    if not restoration_ok:
        return None, "Restoration verification failed"

    # Step 8: Persist
    print("\n[PERSISTENCE] Creating episode artifact...")
    episode = ExecutionRecord(
        episode_id=episode_id,
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        human_intent=human_intent,
        candidate_operation={
            "target": candidate_op.target,
            "operation": candidate_op.operation,
            "source_hypothesis_id": candidate_op.source_hypothesis_id,
            "source_knowledge_item_id": candidate_op.source_knowledge_item_id,
            "source_confidence": candidate_op.source_confidence,
        },
        semantic_target=semantic_target,
        admission_status="ADMITTED",
        admission_reason=f"{semantic_target} has CAUSAL_VERIFIED capability",
        serum_readback_before=float(readback_before),
        serum_mutation_value=float(mutation_value),
        serum_readback_after=float(readback_after_mutation),
        audio_baseline=baseline_validity,
        audio_treatment=treatment_validity,
        measurement_metric=measurement_metric,
        measurement_baseline=float(measurement_baseline),
        measurement_treatment=float(measurement_treatment),
        measurement_delta=float(measurement_delta),
        restoration_value=float(readback_before),
        restoration_readback=float(readback_restored),
    )

    output_file = Path(f"serum2/qualification/{episode_id}.json")
    with open(output_file, "w") as f:
        json.dump(episode.to_dict(), f, indent=2)

    print(f"  Episode persisted to: {output_file}")
    print("\n" + "=" * 80)
    print(f"{semantic_target} EXECUTION COMPLETE")
    print("=" * 80)

    return episode, None


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


def execute_all_producer_episodes():
    """Execute producer episodes for all 5 remaining qualified targets."""
    episodes = []
    results = []

    # Target 1: OSC1.Level
    ep, err = execute_producer_episode(
        human_intent="make the sound quieter",
        semantic_target="OSC1.Level",
        host_param_name="A Level",
        mutation_value=0.25,
        measurement_metric="rms_db",
        episode_id="ep_producer_osc1_level_001",
    )
    episodes.append(ep)
    results.append((ep is not None, "OSC1.Level", err))

    # Target 2: OSC1.Detune
    ep, err = execute_producer_episode(
        human_intent="slightly detune the oscillator",
        semantic_target="OSC1.Detune",
        host_param_name="A Fine",
        mutation_value=0.75,
        measurement_metric="pitch_shift_semitones",
        episode_id="ep_producer_osc1_detune_001",
    )
    episodes.append(ep)
    results.append((ep is not None, "OSC1.Detune", err))

    # Target 3: OSC1.Octave
    ep, err = execute_producer_episode(
        human_intent="make the oscillator one octave higher",
        semantic_target="OSC1.Octave",
        host_param_name="A Octave",
        mutation_value=0.625,
        measurement_metric="pitch_shift_semitones",
        episode_id="ep_producer_osc1_octave_001",
    )
    episodes.append(ep)
    results.append((ep is not None, "OSC1.Octave", err))

    # Target 4: Env1.Attack
    ep, err = execute_producer_episode(
        human_intent="make the attack slower",
        semantic_target="Env1.Attack",
        host_param_name="Env 1 Attack",
        mutation_value=0.6,
        measurement_metric="rms_db",
        episode_id="ep_producer_env1_attack_001",
    )
    episodes.append(ep)
    results.append((ep is not None, "Env1.Attack", err))

    # Target 5: Filter1.Cutoff
    ep, err = execute_producer_episode(
        human_intent="make the sound brighter",
        semantic_target="Filter.Cutoff",
        host_param_name="Filter 1 Freq",
        mutation_value=0.9,
        measurement_metric="spectral_centroid_hz",
        episode_id="ep_producer_filter1_cutoff_001",
    )
    episodes.append(ep)
    results.append((ep is not None, "Filter.Cutoff", err))

    # Summary
    print("\n" + "=" * 80)
    print("PRODUCER EPISODE BATCH SUMMARY")
    print("=" * 80)
    for success, target, error in results:
        status = "[OK]" if success else f"[FAILED] {error}"
        print(f"  {target:20} {status}")

    success_count = sum(1 for s, _, _ in results if s)
    print(f"\nTotal: {success_count}/5 episodes completed successfully")

    return episodes, results


if __name__ == "__main__":
    # Execute all producer episodes
    episodes, results = execute_all_producer_episodes()
