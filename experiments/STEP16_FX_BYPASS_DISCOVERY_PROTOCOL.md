# STEP 16: FX Bypass Discovery Protocol

**Objective:** Determine exact serialized representation of FX bypass in Serum v8 state  
**Type:** Authoritative discovery experiment (no implementation)  
**Authority:** Direct Serum state inspection via DawDreamer + manual UI control  

---

## Executive Summary

We will capture Serum v8 state in three conditions for the same effect slot:

1. **State A:** Effect ACTIVE (processing enabled)
2. **State B:** Effect BYPASSED (disabled via UI, but present in rack)
3. **State C:** Effect REMOVED (deleted from FXRack array)

By diffing these states, we will identify:
- Which field(s) change to represent bypass
- Whether the mechanism is shared across FX types
- Whether `flex` field participates

---

## Prerequisites

- **Serum 2.0.21** VST3 installed at `/Program Files/VstPlugins/Serum_x64.vst3`
- **DawDreamer 0.9.0** installed and working
- **Python 3.14+** with cbor2
- **Serum UI** must be accessible for manual bypass control

---

## Part 1: DISTORTION FX Discovery

### Phase 1A: Setup

**Goal:** Create minimal test case with ONE FX in MAIN rack

1. Run the experiment script (baseline):
   ```bash
   cd D:\ableton claude
   python experiments/step16_fx_bypass_discovery_minimal.py
   ```

2. The script will load Serum but cannot yet add FX via DawDreamer (UI automation limited)

3. **Manual Step:** When prompted, open Serum UI and:
   - Add **FXDistortion** to **MAIN rack, slot 0**
   - Verify it shows in the UI
   - Set a recognizable parameter (e.g., Drive to 50%)

4. Resume the script - it will capture **State A (ACTIVE)**

### Phase 1B: Capture Active State

**State A Definition:**
- Distortion FX is in MAIN rack slot 0
- Processing is ENABLED (not bypassed)
- Drive parameter = 50% (or other recognizable value)

**Script Output:**
```
Capturing A: DISTORTION ACTIVE...
  ✓ State decoded (XXXX bytes)
  
A: DISTORTION ACTIVE:
  FXRack0.FX length: 1
  FXRack0.FX[0] keys: [type, plainParams, flex, ...]
    type: 0
    plainParams keys: [kParamDrive, kParamMode, kParamLevelOut, ...]
    flex: list of X elements
```

**Critical Check:**
- FXRack0.FX array has length 1
- FX[0] contains the Distortion data
- Effect is "active" (no bypass field is true)

### Phase 1C: Capture Bypassed State

**Manual Step:**
1. In Serum UI, locate the Distortion effect in MAIN rack
2. Click the **BYPASS** button (or disable button)
   - Visual feedback: effect should show as "bypassed" or greyed out
3. Verify the button state visually
4. Resume the script - it will capture **State B (BYPASSED)**

**State B Definition:**
- Distortion FX is still in MAIN rack slot 0
- Processing is DISABLED (bypassed via UI)
- Parameters are preserved (Drive still recognizable)
- FX[0] is still present (topology unchanged)

**Critical Distinction:**
- B has the same topology as A (still 1 FX in array)
- B differs from A only in bypass state (one or more fields changed)

### Phase 1D: Capture Removed State

**Manual Step:**
1. In Serum UI, locate the Distortion effect in MAIN rack
2. Click **DELETE** or **REMOVE** button
   - Visual feedback: effect disappears from rack
3. Verify the slot is now empty
4. Resume the script - it will capture **State C (REMOVED)**

**State C Definition:**
- Distortion FX is deleted from MAIN rack
- FXRack0.FX array is empty (or shorter)
- Topology has changed (1 FX → 0 FX)

**Critical Distinction:**
- C has different topology from B (array changed)
- B→C should show array shrinkage, not just field changes

### Phase 1E: Analysis

The script performs recursive structural diff:

**Expected Output Pattern:**

```
A→B (ACTIVE → BYPASSED):
  FXRack0.FX[0].plainParams.{BYPASS_FIELD}: value_change
    A: false
    B: true
  (possibly other fields in flex or elsewhere)

B→C (BYPASSED → REMOVED):
  FXRack0.FX: length_change
    A_length: 1
    B_length: 0
  (array topology changed)

A→C (ACTIVE → REMOVED):
  FXRack0.FX: length_change (same as B→C)
```

**If A→B shows only topology changes:**
- This would indicate bypass IS implemented as removal (wrong)
- This would contradict the bypass-preserves-structure requirement

**If A→B shows field changes but no topology change:**
- This is correct - bypass changed a field, not the array
- Identify the field name and type

---

## Part 2: DELAY FX Discovery (Validation)

**Goal:** Verify that bypass mechanism is shared across FX families

### Phase 2A: Setup

**Manual Step:**
1. Delete the Distortion from MAIN rack (if still there)
2. Add **FXDelay** to MAIN rack, slot 0
3. Set a recognizable parameter (e.g., Feedback to 75%)
4. Resume discovery script (or create copy for Delay)

### Phase 2B-2D: Repeat Phases 1B-1D

- Capture State A (DELAY ACTIVE)
- Bypass via UI
- Capture State B (DELAY BYPASSED)
- Remove via UI
- Capture State C (DELAY REMOVED)

### Phase 2E: Validation

Compare A→B diffs for Distortion vs Delay:

**Expected: Same mechanism**
```
FXDistortion A→B:
  FXRack0.FX[0].plainParams.kParamBypass: false → true

FXDelay A→B:
  FXRack0.FX[0].plainParams.kParamBypass: false → true
```

**This would prove:** Bypass is implemented uniformly across FX types.

---

## Output: Structured Findings Report

After both experiments, deliver:

### A. Active → Bypassed Changes (A→B)

**For each FX type (Distortion, Delay):**

```
DISTORTION:
  Changed path 1: FXRack0.FX[0].{FIELD_NAME}
    Type: {type_change | value_change | ...}
    A value: {value_a}
    B value: {value_b}
  Changed path 2: ...

DELAY:
  Changed path 1: FXRack0.FX[0].{FIELD_NAME}
    Type: {type_change | value_change | ...}
    A value: {value_a}
    B value: {value_b}
  Changed path 2: ...
```

### B. Bypassed → Removed Changes (B→C)

```
DISTORTION:
  FXRack0.FX: length_change (1 → 0)
  (all fields in FX[0] removed as array shrinks)

DELAY:
  FXRack0.FX: length_change (1 → 0)
  (all fields in FX[0] removed as array shrinks)
```

### C. Does flex participate?

```
Flex field in A→B diff:
  ✓ YES, changes from {value_a} to {value_b}
  ✗ NO, unchanged between A and B
```

### D. Is mechanism shared?

```
Same field(s) changed across both FX types:
  ✓ YES: Both use FXRack0.FX[0].{FIELD} for bypass
  ✗ NO: Different mechanisms for Distortion vs Delay
```

### E. Minimal evidence for implementation

**If bypass is in plainParams:**
```
Mutation type: scalar field mutation
Target path: FXRack0.FX.{N}.FX{Type}.plainParams.{BYPASS_FIELD}
Value type: boolean
False = enabled
True = bypassed
```

**If bypass is in flex:**
```
Mutation type: TBD (after decoding flex structure)
Target path: FXRack0.FX.{N}.flex.{FIELD}
Value type: {type_from_observation}
```

**Operations to implement (pending proof):**
1. `enable_effect(bus, slot)` → set bypass field to False
2. `bypass_effect(bus, slot)` → set bypass field to True
3. `unbypass_effect(bus, slot)` → set bypass field to False (same as enable)

---

## Critical Constraints

✋ **DO NOT:**
- Implement any operations during discovery
- Modify compiler/targets files
- Declare bypass "found" unless correlated with UI action
- Invent semantic names for unknown fields

✅ **DO:**
- Report every changed field path exactly as shown in serialized state
- Verify that bypassed effect remains in FX array (topology preserved)
- Verify that removed effect changes array topology
- Repeat measurement for at least two FX types
- Save raw state diffs for evidence trail

---

## Success Criteria

✅ **Bypass Discovered Successfully:**
1. A→B diff identifies specific field change(s)
2. B→C diff shows array topology change (no field-level changes)
3. A→B pattern is identical for Distortion and Delay
4. Field value correlates: bypass=true when UI shows bypassed, false when active

❌ **Bypass NOT Found:**
1. A→B shows no field changes (or only unrelated changes)
2. A→B and B→C show identical changes (both are topology changes)

❌ **Inconclusive:**
1. A→B shows changes but pattern differs between Distortion and Delay
2. Bypass cannot be reliably distinguished from other state variations

---

## Timeline

1. **Phase 1A:** Setup experiment, confirm DawDreamer works
2. **Phase 1B:** Capture and review State A (ACTIVE)
3. **Phase 1C:** Bypass manually, capture and review State B (BYPASSED)
4. **Phase 1D:** Remove manually, capture and review State C (REMOVED)
5. **Phase 1E:** Analyze diffs, identify changes
6. **Phase 2A-2D:** Repeat for Delay FX
7. **Phase 2E:** Validate cross-FX consistency
8. **Report:** Deliver structured findings

---

## Reference

- **Memory:** memory/fx_bypass_mechanism_unknown.md
- **Previous Investigation:** step15_2_8_fxdistortion_enable_discovery.py (flex field unexplored)
- **Target Document:** FX_BYPASS_INVESTIGATION_CLOSED.md
- **Compiler Status:** 96/102 targets active (6 enable/bypass unresolved)

---

## Next Use

Once findings are delivered, the next phase is:

**Phase 3: Implement Bypass Operations**
- Design mutations based on discovered field(s)
- Implement enable_effect, bypass_effect, unbypass_effect
- Write tests proving bypass preserves topology
- Update compiler to admit bypass operations

No implementation until discovery is complete and findings are approved.
