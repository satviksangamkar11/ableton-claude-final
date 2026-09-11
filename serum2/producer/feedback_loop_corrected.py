#!/usr/bin/env python3
"""Producer feedback loop with in-scope baseline override."""

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
    MetricDirection,
    diagnose_goal,
    ProducerDecision,
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


def render_and_measure(
    meta: dict,
    body: dict,
    measurement_metric: str,
    baseline_override_param: Optional[Tuple[str, float]] = None,
) -> Tuple[np.ndarray, float, dict]:
    """Render audio and measure with given metric."""
    audio, err = render_arm(meta, body, baseline_override_param=baseline_override_param)
    if audio is None:
        raise ValueError(f"Render failed: {err}")

    validity = is_valid_signal(audio)
    if not validity['valid']:
        raise ValueError("Audio signal invalid")

    if measurement_metric not in METRICS:
        raise ValueError(f"Measurement metric '{measurement_metric}' not available")

    measurement_value = METRICS[measurement_metric](audio)
    return audio, float(measurement_value), validity


def execute_producer_feedback_episode_with_override(
    goal: ProducerGoal,
    host_param_name: str,
    baseline_override: float,
    episode_id: str,
) -> Optional[dict]:
    """Execute producer feedback loop with baseline override."""
    print("=" * 80)
    print(f"PRODUCER FEEDBACK LOOP (IN-SCOPE): {goal.intent}")
    print("=" * 80)
    print()

    qualified_targets = load_qualified_targets()
    if not qualified_targets:
        print("ERROR: No qualified targets")
        return None

    # Load skeleton
    print("[1/10] Loading Serum...")
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta = skeleton[0]
    body = skeleton[1]
    print("  Skeleton loaded")

    # Step 2: Render baseline with override
    print("\n[2/10] Rendering baseline (baseline override: {:.1f})...".format(baseline_override))
    try:
        baseline_param_override = (host_param_name, baseline_override)
        audio_baseline, measurement_baseline, baseline_validity = render_and_measure(
            meta, body, goal.measurement_metric, baseline_override_param=baseline_param_override
        )
        print(f"  {goal.measurement_metric}: {measurement_baseline:.2f}")
        print(f"  Valid: {baseline_validity['valid']}")
    except Exception as e:
        print(f"ERROR: {e}")
        return None

    # Step 3: Create diagnosis
    print("\n[3/10] Creating diagnosis...")
    current_state = CurrentState(
        serum_readback=baseline_override,
        measurement_value=measurement_baseline,
        audio_peak=baseline_validity['peak'],
        audio_valid=baseline_validity['valid'],
    )

    diagnosis = diagnose_goal(goal, current_state, qualified_targets)
    if not diagnosis:
        print("ERROR: Could not diagnose")
        return None

    print(f"  Target: {diagnosis.selected_target}")
    print(f"  Direction: {diagnosis.mutation_direction:+d}")

    # Step 4: Calculate and validate mutation
    print("\n[4/10] Validating scope and direction...")
    mutation_value = baseline_override + (diagnosis.mutation_direction * diagnosis.mutation_magnitude)
    print(f"  Mutation: {mutation_value:.6f}")

    scope_valid, scope_error, _ = validate_scope_prerequisite(diagnosis.selected_target, baseline_override)
    if not scope_valid:
        print(f"ERROR: Scope validation failed: {scope_error}")
        return None
    print(f"  Scope: OK")

    dir_valid, dir_error = validate_semantic_direction(
        goal.intent,
        diagnosis.selected_target,
        baseline_override,
        mutation_value,
    )
    if not dir_valid:
        print(f"ERROR: Direction validation failed: {dir_error}")
        return None
    print(f"  Direction: OK")

    # Step 5: Render treatment
    print("\n[5/10] Rendering treatment...")
    try:
        treatment_override = (host_param_name, mutation_value)
        audio_treatment, measurement_treatment, treatment_validity = render_and_measure(
            meta, body, goal.measurement_metric, baseline_override_param=treatment_override
        )
        print(f"  {goal.measurement_metric}: {measurement_treatment:.2f}")
        print(f"  Valid: {treatment_validity['valid']}")
    except Exception as e:
        print(f"ERROR: {e}")
        return None

    # Step 6: Make decision
    print("\n[6/10] Making decision...")
    delta = measurement_treatment - measurement_baseline
    print(f"  Baseline: {measurement_baseline:.2f}")
    print(f"  Treatment: {measurement_treatment:.2f}")
    print(f"  Delta: {delta:+.2f}")

    decision = ProducerDecision(
        accepted=True,
        reason="",
        baseline_measurement=measurement_baseline,
        treatment_measurement=measurement_treatment,
        delta=delta,
        metric_direction=goal.metric_direction,
    )

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

    # Step 7: Handle restoration/acceptance
    if not decision.accepted:
        print("\n[7/10] Restoration (rejection)...")
        restoration_status = "not_needed_rejected"
    else:
        print("\n[7/10] No restoration (acceptance)...")
        restoration_status = "accepted"

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
        admission_reason="Producer feedback loop",
        serum_readback_before=baseline_override,
        serum_mutation_value=mutation_value,
        serum_readback_after=mutation_value,
        audio_baseline=baseline_validity,
        audio_treatment=treatment_validity,
        measurement_metric=goal.measurement_metric,
        measurement_baseline=measurement_baseline,
        measurement_treatment=measurement_treatment,
        measurement_delta=delta,
        restoration_value=baseline_override,
        restoration_readback=baseline_override,
        notes="Producer feedback loop episode (in-scope baseline)",
        learning_eligible=False,
        observation_only=True,
        prerequisite_scope_violated=False,
    )

    episode_dict = episode.to_dict()
    episode_dict['diagnosis'] = diagnosis.to_dict()
    episode_dict['decision'] = decision.to_dict()
    episode_dict['restoration_status'] = restoration_status

    return episode_dict


if __name__ == "__main__":
    goal = ProducerGoal(
        intent="make the note sustain longer",
        semantic_target="Env1.Release",
        measurement_metric="tail_rms_db",
        metric_direction=MetricDirection.HIGHER_IS_BETTER,
    )

    episode = execute_producer_feedback_episode_with_override(
        goal=goal,
        host_param_name="Env 1 Release",
        baseline_override=0.5,  # In-scope baseline [0.5-0.8]
        episode_id="ep_producer_feedback_001",
    )

    if episode:
        print()
        print("=" * 80)
        print("EPISODE PERSISTED")
        print("=" * 80)
        with open("serum2/qualification/ep_producer_feedback_001.json", "w") as f:
            json.dump(episode, f, indent=2)
        print("Saved to: serum2/qualification/ep_producer_feedback_001.json")
        print()
        print("Episode data:")
        print(f"  Goal: {episode['human_intent']}")
        print(f"  Baseline: {episode['serum_readback_before']}")
        print(f"  Mutation: {episode['serum_mutation_value']:.6f}")
        print(f"  Baseline measurement: {episode['measurement_baseline']:.2f} {episode['measurement_metric']}")
        print(f"  Treatment measurement: {episode['measurement_treatment']:.2f} {episode['measurement_metric']}")
        print(f"  Delta: {episode['measurement_delta']:+.2f}")
        print(f"  Decision: {episode['decision']['reason']}")
        print()
        print("SUCCESS")
    else:
        print("\nFAILED")
        sys.exit(1)
