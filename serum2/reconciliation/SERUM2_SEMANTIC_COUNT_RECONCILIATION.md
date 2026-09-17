# Serum 2 Semantic Count Reconciliation

**Date**: 2026-09-16  
**Method**: Git-history reconstruction (Phase 2A-R), not narrative/reported counts

---

## Full Count Table

| Source | Commit | Parse | Records | VERIFIED | PROVEN_NOT_USER_CONTROL | UNVERIFIED_CANDIDATE | Difference from reconstructed freeze |
|--------|--------|-------|---------|----------|--------------------------|------------------------|----------------------------------------|
| Reported audit (narrative) | 4673086 | — (never parsed JSON) | 559+ | 528+ | 24+ | 4 | **+43** |
| First multi-section state | 986d470 | PASS | 438 | 417 | 15 | 6 | −78 |
| VOICE closed | f9a8155 | PASS | 443 | 421 | 16 | 6 | −73 |
| GLOBAL closed | 1cfcb74 | PASS | 474 | 451 | 17 | 6 | −42 |
| GLOBAL correction (earlier session's "v1.0.0") | 3716ee5 | PASS | 474 | 451 | 17 | 6 | −42 |
| BROWSER closed (**last valid JSON in repo**) | 86dfde7 | PASS | 515 | 492 | 17 | 6 | −1 |
| Cross-system + G1-G10 (**corrupted blob**) | 79d74ae | FAIL (JSON syntax error) | — | — | — | — | — |
| **Cross-system + G1-G10 (RECONSTRUCTED via diff)** | 79d74ae-R | PASS (reconstructed) | **516** | **493** | 17 | 6 | **0 (baseline)** |
| Corrected CS IDs | 211c27b | — (doesn't touch JSON) | — | — | — | — | — |
| **Declared freeze (narrative only)** | **4673086** | — (doesn't touch JSON) | **559+** (asserted) | 528+ (asserted) | 24+ (asserted) | 4 (asserted) | **+43 unaccounted** |

---

## Authoritative Result

```
SOURCE-DERIVED, JSON-VERIFIABLE SEMANTIC UNIVERSE AT FREEZE BOUNDARY:

  Base:            commit 86dfde7  (515 records, valid JSON, SHA256 156235f7...)
  Applied diff:     86dfde7 -> 79d74ae  (git diff, textually verified, +1 record, ~1 modified)
  Reconstructed:    516 records
  File:             SERUM2_SEMANTIC_INVENTORY_RECONSTRUCTED.json
  File SHA256:      4dbcbd84775987da60546c20827998b08621a6598a02bc0f1a9af948e36b2f1b

  Status distribution:
    VERIFIED:                 493
    PROVEN_NOT_USER_CONTROL:   17
    UNVERIFIED_CANDIDATE:       6
    TOTAL:                    516

  Unique semantic_ids:  516  (0 duplicates)
  Sections represented:  11 of 14 declared sections
    (ARP, BROWSER, CLIP, GLOBAL, GLOBAL_KEYBOARD, MACRO, MATRIX, MIXER, OSC, VOICE, FX)
```

---

## Discrepancy: 559+ (Reported) vs. 516 (Source-Derived) = +43 Unaccounted

**Root cause identified, not fully resolved**:

1. **Commit 4673086 (the narrative freeze declaration) never parses or reads the JSON file.** It writes hand-authored prose counts into a markdown report. This is confirmed by `git show --stat 4673086` showing only a markdown file was added — zero touches to `SERUM2_SEMANTIC_INVENTORY.json`.

2. **FILTER, ENV, LFO sections were never itemized as individual `semantic_id` records** in the `records[]` array at ANY point in git history. They exist only as *aggregate closure-ledger summaries* nested under `meta.filter_closure_ledger`, `meta.env_closure_ledger`, `meta.lfo_closure_ledger`, containing prose/structured counts like:
   - FILTER: "44 distinct semantic controls per filter, 88 total both filters"
   - ENV: "9 controls × 4 envelopes = 36 total control instances"
   - LFO: "15 controls × 6 active LFOs + 0 × 4 headless = 90 total"

   These aggregate figures (88 + 36 + 90 = 214) were evidently never converted into atomic, reconcilable `semantic_id` rows. If the 559+ figure informally added some/all of these aggregate counts on top of a `records[]` count, the arithmetic still doesn't close cleanly:
   ```
   516 (records[]) + 88 (FILTER) = 604   (exceeds 559)
   516 + 36 (ENV alone) = 552             (close to 559, but arbitrary to isolate one section)
   ```
   No combination reproduces exactly 559 from documented aggregate figures. **This confirms the 559+ figure was not computed by any traceable arithmetic — it is an unverified narrative estimate.**

3. **This is the exact REPORTED-vs-SOURCE-DERIVED contamination flagged before this reconstruction began.** The 559+ number was carried forward across multiple audit documents (Phase 3 G1-G10, FINAL_STATUS_RECONCILIATION) without ever being re-derived from a successful JSON parse, because no successful JSON parse existed after 86dfde7.

---

## Anti-Shortcut Compliance Check

- ❌ Did NOT conclude "474 = complete" (474 was an intermediate, pre-BROWSER state, not even the last valid JSON)
- ❌ Did NOT conclude "559 = complete" (unverifiable against any parseable JSON state)
- ❌ Did NOT conclude "current corrupted file + comma repair = freeze state" (never applied a blind repair; instead, reconstructed via `git diff` with full provenance per changed record)
- ✅ Result is Git-history-derived: base commit + reviewed diff + provenance tag on every changed/added record

---

## Outstanding Gap: FILTER / ENV / LFO Schema Mismatch

This is a **separate, unresolved finding**, distinct from the JSON corruption:

| Section | Aggregate count (from closure ledger prose) | Individual `records[]` entries | Status |
|---------|-----------------------------------------------|----------------------------------|--------|
| FILTER | 88 (44 × 2 filters) | **0** | Not itemized anywhere in git history |
| ENV | 36 (9 × 4 envelopes) | **0** | Not itemized anywhere in git history |
| LFO | 90 (15 × 6 active) | **0** | Not itemized anywhere in git history |

These ~214 semantic controls are **real** (verified via direct UI testing per the closure ledger prose, which is detailed and evidence-backed) but were **never converted to the atomic `semantic_id` schema** used by every other section. They cannot be reconciled against `targets.py` at the individual-control level until this conversion happens.

**This must be resolved before Phase 2D (bidirectional reconciliation)**, since FILTER/ENV/LFO collectively represent a large fraction of the semantic universe and of the 290 existing targets (FILTER: 22 targets, ENV: 16 targets, LFO: 50 targets = 88 targets, or 30% of all targets, currently have NO atomic semantic_id counterpart to reconcile against).

---

## Revised Phase State

```
PHASE 2A-R — Git History Reconstruction
    ✅ COMPLETE
    - Full commit timeline built (13 commits, 12 valid + 1 corrupted-but-diff-recovered)
    - Reconstructed inventory: 516 records, SHA256 documented
    - Freeze boundary determined: JSON-verifiable state ≠ narrative declaration (+43 gap, unexplained)
    - Semantic lineage ledger built (519 unique IDs ever seen, 516 present at freeze, 3 re-homed)

PHASE 2A-SCHEMA-GAP — FILTER/ENV/LFO Itemization
    ⚠️ NEW BLOCKING FINDING
    - 214 semantic controls (FILTER 88, ENV 36, LFO 90) exist only as aggregate
      closure-ledger prose, never itemized as semantic_id records
    - Must be itemized before bidirectional reconciliation can cover these sections

PHASE 2B — Target Extraction
    ✅ COMPLETE (290 targets, unaffected by this finding)

PHASE 2C — Normalization
    🚫 BLOCKED until FILTER/ENV/LFO itemization resolved (or explicitly scoped out)

PHASE 2D — Reconciliation
    🚫 BLOCKED

PHASE 2E — Gap Audit
    🚫 BLOCKED

PHASE 2F — Representation Families
    🚫 BLOCKED

PHASE 3 — Deep Experiments
    🚫 BLOCKED
```

---

## Recommendation

Two paths forward, both legitimate, requiring a decision:

**Path A — Itemize FILTER/ENV/LFO now**: Convert the aggregate closure-ledger prose into atomic `semantic_id` records (e.g., `FILTER1.CUTOFF`, `FILTER1.TYPE_SPECIFIC.FAT`, `ENV1.HOLD`, `LFO1.RATE`, etc.), using the closure ledger's own documented evidence (types, ranges, applicability lists) as the source — no new UI probing required, since the ledger already contains the full enumerated evidence. This is a text-only normalization task, not a discovery task.

**Path B — Scope Phase 2D to the 516 itemized records only**, explicitly excluding FILTER/ENV/LFO as a documented, deferred gap, and reconcile those three sections separately once itemized.

Both are text-only, no-UI-probing options. Recommend **Path A**, since the evidence already exists in the closure ledgers and itemization is mechanical (parsing structured JSON, not new discovery) — but this is a scope decision for the user to confirm before proceeding.

---

**Status**: PHASE 2A-R COMPLETE. New blocking finding surfaced (FILTER/ENV/LFO schema gap). Awaiting decision on Path A vs. Path B before Phase 2C resumes.
