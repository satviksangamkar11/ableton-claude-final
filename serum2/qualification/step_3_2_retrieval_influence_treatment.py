"""Step 3.2: Retrieval Influence - TREATMENT Run

Runs exactly one treatment with retrieved_episodes=[positive_control_release_001].
Same prompt, runtime, candidate grid, sampling config as Step 3.0.
Only change: retrieved_episodes parameter.

CONTROL baseline (from Step 3.0):
    selected = [1] (+0.05)

TREATMENT result:
    selected = ? (to compare)

PASS condition:
    treatment selected != CONTROL selected
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from serum2.producer.planner import PlannerDecisionEngine
from serum2.producer.goal_grounding import GoalGroundingResult, CharacteristicGap, GapType
from serum2.producer.episode_retrieval import retrieve_relevant_episodes


class MockCapabilityContract:
    def __init__(self, target: str, status: str):
        self.target = target
        self.status = status


class MockEvidenceSystem:
    def __init__(self):
        self.capabilities = {
            "Env1.Release": MockCapabilityContract("Env1.Release", "CAUSAL_VERIFIED"),
            "Env1.Attack": MockCapabilityContract("Env1.Attack", "CAUSAL_VERIFIED"),
        }

    def get_capability(self, semantic_target: str):
        return self.capabilities.get(semantic_target)


class MockGoalModel:
    def __init__(self, intent: str):
        self.intent = intent


def create_frozen_grounding():
    """Create frozen goal/context for 3.2 test."""
    goal = MockGoalModel(intent="make the note sustain longer")

    gap = CharacteristicGap(
        characteristic_name="sustain_length",
        goal_value="longer",
        current_value="normal",
        gap_type=GapType.MISSING,
        detail="Goal requires longer sustain",
        possible_capabilities=["Env1.Release", "Env1.Attack"],
    )

    grounding = GoalGroundingResult(
        goal=goal,
        role_state=None,
        all_gaps=[gap],
        satisfied=[],
        missing=[gap],
        contradictory=[],
        constrained=[],
        ungrounded=[],
    )

    return grounding


def load_positive_control_episode():
    """Load the positive control episode from disk."""
    episode_path = Path(__file__).parent / "retrieval_positive_control_release_001.json"

    if not episode_path.exists():
        print(f"[ERROR] Episode file not found: {episode_path}")
        return None

    try:
        with open(episode_path, 'r') as f:
            episode = json.load(f)
        return episode
    except Exception as e:
        print(f"[ERROR] Failed to load episode: {e}")
        return None


def run_treatment_decision(retrieved_episodes=None):
    """Execute one treatment decision with specified retrieved episodes.

    Args:
        retrieved_episodes: list of episode dicts or None

    Returns:
        Planner artifact dict with decision details
    """
    print(f"\n[TREATMENT RUN]")
    print("-" * 70)
    print(f"Retrieved episodes: {len(retrieved_episodes) if retrieved_episodes else 0}")
    if retrieved_episodes:
        for ep in retrieved_episodes:
            print(f"  - {ep.get('episode_id')}")

    evidence = MockEvidenceSystem()
    planner = PlannerDecisionEngine(evidence_system=evidence)
    grounding = create_frozen_grounding()

    # Run planner with retrieved episodes
    plan = planner.plan(
        grounding=grounding,
        retrieved_episodes=retrieved_episodes,
    )

    artifact = {
        "run_type": "TREATMENT",
        "goal": "make the note sustain longer",
        "retrieved_episode_ids": [ep.get("episode_id") for ep in (retrieved_episodes or [])],
        "admissible_candidates": ["Env1.Release", "Env1.Attack"],
        "selected_target": None,
        "selected_magnitude": None,
        "rationale": None,
    }

    if plan.actions:
        action = plan.actions[0]
        artifact["selected_target"] = action.selected_capability
        artifact["rationale"] = action.reasoning

        # Extract magnitude from reasoning if present
        # Format: "<rationale> [magnitude: +0.05]"
        import re
        magnitude_match = re.search(r'\[magnitude: ([+\-]?\d+\.?\d*)\]', action.reasoning)
        if magnitude_match:
            artifact["selected_magnitude"] = float(magnitude_match.group(1))

        print(f"  Selected target: {action.selected_capability}")
        print(f"  Selected magnitude: {artifact.get('selected_magnitude')}")
        print(f"  Rationale: {action.reasoning[:100]}...")
    else:
        print(f"  [ERROR] No actions in plan")

    return artifact


def main():
    print("[STEP 3.2] RETRIEVAL INFLUENCE — TREATMENT RUN")
    print("=" * 70)
    print("Testing: does retrieved experience change Claude's decision?")
    print()

    # ========== LOAD POSITIVE CONTROL EPISODE ==========
    print("[LOADING POSITIVE CONTROL EPISODE]")
    print("-" * 70)

    positive_control = load_positive_control_episode()

    if not positive_control:
        print("[FATAL] Could not load positive control episode")
        return 1

    print(f"\nLoaded: {positive_control.get('episode_id')}")
    print(f"  semantic_target: {positive_control.get('semantic_target')}")
    print(f"  human_intent: {positive_control.get('human_intent')}")
    print(f"  decision.accepted: {positive_control.get('decision', {}).get('accepted')}")
    print(f"  learning_eligible: {positive_control.get('learning_eligible')}")

    # ========== RUN TREATMENT ==========
    print("\n[EXECUTING TREATMENT WITH RETRIEVED EPISODE]")
    print("=" * 70)

    treatment = run_treatment_decision(retrieved_episodes=[positive_control])

    # ========== COMPARISON ==========
    print("\n" + "=" * 70)
    print("[COMPARISON: CONTROL vs TREATMENT]")
    print("=" * 70)

    control_magnitude = 0.05  # Step 3.0 selected candidate [1] = +0.05
    treatment_magnitude = treatment.get("selected_magnitude")

    print(f"\nCONTROL (Step 3.0):")
    print(f"  selected magnitude = +{control_magnitude}")
    print(f"  target = Env1.Release")

    print(f"\nTREATMENT (Step 3.2):")
    print(f"  selected magnitude = +{treatment_magnitude if treatment_magnitude else '?'}")
    print(f"  target = {treatment.get('selected_target')}")
    print(f"  rationale: {treatment.get('rationale', '')[:80]}...")

    # ========== DECISION ==========
    print("\n" + "=" * 70)
    print("[STEP 3.2 RESULT]")
    print("=" * 70)

    if treatment_magnitude is None:
        print(f"\nClassification: UNABLE_TO_EXTRACT_MAGNITUDE")
        print(f"  Could not extract magnitude from reasoning string")
        print(f"  Reasoning: {treatment.get('rationale', '')}")
        print(f"\nStep 3.2 Status: UNABLE_TO_CLASSIFY")
        return 1

    if abs(control_magnitude - treatment_magnitude) > 0.001:  # Allow small floating point diff
        print(f"\nClassification: INFLUENCE_EVIDENCE")
        print(f"  CONTROL magnitude: +{control_magnitude}")
        print(f"  TREATMENT magnitude: +{treatment_magnitude}")
        print(f"  Magnitudes differ -> retrieval influenced decision")
        print(f"\nStep 3.2 Status: PASS")
        print(f"  Retrieved experience demonstrably changed Claude's magnitude selection.")
        return 0
    else:
        print(f"\nClassification: RETRIEVED_BUT_IGNORED")
        print(f"  CONTROL magnitude: +{control_magnitude}")
        print(f"  TREATMENT magnitude: +{treatment_magnitude}")
        print(f"  Same magnitude selected despite retrieval")
        print(f"\nStep 3.2 Status: FAIL")
        print(f"  Episode was retrieved and passed to Claude, but did not affect magnitude selection.")

        return 1


if __name__ == "__main__":
    sys.exit(main())
