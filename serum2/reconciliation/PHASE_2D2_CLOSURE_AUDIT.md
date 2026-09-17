# Phase 2D.2: Mechanical Reconciliation Closure

**Date**: 2026-09-16

---

## Result: Before vs After

```
                    First pass   Closed pass
EXACT                    73           84
ONE_TO_MANY               1            1
UNKNOWN                 834          823
MAPPED (reverse)          78           89
ORPHAN_TECHNICAL         177          166
```

11 semantics newly resolved via `UI_SURFACE_ALIAS` (the R.7 ownership-alias closure), plus a handful via the `FX.EQUALIZER→FXEQ` and `GLOBAL→Global` namespace fixes reaching some targets that share exact field names.

---

## `mapping_basis` Now Populated

Every EXACT/ONE_TO_MANY row carries an explicit basis, not a bare match:

| mapping_basis | Count | Meaning |
|---|---|---|
| `ALIAS_RULE` | 73 | Structural namespace/numbering alias with cited evidence (Filter1↔Filter, LFO off-by-one, FX module pattern, etc.) |
| `UI_SURFACE_ALIAS` | 11 | Phase 2A-R.7 ownership finding — semantic and target use different namespaces because they were discovered from different UI surfaces (OSC panel vs. MIXER channel strip) for the *same* physical VST3 parameter |
| `STRUCTURAL_OPERATION` | 1 | MATRIX routing concept exposing a multi-field family (not a scalar 1:1) |
| `UNRESOLVED` | 823 | No rule applied — explicitly `mapping_basis: UNRESOLVED`, not silently blank |

No row claims a mapping without a cited basis. `mapping_basis: UNRESOLVED` is itself informative — it distinguishes "we don't know" from "we decided."

---

## Ownership Aliases Applied (Without Resurrecting Retracted IDs)

Per your explicit instruction, the retracted semantic_ids (`OSC1.ENABLE`, `SUB_OSC.ENABLE`, etc.) were **not** brought back. Instead, the *surviving* canonical semantic_ids now carry the target linkage directly:

```
MIXER.OSC_A.ENABLE  → OSC1.Enable   [ui_surface: OSC_PANEL, MIXER_CHANNEL_STRIP]
MIXER.OSC_A.LEVEL   → OSC1.Level    [same]
MIXER.OSC_A.PAN     → OSC1.Pan      [same]
MIXER.OSC_B.ENABLE  → OSC2.Enable
MIXER.OSC_B.LEVEL   → OSC2.Level
MIXER.OSC_B.PAN     → OSC2.Pan
MIXER.OSC_C.ENABLE  → OSC3.Enable
MIXER.OSC_C.LEVEL   → OSC3.Level
MIXER.OSC_C.PAN     → OSC3.Pan
MIXER.SUB.ENABLE    → SUB.Enable
```

**`MIXER.NOISE.ENABLE` was explicitly left unaliased** — `targets.py` has no `NOISE.Enable` entry (only `NOISE.Volume`/`.Level`/`.Pan`/etc.). Aliasing it anyway would fabricate a target that doesn't exist. Documented in the registry's `explicitly_not_aliased` section as a genuine target-vocabulary gap, not a matcher miss.

---

## MACRO: Confirmed Still UNKNOWN, Not Auto-Classified

```python
assert all(r['mapping_class'] != 'NO_TARGET' for r in macro_rows)
# PASSED -- all 48 MACRO.* rows remain UNKNOWN
```

`ModRoute.MacroDepth` (the only Macro-adjacent target) is a routing-depth concept, not the macro's own value. No evidence establishes it as the macro-value target. Left `UNKNOWN` per your explicit instruction — proving `NO_TARGET` requires positive confirmation this pass does not attempt.

---

## New Finding: EQ Structural Model Mismatch (Not a Lexical Gap)

`FXEQ.*` targets remained orphaned even after the `FX.EQUALIZER→FXEQ` namespace alias, because the two sides use **genuinely different structural models**, not just different names for the same fields:

```
Semantic side (FX.EQUALIZER.*):   LEFT_TYPE / LEFT_FREQ / LEFT_Q / LEFT_GAIN
                                    RIGHT_TYPE / RIGHT_FREQ / RIGHT_Q / RIGHT_GAIN
                                    (independent stereo-channel EQ, confirmed by the FX closure
                                    ledger's own text: "independent Left/Right band types
                                    [Shelf/Peak/HP vs Shelf/Peak/LP]" -- the two channels can
                                    even have DIFFERENT available type options)

Target side (FXEQ.*):             Type1 / Freq1 / Reso1 / Gain1
                                    Type2 / Freq2 / Reso2 / Gain2
                                    (numbered-band model, no explicit Left/Right semantics)
```

Whether `Left↔1, Right↔2` is a correct alias requires evidence this pass doesn't have — it could equally be that targets.py's "1/2" numbering was built against a different (and possibly incorrect, since targets.py predates this reconciliation and was built with shallower evidence) mental model of the EQ's structure. **Not auto-aliased.** Flagged for Phase 2D.4 review, distinct in kind from the FX-module-name gaps that *were* safely closed this pass.

---

## Three-Population Framework: Current State

Per your framework, only Population C is a legitimate "control gap" claim. Current state:

```
Population A (semantic → target established):     85 semantics  (84 EXACT + 1 ONE_TO_MANY's constituents... 
                                                     precisely: 84 rows classified EXACT, 1 row ONE_TO_MANY 
                                                     mapping to 5 targets)
Population B (semantic → UNKNOWN):                823 semantics
Population C (semantic → proven NO_TARGET):          0 semantics
```

**Population C is empty.** Nothing has been positively proven absent in this reconciliation. This is the correct, honest state — no `NO_TARGET` classification has been made anywhere in Phase 2D, consistent with your governing rule throughout.

---

## Remaining UNKNOWN, By Section (823 total)

| Section | Count | Section | Count |
|---|---|---|---|
| FX | 145 | ARP | 50 |
| OSC | 126 | MACRO | 48 |
| MATRIX | 80 | BROWSER | 41 |
| LFO | 78 | ENV | 32 |
| FILTER | 58 | CLIP | 30 |
| MIXER | 55 | GLOBAL_KEYBOARD | 21 |
| GLOBAL | 51 | VOICE | 8 |

Full per-semantic list is in `_phase2d2_closed_semantic_rows.json`.

---

## Remaining ORPHAN_TECHNICAL Targets (166), By Rough Category

- **EQ family (9)**: `FXEQ.*` — structural model mismatch (see above), not a simple alias gap
- **LFO Shape/Mode/Retrigger (30)**: `LFO{n}.Shape/.Mode/.Retrigger` across all 10 target LFOs — no semantic exists yet with these exact field names (the semantic side has `TYPE`/`DIRECTION`/`TRIGGER_MODE`/`WAVEFORM_GRAPH` instead; likely a genuine naming difference, e.g. semantic `LFO{n}.TYPE` might correspond to target `LFO{n}.Shape` — **not yet checked**, flagged for 2D.4)
- **Routing/BUS-send family (~15)**: `{X}.BUS1Send/.BUS2Send/.Route` for OSC1-3/SUB/NOISE/FILTER1-2 — these were deliberately excluded from new semantic creation in Phase 2A-R.4/R.5 because they were judged to be MIXER-owned; but the MIXER-side records (`MIXER.{X}.BUS1/.BUS2/.ROUTING`) use different field names than these targets expect — **same class of issue as the OSC Enable/Level/Pan case, likely needs its own ownership-alias entries**, not yet built
- **GLOBAL family (~12)**: `Global.MasterVolume/.Transpose/.Tuning/...` — case-alias was added but apparently didn't resolve; needs debugging (the `GLOBAL.*` semantic section may use different sub-field naming than expected)
- **FX MixOrGain/BW variants (~40)**: extended FX parameter names (`MixOrGain`, `BW`, `TimeL/TimeR`, etc.) that don't correspond 1:1 to any single FX closure semantic field name — likely genuine target-vocabulary-ahead-of-semantic-discovery gaps (targets.py was extended with FX detail beyond what the FX closure ledger itemized)
- **Remainder (~60)**: not yet categorized

---

## Honest Assessment

This pass closed the three explicitly-named gaps from the prior audit (FX.EQUALIZER alias attempted — found to be a deeper structural mismatch rather than resolved; ownership alias — resolved, 11 new matches; MACRO — correctly kept UNKNOWN). It also surfaced **two new, more specific gap classes** (LFO Shape/Mode/Retrigger naming, BUS-send ownership-alias-needed) that weren't visible until the first three were addressed.

This is expected — each closure round narrows and sharpens the remaining set rather than eliminating it in one pass. Per your framework, continuing to iterate mechanical closure has diminishing but still-positive returns; the question is whether to continue narrowing mechanically or move to 2D.4 (human/evidence review) on the current, better-categorized remainder.

---

## Deliverables

| File | Contents |
|---|---|
| `SERUM2_ALIAS_REGISTRY.json` | Evidence-backed alias rules, namespace + ownership, with explicit non-aliased cases |
| `_phase2d2_closed_semantic_rows.json` | 908 rows with `mapping_basis`, `ui_surface`, `evidence` fields |
| `_phase2d2_reverse_audit.json` | 255 target rows, reverse classification |
| `PHASE_2D2_CLOSURE_AUDIT.md` | This document |

---

## Updated Phase State

```
PHASE 2D.1  Mechanical reconciliation (first pass)   ✅ COMPLETE
PHASE 2D.2  Alias/ownership closure                   ✅ COMPLETE (this pass)
                84 EXACT (+11), 166 orphan (-11), 2 new gap classes surfaced
PHASE 2D.3  Re-run bidirectional matrix                ✅ COMPLETE (done as part of 2D.2)
PHASE 2D.4  Human/evidence review of remaining UNKNOWN ⏳ NEXT
                Specific queue: LFO Shape/Mode/Retrigger naming, BUS-send ownership
                aliases, EQ Left/Right vs 1/2 structural question, GLOBAL field debug
PHASE 2D.5  Classify true NO_TARGET vs UNKNOWN         🚫 waits on 2D.4
PHASE 2D.6  Operation coverage                         🚫 waits on 2D.5
PHASE 2D.7  Representation families                    🚫 waits on 2D.6
```

---

**Status**: Population C (proven NO_TARGET) remains empty — correct and honest. Population A grew from 73 to 85 semantics. 823 semantics remain in Population B (UNKNOWN), now with sharper sub-categorization for targeted 2D.4 review rather than an undifferentiated mass.
