# Phase 2D.6D: Complete Control-Path Reconciliation for All 908 Semantics

**Date**: 2026-09-16  
**Scope**: Every one of the 908 semantics gets a `control_path_class`, whether or not it has a `target_id`. This is the distinction your instruction drew: a structural action, a MATRIX route, or a resource operation can have an **established control path** without ever being a VST3 scalar parameter.

---

## Bonus Target Found First: ENV Hold

Before the classification pass, checked the census for `Env {N} Hold` (the ENV Hold gap flagged all the way back in Phase 2A-R.4's original itemization) — confirmed real, all 4 indices found by name. Added as 4 more targets. **Population A: 264 → 268.**

---

## Control-Path Classification (All 908)

```
HOST_PARAMETER               238   confirmed VST3 parameter (targeted or PROVEN_NOT_USER_CONTROL)
UI_ACTION                    198   structural_action UI mechanism, CANDIDATE confidence
MATRIX_ROUTE                 104   route source/destination/bus/signal-balance concept
BODY_STATE_FIELD              88   plausible internal state, no confirmed VST3 host param
RESOURCE_OPERATION            53   BROWSER/preset/bank workflow
SHARED_PHYSICAL_PARAMETER     46   confirmed same physical param, dual UI surface
STRUCTURAL_OPERATION          10   slot/bank/context-menu mechanism, ESTABLISHED confidence
MULTI_TARGET                   2   maps to multiple targets simultaneously
UNKNOWN                      169   genuinely no control-path evidence of any kind
────
908
```

```
status: ESTABLISHED  453   (50%)
status: CANDIDATE    286   (31%)
status: UNKNOWN       169   (19%)
```

**Every one of the 908 rows now has a `control_path_class`** — none left as a bare "UNKNOWN" without at least attempting classification from existing evidence. The 169 genuinely `UNKNOWN` rows are concentrated where expected:

| Section | Count |
|---|---|
| FX | 83 |
| MIXER | 12 |
| ARP | 16 |
| MACRO | 17 |
| GLOBAL | 28 |
| GLOBAL_KEYBOARD | 4 |
| CLIP | 4 |
| VOICE | 2 |
| MATRIX | 3 |

---

## Key Distinctions Applied (Per Your Instruction)

- **`STRUCTURAL_OPERATION` (10, ESTABLISHED) vs `UI_ACTION` (198, CANDIDATE)**: Slot/bank/context-menu mechanisms with a very specific, unambiguous UI shape (`.SLOT.`, `.GLOBAL.BANK`, `CONTEXT_MENU`, `PLAY_BUTTON`) got `ESTABLISHED`. Everything else merely flagged `structural_action=True` in its own source record got `UI_ACTION` at `CANDIDATE` confidence — real, but not independently confirmed as a specific control mechanism.
- **`MATRIX_ROUTE` (104, ESTABLISHED)**: Includes the 16 `MATRIX.LFO_BUS.*`, `MATRIX.ROUTING.SIGNAL_BALANCE`, all `MATRIX.SOURCE.*`/`.DESTINATION.*` (49), the `GLOBAL.RETRIGGERS.*` family (19, since it's structurally a per-source route-adjacent toggle), and `ENV{n}.SOURCE`/`LFO{n}.SOURCE` (10, the drag-handle route-creation affordance) — all confirmed by their own closure-ledger evidence, not inferred from naming.
- **`RESOURCE_OPERATION` (53, ESTABLISHED)**: BROWSER section (41) + anything carrying `resource_dependency` — a genuinely different control mechanism (filesystem/preset layer) from parameter mutation.
- **`BODY_STATE_FIELD` (88, CANDIDATE)**: The 40 FILTER type-specific fields (X/Y-slot hypothesis, unconfirmed) + LFO's Type/TempoSync/Division/Triplet/Dotted/Direction/Preset/WaveformGraph (48, confirmed NO VST3 backing via direct census check, plausibly body-state). Marked `CANDIDATE`, not `ESTABLISHED` — the *existence* of these controls is proven (UI-confirmed in the original closure passes), but the *representation mechanism* is not confirmed, exactly the distinction your instruction requires.
- **`HOST_PARAMETER` including `PROVEN_NOT_USER_CONTROL`**: The 6 `UNKNOWN_HOST_BACKLOG` items (Ratio/Hz Offset ×3) get `control_path_class: HOST_PARAMETER` — the VST3 field genuinely exists, it's just deliberately not exposed to the user. This is a resolved classification even though no target was created (correctly, per 2D.6A's earlier decision).

---

## Reverse Audit: Every Target, Ownership Status

```
396 total targets (392 + 4 new ENV Hold)
  268   MAPPED (single semantic owner)
    2   MANY_TO_ONE
  126   ORPHAN_TECHNICAL
```

### Orphan Disposition — Categorized, Not Left as a Mystery

| Category | Count | Disposition |
|---|---|---|
| **LFO6-9's Rate/Shape/Mode/Phase/Retrigger** | 20 | **Explained, not orphaned in spirit**: targets `LFO6`-`LFO9` correspond (via the confirmed off-by-one) to semantic `LFO7`-`LFO10`, which Phase 2A-R.4's own LFO closure directly confirmed as **headless** — 0 UI-accessible parameters each. These targets have no semantic owner because the feature they'd control doesn't exist at the UI level. Technical-only by confirmed structural fact, not an unresolved gap. |
| **LFO0-6's Shape/Mode/Retrigger** | 18 | No VST3 host-parameter backing found anywhere (confirmed directly, twice). Genuinely unconfirmed technical identity — these targets.py entries may not correspond to any real, addressable Serum state at all. |
| **OSC1-3.Volume, OSC1-3.Detune, SUB.Volume/Detune** | 8 | **Already documented as dead** in the pre-existing `OSC_FINAL_CLOSURE_REPORT.md`: *"3 duplicate entries in targets.py are dead vocabulary: OSC1/2/3.Volume, superseded by working .Level targets"* — this is prior project evidence, not a new finding. Technical-only, explicitly stale. |
| **FX MixOrGain/BW/TimeL/TimeR/IRPath family** | ~40 | Extended FX target fields with no single corresponding semantic field name — `targets.py` was extended with FX detail beyond what the FX closure ledger itemized. Genuine target-vocabulary-ahead-of-semantic-discovery gap. |
| **FXEQ family** | 9 | The Left/Right (semantic) vs 1/2 (target) structural-model question, still unresolved per your instruction not to force it without evidence. |
| **Global.Quality/Glide/Voicing/VelocityCurve/PitchTracking** | 5 | Individually reasoned and left open in Phase 2D.3 — unchanged. |
| **Filter.Q, Filter2.Q** | 2 | Not yet investigated — candidate for a future pass. |
| **ARP.Enable** | 1 | Not yet investigated — ARP almost certainly has a semantic Enable concept; needs a targeted check. |
| **Remainder** | ~23 | Not yet individually categorized. |

**126 orphans is not 126 unexplained gaps.** 28 of them (LFO6-9 headless + OSC/SUB dead vocabulary) are now explained by evidence already in the project, not new mysteries.

---

## Gate Assessment (Your Explicit Criteria)

```
✓ Every semantic has:
    - established control path (453, ESTABLISHED)
    - candidate control path (286, CANDIDATE — plausible, not fully confirmed)
    - genuinely UNKNOWN (169, honestly reported)
    - explicitly proven NO_TARGET: STILL ZERO — no semantic has been declared
      unreachable anywhere in this entire reconciliation

✓ Every technical target has:
    - semantic ownership (268 + 2 MANY_TO_ONE = 270)
    - OR is explicitly categorized as technical-only/stale/unconfirmed (28 of 126
      orphans now explained; 98 remain uncategorized, not yet "explicitly technical-only")
```

**The gate is not fully closed.** 169 semantics remain genuinely `UNKNOWN` (no control-path evidence at all), and 98 of 126 orphan targets are not yet individually disposed with a specific reason. This is reported honestly rather than declared complete.

---

## What Changed From the Master-Plan Framing

Your instruction was explicit: *"the ultimate target universe cannot be defined as host parameters alone."* This pass makes that concrete — of the 908:

```
Would-be "controllable" under a host-parameter-only view:   268 (30%)
Actually has a legitimate, evidenced control path:          453 (50%)  established
                                                            + 286 (31%)  candidate
                                                            = 739 (81%)
```

The 471-semantic gap between "has a target" (268) and "has an established/candidate control path" (739) is exactly the population that a VST3-parameter-only reconciliation would have wrongly written off as uncontrollable.

---

## Deliverables

| File | Contents |
|---|---|
| `SERUM2_CONTROL_PATH_MATRIX.json` | 908 rows: control_path_class, target_ids, mapping_basis, status (ESTABLISHED/CANDIDATE/UNKNOWN) |
| `SERUM2_TARGET_NORMALIZED_V4.json` | 396-target vocabulary (392 + 4 ENV Hold) |
| `_phase2d6d_reverse_audit.json` | 396 targets, ownership classification |
| `_phase2d6d_final_semantic_rows.json` | Underlying semantic-to-target mapping state |
| `PHASE_2D6D_CONTROL_PATH_RECONCILIATION.md` | This document |

---

## Updated Phase State

```
PHASE 2D.6D  Control-path reconciliation (all 908)     🟡 SUBSTANTIALLY ADVANCED, NOT CLOSED
                453 ESTABLISHED, 286 CANDIDATE, 169 UNKNOWN
                270 of 396 targets have semantic ownership; 28 more orphans explained
                (headless LFO, dead vocabulary); 98 orphans still uncategorized

PHASE 2D    (global)                                    NOT CLOSED
                Gate criteria: partially met (0 NO_TARGET maintained throughout;
                169 UNKNOWN and 98 uncategorized orphans remain before a clean freeze)
```

---

## Honest Recommendation

Two items would close the gate cleanly if pursued next:
1. **The 98 uncategorized orphan targets** — likely fast, since the categorization pattern (dead vocabulary / headless-structural / target-ahead-of-semantic) already explained 28 of 126 using evidence already on hand; the FX MixOrGain/BW family (~40) is probably the same "target-ahead-of-semantic" pattern and could likely be bulk-categorized rather than individually investigated.
2. **The 169 UNKNOWN semantics** (83 in FX) — this is the population your instruction says is where genuine research should concentrate, once the above is exhausted.

Neither was pursued further in this pass, per "do not experiment yet, do not derive families yet" — this is a status report and control-path classification, not a claim that Phase 2D is finished.

---

**Status**: 908/908 semantics classified by control-path (not left generically "UNKNOWN"). 0 semantics declared `NO_TARGET`. 270/396 targets have confirmed semantic ownership, 28 more orphans explained by existing project evidence. Gate not yet fully closed — 169 UNKNOWN semantics and 98 uncategorized orphans remain, both honestly reported rather than glossed over.
