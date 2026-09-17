# Phase 2D.6C: Operation Coverage for the 264 Established Mappings

**Date**: 2026-09-16  
**Status correction acknowledged**: Phase 2D (global) is NOT closed. This document covers operation coverage for Population A (264) only; the 644-semantic queue remains open, broken out below rather than left as an undifferentiated mass.

---

## Representation Grouping (264, Not 264 Individual Experiments)

```
HOST_PARAMETER_SCALAR         209   continuous/scalar VST3 parameters
SHARED_PHYSICAL_PARAMETER      46   same physical param, discovered via 2 UI surfaces (R.4/R.7 findings)
HOST_PARAMETER_ENUM             3   discrete-option VST3 parameters
STRUCTURAL_OPERATION            3   UI mechanism, not a parameter write
MULTI_TARGET                    2   one semantic maps to multiple targets simultaneously
MATRIX_ROUTE                    1   routing-relationship concept
────
264
```

No `HOST_PARAMETER_TOGGLE`, `BODY_STATE_FIELD`, or `RESOURCE_OPERATION` appear in the *established* 264 — consistent with the reconciliation history: the toggle-shaped candidates (Enable fields) resolved into `SHARED_PHYSICAL_PARAMETER` via the R.7 ownership findings rather than staying as standalone toggles; body-state and resource semantics never got a `targets.py` entry in the first place, so they can't appear in Population A by definition.

**6 genuinely distinct mechanisms**, not 264. This is the actual precondition for minimum-experiment selection.

---

## Operation Status — Extracted From Existing Evidence Only, Not Inferred

Per your explicit instruction, `WRITE=VERIFIED` was never used to infer `READ`/`PERSISTENCE`/`AUTOMATION`/`CAUSAL`. Each field was populated only where direct evidence exists:

| Field | VERIFIED | UNVERIFIED | NOT_APPLICABLE |
|---|---|---|---|
| `read_status` | 4 | 260 | 0 |
| `write_status` | 14 | 250 | 0 |
| `restore_status` | 4 | 260 | 0 |
| `persistence_status` | 0 | 264 | 0 |
| `automation_status` | 0 | 261 | 3 |
| `causal_status` | 2 | 262 | 0 |

**Zero `CONTRADICTED`** anywhere — no evidence in this project actively disproves any of the 264. **Zero `persistence_status: VERIFIED`** — no save/reload cycle has ever been tested for any of the 264 established mappings, across the entire project history. This is a genuinely open gap, not an oversight in this pass.

### Where the 14 `write_status: VERIFIED` Came From

- **10** from the existing DawDreamer experiment corpus (`A_SEED_EXPERIMENT_*`, `DIAG_*` — baseline/treatment renders that succeeded)
- **4** from Phase 2A-R.6's embedded `MUTABLE_RESTORED` census evidence (`SUB_OSC.PITCH_TRACK/SHAPE/CONT_PHASE`, `NOISE_OSC.PITCH_TRACK` — these were actually mutated and read back during the original census experiment, which is why they also get `read_status`/`restore_status: VERIFIED`, not just write)

### Where the 2 `causal_status: VERIFIED` Came From

`FILTER1.CUTOFF`/`FILTER1.RESONANCE` — the only two rows in this entire 264-row matrix with a confirmed audible effect (RMS/spectral-centroid `EFFECT_OBSERVED`), reused from the existing experiment corpus, not re-tested.

---

## Minimum Experiment Set — Derived, Not Assumed

Per your instruction not to assume the mechanism count in advance, this is what the evidence actually supports as **genuinely untested representation classes**:

| Mechanism | Existing evidence | Still needs a representative |
|---|---|---|
| `HOST_PARAMETER_SCALAR` | 2 causal-verified (Cutoff, Resonance), several write-verified | Full cycle (read→mutate→readback→restore→**persist**→**automate**) never proven even for these 2 |
| `SHARED_PHYSICAL_PARAMETER` | 0 | Completely untested — is the "shared" claim itself behaviorally true (does writing via one semantic surface show up when reading the other)? |
| `HOST_PARAMETER_ENUM` | 0 | Completely untested |
| `STRUCTURAL_OPERATION` | 0 | Completely untested — likely not a VST3-parameter-shaped operation at all |
| `MULTI_TARGET` | 0 | Completely untested — does mutating one of the multiple targets affect the others independently or jointly? |
| `MATRIX_ROUTE` | 0 | Completely untested |

**Not run in this pass.** This table is the selection surface for when experiments are authorized, per your explicit "do not run 264 experiments" and "keep the 644 separate" instructions.

---

## The 644 Unresolved Queue, Broken Out (Not a Mass)

```
UNKNOWN_STRUCTURAL       230   UI_ACTION/STRUCTURAL_OPERATION representation class (2D.4),
                                not yet target-established -- likely never will be (these are
                                menu items, slot buttons, editor mechanisms, not parameters)
UNKNOWN_MATRIX            82   genuine MATRIX-route-adjacent (15 confirmed via cross_references
                                in 2D.6B + 67 more classified MATRIX_ROUTE via representation
                                path from 2D.4 but not yet target-established)
UNKNOWN_OWNERSHIP         78   cross-references exist but proved to be sibling/informational,
                                not ownership-transfer (2D.6B finding) -- mislabeled bucket name
                                carried forward for continuity, not because the ownership
                                hypothesis is still believed
UNKNOWN_RESOURCE          51   BROWSER section + resource_dependency-bearing semantics
TRUE_UNKNOWN             153   no representation-path evidence of any kind (concentrated in FX,
                                per 2D.5's original 102 plus residual reclassification)
UNKNOWN_BODY              44   FILTER type-specific (40) + ENV structural (4) -- X/Y generic-slot
                                hypothesis noted in 2D.6B, not confirmed, not aliased
UNKNOWN_HOST_BACKLOG       6   PROVEN_NOT_USER_CONTROL fields excluded from target creation in
                                2D.6A -- genuinely has no meaningful target to create, correctly
                                small and stable
────
644
```

None of these were touched by experiments this pass. `UNKNOWN_STRUCTURAL` (230) is almost certainly not going to convert into target-established mappings at all — these are UI mechanisms, and the master-plan distinction between "target coverage" and "operation coverage" applies differently to them (their "operation" is more likely UI automation than VST3 parameter mutation, a different control route entirely).

---

## Deliverables

| File | Contents |
|---|---|
| `SERUM2_OPERATION_COVERAGE_MATRIX.json` | 264 rows: representation, read/write/restore/persistence/automation/causal status, evidence_refs |
| `_phase2d6c_unresolved_buckets.json` | 644 semantics split into the 7 named buckets |
| `PHASE_2D6C_OPERATION_COVERAGE_AUDIT.md` | This document |

---

## Updated Phase State

```
PHASE 2D.6C  Operation coverage (264 established)      ✅ COMPLETE
                6 genuine representation mechanisms identified (not 264 individual proofs)
                14/264 have WRITE evidence, 4/264 full read+write+restore, 2/264 causal,
                0/264 persistence or automation evidence anywhere

PHASE 2D    (global)                                    NOT CLOSED -- 644 queue explicit, not folded in
PHASE 2D.7  Representation families                     ⏳ can now proceed on the 264's 6 mechanisms
                                                             OR continue narrowing 644 -- your call
```

---

**Status**: Operation coverage established honestly — most of the 264 have a target but zero operation proof, which is the correct state to report rather than assume. 6 distinct mechanisms identified as the minimum-experiment surface once experiments are authorized. 644 unresolved semantics organized into 7 evidence-based buckets, none force-resolved, none spent on experiments this pass.
