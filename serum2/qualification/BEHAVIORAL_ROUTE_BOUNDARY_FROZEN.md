# Behavioral Route Boundary — Frozen

**Date:** 2026-09-11  
**Status:** FINAL - No further behavioral experiments on these controls  
**Scope:** Subprocess DawDreamer architecture + CBOR mutation

---

## Critical Distinction

**CONTROLLABLE** ≠ **BEHAVIORALLY_QUALIFIED**

A control may exist in Serum and be accessible via host parameters (Ableton MCP), but if the activation does not propagate into the isolated DawDreamer subprocess where behavioral evidence is captured, the control **cannot be behaviorally qualified using CBOR mutation.**

---

## Controls: Classification

### **ROUTE_VERIFIED** (Behavioral qualification complete)

| Control | Route | CBOR Path | Status | Evidence |
|---|---|---|---|---|
| **Filter1.Cutoff** | CBOR direct (active by default) | `VoiceFilter0.plainParams.kParamFreq` | ✓ QUALIFIED | A_FILTER_CUTOFF_PILOT_EVIDENCE.json |

**Why:** Filter1 is materialized and active in default skeleton. CBOR mutation works directly.

---

### **STRUCTURAL_ACTIVATION_REQUIRED / ROUTE_UNAVAILABLE_IN_DAWDREAMER**

These controls exist, have correct CBOR paths, but **cannot be activated in the subprocess environment because activation requires host-parameter changes (Ableton MCP) that do not propagate into the isolated DawDreamer instance.**

#### **OSC1.Level**

| Attribute | Value |
|---|---|
| Semantic Target | OSC1.Level |
| CBOR Path | `Oscillator0.plainParams.kParamLevel` |
| MCP Parameter | Parameter 16: "A Enable" (OSC A on/off toggle) |
| Default State | Inactive (sparse plainParams) |
| Activation Route | Ableton MCP only (not available in subprocess) |
| Behavioral Status | **NOT QUALIFIED** (activation route unavailable) |
| Controllability | **CONTROLLABLE** via Ableton MCP in live session |

**Evidence:**
- ✓ CBOR path verified: exists in skeleton structure
- ✓ MCP parameter verified: discovered in 16.5_Serum2_Complete_MCP_Discovery
- ✗ Subprocess activation: exercise_context["A Enable"]=1.0 does not propagate to DawDreamer
- ✗ Baseline render with context: -20.05 dB (still silent, no effect)
- ✗ Treatment render: -20.05 dB (no delta)

**Why activation fails:**
1. Ableton MCP operates on: **Ableton Live's running Serum VST3 instance**
2. DawDreamer renders: **Independent subprocess Serum VST3 instance**
3. Parameter change in Ableton does NOT reach subprocess
4. OSC1.Enable remains 0.0 in subprocess (inactive)
5. CBOR level mutation has no audio effect on inactive oscillator

**Recommendation:** OSC1.Level behavioral qualification requires either:
- Live Ableton MCP layer (separate implementation)
- Or, manual prerequisite verification outside behavioral harness

---

#### **Filter2.Cutoff**

| Attribute | Value |
|---|---|
| Semantic Target | Filter2.Cutoff |
| CBOR Path | `VoiceFilter1.plainParams.kParamFreq` |
| MCP Parameter | Unknown (not in discovered 127-param map; may require Ableton state) |
| Default State | Inactive or bypassed |
| Activation Route | Unknown (likely host-parameter or routing) |
| Behavioral Status | **NOT QUALIFIED** (activation route unknown) |
| Controllability | **POSSIBLY CONTROLLABLE** via Ableton |

**Evidence:**
- ✓ CBOR path verified: exists in skeleton structure
- ? MCP parameter: NOT in standard 127-param discovery
- ✗ Subprocess activation: No known context key activates Filter2
- ✗ Multiple mutation attempts: all produced +0.00 Hz delta
- ✗ Baseline with context activation attempt: still 4378 Hz (high-pass, inactive)

**Why qualification is blocked:**
1. No discovered MCP parameter for Filter2.Cutoff
2. No exercise context key found that activates Filter2
3. May be part of routing matrix (not directly host-parameter-accessible)
4. CBOR mutation has no effect even with materialization attempts

**Recommendation:** Filter2.Cutoff requires Ableton state inspection to determine activation mechanism.

---

#### **Env1.Attack**

| Attribute | Value |
|---|---|
| Semantic Target | Env1.Attack |
| CBOR Path | `Env0.plainParams.kParamAttackTime` |
| MCP Parameter | Parameter 12: "Env 1 Attack" (in 127-param discovery) |
| Default State | Partially materialized (curves present, but not routed) |
| Activation Route | Ableton MCP + routing (not available in subprocess) |
| Behavioral Status | **NOT QUALIFIED** (activation route unavailable) |
| Controllability | **CONTROLLABLE** via Ableton MCP |

**Evidence:**
- ✓ CBOR path verified: exists in skeleton, partially materialized
- ✓ MCP parameter verified: Parameter 12 "Env 1 Attack" discovered
- ✗ Subprocess activation: exercise_context does not reach subprocess
- ✗ Baseline render: -20.05 dB (silent, envelope routed to nothing)
- ✗ Treatment render: -20.05 dB (no delta even with attack=0.9)

**Why qualification is blocked:**
1. Env0 may not be routed to an audible destination (structural issue)
2. MCP parameter affects Ableton's instance, not subprocess
3. CBOR mutation has no effect on unrouted modulation envelope
4. Requires both: activation (routing) + MCP parameter change

**Recommendation:** Env1.Attack requires structural routing investigation (envelope destination assignment) before behavioral qualification is possible.

---

#### **OSC1.Detune (Seed Exp 5)**

| Attribute | Value |
|---|---|
| Semantic Target | OSC1.Detune |
| CBOR Path | `Oscillator0.plainParams.kParamDetune` (inferred) |
| Activation Prerequisite | OSC1.Enable (Parameter 16, unavailable in subprocess) |
| Behavioral Status | **NOT QUALIFIED** (depends on OSC1.Enable activation) |

**Classification:** Inherits STRUCTURAL_ACTIVATION_REQUIRED from OSC1.Enable.

---

#### **OSC2.Detune (Seed Exp 6)**

| Attribute | Value |
|---|---|
| Semantic Target | OSC2.Detune |
| CBOR Path | `Oscillator1.plainParams.kParamDetune` (inferred) |
| Activation Prerequisite | OSC2.Enable (MCP parameter unknown, unavailable in subprocess) |
| Behavioral Status | **NOT QUALIFIED** (depends on unknown activation) |

**Classification:** STRUCTURAL_ACTIVATION_REQUIRED.

---

#### **Env1.Release (Seed Exp 8)**

| Attribute | Value |
|---|---|
| Semantic Target | Env1.Release |
| CBOR Path | `Env0.plainParams.kParamReleaseTime` (inferred) |
| Activation Prerequisite | Env1 routing (unavailable in subprocess) |
| Behavioral Status | **NOT QUALIFIED** (depends on Env1.Attack activation route) |

**Classification:** Inherits STRUCTURAL_ACTIVATION_REQUIRED from Env1 routing.

---

#### **Filter1.Resonance (Seed Exp 2)** — Special Case

| Attribute | Value |
|---|---|
| Semantic Target | Filter1.Resonance |
| CBOR Path | `VoiceFilter0.plainParams.kParamReso` |
| Result | +13.78 Hz (small effect observed) |
| Expected Effect | +100 Hz (threshold set too high) |
| Status | Below threshold; not classified as EFFECT_OBSERVED |

**Classification:** ROUTE_EXISTS_BUT_EFFECT_BELOW_THRESHOLD

**Note:** Filter1.Resonance produced a measurable delta (+13.78 Hz), proving the CBOR mutation mechanism works. However, the effect is below the guessed threshold of 100 Hz. This is NOT a route failure; it's a **threshold calibration issue**. The control is behaviorally observable, but the threshold was too conservative.

**Future action:** If resonance behavioral qualification is desired, lower the threshold or accept EFFECT_OBSERVED at +13.78 Hz.

---

## Preserved Evidence

All evidence from seed batch execution is preserved:
- `A_SEED_EXPERIMENT_02_seed_filter1_resonance_001_EVIDENCE.json`
- `A_SEED_EXPERIMENT_03_seed_filter2_cutoff_001_EVIDENCE.json`
- `A_SEED_EXPERIMENT_04_seed_osc1_level_001_EVIDENCE.json`
- `A_SEED_EXPERIMENT_05_seed_osc1_detune_001_EVIDENCE.json`
- `A_SEED_EXPERIMENT_06_seed_osc2_detune_001_EVIDENCE.json`
- `A_SEED_EXPERIMENT_07_seed_env1_attack_001_EVIDENCE.json`
- `A_SEED_EXPERIMENT_08_seed_env1_release_001_EVIDENCE.json`

**This evidence is forensic only.** It documents what we tried and learned. It is NOT used as behavioral qualification until the activation routes are resolved.

---

## Architecture Summary

### Subprocess Decoupling

```
Ableton Live (session instance)
    └─ MCP: set "A Enable" = 1.0
       └─ Serum VST3 (Ableton's running instance)
          └─ OSC1 is now enabled (in Ableton only)

DawDreamer (subprocess)
    └─ Fresh Serum VST3 process
       └─ Loads state via CBOR
       └─ State includes "A Enable" = 0.0 (unaffected by Ableton MCP)
       └─ OSC1 remains inactive (in subprocess)
       └─ CBOR level mutation has no audio effect
```

**Result:** Structural activation commands (MCP parameters) cannot propagate from Ableton into the isolated DawDreamer subprocess.

---

## Behavioral Qualification Boundary

**Controls qualified for behavioral evidence:**
- Filter1.Cutoff ✓

**Controls blocked by activation route unavailability:**
- OSC1.Level, OSC1.Detune
- Filter2.Cutoff
- Env1.Attack, Env1.Release
- OSC2.Detune
- FXEQ.Freq1 (FX require explicit loading)

**Controls below threshold but mechanically sound:**
- Filter1.Resonance (effect observed but small)

---

## No Further Behavioral Experiments

- Do NOT run 12-control seed again
- Do NOT build new activation machinery
- Do NOT recalibrate thresholds
- Do NOT create CapabilityContracts for unavailable-route controls

**Frozen status:** Behavioral evidence boundary is stable. Next work will be on host-parameter layer (Ableton MCP) or preset-based approach, not subprocess CBOR.

---

## Next Phase

Proceed to YouTube transcript system (Phase B).

Controls will remain marked as:
- `CONTROLLABLE` (via Ableton MCP)
- `NOT_BEHAVIORALLY_QUALIFIED_IN_SUBPROCESS`

For future qualification: Implement separate MCP-based behavioral harness that captures Ableton's running instance state, not subprocess state.
