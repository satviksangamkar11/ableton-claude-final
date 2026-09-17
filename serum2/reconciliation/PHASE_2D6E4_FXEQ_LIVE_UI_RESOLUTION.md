# Phase 2D.6E.4: FXEQ Family — Complete Live UI Resolution

**Date**: 2026-09-17  
**Method**: Direct live-UI verification in Ableton Live 12.3.2 + Serum 2. Equalizer FX module added to a live track; every knob and type-selector right-clicked to read its internal name from the context-menu title — the established gold-standard evidence method used throughout this entire reconciliation project.

---

## The Answer

Serum 2's Equalizer has two parametric bands. Internal naming is **L(ow)/H(igh) frequency band**, not Left/Right stereo channels and not a plain 1/2 index:

| Semantic (project naming) | Live UI internal name | Target resolved |
|---|---|---|
| `FX.EQUALIZER.LEFT_FREQ` | "EQ FreqL" | `FXEQ.Freq1` |
| `FX.EQUALIZER.RIGHT_FREQ` | "EQ FreqH" | `FXEQ.Freq2` |
| `FX.EQUALIZER.LEFT_Q` | "EQ Q L" | `FXEQ.Reso1` |
| `FX.EQUALIZER.RIGHT_Q` | "EQ Q H" | `FXEQ.Reso2` |
| `FX.EQUALIZER.LEFT_GAIN` | "EQ VolL" | `FXEQ.Gain1` |
| `FX.EQUALIZER.RIGHT_GAIN` | "EQ VolH" | `FXEQ.Gain2` |
| `FX.EQUALIZER.LEFT_TYPE` | "EQ TypeL" | `FXEQ.Type1` |
| `FX.EQUALIZER.RIGHT_TYPE` | "EQ TypeH" | `FXEQ.Type2` |

**8 of 9 FXEQ targets resolved.** `FXEQ.LevelOut` left unresolved — no separate Level knob was visible in the module during inspection, and I won't alias it to `FX.EQUALIZER.LEVEL` by label plausibility alone, per the same discipline that caught the earlier Wet/MixOrGain over-commitment.

---

## Correction to the Project's Own Semantic Labels

The semantic_ids themselves (`LEFT_FREQ`, `RIGHT_TYPE`, etc.) were named `LEFT`/`RIGHT` during original discovery — a reasonable inference from the bands' visual screen position. The live UI now shows the actual engine concept is **frequency-band assignment (Low/High)**, not stereo channel. The bands happen to be positioned left/right on screen, which is presumably why the original discovery pass called them that. This is now recorded as a naming-provenance note, not a renaming of the frozen semantic_ids themselves (out of scope for reconciliation to rewrite Phase 1 semantic IDs).

---

## Session Note

Ableton Live crashed once during this verification (auto-generated crash report: `Ableton Crash Report 2026-09-17 104032`), losing the in-progress module state. Recovered by reopening the app, reselecting the Serum 2 track, and re-adding the Equalizer module fresh. All 8 resolutions in this document were captured after recovery, on a freshly re-verified module — not carried over from the pre-crash session.

---

## Result

```
Before this session: 282 target-established (post FreqL/FreqH resolution)
This session:         +6 (Reso1/2, Gain1/2, Type1/2)
────
Population A:        288
```

The FXEQ `AMBIGUOUS_STRUCTURAL_MODEL` flag (open since Phase 2D.2) is now closed — not by inference, by direct observation.

---

## Deliverables

| File | Contents |
|---|---|
| `_phase2d6e3_semantic_rows_FXEQ_complete.json` | 908 rows, FXEQ family fully resolved |
| `PHASE_2D6E4_FXEQ_LIVE_UI_RESOLUTION.md` | This document |

---

## Updated Phase State

```
PHASE 2D.6E.1-4  FX orphan resolution        🟡 ADVANCED
                   288/908 semantics target-established
                   FXEQ family: 8/9 resolved via live UI (1 unconfirmed, correctly left open)
                   Remaining orphan families: FilterFX, Splitter, Filter.Q not yet checked

PHASE 2D.6F      169 semantic UNKNOWNs        🚫 NOT STARTED
PHASE 2D (global)                              NOT CLOSED
```

---

**Status**: The EQ structural-model question — open since 2D.2, explicitly flagged rather than guessed at every subsequent pass — is now resolved with direct evidence. This is the pattern the whole reconciliation has followed: when evidence is insufficient, wait and flag; when evidence becomes available (documentation, census, or live UI), verify and resolve; never fill the gap with a plausible guess in between.
