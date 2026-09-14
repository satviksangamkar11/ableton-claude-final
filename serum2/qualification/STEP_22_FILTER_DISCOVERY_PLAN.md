# STEP 22 — FILTER SECTION DISCOVERY & RECONCILIATION PLAN

**Date:** 2026-09-15  
**Status:** RESEARCH PHASE  
**Method:** Complete semantic-target reconciliation per Section-Closure Method  
**Authority:** User's exact FILTER scope prompt (STEP 3 instruction set)

---

## SCOPE & OBJECTIVE

Completely discover and reconcile the entire user-facing FILTER control universe for **FILTER 1** and **FILTER 2**, including:

1. Every controller/parameter (common and type-specific)
2. Every conditional/type-dependent control
3. Hidden/menu controls and structural actions
4. Routing relationships and resource/editor surfaces
5. Cross-system (MIX/MATRIX) interaction points

**Four Population Separation (mandatory throughout):**
- Technical VST3 fields
- User-facing semantic controls
- Semantic targets in targets.py
- Implemented operations

These are NOT interchangeable completion metrics.

---

## EXISTING EVIDENCE INVENTORY

### Qualified FILTER Parameters (from A_FILTERS_ENV_AUDIT.json)

| Family | Discovered | Qualified | Status |
|--------|-----------|-----------|--------|
| Filter1 | 14 | 14 | COMPLETE |
| Filter2 | 12 | 12 | COMPLETE |

### Behavioral Evidence (Causality Verified)

**Filter1.Cutoff:**
- Evidence file: A_FILTER_CUTOFF_REVISED_EVIDENCE.json
- Status: CAUSAL_VERIFIED (single_field isolation)
- Measurement: spectral_centroid_hz delta = +2684 Hz
- Context: Filter 1 On = 1.0

**Filter1.Drive:**
- Evidence file: A_SEED_EXPERIMENT_11_seed_filter1_drive_001_EVIDENCE.json
- Status: [to be reviewed]

**Filter1.Resonance:**
- Evidence file: A_SEED_EXPERIMENT_02_seed_filter1_resonance_001_EVIDENCE.json + DIAG_01
- Status: [to be reviewed]

**Filter2.Cutoff:**
- Evidence file: A_SEED_EXPERIMENT_03_seed_filter2_cutoff_001_EVIDENCE.json
- Status: [to be reviewed]

### Pilot Evidence

- **A_FILTER_CUTOFF_PILOT_EVIDENCE.json** (prior architecture)
- **filter_cutoff_pilot.py** (pilot specification)
- **test_filter2_pilot_mechanism.py** (mechanism validation)

---

## RESEARCH-FIRST EXECUTION ORDER

### Step 1: Official PDF Reconciliation
- [ ] Locate official Serum 2 User Guide PDF (static.xferrecords.com)
- [ ] Search for: "Filter 1", "Filter 2", filter types, filter controls
- [ ] Document: officially listed filter categories/types
- [ ] Document: officially documented common controls
- [ ] Document: any type-specific controls mentioned
- [ ] Document: series/parallel routing mention
- [ ] Conflict flag any PDF vs. existing project evidence disagreement

### Step 2: Project Research Reconciliation
- [ ] Review all A_FILTER*.json qualification records
- [ ] Extract: each parameter name, kParam CBOR path, default, range
- [ ] Extract: any control interdependencies noted in evidence
- [ ] Review: existing targets.py entries for FILTER family
- [ ] Review: existing operations for FILTER family
- [ ] Identify: any technical fields with unknown semantic meaning

### Step 3: Tutorial/Knowledge Reconciliation
- [ ] Search ingested YouTube tutorial transcripts for Filter discussion
- [ ] Extract: user-facing control naming as demonstrated
- [ ] Extract: filter type selection/switching methods
- [ ] Extract: any mode-specific control surface changes
- [ ] Note: conditional controls (e.g., Drive availability by type)

### Step 4: Existing Project Artifact Review
- [ ] Review: tests/test_20b_part4_filter_level_mix.py for context
- [ ] Extract: what control interactions were tested
- [ ] Extract: MIX/FILTER ownership clarifications
- [ ] Note: any bypassed or unresolved controls flagged in tests

### Step 5: Targeted Serum 2.0.21 UI Inspection
- [ ] Open Serum 2 in Ableton Live 12.3
- [ ] For each filter type (Normal, Multi, Flanges, Misc, New):
  - [ ] Document visible controls on FILTER 1
  - [ ] Document visible controls on FILTER 2
  - [ ] Check for type-specific controls (appear only in certain types)
  - [ ] Check for conditional controls (enable state dependent)
  - [ ] Check for hidden/menu controls (gear icon, right-click, etc.)
  - [ ] Check for resource/editor surfaces (graph, pattern editor, etc.)
  - [ ] Screenshot if control surface changes noticeably
- [ ] For each control observed:
  - [ ] Verify name against evidence files
  - [ ] Verify applicability to both filters
  - [ ] Check for ownership ambiguity (FILTER vs. MIX)

### Step 6: Conflict Resolution
- [ ] Reconcile: official PDF vs. project evidence vs. UI observation
- [ ] For each disagreement:
  - [ ] Record both sources and conflict
  - [ ] Determine which is authoritative (prefer: PDF > project > UI > inference)
  - [ ] Document resolution

---

## FILTER CONTROL CLASSIFICATION FRAMEWORK

### Common Controls (Expected on both FILTER 1 and FILTER 2)

Based on user's prompt and existing evidence, check these:

- **Enable** — Filter on/off toggle
- **Mute** — Filter output mute (if exists)
- **Filter Type/Category** — Normal, Multi, Flanges, Misc, New (if user-selectable)
- **Cutoff** — Main filter frequency control
- **Resonance** — Peak/Q around cutoff
- **Drive** — Saturation/distortion within filter
- **Drive/Clean Mode** — Drive behavior toggle (if conditional)
- **FAT** — Filter saturation amount (if exists)
- **Pan** — Filter output pan (if owned by FILTER; else MIX)
- **Mix** — Dry/wet blend (if owned by FILTER; else MIX)
- **Level** — Filter output level (if owned by FILTER; else MIX)
- **Key Track** — Keyboard pitch tracking for cutoff
- **Routing Indicators** — Series/Parallel mode indicator
- **Graph/Display** — Visual filter curve/response
- **Editor/Pattern Editor** — Draw-able filter curve (if exists)

### Type-Specific Controls

For every filter type, check:

- **Normal** → Are there type-specific knobs? (expect: none, inherited from common)
- **Multi** → Does multiband show per-band controls? (cutoff1, cutoff2, res1, res2, etc.)
- **Flanges** → Does it show flange-specific controls? (rate, depth, feedback, phase?)
- **Misc** → Does it show misc-type controls? (vary by subtype)
- **New** → Are there any newly-added types with unique surfaces?

### Structural/UI Controls

- **Enable/Disable** — Toggle filter active state
- **Type Switching** — UI method to change filter type
- **Initialize** — Reset filter to default state
- **Copy/Paste** — Copy filter settings to another filter
- **Lock** — Lock filter parameters (prevent changes)
- **Context Menus** — Right-click behavior
- **Gear/Settings** — Settings menu or hidden parameters
- **Hidden/Expanded Controls** — Any controls revealed by clicking a gear/arrow
- **Series/Parallel** — Routing topology selector (between Filter 1 and 2)
- **Pattern Editor** — If filter has drawn curve interface

### Conditional Control Testing

For each control found, explicitly test:

```
filter_enabled_state (ON / OFF)
  → does control appear/disappear?
  → does control meaning change?

filter_type (Normal / Multi / Flanges / Misc / New / Subtype)
  → does control appear/disappear?
  → does control have different range/label?
```

### Ownership Reconciliation

For every control identified, classify as EXACTLY ONE of:

- **FILTER-Owned Semantic Control** — directly controls Filter 1/2 sound
- **MIX-Owned Routing Control** — directs signal path (series/parallel, mute)
- **Shared UI Surface** — same control appears in multiple UI locations but is single semantic control
- **Technical Representation Only** — VST3 parameter with no direct user-facing control

---

## TECHNICAL FIELD RECONCILIATION

For every VST3 parameter in A_FILTERS_ENV_AUDIT.json and related evidence files:

```
technical_field
  → official meaning (from kParam name or code comment)
  → UI control (which knob/switch does it map to?)
  → semantic_id (e.g., Filter1.Cutoff)
  → applicable_filter(s) (FILTER1? FILTER2? both?)
  → applicable_type(s) (all types or conditional?)
  → classification (must be exactly one):
     - MAPPED_TO_SEMANTIC_CONTROL
     - DUPLICATE_OF_EXISTING_SEMANTIC_CONTROL
     - TECHNICAL_STRUCTURAL_FIELD
     - PROVEN_NOT_USER_CONTROL
     - UNRESOLVED
```

Do NOT classify as semantic control merely because a VST3 parameter exists.

---

## FOUR INDEPENDENT COVERAGE DIMENSIONS

Maintain separate counts for:

### Dimension 1: FILTER Semantic Controls
- Count: distinct user-facing controls (one per semantic identity, regardless of UI locations)
- Examples: Filter1.Cutoff, Filter1.Enable, Filter1.DriveMode, etc.
- Status: discovered vs. verified vs. gaps

### Dimension 2: FILTER Technical Fields
- Count: VST3 parameters in evidence (might not all map to UI)
- Status: mapped to semantic control? duplicate? technical-only? unresolved?

### Dimension 3: FILTER Semantic Targets
- Count: entries in targets.py for FILTER family (e.g., "Filter1.Cutoff" → "filter_field_freq1")
- Status: exists for all semantic controls? gaps? duplicates?

### Dimension 4: FILTER Operations
- Count: compiled operations that can execute FILTER control changes
- Status: implemented for all semantic controls? gaps?

Plus separately track evidence:

### Evidence Coverage (Independent of the above)
- Semantic evidence (PDF, UI observation, control naming)
- Behavioral evidence (CAUSAL_VERIFIED measurements)
- Persistence evidence (control values persist in presets)
- Implementation evidence (targets.py, operations/*, code)

Never combine these into one "% complete" number.

---

## CRITICAL DISTINCTION: MIX vs. FILTER OWNERSHIP

**FILTER-Owned Controls** (stay in FILTER section):
- Filter1.Enable, Filter1.Cutoff, Filter1.Resonance, Filter1.Drive, etc.
- Any control that directly changes the filter's sound

**MIX-Owned Controls** (belong in MIX section):
- Filter1.Level, Filter1.Pan (if owned by MIX)
- Filter1.SeriesParallel (if it's a routing destination selector)
- Filter1.Mute (if it's a channel mute, not a filter-internal bypass)

**Boundary Controls** (explicit classification needed):
- FAT (is it filter-owned distortion, or MIX bus saturation?)
- Mix (dry/wet: is it FILTER-owned blend, or MIX-owned send level?)
- Key Track (if it's global FILTER tracking, FILTER-owned; if per-filter routing, MATRIX-owned)

Do not duplicate one semantic control merely because it appears in multiple UI locations.

---

## SECTION-CLOSURE RULE

**MUST resolve before closure:**

- P0 = 0 (all semantic controls identified)
- P1 = 0 (all discovery gaps resolved)

**MAY defer (at most one genuinely non-blocking):**

- P2 = 0 or 1 (narrow, non-blocking, full context captured)

**P2 is NOT allowed if it could change:**

- Control count
- Control ownership
- Filter type universe
- Conditional UI
- Structural topology
- Resource workflow
- Cross-system semantics

---

## EXPECTED OUTCOMES

### Semantic Control Count (Preliminary Estimate)

Based on A_FILTERS_ENV_AUDIT.json:
- Filter 1: 14 parameters → expected 10-12 semantic controls (some might be technical-only)
- Filter 2: 12 parameters → expected 9-11 semantic controls
- Shared controls (series/parallel, etc.): 1-3

**Preliminary total: 20-26 distinct semantic controls**

(Will be revised after Step 1-2 research.)

### Target Vocabulary Gaps (Expected)

Review targets.py; likely findings:
- Most common controls have targets (Enable, Cutoff, Resonance, Drive)
- Some type-specific controls may lack targets
- Filter2-specific controls may have fewer targets than Filter1

### Operation Gaps (Expected)

Likely findings:
- Basic operations exist for Filter1 (from past qualification)
- Filter2 operations may be incomplete
- Type-switching may be unimplemented

---

## FINAL FILTER REPORT CONTENTS

Before declaring FILTER closed, report:

```
Total FILTER semantic controls: N
Total FILTER technical fields: M
Filter1 exclusive controls: X
Filter2 exclusive controls: Y
Shared controls (both filters): Z
Type-specific controls: A
Conditional controls (enable/type-dependent): B
Structural actions (series/parallel, initialize, copy): C
Hidden/menu controls: D
Resource/editor controls (graph, pattern editor): E
Cross-system controls (MIX ownership, MATRIX targets): F

Semantic target coverage: N_targets / N_controls = X%
Operation coverage: N_ops / N_controls = Y%

NEW controls discovered: [list]
CONTROLS merged/reclassified: [list]
CONTROLS re-attributed (ownership change): [list]
TECHNICAL fields proven non-user-facing: [list]
CONTROLS requiring later behavioral qualification: [list]

P0 gaps: [list or "none"]
P1 gaps: [list or "none"]
P2 deferred: [one item + full context, or "none"]

Authority: SERUM2_SEMANTIC_INVENTORY.json meta.filter_closure_ledger
Next section: ENV (Environmental Controls)
```

---

## NO PREMATURE CLOSURE

Do not declare FILTER closed until:
1. All research phases complete (Steps 1-5)
2. All conflicts resolved (Step 6)
3. All four populations separated and reconciled
4. P0 and P1 gaps resolved or properly classified
5. Final report completed and committed

---

Generated: 2026-09-15  
Next step: Begin STEP 1 (Official PDF Reconciliation)
