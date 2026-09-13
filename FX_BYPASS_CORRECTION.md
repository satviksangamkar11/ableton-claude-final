# FX BYPASS CORRECTION: Phase FX-FULL Semantic Fix

**Status:** CRITICAL - Implementation conflated BYPASS with REMOVE

---

## EVIDENCE

### Modulation Routes Pattern (Verified)
Serum uses `ModSlot{N}.bypass` field:
- Type: boolean (true=bypassed, false=enabled)
- Behavior: Disables processing WITHOUT removing route structure
- Example: `ModSlot0.bypass = true` → route exists but inactive

### Expected FX Pattern
FX effects should follow the same pattern:
- `FXRack{R}.FX.{N}.plainParams.kParamBypass` (if follows pattern)
- OR other bypass field mechanism
- Behavior: Disables processing while preserving effect completely

---

## INCORRECT CURRENT IMPLEMENTATION

```python
# WRONG: These conflate two different operations
def disable_effect(...):
    # Currently: removes from array
    # array_remove(body, fx_array_path, index)
    # INCORRECT: This is REMOVE, not BYPASS

# WRONG: Operation names misleading
DISABLE_EFFECT = "disable_effect"  # → should be REMOVE
ADD_EFFECT = "add_effect"  # → should be ADD
```

### Problem
- disable_effect() calls array_remove() 
- This changes topology (REMOVE semantics)
- But operation is named DISABLE (BYPASS semantics)
- They must be separate operations

---

## CORRECT SEMANTIC MODEL

### Three Distinct Operations

#### 1. ENABLE / SET_BYPASS
**Purpose:** Toggle effect processing on/off  
**Mechanism:** Set bypass field  
**State Changes:**
- Effect type: PRESERVED
- Effect parameters: PRESERVED  
- Effect ordering: PRESERVED
- Resource references: PRESERVED
- Bus assignment: PRESERVED
- Processing: CHANGES (enabled → disabled or vice versa)

**Implementation:**
```python
def enable_effect(bus, slot):
    # Verify bypass field exists
    path = f"FXRack{bus}.FX.{slot}.plainParams.kParamBypass"
    mutation = Mutation(target_path=path, value=False)
    return mutation

def bypass_effect(bus, slot):
    path = f"FXRack{bus}.FX.{slot}.plainParams.kParamBypass"
    mutation = Mutation(target_path=path, value=True)
    return mutation
```

#### 2. REMOVE / DELETE_EFFECT
**Purpose:** Delete effect from rack  
**Mechanism:** Array element removal  
**State Changes:**
- Effect type: REMOVED
- Effect parameters: REMOVED
- Effect ordering: SHIFTS (subsequent slots move down)
- Resource references: REMOVED
- Bus assignment: N/A (effect gone)
- Topology: CHANGES

**Implementation:**
```python
def remove_effect(bus, slot):
    fx_path = f"FXRack{bus}.FX"
    # Use array_remove primitive
    array_remove(body, fx_path, slot)
    return mutation
```

#### 3. ADD / INSERT_EFFECT  
**Purpose:** Add new effect to rack  
**Mechanism:** Array element insertion  
**State Changes:**
- New effect added
- Existing effects at/after slot: SHIFT UP
- Topology: CHANGES

**Implementation:**
```python
def add_effect(bus, slot, effect_structure):
    fx_path = f"FXRack{bus}.FX"
    # Use array_insert primitive
    array_insert(body, fx_path, slot, effect_structure)
    return mutation
```

---

## REQUIRED VERIFICATION

### 1. Determine Bypass Field
**Question:** Does FX plainParams contain kParamBypass?

**How to verify:**
- Search corpus for FXRack effects with plainParams fields
- Check if any contain "bypass" or "Bypass" or similar
- Look at Serum documentation or skeleton defaults

**If found:** Bypass field exists → use it  
**If NOT found:** Investigate alternative mechanisms

### 2. Test Bypass Semantics
Write tests proving bypass preserves structure:
```python
def test_bypass_preserves_effect():
    body = {FX: [{"FXDistortion": {plainParams: {kParamDrive: 50}}}]}
    
    # Bypass the effect
    bypass_effect(body, bus=0, slot=0)
    
    # Verify structure still intact
    assert FX[0] has "FXDistortion"
    assert FX[0].plainParams.kParamDrive == 50  # Preserved!
    assert FX[0].plainParams.kParamBypass == True  # Now bypassed
    
def test_remove_changes_topology():
    body = {FX: [
        {"FXDistortion": {...}},
        {"FXReverb": {...}},
    ]}
    
    # Remove first effect
    remove_effect(body, bus=0, slot=0)
    
    # Verify topology changed
    assert len(FX) == 1  # Now only 1 effect
    assert FX[0] has "FXReverb"  # Reverb moved to slot 0
```

### 3. Distinguish Enable vs Add
```
enable_effect:
  - Effect already in slot
  - Set bypass = False
  - Reactivates processing

add_effect:
  - Effect not in rack
  - Insert new effect into array
  - Topology changes
```

---

## CORRECTED FX OPERATIONS

| Operation | Type | Mechanism | Array | Topology | Parameters |
|-----------|------|-----------|-------|----------|-----------|
| **enable_effect** | Scalar | Set kParamBypass=false | No change | No change | Preserved |
| **bypass_effect** | Scalar | Set kParamBypass=true | No change | No change | Preserved |
| **add_effect** | Structural | array_insert | Grows | Changes | N/A (new) |
| **remove_effect** | Structural | array_remove | Shrinks | Changes | Lost |
| **replace_effect** | Structural | array_replace | No change | No change | Replaced |
| **reorder_effect** | Structural | array_remove+insert | No change | Changes | Preserved |
| **clear_rack** | Structural | Replace FX=[] | Empties | Clears | All lost |

---

## CORRECTED INVENTORY

**Atomic Scalar Operations:**
- ✅ enable_effect (14 ops, one per effect type)
- ✅ bypass_effect (14 ops, one per effect type)
- ✅ 76 FX parameter controls

**Atomic Structural Operations:**
- ✅ add_effect (14 ops, one per effect type)
- ✅ remove_effect (14 ops, one per effect type)
- ✅ replace_effect (14 ops, one per effect type)
- ✅ clear_rack (3 ops, one per bus)

**Multi-Step Operations (via existing primitives):**
- 🟡 reorder_effect (sequence: remove + insert)
- 🟡 move_between_buses (sequence: remove from BUS1 + insert to BUS2)

**Total FX-FULL Coverage:**
- Scalar: 90 + 76 parameter controls = 166
- Structural: 28 atomic + 2 multi-step = 30
- **Grand Total: 196 FX operations**

---

## IMPLEMENTATION CORRECTIONS NEEDED

1. **Phase FX-FULL v2:**
   - Separate enable/bypass from remove operations
   - Add bypass field support to FX parameter catalog
   - Create enable_effect and bypass_effect operations
   - Keep remove_effect (separate from bypass)

2. **Update Semantic Targets:**
   - Add "FXEffect.Enable" targets
   - Add "FXEffect.Bypass" targets
   - These are SCALAR operations (boolean fields)
   - Not STRUCTURAL operations

3. **Update Pathmerge Paths:**
   - Add bypass field paths: `fx_field_{effect}_bypass`
   - Map to `FXRack{R}.FX.{N}.FX{Type}.plainParams.kParamBypass`

4. **Update Tests:**
   - Test bypass ≠ remove
   - Test bypass preserves parameters
   - Test remove changes topology

---

## NEXT STEPS

1. Verify bypass field exists in actual Serum state
2. Implement corrected operations
3. Add comprehensive tests
4. Update final report with correct inventory
5. Commit corrected implementation

---

**Status:** BLOCKED PENDING VERIFICATION
**Reason:** Bypass field representation must be confirmed before implementation
**Action:** Inspect actual Serum v8 state or documentation for bypass mechanism

