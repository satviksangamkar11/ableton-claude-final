# Serum 2.0.21 Target Reconciliation Audit

**Date**: 2026-09-16  
**Phase**: 2 (Target Reconciliation) — Preparation  
**Scope**: Establish bidirectional mapping between frozen semantic inventory and existing targets  
**Discipline**: No UI probing. Text-only extraction + reconciliation from frozen evidence and existing code.  
**Next Action**: Execute the 5-phase reconciliation process

---

## Executive Summary

The semantic freeze (APPROVED 2026-09-16) established that Serum 2.0.21 has **559+ user-facing controls** across 14 sections:

- **528+ VERIFIED** controls with direct UI evidence
- **24+ PROVEN_NOT_USER_CONTROL** (correctly excluded)
- **4 UNVERIFIED_CANDIDATE** (P2, non-blocking)

The project currently has **~130+ semantic targets** defined in `serum2/compiler/targets.py`, mapping semantic names to VST3 capability keys.

**Critical Finding**: The semantic universe (what controls exist) ≠ target universe (how those controls are implemented). This reconciliation bridges the gap.

---

## Phase 1: Extract Both Vocabularies

### A. Frozen Semantic Vocabulary

**Source**: `SERUM2_SEMANTIC_INVENTORY.json` v1.2.0-CROSS-SYSTEM-RECONCILIATION-PHASE-1

**What to extract per semantic record**:
```
- semantic_id (e.g., OSC1.ENABLE, FILTER1.CUTOFF, ENV1.HOLD)
- section (OSC, FILTER, ENV, LFO, MATRIX, MIXER, FX, ARP, CLIP, GLOBAL_KEYBOARD, VOICE, GLOBAL, BROWSER)
- module (OSC1, OSC2, etc.)
- submodule (if any)
- label (user-visible label in UI)
- control_type (BOOLEAN, ENUM, SCALAR, ACTION, etc.)
- value_range (e.g., "0.0-1.0", "0-127")
- options (array for enums)
- conditional_visibility (gate conditions)
- conditions (list of gating rules)
- cross_references (other sections' semantics this references)
- resource_dependency (browser workflows, presets, etc.)
- structural_action (is this a menu/interaction, not a parameter?)
- status (VERIFIED, PROVEN_NOT_USER_CONTROL, UNVERIFIED_CANDIDATE)
- sources (evidence trails)
- evidence_type (OFFICIAL_DOCS, DIRECT_UI_OBSERVATION, SCREENSHOT, etc.)
```

**Expected count**: 559+ total records
- MACRO: ~8 records
- OSC: ~50+ records (5 oscillators × ~10 controls each)
- FILTER: ~88 records (44 controls × 2 filters)
- ENV: ~36 records (9 controls × 4 envelopes)
- LFO: ~90 records (15 controls × 6 visible + 0 × 4 headless)
- MATRIX: ~40 records (structural + routing)
- MIXER: ~66 records (11 channel families × ~6 controls each)
- FX: ~173 records (13 processors + 3 splitters + 3 racks)
- ARP: ~49 records (after KEYBOARD re-homing)
- CLIP: ~28 records
- GLOBAL_KEYBOARD: ~21 records (after VOICE re-homing)
- VOICE: ~8 records
- GLOBAL: ~31 records
- BROWSER: ~41 records

### B. Existing Target Vocabulary

**Source**: `serum2/compiler/targets.py` SEMANTIC_TARGETS dictionary

**What to extract per target**:
```
- semantic_name (e.g., "OSC1.Enable", "Filter.Cutoff")
- capability_key (VST3 field name, e.g., "oscillator_field_OSC1-ENABLE")
- target_source (VST3_PARAMETER, UI_ACTION, STRUCTURAL_OPERATION, RESOURCE_OPERATION, MATRIX_ROUTE, OTHER)
- current_operation_support (IMPLEMENTED, NOT_IMPLEMENTED, UNPROVEN)
- mutation_path (if known from existing contracts)
- evidence_refs (references to CapabilityContract, if any)
```

**Expected count**: 130+ targets currently defined
- OSC family: ~40 targets (OSC1-3, SUB, NOISE with Enable/Octave/Volume/Level/Pan/Routing/Detune/Warp/etc.)
- Filter family: ~15 targets (Filter1/2 with Cutoff/Resonance/Type/Drive/Q, plus BUS sends and routing)
- Envelope family: ~16 targets (Env1-4 with Attack/Decay/Sustain/Release)
- LFO family: ~50 targets (LFO0-9 with Rate/Shape/Mode/Phase/Retrigger)
- FX family: ~45+ targets (EQ, Distortion, Delay, Reverb, Compressor, Chorus, etc.)
- Global family: ~12 targets (MasterVolume, Transpose, Tuning, Quality, Swing, Scale, Key, Portamento, etc.)
- ModRoute family: ~5 targets (Curve, Bipolar, AuxSource, etc.)

---

## Phase 2: Normalize Both Vocabularies

**Goal**: Create canonical forms that can be compared directly.

### A. Semantic Normalization

For each frozen semantic record, create a canonical entry:
```json
{
  "semantic_id": "normalized without special characters",
  "section": "parent section",
  "module": "submodule if any",
  "control_type": "standardized type (BOOLEAN, ENUM, SCALAR, STRUCTURAL)",
  "evidence_status": "VERIFIED or PROVEN_NOT_USER_CONTROL or UNVERIFIED_CANDIDATE",
  "ui_observable": "is this a genuine user-facing UI control?",
  "runtime_controllable": "can this be mutated at runtime (vs display-only)?",
  "persistent": "does state persist across preset loads?",
  "automatable": "can this be modulated/automated?"
}
```

### B. Target Normalization

For each existing target, create a canonical entry:
```json
{
  "semantic_name": "from targets.py key",
  "capability_key": "VST3 field name",
  "host_parameter_name": "if known, the VST3 parameter name",
  "target_source": "VST3_PARAMETER or other",
  "operation_supported": "from existing CapabilityContracts or UNKNOWN",
  "evidence_status": "IMPLEMENTED or DISCOVERED_NOT_IMPLEMENTED or UNPROVEN"
}
```

---

## Phase 3: Build Bidirectional Reconciliation Matrix

**Critical**: Map in BOTH directions:
- semantic_id → target_id (catches semantics with no targets)
- target_id → semantic_id (catches orphan targets with no semantics)

### Mapping Classes

| Class | Meaning | Example |
|-------|---------|---------|
| EXACT | 1:1 semantic ↔ target | OSC1.Enable ↔ OSC1.Enable |
| ONE_TO_MANY | 1 semantic maps to N targets | ENV1.Hold → none (gap) or multiple if intermediate targets exist |
| MANY_TO_ONE | N semantics share 1 target | FILTER1.Cutoff + FILTER2.Cutoff → both use "Filter.Cutoff" (ambiguous) |
| NO_TARGET | semantic has no target | ENV1.Hold (DISCOVERED_NOT_IMPLEMENTED) |
| NO_SEMANTIC | target has no semantic | (potential orphan — rare in this project) |
| UNKNOWN | ambiguous or conflict | conflicting evidence |

### Gap Analysis per Mapping Class

- **EXACT**: No action needed; 1:1 confirmed
- **ONE_TO_MANY**: Semantic maps to multiple targets (routing/modulation scenarios); document the family
- **MANY_TO_ONE**: Multiple semantics share target (filter 1 vs 2); disambiguate in targets.py or accept as shared family
- **NO_TARGET**: Create target stub or mark as NOT_YET_IMPLEMENTED
- **NO_SEMANTIC**: Flag as potential orphan (rare); may indicate undocumented capability or stale target

---

## Phase 4: Derive Representation Families

**Critical Rule**: Families derive from BEHAVIOR, NOT VST3 naming.

### Behavioral Properties That Define Families

| Property | Options | Example |
|----------|---------|---------|
| Mutability | READ_WRITE, READ_ONLY, WRITE_ONLY | Most params are READ_WRITE |
| Persistence | PERSISTENT, TRANSIENT, SESSION | Parameter state persists; live input (ModWheel) is transient |
| Automation | AUTOMATABLE, NOT_AUTOMATABLE | Modulation matrix routes ↔ automatable parameters |
| Value Type | BOOLEAN, ENUM, SCALAR_RANGE, ACTION | Covers all semantic control types |
| Scope | VOICE, GLOBAL, PATTERN | Voice-scoped (per note) vs global (whole synth) |

### Example Families

```
FAMILY: BOOLEAN_READ_WRITE_PERSIST_GLOBAL
  Members:
    - OSC1.Enable
    - OSC2.Enable
    - OSC3.Enable
    - NOISE.Enable
    - Filter1.Enable
    - Filter2.Enable
  Behavioral Contract:
    - Read: get current toggle state (true/false)
    - Write: set toggle state
    - Persist: state survives preset loads
    - Automate: yes, via MATRIX
  Single Deep Experiment:
    - Prove one member (e.g., OSC1.Enable) with full read/write/persist/automation evidence
    - Assume all family members share identical semantics (index/instance only differs)

FAMILY: SCALAR_NUMERIC_RANGE_0_1_READ_WRITE_PERSIST_VOICE
  Members:
    - OSC1.Volume
    - OSC2.Volume
    - OSC3.Volume
    - SUB.Volume
    - NOISE.Volume
  Behavioral Contract:
    - Range: 0.0 to 1.0 (or native VST3 range)
    - Read: get current value
    - Write: set to any value in range
    - Persist: state survives preset loads
    - Automate: yes, via MATRIX
  Single Deep Experiment:
    - Prove OSC1.Volume with exact mutation path and persistence logic
    - Reuse for OSC2, OSC3, etc. (same path template, different indices)

FAMILY: ENUM_DISCRETE_OPTIONS_READ_WRITE_PERSIST_GLOBAL
  Members:
    - OSC1.Type (5 options)
    - Filter1.Type (107 options)
    - Filter2.Type (107 options)
    - LFO.Type (5 options)
  Behavioral Contract:
    - Options: discrete set (not range)
    - Read: get current selection index or name
    - Write: set to valid option
    - Persist: state survives preset loads
    - Automate: varies (some enums automatable via MATRIX, some not)
  Deep Experiments per Subfamily:
    - 5-option enum (LFO.Type): prove all 5 options + edge cases
    - 100+ option enum (FILTER.Type): prove category boundaries + edge types
```

---

## Phase 5: Select Minimum Deep Experiments

**Goal**: For each representation family, select ONE representative semantic to deep-test. Proven family patterns reused for all family members.

### Experiment Selection Criteria

Per family, choose ONE member that:
1. Has the most complete prior evidence (from Phase 1 closure)
2. Has the clearest operation path (shortest mutation_target_path in contracts)
3. Covers the full behavioral contract (read, write, persist, automation)
4. Preferably already has some CapabilityContract evidence from prior work

### Example Experiment Plan

| Family | Representative | Experiment | Expected Proof |
|--------|-----------------|------------|----------------|
| BOOLEAN_GLOBAL | OSC1.Enable | Mutate OSC1 Enable toggle, read back, restore | read_supported=true, write_supported=true, persistent=true, automatable=true |
| SCALAR_VOICE | OSC1.Volume | Mutate OSC1 Volume to 0.5, read back, restore | exact_value_read=0.5, range_limits, persistence_across_preset_reload |
| ENUM_5_OPTION | LFO1.Type | Select each of 5 types, confirm menu + UI state changes | all_5_options_selectable, read_back_accurate |
| ENUM_100_OPTION | FILTER1.Type | Spot-check 10 types (edge cases + common), confirm category boundaries | category_membership_accurate, option_ordering_preserved |
| MATRIX_ROUTE | ModRoute[0].Curve | Create route with different curve values, confirm modulation output differs | route_creation_works, curve_affects_output_measurable |
| RESOURCE_LOAD | BROWSER.PresetLoad | Load preset via single click, confirm state changes | atomic_load_operation, all_parameters_affected_correctly |

---

## Critical Gaps Anticipated

Based on Phase 1 closure evidence:

### Known Gaps (NO_TARGET)

| Semantic | Section | Status | Impact |
|----------|---------|--------|--------|
| ENV1.Hold | ENV | VERIFIED control, NO target | 4 missing Hold targets (Env1-4) |
| ENV1.BPM (TimeMode) | ENV | VERIFIED control, NO target | 4 missing TimeMode targets |
| ENV1.LegatoInverted | ENV | VERIFIED control, NO target | 4 missing LegatoInverted targets |
| ENV1.VoiceStealRetriggerMode | ENV | VERIFIED control, NO target | 4 missing VSRetrigger targets |
| FILTER.Pan | FILTER | VERIFIED control (per-channel in MIXER section), routing unknown | 2+ Pan targets may be missing per filter |
| MATRIX.CVY (Curve Visualization) | MATRIX | VERIFIED structural, NO target | graphic display, not runtime-controllable |
| All 20 FILTER type-specific 4th-knob controls | FILTER | VERIFIED (20 per filter × 2 = 40 controls), ~0% target coverage | 40 missing targets for type-specific parameters |
| ARP rhythm controls | ARP | VERIFIED menu, NO targets for pattern/rate/mode mutation | Full ARP control missing |
| CLIP recording controls | CLIP | VERIFIED UI, NO targets for record/overdub operations | Recording workflow not targetable |

### Known Ambiguities (MANY_TO_ONE or ONE_TO_MANY)

| Issue | Semantics | Targets | Conflict | Resolution Path |
|-------|-----------|---------|----------|-----------------|
| Filter 1 vs 2 | FILTER1.*, FILTER2.* | Filter.Cutoff, Filter2.Cutoff (mixed naming) | Generic "Filter.*" vs "Filter2.*" inconsistency | Reconcile targets.py naming: use FILTER1.* and FILTER2.* exclusively, no generic Filter.* |
| FX Enable/Disable | FX module enable toggles | ModRoute.Bypass (matrix route disable, not module disable) | Semantic: FX module on/off; Target: route bypass (different semantics) | Clarify: is FX module enable a VST3 parameter or structural/UI-only? |
| OSC Wavetable | OSC1.Wavetable (17+ params) | OSC1.Wavetable (single target) | Semantic: wavetable SELECTION + position + loop mode + etc. Target: only selection | One target for multi-dimensional semantic; requires clarification of sub-targets |

---

## Reconciliation Rules

1. **Frozen inventory is authoritative**: If Phase 1 found a control, it exists. No re-discovery.
2. **No VST3 index assumptions**: Semantic count ≠ VST3 parameter count.
3. **Bidirectional validation**: Every semantic must map to target(s); every target should map to semantic.
4. **Family derivation from behavior**: Don't assume family membership from VST3 naming; prove it via operation semantics.
5. **Minimum experiments**: One proven experiment per family; reuse the path for all family members.
6. **No shortcuts to implementation**: Complete this reconciliation BEFORE writing any operation code.

---

## Next Actions

1. **Execute Phase 1**: Extract 559+ semantic records from frozen inventory (text only, no UI)
2. **Execute Phase 1B**: Extract ~130+ targets from targets.py
3. **Execute Phase 2**: Normalize both vocabularies into comparable forms
4. **Execute Phase 3**: Build complete bidirectional reconciliation matrix (all 559+ rows)
5. **Execute Phase 4**: Enumerate all gaps (orphan targets, missing targets, ambiguities) with explicit disposition
6. **Execute Phase 5**: Identify ~15-25 representation families based on behavioral contracts
7. **Execute Phase 5B**: Select minimum set of representative semantics for deep experiments (one per family)
8. **Publish Audit**: Complete reconciliation audit with gap analysis, family derivation, and experiment plan
9. **THEN and ONLY THEN**: Begin Phase 3 deep experiments on selected representatives

---

## Handoff Criteria (When This Audit Is Complete)

✅ All 559+ semantic records extracted and normalized  
✅ All ~130+ targets extracted and normalized  
✅ Bidirectional reconciliation matrix complete (semantic → target AND target → semantic)  
✅ Gap analysis complete (orphan targets, missing targets, ambiguities enumerated with disposition)  
✅ Representation families derived from behavioral properties, not naming  
✅ Minimum set of deep experiments selected (one per family)  
✅ No undocumented assumptions about VST3 parameter structure  
✅ Ready for Phase 3: Begin experiments on selected representatives

---

**Status**: PHASE 2 AUDIT PREPARED  
**Ready for**: Phase 1 execution (extract vocabularies)  
**No UI work**: This is text-only reconciliation using frozen evidence  
**Handoff**: To Phase 3 when extraction + normalization + reconciliation complete
