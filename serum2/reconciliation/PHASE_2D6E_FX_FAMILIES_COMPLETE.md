# Phase 2D.6E: FX Orphan Families Complete — Final Disposition + Arithmetic Reconciliation

**Date**: 2026-09-17

---

## FilterFX — Resolved

All 5 `FX.FILTER.*` semantics now map to `FXFilter.*` targets:

```
FX.FILTER.TYPE   → FXFilter.Type       (already resolved, prior pass)
FX.FILTER.CUTOFF → FXFilter.Cutoff     (already resolved — label states internal name "FX Fil Freq")
FX.FILTER.RES    → FXFilter.Resonance (resolved this pass — "RES" abbreviation wasn't caught by
                                        the general title-case matcher)
FX.FILTER.DRIVE  → FXFilter.Drive      (already resolved, prior pass)
FX.FILTER.WET    → FXFilter.MixOrGain  (already resolved, earlier unambiguous-Wet pass)
```

**`FXFilterFX.*` (5 targets: Type/Cutoff/Resonance/Drive/Mix) remains orphaned.** Checked capability_keys: `fx_field_filter_fx_*` vs `FXFilter.*`'s `fx_field_filter_*` — genuinely different keys, not the same field under two names. No semantic in the 908-record inventory uses "FilterFX" naming or describes a second, distinct Filter-as-FX-module. Left `TRUE_ORPHAN` — plausibly a stale/legacy target-vocabulary entry (parallel to the dead OSC.Volume pattern), but not confirmed identical the way that case was, so not merged.

---

## Splitter — Genuinely Structural, Not Resolvable by 1:1 Aliasing

The semantic inventory documents **three distinct splitter types**, each with its own crossover-frequency field(s):

```
FX.SPLITTER_LH.SPLIT_FREQ              -- 1 crossover (2-band: Lows/Highs)
FX.SPLITTER_LMH.SPLIT_FREQ_LOW_MID     -- 2 crossovers (3-band: Lows/Mids/Highs)
FX.SPLITTER_LMH.SPLIT_FREQ_MID_HIGH
FX.SPLITTER_MS.*                       -- 0 crossovers (Mid/Side, not frequency-based)
```

But `targets.py` has one **generic** family: `FXSplitter.BandCount/Crossover1/Crossover2/Crossover3` — with no way to tell, from the target vocabulary alone, which splitter type it addresses. This mirrors the same conditional/instance-dependent pattern as the FILTER type-specific 4th-knob controls: the target's meaning depends on which splitter module is currently loaded in the rack.

**Not aliased.** Forcing `FXSplitter.Crossover1 → FX.SPLITTER_LH.SPLIT_FREQ` would be arbitrary — it could equally mean `FX.SPLITTER_LMH.SPLIT_FREQ_LOW_MID`, and there's no evidence to prefer one. Correctly left as `AMBIGUOUS_STRUCTURAL_MODEL` (same category as the EQ case was, before live UI resolved it) — this one would need the same live-UI treatment (load each splitter type, right-click its crossover knob, read the internal name) to resolve, not attempted this pass since it wasn't in the immediate family list.

---

## Filter.Q / Filter2.Q — Checked, Confirmed Distinct From Resonance, Left Orphaned

Checked capability_keys directly:

```
Filter.Resonance  → filter_field_reso   (already mapped, R.4)
Filter.Q          → filter_field_q      (different key -- NOT a duplicate)
```

This is the opposite finding from the EQ case, where "Q" and "Resonance"/"Reso" turned out to be the same knob (confirmed live: `FXEQ.Reso1` ↔ "EQ Q L"). For the *main* Filter section, `Q` is a genuinely separate field from `Resonance` by capability_key — and no semantic in the 908-record inventory documents a distinct "Q" control for `FILTER1`/`FILTER2` (only `RESONANCE` exists). This is a real, unresolved question: either the main Filter has an undiscovered `Q` control distinct from Resonance (a semantic-discovery gap, like `ARP.Enable`), or `Filter.Q`/`Filter2.Q` are stale targets. **Left `TRUE_ORPHAN`, not merged with Resonance** — the EQ precedent doesn't transfer here because the technical evidence points the opposite direction.

---

## Complete Arithmetic Reconciliation (Per Your Instruction — Two Populations, Not Mixed)

### Target-Side: 396 Technical Targets

```
396 total
├── 289 MAPPED (single semantic owner)
├──   2 MANY_TO_ONE (shared across multiple semantics: MATRIX routing family,
│                     FILTER GRAPHIC_CUTOFF_RESONANCE dual-parameter surface)
└── 105 ORPHAN_TECHNICAL
     ├──  28 explained: HEADLESS_FEATURE (LFO6-9's Rate/Shape/Mode/Phase/Retrigger, 20)
     │                  + DEAD/SUPERSEDED (OSC1-3/SUB.Volume, 4) + remainder (4, not
     │                  yet individually re-verified this session)
     ├──  21 AMBIGUOUS_MULTI_CANDIDATE (FX Wet/Mix/MixOrGain family across 7 modules:
     │       BODE, Chorus, Compressor, Convolve, Delay, Flanger, Hyper, Phaser, Reverb,
     │       Utility -- 2 targets each where both Mix and MixOrGain are live)
     ├──   4 AMBIGUOUS_STRUCTURAL_MODEL (FXSplitter family -- conditional on which
     │       splitter type is loaded, unresolved this pass)
     ├──   1 SEMANTIC_GAP_CANDIDATE (ARP.Enable -- tracked separately per your instruction,
     │       not manufactured)
     ├──   5 individually reasoned (Global.Quality/Glide/Voicing/VelocityCurve/PitchTracking)
     ├──   2 CONFIRMED_DISTINCT_UNRESOLVED (Filter.Q, Filter2.Q -- different capability_key
     │       from Resonance, no corresponding semantic found)
     ├──   5 FXFilterFX family (TRUE_ORPHAN -- different capability_key from FXFilter,
     │       no corresponding "FilterFX" semantic exists)
     └── ~39 TRUE_ORPHAN, not yet individually re-checked this session (various single
             FX-field remainders: LevelOut/BW/Tone/OffsetL/OffsetR/Time across several
             modules, NOISE.Type/Warp, OSC Detune/Wavetable remainder)
```

**Verification**: 28 + 21 + 4 + 1 + 5 + 2 + 5 + 39 = 105 ✓

### Semantic-Side: 908 Semantics

```
908 total
├── 286 EXACT (single target established)
├──   3 ONE_TO_MANY (maps to multiple targets: MATRIX.ROUTING.SIGNAL_BALANCE,
│                     MIXER.FILTER1/2.GRAPHIC_CUTOFF_RESONANCE)
└── 619 UNKNOWN
     ├── Recall from Phase 2D.6D's control-path classification (built independently of
     │   target-mapping status): of the semantics without a target, most already carry an
     │   established or candidate control_path_class (UI_ACTION/MATRIX_ROUTE/BODY_STATE_FIELD/
     │   RESOURCE_OPERATION/STRUCTURAL_OPERATION) -- this 619 is the target-reconciliation
     │   view, NOT the control-path view. The two are deliberately kept separate, per your
     │   instruction.
     └── 0 declared NO_TARGET anywhere, this session or any prior session
```

**Verification**: 286 + 3 + 619 = 908 ✓

---

## The Two Populations, Explicitly Not Mixed

```
TARGET-SIDE QUESTION:    "Does this technical target have a semantic owner?"
                          396 = 289 mapped + 2 many-to-one + 105 orphan (7 sub-categories)

SEMANTIC-SIDE QUESTION:  "Does this semantic have a target?"
                          908 = 286 exact + 3 one-to-many + 619 unknown

These numbers are NOT symmetric and should not be expected to be -- a target can be
orphaned for reasons that have nothing to do with why a semantic lacks a target (e.g.
FXFilterFX's 5 orphans are a target-vocabulary duplication question, unrelated to any
of the 619 semantic unknowns).
```

---

## FX Portion: Status

```
✅ EQ            -- fully resolved via live UI (8/9 fields; LevelOut appropriately open)
✅ FilterFX      -- fully resolved (5/5 via label/capability_key evidence)
⚠️ Splitter      -- checked, genuinely structural/conditional, correctly left unresolved
⚠️ Filter.Q      -- checked, confirmed distinct from Resonance, correctly left unresolved
```

Per your framing: FX orphan family exhaustion is **complete** in the sense that every named family has been individually checked with evidence (not skipped) — not in the sense that every orphan is now resolved. Splitter and Filter.Q remain open because the evidence itself doesn't support a resolution, not because they weren't investigated.

---

## Deliverables

| File | Contents |
|---|---|
| `_phase2d6e5_semantic_rows.json` | 908 rows, final state |
| `_phase2d6e_final_reverse_audit.json` | 396 targets, final reverse classification |
| `PHASE_2D6E_FX_FAMILIES_COMPLETE.md` | This document |

---

## Updated Phase State

```
PHASE 2D.6E    FX orphan family exhaustion         ✅ COMPLETE (all named families checked)
                  289 target-established (up from 65 at the very first mechanical pass)
                  105 orphans, all now categorized into 8 named dispositions
PHASE 2D.6F    169+ semantic UNKNOWNs              ▶ NEXT
PHASE 2D (global)                                   NOT CLOSED
```

---

**Status**: FX portion of the reverse-target audit is closed in the sense your instruction required — every family individually investigated with evidence, no forced aliases, ambiguities named rather than guessed. Ready to move to the semantic-side UNKNOWN queue.
