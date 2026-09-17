# Phase 2D.6: Operation Coverage for the 122 Target-Established Semantics

**Date**: 2026-09-16  
**Scope**: The 122 semantics from Population A only. The 786 not-yet-established semantics (104 UNKNOWN-HOST, 107 UNKNOWN-MATRIX, 80 UNKNOWN-OWNERSHIP, 44 UNKNOWN-BODY, 102 TRUE-UNKNOWN, plus the ~349 UI_ACTION/STRUCTURAL/RESOURCE from 2D.4) remain open in parallel, not resolved here.

---

## Operation Mechanism Grouping (Not 122 Individual Experiments)

```
NUMERIC_SCALAR_MUTATION             42   confirmed continuous/scalar control_type
NUMERIC_SCALAR_MUTATION_CANDIDATE   18   inferred from label + VST3_PLAIN_PARAM/HOST_FIELD kind
                                          (MIXER Pan/Level/Wet, FX Shift/Range/Drive/Gain fields
                                          whose control_type was never recorded on the semantic side)
MATRIX_ROUTE_MUTATION                21   ROUTING_SLOT_FIELD-backed targets (BUS1Send/BUS2Send/Route family)
STRUCTURAL_OPERATION                 13   structural_action=True semantics
ENUM_MUTATION                         3   discrete-option controls
UNCLASSIFIED_MECHANISM               25   insufficient metadata to classify even provisionally
────
Total                                122
```

This is the actual precondition for minimum-experiment selection: **6 mechanism classes**, not 122 independent parameters. A representative from each of the first 5 classes (`UNCLASSIFIED_MECHANISM` needs its own metadata investigation before it can even be grouped) would cover the operation semantics for the great majority of the 122.

---

## Existing Evidence Applied (Not New Experiments)

Searched the project's existing DawDreamer experiment corpus (`A_SEED_EXPERIMENT_*_EVIDENCE.json`, `DIAG_*.json`) for prior render-level evidence matching any of the 122 established target_ids. Found **8 direct matches**, including catching a naming variant (`Filter1.Cutoff` in the experiment corpus vs. `Filter.Cutoff` in `targets.py` — the same R.4-established generic-alias gap, applied here to reused evidence rather than re-derived):

| semantic_id | target_id | mutation_path | write | causal |
|---|---|---|---|---|
| `FILTER1.CUTOFF` | `Filter.Cutoff` | `VoiceFilter0.plainParams.kParamFreq` | VERIFIED | **VERIFIED** (RMS + spectral centroid both EFFECT_OBSERVED) |
| `FILTER1.RESONANCE` | `Filter.Resonance` | `VoiceFilter0.plainParams.kParamReso` | VERIFIED | **VERIFIED** (corrected re-run showed EFFECT_OBSERVED on RMS) |
| `FILTER1.DRIVE` | `Filter.Drive` | `VoiceFilter0.plainParams.kParamDrive` | VERIFIED | UNVERIFIED (render succeeded, no effect detected by these 2 metrics) |
| `FILTER2.CUTOFF` | `Filter2.Cutoff` | `VoiceFilter1.plainParams.kParamFreq` | VERIFIED | UNVERIFIED |
| `ENV1.ATTACK` | `Env1.Attack` | `VoiceEnv0.plainParams.kParamAttackTime` | VERIFIED | UNVERIFIED |
| `ENV1.RELEASE` | `Env1.Release` | `VoiceEnv0.plainParams.kParamReleaseTime` | VERIFIED | UNVERIFIED |
| `LFO2.RATE` | `LFO1.Rate` | `VoiceModulation0.plainParams.kParamRate` | VERIFIED | UNVERIFIED |
| `MIXER.OSC_A.LEVEL` | `OSC1.Level` | `VoiceOsc0.plainParams.kParamLevel` | VERIFIED | UNVERIFIED |

**`WRITE` is VERIFIED for all 8** — every one has a `treatment_rendered: true` render, meaning the mutation was successfully applied and the plugin processed it without error. `CAUSAL_BEHAVIOR` is `UNVERIFIED` (not `CONTRADICTED`) where `NO_OBSERVED_EFFECT` was returned — a null result on RMS/spectral-centroid metrics doesn't disprove the parameter works, it means those two metrics weren't sensitive to it at the tested magnitude. Distinguishing `UNVERIFIED` from `CONTRADICTED` here matters: `CONTRADICTED` should be reserved for evidence that actively disproves function, which none of this is.

**Neither `READ`, `RESTORE`, `PERSISTENT`, nor `AUTOMATABLE` has any existing evidence** in this corpus for any of the 122 — these experiment files only capture a one-shot baseline/treatment render comparison, not a full read→mutate→readback→restore→persist→automate cycle. Left `UNVERIFIED` across the board, honestly.

---

## The One Piece of Complete Operation Evidence in This Whole Reconciliation

Worth restating: Phase 2A-R.9b's live Clip Player Rate test is the **only** row anywhere in this project with a full `read→mutate→readback→restore` cycle actually executed and confirmed (`0.5 → 0.15 confirmed → 0.5 confirmed`). It's not part of the 122 (Clip Player isn't a `targets.py` entry), but it's the template for what a genuinely complete operation-coverage row looks like, and the method (DawDreamer `get_parameter`/`set_parameter`, direct and cheap) is immediately reusable for the 122.

---

## Remaining 114 of 122: No Operation Evidence Yet

The other 114 established semantics have a confirmed **target** (Population A) but **zero** operation-coverage evidence — not even a WRITE test. This is the honest state: target-mapping and operation-proof are different completion states, exactly as your framework separates them.

---

## Recommended Minimum Experiment Set (Selection, Not Execution)

One representative per mechanism class, prioritizing ones *without* existing evidence to maximize new information per experiment:

| Mechanism | Representative candidate | Why |
|---|---|---|
| `NUMERIC_SCALAR_MUTATION` | Already have 2 VERIFIED (`Filter.Cutoff`, `Filter.Resonance`) — mechanism is proven | Reuse, don't re-test |
| `NUMERIC_SCALAR_MUTATION_CANDIDATE` | `MIXER.OSC_A.PAN → OSC1.Pan` | Untested; would also confirm the control_type inference used to classify this group |
| `MATRIX_ROUTE_MUTATION` | One of the 21 BUS1Send/BUS2Send/Route family (e.g. `MIXER.OSC_A.BUS1 → OSC1.BUS1Send`) | Completely untested mechanism class — no existing evidence anywhere |
| `STRUCTURAL_OPERATION` | One of the 13 | Untested — needs its own read/write model (likely not VST3 parameter mutation at all) |
| `ENUM_MUTATION` | One of the 3 | Untested — smallest group, cheap to fully qualify |
| `UNCLASSIFIED_MECHANISM` | N/A | Needs metadata investigation (control_type backfill) before an experiment can even be designed |

**Not run in this pass** — this is a selection, per your instruction to build the coverage matrix and mechanism grouping, not to execute new experiments yet.

---

## Parallel Queue Status (Unchanged, Explicitly Not Closed)

```
786 not-yet-established, held open in parallel:
  104 UNKNOWN-HOST        — target-vocabulary backlog (priority 2, per your ordering)
  107 UNKNOWN-MATRIX      — route-mechanism, conceptually understood
   80 UNKNOWN-OWNERSHIP   — likely resolvable via proven cross-reference pattern (priority 4)
   44 UNKNOWN-BODY        — plausible body-state, unconfirmed (priority 3)
  102 TRUE-UNKNOWN         — genuinely open, concentrated in FX (priority 1, per your ordering)
```

---

## Wording Correction Applied

Per your instruction, prior status language is corrected: Phase 2D.5's isolation is **"true-UNKNOWN isolation complete for the current reconciliation snapshot"** — not a claim that the target universe itself is complete. Later alias discoveries could still move semantics between buckets; this snapshot is a working state, not a final boundary.

---

## Deliverables

| File | Contents |
|---|---|
| `SERUM2_OPERATION_COVERAGE_MATRIX.json` | 122 rows: representation_path (mechanism), read/write/restore/persistent/automatable/causal_verified, evidence_refs |
| `PHASE_2D6_OPERATION_COVERAGE.md` | This document |

---

## Updated Phase State

```
PHASE 2D.6  Operation coverage (122 established)      ✅ COMPLETE (grouping + existing-evidence reuse)
                8 rows with WRITE=VERIFIED via existing corpus, 2 with CAUSAL=VERIFIED
                114 rows with confirmed target but zero operation evidence
                6 mechanism classes identified for minimum-experiment selection

PHASE 2D    (global)                                   NOT CLOSED — 786-semantic queue remains open
PHASE 2D.7  Representation families (final)             ⏳ NEXT — can now proceed on the 122's
                                                             6 mechanism classes without waiting on
                                                             the 786 queue
```

---

**Status**: Operation coverage established for the 122, using existing evidence wherever it already existed rather than re-running experiments. 786-semantic parallel queue explicitly unresolved, not folded into this closure. Ready for representation-family derivation on the mechanism-grouped 122, or continued work on the priority-ordered 786 queue — your call per the priorities you set (FX true-unknowns → body-state → structural/resource → ownership).
