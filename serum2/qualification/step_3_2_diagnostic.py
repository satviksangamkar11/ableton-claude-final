"""Step 3.2 Diagnostic: Localize the retrieval-influence failure.

Captures three artifacts:
  A. Exact prompt sent to Claude
  B. Exact raw response from Claude
  C. Candidate construction site in code

These three distinguish all five hypotheses without rerunning.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Monkey-patch claude_reasoning to capture prompt and response
captured_artifacts = {
    "prompt": None,
    "raw_response": None,
}

original_build_prompt = None
original_invoke = None


def capture_prompt(goal_intent, semantic_target, admissible_candidates,
                   retrieved_episodes=None, context=None):
    """Captured version of _build_claude_prompt."""
    prompt = original_build_prompt(
        goal_intent, semantic_target, admissible_candidates,
        retrieved_episodes, context
    )
    captured_artifacts["prompt"] = prompt
    return prompt


def capture_invoke(goal_intent, semantic_target, admissible_candidates,
                   retrieved_episodes=None, context=None):
    """Captured version of invoke_claude_for_selection."""
    from serum2.producer import claude_reasoning
    import subprocess

    prompt = original_build_prompt(
        goal_intent, semantic_target, admissible_candidates,
        retrieved_episodes, context
    )
    captured_artifacts["prompt"] = prompt

    # Run Claude
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    captured_artifacts["raw_response"] = result.stdout

    # Parse and continue normally
    return original_invoke(goal_intent, semantic_target, admissible_candidates,
                          retrieved_episodes, context)


def setup_capture():
    """Install capture hooks."""
    from serum2.producer import claude_reasoning
    global original_build_prompt, original_invoke

    original_build_prompt = claude_reasoning._build_claude_prompt
    original_invoke = claude_reasoning.invoke_claude_for_selection

    claude_reasoning._build_claude_prompt = capture_prompt
    claude_reasoning.invoke_claude_for_selection = capture_invoke


def show_artifact_a():
    """Show the exact prompt sent to Claude."""
    print("\n" + "=" * 70)
    print("ARTIFACT A: EXACT PROMPT SENT TO CLAUDE")
    print("=" * 70)

    if not captured_artifacts["prompt"]:
        print("  [No prompt captured]")
        return

    prompt = captured_artifacts["prompt"]

    # Show first 1000 chars and mark where episode appears
    print(prompt[:2000])

    if "RETRIEVED EPISODES" in prompt:
        idx = prompt.index("RETRIEVED EPISODES")
        print(f"\n[Episode position: character {idx} / {len(prompt)}]")
        print(f"[Episode starts at ~{(idx/len(prompt))*100:.0f}% through prompt]")
    else:
        print("\n[No RETRIEVED EPISODES section found in prompt]")

    print(f"\n[Total prompt length: {len(prompt)} characters]")


def show_artifact_b():
    """Show the exact raw response from Claude."""
    print("\n" + "=" * 70)
    print("ARTIFACT B: EXACT RAW RESPONSE FROM CLAUDE")
    print("=" * 70)

    if not captured_artifacts["raw_response"]:
        print("  [No response captured]")
        return

    response = captured_artifacts["raw_response"]

    # Show first 1500 chars
    print(response[:1500])

    if len(response) > 1500:
        print(f"\n... [truncated, total length: {len(response)} characters]")

    # Parse and analyze structure
    try:
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(1))
            if "candidates" in parsed:
                print(f"\n[Parsed candidates count: {len(parsed['candidates'])}]")
                print(f"[Selected index: {parsed.get('selected', 'N/A')}]")
            else:
                print("\n[No 'candidates' field in parsed response]")
    except:
        pass


def show_artifact_c():
    """Show the candidate construction site in code."""
    print("\n" + "=" * 70)
    print("ARTIFACT C: CANDIDATE CONSTRUCTION SITE")
    print("=" * 70)

    planner_path = Path(__file__).parent.parent / "producer" / "planner.py"

    # Read planner.py and find _plan_missing_gap
    try:
        with open(planner_path, "r") as f:
            content = f.read()

        # Find the admissible_candidates construction
        start_idx = content.find("admissible_candidates = []")
        if start_idx != -1:
            # Show 2000 chars from that point
            snippet = content[start_idx:start_idx+1500]
            print(snippet)
            print("\n[Candidate construction: BUILD LOOP (enumeration in Python)]")
        else:
            print("  [Could not find candidate construction site]")
    except Exception as e:
        print(f"  [Error reading planner.py: {e}]")


def main():
    print("[Step 3.2 DIAGNOSTIC]")
    print("=" * 70)
    print("Capturing artifacts A, B, C from failed 3.2 run\n")

    # Install capture hooks
    setup_capture()

    # Run TREATMENT (with retrieved episodes) to capture artifacts
    from serum2.producer.planner import PlannerDecisionEngine
    from serum2.producer.goal_grounding import GoalGroundingResult, CharacteristicGap, GapType

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

    print("Running TREATMENT with retrieval (to capture artifacts)...\n")

    evidence = MockEvidenceSystem()
    planner = PlannerDecisionEngine(evidence_system=evidence)

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

    # Run with retrieved episode
    positive_control = [
        {
            "episode_id": "retrieval_positive_control_release_001",
            "semantic_target": "Env1.Release",
            "human_intent": "make the note sustain longer",
            "decision": {"accepted": False},
        }
    ]

    plan = planner.plan(grounding=grounding, retrieved_episodes=positive_control)

    if plan.actions:
        print(f"Planner returned: {plan.actions[0].selected_capability}")

    # Show artifacts
    show_artifact_a()
    show_artifact_b()
    show_artifact_c()

    print("\n" + "=" * 70)
    print("[DIAGNOSTIC INTERPRETATION]")
    print("=" * 70)
    print("""
Compare the three artifacts to the hypothesis table:

H1 (candidates enumerated in code):
  → Artifact A: Episode present
  → Artifact B: Selection-only output (no candidate array)
  → Artifact C: admissible_candidates built in for loop

H2 (prompt-structure bias):
  → Artifact A: Episode in low-attention position
  → Artifact B: Same candidate array literal
  → Artifact C: Candidates parsed from response

H3 (no actionable content):
  → Artifact A: Episode present
  → Artifact B: Rationale mentions it, candidates unchanged
  → Artifact C: Candidates parsed from response

H4 (rule-based selection):
  → Artifact A: Episode present
  → Artifact B: Same selection triggered
  → Artifact C: Selection is max(...) or [0]

H5 (irrelevant retrieval):
  → Artifact A: Episode present
  → Artifact B: "not applicable" in rationale
  → Artifact C: Any construction method
    """)


if __name__ == "__main__":
    main()
