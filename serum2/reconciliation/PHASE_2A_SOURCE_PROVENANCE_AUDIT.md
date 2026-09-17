# Phase 2A: Source Provenance Audit

**Date**: 2026-09-16  
**Issue**: Malformed JSON in current SERUM2_SEMANTIC_INVENTORY.json  
**Discovery**: Line 8 missing comma after `last_modified` field (after `phase_1_reconciliation_date` addition)

---

## JSON Corruption Analysis

### Current State (HEAD / commit 4673086)
```
File: serum2/SERUM2_SEMANTIC_INVENTORY.json
Version: 1.2.0-CROSS-SYSTEM-RECONCILIATION-PHASE-1
Parser status: ❌ FAIL
Error: JSONDecodeError at line 8 column 5
Reason: Missing comma after "phase_1_changes" line
```

### Root Cause (Git History)

**Commit 3716ee5** (GLOBAL closure correction)
- Version: 1.0.0-GLOBAL-CLOSED
- Parser: ✅ VALID JSON
- Date: 2026-09-16

**Commits 3716ee5 → 79d74ae**: Upgrade to v1.2.0-CROSS-SYSTEM-RECONCILIATION-PHASE-1
- Introduced: `"phase_1_reconciliation_date": "2026-09-16"`
- Introduced: `"phase_1_changes": "MPE_OWNERSHIP_RECONCILIATION..."`
- **Error**: Missing comma before "sections_complete" after "phase_1_changes" string

**Commit 79d74ae** (Phase 2–Phase 3 Complete)
- Version: 1.2.0-CROSS-SYSTEM-RECONCILIATION-PHASE-1
- Parser: ❌ INVALID JSON
- Contains the corruption

**Commits 79d74ae → 4673086** (and all subsequent)
- Corruption persists unchanged
- No fix applied

---

## Extraction Decision

**Policy**: Do not repair malformed JSON. Use last known-valid version before corruption.

**Selected Source**: Commit 3716ee5
- File path: serum2/SERUM2_SEMANTIC_INVENTORY.json
- Commit hash: 3716ee5 (GLOBAL closure correction: resolve mislabeled P1, log MPE ownership as P2)
- Commit date: 2026-09-16
- Inventory version: 1.0.0-GLOBAL-CLOSED
- Parser status: ✅ VALID JSON
- Provenance: Last clean version before v1.2.0 corruption

---

## Why This Version?

1. **Last known-valid**: All attempts to parse v1.2.0 fail; v1.0.0 parses successfully
2. **Same date as freeze**: Commit 3716ee5 is also 2026-09-16, same day as freeze
3. **Authoritative**: Used for GLOBAL closure audit, part of Phase 1 discovery closure chain
4. **Proxies for frozen state**: While not the exact v1.2.0 frozen version, v1.0.0 represents semantic inventory at freeze date with known-good JSON

**Caveat**: v1.0.0 may not include updates applied in v1.2.0 (phase_1_reconciliation_date, phase_1_changes fields, any records added between 3716ee5 and 79d74ae). This will be documented as a VERSION DISCREPANCY when comparing against REPORTED count.

---

## Extraction Plan

1. **Parse commit 3716ee5**:
   - `git show 3716ee5:serum2/SERUM2_SEMANTIC_INVENTORY.json`
   - Extract all semantic records
   - Count by section, status
   - Record file hash

2. **Document discrepancy**:
   - Reported count: 559+ (from FINAL_STATUS_RECONCILIATION_AND_G1_G10_HONEST.md, based on v1.2.0)
   - SOURCE-DERIVED count: N (from v1.0.0 parse)
   - Difference: N - 559 = ? (likely negative, since v1.0.0 is earlier)

3. **Flag for reconciliation**:
   - If version difference exists, document it
   - Use SOURCE-DERIVED count for Phase 2C/2D
   - Mark reported 559+ as "derived from later (corrupted) version"

---

## Next Action

Execute Phase 2A with commit 3716ee5 as authoritative source, documenting version variance if it exists.

**Status**: AUDIT GATE COMPLETE  
**Decision**: Use v1.0.0 (commit 3716ee5) for source-derived extraction  
**Next**: Parse and count records from clean JSON
