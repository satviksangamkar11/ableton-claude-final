---
title: Phase 2 Cross-System Matrix Integrity Check
subtitle: 14-Row Relationship Audit Before Testing
date: 2026-09-16
status: PRE-FLIGHT VERIFICATION
---

# Phase 2: Cross-System Matrix Integrity Check

**Purpose**: Verify that every relationship in the master plan has an explicit disposition (REFERENCE / TEST / EXCLUSION) with documented evidence before Phase 2 experiments begin.

**Master Plan Reference**: 14 relationship classes defined in project roadmap.

---

## 14-Row Integrity Audit

### Row 1: OSC ↔ FILTER

| Field | Value |
|-------|-------|
| **Systems** | OSC (oscillators A/B/C/SUB/NOISE) ↔ FILTER (FILTER1/FILTER2) |
| **Question** | Does the routing relationship (OSC selection → FILTER1/FILTER2 input) introduce a NEW semantic control or state? |
| **Existing Identities** | OSC.A/B/C/SUB/NOISE (oscillators); FILTER.1/FILTER.2 (filter types/parameters); no "OSC→FILTER routing" control exists in either section |
| **Evidence** | OSC section: no routing field; FILTER section: no per-oscillator input selector. Routing is implicit (all OSC sum to filter input by default). Prior passes found no per-oscillator routing gate. |
| **Interpretation** | Routing is architectural, not user-facing semantic control. |
| **Disposition** | **REFERENCE ONLY** — No test needed; cross-reference only. If Phase 3 auditing finds a conditional routing control, promote to TEST retroactively. |
| **Final Status** | ✅ LOCKED |

---

### Row 2: OSC ↔ MATRIX

| Field | Value |
|-------|-------|
| **Systems** | OSC (A/B/C/SUB/NOISE output) ↔ MATRIX (Mod Sources: OSC A/B/C level, OSC A/B/C pitch, etc.) |
| **Question** | Does MATRIX's ability to modulate OSC parameters create a NEW semantic control or state? |
| **Existing Identities** | KEYBOARD.MPE.* (Performance Sources mapped to Matrix); MATRIX.SOURCE (OSC A/B/C level/pitch/warp/etc. are listed). MATRIX already owns modulation-routing; OSC already owns parameter definitions. |
| **Evidence** | MATRIX section closure (2026-09-16) documented SOURCE universe including OSC-scoped destinations. KEYBOARD section documented OSC Mapping (Note Range Editor). No missing state. |
| **Interpretation** | Relationship already fully represented. No new semantic identity. |
| **Disposition** | **REFERENCE ONLY** — Cross-reference MATRIX.SOURCE.OSC_* to OSC parameter definitions; no test needed. |
| **Final Status** | ✅ LOCKED |

---

### Row 3: FILTER ↔ MATRIX

| Field | Value |
|-------|-------|
| **Systems** | FILTER (FILTER1/FILTER2 parameters) ↔ MATRIX (Mod Sources: Filter1/Filter2 cutoff, resonance, etc.) |
| **Question** | Does MATRIX's ability to modulate FILTER parameters create NEW semantic control or state? |
| **Existing Identities** | MATRIX.SOURCE (Filter category: Cutoff/Resonance/Drive for each Filter). FILTER section owns parameter definitions. |
| **Evidence** | MATRIX section closure documented SOURCE filter category. FILTER section (2026-09-16) documented all filter types and parameters. No missing state. |
| **Interpretation** | Relationship already fully represented; no new state. |
| **Disposition** | **REFERENCE ONLY** — Cross-reference MATRIX.SOURCE.FILTER_* to FILTER parameter definitions; no test needed. |
| **Final Status** | ✅ LOCKED |

---

### Row 4: OSC/FILTER ↔ MIX

| Field | Value |
|-------|-------|
| **Systems** | OSC/FILTER (signal outputs) ↔ MIX (channel routing: OSC/FILTER channels, level, pan, sends, filter balance) |
| **Question** | Does the relationship introduce a NEW semantic control or state beyond existing MIX routing controls? Specifically: does MIXER.CHANNEL.FILTER_BALANCE (conditional on Routing=Filter) introduce a new state, or is it already represented? |
| **Existing Identities** | MIXER.OSC_A/B/C/SUB/NOISE (7 channels × 8 controls each); MIXER.FILTER1/FILTER2 (8 controls each); MIXER.CHANNEL.ROUTING (conditional visibility of Filter Balance). Filter Balance is already listed in inventory but conditional visibility needs verification. |
| **Evidence** | MIXER closure (2026-09-16) documented Filter Balance knob with note: "conditional_visibility: only visible when channel Routing=Filter". FILTER section owns Wet/Mix knob (separate from Balance). Routing is MIXER-owned. |
| **Interpretation** | MIXER.CHANNEL.FILTER_BALANCE is already represented and correctly scoped as MIXER-owned. Conditional visibility already documented. But conditional-visibility depth was not experimentally re-verified this session. |
| **Disposition** | **TEST (Targeted)** — One specific test: Verify FILTER_BALANCE conditional visibility by toggling Routing on a channel (e.g., OSC A: Routing=Filter, observe Filter Balance appears; Routing=Main, observe it disappears). Expected outcome: existing MIXER record confirmed; no new semantic identity. |
| **Final Status** | ⏳ TEST REQUIRED |

---

### Row 5: FX ↔ MIX

| Field | Value |
|-------|-------|
| **Systems** | FX (13 processors + splitters in racks MAIN/BUS1/BUS2) ↔ MIX (MAIN/BUS1/BUS2 channel volumes) |
| **Question** | Does the FX rack structure introduce NEW semantic control or state beyond existing MIX/FX ownership? |
| **Existing Identities** | FX section: 173 records (MAIN/BUS1/BUS2 racks). MIXER section: 66 records (MAIN/BUS1/BUS2 channels + per-channel routing). Both sections explicitly cross-referenced in closure notes. |
| **Evidence** | FX closure (2026-09-16): "FX rack tabs (MAIN/BUS1/BUS2) cross-referenced to MIXER.MAIN/BUS1/BUS2". MIXER closure: explicit cross-reference backward. No ownership conflict; no hidden state. |
| **Interpretation** | Relationship is structural (racks correspond to channels) and already fully represented via cross-references. No new semantic identity. |
| **Disposition** | **REFERENCE ONLY** — Cross-reference only; no test needed. Structural correspondence already verified in closure notes. |
| **Final Status** | ✅ LOCKED |

---

### Row 6: MACRO ↔ MATRIX

| Field | Value |
|-------|-------|
| **Systems** | MACRO (1-8) ↔ MATRIX (Mod Sources: Macro 1-8) |
| **Question** | Does MACRO's role as Mod Source introduce NEW semantic control or state? |
| **Existing Identities** | MACRO.SYS.VALUE_AS_MOD_DESTINATION (documented: "each macro as a potential destination"). MATRIX.SOURCE (Macro category: Macro 1-8). KEYBOARD.MPE.XYZ/YZ/Y_TO_MACROS (quick-actions; undocumented function but listed). |
| **Evidence** | MACRO closure (2026-09-14): confirmed "each macro as a potential destination" via official PDF + direct UI. KEYBOARD closure: documented MPE-to-Macro mapping items (function undecided: radio vs. quick-action, but existence confirmed). No hidden Macro state. |
| **Interpretation** | Relationship already fully represented. No new state. |
| **Disposition** | **REFERENCE ONLY** — Cross-reference MATRIX.SOURCE.MACRO_1-8 to MACRO section; do NOT test KEYBOARD.MPE quick-actions (their function is an existing P2 deferral, not a new relationship question). |
| **Final Status** | ✅ LOCKED |

---

### Row 7: MACRO ↔ CLIP

| Field | Value |
|-------|-------|
| **Systems** | MACRO (1-8) ↔ CLIP (CLIP.GLOBAL.SHOW_MACROS display toggle + Pattern Editor macro lanes) |
| **Question** | Does the "Show Macros" toggle or the per-lane macro automation in CLIP introduce NEW semantic control or state? Or is it purely a display/view operation over existing MACRO.1-8 semantics? |
| **Existing Identities** | MACRO.1-8 (8 global macros with value/range/assignments). CLIP.GLOBAL.SHOW_MACROS (display toggle). ARP also has parallel Pattern Editor macro lanes + SHOW_MACROS equivalent. Question: are these new Macro-specific states, or just views? |
| **Evidence** | CLIP closure (2026-09-17): confirmed SHOW_MACROS exists and is a display toggle. ARP closure: confirmed ARP.GLOBAL.SHOW_MACROS exists and mentioned Macro lanes in editor. But semantics of "per-lane macro assignment" not proven distinct from global MACRO.1-8. |
| **Interpretation** | SHOW_MACROS is a UI display toggle (not a semantic control). Macro lanes in CLIP/ARP editors are automation targets for existing MACRO.1-8, not new semantic identities. But this must be experimentally confirmed: do lane changes create new CLIP-scoped macro state, or merely record automation on existing global macros? |
| **Disposition** | **TEST (Targeted)** — One specific test: Open CLIP Pattern Editor; create per-lane macro automation for Macro 1 (e.g., lane rises from 0 to 100 over 8 steps); then toggle SHOW_MACROS off and on; verify that the same global MACRO.1 semantics are being automated (no new CLIP-local macro state). Expected outcome: CLIP macro lanes are automation UI over existing MACRO.1-8; no new semantic identity. |
| **Final Status** | ⏳ TEST REQUIRED |

---

### Row 8: KEYBOARD ↔ OSC

| Field | Value |
|-------|-------|
| **Systems** | KEYBOARD (Keyboard/Performance bar) ↔ OSC (A/B/C/SUB/NOISE oscillators) |
| **Question** | Does the KEYBOARD.OSC_MAPPING (Note Range Editor) introduce NEW semantic control or state? |
| **Existing Identities** | KEYBOARD.OSC_MAPPING (6 records: EDITOR, ARP_ROW_FOLD, ARP_ROW_WARP, ARP_ROW_KEY_RANGE, VEL_TAB, RESET_ALL). OSC section owns oscillator definitions. |
| **Evidence** | KEYBOARD closure (2026-09-17): "OSC MAPPING editor launches from Keyboard/Performance bar independent of ARP/CLIP tab... re-homed from ARP to GLOBAL_KEYBOARD... Editor confirmed directly launched from Keyboard/Performance bar". Full feature enumeration. No missing state. |
| **Interpretation** | Relationship is fully represented and owned by KEYBOARD section (not by OSC). No new semantic identity. |
| **Disposition** | **REFERENCE ONLY** — No test needed; existing KEYBOARD records fully document this relationship. |
| **Final Status** | ✅ LOCKED |

---

### Row 9: KEYBOARD ↔ ARP

| Field | Value |
|-------|-------|
| **Systems** | KEYBOARD (OSC Mapping ARP row, transpose, key, scale) ↔ ARP (GLOBAL settings, patterns, slots) |
| **Question** | Does KEYBOARD's control of ARP per-note routing or ARP transpose introduce NEW semantic control or state? |
| **Existing Identities** | KEYBOARD.OSC_MAPPING.ARP_ROW_* (fold/warp/key-range targeting ARP row). KEYBOARD.TRANSPOSE (global MIDI offset, documented as distinct from ARP.TRANSPOSE.SHIFT). ARP.TRANSPOSE.SHIFT (per-pattern transpose). |
| **Evidence** | KEYBOARD closure: "ARP row content cross-referenced back to ARP; TRANSPOSE/KEY/SCALE/SWING/PORTA/CURVE/ALWAYS_SCALED confirmed as Keyboard-bar-owned, not ARP-owned". ARP closure: "TRANSPOSE (Shape=18 options, Shift/Range both modulatable)". Clear ownership boundaries. |
| **Interpretation** | Relationship is ownership-clear: KEYBOARD owns global transpose and OSC mapping; ARP owns its own transpose feature. Two distinct controls, not duplicates. Already documented in closures. |
| **Disposition** | **REFERENCE ONLY** — Cross-reference KEYBOARD.TRANSPOSE to ARP.TRANSPOSE.SHIFT; no test needed. |
| **Final Status** | ✅ LOCKED |

---

### Row 10: KEYBOARD ↔ CLIP

| Field | Value |
|-------|-------|
| **Systems** | KEYBOARD (OSC Mapping CLIP row, transpose, key, scale) ↔ CLIP (GLOBAL settings, CLIP selector, CLIP editor) |
| **Question** | Does KEYBOARD's control of CLIP per-note routing or CLIP transpose introduce NEW semantic control or state? |
| **Existing Identities** | KEYBOARD.OSC_MAPPING.CLIP_ROW (presumably exists, though not explicitly listed in closure notes — need to verify). KEYBOARD.TRANSPOSE. CLIP.GLOBAL (settings). |
| **Evidence** | KEYBOARD closure: "OSC MAPPING editor... 6 rows (SUB/OSC A/B/C/NOISE/ARP)". Notably, closure mentions ARP row but does NOT explicitly mention CLIP row. CLIP closure: "CLIP.GLOBAL.BANK / Launch Quant / Edit All / Show Macros... Launch Quant (structurally relocated to per-clip...)". No mention of KEYBOARD-scoped CLIP note mapping. **GAP IDENTIFIED.** |
| **Interpretation** | Unclear whether KEYBOARD.OSC_MAPPING has a CLIP row, and if so, whether it introduces new CLIP state or is purely routing. Prior KEYBOARD closure may have overlooked CLIP row in the OSC Mapping editor. |
| **Disposition** | **TEST (Targeted — Critical)** — One specific test: Open CLIP mode in OSC Mapping editor; verify (1) CLIP row exists with Fold/Warp/Key Range controls, (2) state is pure routing (not a new CLIP semantic), (3) ownership clear. Expected outcome: confirm CLIP row is KEYBOARD-owned routing, no new semantic identity. **CRITICAL: This gap must be resolved before proceeding with Phase 3.** |
| **Final Status** | ⏳ TEST REQUIRED (Critical gap) |

---

### Row 11: ARP ↔ OSC

| Field | Value |
|-------|-------|
| **Systems** | ARP (GLOBAL patterns/sequences) ↔ OSC (A/B/C/SUB/NOISE playback) |
| **Question** | Does the ARP playback path through OSC introduce NEW semantic control or state? |
| **Existing Identities** | ARP.OSC_MAPPING (re-homed from ARP to KEYBOARD; 6 records). OSC section owns oscillator definitions. ARP owns sequencer patterns. |
| **Evidence** | ARP closure: "OSC MAPPING's ARP row cross-referenced back to ARP". KEYBOARD closure: "OSC MAPPING editor launches... independent of ARP/CLIP tab selection". Ownership is clear: routing is KEYBOARD-owned, playback is ARP-owned. No hidden state. |
| **Interpretation** | Relationship is architectural (ARP sequences notes into OSC). No new semantic control. |
| **Disposition** | **REFERENCE ONLY** — Cross-reference only; no test needed. |
| **Final Status** | ✅ LOCKED |

---

### Row 12: CLIP ↔ OSC

| Field | Value |
|-------|-------|
| **Systems** | CLIP (editor/piano roll) ↔ OSC (A/B/C/SUB/NOISE playback) |
| **Question** | Does CLIP playback through OSC introduce NEW semantic control or state? |
| **Existing Identities** | CLIP.OSC_MAPPING (if it exists — need to verify per Row 10 gap). CLIP section owns clip editing. OSC owns oscillator definitions. |
| **Evidence** | CLIP closure: no explicit mention of per-row routing controls like Row 10. KEYBOARD closure: OSC Mapping rows include CLIP. But CLIP section closure did not document CLIP-specific routing state. **GAP IDENTIFIED (related to Row 10).** |
| **Interpretation** | Relationship may be incomplete depending on Row 10 resolution. |
| **Disposition** | **TEST (Targeted — Dependent on Row 10)** — Resolve Row 10 first (KEYBOARD ↔ CLIP OSC Mapping row); this relationship's disposition will follow. |
| **Final Status** | ⏳ TEST REQUIRED (Dependent) |

---

### Row 13: ARP/CLIP ↔ MATRIX

| Field | Value |
|-------|-------|
| **Systems** | ARP/CLIP (trigger events) ↔ MATRIX (Mod Sources: ARP/CLIP triggers for automation) |
| **Question** | Does ARP/CLIP's role as MATRIX Mod Source introduce NEW semantic control or state? |
| **Existing Identities** | MATRIX.SOURCE (ARP category, CLIP category — documented in closure as Trigger sources). ARP/CLIP sections own sequencer/editor semantics. |
| **Evidence** | MATRIX closure (2026-09-16): "MATRIX menu [Sort by Source, Sort by Destination, Lock Matrix, Create Vibrato, Create Velo->Amp Assignment, Apply and Delete Macros] -- all 6 items VERIFIED". MATRIX.SOURCE includes ARP/CLIP triggers. ARP/CLIP closures did not find new state. |
| **Interpretation** | Relationship is fully represented via existing MATRIX.SOURCE category. No new semantic identity. |
| **Disposition** | **REFERENCE ONLY** — Cross-reference MATRIX.SOURCE.ARP_TRIGGER / MATRIX.SOURCE.CLIP_TRIGGER to ARP/CLIP sections; no test needed. |
| **Final Status** | ✅ LOCKED |

---

### Row 14: BROWSER ↔ RESOURCES

| Field | Value |
|-------|-------|
| **Systems** | BROWSER (Presets Browser panel) ↔ RESOURCES (preset files, packs, tuning files, resource ownership) |
| **Question** | Does BROWSER introduce NEW semantic resource state or control, or is it purely a load/select/navigation interface over existing resource entities? Specifically: does the "single-click LOAD" behavior found in BROWSER closure introduce a new semantic identity (e.g., BROWSER.LOAD) distinct from other load operations? |
| **Existing Identities** | BROWSER.PRESET_LIST (41 records covering selection, metadata, ratings, sorting). TOPMENU.RESOURCE (preset/pack management actions: Load/Revert/Save-as-Default/Get-Packs/Import/Rescan). Single-click load behavior observed but semantic scope unclear. |
| **Evidence** | BROWSER closure (2026-09-16): "KEY WORKFLOW FINDING: a single click on a preset row (name or icon) commits a FULL LOAD into Serum's engine state immediately -- there is no separate preview-without-committing step observable at the row level". But closure did not define whether BROWSER.LOAD is a NEW semantic identity or simply names an existing resource-load operation. |
| **Interpretation** | Ambiguous. Does "single-click LOAD" represent a new semantic state (BROWSER.LOAD.ATOMIC vs. PREVIEW), or is it simply a user-interface characteristic of existing resource-load semantics? This question must be resolved: if BROWSER introduces new resource-state semantics (e.g., BROWSER.LOAD_ATOMIC distinct from other load types), it needs a semantic identity. If it's purely UI over existing load semantics, it's a reference. |
| **Disposition** | **TEST (Targeted)** — One specific test: Determine whether the "single-click load" behavior creates a NEW semantic resource-state identity or is simply a UI affordance. Test: (1) Click a preset in Browser; observe LOAD commits atomically. (2) Compare to TOPMENU.RESOURCE.LOAD_PRESET behavior (if testable). (3) Determine if any NEW BROWSER-scoped semantic state (e.g., BROWSER.LOAD_STATE) needs to be documented. Expected outcome: BROWSER operations are user-interface patterns over existing resource-load semantics; no new semantic identity (BROWSER section owns UI/workflow, RESOURCES/TOPMENU own the actual load state). **Note: Do NOT conflate this with BROWSER_RESCAN_OWNERSHIP P2 deferral; that is a separate filesystem experiment.** |
| **Final Status** | ⏳ TEST REQUIRED |

---

## Summary: Matrix Lock Status

| # | Relationship | Disposition | Status | Test? |
|---|---|---|---|---|
| 1 | OSC ↔ FILTER | REFERENCE ONLY | ✅ LOCKED | ❌ NO |
| 2 | OSC ↔ MATRIX | REFERENCE ONLY | ✅ LOCKED | ❌ NO |
| 3 | FILTER ↔ MATRIX | REFERENCE ONLY | ✅ LOCKED | ❌ NO |
| 4 | OSC/FILTER ↔ MIX | TEST (conditional visibility) | ⏳ PENDING | ✅ YES |
| 5 | FX ↔ MIX | REFERENCE ONLY | ✅ LOCKED | ❌ NO |
| 6 | MACRO ↔ MATRIX | REFERENCE ONLY | ✅ LOCKED | ❌ NO |
| 7 | MACRO ↔ CLIP | TEST (Show Macros semantics) | ⏳ PENDING | ✅ YES |
| 8 | KEYBOARD ↔ OSC | REFERENCE ONLY | ✅ LOCKED | ❌ NO |
| 9 | KEYBOARD ↔ ARP | REFERENCE ONLY | ✅ LOCKED | ❌ NO |
| 10 | KEYBOARD ↔ CLIP | TEST (OSC Mapping CLIP row — **CRITICAL GAP**) | ⏳ PENDING | ✅ YES |
| 11 | ARP ↔ OSC | REFERENCE ONLY | ✅ LOCKED | ❌ NO |
| 12 | CLIP ↔ OSC | TEST (Dependent on Row 10) | ⏳ PENDING | ✅ YES? |
| 13 | ARP/CLIP ↔ MATRIX | REFERENCE ONLY | ✅ LOCKED | ❌ NO |
| 14 | BROWSER ↔ RESOURCES | TEST (Load semantics scope) | ⏳ PENDING | ✅ YES |

### Test Count

- **REFERENCE ONLY (no test needed)**: 9 relationships (✅ LOCKED)
- **TEST REQUIRED**: 5 relationships (⏳ PENDING)
  - 4 targeted tests (Rows 4, 7, 10, 14)
  - 1 dependent test (Row 12, awaits Row 10 resolution)
  - Total sequence: Row 10 → Row 12 (dependent), then Rows 4, 7, 14 in parallel

---

## Critical Gap Identified

**Row 10: KEYBOARD ↔ CLIP**

The KEYBOARD section closure documented OSC Mapping but may have overlooked the CLIP row. The CLIP section closure did not mention KEYBOARD-scoped routing state.

**This gap must be resolved before Phase 2 experiments begin.**

Action: 
1. Check KEYBOARD closure notes for explicit mention of CLIP row in OSC Mapping editor
2. If CLIP row exists but was not explicitly documented in closure, it becomes TEST Row 10 (critical)
3. If CLIP row does not exist, this represents a potential completeness gap (CLIP may be missing from OSC Mapping editor)

---

## Next Steps

### If Gap is Resolved (CLIP row exists and is documented):

**Proceed with Phase 2 Experiments**:

1. Row 4: FILTER ↔ MIX (Filter Balance conditional visibility) — 10 minutes
2. Row 7: MACRO ↔ CLIP (Show Macros semantics) — 10 minutes
3. Row 10: KEYBOARD ↔ CLIP (OSC Mapping CLIP row verification) — 10 minutes
4. Row 14: BROWSER ↔ RESOURCES (Load semantics) — 10 minutes
5. Row 12: CLIP ↔ OSC (dependent; should resolve to REFERENCE based on Row 10)

**Total time**: ~40 minutes of focused testing.

### If Gap Reveals Missing State:

**Perform gap-filling investigation** before Phase 2 experiments begin.

---

## Matrix Lock Declaration

**PRE-FLIGHT CHECK**: Matrix is locked. 9 relationships confirmed REFERENCE ONLY. 5 relationships confirmed TEST REQUIRED. 1 critical gap identified (Row 10) requiring verification before experiments begin.

**Status**: ⏳ READY FOR PHASE 2 EXPERIMENTS (pending Row 10 gap verification)

---

**Artifact Version**: Phase 2 Pre-Flight (2026-09-16)
**Next Artifact**: Phase 2 Test Results Log + Updated Reconciliation Matrix
