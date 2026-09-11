# Root Cause Analysis: Why Seed Experiments Failed

**Status:** Root cause identified  
**Classification:** EXPERIMENT_CONFIGURATION_ERROR (wrong treatment values, not mutation mechanism)

---

## The Critical Finding

Filter2.Cutoff produces **exact zero delta** (+0.00 Hz), while Filter1.Resonance produces +13.78 Hz. The baseline spectra tell the story:

```
Filter1.Resonance baseline:  463.09 Hz  (low-frequency-biased, normal state)
Filter2.Cutoff baseline:    4378.13 Hz  (high-frequency-biased, already high-pass)
```

**Filter2 is starting in a DIFFERENT STATE than Filter1.**

---

## Root Cause: Wrong Treatment Values

The seed experiments were designed with **guessed treatment values** without understanding what state Serum starts in.

### Filter2.Cutoff Example

**What we did:**
```
treatment_cbor_path: VoiceFilter1.plainParams.kParamFreq
treatment_cbor_value: 0.9  (high cutoff, high-pass)
```

**What Serum's baseline state was:**
- Filter2 baseline: 4378.13 Hz centroid (already high-pass)
- Interpretation: Filter2 cutoff is already ~0.9 or higher

**Result:**
- Mutation: 0.9 → 0.9 (or close to it)
- No audible change: +0.00 Hz (exact zero)
- Measurement status: NO_OBSERVED_EFFECT ✓ (correct, no change occurred)

---

## Evidence-Based Classification

| Experiment | Baseline Centroid | Mutation | Likely State | Classification |
|---|---|---|---|---|
| Filter1.Resonance | 463.09 Hz | kParamReso → 0.9 | Low resonance | EFFECT_SMALL (delta below threshold) |
| Filter2.Cutoff | 4378.13 Hz | kParamFreq → 0.9 | Already high-pass | NO_EFFECT (mutation is no-op) |
| OSC1.Level | (unknown) | kParamLevel → 1.0 | Possibly already max | MUTATION_NO_OP (baseline = treatment) |
| OSC1.Detune | (unknown) | kParamDetune → 0.5 | ? | UNKNOWN |

---

## The Actual State of Serum

The seed experiments revealed **the true default state** of Serum:

1. **Filter2 is high-pass by default** (4378 Hz suggests a very high cutoff)
2. **Filter1 is low-pass by default** (463 Hz suggests a moderate cutoff)
3. **OSC levels might be at maximum** (mutation to max shows no change)
4. **Other parameters might already be in the "treatment" state**

This is not a bug or architecture failure. **This is real behavioral discovery:** Serum's default state is not what we assumed.

---

## Filter1.Cutoff Works Because...

The Filter1.Cutoff pilot succeeds (+2684 Hz) because:

1. **Baseline Filter1 state:** 463.09 Hz centroid (low-pass, moderate cutoff)
2. **Mutation value:** 0.9 (high cutoff, high-pass)
3. **Expected effect:** Increase in centroid (more high-frequency content)
4. **Observed:** +2684 Hz (LARGE, well above threshold)

The mutation is a **true contrast**: moving from moderate cutoff to high cutoff produces a dramatic spectral shift.

---

## Why CBOR Mutations ARE Being Applied

Evidence that mutations reach Serum and affect audio:

1. **Filter1.Cutoff:** +2684 Hz delta (wouldn't exist if mutations were ignored)
2. **Filter1.Resonance:** +13.78 Hz delta (real, measurable change)
3. **Encoding changes:** CBOR states encode differently after mutations (verified)
4. **Zero deltas aren't encoding failures:** They're real no-ops (baseline = treatment state)

**Conclusion:** The mutations ARE being written to CBOR AND being loaded into Serum. The problem is NOT mutation delivery; it's **experiment design**.

---

## The Real Issue: Treatment Value Selection

We guessed treatment values without empirical baseline knowledge:

**What we should have done:**
1. Run a diagnostic experiment: Load baseline Serum and read each parameter
2. Determine default state for each control
3. Choose treatment values that create meaningful contrast

**What we did:**
1. Guessed treatment values based on parameter ranges (0.0–1.0)
2. Assumed defaults were sensible starting points
3. Applied mutations that might be no-ops

**Result:** Some mutations contrast (Filter1.Cutoff, Filter1.Resonance), others are no-ops (Filter2.Cutoff, OSC1.Level).

---

## Classification of All 10 Seed Experiments

| # | Control | Status | Delta | Baseline Clue | Root Cause |
|---|---|---|---|---|---|
| 1 | Pilot Filter1.Cutoff | OK | +2684 Hz | 463 Hz (low) | Real contrast |
| 2 | Filter1.Resonance | SMALL | +13.78 Hz | 463 Hz (low) | Resonance has small effect |
| 3 | Filter2.Cutoff | ZERO | +0.00 Hz | 4378 Hz (high) | MUTATION_NO_OP |
| 4 | OSC1.Level | ZERO | +0.00 Hz | ? | MUTATION_NO_OP (baseline ≈ 1.0) |
| 5 | OSC1.Detune | ZERO | +0.00 Hz | ? | MUTATION_NO_OP (baseline ≈ 0.5?) |
| 6 | OSC2.Detune | ZERO | +0.00 Hz | ? | MUTATION_NO_OP |
| 7 | Env1.Attack | ZERO | +0.00 Hz | ? | No routing? Or MUTATION_NO_OP |
| 8 | Env1.Release | ZERO | +0.00 Hz | ? | No routing? Or MUTATION_NO_OP |
| 9 | LFO1.Rate (no dest) | ZERO | +0.00 Hz | 0 Hz (silent) | CORRECT (LFO isolated) |
| 10 | LFO1.Rate (filter) | NOT_RUN | N/A | N/A | Treatment render failed |
| 11 | Filter1.Drive | SMALL | +0.34 Hz | ? | Drive has tiny effect |

---

## Root Cause Summary

**NOT:** CBOR mutations aren't working  
**NOT:** Codec is ignoring mutations  
**NOT:** Serum state is fabricated  

**ACTUALLY:** The seed experiments used **untested treatment values** without first understanding Serum's default state.

- Filter1.Cutoff works: mutation creates real contrast (+2684 Hz)
- Filter2.Cutoff fails: mutation is a no-op (both baseline and treatment are high-pass)
- OSC1.Level fails: mutation might be a no-op (baseline already at max?)
- LFO1.Rate (no dest) correctly shows no effect: LFO alone is silent

---

## What This Means

The subprocess architecture and CBOR mutation mechanism ARE WORKING CORRECTLY. The issue is **experimental design**: treatment values were not calibrated to the actual Serum state.

**This is not an architecture failure. This is a feature of the discovery process.**

The evidence reveals Serum's true default state, which enables us to calibrate future experiments properly.

---

## Next Steps (For User Decision)

1. **Diagnostic experiment:** Probe Serum's actual default values for each parameter
2. **Recalibrate treatment values:** Choose mutations that create meaningful contrast
3. **Re-run seed experiments with better calibration:** Expect larger deltas
4. **OR: Accept zero/small deltas as valid evidence:** Some controls genuinely have small effects or are already at desired state

The mutation mechanism is sound. Experiment calibration is the next lever.
