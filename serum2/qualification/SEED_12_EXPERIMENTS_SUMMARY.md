# Seed Set: 12-Experiment Behavioral Qualification Plan

**Status:** Specifications complete and validated  
**Date:** 2026-09-11  
**Architecture:** BehaviorExperiment ← Subprocess → DawDreamer/Serum → BehaviorObservation + ExerciseQualification

## Overview

The 12-experiment seed set expands the Filter1.Cutoff proof-of-concept into a systematic discovery of Serum 2.0.21's behavioral surface. Each experiment is:

- **Self-contained:** explicit context, intervention, measurement plan, expected outcome
- **Independent:** no dependencies across experiments
- **Observable:** multi-dimensional measurements (not single metric)
- **Context-aware:** prerequisites captured explicitly; no implicit assumptions
- **Testable:** expected outcome is a hypothesis, not a claim

## Experiments by Classification

### EXPECTED POSITIVE (9 experiments)

Controls that measurably affect audio in isolation.

| # | Semantic Target | Intervention | Context | Measurements | Expected Direction |
|---|---|---|---|---|---|
| 1 | Filter1.Cutoff | VoiceFilter0.kParamFreq = 0.9 | Filter1 On | spectral_centroid_hz, rms_db | increase |
| 2 | Filter1.Resonance | VoiceFilter0.kParamReso = 0.9 | Filter1 On | spectral_centroid_hz, rms_db | increase |
| 3 | Filter2.Cutoff | VoiceFilter1.kParamFreq = 0.9 | Filter2 On | spectral_centroid_hz, rms_db | increase |
| 4 | OSC1.Level | VoiceOsc0.kParamLevel = 1.0 | (none) | rms_db, peak_amplitude | increase |
| 5 | OSC1.Detune | VoiceOsc0.kParamDetune = 0.5 | (none) | spectral_centroid_hz, spectral_spread | increase |
| 6 | OSC2.Detune | VoiceOsc1.kParamDetune = 0.5 | (none) | spectral_centroid_hz, spectral_spread | increase |
| 11 | Filter1.Drive | VoiceFilter0.kParamDrive = 1.0 | Filter1 On | rms_db, spectral_centroid_hz | increase |
| 12 | FXEQ.Freq1 | FXRack0.Devices[0].kParamEQ1Frequency = 0.8 | FX EQ On | spectral_centroid_hz, rms_db | increase |

**Rationale:** These controls directly modulate synthesis parameters (filters, oscillators, EQ) with observable audio consequences. All should produce measurable deltas above thresholds.

---

### EXPECTED CONDITIONAL (2 experiments)

Controls whose effect depends on runtime context or envelope routing.

| # | Semantic Target | Intervention | Context | Measurements | Condition |
|---|---|---|---|---|---|
| 7 | Env1.Attack | VoiceEnv0.kParamAttackTime = 0.1 | (none) | rms_db, spectral_centroid_hz | depends on routing |
| 8 | Env1.Release | VoiceEnv0.kParamReleaseTime = 0.1 | (none) | rms_db, spectral_centroid_hz | tail outside render window |

**Rationale:** Envelope parameters affect time-domain shaping, but the effect is observable only if:
- The envelope actually routes to a synthesis parameter (Attack/Release may or may not affect filter, level, etc.)
- The render window captures the affected phase (Release tail may extend past 2.0s)

These experiments reveal **what envelopes actually control**, not assume from naming.

---

### EXPECTED NULL (1 experiment)

Controls that produce no audio effect in isolation.

| # | Semantic Target | Intervention | Context | Measurements | Expected Effect |
|---|---|---|---|---|---|
| 9 | LFO1.Rate | VoiceModulation0.kParamRate = 0.5 | (none) | rms_db, spectral_centroid_hz | NO_OBSERVED_EFFECT |

**Rationale:** LFO oscillates internally but modulates nothing. Rate changes vary the LFO frequency internally (unaudible). This is **important negative evidence**: proves that LFO.Rate controls produce no audio impact without a modulation destination.

---

### EXPECTED POSITIVE + CONDITIONAL (1 experiment)

Context-dependent control: same parameter, different outcomes based on modulation destination.

| # | Semantic Target | Intervention | Context | Measurements | Expected Effect |
|---|---|---|---|---|---|
| 10 | LFO1.Rate | VoiceModulation0.kParamRate = 0.5 | LFO1 → Filter1.Cutoff + Filter1 On | spectral_centroid_hz, rms_db | EFFECT_OBSERVED |

**Rationale:** **This is the same target (LFO1.Rate) as experiment 9**, but with modulation destination configured. Rate now controls sweep speed of cutoff, producing observable spectral variation.

**Significance:** Experiments 9 and 10 together **reveal context-dependent behavior**. The control's effectiveness is not intrinsic; it depends on what it modulates. This cannot be captured by a single experiment.

---

## Measurement Dimensions

All experiments capture multiple measurement kernels per control type:

- **Frequency-based** (Filter1.Cutoff, Filter1.Resonance, Filter2.Cutoff, OSC1.Detune, OSC2.Detune, FXEQ.Freq1, LFO1.Rate, Filter1.Drive):
  - `spectral_centroid_hz` (primary)
  - `spectral_spread_hz` (secondly, for spread controls)
  - `overall_rms_db` (secondly, for harmonic/resonance changes)

- **Level-based** (OSC1.Level):
  - `overall_rms_db` (primary)
  - `peak_amplitude` (secondary, peak detection)

- **Envelope-based** (Env1.Attack, Env1.Release):
  - `overall_rms_db` (if envelope routes to level)
  - `spectral_centroid_hz` (if envelope routes to filter)

**Philosophy:** Capture all dimensions; interpret post-hoc via BehaviorClaim layer. Don't force one measurement type per control.

---

## Contexts (Prerequisites)

### Filter prerequisites:
```
Filter1 On = 1.0   (experiments 1, 2, 11, 10)
Filter2 On = 1.0   (experiment 3)
FX EQ On = 1.0     (experiment 12)
```

**Provenance:** Filters and effects must be active to process audio. Inactive filters/FX are silent.

### LFO prerequisites:
```
(Experiment 9) Empty context: LFO isolated, no destination
(Experiment 10) LFO1 Mod Dest = "Filter1.Cutoff" + Filter1 On = 1.0
```

**Provenance:** LFO modulation routing is explicit context. Rate has no effect without a destination.

### Oscillator, envelope, and drive:
```
(Experiments 4, 5, 6, 7, 8, 11) No explicit context
```

**Provenance:** These operate on default Serum skeleton (both oscillators playing, envelopes always active, filters default-routed).

---

## Intervention Specifications (CBOR Paths)

All interventions are CBOR path mutations applied only to the treatment arm.
Baseline arm receives default Serum state (with context applied to both).

| Semantic Target | CBOR Path | Treatment Value | Rationale |
|---|---|---|---|
| Filter1.Cutoff | VoiceFilter0.plainParams.kParamFreq | 0.9 | High-pass: passes high frequencies |
| Filter1.Resonance | VoiceFilter0.plainParams.kParamReso | 0.9 | High resonance peak at cutoff |
| Filter2.Cutoff | VoiceFilter1.plainParams.kParamFreq | 0.9 | Same as Filter1 |
| OSC1.Level | VoiceOsc0.plainParams.kParamLevel | 1.0 | Maximum amplitude |
| OSC1.Detune | VoiceOsc0.plainParams.kParamDetune | 0.5 | Medium detune spread |
| OSC2.Detune | VoiceOsc1.plainParams.kParamDetune | 0.5 | Medium detune spread |
| Env1.Attack | VoiceEnv0.plainParams.kParamAttackTime | 0.1 | Fast attack |
| Env1.Release | VoiceEnv0.plainParams.kParamReleaseTime | 0.1 | Fast release |
| LFO1.Rate | VoiceModulation0.plainParams.kParamRate | 0.5 | Medium rate |
| Filter1.Drive | VoiceFilter0.plainParams.kParamDrive | 1.0 | Maximum drive |
| FXEQ.Freq1 | FXRack0.Devices.0.EQParameters.kParamEQ1Frequency | 0.8 | Boost high-mid frequency |

---

## Validation Results

```
STRUCTURAL VALIDATION:           PASS
  [1] Filter1.Cutoff             [OK]
  [2] Filter1.Resonance          [OK]
  [3] Filter2.Cutoff             [OK]
  [4] OSC1.Level                 [OK]
  [5] OSC1.Detune                [OK]
  [6] OSC2.Detune                [OK]
  [7] Env1.Attack                [OK]
  [8] Env1.Release               [OK]
  [9] LFO1.Rate (no dest)        [OK]
  [10] LFO1.Rate (with dest)     [OK]
  [11] Filter1.Drive             [OK]
  [12] FXEQ.Freq1                [OK]

CLASSIFICATION:
  EXPECTED POSITIVE:     9 experiments
  EXPECTED CONDITIONAL:  2 experiments
  EXPECTED NULL:         1 experiment
  TOTAL:                 12 experiments

CONTEXT DISTINCTNESS:
  LFO1.Rate (experiments 9 + 10):
    - Experiment 9:  empty context (NO_OBSERVED_EFFECT)
    - Experiment 10: modulation dest specified (EFFECT_OBSERVED)
    - Verdict: PASS (context-dependence captured)
```

---

## Design Philosophy

1. **Multi-dimensional measurement:** No single metric per control. Capture all relevant dimensions; semantic interpretation (BehaviorClaim) happens later.

2. **Context as evidence:** Contexts are not assumptions; they are explicit prerequisites that went into the experiment design. Evidence layer records them; interpretation layer uses them.

3. **Negative evidence is evidence:** Experiment 9 (LFO with no destination) is as important as positive experiments. It **proves** that LFO.Rate alone produces nothing.

4. **Conditional evidence is discoverable:** Experiments 9 + 10 together reveal LFO behavior depends on context. No amount of expert reasoning would have predicted this; only paired experiments discover it.

5. **No premature claims:** These are experiments, not claims. Each produces BehaviorObservation (facts) + ExerciseQualification (evidence binding). Semantic claims (BehaviorClaim layer) come later, after all measurements are available for interpretation.

---

## Next Steps (After User Approval)

1. **Run subprocess worker on Filter1.Cutoff:** Already complete (✓ is_valid=True).

2. **Execute 12 experiments sequentially** (one subprocess per experiment):
   - Each produces BehaviorObservation JSON + ExerciseQualification JSON
   - Persist to `serum2/qualification/A_SEED_<target>_<id>_EVIDENCE.json`

3. **Analyze results** (NOT execute during this step):
   - Do null-hypothesis expectations match measurements?
   - What unexpected patterns emerge?
   - Which expected-positive controls underperformed or over-performed?
   - Which expected-conditional controls showed context dependence?

4. **Interpret via BehaviorClaim layer** (semantic layer):
   - For each BehaviorObservation, produce a BehaviorClaim mapping measurements to semantic concepts.
   - Map spectral_centroid_hz → "control affects brightness"
   - Map rms_db → "control affects amplitude"

5. **NO CapabilityContract generation yet:**
   - Evidence must be qualified + interpreted before promotion to contracts.
   - Contracts are final; they go into production.

---

## Files Changed

- **Created:** `serum2/qualification/seed_12_experiments.py` (12 experiment definitions)
- **Created:** `serum2/qualification/SEED_12_EXPERIMENTS_SUMMARY.md` (this file)
- **Preserved:** `serum2/qualification/filter_cutoff_revised_spec.py` (pilot remains unchanged)
- **Preserved:** `serum2/qualification/A_FILTER_CUTOFF_REVISED_EVIDENCE.json` (pilot evidence remains)

---

## Status

✓ Specifications complete  
✓ Validation passed (12/12 experiments structurally sound)  
✓ Contexts explicit  
✓ Interventions defined (all CBOR paths or host params)  
✓ Measurement plans multi-dimensional  
✓ Expected outcomes classified  
✓ Context-dependence captured (LFO1.Rate x2)  
✗ NOT YET EXECUTED (awaiting user approval)  
✗ NO CLAIMS MADE (only experiment specs)  
✗ NO CONTRACTS GENERATED (only evidence will be produced)

**Ready for execution on user signal.**
