"""Step 3.2: Retrieval Influence

Prove that retrieved experience actually changes the Claude decision.

Runs CONTROL (no episodes) vs TREATMENT (with positive control episode).
Everything else frozen.

Success condition: Observable change in structured decision artifact.
- Changed candidate set → PASS
- Changed selected candidate → PASS
- Only rationale changed → INSUFFICIENT (not PASS)
- Nothing changed → RETRIEVED_BUT_IGNORED
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


def run_decision(run_type: str, retrieved_episodes=None):
    """Execute one decision with specified retrieved episodes.

    Args:
        run_type: "CONTROL" or "TREATMENT"
        retrieved_episodes: list of episodes or None

    Returns:
        Planner artifact dict
    """
    print(f"\n[{run_type}]")
    print("-" * 70)

    evidence = MockEvidenceSystem()
    planner = PlannerDecisionEngine(evidence_system=evidence)
    grounding = create_frozen_grounding()

    # Run planner with specified episodes
    plan = planner.plan(
        grounding=grounding,
        retrieved_episodes=retrieved_episodes,
    )

    artifact = {
        "run_type": run_type,
        "goal": "make the note sustain longer",
        "retrieved_episode_ids": [ep.get("episode_id") for ep in (retrieved_episodes or [])],
        "admissible_candidates": [
            "Env1.Release",
            "Env1.Attack",
        ],
        "claude_candidates": [],  # Would need to capture from Claude
        "selected": None,
        "rationale": None,
    }

    if plan.actions:
        action = plan.actions[0]
        artifact["selected"] = action.selected_capability
        artifact["rationale"] = action.reasoning

        print(f"  Selected: {action.selected_capability}")
        print(f"  Rationale: {action.reasoning[:100]}...")
    else:
        print(f"  [ERROR] No actions in plan")

    return artifact


def compare_artifacts(control, treatment):
    """Compare control vs treatment artifacts for influence evidence.

    Returns:
        (classification, detail)
    """
    print("\n" + "=" * 70)
    print("[COMPARISON]")
    print("=" * 70)

    # Check candidate set changes
    control_candidates = set(control.get("admissible_candidates", []))
    treatment_candidates = set(treatment.get("admissible_candidates", []))

    candidates_changed = control_candidates != treatment_candidates

    if candidates_changed:
        print("\n1. CANDIDATE SET CHANGED")
        print(f"   CONTROL:   {control_candidates}")
        print(f"   TREATMENT: {treatment_candidates}")
        return "INFLUENCE_EVIDENCE", "candidate_set_changed"

    # Check selected candidate changes
    control_selected = control.get("selected")
    treatment_selected = treatment.get("selected")

    selection_changed = control_selected != treatment_selected

    if selection_changed:
        print("\n2. SELECTED CANDIDATE CHANGED")
        print(f"   CONTROL:   {control_selected}")
        print(f"   TREATMENT: {treatment_selected}")
        return "INFLUENCE_EVIDENCE", "selection_changed"

    # Check rationale changes
    control_rationale = control.get("rationale", "")
    treatment_rationale = treatment.get("rationale", "")

    rationale_changed = control_rationale != treatment_rationale

    if rationale_changed:
        print("\n3. RATIONALE CHANGED (but candidates/selection same)")
        print(f"   CONTROL:   {control_rationale[:80]}...")
        print(f"   TREATMENT: {treatment_rationale[:80]}...")
        return "INSUFFICIENT_EVIDENCE", "rationale_only_changed"

    # Nothing changed
    print("\n[NO CHANGES DETECTED]")
    print(f"  Selected: {control_selected} (both runs)")
    print(f"  Rationale identical")
    return "RETRIEVED_BUT_IGNORED", "episode_not_used"


def main():
    print("[Step 3.2] RETRIEVAL INFLUENCE TEST")
    print("=" * 70)
    print("Testing: does retrieved experience change Claude's decision?")
    print()
    print("Frozen conditions:")
    print("  - Goal: make the note sustain longer")
    print("  - Context: sustain_length")
    print("  - Admissible candidates: Env1.Release, Env1.Attack")
    print("  - Prompt: same")
    print("  - Claude runtime: same")
    print()

    # ========== CONTROL RUN ==========
    print("CONTROL RUN (no retrieved episodes)")
    control = run_decision("CONTROL", retrieved_episodes=None)

    # ========== TREATMENT RUN ==========
    print("\nTREATMENT RUN (with positive control episode)")
    positive_control = [
        {
            "episode_id": "retrieval_positive_control_release_001",
            "semantic_target": "Env1.Release",
            "human_intent": "make the note sustain longer",
            "decision": {"accepted": False},
            "learning_eligible": True,
        }
    ]
    treatment = run_decision("TREATMENT", retrieved_episodes=positive_control)

    # ========== COMPARISON ==========
    classification, detail = compare_artifacts(control, treatment)

    # ========== RESULT ==========
    print("\n" + "=" * 70)
    print("[STEP 3.2 RESULT]")
    print("=" * 70)

    print(f"\nClassification: {classification}")
    print(f"Detail: {detail}")

    if classification == "INFLUENCE_EVIDENCE":
        print("\nStep 3.2 Status: PASS")
        print("  Retrieval demonstrably affected Claude's decision.")
        print("  Evidence of influence: {}".format(detail))
        return 0

    elif classification == "INSUFFICIENT_EVIDENCE":
        print("\nStep 3.2 Status: FAIL")
        print("  Rationale changed but decision structure unchanged.")
        print("  Does not meet PASS criteria for influence.")
        return 1

    elif classification == "RETRIEVED_BUT_IGNORED":
        print("\nStep 3.2 Status: FAIL")
        print("  Episode retrieved but not used by Claude.")
        print("  No evidence of retrieval influence.")
        return 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
