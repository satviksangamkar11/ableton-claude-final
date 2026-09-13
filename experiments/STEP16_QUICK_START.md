# STEP 16: Quick Start Checklist

## What This Does

Discovers how Serum represents FX bypass in its v8 serialized state by:
1. Capturing state with effect ACTIVE
2. Capturing state with effect BYPASSED (via UI)
3. Capturing state with effect REMOVED
4. Diffing all three to find changed fields
5. Repeating for second FX type to confirm pattern

**No implementation. Discovery only.**

---

## Prerequisites

- [ ] Serum 2.0.21 at `C:\Program Files\VstPlugins\Serum_x64.vst3`
- [ ] DawDreamer 0.9.0 working
- [ ] Python 3.14+
- [ ] cbor2 installed (`pip install cbor2`)
- [ ] Serum UI accessible and responsive

---

## Execution (Part 1: Distortion)

### Step 1: Run Setup
```bash
cd "D:\ableton claude"
python experiments/step16_fx_bypass_discovery_minimal.py
```

Script output will prompt you at each stage.

### Step 2: Add Distortion to Serum (Manual)
- Serum UI opens in background
- Go to MAIN FX rack, slot 0
- **Click the "+" or FX menu**
- **Select Distortion**
- **Set Drive to ~50%** (recognizable value)
- **Resume script**

### Step 3: Capture State A (ACTIVE)
Script reads v8 state and saves it. Output:
```
Capturing A: DISTORTION ACTIVE...
  ✓ State decoded (XXXX bytes)
  FXRack0.FX length: 1
  FXRack0.FX[0] keys: [type, plainParams, flex, ...]
```

**Verify:**
- FX array has length 1
- FX[0] contains Distortion data
- plainParams shows Drive ≈ 50%

**Then resume script**

### Step 4: Bypass Distortion (Manual)
- **In Serum UI, find the Distortion effect panel**
- **Click the BYPASS or DISABLE button**
  - Look for a small power icon or bypass label
  - Effect should grey out or show "bypassed"
- **Verify button is toggled**
- **Resume script**

### Step 5: Capture State B (BYPASSED)
Script reads v8 state. Output should show:
```
Capturing B: DISTORTION BYPASSED...
  ✓ State decoded (XXXX bytes)
  FXRack0.FX length: 1  ← SAME as A
  FXRack0.FX[0] keys: [type, plainParams, flex, ...]
```

**Critical:**
- FX array still has length 1 (topology preserved)
- FX[0] is still present (not removed)

**Then resume script**

### Step 6: Remove Distortion (Manual)
- **In Serum UI, find the Distortion effect panel**
- **Click DELETE or the "X" button**
  - Effect should disappear from rack
- **Verify slot is now empty**
- **Resume script**

### Step 7: Capture State C (REMOVED)
Script reads v8 state. Output should show:
```
Capturing C: DISTORTION REMOVED...
  ✓ State decoded (XXXX bytes)
  C: DISTORTION REMOVED:
    FXRack0.FX length: 0  ← CHANGED from A
```

**Critical:**
- FX array is now empty or shorter (topology changed)
- FX[0] no longer exists

**Then resume script**

### Step 8: Review Diffs

Script outputs structural diffs:

```
A→B (ACTIVE → BYPASSED):
  FXRack0.FX[0].plainParams.{FIELD}: value_change
    A: {value_a}
    B: {value_b}
  (and any other changes)

B→C (BYPASSED → REMOVED):
  FXRack0.FX: length_change
    A_length: 1
    B_length: 0
```

**Record these exactly. This is the evidence.**

---

## Execution (Part 2: Delay)

Repeat the above with **Delay** instead of Distortion:

1. Run setup script again (or copy for Delay)
2. Add **FXDelay** to MAIN rack, slot 0
3. Set Feedback to ~75% (recognizable)
4. Capture State A (DELAY ACTIVE)
5. Bypass via UI
6. Capture State B (DELAY BYPASSED)
7. Remove via UI
8. Capture State C (DELAY REMOVED)
9. Review diffs

**Compare:** Are the A→B diffs identical to Distortion's? ✓ YES = shared mechanism

---

## Expected Output Pattern

### If Bypass Found (Correct)

```
DISTORTION A→B:
  FXRack0.FX[0].plainParams.kParamBypass: false → true
  (possibly other fields)

DELAY A→B:
  FXRack0.FX[0].plainParams.kParamBypass: false → true
  (same pattern)

BOTH B→C:
  FXRack0.FX: length_change (1 → 0)
  (topology changes, not field changes)

CONCLUSION: Bypass mechanism is kParamBypass (boolean field)
```

### If Bypass NOT Found (Unexpected)

```
DISTORTION A→B:
  FXRack0.FX: length_change (1 → 0)
  (topology changed, no field-level changes)

CONCLUSION: Either bypass is not implemented,
            or it's represented differently than expected
            (e.g., in flex, or elsewhere)
```

### If Bypass in Flex (Possible)

```
DISTORTION A→B:
  FXRack0.FX[0].flex: value_change
    A: [dict1, dict2]
    B: [dict1, dict2_modified]
  (flex field changed, but array topology preserved)

CONCLUSION: Bypass mechanism is in flex field
            (requires further decoding)
```

---

## Troubleshooting

**Script says "DawDreamer not available"**
- Install: `pip install dawdreamer`
- Or check Python environment

**Serum UI doesn't open**
- Check Serum installation path
- Verify VST3 path: `/Program Files/VstPlugins/Serum_x64.vst3`

**Can't find Bypass button in Serum**
- Look for small icon near effect name
- Try right-click on effect name (context menu)
- Or check Serum manual for bypass location

**State capture fails**
- Serum may need time to load
- Try closing/reopening Serum UI
- Verify DawDreamer can still communicate

**Diff shows nothing changed**
- Bypass may be toggling but not persisting in state
- Or UI action didn't actually bypass (verify visually)
- Or bypass is implemented outside FX[0] structure

---

## Deliverable

After both Distortion and Delay:

📋 **Create file:** `experiments/STEP16_FX_BYPASS_FINDINGS.md`

Document:
1. **A→B Changes for Distortion** (exact paths, types, values)
2. **A→B Changes for Delay** (exact paths, types, values)
3. **B→C Changes for Both** (topology confirmation)
4. **Cross-FX Consistency** (same mechanism? yes/no)
5. **Mechanism Identified** (which field? type? how to mutate?)

---

## Next Phase (After Approval)

Once findings are validated:
- Implement `enable_effect()`, `bypass_effect()`, `unbypass_effect()`
- Update semantic targets
- Write tests
- Commit

**Do NOT implement until findings are approved.**

---

## Files

- Script: `experiments/step16_fx_bypass_discovery_minimal.py`
- Full Protocol: `experiments/STEP16_FX_BYPASS_DISCOVERY_PROTOCOL.md`
- This Checklist: `experiments/STEP16_QUICK_START.md`

Start with this checklist. See full protocol for details.
