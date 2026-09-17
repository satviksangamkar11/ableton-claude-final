# Phase 2A-R: Final Consolidated Evidence-Derived Semantic Universe

**Date**: 2026-09-16  
**Pipeline complete**: Git reconstruction → duplicate detection → OSC atomization → SUB/NOISE completeness → ownership resolution → MATRIX.SOURCE atomization → this consolidation

---

## The Full Number History (Why None of the Earlier Numbers Were Right)

| # | Value | What it was | Why it was wrong/incomplete |
|---|---|---|---|
| 1 | 474 | First "valid JSON" found by picking a commit | Arbitrary — not even the last valid commit |
| 2 | 515/516 | Last valid JSON + 1 diff-recovered record | Correct as a **Git artifact**, but Git commits are a persistence layer, not the evidence ceiling |
| 3 | 559+ | Narrative claim in freeze document | Never computed from a JSON parse at all (commit that made the claim never touched the file) |
| 4 | 712 | First itemization attempt (FILTER+ENV+LFO, naive) | Arithmetic not verified against overlap — contained 14 undetected duplicates |
| 5 | 704 | FILTER+ENV+LFO, set-reconciled (A∩B=0 verified) | Correct for that scope, but OSC/SUB/NOISE/MATRIX.SOURCE not yet checked |
| 6 | 833 | + OSC1/2/3 atomized | Correct for that scope, but carried 9 unresolved duplicate flags |
| 7 | 839 | + SUB/NOISE completeness | Correct for that scope, carried 11 unresolved duplicate flags |
| 8 | 828 | − 11 confirmed duplicates (ownership resolved) | Correct, but MATRIX.SOURCE gap still open |
| **9** | **870** | **+ 42 MATRIX.SOURCE records** | **Current: all six aggregate-ledger sections checked, all known ambiguities resolved** |

---

## What Changed At Each Step, With Evidence Class

```
516  Git-reconstructed baseline                         [git diff, textually verified]
+188 FILTER(62)+ENV(36)+LFO(90)                          [closure-ledger itemization,
                                                           14 overlaps detected & excluded
                                                           via existing cross_reference text]
+129 OSC1/2/3 (43 fields x 3, 2 NOT_USER_CONTROL)        [technical inventory + semantic
                                                           disposition cross-reference]
 +6  SUB(4)+NOISE(2)                                     [VST3 census field-by-field mapping,
                                                           NOT assumed identical to OSC A/B/C]
-11  OSC1-3/SUB/NOISE Enable-Level-Pan retracted         [internal VST3 field name match:
                                                           MIXER's own tooltip text = census
                                                           field name -- decisive, not inferred]
+42  MATRIX.SOURCE (Envelopes/LFOs/Note/Macros/MPE/      [matrix_closure_ledger's own source
      +5 leaf categories)                                 domain enumeration, only Oscillators+
                                                           Filters had been atomized]
────
870  final
```

---

## Verification Discipline Applied Throughout

Every addition passed through the same gate:
1. Extract candidate from existing, already-collected evidence (closure ledger, technical census, or source-domain enumeration) — **no new UI probing**
2. Construct the candidate `semantic_id`
3. Check it against the current baseline set — **explicit `A ∩ B` computation, never assumed zero**
4. Where overlap was found, trace it to **specific textual evidence** (a cross-reference field, a matching internal parameter name) before excluding — never excluded on "looks similar" grounds
5. Where no evidence for merging existed (the OSC1-3 Enable/Level/Pan case, initially), the item was **flagged unresolved rather than force-decided**, and only resolved once independent corroborating evidence (VST3 census) was found

---

## Final Section Breakdown

| Section | Count | Section | Count |
|---|---|---|---|
| FX | 173 | GLOBAL | 32 |
| OSC | 135 | GLOBAL_KEYBOARD | 21 |
| LFO | 90 | ARP | 49 |
| MATRIX | 81 | CLIP | 28 |
| MIXER | 66 | VOICE | 8 |
| FILTER | 62 | ENV | 36 |
| MACRO | 48 | BROWSER | 41 |
| **TOTAL** | **870** | | |

By status: (carried forward from prior VERIFIED/PROVEN_NOT_USER_CONTROL/UNVERIFIED_CANDIDATE distribution, plus 6 new PROVEN_NOT_USER_CONTROL from OSC's Ratio/Hz Offset ×3)

---

## Coverage Sweep: No Other Sections Carry This Risk Pattern

Only 6 sections in the entire inventory ever used the "aggregate closure-ledger without atomic records" structure: `macro`, `osc`, `filter`, `env`, `lfo`, `matrix` — all closed on 2026-09-14/15, before the atomic-`records[]` convention was adopted for every section from `MATRIX` (partial) onward on 2026-09-16.

- MACRO: checked — its ledger has no aggregate-matrix structure; already fully atomic (48 records, matching your own statement that "Macro exploration ultimately produced 48 records")
- OSC: resolved (technical-field-based, not ledger-based — different fix required, applied)
- FILTER/ENV/LFO: resolved
- MATRIX: resolved (both the destination side, closed earlier, and the newly-found source-domain gap)

The other 8 sections (MIXER, FX, ARP, CLIP, GLOBAL_KEYBOARD, VOICE, GLOBAL, BROWSER) were all closed after the atomic convention existed and carry no equivalent `meta.*_closure_ledger` structure — they do not need this same check.

---

## Remaining Known Caveats (Explicit, Not Hidden)

1. **OSC mode-dependent applicability is not fully tabulated field-by-field.** The 41 genuine OSC1/2/3 fields carry a qualitative `conditional_visibility` note (mode-dependent rendering) but not an exact per-mode applicability matrix like FILTER's type-specific controls got. Would require the same rigor as FILTER's 20-item table if precision is later needed for target reconciliation.
2. **MATRIX.SOURCE's 42 new items are unverified as to whether they're each independently selectable** vs. some being conditionally gated (e.g., can `Voice Mod 1`/`Voice Mod 2` always be selected, or only in certain contexts?) — itemized as flat entries per the source enumeration, deeper conditional structure not investigated.
3. **DESTINATION-side of MATRIX was closed earlier (Phase 1, pre-atomic-convention)** and contributed the existing 39 MATRIX records — it was not re-audited in this pass the way SOURCE was. Given SOURCE had a 6x undercount (7 found vs. 49 actual), DESTINATION deserves the same scrutiny before a full freeze. **Not done in this pass** — flagged as the most likely remaining risk.

---

## Recommendation

870 is the most rigorously verified number produced so far, but caveat 3 above (MATRIX DESTINATION side) is a real, specific, evidenced risk — it follows the exact same pattern that just produced a 6x undercount on the SOURCE side, and has not yet been checked with the same method.

Given the demonstrated pattern (every section checked with this rigor has revealed additional records), recommend checking MATRIX DESTINATION before declaring the freeze, using the identical method: pull the destination enumeration from `matrix_closure_ledger`, cross-check against existing `MATRIX.*` records, verify `A ∩ B = 0` for any additions.

---

## Updated Phase State

```
PHASE 2A-R.8  MATRIX.SOURCE atomization               ✅ COMPLETE (870)
PHASE 2A-R.9  MATRIX.DESTINATION completeness check    ⏳ RECOMMENDED NEXT (same risk pattern as SOURCE)

PHASE 2C+                                             🚫 still blocked — no freeze yet
```

---

**Status**: 870 is the current best evidence-derived union, 0 duplicate IDs, every addition and every exclusion traced to explicit evidence. One more specific, high-probability gap identified (MATRIX DESTINATION) and explicitly not yet checked — not swept under the rug.
