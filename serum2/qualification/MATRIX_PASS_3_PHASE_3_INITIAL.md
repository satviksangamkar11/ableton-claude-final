# MATRIX Pass 3 Phase 3 — Route Mechanics (INITIAL FINDINGS)

**Date:** 2026-09-15 (Session 3 Continuation)  
**Status:** IN PROGRESS — Foundation established, critical tests initiated  
**Method:** Direct UI testing via live MATRIX panel interaction

---

## ROUTE CAPACITY

**Finding:** 8 visible route rows in standard MATRIX view

- **Observed:** Standard view displays exactly 8 modulation route rows
- **Scrolling test:** Scrolling down in route area did NOT reveal additional rows
- **Interpretation:** Maximum route capacity = 8 (or possibly more, requires full capacity test)

**Next test:** Populate all 8 rows with active routes to determine true maximum

---

## ROUTE CREATION MECHANISM

**Finding:** Routes auto-create on SOURCE selection

- **Mechanism:** Clicking SOURCE field on empty row and selecting a source automatically creates the route
- **No explicit "Create Route" button:** Routes are created by populating SOURCE field
- **Behavior:** Empty rows can immediately receive SOURCE selections; no separate creation step required

**Classification:** AUTO-CREATE on SOURCE selection

---

## ROUTE DELETION MECHANISM

**Finding:** Routes are deleted by clearing SOURCE to "Off"

- **Mechanism:** Right-click on SOURCE field → Select "Off" from menu
- **Effect:** Setting SOURCE="Off" clears the entire route (all columns reset to "-")
- **No separate delete button:** No visible delete/remove button or context menu option
- **Classification:** CLEAR via SOURCE field to "Off"

---

## ROUTE STRUCTURE (VERIFIED)

Per-route layout confirmed — 10 columns per route:

```
SOURCE | CVY | AMOUNT | POL | DESTINATION | OUT | AUX SOURCE | INV | CVY | OUTPUT
```

- **SOURCE:** Dropdown (LFO 1-10, Envelopes, Macros, Note, OSC, MPE, Filters, etc.)
- **CVY:** Curve selector (control type TBD)
- **AMOUNT:** Knob/continuous (modulation depth)
- **POL:** Polarity control (options TBD)
- **DESTINATION:** Hierarchical dropdown (17 top-level categories enumerated)
- **OUT:** Read-only output value display
- **AUX SOURCE:** Secondary source dropdown (same options as SOURCE)
- **INV:** Auxiliary inversion control (type TBD)
- **CVY:** Secondary curve (for AUX SOURCE, type TBD)
- **OUTPUT:** Final output value display (similar to OUT)

---

## CRITICAL ROUTE MECHANICS STILL TBD

### CVY Control (Curve Selection)
- **Question:** What curve options are available?
- **Status:** UNVERIFIED — needs direct enumeration
- **Test:** Click CVY field to see dropdown/selector options

### POL Control (Polarity Mode)
- **Question:** What polarity modes exist? (Positive, Negative, Bipolar, Unipolar, Off?)
- **Status:** UNVERIFIED
- **Test:** Click POL field to enumerate options

### INV Control (AUX Inversion)
- **Question:** Simple boolean toggle or selector?
- **Status:** UNVERIFIED
- **Test:** Click INV field to determine control type

### AUX SOURCE Combination Logic
- **Question:** How do primary and auxiliary sources combine?
  - Additive (primary + aux)?
  - Multiplicative (primary × aux)?
  - Replacement (aux replaces primary under conditions)?
  - Scaling (aux scales primary amount)?
- **Status:** UNVERIFIED
- **Test:** Create routes with AUX SOURCE, measure output behavior

### Route Bypass Mechanism
- **Question:** Can individual routes be bypassed without deletion?
- **Status:** NOT FOUND — no visible bypass toggle observed
- **Possibilities:** 
  - Bypass via context menu (not yet tested)
  - Bypass via SET SOURCE="Off" (actually deletion, not bypass)
  - No bypass capability (routes are on/off only)
- **Test:** Right-click on route row; check for bypass option

### Route Reorder Mechanism
- **Question:** Can route order be changed?
- **Status:** NOT FOUND — no drag handles or reorder buttons observed
- **Possibilities:**
  - Reorder via drag-drop (test needed)
  - Reorder via up/down arrows (not visible)
  - Fixed order (routes processed in row order 1-8)
- **Test:** Attempt to drag routes or look for reorder controls

---

## UNRESOLVED SEMANTIC QUESTIONS FOR PHASE 3

- [ ] **Bypass:** Is there a per-route bypass mechanism separate from deletion?
- [ ] **Reorder:** Can routes be reordered, or is row order fixed?
- [ ] **CVY options:** What curve shapes or types are available?
- [ ] **POL options:** Complete enumeration of polarity modes
- [ ] **INV type:** Toggle vs. selector; how does it interact with AUX SOURCE?
- [ ] **AUX combination:** Additive, multiplicative, or other logic?
- [ ] **Route capacity:** Is 8 truly the maximum, or can more be added?
- [ ] **Duplicate routes:** Can the same SOURCE → DESTINATION pair be assigned twice?
- [ ] **Create Vibrato:** Where does this function appear? What does it create?
- [ ] **LFO Bus:** Is "LFO Busses" a MATRIX-owned destination or LFO-owned parameter?
- [ ] **Macro Depth:** Column ownership (MATRIX vs. MACRO section)?

---

## PHASE 3 COMPLETION STATUS

| Item | Status | Evidence |
|------|--------|----------|
| Route capacity limit | ⚠️ PARTIAL | 8 rows visible; scroll test negative; full population test pending |
| Route creation | ✅ VERIFIED | Auto-create on SOURCE selection confirmed |
| Route deletion | ✅ VERIFIED | Clear via SOURCE="Off" mechanism confirmed |
| Route structure | ✅ VERIFIED | 10-column layout confirmed via direct observation |
| CVY control | ❌ PENDING | Control type unknown; options not enumerated |
| POL control | ❌ PENDING | Control type unknown; options not enumerated |
| INV control | ❌ PENDING | Control type unknown; toggles/options not enumerated |
| AUX combination | ❌ PENDING | Interaction model unknown |
| Route bypass | ❌ PENDING | Mechanism not found |
| Route reorder | ❌ PENDING | Mechanism not found |
| Duplicate routes | ❌ PENDING | Allowed/disallowed status unknown |
| Route processing order | ❌ PENDING | Unknown if order matters |

---

## NEXT SESSION PHASE 3 CONTINUATION

**Priority order:**
1. Complete route capacity test (populate all 8 rows)
2. Enumerate CVY, POL, INV options via direct clicks
3. Test AUX SOURCE combination logic (behavioral testing)
4. Locate bypass/reorder mechanisms (if they exist)
5. Document Create Vibrato, LFO Bus, Macro Depth semantics

**Prerequisite for MATRIX closure gate:** Complete Phase 3 verification of all route mechanics and unresolved questions.

---

Generated: 2026-09-15 (Session 3, Continuation)  
Method: Direct UI testing of MATRIX route mechanics  
Status: Phase 3 IN PROGRESS — foundation solid, detailed control enumeration pending
