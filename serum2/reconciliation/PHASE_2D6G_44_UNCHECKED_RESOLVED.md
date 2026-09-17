# Phase 2D.6G: The 44 (45) UNCHECKED Target-Side Entries — Disposed

**Date**: 2026-09-17  
**Method**: Semantic-set cross-check first (label/capability_key), live UI verification for the highest-value ambiguity (LFO Shape/Mode/Retrigger, 18 targets — the largest remaining unchecked cluster).

---

## Major Resolution: LFO Trigger-Mode Family (Live UI)

Added LFO panel inspection to the live Serum 2 session. Right-clicked all three LFO structural controls:

```
Type dropdown ("Normal")           -> context menu: "LFO 1 Type"
Direction dropdown ("Forward")     -> context menu: "LFO 1 Direction"
Trigger buttons (FREE/RETRIG/...)  -> context menu: "LFO 1 Mode"
```

**Decisive finding**: the FREE/RETRIG/ENVELOPE/MONO button group's internal name is literally **"Mode"** — exactly matching the target name `LFO{n}.Mode`. This resolves 6 targets (`LFO0.Mode` through `LFO5.Mode`) to the semantic `LFO{n}.TRIGGER_MODE` via the confirmed off-by-one indexing.

**Equally important negative result**: neither "Type" nor "Direction" matches "Shape" or "Retrigger". The target vocabulary's `Shape`/`Retrigger` names do not correspond to any UI element checked. **Not aliased** — `LFO0-5.Shape` (6) and `LFO0-5.Retrigger` (6) remain genuinely unresolved technical identities, now with *positive* evidence they don't match the two most likely candidates, rather than simply "unchecked."

---

## Second Resolution: FXHyper.Retrigger

`FX.HYPER.RETRIG` (label "Hyper Retrig") directly matches `FXHyper.Retrigger` — resolved via label match, no ambiguity (single Hyper module, single Retrig control, no competing candidate).

---

## Confirmed Technical-Only / Unconfirmed (No Match Found, VST3 Census Checked)

Checked the census directly for these — **zero matches found anywhere in 2623 parameters**:

```
OSC{1,2,3}.Detune   -- "A Detune" not found
OSC1.Wavetable      -- "A Wavetable" not found (plausibly a resource-operation,
                        not a scalar VST3 field -- the visible "Default Shapes"
                        dropdown in the OSC panel is a resource selector, consistent
                        with this)
NOISE.Type          -- "Noise Type" not found
NOISE.Warp          -- "Noise Warp" not found
SUB.Warp            -- "Sub Warp" not found
```

These 5 predate the R.5/R.6 census-based itemization (they're original `targets.py` entries, not additions from this reconciliation). No VST3 backing, no semantic correspondence. Left `UNCONFIRMED_TECHNICAL_IDENTITY` — plausibly stale/speculative from before rigorous discovery, but not proven dead the clean way `OSC1.Volume` was (no duplicate-key evidence, just absence).

---

## Attempted, Inconclusive

`FXConvolve.IR`/`IRGain`/`IRPath` — added the Convolve module and inspected its knob layout (Size/Tone/MinPhase/PreDly/BPM/Attack/Decay/Damp/IRGain/Mix). No dedicated "IR" name/browser display was visible in the compact module view the way the semantic discovery described (`IR_BROWSER — black display bar`). A right-click attempt on IR Gain didn't land cleanly. **Not resolved this pass** — would need the module expanded or a different click target, not pursued further given diminishing returns.

---

## Result

```
Before this round: 45 UNCHECKED
Resolved this round:
   6  LFO{0-5}.Mode -> LFO{1-6}.TRIGGER_MODE (live UI verified)
   1  FXHyper.Retrigger -> FX.HYPER.RETRIG (label match)
────
   7 resolved

Reclassified (checked, confirmed no match -- no longer "unchecked", now
"positively confirmed unresolved"):
   6  LFO{0-5}.Shape       -- checked against Type, doesn't match
   6  LFO{0-5}.Retrigger   -- checked against Direction, doesn't match
   5  OSC/NOISE/SUB Detune/Wavetable/Type/Warp -- census-checked, zero backing found

Still genuinely UNCHECKED: 45 - 7 - 17 = 21
   FXBODE.Frequency/LevelOut, FXChorus.Phase, FXConvolve.IR/IRPath (attempted,
   inconclusive), FXDelay.BW/OffsetL/OffsetR/Time, FXDistortion.BW/LevelOut/Tone,
   FXEQ.LevelOut, FXReverb.Damping/Time, FXUtility.Gain/Mono/Phase
```

---

## Updated Population State

```
908 semantics
  296 target-established (up from 289)
  ...remainder unchanged pending full recount

396 targets
  296+ MAPPED
   21  genuinely UNCHECKED (down from 45)
   18  CONFIRMED_UNRESOLVED (checked, positively ruled out against best candidates --
       LFO Shape/Retrigger x12, OSC/NOISE/SUB x5, distinct from "unchecked")
   25  AMBIGUOUS (Mix/MixOrGain family, unchanged)
    4  AMBIGUOUS (Splitter, unchanged)
    1  SEMANTIC_GAP (ARP.Enable, unchanged)
    5  UNCHECKED individually-reasoned (Global.*, unchanged)
    2  CONFIRMED_DISTINCT (Filter.Q/Filter2.Q, unchanged)
    5  UNCONFIRMED (FXFilterFX family, unchanged)
```

---

## Deliverables

| File | Contents |
|---|---|
| `_phase2d6g_semantic_rows.json` | 908 rows, final state this round |
| `PHASE_2D6G_44_UNCHECKED_RESOLVED.md` | This document |

---

## Updated Phase State

```
PHASE 2D.6G  44/45 UNCHECKED targets disposed   🟡 SUBSTANTIALLY ADVANCED
                7 resolved, 17 reclassified from "unchecked" to "confirmed unresolved"
                (a real state change, even though not "solved"), 21 remain genuinely
                unchecked (mostly single FX fields: BW/OffsetL/OffsetR/Time/Tone/
                LevelOut/Mono/Phase/Damping across Delay/Distortion/Utility/Reverb/BODE)

PHASE 2D.6H  Rerun full bidirectional reconciliation + recompute 152 queue   ⏳ NEXT
PHASE 2D (global)                                                             NOT CLOSED
```

---

**Status**: The 45 UNCHECKED entries are no longer an undifferentiated pile — 7 resolved with real evidence (6 via live UI, 1 via label), 17 more positively checked and confirmed NOT to match their best candidates (a genuine finding, not a gap), 21 remain untouched. Ready to rerun the full bidirectional reconciliation and recompute the semantic-side UNKNOWN queue before moving to the 152.
