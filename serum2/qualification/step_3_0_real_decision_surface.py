"""Step 3.0: Characterize Claude's decision surface.

Tests the REAL decision boundary with Claude Code reasoning.

N = 5 matched runs with frozen:
  - goal
  - context
  - admissible candidate set
  - model/runtime conditions
  - NO retrieved episodes

Records for every run:
  - admissible candidate set
  - selected candidate
  - Claude's rationale

Answers: Is the decision process stable enough for controlled
retrieval-influence experiment?

Status: IMPLEMENTATION PHASE - awaiting Claude decision in this session.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from serum2.producer.planner import PlannerDecisionEngine, GoalModel, Plan
from serum2.producer.goal_grounding import (
    GoalGroundingResult,
    CharacteristicGap,
    GapType,
)
from serum2.producer.claude_reasoning import prepare_claude_request, ClaudeDecision, ClaudeCandidate


# Minimal mock evidence system for testing
class MockCapabilityContract:
    def __init__(self, target: str, status: str):
        self.target = target
        self.status = status


class MockEvidenceSystem:
    def __init__(self):
        self.capabilities = {
            "Env1.Release": MockCapabilityContract("Env1.Release", "CAUSAL_VERIFIED"),
            "Env1.Attack": MockCapabilityContract("Env1.Attack", "CAUSAL_VERIFIED"),
            "Filter.Cutoff": MockCapabilityContract("Filter.Cutoff", "STRUCTURAL_ONLY"),
        }

    def get_capability(self, semantic_target: str):
        return self.capabilities.get(semantic_target)


class MockGoalModel:
    def __init__(self, intent: str):
        self.intent = intent


def create_step_3_0_goal_grounding() -> tuple[GoalGroundingResult, MockEvidenceSystem]:
    """Create a frozen goal/context for Step 3.0 testing.

    Replicates the frozen intent from earlier steps:
      intent: "make the note sustain longer"
      semantic_target: "Env1.Release"
      baseline: 0.5 (in-scope)

    Returns:
        (GoalGroundingResult, evidence_system)
    """
    goal = MockGoalModel(intent="make the note sustain longer")
    evidence = MockEvidenceSystem()

    # Create a MISSING gap for Env1.Release
    # (This is what the planner will address)
    gap = CharacteristicGap(
        characteristic_name="sustain_length",
        goal_value="longer",
        current_value="normal",
        gap_type=GapType.MISSING,
        detail="Goal requires longer sustain; current measurement is normal",
        possible_capabilities=["Env1.Release", "Env1.Attack"],
    )

    # Create a minimal GoalGroundingResult
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

    return grounding, evidence


def run_single_decision(
    run_id: int,
    planner: PlannerDecisionEngine,
    grounding: GoalGroundingResult,
    evidence_system: MockEvidenceSystem,
) -> dict:
    """Run one decision cycle.

    Args:
        run_id: run number (1-5)
        planner: PlannerDecisionEngine instance
        grounding: frozen goal grounding
        evidence_system: frozen evidence system

    Returns:
        Dictionary with run results:
          - admissible_candidates
          - selected_candidate
          - rationale
          - claude_request (for inspection)
    """
    print(f"\n[Step 3.0] Run {run_id} — Invoking planner...")

    # The planner will call claude_reasoning, which will raise NotImplementedError
    # We catch that and handle Claude's decision directly in THIS session

    # First, get the gap that needs decision
    gap = grounding.missing[0]  # Only one MISSING gap in our test

    # Collect admissible candidates (mimicking _plan_missing_gap logic)
    admissible_candidates = []
    for semantic_target in gap.possible_capabilities:
        contract = evidence_system.get_capability(semantic_target)
        if contract is None:
            continue

        contract_status = contract.status
        if contract_status not in ["CAUSAL_VERIFIED"]:
            continue

        admissible_candidates.append({
            "target": semantic_target,
            "status": contract_status,
            "reason": f"{contract_status} contract available",
            "source": "capability",
        })

    print(f"  Admissible candidates: {[c['target'] for c in admissible_candidates]}")

    # Prepare Claude request
    claude_request = prepare_claude_request(
        goal_intent=grounding.goal.intent,
        semantic_target=gap.characteristic_name,
        admissible_candidates=admissible_candidates,
        retrieved_episodes=[],  # No episodes in Step 3.0
        context={
            "characteristic": gap.characteristic_name,
            "goal_value": str(gap.goal_value),
            "current_value": str(gap.current_value),
        },
    )

    print(f"\n[Step 3.0] Run {run_id} — Claude decision required:\n")
    print(json.dumps(claude_request, indent=2))

    # STOP HERE: awaiting Claude's structured selection
    # This is where Claude Code in THIS session should provide:
    # {
    #   "candidates": [...],
    #   "selected": <index>,
    #   "rationale": "<explanation>"
    # }

    return {
        "run_id": run_id,
        "admissible_candidates": admissible_candidates,
        "claude_request": claude_request,
        "selected_candidate": None,  # To be filled by Claude
        "rationale": None,  # To be filled by Claude
    }


def main():
    print("[Step 3.0] Real Decision Surface Characterization")
    print("=" * 60)
    print("Testing Claude Code as the reasoning brain.")
    print(f"Start time: {datetime.now().isoformat()}\n")

    # Initialize
    evidence_system = MockEvidenceSystem()
    planner = PlannerDecisionEngine(evidence_system=evidence_system)
    grounding, _ = create_step_3_0_goal_grounding()

    # Run N=5 decision cycles
    results = []
    for run_id in range(1, 6):
        result = run_single_decision(
            run_id=run_id,
            planner=planner,
            grounding=grounding,
            evidence_system=evidence_system,
        )
        results.append(result)

    print("\n" + "=" * 60)
    print("[Step 3.0] AWAITING CLAUDE SELECTION")
    print("=" * 60)
    print(f"\nN = 5 runs prepared.")
    print(f"Frozen conditions: goal intent, semantic target, candidates, context.")
    print(f"Variable: Claude's decision (selected candidate + rationale).")
    print(f"\nFor each run above, provide:")
    print(f'  {{"candidates": [...], "selected": <int>, "rationale": "<text>"}}')
    print(f"\nWill record:")
    print(f"  - admissible candidate set")
    print(f"  - selected candidate index")
    print(f"  - Claude's rationale")
    print(f"\nAnalysis:")
    print(f"  - Are all 5 runs identical? (perfect stability)")
    print(f"  - Do they vary? (characterize variance)")
    print(f"  - Is the decision surface interpretable?")

    # Save prepared requests to file for reference
    output_file = Path(__file__).parent / "step_3_0_claude_requests.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nRequests saved to: {output_file}")


if __name__ == "__main__":
    main()
