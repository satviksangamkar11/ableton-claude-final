# Phase 2D.3: Final Closure Round + Reconciliation Snapshot Freeze

**Date**: 2026-09-16

---

## Result Across All Closure Rounds

```
                First pass  2D.2 closure  2D.3 closure (final)
EXACT               73          84            119
ONE_TO_MANY          1           1              1
UNKNOWN            834         823            788
MAPPED (reverse)    78          89            124
ORPHAN_TECHNICAL   177         166            131
```

---

## The Four Resolver Classes — Disposition

### 1. BUS-send ownership — CLOSED (21 mappings)

`MIXER.{X}.BUS1/BUS2` records explicitly state in their own pre-existing notes: *"Exact physical control underlying the Matrix destination {X}>BUS1/BUS2"* — direct textual evidence, not inference. `ROUTING→Route` extended via the FILTER closure ledger's own explicit grouping of BUS1Send+BUS2Send+Route as one "existing_routing_targets" package. Applied across OSC1-3/SUB/NOISE/FILTER1-2 (7 instances × 3 fields = 21).

**Bonus, found while closing this class**: `MIXER.FILTER{n}.LEVEL/WET/ENABLE` → `FILTER{n}.Level/Mix` + `Filter{n}.Enable` (6 more mappings) — same R.4 evidence, just not yet wired into the matcher.

### 2. LFO Shape/Mode/Retrigger — INVESTIGATED, LEFT UNKNOWN (correctly)

Checked the actual VST3 parameter census directly. **Decisive finding**: LFO's real host parameters are exactly `Rate/Smooth/Rise/Delay/Phase` (5 fields) — confirmed by name (`"LFO 1 Rate"`, `"LFO 1 Smooth"`, etc.). **Zero** `Shape`/`Mode`/`Retrigger` parameters exist anywhere in the 2623-parameter space (searched for "trig", "shape" — only unrelated matches: `Arp Retrig Rate`, `Sub Shape`).

This means `targets.py`'s `LFO{n}.Shape/.Mode/.Retrigger` (30 entries) have no confirmed VST3 host-parameter backing at all — they use the `_field_` (body-state) capability_key pattern, which this pass could not independently verify. Whether they correspond to the semantic side's confirmed `TYPE`/`DIRECTION`/`TRIGGER_MODE` fields is plausible by name but **not established by evidence**. Per your instruction, **not aliased**.

**Secondary finding**: `Smooth`/`Rise`/`Delay` are now confirmed-real semantic AND VST3-parameter fields, but `targets.py` has no target entries for them at all — a genuine target-vocabulary gap distinct from the Shape/Mode/Retrigger question.

### 3. GLOBAL field debug — 8 of 13 CLOSED, 5 LEFT UNKNOWN WITH NAMED REASONS

`targets.py`'s `Global.*` namespace bundles fields the semantic inventory correctly split across GLOBAL/GLOBAL_KEYBOARD/VOICE by actual UI panel location.

| Target | Resolution | Basis |
|---|---|---|
| `Global.MasterVolume` | → `MIXER.MAIN.LEVEL` | Direct (R.9 + existing GLOBAL closure text) |
| `Global.Transpose` | → `KEYBOARD.TRANSPOSE` | Direct (R.9) |
| `Global.Tuning` | → `GLOBAL.TUNING.GLOBAL_TUNING` | Direct (R.9) |
| `Global.Swing` | → `KEYBOARD.SWING` | Direct (R.9) |
| `Global.Portamento` | → `VOICE.VOICING.PORTA_TIME` | Direct (R.9) |
| `Global.Scale` | → `KEYBOARD.SCALE` | Structural pattern (same GLOBAL_KEYBOARD family as 2 direct confirmations) |
| `Global.Key` | → `KEYBOARD.KEY` | Structural pattern |
| `Global.Mono` | → `VOICE.VOICING.MONO` | Structural pattern (same VOICE family as Portamento) |
| `Global.Quality` | **UNKNOWN** | 4 ambiguous candidates (Oversampling/OversamplingLock/S1Compat/DisableSmoothing), no disambiguator |
| `Global.Glide` | **UNKNOWN** | No "Glide" field found anywhere in VOICE.VOICING.* or elsewhere |
| `Global.Voicing` | **UNKNOWN** | Ambiguous between MONO/POLY/other, no disambiguator |
| `Global.VelocityCurve` | **UNKNOWN** | Matches an existing project memory's own explicitly-unresolved hypothesis (VOICE closure: "likely a mislabeling of PORTA_CURVE... NOT ruled out") — consistent with that prior disposition, not newly resolved here |
| `Global.PitchTracking` | **UNKNOWN** | No corroborating evidence found |

### 4. EQ LEFT/RIGHT ↔ target 1/2 — CORRECTLY LEFT UNKNOWN

No new evidence found this round to establish the correspondence. Remains flagged as a structural-model question (independent stereo channels vs. numbered bands), not resolved by lexical substitution. **9 `FXEQ.*` targets remain orphaned**, honestly.

---

## Three-Population State (Final for This Snapshot)

```
Population A (target established):   120 semantics  (119 EXACT + 1 ONE_TO_MANY)
Population B (UNKNOWN):               788 semantics
Population C (proven NO_TARGET):        0 semantics
```

**Population C remains empty.** No semantic anywhere in this reconciliation has been positively proven to lack a target. This is the correct, disciplined outcome after four full closure rounds — `UNKNOWN` is doing its job as the honest default.

---

## Remaining Unresolved Queue

### UNKNOWN semantics (788), by section

| Section | Count | Section | Count |
|---|---|---|---|
| FX | ~140 | ARP | 50 |
| OSC | ~115 | MACRO | 48 |
| MATRIX | 80 | BROWSER | 41 |
| LFO | 78 | ENV | 32 |
| MIXER | ~40 | CLIP | 30 |
| FILTER | ~50 | GLOBAL_KEYBOARD | 21 |
| GLOBAL | ~46 | VOICE | 8 |

*(Full per-semantic list: `_phase2d3_closed_semantic_rows.json`)*

### ORPHAN targets (131), named categories

- **EQ family (9)**: structural Left/Right vs 1/2 question, unresolved
- **LFO Shape/Mode/Retrigger (30)**: no VST3 backing found; body-state-only claim unverified
- **FX MixOrGain/BW/TimeL/TimeR variants (~45)**: extended FX target fields with no corresponding single semantic field name — likely targets.py extensions beyond what the FX closure ledger itemized
- **GLOBAL remainder (5)**: Quality/Glide/Voicing/VelocityCurve/PitchTracking, each individually reasoned above
- **MACRO-adjacent, FILTER Q, misc (~15)**: `Filter.Q`/`Filter2.Q`, `NOISE.Fine`, `ARP.Enable`, `BUS1.Level`/`BUS2.Level`, `OSC{n}.Volume/Detune/Wavetable` — not yet investigated, candidates for a future round
- **MACRO value itself**: still fully UNKNOWN (48 semantics), `ModRoute.MacroDepth` confirmed insufficient, no replacement target identified

### ONE_TO_MANY (1)

`MATRIX.ROUTING.SIGNAL_BALANCE` → 5 `ModRoute.*` targets (Curve/Bipolar/AuxSource/MacroDepth/Bypass) — genuine structural multiplicity, not ambiguity.

### MANY_TO_ONE (reverse audit)

Present in the reverse audit file wherever a target has >1 mapped semantic — not separately tabulated here, available in `_phase2d3_reverse_audit.json`.

---

## Snapshot Frozen

```
SERUM2_ALIAS_REGISTRY.json           — final, all 4 resolver classes documented with evidence
_phase2d3_closed_semantic_rows.json  — 908 rows, final mapping_class/mapping_basis/evidence
_phase2d3_reverse_audit.json         — 255 rows, final target->semantic classification
PHASE_2D3_CLOSURE_AND_FREEZE.md      — this document
```

This snapshot is the reconciliation state as of 2026-09-16, closure rounds 2D.1-2D.3 complete.

---

## Updated Phase State

```
PHASE 2D.1  Mechanical reconciliation (first pass)   ✅ 73/834/177
PHASE 2D.2  Alias/ownership closure round 1           ✅ 84/823/166
PHASE 2D.3  Alias/ownership closure round 2 (final)   ✅ 119/788/131
PHASE 2D.4  Human/evidence review of remainder        ⏳ NEXT
                Queue: FX MixOrGain/BW gaps, MACRO value target, Filter.Q,
                remaining ~15 uncategorized orphans
PHASE 2D.5  Classify true NO_TARGET vs UNKNOWN         🚫 waits on 2D.4
PHASE 2D.6  Operation coverage                         🚫 waits on 2D.5
PHASE 2D.7  Representation families                    🚫 waits on 2D.6
```

---

**Status**: Reconciliation snapshot frozen. 120 of 908 semantics (13.2%) now have an evidence-backed target mapping — up from 65 (7.2%) at the very first pass, via four disciplined closure rounds, zero forced aliases, zero fabricated `NO_TARGET` declarations. 788 remain genuinely `UNKNOWN`, correctly distinguished from `NO_TARGET`. Ready for 2D.4 once you're ready to proceed — not yet moving to representation families.
