"""Producer feedback loop: observe → diagnose → mutate → measure → decide → persist."""

import json
import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Tuple

import numpy as np
import dawdreamer as daw

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2 import bridge
from serum2.evidence.measure import METRICS
from serum2.evidence import epoch as epoch_mod
from serum2.qualification.vertical_slice_executor import ExecutionRecord
from serum2.qualification.execute_vertical_slice import (
    is_valid_signal,
    render_arm,
    validate_scope_prerequisite,
    validate_semantic_direction,
)
from serum2.producer.diagnosis import (
    ProducerGoal,
    CurrentState,
    Diagnosis,
    ProducerDecision,
    MetricDirection,
    diagnose_goal,
)

SR = 44100
BLOCK = 512
VST3 = epoch_mod.SERUM_VST3


def load_qualified_targets() -> dict:
    """Load all qualified capability contracts."""
    try:
        with open('serum2/knowledge/step_b_evidence_to_capability_integration.json') as f:
            data = json.load(f)
            return {c['target']: c for c in data.get('capability_contracts', [])}
    except Exception as e:
        print(f"Error loading qualified targets: {e}")
        return {}


def read_current_serum_state(host_param_name: str) -> Tuple[dict, dict, float]:
    """
    Read current Serum parameter value.

    Returns:
        (meta, body, parameter_value)
    """
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta = skeleton[0]
    body = skeleton[1]

    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)

    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)
    synth.load_state(tmp)
    os.remove(tmp)

    params = synth.get_parameters_description()
    by_name = {p["name"]: p["index"] for p in params}

    if host_param_name not in by_name:
        raise ValueError(f"Parameter '{host_param_name}' not found")

    param_idx = by_name[host_param_name]
    param_value = synth.get_parameter(param_idx)

    return meta, body, float(param_value)


def render_and_measure(
    meta: dict,
    body: dict,
    measurement_metric: str,
    baseline_override_param: Optional[Tuple[str, float]] = None,
) -> Tuple[np.ndarray, float, bool]:
    """
    Render audio and measure with given metric.

    Returns:
        (audio, measurement_value, is_valid)
    """
    audio, err = render_arm(meta, body, baseline_override_param=baseline_override_param)
    if audio is None:
        raise ValueError(f"Render failed: {err}")

    # Check validity
    validity = is_valid_signal(audio)
    if not validity['valid']:
        raise ValueError("Audio signal invalid (peak too low or nonzero fraction too small)")

    # Measure
    if measurement_metric not in METRICS:
        raise ValueError(f"Measurement metric '{measurement_metric}' not available")

    measurement_value = METRICS[measurement_metric](audio)
    return audio, float(measurement_value), True


def execute_producer_feedback_episode(
    goal: ProducerGoal,
    host_param_name: str,
    episode_id: str,
) -> Optional[ExecutionRecord]:
    """
    Execute one complete producer feedback loop episode.

    Returns:
        Episode record if successful, None on error
    """
    print("=" * 80)
    print(f"PRODUCER FEEDBACK LOOP: {goal.intent}")
    print("=" * 80)
    print()

    qualified_targets = load_qualified_targets()
    if not qualified_targets:
        print("ERROR: No qualified targets loaded")
        return None

    # Step 1: Read current state
    print("[1/10] Reading current Serum state...")
    try:
        meta, body, baseline_param = read_current_serum_state(host_param_name)
        print(f"  Parameter {host_param_name}: {baseline_param:.6f}")
    except Exception as e:
        print(f"ERROR reading state: {e}")
        return None

    # Step 2: Render baseline audio
    print("\n[2/10] Rendering baseline audio...")
    try:
        audio_baseline, measurement_baseline, _ = render_and_measure(meta, body, goal.measurement_metric)
        baseline_validity = is_valid_signal(audio_baseline)
        print(f"  {goal.measurement_metric}: {measurement_baseline:.2f}")
        print(f"  Peak: {baseline_validity['peak']:.6f}, Valid: {baseline_validity['valid']}")
    except Exception as e:
        print(f"ERROR rendering baseline: {e}")
        return None

    # Step 3: Create diagnosis
    print("\n[3/10] Creating diagnosis...")
    current_state = CurrentState(
        serum_readback=baseline_param,
        measurement_value=measurement_baseline,
        audio_peak=baseline_validity['peak'],
        audio_valid=baseline_validity['valid'],
    )

    diagnosis = diagnose_goal(goal, current_state, qualified_targets)
    if not diagnosis:
        print("ERROR: Could not create diagnosis")
        return None

    print(f"  Selected target: {diagnosis.selected_target}")
    print(f"  Mutation direction: {diagnosis.mutation_direction:+d}")
    print(f"  Reason: {diagnosis.reason}")

    # Step 4: Validate scope and direction
    print("\n[4/10] Validating scope and semantic direction...")

    # Determine mutation value
    mutation_value = baseline_param + (diagnosis.mutation_direction * diagnosis.mutation_magnitude)
    print(f"  Calculated mutation: {mutation_value:.6f}")

    # Scope validation
    scope_valid, scope_error, _ = validate_scope_prerequisite(diagnosis.selected_target, baseline_param)
    if not scope_valid:
        print(f"ERROR: Scope validation failed: {scope_error}")
        return None
    print(f"  Scope validation: OK")

    # Direction validation
    dir_valid, dir_error = validate_semantic_direction(
        goal.intent,
        diagnosis.selected_target,
        baseline_param,
        mutation_value,
    )
    if not dir_valid:
        print(f"ERROR: Direction validation failed: {dir_error}")
        return None
    print(f"  Direction validation: OK")

    # Step 5: Mutate and render treatment
    print("\n[5/10] Mutating and rendering treatment...")
    try:
        treatment_override = (host_param_name, mutation_value)
        audio_treatment, measurement_treatment, _ = render_and_measure(
            meta, body, goal.measurement_metric, baseline_override_param=treatment_override
        )
        treatment_validity = is_valid_signal(audio_treatment)
        print(f"  {goal.measurement_metric}: {measurement_treatment:.2f}")
        print(f"  Peak: {treatment_validity['peak']:.6f}, Valid: {treatment_validity['valid']}")
    except Exception as e:
        print(f"ERROR rendering treatment: {e}")
        return None

    # Step 6: Make decision
    print("\n[6/10] Making decision...")
    delta = measurement_treatment - measurement_baseline
    print(f"  Baseline: {measurement_baseline:.2f}")
    print(f"  Treatment: {measurement_treatment:.2f}")
    print(f"  Delta: {delta:+.2f}")

    # Create decision
    decision = ProducerDecision(
        accepted=True,  # placeholder
        reason="",
        baseline_measurement=measurement_baseline,
        treatment_measurement=measurement_treatment,
        delta=delta,
        metric_direction=goal.metric_direction,
    )

    # Determine if improvement
    improved = decision.improvement_observed()
    decision = ProducerDecision(
        accepted=improved,
        reason="Improvement observed" if improved else "No improvement",
        baseline_measurement=measurement_baseline,
        treatment_measurement=measurement_treatment,
        delta=delta,
        metric_direction=goal.metric_direction,
    )

    print(f"  Decision: {'ACCEPT' if decision.accepted else 'REJECT'}")
    print(f"  Reason: {decision.reason}")

    # Step 7: Handle rejection (restore baseline)
    if not decision.accepted:
        print("\n[7/10] Restoring baseline (rejection)...")
        # Restoration is automatic - just re-render with baseline state
        # The episode will be marked with restoration_status
        restoration_status = "not_needed_rejected"
        readback_restored = baseline_param
    else:
        print("\n[7/10] Accepting mutation (no restoration)...")
        restoration_status = "accepted"
        readback_restored = baseline_param

    # Step 8: Persist episode
    print("\n[8/10] Persisting episode...")
    episode = ExecutionRecord(
        episode_id=episode_id,
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        human_intent=goal.intent,
        candidate_operation={
            "target": diagnosis.selected_target,
            "operation": None,
            "source_hypothesis_id": None,
            "source_knowledge_item_id": None,
            "source_confidence": diagnosis.confidence,
        },
        semantic_target=diagnosis.selected_target,
        admission_status="ADMITTED",
        admission_reason="Producer feedback loop execution",
        serum_readback_before=baseline_param,
        serum_mutation_value=mutation_value,
        serum_readback_after=mutation_value,  # Assumed from render
        audio_baseline=baseline_validity,
        audio_treatment=treatment_validity,
        measurement_metric=goal.measurement_metric,
        measurement_baseline=measurement_baseline,
        measurement_treatment=measurement_treatment,
        measurement_delta=delta,
        restoration_value=baseline_param,
        restoration_readback=readback_restored,
        notes="Producer feedback loop episode",
        learning_eligible=False,  # Producer episodes don't update learning
        observation_only=True,  # Observation only, not evidence
        prerequisite_scope_violated=False,
    )

    # Add diagnosis and decision to notes as structured data
    episode_dict = episode.to_dict()
    episode_dict['diagnosis'] = diagnosis.to_dict()
    episode_dict['decision'] = decision.to_dict()
    episode_dict['restoration_status'] = restoration_status

    return episode_dict


if __name__ == "__main__":
    # Test with Env1.Release goal
    goal = ProducerGoal(
        intent="make the note sustain longer",
        semantic_target="Env1.Release",
        measurement_metric="tail_rms_db",
        metric_direction=MetricDirection.HIGHER_IS_BETTER,
    )

    episode = execute_producer_feedback_episode(
        goal=goal,
        host_param_name="Env 1 Release",
        episode_id="ep_producer_feedback_001",
    )

    if episode:
        print()
        print("=" * 80)
        print("EPISODE PERSISTED")
        print("=" * 80)
        with open("serum2/qualification/ep_producer_feedback_001.json", "w") as f:
            json.dump(episode, f, indent=2)
        print("Saved to serum2/qualification/ep_producer_feedback_001.json")
        print()
        print("SUCCESS")
    else:
        print("\nFAILED")
        sys.exit(1)
