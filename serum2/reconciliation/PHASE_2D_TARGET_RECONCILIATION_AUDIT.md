# Phase 2D: Target Reconciliation Audit (First Mechanical Pass)

**Date**: 2026-09-16  
**Status**: First-pass mechanical reconciliation complete. Documented as a starting point, not a finished bidirectional map.

---

## Result Summary

```
908 semantics x 255 targets

Semantic -> Target:
  EXACT          73
  ONE_TO_MANY      1
  UNKNOWN        834   (no mechanical alias rule produced a match)

Target -> Semantic (reverse audit):
  MAPPED          78
  ORPHAN_TECHNICAL 177  (no semantic mapped to this target via current rules)
```

Per your governing rule, **UNKNOWN, not NO_TARGET**, is used throughout for the 834 unmatched semantics — a mechanical-matcher miss is not evidence that no target exists. Declaring `NO_TARGET` would require positively establishing absence, which this pass does not do.

---

## Matching Method: Documented Aliases Only, Not Fuzzy Guessing

Every match traces to one of these explicit, evidence-based rules established during Phase 2A-R:

| Rule | Basis |
|---|---|
| `FILTER1.*` → `Filter.*` | Confirmed R.4: `Filter.*` is the implicit FILTER1 alias in targets.py |
| `FILTER2.*` → `Filter2.*` | Explicit numbered form |
| `ENV{n}.*` → `Env{n}.*` | Case-normalized, 1-based, direct |
| `LFO{n}.*` (semantic, UI-numbered) → `LFO{n-1}.*` (target, 0-based) | **Confirmed via live `bridge.capture_v8_skeleton`**: body-state has exactly `LFO0`-`LFO9` (10 objects = Serum's 10 UI LFOs), 0-based. The same-number candidate was tested, found to produce a false-positive `ONE_TO_MANY` on every LFO field, and explicitly suppressed with evidence, not just deprioritized. |
| `OSC{n}.*` → `OSC{n}.*` | Case-normalized, direct |
| `SUB_OSC.*` → `SUB.*`, `NOISE_OSC.*` → `NOISE.*` | Direct alias |
| `FX.{Module}.{Field}` → `FX{Module}.{Field}` | Pattern-based, case-insensitive fallback |
| `MATRIX.ROUTING.SIGNAL_BALANCE` → all `ModRoute.*` | Genuine one-to-many: one routing concept exposes multiple sub-fields (Curve/Bipolar/AuxSource/MacroDepth/Bypass) |

---

## Known Matcher Gaps (Not Yet Fixed — Documented, Not Hidden)

These are specific, identified reasons for false `UNKNOWN`/`ORPHAN_TECHNICAL` results, not a claim that no target/semantic exists:

1. **FX module abbreviations**: `FXEQ.*` (target) has no matching rule because the semantic side uses `FX.EQUALIZER.*` (full word), not `FX.EQ.*`. Same likely applies to other abbreviated FX module names. **7 targets** (`FXEQ.Freq1/Freq2/Reso1/Reso2/Gain1/Gain2/LevelOut`) affected by this alone.

2. **Retraction side-effect (Phase 2A-R.7)**: `SUB.Enable`, `OSC1.Enable`, and their Level/Pan siblings now show as orphaned because the candidate semantic records that would have matched them (`SUB_OSC.ENABLE`, `OSC1.ENABLE`, etc.) were correctly retracted as duplicates — but the canonical replacement records (`MIXER.SUB.ENABLE`, `MIXER.OSC_A.ENABLE`) use different naming and have no alias rule pointing at these targets yet. This needs an explicit `MIXER.{X}.ENABLE` → `{X}.Enable` alias rule to close the loop the R.7 resolution opened.

3. **MACRO has no direct value target**: confirmed in this session — targets.py contains only `ModRoute.MacroDepth` (a routing-depth concept, not the macro dial value itself) for the entire MACRO family. All 48 MACRO semantic records (`MACRO.0{n}.VALUE`, `.NAME`, etc.) are genuinely `UNKNOWN`/likely `NO_TARGET` candidates — but per the governing rule, this needs positive confirmation (e.g., checking whether `Global{n}.plainParams` or similar holds macro values) before downgrading to `NO_TARGET`. **Not confirmed here.**

4. **No fuzzy/semantic label matching attempted**: only structural ID-pattern aliases were used. Many `UNKNOWN` semantics likely correspond to targets whose names don't follow any of the 8 documented patterns above (e.g., `GLOBAL.*` semantics vs. `Global.*` targets — case-only, should be added; `ARP.*`/`CLIP.*` structural semantics almost certainly have zero targets, correctly, since these sections' operations were never implemented per the project's own prior notes).

---

## Reverse Audit: 177 Orphan Targets — Composition

Not a monolithic "gap" — breaks down into distinct categories:

| Category (approximate, by target_source) | Count | Likely explanation |
|---|---|---|
| FX_PARAMETER orphans | ~30-40 | FX naming-alias gaps (see #1 above) — likely mostly false orphans |
| SYNTH_PARAMETER orphans (SUB/OSC/NOISE Enable-family) | ~11 | Retraction side-effect (see #2 above) — false orphans, need alias fix |
| SYNTH_PARAMETER orphans (Global.*, Env.* remainder) | remainder | Mix of case-alias gaps and potentially genuine gaps |
| MATRIX_ROUTE | 0 | Fully mapped via the one-to-many rule |

*(Exact per-category breakdown requires the matcher fixes in items 1-2 above before it's meaningful — reported qualitatively here rather than with a possibly-wrong precise count.)*

---

## Operation Coverage: Explicitly Not Populated

Per the Phase 2C boundary (no persisted `CapabilityContract` store found in the repo), the following fields are `UNKNOWN` for all 908 rows in `SERUM2_TARGET_RECONCILIATION_MATRIX_FINAL.json`:

```
mutation_path, read_supported, write_supported, persistent, automatable
```

`causal_verified` is `NOT_RUN` for all rows. The **one exception** in the entire reconciliation effort is the live-tested `Clip Player Rate` field (Phase 2A-R.9b) — but that field is not part of `targets.py`'s `SEMANTIC_TARGETS`, so it doesn't appear as a row here. It stands as proof-of-method for what a genuine operation-coverage entry looks like once tested, not yet generalized.

**This is intentional, not an oversight.** Populating operation coverage for 908 rows individually would be exactly the "908 redundant experiments" anti-pattern you flagged. It waits for representation-family derivation.

---

## Representation Family: Deliberately Not Classified

Every row's `representation_family` field is literally `"NOT_YET_CLASSIFIED"`. No family count or taxonomy was predeclared. This is queued as the next step, but only makes sense to attempt on the **mapped** subset (73 EXACT + resolved matcher-gap fixes), not the 834 `UNKNOWN` rows, which don't yet have a target to derive a mechanism from.

---

## Honest State of This Deliverable

This is a **first mechanical pass**, not a finished reconciliation:

✅ Bidirectional structure built (908→target, target→908)  
✅ Every classification traces to an explicit, evidenced rule — no guessing  
✅ `UNKNOWN` used correctly (not conflated with `NO_TARGET`)  
✅ Matcher gaps identified with specific, named causes, not hand-waved  
⏳ FX abbreviation aliases, retraction-side-effect aliases, and case-only aliases (GLOBAL/Global) not yet added — would likely reduce `UNKNOWN` count meaningfully  
⏳ MACRO's apparent `NO_TARGET` status not yet positively confirmed  
🚫 Operation coverage: correctly deferred, not populated  
🚫 Representation families: correctly deferred, not populated

---

## Deliverables

| File | Contents |
|---|---|
| `SERUM2_TARGET_RECONCILIATION_MATRIX_FINAL.json` | Full bidirectional matrix: 908 semantic→target rows, 255 target→semantic rows |
| `PHASE_2D_TARGET_RECONCILIATION_AUDIT.md` | This document |

---

## Recommended Next Action

Before moving to representation families: close the three named matcher gaps (FX abbreviation, retraction-alias, GLOBAL case-alias) and re-run. This is mechanical refinement of the *same* Phase 2D pass, not new discovery — expect `UNKNOWN` to drop meaningfully and `ORPHAN_TECHNICAL` to drop toward the FX-abbreviation and retraction-alias counts. Then reassess what fraction of the 908 genuinely has no target (candidate `NO_TARGET` reclassification, still requiring positive confirmation per the governing rule) versus what fraction remains a matcher limitation.

---

**Status**: Phase 2D first pass complete and honestly reported. Not yet ready for representation-family derivation — recommend one more matcher refinement cycle first, since the current 834 UNKNOWN count is known to be inflated by specific, fixable gaps rather than reflecting the true absence of targets.
