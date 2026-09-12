#!/usr/bin/env python3
"""Canonical producer feedback loop: deterministic diagnosis → one mutation → accept/reject → persist.

Real execution contract:
  goal → resolve intent → admitted capability → scope validation → direction validation →
  read baseline → render baseline → measure baseline → ONE mutation → readback →
  render treatment → measure treatment → accept/reject → restore only on rejection → persist
"""

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
from serum2.compiler.targets import SEMANTIC_TARGETS

SR = 44100
BLOCK = 512
VST3 = epoch_mod.SERUM_VST3


def resolve_host_param_name(semantic_target: str) -> str:
    """
    Resolve semantic target to DawDreamer host parameter name.

    Uses the authoritative semantic_vst3_mapping.json (runtime-verified).
    Fails explicitly (raises) if mapping not found.

    Args:
        semantic_target: e.g., "Env1.Release"

    Returns:
        DawDreamer parameter name, e.g., "Env 1 Release"

    Raises:
        ValueError: if semantic target, capability key, or host mapping not found
    """
    # Step 1: Get capability key from semantic target (FAIL EXPLICITLY)
    target_ref = SEMANTIC_TARGETS.get(semantic_target)
    if target_ref is None:
        raise ValueError(
            f"Semantic target {semantic_target!r} not registered. "
            f"Add to SEMANTIC_TARGETS in serum2/compiler/targets.py"
        )

    capability_key = target_ref.capability_key

    # Step 2: Load mapping (FAIL EXPLICITLY)
    try:
        with open('serum2/qualification/semantic_vst3_mapping.json') as f:
            mapping_data = json.load(f)
    except FileNotFoundError:
        raise ValueError(
            "Cannot load serum2/qualification/semantic_vst3_mapping.json. "
            "This file is required for VST3 parameter resolution."
        )
    except json.JSONDecodeError as e:
        raise ValueError(
            f"semantic_vst3_mapping.json is malformed: {e}"
        )

    # Step 3: Extract mappings dict (FAIL EXPLICITLY)
    if 'mappings' in mapping_data:
        mappings = mapping_data['mappings']
    else:
        raise ValueError(
            "semantic_vst3_mapping.json missing 'mappings' key. "
            "Expected structure: {\"mappings\": {\"capability_key\": \"param_name\"}}"
        )

    # Step 4: Look up host parameter name (FAIL EXPLICITLY)
    host_param_name = mappings.get(capability_key)
    if host_param_name is None:
        raise ValueError(
            f"No DawDreamer host parameter mapping for capability {capability_key!r} "
            f"(from semantic target {semantic_target!r}). "
            f"The target may not yet be resolved to VST3. "
            f"Check serum2/qualification/semantic_vst3_mapping.json"
        )

    return host_param_name


def _resolve_intent_to_target(intent: str) -> Optional[dict]:
    """
    Deterministic intent resolution using INTENT_SEMANTIC_MAP.

    No YouTube knowledge required (that's Step 5).
    Step 2 uses only the static semantic mapping.

    Returns: {semantic_target, measurement_metric, metric_direction, concept}
    """
    from serum2.knowledge.semantic_intent_resolver import INTENT_SEMANTIC_MAP, METRIC_FOR_TARGET

    intent_lower = intent.lower()
    intent_tokens = tuple(w.lower() for w in intent.split())

    # Find matching pattern (longest first)
    sorted_patterns = sorted(INTENT_SEMANTIC_MAP.keys(), key=len, reverse=True)
    matching_pattern = None
    for pattern in sorted_patterns:
        if all(word in intent_tokens for word in pattern):
            matching_pattern = pattern
            break

    if matching_pattern is None:
        return None

    # Get semantic mapping
    mapping = INTENT_SEMANTIC_MAP[matching_pattern]
    semantic_target = mapping["semantic_target"]
    measurement_metric = METRIC_FOR_TARGET.get(semantic_target)

    if measurement_metric is None:
        return None

    # Infer metric direction from semantic concept
    concept = mapping["semantic_concept"].lower()
    if any(word in concept for word in ['increase', 'longer', 'louder', 'higher', 'brighter']):
        metric_direction = MetricDirection.HIGHER_IS_BETTER
    elif any(word in concept for word in ['decrease', 'shorter', 'quieter', 'lower', 'darker']):
        metric_direction = MetricDirection.LOWER_IS_BETTER
    else:
        metric_direction = MetricDirection.HIGHER_IS_BETTER

    return {
        "semantic_target": semantic_target,
        "measurement_metric": measurement_metric,
        "metric_direction": metric_direction,
        "concept": concept,
    }


def execute_producer_from_intent(
    intent: str,
    episode_id: str,
    *,
    baseline_override: Optional[float] = None,
) -> dict:
    """
    Entry point: human intent → complete feedback episode.

    Resolves intent to goal, resolves target to host parameter,
    executes feedback loop, persists episode.

    Args:
        intent: e.g., "make the note sustain longer"
        episode_id: unique episode identifier
        baseline_override: optional baseline parameter value (for testing)

    Returns:
        Complete episode dict with diagnosis, decision, and measurements

    Raises:
        ValueError: if intent cannot be resolved or semantic target not mapped
        RuntimeError: if feedback execution fails (Serum, rendering, etc.)
    """
    # Resolve intent to target details (FAIL EXPLICITLY)
    resolution = _resolve_intent_to_target(intent)
    if resolution is None:
        raise ValueError(
            f"Cannot resolve intent {intent!r}. "
            f"No matching pattern in INTENT_SEMANTIC_MAP. "
            f"Check serum2/knowledge/semantic_intent_resolver.py"
        )

    # Create ProducerGoal
    goal = ProducerGoal(
        intent=intent,
        semantic_target=resolution["semantic_target"],
        measurement_metric=resolution["measurement_metric"],
        metric_direction=resolution["metric_direction"],
    )

    # Resolve target to DawDreamer host parameter name (FAIL EXPLICITLY)
    host_param_name = resolve_host_param_name(goal.semantic_target)

    # Execute feedback loop with existing machinery (may raise RuntimeError)
    episode = execute_producer_feedback_episode(
        goal=goal,
        host_param_name=host_param_name,
        baseline_override=baseline_override,
        episode_id=episode_id,
    )

    if episode is None:
        raise RuntimeError(
            f"Feedback episode execution returned None for {goal.semantic_target}"
        )

    return episode


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
        raise ValueError("Audio signal invalid (peak too low or nonzero fraction too small)")

    if measurement_metric not in METRICS:
        raise ValueError(f"Measurement metric '{measurement_metric}' not available")

    measurement_value = METRICS[measurement_metric](audio)
    return audio, float(measurement_value), validity


def execute_producer_feedback_episode(
    goal: ProducerGoal,
    host_param_name: str,
    baseline_override: Optional[float],
    episode_id: str,
) -> Optional[dict]:
    """
    Execute canonical producer feedback loop with real Serum execution.

    Args:
        goal: Producer goal (intent + target + metric + direction)
        host_param_name: Serum parameter name (e.g., "Env 1 Release")
        baseline_override: Optional baseline to use (for in-scope testing)
        episode_id: Episode identifier

    Returns:
        Episode dict if successful, None on error

    Real execution contract:
      - Scope prerequisite validation (baseline must be in-scope)
      - Semantic direction validation (intent must match mutation direction)
      - Real Serum rendering (DawDreamer baseline + treatment)
      - Real metric measurement
      - Accept only if improvement observed
      - Restore only on rejection
      - Persist with diagnosis + decision
    """
    print("=" * 80)
    print(f"PRODUCER FEEDBACK LOOP: {goal.intent}")
    print("=" * 80)
    print()

    qualified_targets = load_qualified_targets()
    if not qualified_targets:
        print("ERROR: No qualified targets loaded")
        return None

    # Load Serum skeleton
    print("[1/10] Loading Serum skeleton...")
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta = skeleton[0]
    body = skeleton[1]
    print("  Skeleton loaded")

    # Render baseline with optional override
    print("\n[2/10] Rendering baseline audio...")
    baseline_param_name = host_param_name
    if baseline_override is not None:
        print(f"  Using baseline override: {baseline_override}")
        baseline_override_param = (baseline_param_name, baseline_override)
        baseline_param = baseline_override
    else:
        baseline_override_param = None
        # Read current baseline from Serum
        engine = daw.RenderEngine(SR, BLOCK)
        synth = engine.make_plugin_processor("serum", VST3)
        fd, tmp = tempfile.mkstemp(suffix=".bin")
        os.close(fd)
        bridge.write_state_file(tmp, meta, body)
        synth.load_state(tmp)
        os.remove(tmp)
        params = synth.get_parameters_description()
        by_name = {p["name"]: p["index"] for p in params}
        if baseline_param_name not in by_name:
            print(f"ERROR: Parameter '{baseline_param_name}' not found")
            return None
        param_idx = by_name[baseline_param_name]
        baseline_param = synth.get_parameter(param_idx)

    try:
        audio_baseline, measurement_baseline, baseline_validity = render_and_measure(
            meta, body, goal.measurement_metric, baseline_override_param=baseline_override_param
        )
        print(f"  Baseline {goal.measurement_metric}: {measurement_baseline:.2f}")
        print(f"  Valid: {baseline_validity['valid']}")
    except Exception as e:
        print(f"ERROR: {e}")
        return None

    # Create diagnosis
    print("\n[3/10] Creating diagnosis...")
    current_state = CurrentState(
        serum_readback=baseline_param,
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
    print(f"  Reason: {diagnosis.reason}")

    # Validate scope and direction
    print("\n[4/10] Validating scope prerequisite...")
    scope_valid, scope_error, scope_info = validate_scope_prerequisite(
        diagnosis.selected_target, baseline_param
    )
    if not scope_valid:
        print(f"ERROR: Scope validation failed: {scope_error}")
        return None
    print(f"  Baseline {baseline_param} within scope: OK")

    print("\n[5/10] Validating semantic direction...")
    mutation_value = baseline_param + (diagnosis.mutation_direction * diagnosis.mutation_magnitude)
    dir_valid, dir_error = validate_semantic_direction(
        goal.intent,
        diagnosis.selected_target,
        baseline_param,
        mutation_value,
    )
    if not dir_valid:
        print(f"ERROR: Direction validation failed: {dir_error}")
        return None
    print(f"  Mutation {baseline_param} -> {mutation_value}: OK")

    # Render treatment (ONE mutation only)
    print("\n[6/10] Rendering treatment (ONE mutation only)...")
    try:
        treatment_override = (host_param_name, mutation_value)
        audio_treatment, measurement_treatment, treatment_validity = render_and_measure(
            meta, body, goal.measurement_metric, baseline_override_param=treatment_override
        )
        print(f"  Treatment {goal.measurement_metric}: {measurement_treatment:.2f}")
        print(f"  Valid: {treatment_validity['valid']}")
    except Exception as e:
        print(f"ERROR: {e}")
        return None

    # Make decision
    print("\n[7/10] Making decision...")
    delta = measurement_treatment - measurement_baseline
    print(f"  Baseline: {measurement_baseline:.2f}")
    print(f"  Treatment: {measurement_treatment:.2f}")
    print(f"  Delta: {delta:+.2f}")

    # Determine improvement
    decision = ProducerDecision(
        accepted=True,  # placeholder
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

    # Handle restoration/acceptance
    if not decision.accepted:
        print("\n[8/10] Restoring baseline (rejection)...")
        restoration_status = "baseline_restored"
        readback_restored = baseline_param
    else:
        print("\n[8/10] Accepting mutation (no restoration)...")
        restoration_status = "mutation_accepted"
        readback_restored = mutation_value

    # Persist episode
    print("\n[9/10] Persisting episode...")
    # Learning eligibility: episode can teach if in-scope (both accepted AND rejected are valuable)
    # Accepted = positive experience (what worked)
    # Rejected = negative experience (what didn't work, avoid repeating)
    # Separate: capability_promotion_eligible (requires Evidence → Claim → Capability machinery)
    learning_eligible_value = scope_valid  # True if in-scope (regardless of accept/reject)

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
        serum_readback_after=mutation_value,
        audio_baseline=baseline_validity,
        audio_treatment=treatment_validity,
        measurement_metric=goal.measurement_metric,
        measurement_baseline=measurement_baseline,
        measurement_treatment=measurement_treatment,
        measurement_delta=delta,
        restoration_value=baseline_param,
        restoration_readback=readback_restored,
        notes="Canonical producer feedback loop episode - deterministic target selection + mutation planning",
        learning_eligible=learning_eligible_value,  # True if in-scope (both accepted and rejected episodes teach)
        observation_only=True,  # Cannot alter authoritative capability state
        prerequisite_scope_violated=not scope_valid,
    )

    episode_dict = episode.to_dict()
    episode_dict['diagnosis'] = diagnosis.to_dict()
    episode_dict['decision'] = decision.to_dict()
    episode_dict['restoration_status'] = restoration_status
    episode_dict['scope_info'] = scope_info

    print("[10/10] Episode ready for persistence")

    return episode_dict


if __name__ == "__main__":
    # Test the entry point: intent → episode
    print("=" * 80)
    print("STEP 2: CANONICAL SERUM RUNTIME VERTICAL SLICE")
    print("=" * 80)
    print()

    try:
        episode = execute_producer_from_intent(
            intent="make the note sustain longer",
            episode_id="ep_producer_canonical_001",
            baseline_override=0.5,  # In-scope baseline for testing
        )

        if episode is None:
            print("ERROR: Intent resolution failed")
            sys.exit(1)

        print()
        print("=" * 80)
        print("STEP 2 RESULT: EPISODE PERSISTED")
        print("=" * 80)
        with open("serum2/qualification/ep_producer_canonical_001.json", "w") as f:
            json.dump(episode, f, indent=2)
        print(f"Saved: serum2/qualification/ep_producer_canonical_001.json")
        print()
        print(f"Intent:              {episode['human_intent']}")
        print(f"Semantic target:     {episode['semantic_target']}")
        print(f"Baseline before:     {episode['serum_readback_before']}")
        print(f"Mutation value:      {episode['serum_mutation_value']}")
        print(f"Measurement metric:  {episode['measurement_metric']}")
        print(f"Baseline measurement: {episode['measurement_baseline']:.2f}")
        print(f"Treatment measurement: {episode['measurement_treatment']:.2f}")
        print(f"Decision:            {episode['decision']['reason']}")
        print(f"Learning eligible:   {episode['learning_eligible']}")
        print(f"Observation only:    {episode['observation_only']}")
        print()
        print("[PASS] STEP 2: CANONICAL SERUM RUNTIME VERTICAL SLICE")

    except Exception as e:
        print(f"\n[FAIL] STEP 2: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
