---
title: Phase 2 — Cross-System Reconciliation (Auditable)
subtitle: 14 Canonical Relationships Reconciled with Complete Evidence
date: 2026-09-16
inventory_version: 1.3.0-CROSS-SYSTEM-RECONCILIATION-PHASE-2-COMPLETE
---

# Phase 2: Cross-System Reconciliation

**Methodology**: Reconcile all 14 cross-system relationships using existing Phase 1 section-closure evidence. Apply the reconciliation rule: "Does this relationship introduce a NEW user-facing semantic control or state?"

**Canonical Relationship IDs**: CS-01 through CS-14 (permanent, position-independent identifiers)

**Status**: ✅ COMPLETE — All 14 relationships reconciled using existing evidence (no new UI discovery performed).

---

## Canonical Cross-System Relationship Registry

### CS-01: OSC ↔ MATRIX

**Relationship**: Oscillators routed to MATRIX modulation destinations

**Type**: Routing + Modulation

**Existing Semantic IDs**:
- OSC.1–5 (oscillator enable/disable state)
- MATRIX.SOURCE.OSC_1–5 (modulation routing)
- MATRIX.ROUTING.SIGNAL_BALANCE (oscillator amplitude for modulation)

**Evidence References**:
- OSC section closure (inventory v1.2.0): OSC.1–5 oscillators documented with enable/disable
- MATRIX section closure (inventory v1.2.0): 64-slot matrix with SOURCE domain includes OSC.1–5 modulation targets
- MATRIX ROUTING.SIGNAL_BALANCE documented as existing control within MATRIX section

**New Semantic Identity?**: NO

**Ownership**: MATRIX owns routing destination specification and modulation amplitude control; OSC owns oscillator synthesis state

**Conditionality**: Modulation application conditional on MATRIX destination row selection and oscillator enable state

**Structural Effect**: None (existing routing topology)

**Resource Effect**: None

**Disposition**: REFERENCE_ONLY

**Unresolved Issue**: None

**Blocking Status**: NOT BLOCKING

---

### CS-02: FILTER ↔ MATRIX

**Relationship**: Filters routed to MATRIX modulation destinations

**Type**: Routing + Modulation

**Existing Semantic IDs**:
- FILTER.1–2 (filter enable/disable state)
- MATRIX.SOURCE.FILTER_1–2 (modulation routing)
- MATRIX.ROUTING.SIGNAL_BALANCE (filter amplitude for modulation)

**Evidence References**:
- FILTER section closure (inventory v1.2.0): FILTER.1–2 documented with enable/disable
- MATRIX section closure (inventory v1.2.0): 64-slot matrix with SOURCE domain includes FILTER.1–2 modulation targets
- MATRIX ROUTING.SIGNAL_BALANCE documented as existing control within MATRIX section

**New Semantic Identity?**: NO

**Ownership**: MATRIX owns routing destination specification; FILTER owns filter synthesis state

**Conditionality**: Modulation application conditional on MATRIX destination row selection and filter enable state

**Structural Effect**: None

**Resource Effect**: None

**Disposition**: REFERENCE_ONLY

**Unresolved Issue**: None

**Blocking Status**: NOT BLOCKING

---

### CS-03: FILTER ↔ MIX

**Relationship**: Filter routing to MIXER channels exposes Filter Balance conditional control

**Type**: Routing + Conditional Control

**Existing Semantic IDs**:
- MIXER.CHANNEL.ROUTING (per-channel routing control)
- MIXER.CHANNEL.FILTER_BALANCE (conditional knob, visible only when Routing=Filter)

**Evidence References**:
- MIXER section closure (inventory v1.2.0): "Filter Balance knob only visible when channel Routing=Filter, directly verified via before/after toggle across all 5 oscillator-type channels (SUB, OSC A/B/C, NOISE)"
- Direct UI evidence: MIXER.CHANNEL.FILTER_BALANCE documented as "A-Filter Balance (-100)" with tooltip "Set how much signal is mixed between the two main filters"
- Evidence type: VERIFIED (direct observation + conditional visibility test)

**New Semantic Identity?**: NO

**Ownership**: MIXER owns both Routing dropdown and Filter Balance conditional control; Filter Balance is MIXER-scoped, not cross-system

**Conditionality**: MIXER.CHANNEL.FILTER_BALANCE visibility gated by MIXER.CHANNEL.ROUTING = "Filter"; appears only for oscillator-type channels (not BUS/MAIN/DIRECT)

**Structural Effect**: Conditional UI presentation (knob appears/disappears)

**Resource Effect**: None

**Disposition**: REFERENCE_ONLY + CONDITIONAL

**Unresolved Issue**: None (directly tested and resolved)

**Blocking Status**: NOT BLOCKING

---

### CS-04: OSC/FILTER ↔ MIX

**Relationship**: OSC and FILTER routing to MIXER channels

**Type**: Routing

**Existing Semantic IDs**:
- OSC.1–5, FILTER.1–2 (synthesis source enable/disable)
- MIXER.CHANNEL.ROUTING (per-channel routing control with options: Filter/Main/Direct/None for OSC channels; OtherFilter/Main/Direct/None for FILTER channels)
- MIXER.CHANNEL.LEVEL (per-channel amplitude)
- MIXER.CHANNEL.PAN (per-channel panning)

**Evidence References**:
- MIXER section closure (inventory v1.2.0): "11 channel families fully enumerated with independent per-channel evidence (no assumed parity) -- SUB, OSC A/B/C, NOISE (7-8 controls each: Enable, Routing[Filter/Main/Direct/None], conditional Filter Balance, BUS1, BUS2, Pan, Level, Env1-bypass toggle); FILTER1/FILTER2 (8 controls each: Enable, Routing[OtherFilter/Main/Direct/None -- CONFIRMED DIFFERENT option set from osc channels]...)"

**New Semantic Identity?**: NO

**Ownership**: MIXER owns all channel-level routing and mixing controls; OSC/FILTER own synthesis state

**Conditionality**: Channel enable state affects whether routing applies; Filter Balance conditionality scoped to FILTER routing (CS-03)

**Structural Effect**: None (existing channel topology)

**Resource Effect**: None

**Disposition**: REFERENCE_ONLY

**Unresolved Issue**: None

**Blocking Status**: NOT BLOCKING

---

### CS-05: FX ↔ MIX

**Relationship**: FX rack tabs (MAIN/BUS1/BUS2) correspond to MIXER master channels

**Type**: Structure

**Existing Semantic IDs**:
- FX.MAIN, FX.BUS1, FX.BUS2 (FX processor chains)
- MIXER.MAIN, MIXER.BUS1, MIXER.BUS2 (master channel levels)

**Evidence References**:
- FX section closure (inventory v1.2.0): "3 racks (MAIN/BUS1/BUS2) fully discovered"
- MIXER section closure (inventory v1.2.0): "DIRECT, MAIN (1 control: Main Vol, CONFIRMED NON-MODULATABLE no Mod Source); DIRECT (1 control: Direct Vol)"

**New Semantic Identity?**: NO

**Ownership**: MIXER owns master channel identities and amplitude; FX owns per-chain processor semantics

**Conditionality**: None (fixed 1:1 mapping)

**Structural Effect**: Unified naming topology across dual surfaces

**Resource Effect**: None

**Disposition**: REFERENCE_ONLY

**Unresolved Issue**: None

**Blocking Status**: NOT BLOCKING

---

### CS-06: MACRO ↔ MATRIX

**Relationship**: Macros act as modulation sources in MATRIX

**Type**: Modulation

**Existing Semantic IDs**:
- MACRO.1–8 (macro knobs)
- MATRIX.SOURCE.MACRO_1–8 (modulation routing destinations)

**Evidence References**:
- MACRO section closure (inventory v1.2.0): "All 8 Macro identities with complete context-menu and UI-behavior documentation"
- MATRIX section closure (inventory v1.2.0): "64-slot modulation matrix with source/destination enumeration complete" (includes MACRO.1–8 as SOURCE members)

**New Semantic Identity?**: NO

**Ownership**: MACRO owns macro knob state; MATRIX owns routing destination specification

**Conditionality**: Macro sources available in MATRIX.SOURCE domain; modulation application conditional on destination row selection

**Structural Effect**: None

**Resource Effect**: None

**Disposition**: REFERENCE_ONLY

**Unresolved Issue**: None

**Blocking Status**: NOT BLOCKING

---

### CS-07: MACRO ↔ CLIP

**Relationship**: CLIP.GLOBAL.SHOW_MACROS display toggle shows existing MACRO.1–8 inline

**Type**: Interaction + Display

**Existing Semantic IDs**:
- MACRO.1–8 (macro knobs)
- CLIP.GLOBAL.SHOW_MACROS (display toggle control)

**Evidence References**:
- MACRO section closure (inventory v1.2.0): "All 8 Macro identities documented"
- CLIP section closure (inventory v1.2.0): "Show Macros (confirmed reveals 8 inline Macro knobs)"
- Direct evidence: CLIP section documented "Show Macros toggle merely displays existing MACRO.1-8 controls inline; no new Macro-specific state"

**New Semantic Identity?**: NO

**Ownership**: MACRO owns macro knob state; CLIP owns Show Macros display toggle (owns which view to show, not the macro state)

**Conditionality**: Show Macros toggle conditionally displays existing MACRO.1–8 knobs inline within CLIP editor

**Structural Effect**: UI display organization (inline vs. separate panel)

**Resource Effect**: None

**Disposition**: REFERENCE_ONLY + CONDITIONAL

**Unresolved Issue**: None (directly verified in CLIP closure)

**Blocking Status**: NOT BLOCKING

---

### CS-08: KEYBOARD ↔ OSC

**Relationship**: OSC Mapping Note Range Editor contains 6 rows (SUB/OSC A/B/C/NOISE/ARP)

**Type**: Performance Input + Mapping

**Existing Semantic IDs**:
- KEYBOARD.OSC_MAPPING (full Note Range Editor with 6 rows, KEY/VEL tabs, Fold/Warp toggles, draggable key-range bar)
- OSC.1–5 (oscillator routing targets)

**Evidence References**:
- KEYBOARD section closure (inventory v1.2.0): "OSC_MAPPING: Full Note Range Editor with 6 rows (SUB/OSC A/B/C/NOISE/ARP), KEY and VEL tabs, Fold/Warp toggles per row (both VERIFIED), double-click-then-drag key-range bars (VERIFIED after discovering correct gesture), Reset All button (VERIFIED functional)."

**New Semantic Identity?**: NO

**Ownership**: KEYBOARD owns OSC Mapping editor and row selection; OSC owns oscillator routing

**Conditionality**: OSC row availability conditional on OSC enable state and KEYBOARD tab selection

**Structural Effect**: None (existing keyboard performance control structure)

**Resource Effect**: None

**Disposition**: REFERENCE_ONLY

**Unresolved Issue**: None

**Blocking Status**: NOT BLOCKING

---

### CS-09: KEYBOARD ↔ ARP

**Relationship**: OSC Mapping Note Range Editor contains ARP row

**Type**: Performance Input + Mapping

**Existing Semantic IDs**:
- KEYBOARD.OSC_MAPPING.ARP_ROW (one of 6 rows in Note Range Editor)
- ARP.* (ARP playback and pattern controls)

**Evidence References**:
- KEYBOARD section closure (inventory v1.2.0): "OSC Mapping's ARP row references existing ARP; no new cross-system semantic identity"
- ARP section closure (inventory v1.2.0): "OSC Mapping editor confirmed to launch from Keyboard/Performance bar independent of ARP/CLIP tab selection"

**New Semantic Identity?**: NO

**Ownership**: KEYBOARD owns OSC Mapping editor; ARP owns playback and pattern source state

**Conditionality**: ARP row conditional on ARP enable state

**Structural Effect**: None

**Resource Effect**: None

**Disposition**: REFERENCE_ONLY

**Unresolved Issue**: None

**Blocking Status**: NOT BLOCKING

---

### CS-10: KEYBOARD ↔ CLIP

**Relationship**: CLIP row does NOT exist in OSC Mapping; CLIP uses separate KB_SPAN control

**Type**: Performance Input + Mapping

**Existing Semantic IDs**:
- KEYBOARD.OSC_MAPPING (6 rows: SUB/OSC A/B/C/NOISE/ARP — **NO CLIP ROW**)
- CLIP.KB_SPAN (separate CLIP-owned keyboard-span control)

**Evidence References**:
- KEYBOARD section closure (inventory v1.2.0): "OSC Mapping's ARP row cross-referenced back to ARP section; no CLIP row exists (verified exhaustively)"
- CLIP section closure (inventory v1.2.0): "KB Span (4 options: Off/Mono/Poly/Offset -- CLIP-exclusive, governs keyboard-to-pitch remapping, Poly confirmed to add a slot badge)"
- Xfer official documentation: "CLIP uses separate KB_SPAN mechanism (confirmed via official Xfer documentation)"

**New Semantic Identity?**: NO

**Ownership**: KEYBOARD owns OSC Mapping (6 rows); CLIP owns KB_SPAN separate control

**Conditionality**: CLIP keyboard control is managed by CLIP.KB_SPAN, not OSC Mapping row selection

**Structural Effect**: None (CLIP has its own control mechanism, not shared via OSC Mapping)

**Resource Effect**: None

**Disposition**: REFERENCE_ONLY

**Unresolved Issue**: None (exhaustively verified: CLIP row not found, separate KB_SPAN mechanism documented)

**Blocking Status**: NOT BLOCKING

---

### CS-11: ARP ↔ OSC

**Relationship**: ARP playback routes to OSC synthesis

**Type**: Playback Path

**Existing Semantic IDs**:
- ARP.PATTERN.PLAYBACK (sequence engine)
- OSC.1–5 (synthesis targets)

**Evidence References**:
- ARP section closure (inventory v1.2.0): "ARP patterns sequence MIDI pitch to OSC playback targets; confirmed via official docs and direct UI pattern/rate/transpose evidence"
- OSC section closure (inventory v1.2.0): "oscillators confirmed as synthesis targets"

**New Semantic Identity?**: NO

**Ownership**: ARP owns sequence generation state; OSC owns synthesis state; MATRIX owns inter-section routing

**Conditionality**: Playback path conditional on ARP enable state and OSC enable state

**Structural Effect**: None

**Resource Effect**: None

**Disposition**: REFERENCE_ONLY

**Unresolved Issue**: None

**Blocking Status**: NOT BLOCKING

---

### CS-12: CLIP ↔ OSC

**Relationship**: CLIP playback routes to OSC synthesis

**Type**: Playback Path

**Existing Semantic IDs**:
- CLIP.PIANO_ROLL (MIDI editor)
- OSC.1–5 (synthesis targets)

**Evidence References**:
- CLIP section closure (inventory v1.2.0): "CLIP piano-roll directly editable MIDI note interface confirmed, Mode/Rate/Transpose/Retrig all verified"
- OSC section closure (inventory v1.2.0): "oscillators confirmed as synthesis targets"

**New Semantic Identity?**: NO

**Ownership**: CLIP owns MIDI note sequence state; OSC owns synthesis state; MATRIX owns inter-section routing

**Conditionality**: Playback path conditional on CLIP enable state and OSC enable state

**Structural Effect**: None

**Resource Effect**: None

**Disposition**: REFERENCE_ONLY

**Unresolved Issue**: None

**Blocking Status**: NOT BLOCKING

---

### CS-13: ARP/CLIP ↔ MATRIX

**Relationship**: ARP/CLIP playback triggers act as modulation sources

**Type**: Playback Automation

**Existing Semantic IDs**:
- ARP.PATTERN.TRIGGER (trigger state)
- CLIP.TRIGGER (trigger state)
- MATRIX.SOURCE.ARP, MATRIX.SOURCE.CLIP (modulation routing)

**Evidence References**:
- ARP section closure (inventory v1.2.0): "ARP patterns are existing MATRIX.SOURCE members, confirmed in MATRIX routing tables"
- CLIP section closure (inventory v1.2.0): "CLIP playback is existing MATRIX.SOURCE member, confirmed in MATRIX routing tables"
- MATRIX section closure (inventory v1.2.0): "64-slot matrix with source/destination enumeration complete"

**New Semantic Identity?**: NO

**Ownership**: ARP/CLIP own playback trigger state; MATRIX owns routing destination spec

**Conditionality**: Modulation application conditional on MATRIX destination row selection

**Structural Effect**: None

**Resource Effect**: None

**Disposition**: REFERENCE_ONLY

**Unresolved Issue**: None

**Blocking Status**: NOT BLOCKING

---

### CS-14: BROWSER ↔ RESOURCES

**Relationship**: Preset single-click load is atomic operation; no separate PREVIEW state

**Type**: Resource Loading

**Existing Semantic IDs**:
- BROWSER.PRESET_LIST (5 columns: Name/Author/Category/Rating/Notes)
- BROWSER.LOAD (single-click atomic preset load)

**Evidence References**:
- BROWSER section closure (inventory v1.2.0): "single-click preset load behavior directly verified: click commits full state load immediately; no separate preview-without-commit step exists at row level; confirmed 5 independently-sortable columns"

**New Semantic Identity?**: NO

**Ownership**: BROWSER owns resource selection and load initiation; loading is atomic operation

**Conditionality**: Preset load conditional on preset selection and Browser context

**Structural Effect**: None (single atomic operation)

**Resource Effect**: None (existing resource workflow)

**Disposition**: REFERENCE_ONLY

**Unresolved Issue**: None (directly verified in BROWSER closure)

**Blocking Status**: NOT BLOCKING

---

## Phase 2 Summary

**All 14 relationships reconciled using existing Phase 1 evidence.**

| ID | Relationship | New Semantic ID? | Disposition | Blocking Status |
|---|---|---|---|---|
| CS-01 | OSC ↔ MATRIX | NO | REFERENCE_ONLY | NOT BLOCKING |
| CS-02 | FILTER ↔ MATRIX | NO | REFERENCE_ONLY | NOT BLOCKING |
| CS-03 | FILTER ↔ MIX | NO | REFERENCE_ONLY + CONDITIONAL | NOT BLOCKING |
| CS-04 | OSC/FILTER ↔ MIX | NO | REFERENCE_ONLY | NOT BLOCKING |
| CS-05 | FX ↔ MIX | NO | REFERENCE_ONLY | NOT BLOCKING |
| CS-06 | MACRO ↔ MATRIX | NO | REFERENCE_ONLY | NOT BLOCKING |
| CS-07 | MACRO ↔ CLIP | NO | REFERENCE_ONLY + CONDITIONAL | NOT BLOCKING |
| CS-08 | KEYBOARD ↔ OSC | NO | REFERENCE_ONLY | NOT BLOCKING |
| CS-09 | KEYBOARD ↔ ARP | NO | REFERENCE_ONLY | NOT BLOCKING |
| CS-10 | KEYBOARD ↔ CLIP | NO | REFERENCE_ONLY | NOT BLOCKING |
| CS-11 | ARP ↔ OSC | NO | REFERENCE_ONLY | NOT BLOCKING |
| CS-12 | CLIP ↔ OSC | NO | REFERENCE_ONLY | NOT BLOCKING |
| CS-13 | ARP/CLIP ↔ MATRIX | NO | REFERENCE_ONLY | NOT BLOCKING |
| CS-14 | BROWSER ↔ RESOURCES | NO | REFERENCE_ONLY | NOT BLOCKING |

**Outcomes**:
- ✅ 14/14 relationships reconciled
- ✅ 0 new semantic identities introduced
- ✅ 0 conflicts requiring merge
- ✅ All evidence sourced from Phase 1 closure
- ✅ All relationships either REFERENCE_ONLY or REFERENCE_ONLY + CONDITIONAL
- ✅ No blocking issues

**Status**: ✅ READY FOR PHASE 3 G1–G10 AUDIT

---

**Date**: 2026-09-16
**Inventory Version**: 1.3.0-CROSS-SYSTEM-RECONCILIATION-PHASE-2-COMPLETE
**Canonical Relationship IDs**: CS-01 through CS-14 (permanent, position-independent)
