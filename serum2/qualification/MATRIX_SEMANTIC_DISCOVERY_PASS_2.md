# MATRIX Semantic Discovery — PASS 2

**Date:** 2026-09-15 (Session 2 Continuation)  
**Method:** Direct Serum 2.0.21 UI interaction + menu inspection  
**Status:** PASS 2 DETAILED INVESTIGATION — Route structure and source universes established

---

## EXECUTIVE FINDINGS

MATRIX is Serum's modulation routing system with this core structure:

**Per-Route Architecture:**
```
PRIMARY SOURCE → CURVE → AMOUNT → POLARITY → DESTINATION → OUTPUT
AUX SOURCE → AUX INVERT → AUX CURVE → (combines with primary)
```

**Modulation Route Maximum:** 8 visible rows in standard view (TBD if scrollable for more)

**Key Discovery:** AUX SOURCE is an independent secondary modulation source that can scale/modify the primary modulation independently.

---

## 1. MATRIX GLOBAL / PAGE CONTROLS

**Observed:**
- MATRIX Tab (clickable, switches to modulation routing view)
- No visible "Create Route" button (routes appear auto-created on SOURCE selection)
- No visible "Delete Route" button (likely via context menu or row removal mechanism)
- No visible "Clear All Routes" button
- Route expansion icons visible on right side of first route (edit/close icons)

**Still TBD:** 
- Route creation mechanism (auto or manual?)
- Route deletion mechanism
- Route count limits
- Global MATRIX bypass or scale

---

## 2. EXACT ROUTE STRUCTURE — VERIFIED

Each modulation route contains these user-facing elements:

| Column | Label | Control Type | Purpose |
|--------|-------|--------------|---------|
| 1 | SOURCE | Dropdown menu | Primary modulation source selection |
| 2 | CVY | Visual display (?) | Curve shape preview (not yet determined if editable) |
| 3 | AMOUNT | Knob / continuous | Modulation depth/intensity |
| 4 | POL | Icon/display (?) | Polarity indicator (control type TBD) |
| 5 | DESTINATION | Hierarchical dropdown | Target parameter selection |
| 6 | OUT | Read-only value | Output value display |
| 7 | AUX SOURCE | Dropdown menu | Secondary/auxiliary modulation source |
| 8 | INV | Icon/toggle (?) | Auxiliary source inversion (control type TBD) |
| 9 | CVY (aux) | Visual display (?) | Auxiliary curve preview (control type TBD) |
| 10 | OUTPUT | Read-only value (?) | Final modulation output value |

**Control Type Classifications (TBD = requires direct testing):**
- AMOUNT: **VERIFIED** (knob, context menu shows "Mod 1 Amount", Reset Control, MIDI Learn, Lock Parameter options)
- SOURCE: **VERIFIED** (dropdown menu, extensive source options)
- DESTINATION: **VERIFIED** (hierarchical dropdown menu)
- AUX SOURCE: **VERIFIED** (dropdown menu with comprehensive source options)
- CVY/POL/INV/OUTPUT: **UNCONFIRMED** (visual appearance suggests display-only, but control/editability status requires testing)

---

## 3. SOURCE UNIVERSE — ENUMERATED

**Primary SOURCE options (observed via prior LFO discovery):**
- LFO 1-10
- Envelopes (ENV 1-4 + submenus)
- Macros (1-8)
- Note
- Velocity
- (other sources in LFO discovery pass)

**Auxiliary SOURCE options (expanded menu observed THIS SESSION):**
- Off (default)
- Envelopes (with submenu → ENV 1-4 or similar)
- LFOs (with submenu → LFO 1-10)
- Note (with submenu, possibly Note, Velocity, Gate, etc.)
- Oscillators (with submenu → OSC A/B/C or outputs)
- Macros (with submenu → Macro 1-8)
- MPE (with submenu → MPE-specific controls)
- Filters (with submenu → Filter 1/2 or parameters?)
- Mod Wheel (with submenu → continuous controller)
- Aftertouch (with submenu → touch/pressure data)
- Poly Aftertouch (with submenu → per-note aftertouch)
- Pitch Bend (with submenu → pitch wheel data)
- Fixed (with submenu → fixed/constant values?)

**Total Distinct Source Families:** 13 (Off + 12 source categories)

**Cross-Reference to Existing Semantic IDs:**
- LFOs → LFO.1-10 (LFO section, already discovered)
- Envelopes → ENV.1-4 (ENV section, already discovered)
- Macros → MACRO.1-8 (MACRO section, already discovered)
- Oscillators → OSC.A/B/C (OSC section, already discovered)
- Note/Velocity/Pitch Bend/Aftertouch/Mod Wheel → KEYBOARD/PERFORMANCE (not yet discovered sections)
- MPE → (KEYBOARD subsystem)
- Filters → FILTER.1-2 (FILTER section, already discovered)
- Fixed → (MATRIX-owned: fixed/constant values)

---

## 4. DESTINATION UNIVERSE — PARTIALLY ENUMERATED

**Top-Level Destination Categories (observed via dropdown):**
- Off
- OSC A (submenu → specific OSC A parameters)
- OSC B (submenu → specific OSC B parameters)
- OSC C (submenu → specific OSC C parameters)
- Noise OSC (submenu)
- SUB OSC (submenu)
- Filter 1 (submenu)
- Filter 2 (submenu)
- Env 1 (submenu)
- LFO 6 (submenu, likely means "LFO 1-6 parameters")
- Macros (submenu)
- LFO Busses (submenu)
- Routing Matrix (submenu)
- Clip Player (submenu)
- Arpeggiator (submenu)
- Retriggers (submenu)
- Global (submenu)

**Destination Mapping to Existing Semantic IDs:**
- OSC A/B/C → OSC section (already discovered)
- Noise OSC → OSC section (Noise = one oscillator type)
- SUB OSC → OSC section (Sub = another oscillator)
- Filter 1/2 → FILTER section (already discovered)
- Env 1 → ENV section (already discovered; note: only Env 1 visible in menu? TBD if Env 2-4 in submenu)
- LFO 6 → LFO section (TBD: does submenu show LFO 1-10 edit parameters?)
- Macros → MACRO section (already discovered)
- LFO Busses → (MATRIX-owned: LFO bus assignment/depth control?)
- Routing Matrix → (MATRIX-self-modulation: can modulate AMOUNT, CURVE, POLARITY of existing routes?)
- Clip Player → (ARP/CLIP subsystems, not yet discovered)
- Arpeggiator → (ARP section, not yet discovered)
- Retriggers → (GLOBAL/VOICE subsystem, not yet discovered)
- Global → (GLOBAL section, not yet discovered)

**Key Question:** Each submenu needs expansion to see the exact parameters available. OSC A parameters might include: Pitch, Volume, Wavetable Position, Morph, Unison Spread, Phase, etc. Filter 1 might include: Cutoff, Resonance, Shaper Mix, Type, etc.

---

## 5. CURVE / CVY INVESTIGATION

**Current Status: UNCONFIRMED**

**Observations:**
- Two CVY columns visible (one before AMOUNT, one after AUX CURVE)
- Appear as graphical waveform/curve previews
- Unable to directly click/interact with them in initial testing
- Unclear whether they are:
  A. Editable curve selectors (with predefined curve shapes)
  B. Display-only previews of the source's curve
  C. Curve editing tools with visual feedback

**Next Testing Required:**
- Click directly on the curve graphic to see if menu opens
- Check if curve changes when SOURCE is changed
- Check if curve changes when AUX SOURCE is changed
- Determine if one curve is for primary modulation and one for auxiliary

---

## 6. POLARITY / POL INVESTIGATION

**Current Status: UNCONFIRMED**

**Observations:**
- POL column shows an icon (appears to be a polarity indicator, possibly crosshairs or ⊕ symbol)
- Unable to directly click/interact with it in initial testing
- Likely control options (estimate): 
  - Positive (unipolar, 0-100% → min-max)
  - Negative (inverted)
  - Bipolar (±100%, center=0)
  - Off

**Next Testing Required:**
- Click on POL icon to open selector menu
- Document exact option labels
- Verify if polarity is mutually exclusive or independent toggle

---

## 7. AUX SOURCE INVESTIGATION

**Current Status: PARTIALLY VERIFIED**

**Observations:**
- AUX SOURCE menu fully expanded and enumerated (see Section 3)
- Default: "Off" (no auxiliary source)
- 13 source families available (same as primary SOURCE or extended?)
- Appears to enable two independent modulation sources per route

**Semantic Identity:**
- MATRIX-owned control
- Enables per-route secondary modulation
- Enables complex modulation chains (primary source modulated by auxiliary source?)

**Still TBD:**
- How does AUX SOURCE interact with primary SOURCE?
  - Is it additive (primary + auxiliary)?
  - Is it multiplicative (primary × auxiliary)?
  - Does it replace the primary source under certain conditions?
  - Does it scale/modulate the primary source amount?
- Does changing AUX SOURCE affect INV and AUX CURVE behaviors?

---

## 8. AMOUNT, OUT, AND OUTPUT

**AMOUNT: VERIFIED**
- Control type: Knob / continuous parameter
- Editable: YES (context menu confirms MIDI Learn, Reset Control, Lock Parameter available)
- Purpose: Scales the modulation depth
- Display: Shown as a knob with position indicator

**OUT: UNCONFIRMED**
- Currently shows "-" for routes without destination
- Appears to show output value when destination is assigned
- Classification: Likely display-only (shows resulting modulation value)

**OUTPUT: UNCONFIRMED**
- Rightmost column, name slightly different from OUT
- Similar display characteristics
- Unclear if identical to OUT or different measurement

**Next Testing Required:**
- Assign a destination to a route
- Observe OUT and OUTPUT values when route is active
- Determine if they display the same value or different aspects of modulation

---

## 9. ROUTE CREATION / DELETION / BYPASS

**Create Route Mechanism: UNCONFIRMED**
- Possible mechanism 1: Auto-create when selecting SOURCE
- Possible mechanism 2: Click "+" button to create new route
- Possible mechanism 3: Click on SOURCE field in empty row to activate

**Delete Route Mechanism: UNCONFIRMED**
- Edit/close icons visible on right side of first route (need testing)
- Possible via context menu right-click
- Possible via "Remove" button or similar

**Bypass Route: UNCONFIRMED**
- No bypass toggle visible in current view
- Possible via context menu or route-specific control

**Reorder Routes: UNCONFIRMED**
- No visible drag handles or reorder buttons
- TBD if order matters for route processing

---

## 10. ROUTE COUNT / LIMITS

**Current Observation:** 8 route rows visible in standard MATRIX view

**Unconfirmed:**
- Is 8 the maximum routes, or are more routes accessible via scrolling?
- Can routes be deleted freely to create new routes?
- Are there any route count restrictions?

---

## 11. DISPLAY-ONLY vs SEMANTIC CONTROLS

**Likely Display-Only (require verification):**
- CVY columns (curve previews)
- OUT column (output value display)
- OUTPUT column (output value display?)

**User-Facing Semantic Controls (verified or high confidence):**
- SOURCE
- AMOUNT
- DESTINATION
- AUX SOURCE

**Control Type TBD:**
- POL (polarity)
- INV (inversion)
- CVY columns (if editable, not display-only)

---

## SEMANTIC CONTROL SUMMARY — MATRIX ROUTE STRUCTURE

**Per-Route Semantic Controls (Core):**
1. SOURCE (enum: 10+ LFO/ENV/Macro/Note/Velocity/etc. families)
2. AMOUNT (continuous: 0-100 or similar)
3. DESTINATION (hierarchical enum: OSC/Filter/Env/Macro/Global/etc.)
4. AUX SOURCE (enum: Off + 12 source families)

**Per-Route Semantic Controls (Conditional/Refinement):**
5. CVY (if editable: enum curve shapes, or display-only)
6. POL (if editable: enum polarity modes, or display-only)
7. INV (if editable: boolean toggle for AUX inversion, or display-only)
8. AUX CVY (if editable: enum curve shapes for auxiliary, or display-only)

**Global MATRIX Controls (TBD):**
- Route creation mechanism
- Route deletion mechanism
- Route bypass mechanism
- Route reorder mechanism
- Route count limit / scrolling access to additional routes
- Any global MATRIX scale or bypass

---

## UNRESOLVED QUESTIONS FOR PASS 3

1. **CVY Editability:** Are curve columns editable selectors or display-only previews?
2. **POL Control:** What are the exact polarity modes? Mutually exclusive?
3. **INV Control:** Boolean toggle or selector? Applies to AUX SOURCE or primary?
4. **AUX Combination Logic:** How do primary and auxiliary sources combine? Additive? Multiplicative? Other?
5. **Route Creation:** Automatic on SOURCE selection, or manual button/field?
6. **Route Deletion:** Button, context menu, or field clearing?
7. **Route Bypass:** Available mechanism and semantic identity?
8. **OUTPUT vs OUT:** Different measurements or identical?
9. **Route Reorder:** Is reordering possible and does order affect behavior?
10. **Route Limit:** Is 8 the maximum or are additional routes accessible via scrolling?
11. **Create Vibrato:** Where does this function appear? What does it create?
12. **LFO Bus:** Is this MATRIX-owned (route parameter) or LFO-owned (LFO parameter)?
13. **Macro Depth:** Is this a MATRIX column/control or part of Macro assignment?
14. **Destination Expansion:** What specific parameters appear in each destination submenu?

---

## CROSS-SYSTEM INTEGRATION NOTES

- MATRIX routes combine existing subsystem sources (LFO, ENV, MACRO, OSC, KEYBOARD, etc.) with MATRIX-owned routing logic
- MATRIX destinations reference existing subsystem parameters (OSC parameters, FILTER parameters, etc.)
- No duplicate semantic controls should be created for destination parameters; they remain owned by their source subsystems
- MATRIX semantic identity: the routing system, source/destination mapping, and route parameter controls (SOURCE, AMOUNT, DESTINATION, AUX SOURCE, CVY, POL, INV, AUX CVY)

---

## PASS 2 COMPLETION STATUS

✅ Route structure identified (10 columns per route)  
✅ Primary SOURCE universe enumerated  
✅ Auxiliary SOURCE universe enumerated  
✅ DESTINATION top-level categories identified (17 categories)  
❌ DESTINATION submenus not yet fully enumerated  
❌ CVY/POL/INV/AUX CVY/OUTPUT editability not yet confirmed  
❌ Route creation/deletion/bypass mechanisms not yet confirmed  
❌ Route count limits and scrolling access not yet tested  

**Recommendation:** PASS 3 should focus on resolving the TBD items through direct UI interaction (clicking controls, expanding menus, testing operations).

---

Generated: 2026-09-15  
Method: Direct Serum 2.0.21 UI investigation  
Next: PASS 3 — Final control enumeration and closure gate verification
