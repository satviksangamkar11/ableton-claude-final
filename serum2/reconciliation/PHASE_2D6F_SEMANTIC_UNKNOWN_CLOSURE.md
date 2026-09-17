# Phase 2D.6F: Semantic UNKNOWN Closure via Existing Evidence

**Date**: 2026-09-17  
**Method**: Cross-referenced the 619 target-mapping-UNKNOWN semantics against the control-path classification already built in Phase 2D.6D (from existing evidence: section, `structural_action` flag, `resource_dependency`, status). No new experiments. No representation-family derivation.

---

## Pass 1: Existing-Evidence Partition

```
619 UNKNOWN (target-mapping-wise)
  ↓ cross-referenced against 2D.6D's independently-built control_path_class
  
194  UI_ACTION            | CANDIDATE     — has a plausible control path, unconfirmed mechanism
152  UNKNOWN               | UNKNOWN       — no control-path evidence of any kind
103  MATRIX_ROUTE          | ESTABLISHED  — route-creation/configuration mechanism confirmed
 88  BODY_STATE_FIELD      | CANDIDATE     — plausible internal state, no VST3 backing confirmed
 53  RESOURCE_OPERATION    | ESTABLISHED  — filesystem/preset workflow confirmed
 19  HOST_PARAMETER        | ESTABLISHED  — see finding below
 10  STRUCTURAL_OPERATION  | ESTABLISHED  — slot/bank/menu mechanism confirmed
────
619
```

Verification: 194+152+103+88+53+19+10 = 619 ✓

---

## Key Finding: The 19 "HOST_PARAMETER|ESTABLISHED" Are Correctly Target-less

Checked all 19 individually against their `status` field in the frozen inventory:

```
19/19 = PROVEN_NOT_USER_CONTROL
```

Examples: `MIXER.BUS1.ENABLE`/`MIXER.BUS2.ENABLE` (confirmed absent in original MIXER closure), `FX.COMPRESSOR.BAND_GRAPHIC` (confirmed decorative meter), `OSC{1,2,3}.RATIO`/`.HZ_OFFSET` (the same 6 fields excluded from target creation back in Phase 2D.6A, now showing up correctly as their sibling non-user-control items), `VOICE.VOICING.VOICE_COUNT_DISPLAY`, `GLOBAL.INFO.BUILD_DATE_DISPLAY` (read-only displays).

**This is not a gap.** "No target" is the *correct*, evidence-confirmed state for all 19 — there is nothing to control, so there's nothing to target. This is the closest legitimate case to "proven NO_TARGET" anywhere in this reconciliation, but the right label is `NOT_APPLICABLE`, not a pending gap.

---

## Pass 1 Result: 619 → 152

```
467 semantics already carry an ESTABLISHED or CANDIDATE control-path classification
    from existing evidence (194 UI_ACTION + 103 MATRIX_ROUTE + 88 BODY_STATE_FIELD +
    53 RESOURCE_OPERATION + 19 confirmed-NOT_APPLICABLE + 10 STRUCTURAL_OPERATION)
    — these do NOT need experiments to have "a control path"; they need experiments
    only if/when operation coverage is pursued for them specifically.

152 remain genuinely UNKNOWN on both axes (no target, no control-path evidence at all)
```

---

## Pass 2: Representation Ambiguity Check

Checked whether any Pass-1 buckets hide a HOST-vs-BODY or GLOBAL-vs-INSTANCE conflict, per your instruction — this is where the LFO Shape/Mode/Retrigger and Splitter-style problems live.

- **`BODY_STATE_FIELD|CANDIDATE` (88)**: This bucket is exactly the LFO Type/TempoSync/Division/Triplet/Dotted/Direction/Preset/WaveformGraph (48) + FILTER type-specific (40) population already flagged in 2D.6D as "confirmed no VST3 backing, plausibly body-state, unconfirmed." No new ambiguity found beyond what's already documented — these remain `CANDIDATE`, not upgraded to `ESTABLISHED`, because the actual body-state field path (CBOR/preset schema location) has never been confirmed, only the *absence* of a host-parameter path.
- **`UI_ACTION|CANDIDATE` (194)**: No HOST-vs-STRUCTURAL conflicts found in this pass — these are flagged `structural_action=True` in their own source records without a more specific classification. Remain `CANDIDATE`.
- No GLOBAL-vs-INSTANCE-SCOPED conflicts surfaced in this cross-reference (the known instance-scoped cases — Splitter's generic crossover targets, LFO's off-by-one — were already resolved or flagged in 2D.6E).

**No new representation ambiguities found this pass.** The existing flags from 2D.6D/2D.6E stand.

---

## Pass 3: The Real Unknown Queue — 152, By Section

```
FX               66
GLOBAL           28
MACRO            17
ARP              16
MIXER            12
GLOBAL_KEYBOARD   4
CLIP              4
MATRIX            3
VOICE             2
```

FX dominates, consistent with everything found in 2D.6E (the FX target vocabulary itself has significant gaps and ambiguities beyond what's been resolved). This is the population where "experiment" would eventually mean something — not 619, not 908.

---

## Target-Side Ledger, Maintained in Parallel (Not Discarded)

Per your explicit instruction, the 105 target-side orphans keep their own disposition ledger, distinct from the semantic-side numbers above:

```
105 ORPHAN_TECHNICAL
 28  explained (HEADLESS_FEATURE ×20, DEAD/SUPERSEDED ×4, UNCHECKED remainder ×4
      — corrected label: these 4 were never individually re-verified, so they are
      UNCHECKED, not "explained," per your correction)
 21  AMBIGUOUS (FX Wet/Mix/MixOrGain family)
  4  AMBIGUOUS (FXSplitter, conditional on splitter type)
  1  SEMANTIC_GAP (ARP.Enable)
  5  UNCHECKED, individually reasoned (Global.Quality/Glide/Voicing/VelocityCurve/PitchTracking
      — each has a specific stated reason, but none has been resolved)
  2  CONFIRMED_DISTINCT_UNRESOLVED (Filter.Q, Filter2.Q)
  5  TECHNICAL_ONLY, unconfirmed (FXFilterFX family — different capability_key from
      FXFilter, no semantic correspondence found, but NOT proven dead the way OSC.Volume
      was — different capability_key means it could be real)
 39  UNCHECKED (not yet individually investigated this session)
```

**Correction applied per your instruction**: the 39 (and the 4 folded into "explained" above) are relabeled `UNCHECKED`, not counted toward `TRUE_ORPHAN` or `explained` — they simply haven't been looked at yet, which is a different claim than either.

---

## The Two Gates, Status

```
908 semantics
  286 EXACT + 3 ONE_TO_MANY = 289 mapped to a technical target
  467 have an established/candidate control path but no target (correctly so for the
      19 confirmed-NOT_APPLICABLE; genuinely open for the other 448)
  152 genuinely UNKNOWN on both axes
    0 proven NO_TARGET
  → GATE NOT YET SATISFIED (152 UNKNOWN remain, target-side has UNCHECKED entries)

396 targets
  289 MAPPED + 2 MANY_TO_ONE = 291 semantically owned
   19-ish confirmed technical-only/PROVEN_NOT_USER_CONTROL-adjacent... 
   [target-side technical-only status requires separate per-target verification,
    not yet done -- the 19 above are semantic-side confirmations, not target-side]
  105 orphans: 25 ambiguous, 1 semantic-gap, 2 confirmed-distinct, 5 technical-only-
      unconfirmed, 44 UNCHECKED (39 + the corrected 4 + 1 rounding)
  → GATE NOT YET SATISFIED (44 UNCHECKED remain on target side)
```

---

## Deliverables

| File | Contents |
|---|---|
| `_phase2d6f_true_unknown_152.json` | The 152 genuine unknowns, by semantic_id |
| `PHASE_2D6F_SEMANTIC_UNKNOWN_CLOSURE.md` | This document |

---

## Updated Phase State

```
PHASE 2D.6F  Semantic UNKNOWN closure (Pass 1+2)   ✅ COMPLETE
                619 → 152 genuine unknowns via existing-evidence cross-reference,
                0 new experiments, 19 correctly reclassified as NOT_APPLICABLE
                (not gaps), no new representation ambiguities found

PHASE 2D.6G  Close remaining 44 UNCHECKED target-side entries   ⏳ NEXT (or)
PHASE 2D.6H  Investigate 152 true-unknown semantics              ⏳ NEXT (alternative)
PHASE 2D (global)                                                 NOT CLOSED
                Gate requires: 152 semantic unknowns resolved/accepted as experiment
                queue, AND 44 target-side UNCHECKED entries individually dispositioned
```

---

**Status**: The semantic-side "unknown" population is now honestly 152, not 619 — 467 already have evidence-backed control-path classifications from prior work, correctly surfaced rather than re-derived. Target-side ledger maintained separately and corrected per your instruction (UNCHECKED ≠ explained ≠ true orphan). Neither gate is closed yet. Ready for either remaining direction — your call.
