# MATRIX DESTINATION ENUMERATION — EXACT PARAMETER TRACKING

**Status:** Destination-family enumeration: 15/15 actual destination families = 100% (16/16 top-level menu entries inspected, including Off, which is the empty state and not a destination family). Routability: COMPLETE (9/9 non-cross-referenced families behaviorally route-tested). Phase 2C route mechanics: NOT STARTED. Note: destination enumeration + routability being complete does NOT itself close MATRIX — structural/cross-system route-mechanics coverage (Phase 2C) is still required.
**Method:** Direct Serum UI systematic scrolling to completion per category  
**Standard:** Exact parameter counts and labels (no approximations, no assumptions)
**Canonical authority note:** This Markdown file is a convenience/audit view, not the semantic authority. `SERUM2_SEMANTIC_INVENTORY.json` → `meta.matrix_closure_ledger` is canonical; this file must remain synchronized with it, not the reverse.

---

## VERIFIED CATEGORIES (EXACT COUNTS)

### 1. OSC A — MODE-CONDITIONAL (23–38 exact, per mode) ✅
| Mode | Count |
|------|------:|
| Wavetable | 23 |
| Multisample | 29 |
| Sample | 33 |
| Granular | 37 |
| Spectral | 38 |

**Spectral-mode exact label list (38 params, directly UI-verified):**
Level, Pan, Octave, Semi, Fine, Coarse Pitch, Ratio, Hz Offset, Start, End, Reverse, Scan Rate, Scan BPM Rate, Position, Loop Start, Loop End, Loop X-Fade, Loop Mode, Relative Loop, Slice Play Mode, Single Slice, Uni Detune, Uni Blend, Uni Width, Uni Range, Uni Rotate, Uni Span, Uni Rand Start, Uni Warp, Uni Warp 2, Warp, Warp Var, Warp 2, Warp 2 Var, Spec Fit Cutoff, Spec Fit Wet/Dry, Freq Lo, Freq Hi

**Semantic ownership:** OSC section (existing, CLOSED_STAR)  
**New controls created:** None

### 2. Filter 1 — 7 PARAMETERS ✅
Wet, Freq, Res, Drive, Var, Stereo, Level

**Semantic ownership:** FILTER section (existing)  
**New controls created:** None

### 3. Filter 2 — 7 PARAMETERS ✅
Wet, Freq, Res, Drive, Var, Stereo, Level

**Semantic ownership:** FILTER section (existing)  
**New controls created:** None

### 4. Env 1 — 8 PARAMETERS ✅
Attack, Hold, Decay, Sustain, Release, Atk Curve, Dec Curve, Rel Curve

**Semantic ownership:** ENV section (existing)  
**New controls created:** None

### 5. Global — 7 PARAMETERS ✅
Main Tuning, Amp, Porta Time, Swing, Transpose, Envelope Scaling, LFO Scaling

**Semantic ownership:** GLOBAL section (new, requires documentation)  
**New controls created:** Possibly all (new subsystem)

---

## REMAINING 14 CATEGORIES (enumeration now complete — heading retained for session-history continuity, see PHASE 2B COMPLETION SUMMARY for current status)

### OSC B — MODE-CONDITIONAL (23–38 exact, per mode) ✅
| Mode | Count |
|------|------:|
| Wavetable | 23 |
| Multisample | 29 |
| Sample | 33 |
| Granular | 37 |
| Spectral | 38 |

**Wavetable-mode exact label list (23 params, directly UI-verified):**
Level, Pan, Octave, Semi, Fine, Coarse Pitch, Ratio, Hz Offset, Uni Detune, Uni Blend, Uni Width, Uni Range, Uni Rotate, Uni Warp, Uni Warp 2, Warp, Warp Var, Warp 2, Warp 2 Var, WT Pos, Uni WT Pos, Phase, Rand Phase

Ownership: OSC section (existing, CLOSED_STAR)  
Status: VERIFIED — mode-conditional coverage identical to OSC A across all 5 modes.

> **SUPERSEDED CLAIM (retained for audit history, do not treat as current):**
> "OSC B ≠ OSC A in parameter set (NOT parity, different feature set) — OSC A (38): Sampling/granular focus; OSC B (23): Wavetable/synthesis focus; IMPLICATION: Each OSC (A, B, C) likely has unique feature sets due to different synthesis engines."
> **CURRENT STATUS: SUPERSEDED.**
> **REASON:** Later direct UI enumeration verified identical conditional coverage across all three oscillators: Wavetable 23, Multisample 29, Sample 33, Granular 37, Spectral 38. The original 38-vs-23 reading was a mode snapshot (OSC A observed in Spectral mode, OSC B observed in Wavetable mode), not a permanent architectural difference between oscillator instances.

### OSC C — MODE-CONDITIONAL (23–38 exact, per mode) ✅
| Mode | Count |
|------|------:|
| Wavetable | 23 |
| Multisample | 29 |
| Sample | 33 |
| Granular | 37 |
| Spectral | 38 |

**Wavetable-mode exact label list (23 params, directly UI-verified):**
Level, Pan, Octave, Semi, Fine, Coarse Pitch, Ratio, Hz Offset, Uni Detune, Uni Blend, Uni Width, Uni Range, Uni Rotate, Uni Warp, Uni Warp 2, Warp, Warp Var, Warp 2, Warp 2 Var, WT Pos, Uni WT Pos, Phase, Rand Phase

Ownership: OSC section (existing, CLOSED_STAR)  
Status: VERIFIED — mode-conditional coverage identical to OSC A/B across all 5 modes.

> **SUPERSEDED CLAIM (retained for audit history, do not treat as current):**
> "OSC C ≡ OSC B (IDENTICAL wavetable feature set; NOT parity with OSC A)."
> **CURRENT STATUS: SUPERSEDED.**
> **REASON:** Later direct UI enumeration verified identical conditional coverage across all three oscillators: Wavetable 23, Multisample 29, Sample 33, Granular 37, Spectral 38. The original OSC C Wavetable/Spectral anomaly (see MATRIX_LFO_AUDIT_CORRECTION.md-equivalent OSC investigation) was traced to a stale prior observation and directly re-verified, not a real contradiction.

### Noise OSC — 6 PARAMETERS ✅
Level, Pan, Pitch, Fine, Phase, Rand Phase

**Semantic ownership:** OSC section (existing)  
**Routability:** VERIFIED (LFO 1 → Noise OSC Level tested and persisted)  
Status: COMPLETE

### SUB OSC — 5 PARAMETERS ✅
Level, Pan, Octave, Coarse Pitch, Phase

**Semantic ownership:** OSC section (existing)  
**Routability:** VERIFIED (LFO 1 → SUB OSC Level tested and persisted)  
Status: COMPLETE

### Macros — 8 PARAMETERS ✅
Macro 1, Macro 2, Macro 3, Macro 4, Macro 5, Macro 6, Macro 7, Macro 8

**Semantic ownership:** MACRO section (existing)  
**Routability:** VERIFIED (LFO 1 → Macro 1 tested and persisted)  
Status: COMPLETE

### LFO Busses — 16 PARAMETERS ✅
LFO Bus 1, LFO Bus 2, LFO Bus 3, LFO Bus 4, LFO Bus 5, LFO Bus 6, LFO Bus 7, LFO Bus 8, LFO Bus 9, LFO Bus 10, LFO Bus 11, LFO Bus 12, LFO Bus 13, LFO Bus 14, LFO Bus 15, LFO Bus 16

**Semantic ownership:** MATRIX-owned (new subsystem)  
Status: COMPLETE

### Routing Matrix — 19 PARAMETERS ✅
A>Filter Balance, A>BUS1, A>BUS2, B>Filter Balance, B>BUS1, B>BUS2, C>Filter Balance, C>BUS1, C>BUS2, Noise>Filter Balance, Noise>BUS1, Noise>BUS2, Sub Osc>Filter Balance, Sub Osc>BUS1, Sub Osc>BUS2, Filter 1>BUS1, Filter 1>BUS2, Filter 2>BUS1, Filter 2>BUS2

**Semantic ownership:** MATRIX-owned (self-modulation routing)  
Status: COMPLETE

### Clip Player — 39 PARAMETERS ✅
Clip Player Transpose, Clip Player Rate, Clip Player Offset, Clip 1-12 (Transpose, Rate, Offset each)

**Semantic ownership:** CLIP subsystem (new)  
Status: COMPLETE

### Arpeggiator — 14 PARAMETERS ✅
Rate, Shift, Range, Offset, Repeats, Gate, Chance, Retrig Rate, Velo Decay, Velo Target, Transpose, Wrap Transpose, Wrap Range, Wrap Phantom Note

**Semantic ownership:** ARP subsystem (new)  
Status: COMPLETE

### Retriggers — 19 PARAMETERS ✅
Note, OSC A, OSC B, OSC C, Sub, Noise, Env 2, Env 3, Env 4, LFO 1-10

**Semantic ownership:** GLOBAL/VOICE subsystem (new)  
Status: COMPLETE

---

## CRITICAL CORRECTION PRESERVED

```text
INVALIDATED CLAIM:
  "LFO 6 available as destination with 5 parameters (Rate, Smooth, Rise, Delay, Phase)"

CORRECTED FINDING:
  "No LFO destination category exists in Matrix DESTINATION menu"
  "LFO semantic universe = 90 controls (PRESERVED)"
  "LFO Matrix destinations = 0/90 (NOT 5/90)"
  "LFO control path = DIRECT_UI_ONLY"
```

---

## SEMANTIC OWNERSHIP RECONCILIATION (IN PROGRESS)

### Existing Sections (No New Controls Created):
- **OSC A/B/C parameters** → OSC section
- **Filter 1/2 parameters** → FILTER section
- **Env 1 parameters** → ENV section
- **Macros parameters** → MACRO section (if only 8 depth controls)

### New Sections (Controls Introduced by Matrix):
- **Global section** → Ownership: GLOBAL
- **LFO Busses** → Ownership: RESOLVED — MATRIX (new subsystem, distinct entity from the CLOSED_STAR LFO section's 10 LFO instances despite the name similarity; see matrix_closure_ledger.destination_family_exact_counts.LFO_Busses in the JSON for full reasoning)
- **Routing Matrix** → Ownership: MATRIX
- **Clip Player** → Ownership: CLIP subsystem (new, deferred to its own pending section)
- **Arpeggiator** → Ownership: ARP subsystem (new, deferred to its own pending section)
- **Retriggers** → Ownership: RESOLVED — GLOBAL/VOICE subsystem (new, deferred to its own pending section)

---

## NEXT SESSION EXECUTION PLAN

**Phase 2A (Destination Enumeration Continuation):**
```
1. OSC B: Enumerate all parameters, confirm or refute parity with OSC A
2. OSC C: Enumerate all parameters, confirm or refute parity with OSC A
3. Noise OSC: Complete enumeration
4. SUB OSC: Complete enumeration
5. Macros: Verify count and parameter names
6. LFO Busses: Complete enumeration (new category, no assumptions)
7. Routing Matrix: Complete enumeration (new category, no assumptions)
8. Clip Player: Complete enumeration (new category, no assumptions)
9. Arpeggiator: Complete enumeration (new category, no assumptions)
10. Retriggers: Complete enumeration (new category, no assumptions)
```

**Phase 3 (Route Mechanics Resolution):**
```
Explicit P0/P1 Items:
- P0-01: CVY options and editability
- P0-02: POL options
- P0-03: AUX SOURCE combination logic (additive/multiplicative/other)
- P0-04: AUX MOD/INV control type and options
- P0-05: OUT vs OUTPUT distinction (if any)
- P0-06: Route bypass mechanism (if exists)
- P0-07: Route reorder mechanism (if exists)
- P0-08: Route delete/clear mechanism (VERIFIED: via SOURCE="Off")
- P0-09: Route creation mechanism (VERIFIED: auto-create on SOURCE selection)
- P0-10: Exact route capacity and scroll behavior
- P1-01: Create Vibrato function (location, mechanics)
- P1-02: LFO Bus semantic identity (MATRIX vs LFO owned)
- P1-03: Macro Depth control (MATRIX vs MACRO owned)
- P1-04: Hidden/context actions (right-click, keyboard, etc.)
```

---

## METRICS TRACKING (superseded — retained for audit history only)

**CURRENT STATUS: SUPERSEDED.** The table below reflects a mid-session snapshot taken before Noise OSC, SUB OSC, Macros, LFO Busses, Routing Matrix, Clip Player, Arpeggiator, and Retriggers were enumerated, and before the OSC A/B/C mode-conditional model was established. Do not read counts, ownership, or verification status from this table — see PHASE 2B COMPLETION SUMMARY below for the current, correct state.

| Category | Count (stale) | Verified (stale) | Ownership (stale) | New Control? |
|----------|-------|----------|-----------|--------------|
| OSC A | 38 | ✅ | OSC | No |
| OSC B | 23 | ✅ | OSC | No |
| OSC C | 23 | ✅ | OSC | No |
| Noise OSC | ? | ⏳ | OSC | No |
| SUB OSC | ? | ⏳ | OSC | No |
| Filter 1 | 7 | ✅ | FILTER | No |
| Filter 2 | 7 | ✅ | FILTER | No |
| Env 1 | 8 | ✅ | ENV | No |
| Macros | ? | ⏳ | MACRO | No |
| LFO Busses | ? | ⏳ | TBD | TBD |
| Routing Matrix | ? | ⏳ | MATRIX | TBD |
| Clip Player | ? | ⏳ | CLIP | Yes |
| Arpeggiator | ? | ⏳ | ARP | Yes |
| Retriggers | ? | ⏳ | GLOBAL/VOICE | Yes |
| Global | 7 | ✅ | GLOBAL | Yes |

**Superseded:** This "92 parameters / 7 categories remaining" line is from the mid-session snapshot and predates completion of all 15 families. Do not treat as current.

---

## CLOSURE GATE REQUIREMENTS (updated)

```text
SOURCE enumeration              = ✅ COMPLETE (Phase 2A)
DESTINATION enumeration         = ✅ COMPLETE (Phase 2B — 15/15 families, 100%)
DESTINATION routability         = ✅ COMPLETE (9/9 non-cross-referenced families route-tested)
ROUTE CONTROLS enumeration      = ⏳ FOUNDATION ONLY (structure verified, mechanics TBD — Phase 2C)
CONDITIONAL STATES              = ✅ COMPLETE for OSC A/B/C (all 5 modes each, identical coverage)
STRUCTURAL ACTIONS              = ⏳ PARTIAL (create/delete verified, reorder/bypass TBD — Phase 2C)
CROSS-SYSTEM OWNERSHIP          = ✅ COMPLETE (cross-referenced to existing CLOSED_STAR OSC/FILTER/ENV/MACRO records; ARP/CLIP/GLOBAL deferred to their own pending sections)
P0 (unresolved gaps)            = 0
P1 (cheap resolution gaps)      = 1 (ENV Curve-destination cross-section reconciliation)
P2 (deferrals)                  = 0
```

**Gate Status:** MATRIX cannot close until: (1) Phase 2C route mechanics completes (capacity, duplicates, delete, reorder, bypass, CVY, POL, AUX SOURCE, AUX MOD/INV, AUX CVY, OUT, OUTPUT/visualization, Create Vibrato), (2) the 1 remaining P1 is resolved or formally deferred as the section's single allowed P2. Destination enumeration and routability are no longer blockers.

**Canonical authority:** This file is a convenience/audit view. `SERUM2_SEMANTIC_INVENTORY.json` → `meta.matrix_closure_ledger` is the authoritative semantic artifact; figures here must match it.

---

**Generated:** 2026-09-15 (Session 3, Continuation + Session 4 Completion)  
**Method:** Direct Serum UI exhaustive enumeration (no approximations, full systematicscrolling verification)  
**Authority:** Direct UI verification via MATRIX panel interaction  
**Confidence:** HIGH for all categories (100% enumerated and verified via direct Serum UI)

---

## PHASE 2B COMPLETION SUMMARY

**STATUS: ✅ COMPLETE**

### All 16 DESTINATION Categories Enumerated

Count is conditional (mode-dependent) for OSC A/B/C — a single flat number is not valid for these three; see mode breakdown below the table. All other counts are flat/fixed.

| # | Category | Count | Enumeration | Routability |
|---|----------|-------|-------------|-------------|
| 1 | OSC A | 23–38 (mode-conditional) | ✅ VERIFIED (all 5 modes) | N/A — cross-refs existing CLOSED_STAR OSC records |
| 2 | OSC B | 23–38 (mode-conditional) | ✅ VERIFIED (all 5 modes) | N/A — cross-refs existing CLOSED_STAR OSC records |
| 3 | OSC C | 23–38 (mode-conditional) | ✅ VERIFIED (all 5 modes) | N/A — cross-refs existing CLOSED_STAR OSC records |
| 4 | Noise OSC | 6 | ✅ VERIFIED | ✅ VERIFIED (LFO 1 → Level route tested, persisted, cleared) |
| 5 | SUB OSC | 5 | ✅ VERIFIED | ✅ VERIFIED (LFO 1 → Level route tested, persisted, cleared) |
| 6 | Filter 1 | 7 | ✅ VERIFIED | N/A — cross-refs existing CLOSED_STAR FILTER records |
| 7 | Filter 2 | 7 | ✅ VERIFIED | N/A — cross-refs existing CLOSED_STAR FILTER records |
| 8 | Env 1 | 8 | ✅ VERIFIED | N/A — cross-refs existing CLOSED_STAR ENV records (1 P1 gap: Curve destinations not in ENV's 9-control matrix) |
| 9 | Macros | 8 | ✅ VERIFIED | ✅ VERIFIED (LFO 1 → Macro 1 route tested, persisted, cleared) |
| 10 | LFO Busses | 16 | ✅ VERIFIED (scrolled to Bus 16) | ✅ VERIFIED — LFO 1 → LFO Bus 1, persisted, cleared |
| 11 | Routing Matrix | 19 | ✅ VERIFIED (scrolled to Filter 2>BUS2) | ✅ VERIFIED — Mod Wheel → A>Filter Balance, persisted, cleared |
| 12 | Clip Player | 39 | ✅ VERIFIED (global 3 + 12 clips × 3) | ✅ VERIFIED — LFO 1 → Clip Player Transpose, persisted, cleared |
| 13 | Arpeggiator | 14 | ✅ VERIFIED | ✅ VERIFIED — LFO 1 → Arp Rate, persisted, cleared |
| 14 | Retriggers | 19 | ✅ VERIFIED | ✅ VERIFIED — LFO 1 → Retrig Note, persisted, cleared |
| 15 | Global | 7 | ✅ VERIFIED | ✅ VERIFIED — LFO 1 → Main Tuning, persisted, cleared |

**Flat (non-conditional) family sum: 155 exact** (6+5+7+7+8+8+16+19+39+14+19+7)
**OSC A/B/C conditional contribution: 69 (all-Wavetable) to 114 (all-Spectral), per-oscillator 23–38**
**Combined envelope if a single figure is required: 224–269 — NOT a fixed total.** (A prior draft of this document stated an unqualified "251 exact"; that figure is withdrawn as non-auditable — see `SERUM2_SEMANTIC_INVENTORY.json` → `meta.matrix_closure_ledger` → `aggregate_count_definition`.)

**Enumeration: 15/15 families complete (100%)**
**Routability: 9/9 non-cross-referenced families behaviorally verified** (Noise OSC Level, SUB OSC Level, Macro 1, LFO Bus 1, Routing Matrix A>Filter Balance, Clip Player Transpose, Arp Rate, Retrig Note, Global Main Tuning). **Destination routability is fully closed.**

### Second routability pass (2026-09-15) — 5 tests run, all PASSED

For each: opened DESTINATION menu → selected family's first parameter → set SOURCE to LFO 1 (Routing Matrix used a pre-existing Mod Wheel source row instead, to avoid disturbing unrelated state) → verified route appeared and persisted → cleared (SOURCE=Off, or destination-only reset for the Mod Wheel row to preserve its original state exactly).

| Family | Route tested | Result |
|--------|-------------|--------|
| LFO Busses | LFO 1 → LFO Bus 1 | ✅ PASSED |
| Routing Matrix | Mod Wheel → A>Filter Balance | ✅ PASSED |
| Clip Player | LFO 1 → Clip Player Transpose | ✅ PASSED |
| Arpeggiator | LFO 1 → Arp Rate | ✅ PASSED |
| Retriggers | LFO 1 → Retrig Note | ✅ PASSED |

### Third routability pass (2026-09-15) — final gap closed

| Family | Route tested | Result |
|--------|-------------|--------|
| Global | LFO 1 → Main Tuning | ✅ PASSED (route accepted; persistence confirmed by reopening DESTINATION menu and observing "Global" checked; cleared via SOURCE=Off) |

**All 9/9 non-cross-referenced destination families are now routability-verified.** Schema note: Noise_OSC, SUB_OSC, and Macros previously used a legacy `routability` free-text field while the rest used `routability_status`/`routability_note`; this has been normalized to one schema across all 9 families in the canonical JSON (no evidence content changed, only field shape).

### Ready for Phase 2C (Route Mechanics Investigation)

Destination enumeration and routability are both fully resolved. Per Master Plan discipline, this does **not** by itself close MATRIX — Phase 2C route-mechanics coverage is still required: capacity → duplicates → delete → reorder → bypass → CVY → POL → Aux Source → Aux MOD/INV → Aux CVY → OUT → visualization → Create Vibrato.
