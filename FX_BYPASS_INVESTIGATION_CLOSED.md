# FX Bypass Investigation: CLOSED

**Status:** Findings applied; control-surface gap marked UNRESOLVED  
**Date:** 2026-09-13  
**Authority:** Authoritative investigation via `step15_2_8_fxdistortion_enable_discovery.py`

---

## Summary

After systematic investigation, **the FX bypass mechanism was NOT FOUND** in any of the expected locations. The implementation has been corrected to stop conflating BYPASS (unknown mechanism) with REMOVE (proven array topology operation).

---

## Investigation Findings

### What Was Searched

**Not found:**
- ❌ `FXRack0.FX[i].FXDistortion.plainParams.kParamEnable` (corpus: 515/516 None, 1 real instance lacks this key)
- ❌ `FXRack0.plainParams` (empty across all 997 corpus bodies)
- ❌ VST3 parameter enumeration (2623 params searched, no per-unit FX enable found)
- ❌ `type` field (identified as discriminant, not bypass flag)

**What remains unexplored:**
- ❓ `FXRack0.FX[i].flex` (structurally present but semantically opaque)

### Explicit Conclusion (Verbatim)

> "We searched the currently understood representation (body fields, FXRack-level fields, the type discriminant, and the full host parameter list) and did not find an Enable mechanism for an individual FX unit. This does NOT mean Serum has no such mechanism, and does NOT mean Enable is unsupported — flex remains unresolved, so both stronger claims are premature."

---

## Control Surface Inventory (Corrected)

### PROVEN OPERATIONS (Implemented)

| Operation | Mechanism | Status | Tests |
|-----------|-----------|--------|-------|
| **Remove FX** | `array_remove()` | ✅ COMPLETE | test_pathmerge_arrays.py (all 19 pass) |
| **Add FX** | `array_insert()` | ✅ COMPLETE | test_pathmerge_arrays.py |
| **Replace FX** | `array_replace_element()` | ✅ COMPLETE | test_pathmerge_arrays.py |
| **Clear Rack** | `FX=[]` | ✅ COMPLETE | test_fx_full.py |
| **FX Parameters** | Scalar field mutation | ✅ COMPLETE | 76 parameters, all 14 effects |

### UNRESOLVED OPERATIONS (Not Implemented)

| Operation | Blocker | Status | Investigation |
|-----------|---------|--------|-----------------|
| **Enable FX** | Bypass field unknown | ❌ UNRESOLVED | Pending flex field decode |
| **Bypass FX** | Bypass field unknown | ❌ UNRESOLVED | Pending flex field decode |
| **Disable FX** | Bypass field unknown | ❌ UNRESOLVED | Pending flex field decode |
| **Unbypass FX** | Bypass field unknown | ❌ UNRESOLVED | Pending flex field decode |

---

## Corrected Implementation Changes

### 1. **fx_structural_operations.py**

**Before:**
```python
def disable_effect(...):
    # Called array_remove (WRONG: conflated remove with bypass)
```

**After:**
```
# ENABLE, DISABLE, BYPASS, UNBYPASS NOT REGISTERED
# These require proven bypass mechanism (currently unknown)
```

**Result:** Only PROVEN operations (clear_rack, remove, add, replace) are registered.

### 2. **compiler/targets.py**

**Before:**
```python
"FX.EnableMain": SemanticTargetRef("FX.EnableMain", "fx_struct_enable_main"),
"FX.EnableBus1": SemanticTargetRef("FX.EnableBus1", "fx_struct_enable_bus1"),
"FX.EnableBus2": SemanticTargetRef("FX.EnableBus2", "fx_struct_enable_bus2"),
"FX.DisableMain": SemanticTargetRef("FX.DisableMain", "fx_struct_disable_main"),
"FX.DisableBus1": SemanticTargetRef("FX.DisableBus1", "fx_struct_disable_bus1"),
"FX.DisableBus2": SemanticTargetRef("FX.DisableBus2", "fx_struct_disable_bus2"),
```

**After:**
```python
# PROVEN: clear_rack, remove, add, replace
# UNRESOLVED: enable/disable/bypass (flex field mechanism unknown)
```

**Result:** 6 unresolved targets removed from public vocabulary; 96 proven targets remain.

### 3. **test_fx_full.py**

**Before:**
```python
assert len(fx_targets) > 100
```

**After:**
```python
assert len(fx_targets) >= 96  # WITH EXPLANATION
# Note: FX enable/bypass/disable operations are UNRESOLVED
# See memory/fx_bypass_mechanism_unknown.md
```

**Result:** Test updated to reflect honest inventory; all 26 tests pass.

---

## What This Means

### For Control Surface Completeness

- **FX parameter controls:** ✅ COMPLETE (76 parameters, 14 effects)
- **FX topology control:** ✅ COMPLETE (add/remove/replace/clear)
- **FX enable/disable:** ❌ **NOT COMPLETE** (genuinely unresolved, explicit gap)

### For Compiler Behavior

- Requests for FX.EnableMain → **REFUSED** (unknown_no_contract)
- Requests for FX.DisableBus1 → **REFUSED** (unknown_no_contract)
- Requests for FX.Remove or FX.Clear → **ADMITTED** (proven)

### For Production Use

The FX control plane is:
- **Stable:** Proven operations are safe and tested
- **Honest:** Unresolved gaps are explicitly marked, not hidden
- **Extensible:** Once flex field is decoded, enable/disable operations can be added

---

## Next Investigation Protocol

To resolve the FX bypass mechanism:

1. **Capture Three Authoritative Serum States**
   - State A: Effect active (normal processing)
   - State B: Effect bypassed (disabled via Serum UI, not removed)
   - State C: Effect removed (deleted from array)

2. **Differential Analysis at v8 Level**
   - Use DawDreamer or direct v8 inspection
   - Compare serialized states for all fields:
     - `FXRack.FX[i].type`
     - `FXRack.FX[i].plainParams`
     - `FXRack.FX[i].flex` (currently opaque)
     - All other fields

3. **Identify Invariant**
   ```
   A ↔ B changes: [field_X, field_Y]
   B ↔ C changes: [topology_only]
   ```

4. **Decode and Implement**
   - If bypass in plainParams → implement via field mutation
   - If bypass in flex → decode flex first, then implement
   - If elsewhere → implement there

---

## Epistemic Status

| Finding | Status | Confidence |
|---------|--------|------------|
| FX bypass not in plainParams | PROVEN | High (systematic search, real corpus) |
| FX bypass not in VST3 list | PROVEN | High (DawDreamer enumeration) |
| FX bypass in flex field | HYPOTHESIS | Low (present but unexplored) |
| FX bypass unknown | CONCLUSION | Very High (exhaustive search excluded known locations) |

---

## Files Changed

1. `serum2/operations/fx_structural_operations.py` — Removed enable/disable registration; marked as UNRESOLVED
2. `serum2/compiler/targets.py` — Removed 6 unresolved semantic targets
3. `serum2/operations/test_fx_full.py` — Updated test expectations; added explanatory comment
4. `memory/fx_bypass_mechanism_unknown.md` — Created permanent record
5. `memory/MEMORY.md` — Added reference to bypass investigation

---

## Testing Status

**All regression tests pass:**
- ✅ test_pathmerge_arrays.py (19/19 pass)
- ✅ test_fx_full.py (26/26 pass)
- No breaking changes to proven operations

---

## Commit Message

```
FX Bypass Investigation: Mark as UNRESOLVED, remove conflation with REMOVE

INVESTIGATION FINDING:
After systematic search, FX bypass mechanism was NOT found in:
  - plainParams.kParamEnable/kParamBypass
  - VST3 parameter enumeration (2623 params)
  - type discriminant field
  
FX.flex field remains structurally present but semantically unexplored.

CORRECTION:
1. Remove enable/disable/bypass from semantic targets (6 unresolved targets)
2. Stop conflating disable_effect (unknown) with remove_effect (proven array_remove)
3. Keep only proven operations: clear_rack, remove, add, replace
4. Mark enable/bypass as explicit control-surface gap pending investigation

INVENTORY CHANGE:
  Before: 102 targets (6 unresolved included)
  After:  96 targets (all proven)

NEXT INVESTIGATION:
Differential state analysis on flex field via three authoritative Serum states:
  - active FX
  - bypassed FX (via UI)
  - removed FX

Reference: memory/fx_bypass_mechanism_unknown.md
```

---

## Author

Satvik Sangamkar (@Claude Haiku 4.5)  
Investigation closed: 2026-09-13

This is an honest boundary: FX control is substantially complete with proven operations.  
Bypass/enable remains explicitly unresolved with clear investigation protocol for resolution.
