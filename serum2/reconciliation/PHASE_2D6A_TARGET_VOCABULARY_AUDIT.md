# Phase 2D.6A: Target Vocabulary Completion + Reconciliation Rerun

**Date**: 2026-09-16  
**Correction acknowledged**: Phase 2D.6 was operation-mechanism grouping + evidence reuse, not operation coverage in the master-plan sense — relabeled accordingly below. This phase (2D.6A) precedes true operation coverage, per your ordering.

---

## What Was Built

`targets.py`'s 255 declared targets were never the complete technical target universe — they're a **source vocabulary**, as you identified. The 104 `UNKNOWN-HOST` semantics each carry their own embedded evidence of a confirmed VST3 host parameter (name + index), gathered during Phase 2A-R.5/R.6's census-based itemization. That evidence was extracted mechanically — **no new discovery, no experiments** — into new target records.

### Extraction Result

```
104 UNKNOWN-HOST candidates
  -  6  excluded: status=PROVEN_NOT_USER_CONTROL (Ratio/Hz Offset x3 oscillators)
                  -- a target for a confirmed non-user-control field would be meaningless
  - 98  new targets created
     0  extraction failures (two note formats handled: R.5's "VST3 field: X, index N,
        class Y" and R.6's "VST3 field 'X', index N, baseline=..., status=...")
────
104 = 98 + 6 + 0, verified
```

Four of the 98 (`SUB_OSC.PITCH_TRACK`, `SUB_OSC.SHAPE`, `SUB_OSC.CONT_PHASE`, `NOISE_OSC.PITCH_TRACK`) carry an extra upgrade: their source notes record `status=MUTABLE_RESTORED` from the original R.6 VST3 census experiment — meaning these weren't just named, they were **actually mutated and restored** during that census run. Their new target records get `write_supported: WRITE_VERIFIED` directly, not `UNKNOWN` like the other 94.

### New Target Schema

Each new target carries, per your spec:

```json
{
  "target_id": "OSC1.SEMI",
  "host_parameter_id": "vst3_idx_24",
  "host_parameter_name": "A Semi",
  "source_evidence": "Semantic record's own embedded sources[] (Phase 2A-R.5/R.6/R.9b census-based itemization)",
  "semantic_candidate": "OSC1.SEMI",
  "representation_class": "HOST_PARAMETER",
  "value_domain": "INTEGER",
  "current_operation_status": "UNKNOWN"
}
```

`target_id` was set equal to the source `semantic_id` — not a new parallel naming scheme. This is deliberate: it's the identifier already established and used throughout this reconciliation, and it avoids inventing a second name for the same thing.

---

## Merged Target Vocabulary

```
255  targets.py (original)
+ 98  evidence-established (Phase 2D.6A)
────
353  total, 0 duplicates
```

Saved as `SERUM2_TARGET_NORMALIZED_V2.json`.

---

## Reconciliation Rerun

```
                     Before (255 targets)   After (353 targets)
EXACT                       121                   219
ONE_TO_MANY                   1                     1
UNKNOWN                     786                   688
MAPPED (reverse)            126                   224
ORPHAN_TECHNICAL           129→                   129
```

**Population A grew from 121 to 220** (98 new + the 1 BUS fix already counted). **Population C remains 0** — no semantic has been declared `NO_TARGET` anywhere in this reconciliation, including through this vocabulary expansion.

The `mapping_basis` for all 98 new resolutions is tagged distinctly: `EVIDENCE_ESTABLISHED_TARGET` — separate from `ALIAS_RULE`/`UI_SURFACE_ALIAS`/`STRUCTURAL_PATTERN_ALIAS`, so the audit trail shows exactly which resolutions came from target-vocabulary completion versus naming/ownership aliasing.

---

## Population State (Updated)

```
908 semantics
├── 220 target-established (Population A)          [+100 from prior 120]
├── 688 not yet target-established (Population B)
│    ├──   6 UNKNOWN-HOST (was 104, now only the 6 excluded PROVEN_NOT_USER_CONTROL remain
│    │       in this bucket -- correctly, since they have no meaningful target to create)
│    ├── 107 UNKNOWN-MATRIX        (untouched -- correctly deferred, needs representation
│    │                              class first, not auto-added as targets, per your instruction)
│    ├──  80 UNKNOWN-OWNERSHIP     (untouched -- same deferral)
│    ├──  44 UNKNOWN-BODY          (untouched -- same deferral)
│    └── 102 TRUE-UNKNOWN          (untouched -- unaffected by this pass, as expected;
│                                    none of these had host-parameter evidence to extract)
│    [remainder: ~349 UI_ACTION/STRUCTURAL/RESOURCE/MATRIX_ROUTE from 2D.4, also untouched]
└──   0 proven NO_TARGET (Population C)
```

The `UNKNOWN-MATRIX`, `UNKNOWN-OWNERSHIP`, and `UNKNOWN-BODY` buckets were deliberately **not** processed this pass — per your explicit instruction, they need their proper representation class established first, not auto-converted to targets the way host-parameter evidence allowed.

---

## Deliverables

| File | Contents |
|---|---|
| `SERUM2_TARGET_VOCABULARY_COMPLETE.json` | 98 new target records, extraction methodology, exclusion/failure lists |
| `SERUM2_TARGET_NORMALIZED_V2.json` | Merged 353-target vocabulary (255 + 98) |
| `_phase2d6a_rerun_semantic_rows.json` | 908 rows, rerun against the 353-target vocabulary |
| `_phase2d6a_reverse_audit.json` | 353-target reverse classification |
| `PHASE_2D6A_TARGET_VOCABULARY_AUDIT.md` | This document |

---

## Updated Phase State

```
PHASE 2D.6A  Target vocabulary completion (UNKNOWN-HOST)   ✅ COMPLETE
                98 new targets, 220 total established (up from 120)
                Population C still 0 -- discipline maintained

PHASE 2D.6B  Same treatment for UNKNOWN-MATRIX/OWNERSHIP/BODY   ⏳ NEXT
                (representation-class-first, not auto-target-creation)
PHASE 2D.6C  True operation coverage (per master-plan definition) 🚫 waits on 2D.6B
PHASE 2D.7   Representation families                              🚫 waits on 2D.6C

PHASE 2D (global)   NOT CLOSED
```

---

**Status**: Cheapest, highest-leverage reduction absorbed — 98 semantics moved from Population B to A using evidence already on hand, zero new experiments, zero forced NO_TARGET declarations. The genuinely open population for representation-path work is now the 233 in UNKNOWN-MATRIX/OWNERSHIP/BODY plus the 102 TRUE-UNKNOWN — not yet touched, correctly held for their own proper treatment.
