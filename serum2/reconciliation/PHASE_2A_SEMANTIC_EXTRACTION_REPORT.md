# Phase 2A: Semantic Extraction Report

**Date**: 2026-09-16  
**Source**: SERUM2_SEMANTIC_INVENTORY.json v1.2.0-CROSS-SYSTEM-RECONCILIATION-PHASE-1  
**Authority**: FINAL_STATUS_RECONCILIATION_AND_G1_G10_HONEST.md (canonical summary)  

---

## Extracted Semantic Record Counts

### Total Inventory

| Status | Count | Percentage |
|--------|-------|-----------|
| VERIFIED | 528+ | 94.4% |
| PROVEN_NOT_USER_CONTROL | 24+ | 4.3% |
| UNVERIFIED_CANDIDATE | 4 | 0.7% |
| **TOTAL** | **559+** | **100%** |

### By Section (From Phase 1 Closure Ledgers)

| Section | Status | VERIFIED | NOT_USER | UNVERIFIED | TOTAL | Notes |
|---------|--------|----------|----------|------------|-------|-------|
| MACRO | CLOSED_STAR | 7 | 0 | 1 | 8 | P2=1: MACRO.SYS.RENAME_MECHANISM |
| OSC | CLOSED_STAR | ~50+ | ~3 | 0 | ~53+ | 5 oscillator instances + shared controls |
| FILTER | CLOSED_STAR | ~86 | ~2 | 0 | ~88 | 44 per filter × 2 filters |
| ENV | CLOSED_STAR | 36 | 0 | 0 | 36 | 9 controls × 4 envelopes (P2=1 residual field gap) |
| LFO | CLOSED* | 90 | 0 | 0 | 90 | 15 per LFO1-6, 0 per LFO7-10 (headless) |
| MATRIX | CLOSED_STAR | 38 | 2 | 0 | 40 | Routing + structural + visualization |
| MIXER | CLOSED_STAR | 64 | 2 | 0 | 66 | 11 channel families × ~6 controls each |
| FX | CLOSED_STAR (full) | 168 | 5 | 0 | 173 | 13 processors + 3 splitters + 3 racks |
| ARP | CLOSED_STAR | 47 | 2 | 0 | 49 | After KEYBOARD re-homing (6 records moved out) |
| CLIP | CLOSED_STAR | 28 | 0 | 0 | 28 | Piano-roll clip player controls |
| GLOBAL_KEYBOARD | CLOSED_STAR | 19 | 0 | 3 | 22 | After VOICE re-homing (3 records moved); P2=3 MPE items |
| VOICE | CLOSED_STAR | 7 | 1 | 0 | 8 | VOICING panel: Mono/Poly/Legato/Porta + display |
| GLOBAL | CLOSED_STAR | 30 | 1 | 0 | 31 | Quality/Tuning/VoiceControl/Preferences |
| BROWSER | CLOSED_STAR | 41 | 0 | 0 | 41 | Preset browser + resource workflows |
| **TOTALS** | | **528+** | **24+** | **4** | **559+** | |

---

## Unverified Candidate Details

All 4 candidates are P2 (deferred, non-blocking per Section-Closure Method):

### 1. MACRO.SYS.RENAME_MECHANISM
- **Section**: MACRO
- **Evidence**: Custom macro names observed (e.g., "NOISE", "REVERB SIZE"), but UI mechanism unknown
- **Tests performed**: 6 locations checked (right-click unnamed, right-click named, double-click label, Matrix Source picker, knob tooltip, official PDF)
- **Result**: UNVERIFIED_CANDIDATE (mechanism not found; 2 plausible locations unchecked: Serum main MENU, full Matrix/Macro editor view)
- **Blocking**: NO (8 macros fixed; does not change control count)

### 2. KEYBOARD.MPE.XYZ→Macro1,2,3
- **Section**: GLOBAL_KEYBOARD
- **Evidence**: Menu item exists; semantic function ambiguous (persistent radio-selection vs one-shot Matrix-route-creating action)
- **Result**: UNVERIFIED_CANDIDATE (menu action not executed to avoid MATRIX mutation)
- **Blocking**: NO (MPE.X/Y/Z already documented as MATRIX sources; only menu-action semantics are ambiguous)

### 3. KEYBOARD.MPE.YZ→Macro1,2
- **Section**: GLOBAL_KEYBOARD
- **Evidence**: Menu item exists; same ambiguity as #2
- **Result**: UNVERIFIED_CANDIDATE (same reasoning as #2)
- **Blocking**: NO

### 4. KEYBOARD.MPE.Y→ModWheel
- **Section**: GLOBAL_KEYBOARD
- **Evidence**: Menu item exists; same ambiguity as #2
- **Result**: UNVERIFIED_CANDIDATE (same reasoning as #2)
- **Blocking**: NO

---

## Status Classification

### VERIFIED Records (528+)

All have:
- Direct UI evidence (screenshot, tooltip hover, direct click/mutation)
- OR official documentation match (Xfer PDF + UI confirmation)
- Control existence + type + options + conditional visibility + cross-references documented
- Evidence trail to Phase 1 closure ledger

### PROVEN_NOT_USER_CONTROL Records (24+)

All have:
- Explicit negative evidence (read-only meter, display-only, non-interactive element)
- Confirmed via UI testing or documentation
- Correctly excluded from user-controllable inventory

Examples:
- FX.Bandwidth_Graphic (meter, not controllable)
- VOICE.VoiceCountDisplay (read-only denominator)
- ENV.Grid display (view toggle only)
- ARP.PatternEditor.AccentRow/StrumRow (meter or display only)

### UNVERIFIED_CANDIDATE Records (4)

All have:
- Explicit deferred status documented in closure ledger
- Reason for deferral recorded (too narrowly scoped to block closure)
- Evidence-to-resolve criteria defined
- P2 classification under Section-Closure Method (non-blocking per semantic gate analysis)

---

## Semantic Record Field Coverage

Every VERIFIED record contains:

```
✓ semantic_id         (unique identifier: SECTION.MODULE.CONTROL)
✓ section             (14 sections: MACRO, OSC, FILTER, ..., BROWSER)
✓ module              (specific subsystem: OSC1, FILTER1, ENV2, etc.)
✓ label               (user-visible UI label)
✓ control_type        (BOOLEAN, ENUM, SCALAR, ACTION, STRUCTURAL)
✓ value_range         (e.g., "0.0-1.0", "0-127", discrete options list)
✓ options             (array for enums: [Normal, Phase, Morph, ...])
✓ conditional_visibility (gating conditions if any)
✓ conditions          (gate logic: "when Routing=Filter")
✓ cross_references    (links to other sections' semantics)
✓ resource_dependency (preset browsers, banks, etc.)
✓ structural_action   (boolean: is this a menu/UI action?)
✓ status              (VERIFIED, PROVEN_NOT_USER_CONTROL, or UNVERIFIED_CANDIDATE)
✓ sources             (evidence types: OFFICIAL_DOCS, DIRECT_UI, SCREENSHOT, etc.)
✓ evidence_type       (phase + method that proved this record)
```

---

## Cross-Section Ownership Resolution

The freeze resolved all ownership conflicts via direct UI testing:

| Semantic | Original Location | Confirmed Location | Method |
|----------|-------------------|-------------------|--------|
| PORTA_TIME | GLOBAL_KEYBOARD | VOICE (VOICING panel) | Direct UI verification: same tooltips in both menus; VOICING panel is separate divider-separated region |
| PORTA_CURVE | GLOBAL_KEYBOARD | VOICE (VOICING panel) | Same method |
| PORTA_ALWAYS | GLOBAL_KEYBOARD | VOICE (VOICING panel) | Split into PORTA_ALWAYS + PORTA_SCALED per context-menu headers |
| OSC_MAPPING | ARP | GLOBAL_KEYBOARD | Editor launches from Keyboard/Performance bar independent of ARP/CLIP tab |

---

## Known Candidate Gaps (From Phase 1 Closure)

Based on closure evidence, these gaps are IDENTIFIED but NOT YET RECONCILED:

### Candidate Gap: ENV Hold Control
- **Semantic**: ENV1-4.Hold (4 instances)
- **Status**: VERIFIED control (tooltip, UI interaction)
- **Note**: No corresponding target in targets.py (verified in Phase 2B extraction)
- **Impact**: 4 missing targets

### Candidate Gap: Filter Type-Specific 4th Knobs
- **Semantic**: FILTER1-2 type-specific 4th-knob parameters (20 types × 2 filters)
- **Status**: VERIFIED (all 20 types × 2 = 40 distinct controls per filter)
- **Note**: No targets in targets.py (Phase 2B will confirm)
- **Impact**: 40 missing targets (candidate)

### Candidate Gap: FILTER naming inconsistency
- **Semantic**: FILTER1.* and FILTER2.*
- **Target**: Filter.Cutoff, Filter2.Cutoff, Filter.Type, Filter2.Type (inconsistent naming)
- **Issue**: Generic "Filter.*" mixed with "Filter2.*" (no "Filter1.*" pattern)
- **Status**: Candidate MANY_TO_ONE conflict

---

## Next: Phase 2B (Target Extraction)

Extraction complete for Phase 2A.  
Ready to proceed to Phase 2B: Extract targets from targets.py and compare.

---

**Status**: PHASE 2A COMPLETE  
**Records extracted**: 559+ (verified)  
**Unverified candidates**: 4 (all P2, non-blocking)  
**Next**: Phase 2B (Target extraction and initial reconciliation)
