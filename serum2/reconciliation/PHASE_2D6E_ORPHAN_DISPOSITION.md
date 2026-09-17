# Phase 2D.6E: Reverse-Target Orphan Disposition

**Date**: 2026-09-16  
**Scope**: The 126 orphan targets from 2D.6D, disposed using existing evidence — verified, not assumed.

---

## Discipline Note: A Premature Alias Caught and Retracted

Initial investigation found every FX module has a `.WET` semantic (labeled "Mix — dry/wet blend"), and targets.py's FX-FULL block has a matching `.MixOrGain` target with capability_key `fx_field_*_mix_or_gain`. I aliased 11 of these — **then found 9 of the 11 modules also have a separate, older `.Mix` target** (capability_key `fx_field_*_mix`, no "_or_gain") still live in the dict with a *different* key, not silently overwritten the way `OSC1.Volume` was.

This is a **genuine ambiguity** — the same class of problem as EQ's Left/Right vs 1/2 question — not resolvable by name plausibility. Checked git history for a deprecation marker on either variant: none found. **Retracted the 9 ambiguous aliases** rather than let a plausible-but-unverified guess stand. Kept only the 2 where no competing `.Mix` variant exists (`FXFilter.WET`→`MixOrGain`, `FXDistortion.WET`→`MixOrGain`).

This matters for the audit trail: verify before committing, and un-commit when new evidence contradicts an earlier step, even within the same working session.

---

## Orphan Disposition, Complete Categorization

| Category | Count | Classification | Basis |
|---|---|---|---|
| **LFO6-9 Rate/Shape/Mode/Phase/Retrigger** | 20 | `HEADLESS_FEATURE` | R.4's own closure confirmed LFO7-10 (semantic, 1-based) = target LFO6-9 (0-based) have 0 UI-accessible parameters. Technical-only by confirmed structural fact. |
| **LFO0-6 Shape/Mode/Retrigger** | 18 | `TRUE_ORPHAN` (unconfirmed technical identity) | Zero VST3 host-parameter backing found anywhere (searched twice, confirmed). May not correspond to any real Serum-addressable state. |
| **OSC1-3.Volume/Detune, SUB.Volume/Detune, NOISE.Warp/Type** | 10 | `TECHNICAL_DEAD/SUPERSEDED` (Volume×4) / `TRUE_ORPHAN` (Detune×4, Warp, Type — not yet investigated) | Volume×4 explicitly documented in `OSC_FINAL_CLOSURE_REPORT.md` as dead vocabulary, superseded by `.Level`. Detune/Warp/Type not yet checked this pass. |
| **FX Wet/Mix/MixOrGain ambiguity** | 9 | `AMBIGUOUS_MULTI_CANDIDATE` (newly flagged, not resolved) | Two live targets per module, different capability_keys, no deprecation marker. Genuinely unresolved, same discipline as EQ. |
| **FX Wet→MixOrGain (unambiguous)** | 2 | `MAPPED_TO_EXISTING_SEMANTIC` | Resolved: `FXFilter.WET`, `FXDistortion.WET` — no competing `.Mix` variant exists for these two modules. |
| **FXDelay.TimeL/TimeR** | 2 | `MAPPED_TO_EXISTING_SEMANTIC` | Bug fix: namespace matcher wasn't stripping underscores (`TIME_L`) before CamelCase conversion. Resolved. |
| **FXEQ family** | 9 | `AMBIGUOUS_STRUCTURAL_MODEL` | Left/Right (semantic) vs 1/2 (target) — unresolved since 2D.2, unchanged. |
| **Global.Quality/Glide/Voicing/VelocityCurve/PitchTracking** | 5 | `TRUE_ORPHAN`, individually reasoned | Unchanged from 2D.3 — each has a specific, cited reason for non-resolution. |
| **ARP.Enable** | 1 | `TRUE_ORPHAN` (confirmed genuine semantic gap) | Checked: no ARP master-enable semantic exists in the 908 (unlike Clip Player, which does). Real discovery gap, not a matcher miss. |
| **FXConvolve.IR/IRGain/IRPath, Damping** | 4 | `TRUE_ORPHAN` | Not yet investigated. |
| **FXDistortion.BW/LPHP/LevelOut/Mode/PrePost/Tone** | 6 | `TRUE_ORPHAN` | Not yet investigated. |
| **FXBODE.Direction/Frequency/LevelOut** | 3 | `TRUE_ORPHAN` | Not yet investigated. |
| **FXCompressor.Threshold, MixOrGain(dup of ambiguity above)** | 1 | `TRUE_ORPHAN` | Not yet investigated. |
| **FXPhaser.Frequency, FXReverb.Time/Damping, FXDelay.Time/BW/OffsetL/OffsetR** | 6 | `TRUE_ORPHAN` | Not yet investigated. |
| **FXUtility.Gain/Mono/Phase, FXHyper.Retrigger** | 4 | `TRUE_ORPHAN` | Not yet investigated. |
| **FXFilterFX family (5), FXSplitter family (4)** | 9 | `TRUE_ORPHAN` | Not yet investigated. |
| **Filter.Q, Filter2.Q** | 2 | `TRUE_ORPHAN` | Not yet investigated. |

---

## Net Result This Pass

```
Before: 126 orphans (28 explained in 2D.6D, 98 unresolved)
This pass:
  +4  genuinely resolved (2 FX Wet unambiguous, 2 Delay TimeL/TimeR bug fix)
  +9  newly and explicitly categorized as AMBIGUOUS_MULTI_CANDIDATE (not resolved,
      but no longer silently unexamined — a specific, named question)
  +1  ARP.Enable confirmed as a genuine semantic-discovery gap (not a matcher issue)
────
Population A: 268 → 272 (net +4)
Remaining TRUE_ORPHAN (uncategorized or confirmed unresolved): ~85 of 122
```

---

## Full Orphan Ledger

```
28  explained (2D.6D: 20 headless-LFO + 8 dead-vocabulary... actually 4 dead + 
                4 not-yet-checked, corrected count below)
 4  resolved this pass (FX Wet unambiguous x2 + Delay TimeL/TimeR x2)
 9  flagged AMBIGUOUS_MULTI_CANDIDATE (FX Wet/Mix, genuine two-target ambiguity)
 9  flagged AMBIGUOUS_STRUCTURAL_MODEL (FXEQ Left/Right vs 1/2)
 1  confirmed genuine semantic gap (ARP.Enable)
 5  individually reasoned open items (Global.* remainder)
~85 not yet individually investigated (mostly single-module FX fields:
     Convolve/Distortion/BODE/Compressor/Phaser/Reverb/Delay/Utility/FilterFX/Splitter
     remainders, Filter.Q, OSC Detune/Warp/Type remainder)
```

**122 total orphan targets** (126 - 4 resolved). Of these, 37 now carry an explicit disposition (headless/dead/ambiguous/gap), leaving **85 genuinely uncategorized** — smaller than the 98 at the start of this pass, but not closed.

---

## Deliverables

| File | Contents |
|---|---|
| `_phase2d6e_semantic_rows_v2.json` | 908 rows, updated after resolution + retraction |
| `PHASE_2D6E_ORPHAN_DISPOSITION.md` | This document |

---

## Updated Phase State

```
PHASE 2D.6E  Reverse-target orphan closure     🟡 ADVANCED, NOT CLOSED
                272/396 targets have semantic ownership (up from 268)
                37/122 remaining orphans now individually disposed
                85 orphans still uncategorized (mostly single-instance FX fields)
                1 premature alias caught and retracted mid-pass (audit discipline preserved)

PHASE 2D.6F  Resolve 169 semantic UNKNOWNs      🚫 NOT STARTED (per your ordering)
PHASE 2D.6G  Freeze bidirectional control-path graph   🚫 waits on 2D.6E/F
PHASE 2D    (global)                             NOT CLOSED
```

---

**Status**: Orphan disposition advanced with verification discipline maintained throughout — including catching and reversing my own premature commitment. 85 targets remain genuinely uncategorized, concentrated in single-instance FX module fields not yet individually checked. Recommend either continuing target-by-target on the FX remainder (likely to yield a few more confirmed dead/duplicate patterns given the ambiguity already found) or moving to 2D.6F on the 169 semantic UNKNOWNs per your stated ordering — your call.
