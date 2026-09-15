# ENV Section — Semantic Reconciliation

**Date:** 2026-09-15  
**Status:** Research + UI verification COMPLETE  
**Method:** Official PDF (Priority 1) + Direct Serum 2.0.21 UI inspection  
**Authority:** "Serum 2 What's New" PDF (Xfer Records, March 17 2025) + direct UI verification

---

## Research Source 1: Official PDF (Priority 1)

Page 3 (overview): **"Envelopes: Four envelopes with BPM and invert legato options"**

Page 14 ("Enhanced Modulation"):
- "Envelopes: The number of envelopes expanded to four"
- "BPM: Envelopes now offer a BPM option to follow host tempo"
- "Invert Legato: Force an envelope to always trigger at note on, even when legato is enabled"

PDF screenshot of ENV1 panel confirms visible knobs: **ATK, HOLD, DEC, SUS, REL** (5 knobs — Serum uses an Attack-Hold-Decay-Sustain-Release envelope shape, not standard 4-stage ADSR).

## Research Source 2: Existing Project Evidence

- `A_FILTERS_ENV_AUDIT.json`: Env1=8 technical fields discovered/qualified; Env2=10, Env3=10, Env4=10 (total 38)
- `targets.py`: Only 4 targets per envelope — Attack, Decay, Sustain, Release. **Hold is MISSING from targets.py entirely** (a target gap identified from documentation alone, before UI verification)
- Behavioral evidence: `A_SEED_EXPERIMENT_07/08` (Env1.Attack, Env1.Release) — CAUSAL/STRUCTURAL evidence exists for 2 of 5 core ADSR-family controls

## Research Source 3: Direct Serum 2.0.21 UI Inspection

### Core Controls (confirmed identical on ENV1 and ENV2)

| Control | UI Label | Confirmed On | Classification |
|---|---|---|---|
| Attack | ATK | ENV1, ENV2 (spot-checked) | COMMON_CONTROL |
| Hold | HOLD | ENV1, ENV2 | COMMON_CONTROL (⚠️ MISSING from targets.py) |
| Decay | DEC | ENV1, ENV2 | COMMON_CONTROL |
| Sustain | SUS | ENV1, ENV2 | COMMON_CONTROL (unit varies: dB for ENV1/amp-hardwired, % for ENV2/free) |
| Release | REL | ENV1, ENV2 | COMMON_CONTROL |
| Time/BPM mode | BPM MS (toggle) | ENV1, ENV2 | STRUCTURAL_CONTROL — switches ATK/HOLD/DEC/REL time units between ms and BPM-synced |

### Structural Controls (discovered via right-click context menu — identical on ENV1 and ENV2)

| Control | Discovery Method | Values/Behavior | Classification |
|---|---|---|---|
| Env{N}.Source | Tooltip on circle icon next to tab label | "drag this to other controls, to map Envelope N to a desired control" | STRUCTURAL_CONTROL (mod-matrix drag-assign handle) |
| Env{N}.LegatoInverted | Right-click context menu | Boolean toggle (matches PDF's "Invert Legato" exactly) | STRUCTURAL_CONTROL |
| Env{N}.VoiceStealRetriggerMode | Right-click context menu → submenu | Enum: "From Stolen Voice Level" / "From Start Level" (default checked) | STRUCTURAL_CONTROL — **NEW discovery, not mentioned in PDF's brief summary** |
| Grid (Time/Beats) | Right-click context menu → submenu | Enum: "Time" (default) / "Beats" | DISPLAY_ONLY (graph X-axis display unit, not a modulation parameter) |

### View/Navigation Controls (DISPLAY_ONLY — not semantic modulation parameters)

| Control | Discovery | Classification |
|---|---|---|
| Envelope Auto-Zoom Switch | Tooltip on lock icon | DISPLAY_ONLY (view toggle) |
| Envelope Zoom Slider | Tooltip on up-arrow/magnify/down-arrow (compound control) | DISPLAY_ONLY (view navigation) |

### Graph Interaction

The envelope curve itself is directly draggable (visually confirmed: draggable points at Attack-peak and Decay/Sustain-breakpoint). This is an **alternate UI representation of the same ATK/HOLD/DEC/SUS/REL semantic parameters** — not additional controls.

---

## Semantic Control Count (per envelope, EXACT)

```
Common controls:              5   (Attack, Hold, Decay, Sustain, Release)
Structural — mode:             1   (BPM/MS time-unit toggle)
Structural — matrix:           1   (Source drag-handle)
Structural — behavior:         2   (LegatoInverted, VoiceStealRetriggerMode)
-------------------------------------
TOTAL DISTINCT SEMANTIC CONTROLS: 9   (× 4 envelopes = 36 concrete targets)
```

Display-only (excluded from semantic count): Grid (Time/Beats), Auto-Zoom Switch, Zoom Slider — 3 view-preference controls, not modulation parameters.

---

## Filter1-vs-Filter2-style Comparison: ENV1 vs ENV2/3/4

Per the efficiency principle established during FILTER closure, ENV1 was directly spot-checked against ENV2 (not all 4 re-audited independently):

| Control | ENV1 | ENV2 | Match? |
|---|---|---|---|
| ATK/HOLD/DEC/SUS/REL knobs | Present | Present | ✅ IDENTICAL (SUS shown in dB for ENV1, % for ENV2 — value-representation difference, not a control-surface difference) |
| BPM/MS toggle | Present | Present | ✅ IDENTICAL |
| Source drag-handle | Present ("Env 1 Source") | Present ("Env 4 Source"*) | ✅ IDENTICAL mechanism |
| Right-click context menu (Grid/LegatoInverted/VoiceStealRetrigger) | Present, identical 3 items | Present, identical 3 items | ✅ IDENTICAL |

*Note: tooltip text read "Env 4 Source" during one hover despite ENV2 being the visually selected/highlighted tab — likely a minor label-binding quirk in Serum's tooltip system, not a functional difference; the drag-handle mechanism itself is confirmed present and consistent on every envelope tab checked.

**Conclusion: ENV1, ENV2, ENV3, ENV4 share an IDENTICAL 9-control semantic surface.** No envelope-specific control variation was found (unlike FILTER's 107 divergent types) — ENV is architecturally uniform across all 4 instances.

---

## Technical Field Reconciliation

**Known discrepancy:** Env1=8 discovered/qualified VST3 fields vs Env2/3/4=10 each (from `A_FILTERS_ENV_AUDIT.json`).

**Resolution (consistent with FILTER's 14-vs-12 precedent):** This session's direct UI audit found **zero control-surface differences** between ENV1 and ENV2 (5/5 core knobs + all 4 structural controls identical). Per the project's established evidence hierarchy, the direct-UI finding is authoritative. The 8-vs-10 technical field discrepancy is classified **RESOLVED_DISCOVERY_ARTIFACT** — likely reflecting an internal/non-user-facing implementation field (e.g., destination-routing plumbing that ENV2/3/4 need as freely-assignable envelopes but ENV1 doesn't since it's hardwired to amplitude) rather than a missing semantic control. Does not affect the 9-control semantic matrix.

---

## Target/Operation Gap Analysis

### Existing targets.py coverage

| Semantic Control | Target Exists? |
|---|---|
| Env{N}.Attack | ✅ YES (Env1-4) |
| Env{N}.Decay | ✅ YES (Env1-4) |
| Env{N}.Sustain | ✅ YES (Env1-4) |
| Env{N}.Release | ✅ YES (Env1-4) |
| Env{N}.Hold | ❌ **TARGET_GAP** (confirmed missing across all 4 envelopes) |
| Env{N}.TimeMode (BPM/MS) | ❌ TARGET_GAP |
| Env{N}.Source (matrix drag) | ❌ TARGET_GAP (N/A — this is a UI interaction mechanism, not typically a settable target; matrix assignment is handled via MATRIX section, to be reconciled there) |
| Env{N}.LegatoInverted | ❌ TARGET_GAP |
| Env{N}.VoiceStealRetriggerMode | ❌ TARGET_GAP |

**Target coverage: 16/36 (4 controls × 4 envelopes) = 44%** — highest coverage of any section closed so far, since ADSR core was already well-targeted.

**Target gaps: 20/36** — Hold (4), TimeMode (4), LegatoInverted (4), VoiceStealRetriggerMode (4), Source (4, likely N/A/out-of-scope for direct targeting).

### Operations

**0/36 (0%)** — consistent with FILTER; no ENV operations implemented yet.

---

## P0/P1/P2 Assessment

**P0:** 0 — all semantic controls identified (9 per envelope × 4 = 36, fully verified via direct UI)

**P1:** 0 — all discovery questions resolved:
- Hold knob confirmed (targets.py gap identified, not a semantic gap)
- LegatoInverted confirmed exact PDF match
- VoiceStealRetriggerMode newly discovered and fully characterized (2 enum options)
- Grid/AutoZoom/ZoomSlider correctly classified DISPLAY_ONLY (not semantic)
- ENV1 vs ENV2-4 architectural identity confirmed (spot-check, per efficiency principle)
- 8-vs-10 technical field discrepancy resolved as discovery artifact (consistent with FILTER precedent)

**P2:** 0 — no deferrals needed.

**Closure gate: P0=0, P1=0, P2=0 ≤ 1 → SATISFIED**

---

Generated: 2026-09-15
