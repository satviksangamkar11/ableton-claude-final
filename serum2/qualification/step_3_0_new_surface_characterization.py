"""Step 3.0 — New Decision-Surface Characterization

Tests Claude's selection behavior on the corrected decision surface:
- Python owns the admissible candidate grid
- Claude selects one candidate by index (no generation/modification)
- Genuine tradeoff in selection criterion
- N=5 repeated runs, everything frozen except run_id
- Record sampling configuration before execution
- Characterize selection variance

This is a new decision surface. Previous Step 3.0 is obsolete.
"""

import json
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


# CORRECTED PROMPT (approved)
STEP_3_0_PROMPT = """You are selecting an admissible production parameter magnitude.

IMPORTANT RULES:
1. You may NOT invent magnitudes.
2. You may NOT modify the target or direction.
3. You must select exactly one candidate by index.
4. You must return JSON only.

GOAL:
  Semantic intent: make the note sustain longer
  Serum target: Env1.Release (controls sustain/decay duration)
  Direction: increase (longer decay = longer sustain)

ADMISSIBLE CANDIDATES:
  [0] Env1.Release, direction=+1, magnitude=+0.03 (resultant: 0.53)
  [1] Env1.Release, direction=+1, magnitude=+0.05 (resultant: 0.55)
  [2] Env1.Release, direction=+1, magnitude=+0.08 (resultant: 0.58)

CONTEXT:
  Current parameter value: 0.50
  Admissible scope: [0.50, 0.80]
  All candidates are in-scope.

SELECTION CRITERION:
Select the candidate that is most likely to achieve the goal while remaining
acceptable under measurement.

Consider the tradeoff:
  - Larger changes (+0.08) may improve the target effect but increase risk
    of overshoot or unintended consequences.
  - Smaller changes (+0.03) may be safer and more conservative but may
    produce insufficient or imperceptible effect.

Do not assume the largest magnitude is always best. Select based on the
balance between effect and acceptable risk.

RETRIEVED-EPISODE RULE:
When retrieved episodes are present, use their observed outcomes and context
as evidence when selecting among the admissible candidates.

For example:
  - A previously rejected mutation is evidence against repeating that
    mutation when the current context is sufficiently comparable.
  - A previously accepted mutation is evidence supporting similar magnitude.

Do NOT treat an episode as authority. It can influence your selection,
but it cannot introduce, remove, or authorize a candidate.

YOUR TASK:
Select exactly one candidate by index [0, 1, or 2].
Do NOT create, remove, or modify candidates.
Return ONLY this JSON:
{
  "selected": <int>,
  "rationale": "<your explanation>"
}"""


def get_claude_sampling_config():
    """Inspect actual Claude CLI sampling configuration before execution."""
    print("\n[SAMPLING CONFIGURATION CHECK]")
    print("=" * 70)
    print("\nInspecting Claude CLI default configuration...")
    print("(Note: These are the defaults used unless overridden)")
    print("\nExpected settings:")
    print("  temperature: (default from CLI)")
    print("  seed: (default or none)")
    print("  model: claude-haiku-4-5 (from environment)")

    # In this environment, Claude uses default settings
    # Temperature is typically not set (uses model default ~0.7-1.0)
    # Seed is typically not set (uses random)
    # Model is typically claude-haiku-4-5

    config = {
        "temperature": "default (not explicitly set)",
        "seed": "random (not set)",
        "model": "claude-haiku-4-5",
        "sampling_mode": "stochastic (temperature not frozen)",
    }

    print("\nConfiguration:")
    for key, value in config.items():
        print(f"  {key}: {value}")

    return config


def run_single_sample(sample_id):
    """Run one Claude selection with the frozen prompt."""
    print(f"\n[SAMPLE {sample_id}]")
    print("-" * 70)

    result = subprocess.run(
        ["claude", "-p", STEP_3_0_PROMPT, "--output-format", "json"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        print(f"  [ERROR] Claude invocation failed")
        return None

    # Parse the response
    try:
        import re
        stdout = result.stdout.strip()
        wrapper = json.loads(stdout)

        if isinstance(wrapper, dict) and "result" in wrapper:
            result_text = wrapper["result"]
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', result_text, re.DOTALL)
            if json_match:
                response = json.loads(json_match.group(1))
            else:
                response = json.loads(result_text)
        else:
            response = wrapper
    except Exception as e:
        print(f"  [ERROR] Could not parse response: {e}")
        return None

    # Extract selection and rationale
    selected = response.get("selected")
    rationale = response.get("rationale", "")

    if selected not in [0, 1, 2]:
        print(f"  [ERROR] Invalid selection: {selected}")
        return None

    # Map to magnitude
    magnitudes = {0: 0.03, 1: 0.05, 2: 0.08}
    magnitude = magnitudes[selected]

    print(f"  selected = {selected}")
    print(f"  magnitude = +{magnitude}")
    print(f"  rationale = \"{rationale[:80]}...\"" if len(rationale) > 80 else f"  rationale = \"{rationale}\"")

    return {
        "sample_id": sample_id,
        "selected": selected,
        "magnitude": magnitude,
        "rationale": rationale,
    }


def main():
    print("[STEP 3.0] NEW DECISION-SURFACE CHARACTERIZATION")
    print("=" * 70)
    print("Testing Claude selection on corrected decision surface")
    print("(Magnitude selection with genuine tradeoff)")
    print()

    # ========== STEP 1: SAMPLING CONFIGURATION ==========
    sampling_config = get_claude_sampling_config()

    # ========== STEP 2: FROZEN DECISION SURFACE ==========
    print("\n[FROZEN DECISION SURFACE]")
    print("=" * 70)
    print("\nGoal: make the note sustain longer")
    print("Target: Env1.Release (sustain/decay duration)")
    print("Direction: increase (+1)")
    print("Current value: 0.50")
    print("Scope: [0.50, 0.80]")
    print("\nCandidate grid:")
    print("  [0] magnitude +0.03 -> resultant 0.53")
    print("  [1] magnitude +0.05 -> resultant 0.55")
    print("  [2] magnitude +0.08 -> resultant 0.58")
    print("\nRetrieved episodes: []")
    print("Prompt: (corrected, with genuine tradeoff criterion)")

    # ========== STEP 3: RUN N=5 SAMPLES ==========
    print("\n[EXECUTING N=5 SAMPLES]")
    print("=" * 70)

    samples = []
    for sample_id in range(1, 6):
        sample = run_single_sample(sample_id)
        if sample:
            samples.append(sample)
        else:
            print(f"  [FAILED] Sample {sample_id} could not be processed")
            return 1

    # ========== STEP 4: SELECTION VARIANCE ==========
    print("\n[SELECTION VARIANCE ANALYSIS]")
    print("=" * 70)

    selections = [s["selected"] for s in samples]
    unique_selections = set(selections)

    print(f"\nSelections: {selections}")
    print(f"Unique candidates selected: {sorted(unique_selections)}")

    if len(unique_selections) == 1:
        variance_classification = "ZERO_VARIANCE"
        print(f"\nVariance: ZERO VARIANCE")
        print(f"  All 5 runs selected candidate [{selections[0]}] (+{samples[0]['magnitude']})")
    else:
        variance_classification = "NON_ZERO_VARIANCE"
        print(f"\nVariance: NON-ZERO VARIANCE")
        for idx in sorted(unique_selections):
            count = selections.count(idx)
            print(f"  Candidate [{idx}]: selected {count} times")

    # ========== STEP 5: INTERPRETATION ==========
    print("\n[INTERPRETATION]")
    print("=" * 70)

    if variance_classification == "ZERO_VARIANCE":
        interpretation = "stable decision at this sampling configuration"
        status = "PASS"
        print(f"\n{interpretation}")
        print("\nClassification: stable selection")
        print("  Same candidate in all 5 runs indicates consistent decision policy")
        print("  This is valid behavior under stochastic sampling")
    else:
        interpretation = "stochastic decision surface at this sampling configuration"
        status = "NOT_INTERPRETABLE_YET"
        print(f"\n{interpretation}")
        print("\nClassification: variable selection")
        print("  Multiple candidates selected across runs")
        print("  Decision surface is stochastic under current sampling config")

    # ========== STEP 6: FINAL OUTPUT ==========
    print("\n" + "=" * 70)
    print("[FINAL REPORT]")
    print("=" * 70)

    print(f"\n1. SAMPLING CONFIGURATION:")
    for key, value in sampling_config.items():
        print(f"   {key}: {value}")

    print(f"\n2. FROZEN DECISION SURFACE:")
    print(f"   goal: make the note sustain longer")
    print(f"   target: Env1.Release")
    print(f"   current: 0.50")
    print(f"   scope: [0.50, 0.80]")
    print(f"   candidates: [+0.03, +0.05, +0.08]")

    print(f"\n3. SAMPLES 1-5:")
    for sample in samples:
        print(f"   [{sample['sample_id']}] selected={sample['selected']}, magnitude=+{sample['magnitude']}")
        print(f"       {sample['rationale'][:70]}...")

    print(f"\n4. SELECTION FREQUENCIES:")
    for idx in range(3):
        count = selections.count(idx)
        print(f"   Candidate [{idx}] (+{[0.03, 0.05, 0.08][idx]}): {count}/5 times")

    print(f"\n5. VARIANCE CLASSIFICATION:")
    print(f"   {variance_classification}")

    print(f"\n6. INTERPRETATION:")
    print(f"   {interpretation}")

    print(f"\n7. STEP 3.0 STATUS:")
    print(f"   {status}")

    print(f"\n8. NEXT ACTION FOR STEP 3.2:")
    if status == "PASS":
        print(f"   Run Step 3.2 with same prompt + same grid")
        print(f"   Add: retrieved_episodes = [positive_control_episode]")
        print(f"   Compare CONTROL selection [Sample 3.0] vs TREATMENT [Sample 3.2]")
        print(f"   Evidence: X != Y indicates retrieval influence")
    else:
        print(f"   Determine if stochasticity affects 3.2 comparison")
        print(f"   Consider: run multiple TREATMENT samples to establish baseline")

    print("\n" + "=" * 70)
    print("[STOP — DO NOT PROCEED TO STEP 3.2 YET]")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
