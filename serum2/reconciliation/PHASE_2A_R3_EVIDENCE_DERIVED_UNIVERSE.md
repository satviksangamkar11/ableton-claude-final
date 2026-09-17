# Phase 2A-R.3: Exploration-Evidence Reconstruction — Final Result

**Date**: 2026-09-16  
**Method**: Union of (a) atomic `records[]` entries recoverable from Git history and (b) semantic controls documented in section closure-ledger evidence but never itemized as atomic records.

---

## The Three Numbers, Explained

```
A = 516   JSON git-reconstructed (Phase 2A-R: commit 86dfde7 + diff to 79d74ae)
B = 712   Evidence-derived (A + FILTER/ENV/LFO itemized from their own closure ledgers)
C = 559+  Narrative claim (commit 4673086's prose; never computed from a JSON parse)
```

```
B - A = +196   Real, evidenced gap: FILTER (70) + ENV (36) + LFO (90) controls that were
               fully discovered, tested, and documented in closure ledgers, but never
               converted to atomic semantic_id records in records[].

C - A = +43    Unexplained. Does not match the real FILTER/ENV/LFO evidence magnitude (196).
               No combination of documented sub-counts reproduces 43 exactly.

B - C = +153   The evidence-derived universe EXCEEDS the narrative's own claim by 153 records.
               559+ was not an overstatement — if anything it understated what the
               exploration actually established.

A - B = -196   (inverse of above)
```

**Conclusion: None of the three prior candidate counts (474, 515/516, 559+) was the true evidence-derived universe. It is 712.**

---

## Why FILTER/ENV/LFO Were Missing From `records[]`

These three sections were closed on 2026-09-15 (dc707b6, 8388843/7c2edea, 315f092) — **before** the atomic `records[]` schema convention was consistently used for every subsequent section (MATRIX onward, starting with commit 986d470 on 2026-09-16). At the time FILTER/ENV/LFO were closed, their closure passes wrote fully-detailed, evidence-backed **aggregate summaries** into `meta.{section}_closure_ledger` — exact type counts, exact control lists, exact applicability sets, tooltip text, discovery method — but the individual records were never subsequently transcribed into `records[]` entries the way MACRO/OSC (and everything after MATRIX) were.

This is a **schema migration gap**, not a discovery gap. The underlying exploration is complete and rigorous — verified by the fact that each section's own internal arithmetic reconciles exactly against its own itemized evidence:

| Section | Ledger's own total claim | Itemized from same ledger | Match? |
|---------|---------------------------|------------------------------|--------|
| FILTER | 44 per filter (88 both) | 6 common + 20 type-specific + 9 structural + 3 routing + 6 generic-actions = 44 | ✅ Exact |
| ENV | 9 per envelope (36 total) | 5 common + 4 structural = 9 | ✅ Exact |
| LFO | 15 per LFO (90 for LFO1-6) | 14 core + 1 trigger mode = 15 | ✅ Exact |

Only the **atomic-record-bearing subset** (excluding the 3 MIX-owned routing cross-references and the 6 generic per-knob UI actions, which no other section itemizes as separate semantic_ids either — e.g. MACRO doesn't have a separate "MIDI Learn" record per macro) was itemized:

- FILTER: 6 + 20 + 9 = 35 per filter × 2 filters = **70**
- ENV: 5 + 4 = 9 per envelope × 4 envelopes = **36**
- LFO: 14 + 1 = 15 per LFO × 6 active LFOs (LFO7-10 headless, 0 each) = **90**

Total: **196 new atomic records**, all with full provenance back to their source closure ledger (`SERUM2_SEMANTIC_EVIDENCE_LEDGER.json`).

---

## Why the Narrative "559+" Does Not Match Either A or B

Commit 4673086 never parses the JSON (`git show --stat` confirms only a markdown file was added). Its "559+" claim is therefore **narrative estimation, not computation**.

Tested hypotheses for what the author might have meant by 43:

| Hypothesis | Arithmetic | Result | Matches 43? |
|---|---|---|---|
| Added FILTER's per-filter (not doubled) figure | 516 + 44 | 560 | Close, not exact |
| Added ENV's total alone | 516 + 36 + ~7 (rounding?) | ~552-559 | Speculative, unconfirmed |
| Added a rough "~40-50 more from FILTER/ENV/LFO closures" gesture | 516 + ~43 | 559 | Plausible but unverifiable — no field in any document literally states "43" |

**No documented arithmetic reproduces 559 exactly.** The most defensible conclusion: the author, aware that FILTER/ENV/LFO closures existed but were not yet itemized, added an approximate mental estimate rather than a computed figure. This is now moot — it is superseded by the actual computed evidence-derived count of 712.

---

## Anti-Pattern Check (Per Your Governing Rule)

- ❌ Did NOT treat 516 (last reconstructible JSON commit) as ground truth
- ❌ Did NOT treat 559 (narrative) as ground truth
- ❌ Did NOT assume the 43-record gap corresponds to 43 real missing semantics
- ✅ Traced every one of the 196 new records to its own specific closure-ledger evidence field (type applicability lists, tooltip text, discovery method) — every record in `SERUM2_SEMANTIC_EVIDENCE_LEDGER.json` carries `evidence_origin`, `discovery_commit`, and `closure_report` provenance
- ✅ Verified each section's itemization against the ledger's own stated total (44/9/15) before accepting it — all three reconciled exactly
- ✅ Left the 43-record gap in the narrative as **unexplained**, not force-fit to a plausible story

---

## Deliverables Produced

| File | Contents |
|------|----------|
| `SERUM2_SEMANTIC_INVENTORY_EVIDENCE_DERIVED.json` | Final canonical file: 712 records, 0 duplicates, all 14 sections represented atomically |
| `SERUM2_SEMANTIC_EVIDENCE_LEDGER.json` | Per-record provenance: evidence_origin, discovery_commit, closure_report, inventory_status |
| `SERUM2_INVENTORY_HISTORY.json` / `_DIFF.json` | (From Phase 2A-R) Full Git timeline and diffs |
| `SEMANTIC_FREEZE_BOUNDARY.md` | (From Phase 2A-R) Freeze commit vs. JSON-state analysis |
| `SERUM2_SEMANTIC_COUNT_RECONCILIATION.md` | (From Phase 2A-R) 474/515/516/559 comparison table (superseded by this document's 712) |

---

## Final Evidence-Derived Universe

```
TOTAL: 712 records
  VERIFIED:                 689  (96.8%)
  PROVEN_NOT_USER_CONTROL:   17  (2.4%)
  UNVERIFIED_CANDIDATE:       6  (0.8%)

By section:
  FX:                173   MIXER:    66   ARP:     49   MACRO:   48
  LFO:                90   BROWSER:  41   MATRIX:  39   GLOBAL:  32
  FILTER:             70   ENV:      36   CLIP:    28   GLOBAL_KEYBOARD: 21
  OSC:                11   VOICE:     8

0 duplicate semantic_ids. All 14 sections now atomically represented.
```

---

## Remaining Caveat: OSC Section — Checked, NOT Itemized (Different Schema)

OSC was checked (not skipped). `meta.osc_closure_ledger` exists but has a **fundamentally different structure** than FILTER/ENV/LFO:

- `closure_pass_2026_09_15_param44_55_validation`: disposition of 165 raw VST3 fields (55 per oscillator × 3) into technical vs. semantic
- `closure_pass_2026_09_15_semantic_target_reconciliation`: reports **"43 distinct control types"** — a de-duplicated count of control *kinds* across all 5 oscillator instances (SUB/OSC1/OSC2/OSC3/NOISE), NOT a clean "N controls × 5 instances" multiplier like FILTER's "44 per filter." The 5 instances are NOT structurally identical (only OSC1 has Wavetable-related fields, per the source data; SUB/NOISE are simpler).

Of the 43 types: 35 are "genuine semantic gaps needing targets," 2 are `PROVEN_NOT_USER_CONTROL`, and the remaining ~6 don't cleanly sum in the ledger's own numbers (`resolved_user_facing: 38` + `proven_not_user_control: 2` = 40, not 43 — a **second internal arithmetic inconsistency**, smaller than the earlier MATRIX one but real).

A separate, more detailed technical-level inventory exists per-oscillator (`A_OSC1_INVENTORY_DISCOVERED.json`, `A_OSC2_INVENTORY_DISCOVERED.json` — 55 raw VST3-field entries each, e.g. `OSC1.Enable` / `A Enable` / index 20 / `BOOLEAN` / `CAUSAL_VERIFIED`), but this is a **target-level schema** (VST3 field + mutation class + controllability), not the semantic-record schema (`semantic_id` + `label` + `control_type` + `conditional_visibility` etc.) used everywhere else. Converting it correctly requires:
1. Filtering out the technical-only fields (already flagged `TECHNICAL_ONLY_FIELD` / category F)
2. Mapping surviving genuine-semantic entries to which of the 5 oscillator instances they actually apply to (not uniform)
3. Resolving the 3-record internal arithmetic gap (43 vs. 40) against source evidence before accepting either number

**I did not fabricate this itemization.** Doing it with the same rigor as FILTER/ENV/LFO is a distinct task, not a five-minute extension of this pass — it needs the per-instance applicability determined from evidence, not assumed. Reported honestly as unresolved rather than folded into 712 or silently left at 11.

---

## Other Caveats

1. **MACRO's internal arithmetic** was not independently re-verified in this pass — the JSON's 48 MACRO records match your statement that "the Macro exploration ultimately produced 48 records," so it appears already reconciled, but was not re-derived from a separate closure report here.

2. **The 3 UNVERIFIED_CANDIDATE MPE menu items and MACRO.SYS.RENAME_MECHANISM** carry forward unchanged; P2/non-blocking disposition is unaffected by this itemization.

---

## Recommended Next Step

```
712  = current evidence-derived total (FILTER/ENV/LFO itemized, verified exact)
 +?  = OSC itemization gap (somewhere between 0 and ~32: 43 types claimed vs. 11
       already-atomic records present, minus technical/non-instance-multiplied nuance)
```

Before freezing the semantic count: resolve OSC using its own source evidence (`A_OSC1/2_INVENTORY_DISCOVERED.json` + the ledger's disposition table), applying the same per-record provenance discipline used for FILTER/ENV/LFO. Also worth a quick check: does `A_OSC1_ROUTE_FAMILY_MATRIX.json` / `A_OSC2_ROUTE_FAMILY_MATRIX.json` (seen in the earlier file listing) resolve the per-instance applicability question directly, avoiding re-derivation from scratch.

**Only after OSC is resolved (itemized, or explicitly and defensibly excluded with reason) should the semantic count be frozen** and Phase 2C (normalization against the 290 targets) begin.

---

**Status**: PHASE 2A-R.3 SUBSTANTIALLY COMPLETE. FILTER/ENV/LFO itemization is exact and verified (712 total). OSC is checked but explicitly left unresolved — different schema, real internal arithmetic gap (43 vs 40), requires dedicated reconciliation against its own source files before the semantic count can be frozen. Phase 2C remains blocked.
