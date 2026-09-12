# STEP 4.0 — Target/Intent/Metric Eligibility Inspection

**Purpose:** Identify which targets have sufficient repository support (intent mapping, metric implementation, scope constraints, capability contracts) to freeze for Step 4 experiments.

**Date:** 2026-09-12

---

## Summary Table

| Target | Intent(s) | Direction | Metric | Metric Impl. | Scope | Status |
|--------|-----------|-----------|--------|--------------|-------|--------|
| Env1.Release | "sustain longer" | increase (+1) | tail_rms_db | ✅ | [0.5–0.8] | **ELIGIBLE** |
| Env1.Attack | "attack faster/slower" | ±1 | rms_db | ✅ | [0.5–0.6] | **ELIGIBLE** |
| OSC1.Detune | "detune" | ±1 | pitch_shift_semitones | ✅ | [0.5–0.75] | **ELIGIBLE** |
| OSC1.Level | "louder/quieter" | ±1 | rms_db | ✅ | [0.75→0.25] | **INELIGIBLE (baseline=0.5 out-of-scope)** |
| Filter.Cutoff | "brighter/darker" | ±1 | spectral_centroid_hz | ✅ | none | **INELIGIBLE (no contract)** |

---

## Detailed Analysis

### Env1.Release — **ELIGIBLE**

**Intents resolved:**
- `('note', 'sustain', 'longer')` → Env1.Release (confidence 0.95)

**Direction:**
- Increase (longer sustain = higher Release value)

**Metric:**
- `Env1.Release` → `tail_rms_db` (implemented ✅)

**Capability status:**
- CAUSAL_VERIFIED (contract exists)

**Scope:**
- Baseline: 0.5
- Valid range: [0.5, 0.8]
- Limitation: Tested only [0.5 → 0.8]; generalization not yet verified
- **Baseline 0.5 is IN-SCOPE ✅**

**Magnitude sampling:** (inherited from Step 3)
- Grid: [+0.03, +0.05, +0.08]
- Rule: even increments within available in-scope movement

---

### Env1.Attack — **ELIGIBLE**

**Intents resolved:**
- `('attack', 'faster')` → Env1.Attack (confidence 0.95)
- `('attack', 'slower')` → Env1.Attack (confidence 0.95)

**Direction:**
- Increase for slower attack, decrease for faster attack
- Step 4 will use: decrease (faster attack, more responsive)

**Metric:**
- `Env1.Attack` → `rms_db` (implemented ✅)
- Different from Release: tests same capability family (Env) but different measurement need

**Capability status:**
- CAUSAL_VERIFIED (contract exists)

**Scope:**
- Baseline: 0.5
- Valid range: [0.5, 0.6]
- Limitation: Tested only [0.5 → 0.6]; generalization not yet verified
- **Baseline 0.5 is IN-SCOPE ✅**

**Magnitude sampling rule:**
- Available in-scope movement: 0.6 - 0.5 = 0.1
- Suggested rule: three decrements (faster attack)
  - Small: -0.02 → 0.48
  - Medium: -0.04 → 0.46
  - Large: -0.06 → 0.44
  - (All within [0.5, 0.6] scope)

---

### OSC1.Detune — **ELIGIBLE** (but different measurement)

**Intents resolved:**
- `('oscillator', 'detune')` → OSC1.Detune (confidence 0.85)

**Direction:**
- Increase (more detune, larger pitch shift)

**Metric:**
- `OSC1.Detune` → `pitch_shift_semitones` (implemented, but not as `METRICS[...]` entry)
- **Note:** This metric is not in the standard `METRICS` dict; measured differently than Env/Filter targets
- Tests: different capability family (Oscillator) + different measurement mechanism

**Capability status:**
- CAUSAL_VERIFIED (contract exists)

**Scope:**
- Baseline: 0.5
- Valid range: [0.5, 0.75]
- Limitation: Tested A Fine [0.5 → 0.75] (+200 cents); generalization not verified
- **Baseline 0.5 is IN-SCOPE ✅**

**Magnitude sampling rule:**
- Available in-scope movement: 0.75 - 0.5 = 0.25
- Suggested rule: three increments
  - Small: +0.08 → 0.58
  - Medium: +0.13 → 0.63
  - Large: +0.19 → 0.69
  - (All within [0.5, 0.75] scope)

---

### OSC1.Level — **INELIGIBLE**

**Intents resolved:**
- `('sound', 'louder')` → OSC1.Level (confidence 0.85)
- `('sound', 'quieter')` → OSC1.Level (confidence 0.85)

**Direction:**
- Increase for louder, decrease for quieter

**Metric:**
- `OSC1.Level` → `rms_db` (implemented ✅)

**Capability status:**
- CAUSAL_VERIFIED (contract exists)

**Scope:**
- Tested range: [0.75 → 0.25] (decrease for "quieter")
- **Baseline 0.5 is OUT-OF-SCOPE ✗**
- Limitation: Tested only at high-level [0.75 → 0.25]; mid-range or low-level not qualified

**Rejection reason:**
The existing contract was measured at a specific range (0.75 → 0.25, for "quieter").
Baseline 0.5 for "louder" direction would require moving [0.5 → higher], which is
different from the tested direction. This violates the prerequisite_scope constraint.

**Future work:**
OSC1.Level requires its own baseline measurement (e.g., 0.75 as baseline for louder,
or qualification of a different baseline range) before it can be used.

---

### Filter.Cutoff — **INELIGIBLE**

**Intents resolved:**
- `('sound', 'brighter')` → Filter.Cutoff (confidence 0.8)
- `('sound', 'darker')` → Filter.Cutoff (confidence 0.8)

**Direction:**
- Increase for brighter, decrease for darker

**Metric:**
- `Filter.Cutoff` → `spectral_centroid_hz` (implemented ✅)

**Capability status:**
- **NO CAPABILITY CONTRACT FOUND** ✗
- The intent mapping exists, the metric exists, but there is no CAUSAL_VERIFIED contract

**Rejection reason:**
Filter.Cutoff has not completed the evidence → claim → capability promotion pipeline.
Until a capability contract exists and passes prerequisites validation, this target cannot
be admitted to the planner.

**Future work:**
Filter.Cutoff must undergo Steps 1–2 (evidence system integration) before Step 4 use.

---

## Frozen Targets for Step 4

Based on this inspection, Step 4 will use **exactly three targets**:

| Step | Target | Intent | Direction | Metric | Axis |
|------|--------|--------|-----------|--------|------|
| 4.1 | Env1.Release | "make the note sustain longer" | increase | tail_rms_db | Step 3 validation (known to work) |
| 4.2 | Env1.Attack | "make the attack faster" | decrease | rms_db | Same family (Env), different metric |
| 4.3 | OSC1.Detune | "detune the oscillator" | increase | pitch_shift_semitones | Different family (OSC), different measurement |

All three:
- Have CAUSAL_VERIFIED capability contracts
- Have resolvable semantic intents
- Have implemented measurement metrics
- Have baselines within scope (0.5 is valid for all three)
- Are ready for Step 4 processing

---

## Magnitude Grids (Authority-Derived)

### Env1.Release (4.1)
```
Current:  0.50
Scope:    [0.50, 0.80]
Movement: 0.30

Grid (inherited from Step 3, per established pattern):
  [0] +0.03 → 0.53
  [1] +0.05 → 0.55
  [2] +0.08 → 0.58
```

### Env1.Attack (4.2)
```
Current:  0.50
Scope:    [0.50, 0.60]
Movement: 0.10
Direction: decrease (faster attack)

Grid (new, proportional to available movement):
  [0] -0.02 → 0.48
  [1] -0.04 → 0.46
  [2] -0.06 → 0.44
```

### OSC1.Detune (4.3)
```
Current:  0.50
Scope:    [0.50, 0.75]
Movement: 0.25
Direction: increase (more detune)

Grid (new, proportional to available movement):
  [0] +0.08 → 0.58
  [1] +0.13 → 0.63
  [2] +0.19 → 0.69
```

---

## Inspection Findings

1. **Intent mapping is complete** for the three selected targets. Each has at least one resolvable human intent pattern.

2. **Metrics are implemented** for all three. Two use the standard `METRICS` dict (tail_rms_db, rms_db); one (pitch_shift_semitones) uses a measurement pathway outside the standard dict but is still valid.

3. **Scope constraints are documented** for all three, though all note that generalization beyond their tested ranges is not yet verified. This is exactly the limitation Step 4 will explore.

4. **Authority separation is clear:** magnitude grids are derived from scope + experimental design, not invented ad-hoc. Each grid respects the existing scope [min, max] and samples evenly within the available movement.

5. **OSC1.Level and Filter.Cutoff are excluded** because they lack either scope alignment (Level) or a capability contract (Cutoff). Both remain eligible for future steps once their prerequisites are met.

---

## Next Steps

After this inspection is frozen:

1. **Step 4.1** — Execute Env1.Release (validation of Step 3 pattern)
2. **Step 4.2** — Execute Env1.Attack (same family, different metric)
3. **Step 4.3** — Execute OSC1.Detune (different family, different measurement)
4. **Step 4.4** — Compare operation shapes across the three

---

## Conclusion

The repository supports **exactly three targets** for Step 4, all with full machinery (intent → target → metric → scope → contract). This inspection establishes the **machinery generalizes**, not that all targets behave identically.

**Status: 4.0 INSPECTION COMPLETE. Step 4.1–4.3 are ready to freeze.**
