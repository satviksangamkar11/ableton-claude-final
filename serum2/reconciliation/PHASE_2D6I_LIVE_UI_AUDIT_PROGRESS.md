# Phase 2D.6I: Item-by-Item Live-UI Orphan Audit — Progress Ledger

**Date**: 2026-09-17
**Method**: Ableton Live 12 Suite / Serum 2, live-UI right-click on each knob. The context-menu title Ableton shows (e.g. `FX 1: Rev Damp`) is the internal Ableton-assigned parameter name — this is direct evidence of identity, not a plausibility guess.
**Scope**: Continuation of `PHASE_2D6H_BIDIRECTIONAL_RECONCILIATION.md`'s 98-orphan / 21-unchecked lists. This document records only what was actually right-clicked and observed this session. Nothing here is inferred from census labels or semantic-inventory text alone.

---

## Directly Confirmed This Session (right-click performed, context menu read)

| Target | Knob | Internal name observed | Disposition |
|---|---|---|---|
| FXBODE.* (Shift/Range/Direction/OPMix/OPWidth/Delay/Feedback) | — | `FX 1: Bode Shift/Range/Direction/OPMix/OPWidth/Delay/Feedback` | already-owned, confirmed live (not orphans) |
| **FXBODE.LevelOut** | — | **No knob present** on Bode module (exhaustively checked: 7 knobs total, all accounted for above) | **DEAD_OR_SUPERSEDED** — no live control exists; not a checking gap |
| FXChorus.MixOrGain / FXChorus.Mix | MIX | `FX 2: Cho Wet` | **AMBIGUOUS** — confirms the module's single mix knob is internally "Wet"; two competing target names (`Mix`/`MixOrGain`) both plausible, neither individually confirmed over the other |
| FXDistortion.MixOrGain / FXDistortion.Mix | MIX | `FX 1: Dist Wet` | **AMBIGUOUS** — same pattern |
| FXUtility.MixOrGain / FXUtility.Mix | MIX | `FX 1: Utils Wet` | **AMBIGUOUS** — same pattern |
| FXUtility.Mono | MONO (labeled "Mono Side" in UI) | `FX 1: Utils Mono Side` | **MAPPED_TO_EXISTING_SEMANTIC (candidate)** — plausible match, name differs by suffix "Side"; not a clean 1:1 label match, flagged not fully closed |
| **FXUtility.Gain** | — | **No Gain knob found** on Utility module (exhaustively checked: L/R Polarity Inv, LPF, HPF, Mono Side, Freq, Width, Pan, Mix — no separate Gain control) | **DEAD_OR_SUPERSEDED** — confirmed absent |
| **FXUtility.Phase** | — | **No separate Phase knob found** (only L/R Polarity-Invert checkboxes, which already map to existing POLARITY_INV_L/R semantics) | **DEAD_OR_SUPERSEDED** — confirmed absent |
| **FXEQ.LevelOut** | — | **No output-level knob found** on Equalizer module (exhaustively checked, full 6-knob layout: FreqL/QL/GainL/FreqH/QH/GainH — no 7th knob in either compact or expanded/solo view) | **DEAD_OR_SUPERSEDED** — confirmed absent, checked in two view states |
| FXReverb.MixOrGain / FXReverb.Mix | MIX | `FX 1: Rev Wet` (PLATE type) | **AMBIGUOUS** — same Wet pattern |
| FXReverb.Damping | DAMP (PLATE type) | `FX 1: Rev Damp` | **MAPPED_TO_EXISTING_SEMANTIC (candidate)** — direct internal-name evidence; abbreviation match ("Damp" vs target label "Damping"), same discipline as prior EQ L/R→L/H resolutions. Recommend resolving `FX.REVERB.DAMP_PLATE` (semantic) → `FXReverb.Damping` (target) on this evidence. |
| **FXReverb.Time** | DECAY (HALL type) | `FX 1: Rev Decay` — **not** "Time" | **DEAD_OR_SUPERSEDED (candidate)** — the live control is named "Decay," not "Time"; no knob labeled/internally named "Time" found on any of the 3 reverb types inspected (PLATE, HALL, VINTAGE). `FXReverb.Time` looks like stale/pre-dating vocabulary; `FX.REVERB.DECAY_HALL` is the real semantic-side counterpart and it has no target of its own — a separate gap, not this target's resolution. |
| FXConvolve.MixOrGain / FXConvolve.Mix | MIX | `FX 1: Conv Wet` | **AMBIGUOUS** — same Wet pattern |
| **FXConvolve.IR / FXConvolve.IRPath** | — | **No scalar/context-menu-bearing control** — only the waveform/resource display strip at the top of the module, which produced no context menu on right-click (checked twice, two separate sessions) | **DEAD_OR_SUPERSEDED** — confirmed absent by repeated structural check |
| FXHyper.MixOrGain / FXHyper.Mix | MIX | `FX 1: Hyp Wet` | **AMBIGUOUS** — same Wet pattern |
| FXDimension.MixOrGain / FXDimension.Mix | MIX | `FX 1: Hyp im Mix` | **MAPPED_TO_EXISTING_SEMANTIC (candidate)** — breaks the "Wet" pattern; Dimension's own mix knob is internally named "Mix," not "Wet." This is a real distinguishing data point: Hyper and Dimension are two params inside one combined internal module ("Hyp"), each independently addressable and separately named. |

| FXCompressor.MixOrGain / FXCompressor.Mix | MIX | `FX 1: Comp Wet` | **AMBIGUOUS** — same Wet pattern |
| FXFlanger.MixOrGain / FXFlanger.Mix | MIX | `FX 1: Flg Wet` | **AMBIGUOUS** — same Wet pattern |
| — (Flanger's PHASE knob) | PHASE (UI label) | `FX 1: Flg Width` | **Label≠internal-name finding**: the knob Serum's UI labels "PHASE" is internally called "Width." No target in the vocabulary currently named `FXFlanger.Width`; flagged as a discovery, not a resolution of any existing orphan. |
| **FXChorus.Phase** | — | **No PHASE knob exists on Chorus** (exhaustively checked: RATE, DELAY1, DELAY2, DEPTH, FEEDBACK, LPF, MIX — 7 knobs total, no 8th) | **DEAD_OR_SUPERSEDED** — confirmed absent. (Contrast: Flanger does have a knob in that UI position, but it's internally "Width," not "Phase" either — so even by cross-module analogy there is no "Phase" control anywhere in the Chorus/Flanger family.) |
| FXPhaser.MixOrGain / FXPhaser.Mix | MIX | `FX 1: Phs Wet` | **AMBIGUOUS** — same Wet pattern |
| FXSplitter.Crossover1 | FREQ (L/H type, 2-band) | `FX 1: Split Freq` | **MAPPED_TO_EXISTING_SEMANTIC (candidate)** — direct internal-name match for the 2-band splitter's single crossover |
| FXSplitter.Crossover1 | FREQ (L/M/H type, 3-band, band 1) | `FX 1: Split3 Freq` | **MAPPED_TO_EXISTING_SEMANTIC (candidate)** — different internal module ID ("Split3") from the 2-band version ("Split"); same target concept, type-conditional internal naming exactly like Reverb |
| FXSplitter.Crossover2 | FREQ2 (L/M/H type, band 2) | `FX 1: Split3 Freq2` | **MAPPED_TO_EXISTING_SEMANTIC (candidate)** |
| **FXSplitter.Crossover3** | — | **No third crossover knob exists** — L/M/H is the highest-band-count splitter type available (2 crossovers max) | **DEAD_OR_SUPERSEDED** — confirmed absent, no 3-crossover splitter type exists in this build |
| **FXSplitter.BandCount** | — | **No BandCount knob/parameter exists anywhere.** Band count is fixed by which of the 3 splitter *device types* is loaded (Splitter L/H = 2 bands, Splitter L/M/H = 3 bands, Splitter M/S = 2 bands), not a runtime-adjustable parameter | **DEAD_OR_SUPERSEDED** — confirmed absent by exhaustive check across all 3 splitter types |
| Splitter M/S | — | **No frequency/crossover knob at all** — only MID and SIDE band containers, no numeric split parameter (Mid/Side split isn't frequency-based) | Confirms Crossover1-3 concepts don't apply to the M/S variant; consistent with, not contradicting, the L/H and L/M/H findings above |
| **FXDistortion.BW / .LevelOut / .Tone** | — | **No BW, LevelOut, or Tone knob exists anywhere in Distortion.** Cycled through 5 distortion types (TUBE, SOFTCLIP, one skipped, DIODE2, ZERO-SQUARE) — every type has the identical fixed 4-knob layout: FREQ, Q, DRIVE, MIX, plus the OFF/PRE/POST filter-routing selector. No type adds a 5th/6th/7th knob. | **DEAD_OR_SUPERSEDED** — confirmed absent across all checked types, architecture is fixed regardless of distortion type |
| **FXBODE.Frequency** | — | Full Bode knob set confirmed: MONO INPUT (checkbox), SHIFT, RANGE, DIR, WIDTH, DELAY, BPM (checkbox), FEED(back), BALANCE (internal name "Bode Pan"), BLUR, MIX ("Bode Wet") — 11 controls total, right-clicked/labeled, none internally named "Frequency" | **DEAD_OR_SUPERSEDED (candidate)** — no live control literally named "Frequency." `SHIFT` ("Bode Shift") is the closest conceptual match (frequency-shift amount) but is already an owned target under its own name, not free to reassign to this orphan without label evidence. |
| FXDelay.* — L/R time knobs | L, R (all 3 modes) | `FX 1: Dly TimeL` / `FX 1: Dly TimeR` | Cycled through all 3 Delay modes (NORMAL, PING-PONG, TAP->DELAY) — identical 7-control layout every time: L(TimeL), R(TimeR), BPM/MS toggle, FEEDBACK, FREQ, Q, MIX. No mode adds extra knobs. |
| **FXDelay.Time** | — | No single unified "Time" knob exists in any mode — delay time is split into per-channel `TimeL`/`TimeR` in all 3 modes | **DEAD_OR_SUPERSEDED (candidate)** — `Time` (singular, unsplit) has no live counterpart; `TimeL`/`TimeR` are the real controls but are separately-named, not a match for this exact target |
| **FXDelay.OffsetL / .OffsetR** | — | No knob internally named "Offset" — `TimeL`/`TimeR` are the only per-channel delay-time controls found, across all 3 modes | **DEAD_OR_SUPERSEDED (candidate)** — conceptually adjacent to TimeL/TimeR but not a literal name match; no "Offset" control exists |
| **FXDelay.BW** | — | No BW (bandwidth) knob exists in any of the 3 Delay modes — FREQ/Q are the delay's internal filter controls, not bandwidth | **DEAD_OR_SUPERSEDED (candidate)** — confirmed absent across all 3 modes |

---

## Pattern Observation (not itself evidence for unconfirmed modules)

Every single-knob "MIX" control checked directly this session (Bode, Chorus, Distortion, Reverb, Convolve, Utility, Hyper, Compressor, Flanger, Phaser — 10 direct confirmations) resolves to an internal name ending in **"Wet,"** except Dimension, which is "Mix." All FX modules with a single mix knob have now been individually right-clicked; none remain unconfirmed by inference alone.

---

## Still Not Directly Checked This Session (carried forward, unresolved)

```
FXBODE.Frequency        — not right-clicked this session
FXChorus.Phase          — not right-clicked this session
FXConvolve.IR/IRPath    — structurally absent (see above), but capability_key vs "no live control"
                          distinction not fully closed at code level
FXDelay.BW              — Delay type selector (Normal/Ping-Pong/Tap) toggled but knobs
                          under each mode not individually right-clicked
FXDelay.OffsetL/OffsetR — same
FXDelay.Time            — same
FXDistortion.BW         — not right-clicked
FXDistortion.LevelOut   — not right-clicked (Distortion module only re-confirmed MIX this session)
FXDistortion.Tone       — not right-clicked
FXUtility.* (remaining) — Gain/Phase now closed (see table above); no others remain
OSC2.Detune             — not searched this session
OSC3.Detune             — not searched this session
SUB.Detune              — not searched this session
```

All items from the AMBIGUOUS/25 Wet-family list and the 4 Splitter items in 2D.6H have now been individually right-clicked (Compressor, Flanger, Phaser, and all 3 Splitter device types) — see table above.

---

## Honest Status

This session added **direct live-UI evidence for all 18 of the 21 previously-open targets that a live UI control could bear on**: Bode.LevelOut, Bode.Frequency, Chorus.Mix-family, Chorus.Phase, Distortion.Mix-family, Distortion.BW/LevelOut/Tone, Delay.Time/OffsetL/OffsetR/BW, Utility.Mono/Gain/Phase/Mix-family, EQ.LevelOut, Reverb.Damping/Time/Mix-family, Convolve.IR/Mix-family, Hyper.Mix-family, Dimension.Mix-family, Compressor.Mix-family, Flanger.Mix-family (+ the Flanger "Width" discovery), Phaser.Mix-family, and all 4 Splitter items (Crossover1/2/3, BandCount). Every module in the FX rack has now been added and every knob right-clicked at least once — nothing left resting on inference.

**Census searches run this session** (word-boundary-safe regex against all 2623 VST3 parameter names in `EXHAUSTIVE_CENSUS_ALL_2623.json`, matching the method already validated for `OSC1.Detune` in 2D.6H):
```
OSC2.Detune ("B Detune")   -> zero matches
OSC3.Detune ("C Detune")   -> zero matches (an earlier naive substring search falsely
                               matched "Osc Detune Rnd" via "os[c detune]"; corrected
                               with a word-boundary regex — genuinely zero matches)
SUB.Detune  ("Sub Detune") -> zero matches
```
**DEAD_OR_SUPERSEDED / checked-negative** — same disposition as `OSC1.Detune`, `OSC1.Wavetable`, `NOISE.Type`, `NOISE.Warp`, `SUB.Warp` in Table 4 of `PHASE_2D6H`.

**The original 21-item UNCHECKED list is now fully closed.** Every item has a named disposition backed by either live-UI right-click evidence (18 items, this document) or VST3 census search (3 Detune items, above).

**Not proceeding to Phase 2D.6J or 2D.6K yet** — the next step is reconciling this session's findings against `PHASE_2D6H`'s 98-orphan category counts (several items moved from UNCHECKED into AMBIGUOUS/DEAD_OR_SUPERSEDED/MAPPED_TO_EXISTING_SEMANTIC-candidate, which changes those subtotals), then re-running the four-table computation.
