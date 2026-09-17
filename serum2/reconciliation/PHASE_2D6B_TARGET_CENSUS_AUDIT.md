# Phase 2D.6B: Target Census Completion for MATRIX/OWNERSHIP/BODY

**Date**: 2026-09-16  
**Accounting note acknowledged**: `EXACT=219` vs `Population A=220` in the prior report was the 1 `ONE_TO_MANY` row — kept separate here, not merged into a single "established" number without distinction.

---

## What This Pass Did

Processed the three deferred populations from 2D.6A (107 MATRIX, 80 OWNERSHIP, 44 BODY = 231), using only existing evidence — the VST3 census file, and each semantic's own cross-reference data. No experiments.

---

## Critical Correction Surfaced: The MATRIX Classification Was Mostly Wrong

Re-checking `UNKNOWN-MATRIX` (107) against the actual `cross_references` field (not the free-text substring match my Phase 2D.5 script used) found only **15** were genuinely MATRIX-related. The other **92** were false positives — a boilerplate provenance note I wrote during Phase 2A-R.4 ("verified MATRIX.SOURCE has no per-LFO atomic entries") accidentally contained the words "MATRIX" and "SOURCE," causing a substring-match bug to misfile 66 ordinary LFO parameter fields and 26 other semantics into the wrong bucket.

**Genuinely MATRIX-related (15)**: 5 `MACRO.SYS.*` route-mechanism items, 3 `MATRIX.OUT/OUT_INDICATOR/MOD` structural items, 1 `NOISE_OSC.LEVEL` (miscategorized, actually resolved below), 6 `LFO{1-6}.SOURCE` (the drag-handle route-creation affordance).

The 92 false positives were re-investigated properly below.

---

## New Targets Created This Pass (39, All Individually Census-Verified)

Every proposed target was checked by **name** against `EXHAUSTIVE_CENSUS_ALL_2623.json` — not trusted by index arithmetic. Where I extrapolated an index (e.g. LFO2-6's Rise/Delay/Smooth from LFO1's confirmed +5-per-instance pattern), the verification step looked up the actual census entry by name and corrected the index if it disagreed. **0 of 39 proposals were rejected** — all found exact name matches:

```
FILTER1/2.VAR, FILTER1/2.STEREO           4   idx 208,210,219,221 ("Filter N Var/Stereo")
ENV1-4.ATK_CURVE/DEC_CURVE/REL_CURVE      12   idx 229-259 (confirmed +8-per-envelope pattern)
LFO1-6.RISE/SMOOTH/DELAY                  18   idx 263-290 (confirmed +5-per-LFO pattern)
NOISE_OSC.PITCH/PHASE/RAND_PHASE           3   idx 189,191,192
SUB_OSC.COARSE_PITCH/PHASE                 2   idx 197,200
────
Total                                     39
```

These were previously miscategorized as `UNKNOWN-MATRIX` (Filter Var/Stereo, Env curves — due to the boilerplate-text bug) or genuinely `UNKNOWN-HOST`/left unresolved (NOISE_OSC/SUB_OSC remainder, LFO Rise/Delay/Smooth — these had real VST3 backing confirmed earlier in this session but weren't extracted into targets in 2D.6A because the evidence wasn't embedded in each semantic's own `sources[]` field the way the OSC1-3 itemization was).

---

## A Second Bug Found and Fixed: Case-Sensitivity

`NOISE_OSC.LEVEL/PAN/FINE` were still unresolved despite `NOISE.Level`/`NOISE.Pan`/`NOISE.Fine` existing as targets, because my namespace-alias matcher checked `module == 'NOISE OSC'` (all caps) against the actual stored value `'Noise OSC'` (title case) — a silent case mismatch that prevented the rule from ever firing for this module, across every closure round since 2D.1. Fixed; 3 more resolved.

---

## OWNERSHIP (80): Mostly a False Lead, One Genuine Resolution

Inspecting the actual `cross_references` content (not just their presence) showed **most of the 80 are sibling/informational references**, not ownership-transfer pointers to where a "real" target lives. Examples: `ARP.VELOCITY.DECAY` cross-references `ARP.VELOCITY.TARGET` because they're functionally paired controls, not because one owns the other's target. `GLOBAL.VOICE_CONTROL.SEQ.PAN` cross-references `.RANDOM.PAN` and `.OSC_SCOPE` the same way. This was a real overreach in my original Phase 2D.5 heuristic ("has cross_references" ≠ "ownership question").

**One genuine case resolved**: `MIXER.FILTER{1,2}.GRAPHIC_CUTOFF_RESONANCE` — its cross-reference (`FILTER.1.*`) and its own pre-existing notes explicitly state it's "an alternative graphical interaction surface for the SAME underlying Cutoff/Resonance parameters" (the exact R.4 finding). Resolved as `ONE_TO_MANY` → `[Filter.Cutoff, Filter.Resonance]` (and the Filter2 equivalent), not a single target — it genuinely represents both parameters simultaneously (a 2D drag surface).

The remaining 78 stay `UNKNOWN`, correctly — their cross-references don't establish an ownership question the way the original label implied.

---

## BODY (44): Left Unresolved, Correctly

40 `FILTER{1,2}.TYPE_SPECIFIC.*` (the type-conditional 4th-knob controls) + 4 `ENV.*` structural fields. Checked the census around Filter 1's field block and found `Filter 1 X` (idx 211) and `Filter 1 Y` (idx 212) — two generic slots that, by analogy to OSC's confirmed mode-dependent field relabeling, are plausibly the underlying VST3 parameters that get relabeled per-type (Fat/Freq2/Morph/etc. depending on which of 107 filter types is selected).

**Not aliased.** This is exactly the case your instruction warned against — inferring a body-state/host-parameter correspondence from a plausible pattern rather than confirmed evidence. Two generic slots (X, Y) cannot obviously represent 20 distinct type-specific labels without per-type behavioral confirmation of which label maps to which slot under which type. Flagged as a strong candidate for a future targeted check, left `UNKNOWN` here.

---

## Result

```
                    2D.6A (353 targets)   2D.6B (392 targets)
EXACT                     219                   261
ONE_TO_MANY                 1                     3
UNKNOWN                   688                   644

Population A (established)  220                   264
Population B (UNKNOWN)      688                   644
Population C (NO_TARGET)      0                     0
```

**44 more semantics resolved this pass** (39 new census-verified targets + 3 case-bug fix + 2 GRAPHIC_CUTOFF_RESONANCE multi-target). Population C remains 0.

---

## Updated Population Breakdown

```
908 semantics
├── 264 target-established (Population A)
├── 644 not yet established (Population B)
│    ├──  15 genuinely MATRIX-related (5 MACRO.SYS route-mechanism, 3 MATRIX.OUT/OUT_INDICATOR/MOD,
│    │       6 LFO{n}.SOURCE, 1 residual) -- conceptually understood, not targets
│    ├──  78 OWNERSHIP-labeled but actually sibling-reference (mislabeled in 2D.5, corrected
│    │       understanding here -- these are just UNKNOWN, not an ownership question)
│    ├──  44 BODY (40 FILTER type-specific + 4 ENV) -- plausible X/Y-slot hypothesis,
│    │       explicitly not confirmed, left UNKNOWN
│    ├── 102 TRUE-UNKNOWN (unaffected this pass, mostly FX)
│    └── ~405 UI_ACTION/STRUCTURAL/RESOURCE/MATRIX_ROUTE (from 2D.4, unaffected)
└──   0 proven NO_TARGET
```

---

## Deliverables

| File | Contents |
|---|---|
| `_phase2d6b_new_targets_verified.json` | 39 new targets, each with census-verified index |
| `SERUM2_TARGET_NORMALIZED_V3.json` | Complete 392-target vocabulary (353 + 39) |
| `_phase2d6b_final_semantic_rows.json` | 908 rows, final state this snapshot |
| `PHASE_2D6B_TARGET_CENSUS_AUDIT.md` | This document |

---

## Updated Phase State

```
PHASE 2D.6B  MATRIX/OWNERSHIP/BODY evidence completion   ✅ COMPLETE
                39 new census-verified targets, 2 bugs found and fixed,
                1 genuine multi-target resolution, honest non-resolution
                of 78 mislabeled-OWNERSHIP and 44 BODY items

PHASE 2D    (global)   NOT CLOSED
PHASE 2D.6C True operation coverage      ⏳ NEXT (or continue narrowing 644 remainder)
PHASE 2D.7  Representation families       🚫 waits on 2D.6C
```

---

**Status**: 264 of 908 semantics (29%) now target-established — up from 65 at the very first mechanical pass, entirely through evidence reuse and bug-fixing, zero experiments, zero forced `NO_TARGET`. Two silent bugs (substring-match false-positive, case-sensitivity) caught and fixed along the way, each independently verified before being trusted. The 644 remaining are now honestly categorized rather than inflated by mislabeling.
