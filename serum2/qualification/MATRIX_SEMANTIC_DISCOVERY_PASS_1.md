# MATRIX Section — Semantic Discovery Pass 1

**Date:** 2026-09-15 (Session 2, Context Continuation)  
**Status:** Research IN PROGRESS  
**Method:** Direct Serum 2.0.21 UI inspection + DESTINATION dropdown exploration  
**Authority:** Direct UI verification + MATRIX panel observation

---

## Overview

The MATRIX section is Serum's modulation routing system, fundamentally different from parameter sections (LFO, ENV, FILTER, OSC). It's a **structural system** that enables routing any modulation source to any parameter destination.

---

## Observed MATRIX Panel Structure

### Layout
- Grid of modulation route rows (appears to be 8+ rows visible)
- Each row represents one modulation route (SOURCE → DESTINATION)
- Columns define route behavior

### Route Row Controls (Left to Right)

1. **SOURCE** — Modulation source selector
   - Type: Dropdown menu
   - Observed options: LFO 1-10, Envelopes, Macros, Note, Velocity, etc.
   - Status: Partially observed (LFO menu enumerated in prior LFO discovery pass)

2. **CVY** — Curve (modulation response curve)
   - Type: Likely dropdown or selector
   - Purpose: Defines how source modulation shape affects destination
   - Status: NOT YET ENUMERATED

3. **AMOUNT** — Modulation depth/intensity
   - Type: Knob or continuous value
   - Purpose: Controls how much the source modulates the destination
   - Status: Visible but not yet clicked to determine control type

4. **POL** — Polarity (modulation direction)
   - Type: Likely dropdown or toggle
   - Purpose: Controls positive/negative/bipolar behavior
   - Status: NOT YET ENUMERATED

5. **DESTINATION** — Target parameter selector
   - Type: Dropdown menu with hierarchical submenus
   - Observed categories:
     - OSC A (with submenu for specific oscillator parameters)
     - OSC B (with submenu)
     - OSC C (with submenu)
     - Noise OSC (with submenu)
     - SUB OSC (with submenu)
     - Filter 1 (with submenu)
     - Filter 2 (with submenu)
     - Env 1 (with submenu)
     - LFO 6 (with submenu)
     - Macros (with submenu)
     - LFO Busses (with submenu)
     - Routing Matrix (with submenu)
     - Clip Player (with submenu)
     - Arpeggiator (with submenu)
     - Retriggers (with submenu)
     - Global (with submenu)
   - Status: VERIFIED (menu structure observed; submenus NOT YET EXPANDED)

6. **OUT** — Output value display
   - Type: Read-only value display
   - Purpose: Shows current output value of the route
   - Status: Observable; classification as display-only vs semantic control TBD

7. **AUX SOURCE** — Auxiliary/secondary modulation source
   - Type: Unclear (likely another source selector)
   - Purpose: Possible secondary modulation or scaling source
   - Status: NOT YET EXAMINED

8. **INV** — Invert control
   - Type: Likely boolean toggle
   - Purpose: Reverse/negate the modulation
   - Status: NOT YET TESTED

9. **CVY** — Secondary curve control (appears again)
   - Type: Likely same as primary CVY
   - Purpose: Additional curve shaping (per-axis? per-output?)
   - Status: NOT YET EXAMINED

10. **OUTPUT** — Output value display (similar to OUT?)
    - Type: Read-only value display
    - Status: Unclear; possible duplicate of OUT column

---

## Key Semantic Questions for MATRIX Closure

### Q1: ROUTE STRUCTURE
- **Question:** How many modulation routes can be active simultaneously? (Appears ≥8, exact count TBD)
- **Impact:** Affects whether route count is a documented semantic limit or dynamically generated
- **Evidence required:** Count visible rows, test adding/removing routes, check documentation

### Q2: ROUTE CONTROLS (PER-ROUTE SEMANTIC INVENTORY)
- **Question:** What are the complete control options for each route?
  - CVY: How many curve options available? (Predefined curves vs. custom?)
  - POL: How many polarity options? (Positive, Negative, Bipolar, Off, etc.?)
  - AUX SOURCE: Is this an optional 2nd source? How does it interact with primary SOURCE?
  - INV: Simple boolean toggle or more complex control?
- **Evidence required:** Click each control dropdown/selector and enumerate all options

### Q3: DESTINATION PARAMETER UNIVERSE
- **Question:** What is the complete set of available modulation destinations?
  - Submenus in DESTINATION dropdown need full expansion (OSC A parameters, Filter 1 parameters, etc.)
  - Does every parameter in Serum appear as a destination option?
  - Are there parameters that CANNOT be modulated?
- **Evidence required:** Expand all submenus in DESTINATION dropdown; enumerate all available targets

### Q4: GLOBAL MATRIX CONTROLS
- **Question:** Are there system-wide MATRIX controls?
  - Enable/disable all routes
  - Clear all routes
  - Lock/protect routes
  - MATRIX scale or global depth
- **Evidence required:** Examine MATRIX panel for any controls outside the route grid

### Q5: ROUTE CREATION/DELETION
- **Question:** How are routes created and deleted?
  - Auto-create on first selection?
  - Delete button/mechanism?
  - Max routes limit?
- **Evidence required:** Test assigning/clearing routes in empty rows

### Q6: DISPLAY-ONLY vs SEMANTIC CONTROLS
- **Question:** Which columns are user-facing semantic controls vs. display-only?
  - OUT and OUTPUT appear to be read-only displays
  - CVY columns: Are both curves user-selectable (2 independent curves) or is one display-only?
- **Evidence required:** Attempt to click/modify each column to determine interactivity

---

## Preliminary Control Count (Unverified)

**Per-Route Controls (per modulation route):** 7-10 (TBD)
- SOURCE (1 control, enum: LFO/ENV/Macro/Note/Velocity/other)
- CVY (1 control, enum: predefined curves)
- AMOUNT (1 control, continuous knob)
- POL (1 control, enum: polarity options)
- DESTINATION (1 control, hierarchical menu)
- AUX SOURCE (1 control?, enum: optional secondary source)
- INV (1 control?, boolean toggle)
- CVY2 (1 control?, enum: secondary curve or display-only?)

**Global MATRIX Controls:** 0-3 (TBD)
- Possibly: Enable/Disable All, Clear All, MATRIX Scale

---

## Next Steps (Priority Order)

1. **Enumerate CVY options:** Click CVY dropdown to see predefined curve shapes available
2. **Enumerate POL options:** Click POL dropdown to see polarity modes (Positive, Negative, Bipolar, Unipolar, etc.)
3. **Expand DESTINATION submenus:** Click each destination category to enumerate specific parameters
4. **Test AUX SOURCE:** Determine if it's an optional secondary source and how it combines with primary SOURCE
5. **Test CVY2 / secondary curve:** Determine if both CVY columns are editable or if second is display-only
6. **Test INV control:** Verify if it's a simple boolean toggle
7. **Check for global controls:** Scan MATRIX panel for any system-level controls outside the route grid
8. **Test route creation/deletion:** Verify how routes are added/removed and if there's a max limit
9. **Enumerate all SOURCE options:** Expand complete SOURCE menu (not just LFO 1-10, but also Envelopes, Macros, Note, Velocity, Bend, Aftertouch, etc.)
10. **Verify DESTINATION completeness:** Confirm whether every Serum parameter appears as a destination option

---

## Discovery Roadmap

**Pass 1 (Current):** Observe MATRIX structure and identify semantic control columns
**Pass 2:** Click each control type to enumerate all options (CVY curves, POL options, etc.)
**Pass 3:** Expand DESTINATION menu fully and enumerate all available target parameters
**Pass 4:** Document any global MATRIX controls and route management mechanisms
**Pass 5:** Resolve P0/P1/P2 gaps and determine closure status

---

## Cross-System Notes

- **Relationship to all sections:** MATRIX is the only section that references controls from other sections (LFO as SOURCE, ENV as SOURCE, Macros as SOURCE, and as DESTINATION targets)
- **Dependency order:** MATRIX closure may require closure of referenced sections (LFO, ENV, MACRO, OSC, FILTER, FX) to fully document destination parameter universes
- **Semantic vs. Technical:** MATRIX routes are semantic modulation assignments; the technical VST3 fields backing routes are separate post-closure work

---

Generated: 2026-09-15  
Authority: Direct Serum 2.0.21 UI inspection  
Version lock: Serum 2.0.21 only  
Status: PASS 1 RESEARCH — Structural observation complete; semantic control enumeration pending
