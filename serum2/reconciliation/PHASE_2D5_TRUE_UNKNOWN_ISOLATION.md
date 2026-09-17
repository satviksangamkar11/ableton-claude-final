# Phase 2D.5: Isolating the True-UNKNOWN Population

**Date**: 2026-09-16  
**Method**: Split the 439 `UNKNOWN`-representation semantics using each record's *own already-embedded* source evidence — no new investigation, no new UI probing.

---

## The Split

```
439 UNKNOWN (from Phase 2D.4)
  ↓ split by embedded evidence
UNKNOWN-MATRIX        107   cross-referenced to a MATRIX source/destination concept
UNKNOWN-HOST          104   own source evidence cites direct VST3 host-param backing
                             (Phase 2A-R.5/R.6 census itemization) -- just no targets.py entry
UNKNOWN-TRUE          104 → 102 (2 resolved this round, see below)
UNKNOWN-OWNERSHIP      80   has cross_references implying shared/cross-section ownership
UNKNOWN-BODY           44   itemized from aggregate closure-ledger prose, no independent
                             host-parameter confirmation
```

**Only 102 of the original 908 semantics (11.2%) are now genuinely without any representation-path evidence at all** — down from 788 undifferentiated, then 439 after representation-class splitting, now 102 after evidence-based sub-classification.

---

## Why Each Bucket Is NOT the Same Problem

- **UNKNOWN-HOST (104)**: These are NOT representation-unknown. Phase 2A-R.5 directly itemized them from the VST3 host-parameter census (e.g. `OSC1.SEMI`, `OSC1.FINE`, `OSC1.START`, `OSC1.LOOP_START` — all confirmed real fields at specific VST3 indices). The gap here is `targets.py` never got a target entry created, not that the control's representation is unclear. This is a **target-vocabulary backlog**, cleanly distinct from a representation-path question.

- **UNKNOWN-MATRIX (107)**: Cross-referenced to MATRIX but not a MATRIX record itself — e.g. `ENV1.SOURCE`/`LFO1.SOURCE` (the drag-handle UI affordance that *initiates* a MATRIX route). Representation path is "MATRIX route creation mechanism," already conceptually understood via the MATRIX_ROUTE class from 2D.4 — just not itself classified as one since it's technically a UI-interaction record, not a route record.

- **UNKNOWN-OWNERSHIP (80)**: Has `cross_references` pointing elsewhere — same shape of question as the resolved OSC Enable/Level/Pan and FILTER Level/Mix/Enable cases, just not yet individually checked for a specific target match.

- **UNKNOWN-BODY (44)**: Itemized from closure-ledger aggregate prose (the same FILTER/ENV/LFO source category that produced the earlier 188 additions), but without the kind of direct field-name confirmation that let those resolve. Plausibly real body-state fields, unconfirmed.

- **UNKNOWN-TRUE (102)**: No representation-path evidence of any kind in the semantic's own source records. Concentrated in **FX (72)**, ARP (11), MIXER (8, after this round's 2 fixes), GLOBAL (8), CLIP (3).

---

## Fix Applied This Round

`MIXER.BUS1.LEVEL` and `MIXER.BUS2.LEVEL` → `BUS1.Level`/`BUS2.Level`. Direct, case-normalized match — same physical bus-channel fader, no ambiguity, simply missed by the namespace-alias matcher (which never had a `MIXER.BUS{n}.*` rule). Both moved from `UNKNOWN-TRUE` to mapped.

---

## UNKNOWN-TRUE (102), Composition

The FX concentration (72) is the dominant remaining population. Sampled names: `FX.BODE.DIR/WIDTH/FEED/BALANCE/BLUR/WET`, `FX.CHORUS.DELAY1/DELAY2/WET`, `FX.COMPRESSOR.THRESH/X_LOW/BELOW/X_HIGH/BAND_H/BAND_M/BAND_L/BAND_GRAPHIC/WET`, `FX.CONVOLVE.SIZE/TONE`. These are FX-module-internal controls with abbreviated/alternate naming (`WET` vs the target vocabulary's `MixOrGain`, `THRESH` vs `Threshold`, `X_LOW`/`X_HIGH`/`BAND_H/M/L` — compressor-specific band-crossover concepts that may not have any `targets.py` equivalent at all).

This is genuinely a case for either (a) FX-specific alias rules with real evidence (e.g. confirming `WET` ↔ `MixOrGain` is the same UI label under two names, similar to the EQ situation), or (b) accepting these as a real, uncovered target-vocabulary gap. **Not resolved in this pass** — flagged, not force-matched, consistent with the discipline applied throughout.

---

## Updated Three-Population Framework

```
Population A (target established):        122 semantics (120 prior + 2 BUS fixes)
Population B (UNKNOWN, now sub-typed):     786 semantics
  - UNKNOWN-HOST         104  (target-vocabulary gap, not representation gap)
  - UNKNOWN-MATRIX       107  (route-mechanism, conceptually understood)
  - UNKNOWN-OWNERSHIP     80  (likely resolvable, same pattern as solved cases)
  - UNKNOWN-BODY          44  (plausible body-state, unconfirmed)
  - UNKNOWN-TRUE         102  (genuinely unresolved, concentrated in FX)
  - [UI_ACTION/STRUCTURAL/RESOURCE/MATRIX_ROUTE from 2D.4]  ~349
Population C (proven NO_TARGET):             0 semantics
```

Population C is still empty — correctly.

---

## Deliverables

| File | Contents |
|---|---|
| `_phase2d5_unknown_split.json` | 439 rows with `sub_class` and evidence-based reasoning |
| `PHASE_2D5_TRUE_UNKNOWN_ISOLATION.md` | This document |

---

## Recommendation

The genuinely open population for further work is now **102 semantics (mostly FX)**, not 908, not 788, not 439. This is the precondition your master plan asked for: a small enough remainder that targeted, evidence-driven closure (or explicit acceptance as a target-vocabulary gap) is tractable, rather than needing per-semantic investigation at scale.

The `UNKNOWN-HOST` (104) and `UNKNOWN-OWNERSHIP` (80) buckets are the next-highest-leverage targets if further closure is wanted — both have a clear, cheap resolution path (target-vocabulary extension for HOST; cross-reference-following for OWNERSHIP) using patterns already proven twice in this reconciliation.

---

## Updated Phase State

```
PHASE 2D.5  True-UNKNOWN isolation                    ✅ COMPLETE (102 genuinely unresolved)
PHASE 2D.6  Operation coverage (per representation family)   ⏳ READY TO START
PHASE 2D.7  Representation families (final derivation)        🚫 waits on 2D.6
```

---

**Status**: Reconciliation has converged from an undifferentiated 788-UNKNOWN mass to a 102-semantic genuinely-unresolved core, with every intermediate bucket carrying its own evidence-based classification and reasoning. Ready to proceed to operation coverage on the established/candidate populations, or continue narrowing the 102 — your call.
