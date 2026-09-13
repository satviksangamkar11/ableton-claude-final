# STEP 20B: MIX Page Persistent Architecture — Findings & Next Steps

## Part 1: OSC Pan/Level (✅ COMPLETE)

**Status:** All 5 oscillators proven with parametric pattern.

**Oscillators:**
- OSC A (Oscillator0), OSC B (Oscillator1), OSC C (Oscillator2), SUB (Oscillator3), NOISE (Oscillator4)

**Persistent Keys:**
- `kParamPan`: -50..+50 (CBOR) → VST3 = 0.5 + kParamPan/100
- `kParamVolume`: 0..1 squared (CBOR) → VST3 = sqrt(kParamVolume)

**Semantic Targets Added:**
- OSC2.Pan, OSC2.Level, OSC3.Pan, OSC3.Level
- SUB.Pan, SUB.Level, NOISE.Pan, NOISE.Level

**Test Evidence:** 4 parametric round-trip tests PASS.

---

## Part 3: Send Levels (⚠ ARCHITECTURE CLARIFICATION)

**Finding:** Serum's send architecture is **routing-level, not per-oscillator**.

**Structure Discovered:**
```
RoutingSlot0..6: Global routing configuration
  ├─ plainParams.kParamFXBus1Level: Send level to FX Bus 1 (0..100)
  ├─ plainParams.kParamFXBus2Level: Send level to FX Bus 2 (0..100)
  └─ plainParams.kParamRoutingDest: Routing destination (e.g., kRoutingDestFilter)
```

**Evidence:** `LD - Split.SerumPreset` shows:
- RoutingSlot0: kParamFXBus1Level = 100.0
- RoutingSlot1: kParamFXBus2Level = 100.0 + kParamRoutingDest

**Interpretation:**
- A→BUS1 notation refers to routing slot configuration, not per-oscillator sends
- Per-oscillator level control is via Pan/Level (already proven in PART 1)
- Actual send-to-bus control happens at RoutingSlot level

**Next Steps for PART 3:**
1. Create test preset with different RoutingSlot configurations via Serum UI
2. Decode CBOR to identify exact value scales for kParamFXBus1Level, kParamFXBus2Level
3. Test persistence through save/reload cycle
4. Add semantic targets: ROUTE0.BUS1Level, ROUTE0.BUS2Level, etc.

---

## Part 4: Filter Mix Channel (READY FOR INVESTIGATION)

**Structure Discovered:**
```
VoiceFilter0, VoiceFilter1: Per-voice filter instances
  └─ plainParams: (currently "default", ready for mutation testing)

Filter: Global filter control
  └─ kUIParamMixOrGain: 0.0 (mix/wet control)
```

**Candidate Keys:**
- kParamMixOrGain (similar to kParamVolume pattern in oscillators)
- kParamLevel (if filter has independent level control)

**Pattern Hypothesis:**
- Filter mix follows same dict-merge pattern as oscillator Pan/Level
- Mix scale likely 0..1 (wet %) or 0..100

**Next Steps for PART 4:**
1. Use Serum UI to set Filter1 Mix to known value (e.g., 75% wet)
2. Save preset, decode CBOR
3. Verify plainParams mutation and scale
4. Test persistence via parametric round-trip test
5. Add semantic targets: Filter1.Level, Filter1.Mix (or Wet)

---

## Part 5: Routing Topology (DEFERRED)

**Structure:** RoutingSlot defines destination (kParamRoutingDest), but full routing graph requires:
- Oscillator → Filter assignment
- Filter1 → Filter2 assignment
- Filter → Output/Bus routing

**Status:** Discovered RoutingSlot exists; full topology requires deeper CBOR investigation.

---

## Part 6: Bus FX Bypass (BLOCKED)

**Prior Finding:** (from memory) FX bypass mechanism is UNRESOLVED. Flex field unexplored.

**Status:** Pending bypass mechanism discovery before implementation.

---

## Recommendation

**Priority Order:**
1. ✅ PART 1: Complete (all oscillators)
2. 📋 PART 4: Filter Mix (similar to PART 1, higher ROI than PART 3)
3. 📋 PART 3: Send levels via RoutingSlots (more complex, requires UI testing)
4. ⏳ PART 5: Routing topology (depends on PART 3 completion)
5. 🚫 PART 6: FX bypass (blocked on prior investigation)

**Commit:** `03d0a1b` — STEP 20B PART 1 complete.
