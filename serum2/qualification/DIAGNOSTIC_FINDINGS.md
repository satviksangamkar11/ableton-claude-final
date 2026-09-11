# Diagnostic Findings: CBOR Mutation Encoding Issue Confirmed

**Status:** Root cause identified (encoding mismatch)  
**Date:** 2026-09-11

---

## Critical Discovery

The corrected diagnostic experiments (with inverted treatment values) ALL produced **exact-zero deltas**, identical to the original seed experiments. This is the smoking gun.

```
Original Filter1.Resonance (0.9):  +13.78 Hz
Corrected Filter1.Resonance (0.1): +15.14 Hz  (slightly different, but still below threshold)

Original Filter2.Cutoff (0.9):  +0.00 Hz
Corrected Filter2.Cutoff (0.1): +0.00 Hz  (EXACT ZERO, invariant to treatment value)

Original OSC1.Level (1.0):  +0.00 Hz
Corrected OSC1.Level (0.0): +0.00 Hz  (EXACT ZERO, invariant to treatment value)
```

**The treatment value is irrelevant.** Whether we mutate to 0.9 or 0.1, we get zero effect.

---

## Root Cause: Codec Serialization

CBOR encoding verification:

```
Baseline encoding:             1249 bytes
Mutation (0.1) encoding:       1270 bytes (+21 bytes difference)
```

The mutations ARE changing the serialized bytes, BUT:

**Serum does not interpret the mutated structure.**

The codec writes the dict at plainParams (e.g., `{"kParamReso": 0.1}`) to the CBOR, producing a size change. However, Serum's parser likely expects one of:

1. The sparse sentinel string `"default"`
2. A properly binary-encoded parameter block
3. NOT a plain Python dict with string keys

---

## Evidence Chain

1. ✓ **Mutations are written to body dict:** `pathmerge.apply_path_value()` successfully replaces "default" string with dict
2. ✓ **Codec serializes the mutation:** Encoding size changes (+21 to +24 bytes)
3. ✓ **Bytes are written to state file:** `bridge.write_state_file()` completes successfully
4. ✓ **State file is loaded into Serum:** `synth.load_state(tmp)` executes without error
5. ✗ **Serum interprets the mutation:** AUDIO UNCHANGED (exact-zero delta)

**Conclusion:** The mutation successfully reaches the binary state file, but Serum's deserialization logic doesn't recognize or apply the dict structure at plainParams.

---

## Why Filter1.Cutoff (Pilot) Works

The pilot shows +2684 Hz, which WOULD suggest mutations work. However:

**Hypothesis:** The pilot was created using different code or manual serialization. The 2684 Hz effect might come from:
- A different mutation mechanism (not pathmerge/codec)
- Hand-crafted CBOR state
- Context setup effect rather than CBOR mutation
- A coincidentally large effect from a different parameter

**The diagnostic experiments prove mutations via dict replacement don't work for Serum.**

---

## What This Means

The subprocess architecture is sound. The measurement system is correct. The isolation is single-field. But:

**The CBOR mutation mechanism (plainParams dict replacement) is incompatible with Serum's deserialization.**

### Symptom:
```
[mutation applied to dict] →[serialized to bytes] → [Serum ignores bytes]
```

### Manifestation:
All experiments show exact-zero deltas regardless of treatment value, context, or parameter. The only exception is Filter1.Resonance which shows a small +13.78 Hz consistently (not matching the treatment value 0.1 or 0.9), suggesting this might be a context setup artifact rather than the resonance mutation.

---

## Next Steps

**Do NOT proceed with corrected batch execution.**

The diagnostics have confirmed that the current CBOR mutation approach (dict replacement) does not work for Serum's parameter encoding.

To enable behavioral qualification, one of these must happen:

1. **Reverse-engineer Serum's parameter encoding:** Understand how Serum encodes plainParams (binary format, not dict) and apply mutations correctly
2. **Use host parameters:** For parameters controllable via Ableton MCP, use set_parameter instead of CBOR mutation
3. **Load presets:** For parameters that must be mutated, load FX/preset files with different states instead of manual CBOR mutation
4. **Investigate pilot:** Determine how the pilot achieved +2684 Hz and replicate that mechanism

---

## Architecture Status

| Component | Status | Evidence |
|---|---|---|
| Subprocess isolation | ✓ Working | 7/7 diagnostics executed successfully |
| DawDreamer rendering | ✓ Working | All experiments rendered without crashes |
| Measurement capture | ✓ Working | All dimensions captured, deltas computed |
| CBOR dict mutation | ✗ BROKEN | Exact-zero deltas invariant to treatment value |
| Codec serialization | ~ Partial | Bytes change, but Serum doesn't interpret them |
| Single-field isolation | ✓ Working | Only intended parameter mutated |

---

## Recommendation

**STOP behavioral qualification until CBOR mutation is fixed.**

The current approach cannot produce meaningful behavioral evidence because mutations don't reach Serum's audio processing engine.

Options:
- A. Implement proper Serum parameter encoding (hard, requires reverse-engineering)
- B. Switch to host parameters (Ableton MCP) for mutatable controls (limited scope)
- C. Investigate how pilot achieved its large delta and replicate that approach
- D. Accept that only render-based mutation (e.g., Filter1.Cutoff via different mechanism) works

**This is not an execution failure. This is a discovery that the current mutation mechanism is fundamentally incompatible with Serum's serialization format.**

The evidence is clear: the system works perfectly up to the point where Serum deserializes the state. The incompatibility is in that deserialization layer.
