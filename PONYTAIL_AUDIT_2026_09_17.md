# Ponytail Audit Report
**Date:** 2026-09-17  
**Scope:** serum2/ codebase (75K lines)  
**Mode:** Full (ponytail-audit, no fixes applied)

---

## Findings (Ranked by Impact)

### 1. Dead Research Scaffolding: step_5_*.py (7 files, 3,228 lines)

**Category:** `delete` — unused experimental code from research phase

| File | Lines | Status |
|------|-------|--------|
| step_5_11_e2e_teaching_proof.py | 624 | UNUSED (0 imports) |
| step_5_12_authority_boundary_proof.py | 556 | UNUSED (0 imports) |
| step_5_6_persistence_proof.py | 503 | UNUSED (0 imports) |
| step_5_3_source_acquisition.py | 428 | UNUSED (0 imports) |
| step_5_4_proposition_extraction.py | 422 | UNUSED (0 imports) |
| step_5_5_knowledge_normalization.py | 404 | UNUSED (0 imports) |
| step_5_4_q_repaired_extraction.py | 291 | UNUSED (0 imports) |

**Location:** `serum2/knowledge/`  
**Rationale:** Part of knowledge-layer discovery pipeline (steps 5.3–5.12); superseded by step_6_* implementations and producer infrastructure  
**Replacement:** None  
**Impact:** -3,228 lines of pure scaffolding

---

### 2. Dead A3 Test Scaffolding (4 files, 1,678 lines)

**Category:** `delete` — obsolete phase A3 qualification tests

| File | Lines | Status |
|------|-------|--------|
| a3_step_18_tests.py | 481 | UNUSED (0 imports) |
| a3_step_19_tests.py | 442 | UNUSED (0 imports) |
| a3_step_20_tests.py | 361 | UNUSED (0 imports) |
| a3_family_bulk_tests.py | 394 | UNUSED (0 imports) |

**Location:** `serum2/qualification/`  
**Rationale:** Qualification scaffolding from phase A3 (steps 18–20); superseded by current qualification pipeline  
**Replacement:** None  
**Impact:** -1,678 lines of dead test code

---

### 3. Incomplete: Hardcoded Placeholders in compound_operations.py

**Category:** `shrink` — stubbed implementation with TODOs

**File:** `serum2/operations/compound_operations.py:85-88`  
**Lines:** 560 total (6 TODO comments, hardcoded values)

```python
route_struct = {
    "destModuleID": 0,  # TODO: resolve from dest_param semantic target
    "destModuleParamID": 3,  # TODO: resolve from dest_param
    "destModuleParamName": "kParamFreq",  # TODO: resolve from dest_param
    "destModuleTypeString": "VoiceFilter",  # TODO: resolve from dest_param
    ...
}
```

**Issue:** Cannot compile real modulation routes; uses hardcoded Filter/Freq values regardless of semantic target  
**Replacement:** Implement semantic-target-to-VST3-module resolution, or remove until completed  
**Impact:** Blocks real modulation route compilation (used by registry)  
**Status:** INCOMPLETE, not dead (actively registered but non-functional)

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Dead scaffolding (step_5_*) | 3,228 lines |
| Dead tests (A3_*) | 1,678 lines |
| Total dead code | **4,906 lines** |
| **Net lines removable** | **-4,906 lines** |
| Incomplete modules (not deleted) | 1 (compound_operations.py) |
| Total Python files scanned | 500+ |
| Unused imports/abstractions | 0 (no Base/Abstract/Interface classes found) |
| Dead config files | 0 |

---

## Recommendations

1. **DELETE immediately (zero-risk):**
   - All 7 step_5_*.py files (research scaffolding, 3,228 lines)
   - All 4 A3_* test files (test scaffolding, 1,678 lines)
   - **Total cleanup: 4,906 lines**

2. **DEFER (separate task):**
   - compound_operations.py: Complete semantic-target resolution or remove function until implemented

---

## Codebase Health

✅ No speculative abstractions (Base/Abstract/Interface classes: 0)  
✅ No single-implementation factories or wrappers  
✅ No dead config/constants  
✅ No redundant layers

**Verdict:** Codebase is lean except for research scaffolding. Removing 11 unused files yields clean, focused code.

---

**Action Required:** User decision on whether to delete the 11 unused files.
