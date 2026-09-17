# Phase 2D.6I: Final Reconciliation of the 21 Unchecked Targets

**Date**: 2026-09-17
**Supersedes**: The "21/21 investigated" claim in `PHASE_2D6I_LIVE_UI_AUDIT_PROGRESS.md` is corrected here per review — several dispositions there were recorded as `(candidate)` when the project's own frozen semantic inventory already supplies confirming cross-reference evidence, and one (`FXReverb.Time`) was recorded as fully `DEAD_OR_SUPERSEDED` when the evidence only supports `DEAD_OR_SUPERSEDED_CANDIDATE` plus a separate, still-open semantic-side gap. This document is the authoritative disposition ledger for the 21.

**Scope note**: This audit does not rediscover the FX module universe. The frozen FX semantic baseline already documents 13 processors + 3 splitter modules as a closed set. What 2D.6I resolves is the *technical target ownership layer* underneath that already-frozen semantic universe — i.e., which `targets.py` entries correspond to real, live, VST3-addressable controls, and which are stale, ambiguous, or missing a technical counterpart entirely.

**Evidence types used**:
- `DIRECT_UI` — live-UI right-click, context-menu title read directly (`PHASE_2D6I_LIVE_UI_AUDIT_PROGRESS.md`)
- `CENSUS_NEGATIVE` — VST3 census search, zero matches, word-boundary-safe
- `SEMANTIC_INVENTORY_CROSS_REF` — cross-check against the frozen 908-record semantic inventory's own internal-name/label field, used only to *strengthen* a DIRECT_UI finding, never as a standalone source

---

## Final Disposition Table (21/21)

| # | Target | Disposition | Evidence | Notes |
|---|---|---|---|---|
| 1 | `FXBODE.Frequency` | `DEAD_OR_SUPERSEDED_CANDIDATE` | DIRECT_UI | No live control named "Frequency" among Bode's 11 controls. `SHIFT` ("Bode Shift") is conceptually adjacent but is a separately-owned existing target, not a free match. |
| 2 | `FXBODE.LevelOut` | **`DEAD_OR_SUPERSEDED`** | DIRECT_UI | Exhaustively checked, 7 (of 11 total) module controls enumerated; no output-level control exists. Strong. |
| 3 | `FXChorus.Phase` | **`DEAD_OR_SUPERSEDED`** | DIRECT_UI | No Phase control in Chorus's fixed 7-knob layout. Strong — consistent with the project's existing direct-UI negative for Flanger's would-be separate "Delay" control (`PROVEN_NOT_USER_CONTROL` discipline). |
| 4 | `FXConvolve.IR` | `DEAD_OR_SUPERSEDED` | DIRECT_UI | No context-menu-bearing scalar control on the waveform/resource strip; checked twice across separate sessions. |
| 5 | `FXConvolve.IRPath` | `DEAD_OR_SUPERSEDED` | DIRECT_UI | Same structural finding as #4. |
| 6 | `FXDelay.BW` | `DEAD_OR_SUPERSEDED_CANDIDATE` | DIRECT_UI | No BW knob in any of the 3 Delay modes (Normal/Ping-Pong/Tap→Delay); FREQ/Q are the delay's internal filter, not bandwidth. |
| 7 | `FXDelay.OffsetL` | `DEAD_OR_SUPERSEDED_CANDIDATE` | DIRECT_UI | No "Offset"-named control in any mode; `TimeL` is the real per-channel control but is a different name, not a literal match. |
| 8 | `FXDelay.OffsetR` | `DEAD_OR_SUPERSEDED_CANDIDATE` | DIRECT_UI | Same as #7, for `TimeR`. |
| 9 | `FXDelay.Time` | `DEAD_OR_SUPERSEDED_CANDIDATE` | DIRECT_UI | No singular/unsplit "Time" control in any mode — delay time is always split into `TimeL`/`TimeR`. |
| 10 | `FXDistortion.BW` | **`DEAD_OR_SUPERSEDED`** | DIRECT_UI | Confirmed absent across 5 distortion types (TUBE, SOFTCLIP, one further type, DIODE2, ZERO-SQUARE) — fixed 4-knob architecture (FREQ/Q/DRIVE/MIX) regardless of type. |
| 11 | `FXDistortion.LevelOut` | **`DEAD_OR_SUPERSEDED`** | DIRECT_UI | Same 5-type check as #10. |
| 12 | `FXDistortion.Tone` | **`DEAD_OR_SUPERSEDED`** | DIRECT_UI | Same 5-type check as #10. |
| 13 | `FXEQ.LevelOut` | **`DEAD_OR_SUPERSEDED`** | DIRECT_UI + SEMANTIC_INVENTORY_CROSS_REF | Exhaustive 6-knob layout confirmed in two view states (compact + expanded/solo); agrees with the frozen FX semantic baseline, which describes Equalizer with no separate Level control. Strong. |
| 14 | `FXReverb.Damping` | **`MAPPED_TO_EXISTING_SEMANTIC`** | DIRECT_UI + SEMANTIC_INVENTORY_CROSS_REF | `FX.REVERB.DAMP_PLATE` (label: "Damp", Plate type only) ↔ `FXReverb.Damping`. DIRECT_UI observed `FX 1: Rev Damp` on the Plate type; the semantic inventory's own label field for `DAMP_PLATE` already records this internal name. No longer a candidate — this is a closed cross-system resolution. |
| 15 | `FXReverb.Time` | `DEAD_OR_SUPERSEDED_CANDIDATE` | DIRECT_UI | The live control on the Hall type is `FX 1: Rev Decay`, not "Time" — checked across Plate/Hall/Vintage (3 of the semantic universe's 5 reverb types). "This target looks stale" is *not* the same claim as "the semantic control has been technically mapped." The semantic-side counterpart, `FX.REVERB.DECAY_HALL` ("Decay," Hall and Vintage types), remains separately unresolved — see Semantic-Gap Carryforward below. This target's stale-candidate status does not close that gap. |
| 16 | `FXUtility.Gain` | **`DEAD_OR_SUPERSEDED`** | DIRECT_UI | Exhaustively checked against Utility's full 8-control layout (L/R Polarity Inv, LPF, HPF, Mono Side, Freq, Width, Pan, Mix) — no separate Gain control. Strong. |
| 17 | `FXUtility.Mono` | **`MAPPED_TO_EXISTING_SEMANTIC`** | DIRECT_UI + SEMANTIC_INVENTORY_CROSS_REF | `FX.UTILITY.MONO_BASS` already records internal name `Utils Mono Side` in the frozen semantic inventory; DIRECT_UI this session independently observed the identical string. No longer a candidate. |
| 18 | `FXUtility.Phase` | **`DEAD_OR_SUPERSEDED`** | DIRECT_UI | No separate Phase control exists. Condition preserved: the existing L/R Polarity-Invert checkboxes stay mapped to their own `POLARITY_INV_L`/`POLARITY_INV_R` semantics and are **not** relabeled or reassigned as "Phase." Strong, conditional on that separation holding. |
| 19 | `OSC2.Detune` | `DEAD_OR_SUPERSEDED` / checked-negative | CENSUS_NEGATIVE | "B Detune" — zero matches, word-boundary-safe regex against all 2623 VST3 parameter names. |
| 20 | `OSC3.Detune` | `DEAD_OR_SUPERSEDED` / checked-negative | CENSUS_NEGATIVE | "C Detune" — zero matches after correcting a naive-substring false positive (`os[c detune]` inside "Osc Detune Rnd"); word-boundary regex confirms genuinely zero. |
| 21 | `SUB.Detune` | `DEAD_OR_SUPERSEDED` / checked-negative | CENSUS_NEGATIVE | "Sub Detune" — zero matches. |

**21/21 investigated. 21/21 have a named, evidence-backed disposition.** 2 are `MAPPED_TO_EXISTING_SEMANTIC` (final, not candidate). 12 are `DEAD_OR_SUPERSEDED` (strong/final). 7 are `DEAD_OR_SUPERSEDED_CANDIDATE` (evidence points one direction but a residual naming gap or a separate semantic-side question remains open — see below).

---

## Carried-Forward Consequences (not closures — flagged explicitly, not absorbed)

These are new graph facts this session produced *in addition to* the 21-item closures above. None of them are being silently folded into a target's disposition.

### 1. `FX.REVERB.DECAY_HALL` — new semantic-gap-candidate on the technical side
The semantic inventory already has `FX.REVERB.DECAY_HALL` (label "Decay," Hall and Vintage types) with no technical target of its own. `FXReverb.Time` being marked stale (`DEAD_OR_SUPERSEDED_CANDIDATE`, row 15) does **not** resolve this — it only removes one wrong candidate from consideration. `DECAY_HALL` remains open and should be tracked as a distinct item when the 152/gap-side work resumes.

### 2. The Wet/Mix target-alias family remains `AMBIGUOUS`
DIRECT_UI confirmed the internal host-parameter name ends in `Wet` for 9 modules (Chorus, Distortion, Utility, Reverb, Convolve, Hyper, Compressor, Flanger, Phaser) and is literally `Mix` for one (Dimension). This is strong structural evidence for how Serum names its mix knobs internally — it is **not** evidence for which of the competing `targets.py` aliases (`Mix` vs `MixOrGain`) is the authoritative technical-target name for each module. No new semantic called `Wet` is being created merely because Ableton's context menu uses that word. These remain `AMBIGUOUS` pending target-vocabulary ownership/history reconciliation, unchanged from the 2D.6H disposition.

### 3. Hyper/Dimension: distinct control identities inside one shared module
`Hyp Wet` (Hyper) and `Hyp im Mix` (Dimension) are two separately-addressable, differently-named controls inside what the host reports as a single internal module ID (`Hyp`). This strengthens — does not contradict — the existing frozen model of Hyper/Dimension as one module with two sections. Recorded as:
```
module = Hyp
section = Hyper | Dimension
control identity = distinct (Hyper: "...Wet", Dimension: "...Mix")
```
`FXDimension.Mix` is retained as a **candidate** match to an existing Dimension-side Mix semantic (not upgraded to final — no semantic-inventory label cross-reference was performed for it the way #14/#17 received one).

### 4. Flanger's UI-labeled "PHASE" knob is internally "Width" — a naming discovery, not a resolution
`FX 1: Flg Width` was observed at the UI position labeled "PHASE." No target in the current vocabulary is named `FXFlanger.Width`, so this does not resolve any of the 21 (it was investigated only because it sits adjacent to the Chorus.Phase question). Flagged for whoever next audits Flanger's own target-side entries — it is a real distinguishing fact, not an assumption.

### 5. Splitter crossover family (carried from the progress ledger, unchanged by this reconciliation)
`FXSplitter.Crossover1`/`Crossover2` remain `MAPPED_TO_EXISTING_SEMANTIC (candidate)` (DIRECT_UI: `Split Freq`, `Split3 Freq`, `Split3 Freq2` — no semantic-inventory label cross-reference performed, so not upgraded to final the way Damping/Mono were). `Crossover3` and `BandCount` remain `DEAD_OR_SUPERSEDED` (confirmed absent, no 3-crossover splitter type and no runtime band-count parameter exist in this build).

---

## What This Reconciliation Does and Does Not Authorize

```
21 UNCHECKED (start of 2D.6I)
        ↓
21 investigated (18 via DIRECT_UI, 3 via CENSUS_NEGATIVE)
        ↓
21 have a final, named disposition (this table)
        ↓
  2 MAPPED_TO_EXISTING_SEMANTIC (final)
 12 DEAD_OR_SUPERSEDED (final)
  7 DEAD_OR_SUPERSEDED_CANDIDATE (evidence-supported, naming gap noted, not force-closed)
        ↓
+ explicit non-closures carried forward:
  - FX.REVERB.DECAY_HALL: still a semantic-side gap, technical target still needed
  - Wet/Mix alias family: still AMBIGUOUS, no vocabulary winner declared
  - FXDimension.Mix: still a candidate, not final
  - FXFlanger "Width": new fact, no target exists for it yet
  - FXSplitter.Crossover1/2: still candidates, not final
```

**Not done in this pass, and not to be inferred from it:**
- The 98-orphan category subtotals in `PHASE_2D6H` (AMBIGUOUS=29, TECHNICAL_ONLY=24, etc.) have **not** been recomputed against these 21 final dispositions. The subtotals will shift (e.g., several DEAD_OR_SUPERSEDED items here were previously counted under UNCHECKED, not under the DEAD_OR_SUPERSEDED=4 bucket).
- The 152 semantic-unknown queue has **not** been touched, recomputed, or reduced. Per instruction, it stays untouched until the full 908↔target graph is rerun.
- Phase 2D.6J (four-table rebuild) and Phase 2D.6K (152 investigation) remain **not started**.

---

## Next Step

Rerun the complete 908 (semantic) ↔ 396 (target) bidirectional graph incorporating:
1. These 21 final dispositions (replacing their prior "unchecked" status in Table 2 of `PHASE_2D6H`)
2. The carried-forward consequences above as their own tracked items, not folded into any of the 21
3. No change yet to the 152 count — that number is recomputed only as an output of the graph rerun, not assumed in advance

That rerun is the authoritative starting population for Phase 2D.6J.
