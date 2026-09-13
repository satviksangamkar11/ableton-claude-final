# PHASE FX-FULL: COMPLETE SERUM FX SYSTEM CONTROL
## Strategy & Implementation Plan

**Date:** 2026-09-13  
**Scope:** Full FX control surface (14 effect types × 3 buses × N slots)  
**Status:** STRATEGY PHASE - requires extensive implementation

---

## DISCOVERY FINDINGS

### FX Structure (v8 State)

```
FXRack0/1/2
├── FX[]  (array of effect slots, 0-14 entries)
│   └── FX_Slot_N
│       ├── FX{Type}
│       │   ├── plainParams  (scalar parameters)
│       │   ├── additional_fields  (type-specific)
│       │   └── resources  (IR path, etc.)
│       ├── type  (FX type identifier)
│       └── kUIParam*  (UI fields - not musical controls)
├── displayName
└── plainParams
```

### Effect Types Found in Corpus

| Code | Reference | Status |
|------|-----------|--------|
| FXBode | BODE | ✅ Found |
| FXChorus | CHORUS | ✅ Found |
| FXComp | COMPRESSOR | ✅ Found |
| FXConv | CONVOLVE | ✅ Found (with IR resource) |
| FXDelay | DELAY | ✅ Found |
| FXDistortion | DISTORTION | ✅ Found |
| FXEQ | EQ | ✅ Found |
| FXFilter | FILTER | ✅ Found |
| FXFlanger | FLANGER | ✅ Found |
| FXHyperD | HYPER/DIMENSION | ✅ Found |
| FXPhaser | PHASER | ✅ Found |
| FXReverb | REVERB | ✅ Found |
| FXSplit | SPLITTER | ✅ Found |
| FXUtils | UTILITY | ✅ Found |

---

## IMPLEMENTATION ARCHITECTURE

### Three-Level Control Model

**Level 1: Scalar Parameter Operations**
- Path: `FXRack{R}.FX.{N}.FX{Type}.plainParams.kParam{Name}`
- Operation: `set_fx_parameter(bus, slot, effect, param_name, value)`
- Compiles to: Single Mutation via pathmerge

**Level 2: Structured Operations**
- Enable/bypass: Presence in array or field mutation
- Effect replacement: Dict replacement at slot
- Reordering: Array manipulation (requires extension)
- Type change: Complete FX object replacement

**Level 3: Resource Operations**
- Convolve IR loading: `FXConv.relativePathToIR`
- Validated via existing resource-resolver

### Buses Model

```python
buses = {
    "MAIN": 0,      # FXRack0
    "BUS1": 1,      # FXRack1  
    "BUS2": 2,      # FXRack2
}
```

Operations must accept: `bus="MAIN"` (or 0)

---

## BLOCKERS & DECISIONS

### Array Manipulation (FX Slot Operations)

**Required for:**
- Add effect to rack
- Remove effect from rack
- Reorder effects
- Move effect between racks

**Current Status:** Pathmerge does NOT support array insertion/deletion

**Options:**
1. **Extend pathmerge** with `array_insert()`, `array_remove()` primitives
2. **Accept current limitation**: Can set FX at existing slots only
3. **Use complete array replacement**: Mutate entire FXRack0.FX array at once

**Recommendation:** Option 3 for MVP; Option 1 for full capability

### Enable/Bypass Mechanism

**Investigation:** No explicit `enable` field found in FX plainParams

**Hypothesis:** FX presence/absence = enable/disable (like we found for FX slots)

**Verification Needed:** Can we disable an FX by:
- Removing it from array (requires array op)
- Replacing it with empty/default struct (requires null representation)
- Setting a bypass flag (if one exists, not yet found)

---

## PARAMETERS BY EFFECT TYPE

*(To be completed via corpus analysis)*

### BODE
- `kParamShift`
- `kParamRange`
- `kParamDirection`
- `kParamLevelOut`
- `kParamMixOrGain`

### CHORUS
- `kParamRate`
- `kParamDepth`
- `kParamFeedback`
- `kParamPhase`
- `kParamMixOrGain`

### COMPRESSOR (FXComp)
- `kParamThreshold`
- `kParamRatio`
- `kParamAttack`
- `kParamRelease`
- `kParamGain`
- `kParamMixOrGain`
- `kParamSingleMultiBand`? (needs verification)

### CONVOLVE (FXConv)
- `kParamIRGain`
- `kParamAttack`
- `kParamDecay`
- `kParamDamping`
- `kParamMixOrGain`
- `relativePathToIR` (resource)
- `embeddedIR` (binary data)

### DELAY (FXDelay)
- `kParamMode`
- `kParamTimeL`
- `kParamTimeR`
- `kParamOffsetL`
- `kParamOffsetR`
- `kParamFeedback`
- `kParamMixOrGain`
- `kParamBW`? (needs verification)

### DISTORTION (FXDistortion)
- `kParamMode`
- `kParamDrive`
- `kParamFreq`
- `kParamLPHP`
- `kParamPrePost`
- `kParamMixOrGain`
- `kParamBW`? (needs verification)

### EQ (FXEQ)
- `kParamType1` / `kParamType2` (band types)
- `kParamFreq1` / `kParamFreq2` (band frequencies)
- `kParamReso1` / `kParamReso2` (band Q)
- `kParamGain1` / `kParamGain2` (band gains)
- `kParamLevelOut` (output level)

### FILTER (FXFilter)
- `kParamType`
- `kParamCutoff`
- `kParamResonance`
- `kParamDrive`
- `kParamMixOrGain`
- `kParamVar`?

### FLANGER (FXFlanger)
- `kParamRate`
- `kParamDepth`
- `kParamFeedback`
- `kParamPhase`
- `kParamMixOrGain`
- `lfophasor` (LFO state)

### HYPER/DIMENSION (FXHyperD)
- `kParamRate`
- `kParamUnison`
- `kParamDetune`
- `kParamMixOrGain`
- `kParamRetrigger`?
- `lfo` (LFO state)

### PHASER (FXPhaser)
- `kParamFrequency`
- `kParamFeedback`
- `kParamPhase`
- `kParamMixOrGain`
- `lfophasor` (LFO state)

### REVERB (FXReverb)
- `kParamSize`
- `kParamDamping`
- `kParamMixOrGain`

### SPLITTER (FXSplit)
- Structure unknown - needs investigation
- Likely: band count, crossover points, band muting

### UTILITY (FXUtils)
- `kParamGain`
- `kParamPhase`
- `kParamMono`
- `kParamMixOrGain`

---

## IMPLEMENTATION ROADMAP

### Phase FX-1: Core FX Registry
- [ ] Extend `fx_resolver.py` with COMPLETE parameter catalog
- [ ] Add all 14 effect types with all parameters
- [ ] Document state paths from corpus evidence
- [ ] Handle enum/mode fields

### Phase FX-2: Slot Operations
- [ ] Design FX slot operation primitives
- [ ] Implement add/remove/replace FX operations
- [ ] Test array mutation strategies

### Phase FX-3: Three-Bus Support
- [ ] Extend operations to accept bus parameter
- [ ] Implement bus-aware FX operations
- [ ] Test multi-bus routing

### Phase FX-4: Resource Operations
- [ ] Integrate Convolve IR loading
- [ ] Validate via resource-resolver
- [ ] Add IR fallback handling

### Phase FX-5: Testing & Verification
- [ ] Unit tests for every effect type
- [ ] Integration tests for operations
- [ ] A/B/C verification via harness

### Phase FX-6: Complete Inventory
- [ ] Generate authoritative FX control matrix
- [ ] Document coverage %, gaps
- [ ] Decision: ship vs. extend

---

## COMPLETION CRITERIA

FX control is COMPLETE only when:

✅ All 14 effect types are controllable
✅ Every parameter from Serum reference is represented
✅ All enum/mode fields are accessible
✅ Resource-backed fields (IR) work
✅ All three buses are supported
✅ FX enable/disable mechanism is verified
✅ Complete inventory shows 100% of representable controls
✅ Tests cover all effect families

**Estimated token cost:** 40-60k tokens for full implementation

---

**Decision:** This phase requires significant additional implementation beyond current token budget.

**Recommendation:** Proceed as Phase FX-FULL in next session with fresh token budget.

---

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
