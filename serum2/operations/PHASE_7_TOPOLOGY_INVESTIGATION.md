# Phase 7: Topology/Module Operations Investigation

**Date:** 2026-09-13  
**Method:** Evidence-based analysis using existing SEMANTIC_TARGETS and corpus

---

## Operations Investigated

### 1. Oscillator Activation (OSC1/OSC2/OSC3)

**OSC1 (Oscillator 1):**
- Semantic target: ✅ `OSC1.Enable` exists in SEMANTIC_TARGETS
- Capability key: `oscillator_field_OSC-ENABLE`
- Status: **CONTROL-COMPLETE** (already implemented in Phase 2 as scalar operation)

**OSC2 (Oscillator 2):**
- Semantic target: ❌ NOT in SEMANTIC_TARGETS
- Corpus evidence: ❌ NOT found in qualification files
- State representation: ❌ NOT confirmed
- Status: **CONTROL-UNRESOLVED** (no evidence to implement)

**OSC3 (Oscillator 3):**
- Semantic target: ❌ NOT in SEMANTIC_TARGETS
- Corpus evidence: ❌ NOT found
- State representation: ❌ NOT confirmed
- Status: **CONTROL-UNRESOLVED**

### 2. Module Enable/Disable (Generic)

**Filter Enable:**
- Semantic target: ❌ NOT in SEMANTIC_TARGETS
- Status: **CONTROL-UNRESOLVED**

**LFO Enable:**
- Semantic target: ❌ NOT in SEMANTIC_TARGETS
- Status: **CONTROL-UNRESOLVED**

**Macro Enable:**
- Semantic target: ❌ NOT in SEMANTIC_TARGETS
- Status: **CONTROL-UNRESOLVED**

---

### 3. FX Enable/Bypass

**FX Enable/Bypass fields:**
- Semantic target: ❌ NOT in SEMANTIC_TARGETS
- Evidence: FORENSIC notes "enable mechanism TBD"
- Corpus: ❌ NOT confirmed
- Status: **CONTROL-UNRESOLVED**

### 4. FX Topology (Reordering)

**FX slot reordering:**
- State structure: Exists (FXRack0.FX is an array-like structure)
- Reordering mechanism: ❌ NOT established
- Mutation strategy: ❌ NOT defined
- Status: **CONTROL-UNRESOLVED** (structure exists but mutation semantics unclear)

### 5. Multisample Resource

**Multisample state field:**
- Expected path: `Oscillator{i}.MultiSampleOsc{i}.relativePathToMultisample`
- Corpus evidence: ❌ NOT found in any qualification files
- State representation: ❌ NOT confirmed
- Status: **CONTROL-UNRESOLVED** (model ready but execution path not verified)

---

## Classification Summary

| Operation | Semantic Target | Corpus Evidence | State Field | Status |
|-----------|-----------------|-----------------|-------------|--------|
| OSC1.Enable | ✅ | ✅ (Phase 2) | ✅ | COMPLETE |
| OSC2.Enable | ❌ | ❌ | ❌ | UNRESOLVED |
| OSC3.Enable | ❌ | ❌ | ❌ | UNRESOLVED |
| Filter.Enable | ❌ | ❌ | ❌ | UNRESOLVED |
| LFO.Enable | ❌ | ❌ | ❌ | UNRESOLVED |
| Macro.Enable | ❌ | ❌ | ❌ | UNRESOLVED |
| FX.Enable | ❌ | ❌ | ❌ | UNRESOLVED |
| FX Reorder | ❌ | ✅ (struct) | ❌ (mutation) | UNRESOLVED |
| Load Multisample | ❌ | ❌ | ❌ | UNRESOLVED |

---

## Evidence Requirement

Per CLAUDE.md section 1: "Unknown capability remains unknown rather than being guessed or laundered into plausibility."

**Application:** Do not implement topology/module operations without evidence that:
1. Semantic target exists in SEMANTIC_TARGETS
2. State field is confirmed in actual Serum corpus
3. Mutation strategy is established

**Result:** All remaining operations must remain CONTROL-UNRESOLVED in Phase 7.

---

## Recommendation

Phase 7 should:
1. Document these operations as explicitly unresolved
2. Create a final Serum control completeness report
3. Stop implementation until evidence is collected for remaining operations
4. Do not proceed to behavioral qualification (Phase D/E) without closure on what CAN be controlled

