# Phase 2C: Normalization Audit

**Date**: 2026-09-16  
**Scope**: Purely mechanical normalization. No target mappings, no semantic conclusions.

---

## Correction Surfaced During Normalization

**Target count corrected: 290 → 255.**

Phase 2B's original 290 was a raw regex match against `targets.py` source text. This does not account for Python dict-literal semantics: when the same key string appears twice in a dict literal, the later occurrence silently overwrites the earlier one at construction time — no error, no warning.

```
Live dict size (from serum2.compiler.targets import SEMANTIC_TARGETS; len(...)):  255
Raw regex text matches:                                                          290
Duplicate source lines:                                                           35
```

All 35 duplicates were checked for whether the overwrite changes anything functionally:

```
Duplicates with DIFFERENT capability_key (real semantic change): 0
Duplicates with SAME capability_key (harmless redundant source lines): 35
```

**No functional bug** — the 35 duplicate lines are dead/redundant source text (mostly in an "Additional FX effects" block later re-declared verbatim in a "PHASE FX-FULL: Complete FX parameter coverage" block), all mapping to identical `capability_key` values. But the *count* was wrong, and is now corrected: **255 unique targets**, not 290.

---

## SERUM2_SEMANTIC_NORMALIZED.json

908 records → normalized canonical form. No records dropped, added, or reinterpreted — purely a field-projection exercise.

### Value Domain Distribution (mechanically inferred from `control_type`)

| Value domain | Count |
|---|---|
| UNSPECIFIED | 322 |
| SCALAR_UNBOUNDED | 264 |
| STRUCTURAL_ACTION | 203 |
| STRUCTURAL_SELECTION | 42 |
| BOOLEAN | 39 |
| ENUM | 29 |
| SCALAR_RANGE | 9 |

**Note on UNSPECIFIED (322 records, 35% of total)**: this is not a defect — it reflects that most records' `control_type` field in the source inventory was never populated with a value this normalization pass recognizes (many closure-ledger-itemized records used free-text `control_type` values like `"unknown"` or left it as a category label rather than a strict enum). This is a **known gap for Phase 2D to resolve**, not silently smoothed over here. A more precise domain classification will likely require re-deriving `value_domain` from `value_range`/`options`/`label` content on a case-by-case basis during reconciliation, not guessed at in this mechanical pass.

---

## SERUM2_TARGET_NORMALIZED.json

255 unique targets → normalized canonical form.

### Parameter Kind Distribution (255, post-dedup)

| Parameter kind | Count |
|---|---|
| VST3_HOST_FIELD | 218 |
| ROUTING_SLOT_FIELD | 21 |
| VST3_PLAIN_PARAM | 16 |

### Target Source Distribution (255, post-dedup)

| Target source | Count |
|---|---|
| SYNTH_PARAMETER | 154 |
| FX_PARAMETER | 96 |
| MATRIX_ROUTE | 5 |

### Explicit Gap: Contract-Level Fields Are UNKNOWN

`targets.py` itself is, by its own docstring, "a dumb alias only: name → capability_key. No structural knowledge, no RequiredContext, no admission decision." The following fields **cannot be populated mechanically from targets.py alone**:

```
host_parameter_name    UNKNOWN
value_domain            UNKNOWN
normalized_domain       UNKNOWN
mutation_path           UNKNOWN
read_supported          UNKNOWN
write_supported         UNKNOWN
automation_supported    UNKNOWN
persistent               UNKNOWN
existing_evidence        UNKNOWN
```

These live in `CapabilityContract` objects, built by `capability_contract.build_all_contracts(claim_engine)`. No persisted contract store (pickle, JSON export, or similar) exists anywhere in the repository — `build_all_contracts` requires a live `claim_engine` input that isn't available as a static artifact.

**This is not a shortcut around Phase 2D — it's an honest boundary.** Phase 2D has two options, not resolved here:
1. Build the claim_engine/contracts live before attempting field-level reconciliation, or
2. Reconcile at the `target_id` ↔ `capability_key` level only (which is all that's mechanically available), treating contract-level operational proof (read/write/automation/persistence) as a separate, later verification layer — consistent with the project's own established distinction between semantic discovery, target-vocabulary existence, and operation implementation.

---

## What Phase 2C Deliberately Did Not Do

- Did not map any of the 908 semantics to any of the 255 targets
- Did not classify any relationship as EXACT/ONE_TO_MANY/MANY_TO_ONE/NO_TARGET/UNKNOWN
- Did not resolve the UNSPECIFIED value-domain records
- Did not attempt to populate target contract-level fields by inference or guessing

All of that is explicitly Phase 2D's work.

---

## Deliverables

| File | Contents |
|---|---|
| `SERUM2_SEMANTIC_NORMALIZED.json` | 908 records, canonical field projection |
| `SERUM2_TARGET_NORMALIZED.json` | 255 unique targets (corrected from 290), canonical field projection, contract-level fields marked UNKNOWN |
| `PHASE_2C_NORMALIZATION_AUDIT.md` | This document |

---

## Updated Phase State

```
PHASE 2C  Normalization                    ✅ COMPLETE
              908 semantics normalized
              255 targets normalized (corrected from 290)
              1 count-correction surfaced and explained

PHASE 2D  Target reconciliation             ▶ NEXT
              908 semantics x 255 targets
              Must resolve: contract-level UNKNOWN fields (build-or-defer decision)
              Must resolve: 322 UNSPECIFIED value-domain records

PHASE 2E  Gap / operation audit            🚫
PHASE 2F  Representation families          🚫
PHASE 3   Deep behavioral experiments      🚫
```

---

**Status**: Phase 2C complete. Ready for Phase 2D once the contract-availability decision (build live vs. defer to capability_key-level reconciliation) is made.
