# Phase 2D.4: Representation-Path Classification Audit

**Date**: 2026-09-16  
**Method**: Bulk classification of all 908 semantics using existing evidence (2D.3 mapping results, structural_action flags, section conventions, resource_dependency fields) — no new investigation performed.

---

## Result: 788 Undifferentiated UNKNOWN → 439 True UNKNOWN + 6 Categorized Populations

```
                              Count   Confidence
UI_ACTION                      200   214 CANDIDATE (across UI_ACTION + a few others)
HOST_PARAMETER                  73   ESTABLISHED (all 73 — these are the prior EXACT/ALIAS_RULE matches)
MATRIX_ROUTE                    68   mix of ESTABLISHED/CANDIDATE
RESOURCE_OPERATION              51   ESTABLISHED (BROWSER section + resource_dependency)
SHARED_PHYSICAL_PARAMETER       46   ESTABLISHED (37) + CANDIDATE (9, structural-pattern-only)
STRUCTURAL_OPERATION            30   ESTABLISHED
MULTI_TARGET                     1   ESTABLISHED (MATRIX.ROUTING.SIGNAL_BALANCE)
────
UNKNOWN (true)                 439   genuinely unclassified
```

`ESTABLISHED` total: 255. `CANDIDATE` total: 214 (plausible from structural evidence but not individually confirmed). `UNKNOWN`: 439.

This is not a re-run of the target matcher — it's a re-reading of the **same** 908×255 mapping output through a representation-mechanism lens, plus classification of the previously-undifferentiated `UNKNOWN` mass using each semantic's own structural properties (section, `structural_action` flag, `resource_dependency`, ID patterns already established in this reconciliation — e.g. `MATRIX.SOURCE.*`, `.SLOT.`, `BROWSER.*`).

---

## Why This Matters More Than Another Alias Round

The distinction your framework draws is real, and this pass makes it visible for the first time:

- **73 `HOST_PARAMETER`**: genuinely VST3-host-automatable, confirmed via `targets.py` + census backing
- **46 `SHARED_PHYSICAL_PARAMETER`**: also host-automatable, but via a *different* semantic_id than the one a naive matcher would expect (the OSC/FILTER dual-UI-surface findings)
- **68 `MATRIX_ROUTE`**: not parameter-shaped at all — these are routing-relationship concepts. Controlling them means creating/configuring a route, not writing a scalar value.
- **51 `RESOURCE_OPERATION`**: file/preset/bank operations — an entirely different control mechanism (filesystem/resource layer, not parameter mutation)
- **30 `STRUCTURAL_OPERATION`** + **200 `UI_ACTION`**: menu items, slot navigation, context actions, editor mechanisms — likely require UI automation or structural state manipulation, not VST3 parameter writes at all
- **439 true `UNKNOWN`**: the population that actually needs further work, now correctly isolated from the ~470 that were `UNKNOWN` in 2D.3 purely because they were never parameter-shaped in the first place

This is exactly the point: many of the 788 were never going to resolve into a `target_id` no matter how many aliases were added, because they don't represent VST3 parameters at all. Continuing the alias approach would have kept treating a representation-mechanism question as a naming question.

---

## True UNKNOWN (439), By Section

| Section | Count | Section | Count |
|---|---|---|---|
| OSC | 111 | ENV | 20 |
| FX | 88 | MIXER | 18 |
| LFO | 72 | ARP | 18 |
| FILTER | 44 | CLIP | 5 |
| GLOBAL | 29 | GLOBAL_KEYBOARD | 4 |
| MACRO | 24 | MATRIX | 3 |
| | | VOICE | 3 |

The OSC (111) and LFO (72) concentrations are expected — these are the sections with the most detailed per-instance, per-mode itemization from Phase 2A-R.5/R.9, most of which was never claimed to have a `targets.py` entry (only ~6 of the 41 genuine OSC field types have targets, confirmed in the original OSC closure report).

MACRO's 24 (of 48 total MACRO semantics — the other 24 landed in `UI_ACTION`/`STRUCTURAL_OPERATION`, e.g. `.NAME` fields as UI actions) remain the clearest concrete control gap: no representation path at all has been identified for the macro dial value itself.

---

## What This Pass Did NOT Do

- Did not investigate any individual true-UNKNOWN semantic's actual representation
- Did not attempt to resolve `CANDIDATE`-confidence rows to `ESTABLISHED`
- Did not touch the EQ Left/Right, LFO Shape/Mode/Retrigger, or GLOBAL Quality/Glide/Voicing/VelocityCurve/PitchTracking questions left open in 2D.3 — those remain exactly as documented there, just now carrying a `representation_class` label (mostly `UNKNOWN` or `HOST_PARAMETER`/`CANDIDATE` where a target exists but correspondence is unconfirmed)

---

## Deliverables

| File | Contents |
|---|---|
| `SERUM2_REPRESENTATION_PATH_MATRIX.json` | 908 rows: `representation_class`, `candidate_targets`, `mapping_confidence`, `notes` |
| `SERUM2_REPRESENTATION_PATH_AUDIT.md` | This document |

---

## On the Shared PDF

`Serum 2 What's New.pdf` (20 pages) — checked and confirmed to be the **same** official Xfer summary document already cited extensively throughout this entire reconciliation (referenced by name dozens of times across the closure ledgers as "the official Xfer 'What's New in Serum 2' PDF"). It has already been incorporated as evidence everywhere it was applicable during the original semantic discovery phase. Not a new source — no re-reading performed, since it wouldn't add anything not already captured.

If you intended a different, more complete document (e.g. the ~350-page full manual referenced but never available in prior sessions), let me know and I'll check it specifically — several open questions (MACRO rename mechanism, LFO Shape/Mode/Retrigger correspondence, EQ Left/Right vs 1/2) would benefit from that higher evidence tier if it exists.

---

## Updated Phase State

```
PHASE 2D.4  Representation-path classification        ✅ COMPLETE
                439 true UNKNOWN (down from 788 undifferentiated)
                255 ESTABLISHED, 214 CANDIDATE across 6 representation classes

PHASE 2D.5  Targeted investigation of true-UNKNOWN     ⏳ NEXT (439 population, not 788)
PHASE 2D.6  Operation coverage (per representation family, not per semantic)  🚫
PHASE 2D.7  Representation families (final)            🚫
```

---

**Status**: 439 semantics now correctly isolated as needing further representation-path work — down from an undifferentiated 788. The other 469 are meaningfully bucketed by control mechanism, which is the actual precondition for minimum-experiment family derivation your master plan calls for.
