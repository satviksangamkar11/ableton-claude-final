# STEP 4 — Harness Design (Before Execution)

**Purpose:** Show the minimal, parallel test structure for 4.1–4.3 before running anything.

---

## Target Specifications Matrix

| Property | 4.1 Release | 4.2 Attack | 4.3 Detune |
|----------|-------------|------------|-----------|
| **Semantic target** | Env1.Release | Env1.Attack | OSC1.Detune |
| **Intent pattern** | `('note', 'sustain', 'longer')` | `('attack', 'faster')` | `('oscillator', 'detune')` |
| **Intent confidence** | 0.95 | 0.95 | 0.85 |
| **Direction** | +1 (increase) | -1 (decrease) | +1 (increase) |
| **Measurement metric** | tail_rms_db | rms_db | pitch_shift_semitones |
| **Current value** | 0.50 | 0.50 | 0.50 |
| **Scope min** | 0.50 | 0.50 | 0.50 |
| **Scope max** | 0.80 | 0.60 | 0.75 |
| **Available movement** | 0.30 | 0.10 | 0.25 |
| **Candidate grid** | [+0.03, +0.05, +0.08] | [-0.02, -0.04, -0.06] | [+0.08, +0.13, +0.19] |
| **Grid rule** | Fixed increments (Step 3 established) | Proportional to movement (20%, 40%, 60%) | Proportional to movement (32%, 52%, 76%) |
| **Capability status** | CAUSAL_VERIFIED | CAUSAL_VERIFIED | CAUSAL_VERIFIED |

---

## Step 3 vs Step 4 Scope Comparison

What we **already know from Step 3.0–3.3**:

```text
Release:
  ✅ Decision surface characterized (N=5 stable at +0.05)
  ✅ Retrieval fidelity proven (episodes reach Claude)
  ✅ Retrieval influence proven (+0.05 → +0.08 on new evidence)
  ✅ Outcome measurement proven (+0.4205 dB delta on +0.08)
```

What we **need to establish for Attack and Detune**:

```text
Attack / Detune:
  ? Can Claude resolve the semantic intent to the target?
  ? Does the direction resolution work (decrease vs increase)?
  ? Does the target-specific grid construct correctly?
  ? Does Claude select from the grid?
  ? Does the existing executor accept the target?
  ? Does the measurement produce a valid signal?
  ? Does the episode persist with correct fields?
  ? Do the three targets show similar operation shapes?
```

---

## Minimal Test Flow for 4.2 (Attack) and 4.3 (Detune)

**Do NOT repeat the full Step 3 sequence (3.0 → 3.1 → 3.2 → 3.3).**

Instead, run a single **unified end-to-end test per target** that answers: "Does the canonical path work for this target?"

### 4.2.1 — Env1.Attack End-to-End Test

**Frozen inputs:**
```
intent = "make the attack faster"
semantic_target = Env1.Attack
direction = -1 (decrease)
metric = rms_db
baseline_value = 0.50
scope = [0.50, 0.60]
candidate_grid = [-0.02, -0.04, -0.06]
```

**Test sequence:**

1. **Semantic resolution** (inline)
   - Resolve intent "make the attack faster" → Env1.Attack, direction -1
   - Confirm it matches INTENT_SEMANTIC_MAP

2. **Decision surface** (single run, not N=5)
   - Invoke Claude with frozen grid + no retrieved episodes
   - Record: selected index, rationale
   - Goal: does Claude select from the grid?

3. **Execution path** (single control run)
   - Load Serum skeleton
   - Render baseline (Env1.Attack = 0.50)
   - Render treatment (Env1.Attack = selected_value)
   - Measure rms_db for both
   - Record: baseline, treatment, delta
   - Goal: does the executor accept the target? Does measurement produce valid signal?

4. **Episode persistence**
   - Construct episode dict with all fields from Step 3
   - Verify: episode_id, semantic_target, decision.accepted, learning_eligible, etc.
   - Goal: does the episode schema work for Attack?

**Output:** Single JSON with decision + execution + measurement results

**Pass condition:**
```
✅ PASS if:
  - semantic resolution succeeded
  - Claude selected a valid index
  - execution completed without error
  - measurement produced valid signal (peak > threshold, nonzero_fraction > threshold)
  - episode constructed with all required fields

❌ FAIL if:
  - any step raised an exception
  - signal invalid
  - episode missing fields
```

### 4.3.1 — OSC1.Detune End-to-End Test

**Identical structure to 4.2.1, with different inputs:**

```
intent = "detune the oscillator"
semantic_target = OSC1.Detune
direction = +1 (increase)
metric = pitch_shift_semitones
baseline_value = 0.50
scope = [0.50, 0.75]
candidate_grid = [+0.08, +0.13, +0.19]
```

**Test sequence:** Same as 4.2.1 (semantic resolution → decision → execution → episode)

**Note:** Measurement metric is pitch_shift_semitones, not rms_db. This tests whether the process survives a different measurement pathway.

---

## Why NOT Repeat Step 3's 3.1–3.3 for Attack/Detune (Yet)

**3.1 (retrieval fidelity)** was necessary in Step 3 because we were proving retrieval infrastructure worked at all. For Step 4, we assume that infrastructure is correct.

**3.2 (retrieval influence) and 3.3 (outcome improvement)** test whether *retrieved experience improves decisions*. This is a learning effectiveness test. We don't need to re-prove learning for every target — we need to prove the *process shape generalizes*.

**If 4.2.1 and 4.3.1 pass**, that's evidence the concrete path works. At that point, we can decide:
- Option A: Trust that retrieval/learning work identically on these targets (parsimonious)
- Option B: Run a single retrieval influence test (4.2.2) on one of them to validate the assumption
- Option C: Full 3.1–3.3 rerun on both (most thorough, most expensive)

**Recommendation:** After 4.2.1 and 4.3.1 pass, stop and report. Then decide with evidence whether 4.2.2/4.3.2 are needed.

---

## 4.4 — Compare Operation Shapes

Once 4.2.1 and 4.3.1 complete, extract and compare:

```text
Release (4.1):
  intent → target resolution
  target → grid construction
  grid → Claude selection
  selection → execution
  execution → measurement
  measurement → episode

Attack (4.2):
  [same flow]

Detune (4.3):
  [same flow]
```

Build a shape comparison table:

| Stage | Release | Attack | Detune | Difference? |
|-------|---------|--------|--------|-------------|
| Intent resolution | exists | ✓/✗ | ✓/✗ | minor / major / N/A |
| Target resolution | Env1.Release | Env1.Attack | OSC1.Detune | family change |
| Direction determination | +1 (increase) | -1 (decrease) | +1 (increase) | sign varies |
| Grid construction rule | fixed increments | proportional | proportional | varies by target |
| Claude selection | index [0,1,2] | index [0,1,2] | index [0,1,2] | same |
| Executor input shape | semantic_target + value | same | same | same |
| Measurement pipeline | tail_rms_db (tail-specific) | rms_db (general) | pitch_shift_semitones (pitch-specific) | metric varies |
| Episode schema | standard | standard | standard | same |

**Finding:** Process shape is identical. What varies is *target-specific details* (metric, grid rule), not the *process structure* (intent → grid → Claude → execute → measure → episode).

---

## 4.5 — Step 4 Conclusion

**Pass condition:**

```
✅ STEP 4 PASS if:
  - 4.2.1 and 4.3.1 both complete without exceptions
  - signals are valid for both
  - episodes construct correctly for both
  - operation shapes (intent → episode flow) are structurally identical
    across Release, Attack, Detune
  - the *only* differences are target-specific details
    (metric, grid rule, direction sign)

❌ STEP 4 FAIL if:
  - any target fails its end-to-end test
  - signals are invalid
  - execution paths differ in structure (not just parameter values)
  - process doesn't generalize to new targets
```

**Report:** Structured comparison of operation shapes, with conclusion:
> The canonical process (intent → semantic target → direction → authority-constrained grid → Claude selection → existing executor → target-appropriate measurement → episode) generalizes across three distinct targets without architectural modification. Target-specific details (metric, grid sampling rule, direction sign) are parameterized correctly. The process is **pattern-stable** across target families and measurement paradigms.

---

## Execution Timeline (Proposed)

```
4.1  (Skip end-to-end rerun; reference Release from Step 3)
4.2.1  Env1.Attack end-to-end test
4.3.1  OSC1.Detune end-to-end test
4.4   Compare shapes
4.5   Conclusion
```

**Estimated scope:** 2 harnesses (Attack, Detune), 1 comparison pass (4.4), no retrieval/outcome retesting unless evidence suggests otherwise.

---

## Harness Implementation Notes

Each harness will:

1. **Reuse existing machinery:**
   - `resolve_host_param_name()` (semantic target → VST3 parameter)
   - `render_and_measure()` (existing render + measurement pipeline)
   - `ExecutionRecord` (episode schema)

2. **Minimize duplication:**
   - Attack and Detune harnesses will be nearly identical (parameter differences only)
   - Release will reference Step 3's evidence directly

3. **Output format:** Single JSON per test with decision + execution + measurement

---

## Design Approval

Before proceeding:

- [ ] 4.1 (Release reference) approach approved
- [ ] 4.2.1 (Attack end-to-end) approach approved
- [ ] 4.3.1 (Detune end-to-end) approach approved
- [ ] 4.4 comparison method approved
- [ ] Do NOT run 4.2.2/4.3.2 (retrieval/outcome) unless explicit go-ahead given after 4.2.1/4.3.1 complete
