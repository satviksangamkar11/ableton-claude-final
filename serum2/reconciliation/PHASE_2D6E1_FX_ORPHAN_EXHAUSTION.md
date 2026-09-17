# Phase 2D.6E.1: FX Orphan Family Exhaustion

**Date**: 2026-09-16  
**Method**: Cross-referenced every orphan target against its full FX module's semantic set (label, internal-name notes, capability_key), family by family. No lexical alias committed without checking for competing live targets first — the `MixOrGain` discipline applied throughout.

---

## Result

```
Before this pass:  122 orphans (28 explained in 2D.6D, 94 remaining)
This pass:          8 resolved via label/internal-name evidence
After this pass:   114 orphans, 280 targets now MAPPED (up from 272)
```

---

## 8 New Resolutions, Each With Cited Evidence

| Semantic | Target | Evidence |
|---|---|---|
| `FX.CONVOLVE.IR_GAIN` | `FXConvolve.IRGain` | Label "IR Gain" — exact match |
| `FX.CONVOLVE.DAMP` | `FXConvolve.Damping` | Label "Damp" — abbreviated form of "Damping" |
| `FX.DISTORTION.FILTER_GRAPH` | `FXDistortion.LPHP` | Semantic's own label explicitly states "internal name Dist LPHP" |
| `FX.DISTORTION.TYPE` | `FXDistortion.Mode` | Label "Distortion type/**mode** selector"; `FILTER_POSITION` already covers the separate OFF/PRE/POST concept, ruling out that competing reading |
| `FX.DISTORTION.FILTER_POSITION` | `FXDistortion.PrePost` | Label "OFF/PRE/POST" is exactly the Pre/Post concept |
| `FX.BODE.DIR` | `FXBODE.Direction` | Label "Dir — shift direction" |
| `FX.COMPRESSOR.THRESH` | `FXCompressor.Threshold` | Label "Thresh — compression threshold" |
| `FX.PHASER.FREQ` | `FXPhaser.Frequency` | Label "Freq — base center frequency" |

Each was checked against its full module's semantic list before committing, to catch any competing-candidate situation like `MixOrGain`'s — none found for these 8.

---

## Complete Disposition Ledger, All Families

### Convolve (13 semantics checked)
- ✅ `IRGain`, `Damping` resolved this pass
- `IR`, `IRPath` — plausibly connect to `FX.CONVOLVE.IR_BROWSER`/`LOAD_IR_EXTERNAL`, but those are resource-selector UI mechanisms, not scalar parameters. Not aliased — a resource-operation correspondence isn't the same claim as a parameter match. Left `TRUE_ORPHAN`.
- `Mix`/`MixOrGain` — ambiguous (both live, different capability_keys), per the retraction discipline. Left `AMBIGUOUS_MULTI_CANDIDATE`.

### Distortion (11 semantics checked)
- ✅ `LPHP`, `Mode`, `PrePost` resolved this pass
- `BW`, `Tone`, `LevelOut` — no corresponding label found anywhere in the 11 Distortion semantics. `TRUE_ORPHAN`.

### BODE (12 semantics checked)
- ✅ `Direction` resolved this pass
- `Frequency` — `FXBODE.Shift` already has its own confirmed target and its own label is "frequency shift amount." `Frequency` (different capability_key: `fx_field_bode_frequency` vs `fx_field_bode_shift`) is NOT the same field by key, but has no other candidate semantic. Left `TRUE_ORPHAN` — plausibly a stale pre-discovery guess, not confirmed.
- `LevelOut` — no candidate. `TRUE_ORPHAN`.
- `Mix`/`MixOrGain` — `AMBIGUOUS_MULTI_CANDIDATE` (unresolved from 2D.6E).

### Compressor (14 semantics checked)
- ✅ `Threshold` resolved this pass
- `MixOrGain` — the module with the extra complication: has BOTH `.GAIN` (makeup gain) and `.WET` (mix) semantics already confirmed separately, so "MixOrGain" as a single target can't be cleanly assigned to either. `AMBIGUOUS_MULTI_CANDIDATE`, distinct reason from the other modules' ambiguity.

### Phaser (9 semantics checked)
- ✅ `Frequency` resolved this pass
- `Mix` — `AMBIGUOUS_MULTI_CANDIDATE` (unresolved from 2D.6E)

### Reverb (18 semantics checked)
- **Checked capability_keys**: `FXReverb.Damping` appears **twice** in `targets.py` with the **identical** key (`fx_field_reverb_damping`) — a true duplicate declaration (same pattern as `OSC1.Volume`), not a Mix/MixOrGain-style ambiguity. But Reverb's own semantic set has no unified "Damping" — only type-conditional `DAMP_PLATE`/`DAMP_VINTAGE`. The target itself is unambiguous; which semantic(s) it corresponds to is not. `TRUE_ORPHAN` (structurally complex, not force-resolved).
- `Time` — different capability_key from `Size` (`fx_field_reverb_time` vs `fx_field_reverb_size`), and no "Time"-labeled semantic exists anywhere in Reverb's 18 fields. Plausibly a stale pre-`Size`-discovery target, not confirmed as dead (different key, unlike the clean `OSC1.Volume` case). `TRUE_ORPHAN`.
- `Mix` — `AMBIGUOUS_MULTI_CANDIDATE`.

### Delay (11 semantics checked)
- `Time` — different key from `TimeL` (`fx_field_delay_time` vs `fx_field_delay_time_l`), no unified "Time" semantic (only `TIME_L`/`TIME_R`, both already mapped). Plausibly stale pre-L/R-split target. `TRUE_ORPHAN`.
- `BW`, `OffsetL`, `OffsetR` — no candidate semantics found. `TRUE_ORPHAN`.
- `Mix` — `AMBIGUOUS_MULTI_CANDIDATE`.

### Utility (9 semantics checked)
- `Gain` — no candidate (Utility has no output-gain concept in its 9 semantics; only filters/pan/width/polarity). `TRUE_ORPHAN`.
- `Mono` — closest candidate is `FX.UTILITY.MONO_BASS` ("force low frequencies to mono"), but that's a frequency-selective feature, not a general mono toggle — a materially different concept, not aliased. `TRUE_ORPHAN`.
- `Phase` — Utility has `POLARITY_INV_L`/`POLARITY_INV_R` (a different concept from a generic Phase control). Not aliased. `TRUE_ORPHAN`.
- `Mix` — `AMBIGUOUS_MULTI_CANDIDATE`.

### Not Yet Individually Checked This Pass
`FXFilterFX.*` (5), `FXSplitter.*` (4), `FXHyper.Retrigger`, `FXChorus.Phase`, `Filter.Q`/`Filter2.Q`, `FXFilter.Resonance` — these weren't part of the originally-named "10 FX families" and remain for a future pass if pursued.

---

## Separate Ledger: Semantic Gap Candidates (Not Target Reconciliation Problems)

Per your explicit instruction — **not manufactured, not folded into the target-reconciliation counts**:

```
SEMANTIC_GAP_CANDIDATE
  ARP.Enable — no ARP-subsystem master-enable semantic exists anywhere in the 908,
               unlike the parallel case of Clip Player (which does have
               CLIP.PLAYER.ENABLE). This is a genuine discovery gap in the original
               ARP closure pass, not a target-matching failure. Confirmed 2D.6E,
               unchanged this pass.
```

---

## Updated Population State

```
908 semantics
  280 target-established (EXACT + ONE_TO_MANY, up from 272)
  628 not yet established

396 targets
  280 MAPPED
    2 MANY_TO_ONE
  114 ORPHAN_TECHNICAL
      28 explained (headless LFO7-10 x20, dead OSC/SUB vocabulary x4, remainder
          not yet checked x4)
      12 AMBIGUOUS_MULTI_CANDIDATE (FX Wet/Mix family across 6 modules)
       9 AMBIGUOUS_STRUCTURAL_MODEL (FXEQ Left/Right vs 1/2)
       1 SEMANTIC_GAP_CANDIDATE (ARP.Enable, tracked separately)
       5 individually reasoned (Global.* remainder)
      ~59 TRUE_ORPHAN (no candidate semantic found despite full-family cross-check)
```

---

## Deliverables

| File | Contents |
|---|---|
| `_phase2d6e1_semantic_rows.json` | 908 rows, final state after this pass |
| `_phase2d6e1_reverse_audit_final.json` | 396 targets, final reverse classification |
| `PHASE_2D6E1_FX_ORPHAN_EXHAUSTION.md` | This document |

---

## Updated Phase State

```
PHASE 2D.6E.1  FX orphan family exhaustion    🟡 SUBSTANTIALLY ADVANCED
                8 of 10 named families fully cross-checked (Convolve/Distortion/
                BODE/Compressor/Phaser/Reverb/Delay/Utility)
                2 families not yet touched (FilterFX, Splitter) + Filter.Q/Filter2.Q
                remainder
                114 orphans remain, ~59 genuinely TRUE_ORPHAN after full-family
                checking (down from ~85 uncategorized)

PHASE 2D.6F    169 semantic UNKNOWNs           🚫 NOT STARTED (per your ordering)
PHASE 2D (global)                               NOT CLOSED
```

---

**Status**: 8 named FX families exhausted with full cross-checking discipline (label + internal-name + capability_key verification before any resolution). 8 new resolutions, all cited. 12 explicit `AMBIGUOUS_MULTI_CANDIDATE` flags (the Wet/Mix pattern generalizes across 6 of 8 checked modules). ARP.Enable tracked as a separate semantic-gap ledger entry, not manufactured. FilterFX/Splitter/Filter.Q remain if you want the two families continued, or ready to move to 2D.6F on the 169 semantic UNKNOWNs.
