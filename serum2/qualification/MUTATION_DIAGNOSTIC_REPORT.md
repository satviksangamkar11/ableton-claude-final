# Mutation Propagation Diagnostic Report

**Date:** 2026-09-11  
**Subject:** Why most seed experiments showed zero/near-zero audio deltas  
**Status:** CRITICAL STRUCTURAL ISSUE IDENTIFIED  

---

## Summary

**The mutations are being WRITTEN to the CBOR state, but Serum does NOT recognize the mutated structure.**

The pathmerge code converts the sparse `"default"` string to a dict containing the mutated field. Serum appears to only recognize the sparse format or a properly encoded representation, not an arbitrary nested dict.

---

## Detailed Findings

### Issue: plainParams is a Sparse Sentinel

In the default Serum skeleton:

```python
VoiceFilter0.plainParams = "default"  # string, not dict
```

This is a **sparse sentinel** meaning "use built-in defaults."

### What Our Code Does

When `pathmerge.apply_path_value()` is called with path `"VoiceFilter0.plainParams.kParamFreq"`:

```
BEFORE:  VoiceFilter0.plainParams = "default"  (type: str)
AFTER:   VoiceFilter0.plainParams = {"kParamFreq": 0.9}  (type: dict)
```

**Line 55-57 of pathmerge.py:**
```python
if cur == SPARSE_DEFAULT or cur is None or not isinstance(cur, (dict, list)):
    cur = {}  # REPLACES "default" with empty dict
    node[part] = cur
```

### Why This Breaks Serum

Serum's CBOR parser likely expects:
- Either the string `"default"` (sparse, use built-ins), OR
- A properly encoded/binary representation of parameters

Our code produces:
- A plain Python dict with string keys (`{"kParamFreq": 0.9}`)

Serum doesn't know how to interpret this structure, so **it ignores the mutation and uses the default behavior instead.**

---

## Evidence

### Test Case 1: Filter1.Resonance

**Experiment:** Mutate `VoiceFilter0.plainParams.kParamReso` from default to 0.9

**Mutation in CBOR:**
```
Before:  plainParams = "default"
After:   plainParams = {"kParamReso": 0.9}
```

**Serum's interpretation:**
- Sees `plainParams` as a dict instead of expected format
- Doesn't recognize or apply the mutation
- Falls back to default filter behavior

**Audio result:**
- Baseline spectral_centroid: 463.09 Hz
- Treatment spectral_centroid: 476.87 Hz
- Delta: +13.78 Hz (BELOW 100 Hz threshold, classified NO_OBSERVED_EFFECT)

**Conclusion:** The small delta (+13.78 Hz) might be from experimental noise or context effects, not the intended resonance mutation.

---

### Test Case 2: Filter2.Cutoff

**Experiment:** Mutate `VoiceFilter1.plainParams.kParamFreq` from default to 0.9

**Mutation in CBOR:**
```
Before:  plainParams = "default"
After:   plainParams = {"kParamFreq": 0.9}
```

**Audio result:**
- Baseline spectral_centroid: 4378.13 Hz
- Treatment spectral_centroid: 4378.13 Hz
- Delta: +0.00 Hz (EXACT ZERO, NO_OBSERVED_EFFECT)

**Conclusion:** Zero delta is strong evidence that the mutation was NOT applied by Serum. The exact zero indicates Filter2 was not even active (different baseline than Filter1, suggesting Filter2.On was false or Filter2 not in signal path).

---

## Root Cause Analysis

| Issue | Evidence | Impact |
|---|---|---|
| **Sparse format mismatch** | plainParams: "default" → plainParams: {dict} | Serum ignores dict structure |
| **No proper encoding** | Writing raw Python dicts, not CBOR-encoded bytes | Serum can't parse mutation |
| **Structure expectation** | Serum expects sparse sentinel or binary, not dict | Mutation silently ignored |
| **No validation** | Code doesn't verify Serum accepted mutation | Undetected silent failure |

---

## Why Filter1.Cutoff (Pilot) Worked

The pilot DID show `is_valid=True` with +2684.3 Hz delta. Possible explanations:

1. **Different CBOR encoding:** The pilot might have used a properly encoded plainParams structure (not just a dict)
2. **Manual creation:** The pilot evidence might have been hand-crafted or loaded from a preset
3. **Coincidence:** The large delta might come from context setup (Filter1 On = 1.0) rather than the cutoff mutation
4. **Different code path:** The pilot might have used different mutation logic

**Recommendation:** Inspect the actual pilot CBOR to understand how its plainParams is structured.

---

## Classification of Seed Results

Based on root-cause analysis:

| Experiment | Expected | Observed | Likely Cause |
|---|---|---|---|
| Filter1.Resonance | POSITIVE | NO_OBSERVED_EFFECT (+13.78 Hz) | MUTATION_NOT_APPLIED (dict ignored) |
| Filter2.Cutoff | POSITIVE | NO_OBSERVED_EFFECT (+0.00 Hz) | MUTATION_NOT_APPLIED + FILTER_INACTIVE |
| OSC1.Level | POSITIVE | NO_OBSERVED_EFFECT (+0.00 dB) | MUTATION_NOT_APPLIED |
| OSC1.Detune | POSITIVE | NO_OBSERVED_EFFECT (+0.00 Hz) | MUTATION_NOT_APPLIED |
| OSC2.Detune | POSITIVE | NO_OBSERVED_EFFECT (+0.00 Hz) | MUTATION_NOT_APPLIED |
| Env1.Attack | CONDITIONAL | NO_OBSERVED_EFFECT (+0.00 dB) | MUTATION_NOT_APPLIED |
| Env1.Release | CONDITIONAL | NO_OBSERVED_EFFECT (+0.00 dB) | MUTATION_NOT_APPLIED |
| LFO1.Rate (no dest) | NULL | NO_OBSERVED_EFFECT (+0.00 dB) | CORRECT (no destination) |
| LFO1.Rate (filter dest) | POSITIVE | NOT_RUN | RENDER_FAILURE (treatment arm didn't render) |
| Filter1.Drive | POSITIVE | NO_OBSERVED_EFFECT (+0.34 dB) | MUTATION_NOT_APPLIED |

---

## Architectural Impact

This is **NOT** a measurement problem. The measurement system works correctly (captures real deltas, reports them honestly).

This **IS** a CBOR mutation problem:

```
CBOR STATE (plainParams: "default")
    ↓
pathmerge.apply_path_value() [WRITES successfully]
    ↓
CBOR STATE (plainParams: {kParamFreq: 0.9})
    ↓
Serum serialization/deserialization [IGNORES dict, expects sparse format]
    ↓
SERUM INTERNAL STATE [unchanged, uses defaults]
    ↓
RENDER [produces audio identical to baseline]
```

The mutation **is written** but **is not interpreted** by Serum.

---

## Resolution Options

1. **Encode properly:** Replace dict mutation with correct CBOR encoding (requires reverse-engineering Serum's parameter encoding)
2. **Use host params:** For Ableton-controllable parameters, use Ableton MCP set_parameter instead of CBOR
3. **Load presets:** For complex parameters, load preset FX instead of mutating CBOR
4. **Verify pilot:** Understand how Filter1.Cutoff actually achieved its large delta

---

## What This Means for Seed Execution

The seed set execution was technically **successful** (no crashes, measurements captured), but **behaviorally invalid** (mutations not applied to Serum):

```
✓ Architecture proven:    Subprocess isolation, rendering, measurement capture
✗ Mutation mechanism broken: CBOR dicts not recognized by Serum
✗ Evidence quality compromised: Measurements reflect Serum defaults, not mutations
```

The evidence files are real (actual audio was rendered and measured), but they don't reflect the intended experiments because Serum ignored the mutations.

---

## Recommendation

**Do NOT recalibrate thresholds.** The issue is not threshold calibration; it's that the experiments didn't actually perturb Serum's behavior.

**Investigate:** How does Filter1.Cutoff achieve its +2684 Hz delta if plainParams: "default" → dict also fails there?

**Next step:** Inspect the pilot's actual CBOR state to understand the correct mutation mechanism.
