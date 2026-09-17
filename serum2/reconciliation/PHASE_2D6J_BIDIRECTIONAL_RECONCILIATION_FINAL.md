2D.6J STATUS: COMPLETE
INPUT GATES: PASSED (908 semantic / 396 target, both asserted against raw files, not assumed)
SEMANTIC COUNT: 908 (source: SERUM2_SEMANTIC_NORMALIZED.json, metadata.record_count)
TARGET COUNT: 396 (source: SERUM2_TARGET_NORMALIZED_V4.json, metadata.total)
OLD UNKNOWN: 152 (source: _phase2d6f_true_unknown_152.json)
NEW UNKNOWN: 140 (recomputed from raw inputs, see Table A)
TARGET DISPOSITION TOTAL: 396 (298 OWNED + 2 MANY_TO_ONE + 13 DEAD_OR_SUPERSEDED + 6 DEAD_OR_SUPERSEDED_CANDIDATE + 77 UNKNOWN)
GRAPH CONSISTENCY: PASSED — 0 fail-closed validation errors

---

# Phase 2D.6J: Authoritative Bidirectional Reconciliation

**Date**: 2026-09-17
**Method**: Rebuilt from raw authoritative inputs by code (`_phase2d6j_build.py`, checked in alongside this report), not by patching 2D.6H's summary numbers. Every 2D.6H total is independently re-derived here and cross-checked against the raw files before any 2D.6I delta is applied.
**Scope**: Applies the 21 final target-side dispositions from `PHASE_2D6I_RECONCILIATION_FINAL.md`, further corrected by explicit rules given in this turn (FX.REVERB.DECAY_HALL treatment, individualized Wet-family evaluation, FX.FLANGER.PHASE contradiction handling, FX.DIMENSION.WET non-assumption). Does not modify `targets.py`, the semantic inventory, capability contracts, experiments, or admission logic — read/reconcile only.

---

## Input Gate Verification

| Artifact | Path | Assertion | Result |
|---|---|---|---|
| Frozen 908-semantic inventory | `SERUM2_SEMANTIC_NORMALIZED.json` | `metadata.record_count == 908` AND `len(records) == 908` | PASS |
| Complete 396-target vocabulary | `SERUM2_TARGET_NORMALIZED_V4.json` | `metadata.total == 396` AND `len(targets) == 396`, all unique | PASS |
| 2D.6D/E/F/G/H raw reconciliation artifacts | `_phase2d6g_semantic_rows.json` (908), `SERUM2_CONTROL_PATH_MATRIX.json` (908), `_phase2d6e_final_reverse_audit.json` (396), `_phase2d6f_true_unknown_152.json` (152), `_phase2d6h_four_tables.json` | all row counts verified against expected | PASS |
| 2D.6I dispositions | `PHASE_2D6I_RECONCILIATION_FINAL.md` (21 targets) | manually transcribed into `DISP_2D6I` dict, cross-checked as a subset of 2D.6H's 98 orphan_ids | PASS (21/21 ⊆ 98) |

No gate failed. No substitution of a partial/stale inventory occurred (the "0.8.0-KEYBOARD-CLOSED" partial inventory was never loaded). No inventory or vocabulary was reconstructed from prose — both counts were asserted directly against the raw JSON files' own record counts.

---

## Reproduction of 2D.6H From Raw Inputs (sanity check before applying any delta)

Before applying anything new, the build script re-derives 2D.6H's own numbers from `_phase2d6e_final_reverse_audit.json` (396 rows, pre-Table-3) plus `_phase2d6h_four_tables.json`'s `table3_newly_resolved` (7 items: 6× `LFOn.TRIGGER_MODE → LFOn-1.Mode`, 1× `FX.HYPER.RETRIG → FXHyper.Retrigger`):

```
296 MAPPED  (289 raw + 7 from Table 3)   == 2D.6H's stated 296 (293+3)  ✓
 98 ORPHAN_TECHNICAL (105 raw - 7)        == 2D.6H's stated 98 orphan_ids, set-equal  ✓
  2 MANY_TO_ONE                            == 2D.6H's stated 2  ✓
```
This match (down to set-equality of the 98 orphan IDs, not just the count) confirms the raw inputs are the same ones 2D.6H itself computed from, not a divergent snapshot.

Similarly, on the semantic side, cross-tabulating `_phase2d6g_semantic_rows.json` (908 rows, `mapping_class`) against `SERUM2_CONTROL_PATH_MATRIX.json` (908 rows, `status`) reproduces 2D.6H's 152 **exactly** (152/152 set-equal against `_phase2d6f_true_unknown_152.json`), and reproduces 460 = 275 CANDIDATE + 185 ESTABLISHED among the no-target semantics.

---

## TABLE A — Semantic → Technical (908 semantics)

```
MAPPED_TO_EXISTING_TARGET       294
MANY_TO_ONE / SHARED              3
CONTROL_PATH_KNOWN_NO_TARGET    447
PROVEN_NOT_USER_CONTROL          23
UNKNOWN                         140
BLOCKED_CONTRADICTED              1   (FX.FLANGER.PHASE -- see Contradiction Table; not
                                        counted in any of the 5 requested categories,
                                        called out separately per this turn's explicit
                                        instruction not to leave it as ordinary MAPPED)
─────
908
```

**`PROVEN_NOT_USER_CONTROL` (23)** is populated directly from the frozen semantic inventory's own `status` field (`SERUM2_SEMANTIC_NORMALIZED.json`), not inferred — e.g. `FX.EQUALIZER.LEVEL`, `FX.FLANGER.NO_SEPARATE_DELAY_KNOB`, `FX.SPLITTER_MS.WET` were already recorded as proven-not-a-control prior to this session. These were previously folded into the `CONTROL_PATH_KNOWN_NO_TARGET` bucket in 2D.6H's arithmetic (they carry `ESTABLISHED`/`CANDIDATE` control-path status); pulling them into their own bucket here is a bucket re-slicing, not a reclassification of any individual item's truth value — no semantic's underlying evidence changed.

**Changes applied this pass** (all individually justified, none inferred in bulk):

| Semantic | Old status | New status | Evidence | Rule applied |
|---|---|---|---|---|
| `FX.REVERB.DAMP_PLATE` | UNKNOWN (in 152) | `MAPPED_TO_EXISTING_TARGET` → `FXReverb.Damping` | DIRECT_UI "Rev Damp" + target now dispositioned in 2D.6I | 2D.6I final table |
| `FX.UTILITY.MONO_BASS` | CONTROL_PATH_KNOWN_NO_TARGET (CANDIDATE) | `MAPPED_TO_EXISTING_TARGET` → `FXUtility.Mono` | DIRECT_UI "Utils Mono Side" (already recorded in the semantic inventory's own label) | 2D.6I final table |
| `FX.REVERB.DECAY_HALL` | UNKNOWN (in 152) | `CONTROL_PATH_KNOWN_NO_TARGET` | DIRECT_UI "Rev Decay" (Hall type). **No target created or assigned** — explicit instruction this turn | This-turn STOP rule #1 |
| `FX.CHORUS.WET` | UNKNOWN (in 152) | `CONTROL_PATH_KNOWN_NO_TARGET` | DIRECT_UI "Cho Wet" | This-turn STOP rule #2, evaluated individually |
| `FX.BODE.WET` | UNKNOWN (in 152) | `CONTROL_PATH_KNOWN_NO_TARGET` | DIRECT_UI "Bode Wet" | same |
| `FX.COMPRESSOR.WET` | UNKNOWN (in 152) | `CONTROL_PATH_KNOWN_NO_TARGET` | DIRECT_UI "Comp Wet" | same |
| `FX.CONVOLVE.WET` | UNKNOWN (in 152) | `CONTROL_PATH_KNOWN_NO_TARGET` | DIRECT_UI "Conv Wet" | same |
| `FX.FLANGER.WET` | UNKNOWN (in 152) | `CONTROL_PATH_KNOWN_NO_TARGET` | DIRECT_UI "Flg Wet" | same |
| `FX.HYPER.WET` | UNKNOWN (in 152) | `CONTROL_PATH_KNOWN_NO_TARGET` | DIRECT_UI "Hyp Wet" | same |
| `FX.PHASER.WET` | UNKNOWN (in 152) | `CONTROL_PATH_KNOWN_NO_TARGET` | DIRECT_UI "Phs Wet" | same |
| `FX.UTILITY.WET` | UNKNOWN (in 152) | `CONTROL_PATH_KNOWN_NO_TARGET` | DIRECT_UI "Utils Wet" | same |
| `FX.REVERB.WET` | UNKNOWN (in 152) | `CONTROL_PATH_KNOWN_NO_TARGET` | DIRECT_UI "Rev Wet" | same |
| `FX.DIMENSION.WET` | UNKNOWN (in 152) | `CONTROL_PATH_KNOWN_NO_TARGET` | DIRECT_UI "Hyp im Mix". **Inspected separately per instruction**: `FXDimension.Mix` / `FXDimension.MixOrGain` **do not exist anywhere in the 396-target vocabulary**. This is not the Wet/Mix alias-ambiguity pattern (which presumes ≥2 competing existing targets) — it is a real, observed control with **zero** candidate targets. Recorded as its own distinct case, not merged into the 9-module Wet-alias family. | This-turn STOP rule #4 |
| `FX.DELAY.WET` | UNKNOWN (in 152) | **unchanged — still UNKNOWN** | No DIRECT_UI right-click was performed on Delay's MIX knob this session (only `TimeL`/`TimeR`/`FREQ`/`Q` were checked). Explicitly **not** moved, to avoid inferring from the 9-module pattern. | This-turn STOP rule #2 (per-item evaluation, absence of evidence honored) |
| `FX.FLANGER.PHASE` | `MAPPED_TO_EXISTING_TARGET` (`FXFlanger.Phase`, via `ALIAS_RULE`) | `BLOCKED_CONTRADICTED` | Old mapping was a mechanical name-pattern guess, never verified. New DIRECT_UI evidence this session ("FX 1: Flg Width" at the same UI position) contradicts it. **Both preserved**; neither trusted until reverified. See Contradiction Table. | This-turn STOP rule #3 |

12 semantics moved out of the 152 (11 into `CONTROL_PATH_KNOWN_NO_TARGET`, 1 into `MAPPED_TO_EXISTING_TARGET`). **Zero** moved in. `FX.DELAY.WET` was evaluated and explicitly left in place.

---

## TABLE B — Technical → Semantic (396 targets)

```
OWNED                          298   (296 raw + 2 newly mapped: FXReverb.Damping,
                                       FXUtility.Mono)
MANY_TO_ONE / SHARED             2
DEAD_OR_SUPERSEDED              13   (final — see list below)
DEAD_OR_SUPERSEDED_CANDIDATE      6   (evidence points this way; residual naming gap or
                                       separate semantic-side question kept open, per
                                       2D.6I discipline — NOT collapsed to final DEAD)
UNKNOWN                         77   (the 98-21=77 orphans not part of this pass's 21;
                                       untouched, still individually undispositioned)
─────
396
```

**`DEAD_OR_SUPERSEDED` (13, final)**:
```
FXBODE.LevelOut
FXChorus.Phase
FXConvolve.IR
FXConvolve.IRPath
FXDistortion.BW
FXDistortion.LevelOut
FXDistortion.Tone
FXEQ.LevelOut
FXUtility.Gain
FXUtility.Phase
OSC2.Detune
OSC3.Detune
SUB.Detune
```

**`DEAD_OR_SUPERSEDED_CANDIDATE` (6, not final)**:
```
FXBODE.Frequency
FXDelay.BW
FXDelay.OffsetL
FXDelay.OffsetR
FXDelay.Time
FXReverb.Time
```
`FXReverb.Time` in particular is explicitly *not* promoted to final dead: its live identity conflicts with the target name ("Decay," not "Time"), but the semantic-side counterpart `FX.REVERB.DECAY_HALL` remains open (now `CONTROL_PATH_KNOWN_NO_TARGET`, not resolved) — the target's staleness and the semantic's gap are two separate open facts, not one closure.

**Newly `OWNED` this pass (2)**:
```
FXReverb.Damping   <- FX.REVERB.DAMP_PLATE
FXUtility.Mono     <- FX.UTILITY.MONO_BASS
```

**`UNKNOWN` (77)** — the remainder of 2D.6H's 98 orphans not touched by 2D.6I or this turn. Listed in the JSON output (`table_b_technical_to_semantic.remaining_orphans_77_not_yet_dispositioned`); includes the AMBIGUOUS Wet/Mix-alias targets themselves (e.g. `FXChorus.Mix`, `FXChorus.MixOrGain`, `FXReverb.Mix`, `FXReverb.MixOrGain`, etc. — the *target* aliases remain undispositioned even though their *semantic* counterpart's control path is now known), the Splitter crossover/bandcount targets, the FilterFX family, Global.* fields, Filter.Q/Filter2.Q, and `ARP.Enable`. None of these were in scope for 2D.6I or this turn's rules, so none were touched — this is a deliberate non-closure, not an oversight.

---

## TABLE C — 2D.6I Delta

```
21 targets dispositioned (2D.6I, all ⊆ 2D.6H's 98 orphans):
   2  MAPPED_TO_EXISTING_SEMANTIC  (FXReverb.Damping, FXUtility.Mono)
  13  DEAD_OR_SUPERSEDED (final)
   6  DEAD_OR_SUPERSEDED_CANDIDATE (not final)

13 semantics touched this pass (beyond the 21 targets):
  11  UNKNOWN -> CONTROL_PATH_KNOWN_NO_TARGET  (DECAY_HALL + 10 Wet-family members)
   1  UNKNOWN -> MAPPED_TO_EXISTING_TARGET     (DAMP_PLATE; already counted in the 2)
   1  CONTROL_PATH_KNOWN_NO_TARGET -> MAPPED_TO_EXISTING_TARGET  (MONO_BASS; already
                                                                   counted in the 2)
   1  MAPPED_TO_EXISTING_TARGET -> BLOCKED_CONTRADICTED  (FX.FLANGER.PHASE)

1 semantic explicitly evaluated and left unchanged:
   FX.DELAY.WET (no DIRECT_UI evidence collected this session)

1 case explicitly distinguished from the Wet/Mix alias family:
   FX.DIMENSION.WET (zero candidate targets exist at all, not 2 competing ones)
```

---

## TABLE D — Unresolved Populations / Disposition Summary

```
Semantic side (908):
  908 = 294 MAPPED_TO_EXISTING_TARGET
      +   3 MANY_TO_ONE
      + 447 CONTROL_PATH_KNOWN_NO_TARGET
      +  23 PROVEN_NOT_USER_CONTROL
      + 140 UNKNOWN
      +   1 BLOCKED_CONTRADICTED

Target side (396):
  396 = 298 OWNED
      +   2 MANY_TO_ONE
      +  13 DEAD_OR_SUPERSEDED
      +   6 DEAD_OR_SUPERSEDED_CANDIDATE
      +  77 UNKNOWN

Old unknown (semantic, 2D.6H):  152
New unknown (semantic, 2D.6J):  140
Delta:                          -12  (11 to CONTROL_PATH_KNOWN_NO_TARGET, 1 to MAPPED)

Target-side unknown (2D.6H orphans, still undispositioned): 77
  (98 - 21 audited this pass = 77; unchanged in count, unchanged in membership --
   none of the 77 were touched)
```

---

## Contradiction Table (separate from ordinary mapping tables, per explicit instruction)

| Semantic | Target | Status | Old evidence | New evidence | Resolution |
|---|---|---|---|---|---|
| `FX.FLANGER.PHASE` | `FXFlanger.Phase` | **`BLOCKED_CONTRADICTED`** | `mapping_class=EXACT`, `mapping_basis=ALIAS_RULE`, evidence: *"FX.{Module}.{Field} -> FX{Module}.{Field} general pattern"* (a mechanical name-pattern guess, never independently verified) | DIRECT_UI this session: right-clicking the UI-labeled "PHASE" knob on Flanger returned `FX 1: Flg Width`, not "Phase" | **UNRESOLVED.** Neither side is treated as authoritative. The old `ALIAS_RULE` mapping is *not* carried forward as ordinary `MAPPED_TO_EXISTING_TARGET` in Table A (see `BLOCKED_CONTRADICTED`, 1). The new evidence is *not* treated as a resolution, and no target named `FXFlanger.Width` is created — that would be inventing vocabulary from a UI label, which this pass does not do. Both records are preserved verbatim in the JSON output for whoever reverifies this next. |

This is the only contradiction surfaced this pass. It was found incidentally — the Flanger's PHASE-position knob was right-clicked in 2D.6I only to investigate the *unrelated* `FXChorus.Phase` orphan (checking whether Chorus and Flanger share an analogous "Phase" concept). It was not a target of the 21-item audit itself, so its correction is bounded strictly to flagging, per this turn's explicit rule 3.

---

## Fail-Closed Validation (all checks executed programmatically, see `_phase2d6j_build.py`)

```
[x] no duplicate semantic IDs           (908 unique, asserted at load)
[x] no duplicate target IDs             (396 unique, asserted at load)
[x] no target assigned contradictory dispositions
[x] no semantic assigned contradictory ownership
[x] no count mismatch                   (908 and 396 both verified to sum exactly)
[x] no UNKNOWN silently converted to dead
[x] no DEAD_OR_SUPERSEDED_CANDIDATE silently converted to final DEAD
[x] no Wet/Mix alias collapse without explicit evidence  (0 Wet-family semantics were
    ever assigned a target_id in this pass)
[x] no FX census-name inference          (all FX-side moves this pass are DIRECT_UI only;
    the 3 Detune census-negatives are OSC-side, not FX, and were already established in
    2D.6I, not re-derived here)

RESULT: 0 errors. PASSED.
```

---

## Explicitly NOT Done This Pass

- The 77 remaining target-side orphans (Wet/Mix aliases themselves, Splitter, FilterFX, Global.*, Filter.Q/Filter2.Q, ARP.Enable) are untouched — still `UNKNOWN` on the target side, unchanged in membership from 2D.6H.
- No semantic inventory file, `targets.py`, capability contract, experiment, or admission-logic file was modified. This was a read/reconcile operation only, verified by the `not_modified` list in the JSON output.
- `FX.FLANGER.PHASE` / `FXFlanger.Phase` remains formally unresolved (`BLOCKED_CONTRADICTED`), not silently defaulted either direction.
- `FX.DIMENSION.WET` is flagged as needing its own future target-vocabulary decision (does a `FXDimension.*` mix target need to be *created*, as opposed to *found*?) — that is a vocabulary-expansion question, explicitly out of scope for a read/reconcile pass, and is not answered here.

---

## Deliverables

| File | Contents |
|---|---|
| `_phase2d6j_build.py` | The exact, auditable script that reproduced 2D.6H from raw inputs and applied the 2D.6I + this-turn deltas |
| `PHASE_2D6J_BIDIRECTIONAL_RECONCILIATION_FINAL.json` | Machine-readable four tables + contradiction table + fail-closed validation result |
| `PHASE_2D6J_BIDIRECTIONAL_RECONCILIATION_FINAL.md` | This document |

**SHA-256 of `PHASE_2D6J_BIDIRECTIONAL_RECONCILIATION_FINAL.json`**: `7db6bc6e2865ea66e58ae0eaf92c6849a07096d444205632b11d5b7aded83cb2`

---

## Updated Phase State

```
PHASE 2D.6I   Item-by-item live-UI orphan audit (21/21)            ✅ CLOSED
PHASE 2D.6J   Authoritative bidirectional reconciliation             ✅ COMPLETE
                908/908 semantic, 396/396 target, both gates passed.
                152 -> 140 (recomputed, not patched). 1 contradiction
                surfaced and preserved unresolved. 77 target-side
                orphans deliberately untouched.
PHASE 2D (global)                                                     NOT CLOSED
                140 semantic unknowns remain (2D.6K candidate queue).
                77 target-side orphans remain undispositioned.
                1 contradiction (FX.FLANGER.PHASE) needs its own
                reverification pass before it can be trusted either way.
```

**Not proceeding to Phase 2D.6K automatically** — this reconciliation produces the starting population (140, not 152) but does not itself launch the semantic-unknown investigation. Awaiting direction.
