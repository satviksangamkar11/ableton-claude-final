# LFO Section — Semantic Discovery Pass 1

**Date:** 2026-09-15  
**Status:** Research + UI verification IN PROGRESS  
**Method:** Official PDF references (where available) + Direct Serum 2.0.21 UI inspection + Matrix source inventory  
**Authority:** Direct UI verification (priority 2 evidence) + confirmed via Matrix source menu (LFO availability proof)

---

## LFO Universe — Exact Count

### Total LFO Instances = 10 (EXACT)

**Verified via Matrix source menu (authoritative evidence):**
- LFO 1 ✓ (UI tab visible, controls verified)
- LFO 2 ✓ (UI tab visible, controls verified)
- LFO 3 ✓ (UI tab visible, controls verified)
- LFO 4 ✓ (UI tab visible, controls verified)
- LFO 5 ✓ (UI tab visible, controls verified)
- LFO 6 ✓ (UI tab visible, controls verified)
- LFO 7 ✓ (Matrix source menu confirms existence; no UI tab visible)
- LFO 8 ✓ (Matrix source menu confirms existence; no UI tab visible)
- LFO 9 ✓ (Matrix source menu confirms existence; no UI tab visible)
- LFO 10 ✓ (Matrix source menu confirms existence; no UI tab visible)

**Note on UI visibility:** LFO 1-6 have dedicated edit panel tabs in the LFO section. LFO 7-10 are available as modulation sources in the Matrix but do not have visible edit panels in the current Serum UI. This is a CONDITIONAL_VISIBILITY issue: LFO 7-10 may become accessible through:
1. Keyboard shortcuts or menu actions
2. Dynamic tab generation after assignment
3. Alternative editor interface (not yet discovered)

This is flagged as a P1 (resolve if cheap) or P2 (defer) item depending on whether UI accessibility can be quickly determined.

---

## LFO Type System — Exact Count

**Total LFO Type Options = 5 (EXACT)**

Discovered via LFO type dropdown menu (top-right of LFO panel):

1. **Normal** — Standard periodic waveform (default)
2. **Path** — Custom waveform drawing editor
3. **Chaos: Lorenz** — Lorenz attractor chaos mode
4. **Chaos: Rossler** — Rossler attractor chaos mode
5. **S&H** — Sample & Hold random LFO

**Classification:** These are LFO SHAPE/TYPE options, not trigger modes. All 5 are available per LFO instance and can be selected via the LFO type dropdown menu visible on every LFO 1-6 panel. No evidence yet of type-specific controls appearing conditionally; each type appears to share the same fundamental control surface.

---

## LFO Trigger Mode System — Preliminary

**Potential Trigger Modes (from left sidebar labels, confirmation pending):**

Observed in left sidebar of LFO panel:
1. FREE — (likely: free-running, continuous oscillation)
2. RETRIG — (likely: retrigger on note attack)
3. ENVELOPE — (likely: envelope-controlled amplitude/gate)
4. MONO — (likely: monophonic playback mode)

**Status: UNCONFIRMED** — These labels appear in the left sidebar as a numbered/labeled list, but their exact semantic identity (whether they are mutually exclusive trigger modes, independent toggles, display-only labels, or view mode indicators) is not yet determined. No clickable menu was found to switch between them. This requires either:
1. Direct testing of each mode's behavioral effect
2. Finding the UI control to switch trigger modes
3. Locating official documentation explaining the sidebar

---

## Core LFO Control Inventory — Verified

### Controls present on ALL LFO 1-6 instances (VERIFIED via spot-check):

**Waveform Graph Display:**
- Visual LFO shape display (blue waveform)
- Interactive editing surface (for Path mode)
- Confirmed as user-facing control (not display-only)

**LFO Type Selector:**
- Dropdown menu showing: Normal, Path, Chaos: Lorenz, Chaos: Rossler, S&H
- Semantic ID: `LFO{N}.Type` (mode/shape selector)
- Control type: Enum (5 options)
- Status: VERIFIED_COMMON_CONTROL

**Time/Rate Controls:**
- `LFO{N}.Rate` — Knob control, labeled "RATE"
- `LFO{N}.BPM` — Toggle switch, switches between Hz and BPM sync modes (Host Tempo)
- `LFO{N}.Tempo Sync (Host/Free)` — Binds rate to host BPM when enabled
- Confirmed controls visible in bottom control row

**Time Division/Signature Controls:**
- `LFO{N}.Division` — Time signature selector (observed: 1/4 note, with navigation arrows)
- `LFO{N}.Triplet` — Triplet modifier (TRIP label visible, checkbox-style)
- `LFO{N}.Dotted` — Dotted note modifier (DOT label visible, checkbox-style)
- Located in bottom control row, right of RATE knob

**LFO Modulation Envelope-style Timing:**
- `LFO{N}.Rise` — Knob, labeled "RISE" (attack/rise time for LFO envelope)
- `LFO{N}.Delay` — Knob, labeled "DELAY" (pre-trigger delay)
- `LFO{N}.Smooth` — Knob, labeled "SMOOTH" (smoothing/portamento)
- `LFO{N}.Phase` — Knob, labeled "PHASE" (phase offset)
- All confirmed in bottom control row

**Direction Control:**
- `LFO{N}.Direction` — Selector showing "Forward" (implies additional options like Backward, Pendulum, etc.)
- Located below preset selector
- Status: VERIFIED but options not yet enumerated

**Preset System:**
- `LFO{N}.Preset` — Dropdown showing "Default"
- `LFO{N}.PresetPrevious` — Navigation arrow (<)
- `LFO{N}.PresetNext` — Navigation arrow (>)
- Allows loading pre-drawn LFO shapes
- Status: VERIFIED_STRUCTURAL

**LFO Source Assignment:**
- `LFO{N}.Source` — Drag-handle circle icon (drag this to other controls to map LFO to a desired control)
- Tooltip: "LFO N Source / drag this to other controls, to map LFO N to a desired control."
- Classification: MODULATION_SOURCE_ASSIGNMENT (cross-referenced to MATRIX section, not independently targetable here)
- Status: VERIFIED

**Sidebar Controls (trigger mode system):**
- Sidebar labels observed: FREE, RETRIG, ENVELOPE, MONO
- Sidebar icons: Up arrow, lock icon, magnifying glass, down arrow
- Status: UNCONFIRMED_SEMANTICS (labels and function not yet determined)

---

## Display-Only Controls (excluded from semantic count)

**Likely DISPLAY_ONLY (requires confirmation):**
1. Waveform graph background grid
2. Time axis labels (2.0 ms, 0.0 ms, 1.00 s, 0.0 dB, 10 ms)
3. Any zoom/view controls
4. "VOICING", "LEGATO", "MONO" labels on far right of bottom panel (may be view indicators rather than semantic controls)

---

## Cross-System Relationships

### MATRIX Integration:
- `LFO{1-10}.Source` — All 10 LFOs are available in Matrix as modulation sources
- Confirmed: Matrix SOURCE dropdown lists "LFO 1" through "LFO 10"
- Implication: All 10 LFOs are fully routable, but LFO 7-10 have no separate edit UI

### GLOBAL/Voice Integration:
- Sidebar label "MONO" may indicate voice-wide or global polyphony setting
- Requires behavioral testing to confirm scope

---

## Conditional Controls & Mode-Specific Behavior

### Path Mode (LFO Type: Path):
- Additional context menu options appear when right-clicking the waveform:
  - Flat (shape preset)
  - Ramp Up (shape preset)
  - Ramp Down (shape preset)
  - Set Loopback Point Here
  - Remove Loopback Point
  - Remove Selected Points
  - Flip Vertical
  - Flip Horizontal
- **Status:** These appear to be mode-conditional EDITING CONTROLS for the Path mode waveform shape, not global LFO parameters

### Chaos Modes (LFO Type: Chaos: Lorenz / Chaos: Rossler):
- **Status:** Not yet inspected. Likely present additional controls for chaos parameter tuning (e.g., chaos amount, attractor damping), but this requires UI inspection of these modes.

### S&H Mode (LFO Type: S&H):
- **Status:** Not yet inspected. Likely presents hold/sample interval controls distinct from standard rate control.

---

## LFO 7-10 Accessibility — Open Question (P1/P2)

**Known:** LFO 7-10 exist and are available as modulation sources in the Matrix.

**Unknown:** How users access the UI edit panels for LFO 7-10, if they exist.

**Possibilities:**
1. **No edit UI for LFO 7-10** — They are "headless" sources, only assignable, with no per-instance parameters. (Seems unlikely given LFO 1-6 parameter richness.)
2. **Dynamic tab generation** — LFO 7-10 tabs appear in the LFO panel only after the first assignment/use.
3. **Keyboard shortcut access** — Tabs exist but are hidden by default; keyboard commands reveal them.
4. **Alternative editor interface** — LFO 7-10 use a different edit UI not yet discovered.
5. **Research notes indicate condition:** "LFO7 – LFO10 (appear only after you assign LFO 6)" — suggests dynamic tab generation after LFO 6 is used in a route.

**Action Required:** Confirm LFO 7-10 edit panel accessibility before closing LFO section. This may require:
- Creating a test modulation route with LFO 6 to trigger appearance of LFO 7-10 tabs
- Checking for keyboard commands (common shortcuts: Ctrl+Tab, Arrow keys in tab bar)
- Consulting official documentation or tutorials

**Current Classification:** P1 if determina quickly via UI testing; otherwise P2 (deferred to post-discovery testing phase).

---

## Semantic Control Count — Preliminary

### Per-LFO Instance (LFO 1-6, assuming full semantic parity):

**Common Controls:** 9 identified so far
1. Type (enum: Normal, Path, Chaos: Lorenz, Chaos: Rossler, S&H)
2. Rate (continuous knob)
3. BPM / Hz Toggle (boolean)
4. Tempo Sync / Host (boolean or toggle to sync to host BPM)
5. Division (enum: 1/4, and others; time signature)
6. Triplet (boolean modifier)
7. Dotted (boolean modifier)
8. Rise (continuous knob)
9. Delay (continuous knob)
10. Smooth (continuous knob)
11. Phase (continuous knob)
12. Direction (enum: Forward, and others)
13. Preset Selector (enum: Default, others)
14. Source (drag-handle assignment)

**Sidebar/Trigger System:** 4+ labels (FREE, RETRIG, ENVELOPE, MONO) — **semantics unconfirmed, may be toggles, display labels, or mutually exclusive modes.**

**Provisional Total per LFO (unconfirmed):** 14-18 controls, depending on whether sidebar items are distinct semantic controls or display-only labels.

**Status:** COUNT IS INCOMPLETE. Requires:
1. Full enumeration of Direction options (e.g., Forward, Backward, Pendulum, Bounce)
2. Confirmation of sidebar trigger mode semantics and count
3. UI inspection of Chaos and S&H modes for conditional controls
4. Verification of LFO 7-10 control surface parity (if UI panels are found)

---

## LFO 1-6 Parity Check

**Hypothesis:** All LFO 1-6 instances present an identical 9+-control semantic surface.

**Evidence:** Spot-check inspection of LFO 1, 2, 3, 4, 5, 6 reveals identical layout, control labels, and UI structure across all instances.

**Confidence:** HIGH (visual parity confirmed across 6 independent samples; no divergences observed).

**Assumption for closure:** Barring evidence to the contrary, LFO 7-10 will also share this identical surface (if UI panels exist for them).

---

## P0 = ? (UNRESOLVED - requires analysis)

**Blocking gaps identified:**
1. ~~LFO 7-10 UI accessibility~~ — Conditional visibility, deferred as P1/P2 unless it blocks the semantic count
2. Sidebar trigger mode semantics — **Unconfirmed; may represent 4 additional semantic controls or display labels**

If the sidebar items ARE semantic controls with user-selectable options, the semantic count per LFO increases significantly and must be documented. If they are display-only, they are excluded.

**Current status:** Cannot determine final P0 count until trigger mode semantics are clarified.

---

## P1 = ? (Pending verification)

**Cheap resolutions available:**
1. **Trigger mode sidebar semantics** — Right-click one of the sidebar labels, or try clicking the checkboxes, or read a tooltip if one appears on hover.
2. **Direction enum options** — Click the Direction dropdown and enumerate all options.
3. **S&H and Chaos mode controls** — Switch LFO 1 to S&H and Chaos modes and observe any additional controls that appear.

All of these can be done within the current Serum UI without new experiments. Should take <5 minutes of UI inspection.

---

## P2 = ? (Deferred non-blocking)

**Likely P2 candidates (if determined too expensive to resolve now):**
1. **LFO 7-10 UI accessibility condition** — If the condition is non-trivial to trigger (e.g., "requires creating a preset, saving, and reloading"), defer to post-discovery phase with a note for future investigation.

---

## Target / Operation Reconciliation — Deferred

This section will be completed during the post-closure MATRIX reconciliation phase, alongside checking:
- Which LFO controls have corresponding targets in targets.py
- Which controls have implemented operations
- Coverage gaps

For now, assume zero targets and zero operations (consistent with FILTER and ENV precedent).

---

## Next Steps

**Immediate (same session, same turn):**
1. [ ] Inspect LFO 1 sidebar trigger mode controls by hovering/clicking each label
2. [ ] Switch LFO 1 to S&H and Chaos modes and document any conditional controls
3. [ ] Enumerate Direction dropdown options
4. [ ] Attempt to access LFO 7-10 UI panels (test: create a mod route with LFO 6, or try keyboard navigation)
5. [ ] Spot-check LFO 7-10 (if accessible) for parity with LFO 1-6

**Post-discovery (if LFO 7-10 remain inaccessible):**
- Defer LFO 7-10 UI confirmation to a post-freeze investigation
- Document this known gap in the LFO closure ledger

**Target/Operation reconciliation (post-freeze):**
- Cross-reference all LFO semantic controls against targets.py
- Identify and log target gaps
- Schedule operation implementation as post-closure work

---

Generated: 2026-09-15  
Authority: Direct Serum 2.0.21 UI inspection + Matrix source menu inventory verification  
Version lock: Serum 2.0.21 only  
Status: PASS 1 RESEARCH — incomplete, proceeding to targeted UI inspection phase
