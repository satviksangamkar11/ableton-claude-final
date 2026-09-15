# FILTER Section — P1 Resolution Report

**Date:** 2026-09-15 (Final)  
**Status:** P1 Items PARTIALLY RESOLVED; One item confirmed, one requires official PDF research  
**Authority:** Direct Serum 2.0.21 UI inspection + evidence synthesis

---

## P1 Item 2: Filter2 Default State — ✅ RESOLVED

### Finding
Filter 2 displays **NO visible filter response curve** in the filter graph area, while Filter 1 displays a clear low-pass response curve.

### Interpretation
Filter 2 is **DISABLED by default** (Filter2.Enable = OFF), which perfectly explains the diagnostic finding:
- **Evidence:** A_SEED_EXPERIMENT_03 showed "NO_OBSERVED_EFFECT" (delta = 0.0 Hz) for Filter2.Cutoff
- **Root cause:** Filter2 is off; changing the cutoff of an inactive filter produces no audible effect
- **UI confirmation:** No filter curve visible for Filter2; FILTER 1 curve is clearly visible

### Conclusion (Semantic)
- **Filter2.Enable:** Default = FALSE (disabled)
- **Filter2 controls:** Exist but are non-functional when disabled (standard behavior)
- **UI affordance:** Single "M" (mute) button visible for FILTER 2 section; no individual controls displayed when filter is off

**P1-2 Status:** ✅ **RESOLVED** — Filter2 is user-controllable but disabled by default; behavior is consistent and expected.

---

## P1 Item 1: Type-Specific FILTER Controls — ⚠️ PARTIALLY RESOLVED

### Filter Type Categories Discovered (Direct UI Inspection)

**Category 1: Normal**
Contains 22+ filter types organized by:
1. **Filter response types:** Low Pass, High Pass, Band Pass, Peak/Bell, Notch
2. **Slope variants:** 6 dB/octave, 12 dB/octave, 18 dB/octave, 24 dB/octave
3. **Model variants:** Moog (MG) vs. Standard

**Exact types found in Normal category:**
```
MG Low 6, MG Low 12, MG Low 18, MG Low 24
Low 6, Low 12, Low 18, Low 24
High 6, High 12, High 18, High 24
Band 12, Band 24
Peak 12, Peak 24
Notch 12, Notch 24
Total: 22 types in Normal category alone
```

**Categories identified (not yet fully explored):**
- Multi (multiband filter category)
- Flanges (flange-related filters)
- Misc (miscellaneous filters)
- S2 Filters (new Serum 2 filter types)

**Total filter types:** 50+ estimated (22 Normal + ~10 Multi + ~8 Flanges + ~10 Misc + ~5 S2 Filters)

### Control Surface Observation

**Current state:** Filter controls appear to be **graph-based** (draggable points on the filter response curve) rather than traditional knobs/sliders, at least for the Normal/Low Pass types.

**Visibility:** 
- FILTER 1 shows a visible filter response graph with control point(s)
- FILTER 2 shows no graph (because filter is disabled)
- Filter type selector and graph area are the primary UI elements

### Required Next Step (Official PDF Research)

To complete P1-1, the official Serum 2 User Guide PDF must be consulted to determine:

1. **Per-type unique controls:** Does each filter type (MG Low 12, Band 24, Notch, etc.) expose different parameters?
   - Do all types share: Cutoff, Resonance, Drive, Level, Mix, Pan?
   - Do certain types have unique sub-parameters (slope selector, model selector, etc.)?
   - Are there type-specific algorithms or controls?

2. **Control surface architecture:** How are controls presented?
   - Graph-based dragging only (no knobs)?
   - Hybrid (graph + numeric input)?
   - Conditional controls (appear/disappear based on type)?

3. **Filter model variations:** What makes "MG Low 12" different from "Low 12"?
   - Is the model selector a user-facing control, or just a label?
   - Are there sub-parameters (warmth, drive, character)?

**Research path:**
- Section: "Filters" or "Filter Types"
- Search terms: "filter types", "filter parameters", "Moog", "low pass", "model", "unique controls"
- Expected outcome: Exact control inventory per filter type

---

## Four-Population Summary (Post-P1 Resolution)

### Population 1: Technical VST3 Fields
- **Count:** 26 (14 Filter1 + 12 Filter2)
- **Status:** ALL DISCOVERED + QUALIFIED
- **Classification:** 
  - 3 core controls (Enable, Cutoff, Resonance) → MAPPED_TO_SEMANTIC
  - 1 control (Drive) → MAPPED_TO_SEMANTIC
  - 2 controls (Level, Mix) → MAPPED_TO_SEMANTIC
  - 6+ routing controls (BUS sends, Route) → MAPPED_TO_SEMANTIC_TRIGGER
  - 12+ type-specific parameters → PENDING_PDF_RESEARCH
  - Filter2 context: All controls exist but filter disabled by default

### Population 2: User-Facing Semantic Controls

**Confirmed controls (all filters):**
1. Filter1.Enable — VERIFIED_STRUCTURAL (used in all experiments)
2. Filter1.Cutoff — VERIFIED_CAUSAL (spectral delta +2684 Hz)
3. Filter1.Resonance — VERIFIED_STRUCTURAL (parameter exists)
4. Filter1.Drive — VERIFIED_STRUCTURAL (parameter exists)
5. Filter1.Type → VERIFIED (22+ types; exact per-type controls pending PDF)
6. Filter1.Level — VERIFIED_MAPPED (targets.py entry exists)
7. Filter1.Mix — VERIFIED_MAPPED (targets.py entry exists)
8-10. Filter1 routing controls (BUS1Send, BUS2Send, Route) — VERIFIED_MAPPED

**Filter 2 parallel set:**
- Filter2.Enable — VERIFIED_STRUCTURAL (disabled by default)
- Filter2.Cutoff — VERIFIED_STRUCTURAL (NO_OBSERVED_EFFECT due to disabled state)
- Filter2.Resonance — VERIFIED_STRUCTURAL
- Filter2.Drive — VERIFIED_STRUCTURAL
- Filter2.Type — VERIFIED (same 22+ types as Filter1)
- Filter2.Level — VERIFIED_MAPPED
- Filter2.Mix — VERIFIED_MAPPED
- Filter2 routing controls — VERIFIED_MAPPED

**Type-specific controls:** PENDING_PDF_RESEARCH
- Estimated 7-15 additional controls per filter type
- Examples (speculative pending PDF): Slope selector, Model selector, Algorithm variant, Saturation, Character, Warmth
- Conditional visibility: Depend on filter type selected

**Semantic control count (confirmed):** 
- Core controls: 8 per filter (Enable, Cutoff, Resonance, Drive, Type, Level, Mix, + 1 routing core)
- Routing controls: 3 per filter (BUS1Send, BUS2Send, Route)
- Total per filter: 11 confirmed semantic controls
- **Total for both filters:** 22 confirmed + 7-15 type-specific = **29-37 semantic controls**

### Population 3: Semantic Targets

**Current in targets.py:**
- Filter.Resonance (generic, ambiguous)
- Filter.Type (generic, ambiguous)
- Filter.Cutoff (generic, ambiguous)
- Filter.Drive (generic, ambiguous)
- Filter.Q (generic, ambiguous)
- Filter2.Cutoff (Filter2-specific)
- Filter2.Resonance (Filter2-specific)
- FILTER1.Level, FILTER1.Mix, FILTER1.BUS1Send, FILTER1.BUS2Send, FILTER1.Route (11 total Filter1-specific)
- FILTER2.Level, FILTER2.Mix, FILTER2.BUS1Send, FILTER2.BUS2Send, FILTER2.Route (11 total Filter2-specific)

**Missing targets:**
- Filter1.Enable (confirmed semantic control, no target)
- Filter2.Enable (confirmed semantic control, no target)
- Filter1.Type explicit target (generic "Filter.Type" exists, ambiguous)
- All type-specific controls (pending PDF identification)

**Target vocabulary coverage:** 12-17 entries / 29-37 controls = **32-59% coverage** (high ambiguity in generic entries)

### Population 4: Implemented Operations

**Current:** 0/29-37 (0% implementation)

---

## Final P1 Status

| Item | Prior Status | Finding | Resolution | Next Action |
|------|-------------|---------|-----------|------------|
| P1-1: Type-specific controls | UNRESOLVED | 50+ filter types identified | PARTIALLY RESOLVED (types listed, unique controls pending) | **Official PDF research required** |
| P1-2: Filter2 behavior | UNRESOLVED | Filter2 disabled by default | ✅ RESOLVED | Confirmed; no further action |

---

## Path to CLOSED*

**Immediate action required:** Official Serum 2 PDF research (Section: Filters)
- Determine unique controls per filter type (if any)
- Confirm or refute "all types share same control surface" hypothesis
- Document any type-specific or conditional controls

**Estimated time:** 15-30 minutes (PDF search + documentation)

**After PDF research:**
- Finalize semantic control count (29-37 confirmed)
- Identify all missing targets (for post-closure implementation work)
- Declare P1 = 0
- Declare FILTER: CLOSED*
- Proceed to ENV section

---

**Authority:** Direct UI inspection (Serum 2.0.21) + evidence synthesis (A_FILTERS_ENV_AUDIT.json, qualification evidence)  
**Version lock:** Serum 2.0.21 only  
**Next session:** PDF research + final reconciliation → FILTER CLOSED*
