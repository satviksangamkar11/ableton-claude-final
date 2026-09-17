# Phase 2A-R.6: SUB/NOISE Completeness Check

**Date**: 2026-09-16  
**Method**: Field-by-field mapping against `EXHAUSTIVE_CENSUS_ALL_2623.json` (full VST3 parameter census with index/name/baseline/behaviorally-verified `MUTABLE_RESTORED` status) — NOT assumed identical to OSC A/B/C.

---

## SUB and NOISE Have Genuinely Smaller Technical Universes

```
OSC A/B/C:  55 fields each  (indices 20-62 semantic + 63-74 technical-only)
SUB:        12 fields total (indices 193-201, plus 460-462 routing)
NOISE:      11 fields total (indices 185-192, plus 457-459 routing)
```

This confirms the caution was correct — SUB/NOISE lack all Wavetable/Sample/Unison/Warp/Loop/Scan complexity. They are structurally simpler generators, not scaled-down copies of the OSC A/B/C model.

---

## Field-By-Field Disposition

### SUB (12 fields)

| VST3 field | idx | Disposition |
|---|---|---|
| Sub Enable | 193 | **NEW** → `SUB_OSC.ENABLE` (flagged, see below) |
| Sub Level | 194 | Already covered → `SUB_OSC.LEVEL` |
| Sub Pan | 195 | Already covered → `SUB_OSC.PAN` |
| Sub Octave | 196 | Already covered → `SUB_OSC.OCTAVE` |
| Sub Coarse Pitch | 197 | Already covered → `SUB_OSC.COARSE_PITCH` |
| Sub Pitch Track | 198 | **NEW** → `SUB_OSC.PITCH_TRACK` |
| Sub Shape | 199 | **NEW** → `SUB_OSC.SHAPE` |
| Sub Phase | 200 | Already covered → `SUB_OSC.PHASE` |
| Sub Cont. Phase | 201 | **NEW** → `SUB_OSC.CONT_PHASE` |
| Sub Osc>Filter Balance | 460 | Already covered → `MIXER.SUB.FILTER_BALANCE` |
| Sub Osc>BUS1 | 461 | Already covered → `MIXER.SUB.BUS1` |
| Sub Osc>BUS2 | 462 | Already covered → `MIXER.SUB.BUS2` |

**8 already covered, 4 genuinely new.**

### NOISE (11 fields)

| VST3 field | idx | Disposition |
|---|---|---|
| Noise Enable | 185 | **NEW** → `NOISE_OSC.ENABLE` (flagged, see below) |
| Noise Level | 186 | Already covered → `NOISE_OSC.LEVEL` |
| Noise Pan | 187 | Already covered → `NOISE_OSC.PAN` |
| Noise Pitch Track | 188 | **NEW** → `NOISE_OSC.PITCH_TRACK` |
| Noise Pitch | 189 | Already covered → `NOISE_OSC.PITCH` |
| Noise Fine | 190 | Already covered → `NOISE_OSC.FINE` |
| Noise Phase | 191 | Already covered → `NOISE_OSC.PHASE` |
| Noise Rand Phase | 192 | Already covered → `NOISE_OSC.RAND_PHASE` |
| Noise>Filter Balance | 457 | Already covered → `MIXER.NOISE.FILTER_BALANCE` |
| Noise>BUS1 | 458 | Already covered → `MIXER.NOISE.BUS1` |
| Noise>BUS2 | 459 | Already covered → `MIXER.NOISE.BUS2` |

**9 already covered, 2 genuinely new.**

---

## Verification Steps Performed

1. Every "already covered" mapping was checked for actual presence in the 833-record baseline (not assumed) — `Mapped-but-NOT-actually-present` check returned empty
2. Every new candidate's constructed `semantic_id` was checked against the baseline before being added — `A ∩ new = 0`
3. Two genuine discoveries surfaced that don't appear anywhere in prior project evidence: **`Sub Shape`** (idx 199) and **`Sub Cont. Phase`** (idx 201) — these are real VST3 fields with `MUTABLE_RESTORED` behavioral confirmation (actually mutated and read back during a census experiment), not previously itemized in any closure report

---

## Enable: Flagged, Not Merged (Consistent With Prior Treatment)

`SUB_OSC.ENABLE` and `NOISE_OSC.ENABLE` both carry `POTENTIAL_DUPLICATE_UNRESOLVED` against `MIXER.SUB.ENABLE` / `MIXER.NOISE.ENABLE`, joining the 9 flagged from OSC1/2/3 (Phase 2A-R.5). This is now an **11-item unresolved ownership question**, deferred to Phase 2A-R.7 as planned — not decided here.

---

## Result

```
833  (post-OSC1/2/3)
 +6  SUB(4) + NOISE(2), verified non-overlapping
────
839  current evidence-derived union
```

---

## Updated Phase State

```
PHASE 2A-R.5  OSC1/2/3 atomization                  ✅ COMPLETE (833)
PHASE 2A-R.6  SUB/NOISE completeness                 ✅ COMPLETE (839)
PHASE 2A-R.7  Resolve 11 flagged Enable/Level/Pan    ⏳ NEXT
              ownership questions (OSC1-3: 9, SUB: 1, NOISE: 1)
PHASE 2A-R.8  MATRIX.SOURCE atomization              ⏳ AFTER R.7 (kept separate, not mixed into OSC accounting)

PHASE 2C+                                            🚫 still blocked
```

---

**Status**: 839 is the current machine-verified union (0 duplicate IDs across all additions). Two new controls discovered (Sub Shape, Sub Cont. Phase) that existed in no prior project document. 11 ownership questions await Phase 2A-R.7. MATRIX.SOURCE gap remains separately tracked, not yet touched.
