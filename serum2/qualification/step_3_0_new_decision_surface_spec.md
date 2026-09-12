# NEW Step 3.0 Decision Surface Specification

## Change Rationale

The original Step 3.0 tested:
```
target selection (deterministic) + hardcoded magnitude (+0.05)
```

The new Step 3.0 tests:
```
(target, direction, magnitude) candidate selection by Claude
```

This is a materially different decision surface. Step 3.0 must be re-characterized.

---

## 1. ADMISSIBLE TARGET SET (with evidence)

### Env1.Release: INCLUDED

**Evidence:**
- Semantic intent: "make the note sustain longer"
- Serum semantics: Env1.Release controls decay/sustain duration after MIDI note-off
- Capability contract: CAUSAL_VERIFIED, tested on [0.5, 0.8]
- Direction: increase Release → longer decay → longer audible sustain
- Match: Direct semantic match to intent

**Conclusion:** Env1.Release is the sole relevant target for this intent.

### Env1.Attack: EXCLUDED

**Evidence:**
- Semantic intent: "make the note sustain longer"
- Serum semantics: Env1.Attack controls fade-in time at note onset
- Semantic relation: Attack time does NOT affect sustain duration (the tail after note release)
- Direction: Modifying Attack does not address the intent

**Conclusion:** Env1.Attack is excluded as not semantically relevant.

### Final Target Set
```
ADMISSIBLE TARGETS:
  [Env1.Release]
```

**Single target, multiple magnitudes.**

---

## 2. MAGNITUDE UNITS AND INTERPRETATION

### Current Parameter State
```
Serum parameter: Env1.Release
Current readback: 0.5 (normalized, unitless, 0.0-1.0 range)
Scope: [0.5, 0.8] (normalized)
```

### Magnitude Definition
```
Magnitude = absolute change in normalized parameter value
Unit: parameter-units (0.0-1.0 scale)

Examples:
  magnitude +0.03 means: current (0.5) + 0.03 = 0.53
  magnitude +0.05 means: current (0.5) + 0.05 = 0.55
  magnitude +0.08 means: current (0.5) + 0.08 = 0.58
```

### Candidate Magnitudes (Experiment Sampling)

```
Authority constraint: admissible range [0.5, 0.8]
Current value: 0.5

Experiment sampling (within constraint):
  [0] magnitude = +0.03 → resultant value = 0.53 (in-scope ✓)
  [1] magnitude = +0.05 → resultant value = 0.55 (in-scope ✓)
  [2] magnitude = +0.08 → resultant value = 0.58 (in-scope ✓)
```

**No magnitude exceeds the [0.5, 0.8] scope. All valid.**

---

## 3. EXACT CLAUDE PROMPT AND EXPECTED OUTPUT

### Claude Prompt Structure

```
GOAL:
  Semantic intent: make the note sustain longer
  Target: Env1.Release (sustain/decay duration)

ADMISSIBLE CANDIDATES:
  [0] target=Env1.Release, direction=+1 (increase), magnitude=+0.03
  [1] target=Env1.Release, direction=+1 (increase), magnitude=+0.05
  [2] target=Env1.Release, direction=+1 (increase), magnitude=+0.08

RETRIEVED EPISODES:
  (none for Step 3.0 baseline)

TASK:
  Select exactly ONE candidate by index.
  You may NOT:
    - generate new candidates
    - modify target, direction, or magnitude
    - alter the admissible set
  Return the selected index and your rationale.

OUTPUT FORMAT:
  {
    "selected": <int: 0, 1, or 2>,
    "rationale": "<your explanation>"
  }
```

### Key Constraint

**Claude is a selector, not a generator.**
- Grid is fixed by Python (authority + experiment design)
- Claude's role: select one candidate and explain why
- No `candidates` field in response (grid already exists in Python)
- No free-text candidate generation

### Expected Output Format

```json
{
  "selected": 1,
  "rationale": "Magnitude +0.05 was previously tested in this context and showed significant improvement (+0.27 dB) with stable decision boundary. This middle option balances exploration and risk."
}
```

**NOT:**
```json
{
  "candidates": [...],
  "selected": 1,
  "rationale": "..."
}
```

---

## Architectural Boundary

```
AUTHORITY/POLICY (Python)
  ├─ target set: {Env1.Release}
  ├─ direction: +1 (increase, from intent semantics)
  └─ magnitude grid: [0.03, 0.05, 0.08]

        ↓

   CLAUDE REASONING
  (select one candidate)

        ↓

   SELECTION OUTPUT
  (index + rationale)

        ↓

   EXECUTOR
  (apply selected magnitude)
```

**Responsibility separation:**
- Authority owns: what targets exist, what ranges are valid, what experiments sample
- Claude owns: which sample best addresses the goal

---

## Step 3.0 Frozen Conditions

```
Goal: make the note sustain longer
Target set: {Env1.Release}
Magnitude grid: [+0.03, +0.05, +0.08]
Current value: 0.5
Scope: [0.5, 0.8]
Retrieved episodes: []
Prompt: (as specified above)
Claude runtime: same
Model: Claude Haiku 4.5
```

**All frozen. N=5 repeated runs with this exact surface.**

---

## Next Step

Validate these three specifications, then run NEW Step 3.0 on this decision surface.
