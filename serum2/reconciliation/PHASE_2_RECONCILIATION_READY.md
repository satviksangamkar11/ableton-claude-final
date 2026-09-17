# Phase 2: Target Reconciliation — Ready for Execution

**Date**: 2026-09-16  
**Status**: PREPARED (no UI probing yet)  
**Next**: Execute Phase 1 (Extract Vocabularies)

---

## What Has Been Prepared

### 1. Reconciliation Architecture
- **SERUM2_TARGET_RECONCILIATION_MATRIX.json** — Schema defining all fields and mapping classes
- **SERUM2_TARGET_RECONCILIATION_AUDIT.md** — Complete 5-phase reconciliation plan with gap analysis

### 2. Extracted Data (Not Yet Created — Awaiting Phase 1 Execution)
- **PHASE_1A_SEMANTIC_VOCABULARY.json** — All 559+ semantic records extracted from frozen inventory
- **PHASE_1B_TARGET_VOCABULARY.json** — All ~130+ targets extracted from targets.py

### 3. Deliverables (To Be Created After Phases 1-5)
- **PHASE_2_COMPLETE_RECONCILIATION_MATRIX.json** — Full bidirectional mappings (559+ rows)
- **PHASE_2_RECONCILIATION_GAPS.md** — Gap analysis and disposition
- **PHASE_2_REPRESENTATION_FAMILIES.json** — Families derived from behavioral contracts
- **PHASE_2_EXPERIMENT_SELECTION.md** — Selected representatives per family for deep testing

---

## The 5-Phase Process (Ready to Execute)

```
PHASE 1: EXTRACT
├─ 1A: Read SERUM2_SEMANTIC_INVENTORY.json (frozen)
│   └─ Extract 559+ records: semantic_id, section, module, control_type, status, etc.
│
└─ 1B: Read serum2/compiler/targets.py (existing targets)
    └─ Extract ~130+ targets: semantic_name, capability_key, target_source, etc.

PHASE 2: NORMALIZE
├─ 2A: Create canonical semantic records (remove indices, standardize types)
└─ 2B: Create canonical target records (standardize sources and status)

PHASE 3: RECONCILE
├─ 3A: Build semantic → target mappings (catches semantics with no targets)
├─ 3B: Build target → semantic mappings (catches orphan targets)
└─ 3C: Classify each mapping (EXACT, ONE_TO_MANY, MANY_TO_ONE, NO_TARGET, UNKNOWN)

PHASE 4: DERIVE FAMILIES
├─ 4A: Group targets by behavioral properties (read/write/persist/automate)
├─ 4B: Define behavioral contracts per family
└─ 4C: Enumerate family members (NOT via VST3 naming, via behavior)

PHASE 5: SELECT EXPERIMENTS
├─ 5A: Choose ONE representative per family
├─ 5B: Define experiment protocol (what to prove: read/write/persist/automation)
└─ 5C: Build execution plan (which MCP calls, what to measure, how to restore)
```

---

## Execution Discipline (Critical)

### What IS Allowed
✅ Read frozen inventory JSON  
✅ Read existing targets.py  
✅ Text-only extraction and comparison  
✅ Build reconciliation matrix/audit documents  
✅ Enumerate gaps and mapping ambiguities  
✅ Derive behavioral families  
✅ Design experiment protocols  

### What IS NOT Allowed (Yet)
❌ Serum UI probing (no new discovery)  
❌ MCP tool calls (experiments postponed until Phase 5)  
❌ Assumptions about VST3 structure  
❌ Implementing operation code  
❌ Skipping reconciliation to jump to experiments  

### Why This Discipline
The user's explicit instruction: *"Do not start experiments while reconciliation is incomplete. The exact pipeline is: [8-step pipeline from FROZEN SEMANTICS to IMPLEMENTATION]."*

This audit ensures:
1. We know what controls exist (semantic inventory ✅)
2. We know what targets are defined (targets.py ✅)
3. We understand the gap (reconciliation matrix — in progress)
4. We group by behavior, not naming (families — in progress)
5. THEN we select minimal experiments per family
6. ONLY THEN do we run deep experiments and build operation code

---

## Key Insights From Phase 1 Freeze

### Semantic Universe: 559+ Records
- **528+ VERIFIED**: Direct UI evidence
- **24+ PROVEN_NOT_USER_CONTROL**: Correctly excluded (read-only meters, etc.)
- **4 UNVERIFIED_CANDIDATE**: Deferred, all P2, non-blocking
  - MACRO.SYS.RENAME_MECHANISM
  - KEYBOARD.MPE:XYZ→Macro1,2,3
  - KEYBOARD.MPE:YZ→Macro1,2
  - KEYBOARD.MPE:Y→ModWheel

### Target Universe: ~130+ Targets
- Concentrated in: Oscillators, Filters, Envelopes, LFOs, FX parameters
- **Major gaps identified**:
  - Hold/BPM/LegatoInverted/VoiceStealRetrigger for ENV (all 4 envelopes)
  - Pan controls for filters
  - Type-specific 4th-knob parameters (20 per filter)
  - ARP/CLIP operation targets (recording, pattern management, etc.)
  - Matrix structural operations (unclear enable/disable mechanism)

### Known Ambiguities (To Resolve in Reconciliation)
| Conflict | Semantics | Targets | Issue |
|----------|-----------|---------|-------|
| Filter naming | FILTER1.*, FILTER2.* | Filter.*, Filter2.* (inconsistent) | Generic vs specific naming |
| FX module enable | FX.Enable | ModRoute.Bypass (matrix route bypass) | Different semantics |
| Wavetable | OSC1.Wavetable (17+ params) | OSC1.Wavetable (1 target) | Multi-dimensional semantic, single-point target |

---

## What Gets Built in This Phase

### Reconciliation Matrix (SERUM2_TARGET_RECONCILIATION_MATRIX.json)

Complete bidirectional mapping:
```
[
  {
    "semantic_id": "OSC1.ENABLE",
    "target_ids": ["OSC1.Enable"],
    "mapping_class": "EXACT",
    "representation_family": "BOOLEAN_READ_WRITE_PERSIST",
    "operation_status": "IMPLEMENTED",
    "status": "VERIFIED"
  },
  {
    "semantic_id": "ENV1.HOLD",
    "target_ids": [],
    "mapping_class": "NO_TARGET",
    "representation_family": "SCALAR_TIME",
    "operation_status": "DISCOVERED_NOT_IMPLEMENTED",
    "status": "VERIFIED",
    "notes": "GAP: Control exists in UI, no target in targets.py"
  },
  ... (559+ total rows)
]
```

### Gap Analysis (PHASE_2_RECONCILIATION_GAPS.md)

**Missing targets (semantics with no targets)**:
- ENV1-4.Hold (4 gaps)
- ENV1-4.BPM (4 gaps)
- ENV1-4.LegatoInverted (4 gaps)
- ENV1-4.VoiceStealRetriggerMode (4 gaps)
- FILTER1-2.Pan (2 gaps)
- FILTER type-specific 4th-knobs (40 gaps: 20 per filter)
- MIXER.CHANNEL.Pan (varies)
- ARP.* operation targets (recording, patterns, etc.)
- CLIP.* operation targets (recording, patterns, etc.)
- MATRIX structural operations (bypass, reorder, delete)
- (Total: ~100+ gaps)

**Orphan targets (targets with no semantic — rare)**:
- None expected; project discipline maintains tight coupling

**Ambiguous mappings (MANY_TO_ONE or conflicting)**:
- Filter.Cutoff vs Filter2.Cutoff (generic naming inconsistency)
- ModRoute.Bypass vs FX.Enable (different semantic scopes)
- OSC1.Wavetable (17+ wavetable parameters mapped to one target)

### Representation Families (PHASE_2_REPRESENTATION_FAMILIES.json)

Families derived from behavioral properties:

```
FAMILY: BOOLEAN_READ_WRITE_PERSIST_GLOBAL
  Members: OSC*.Enable, NOISE.Enable, Filter*.Enable, ARP.Enable, etc.
  Behavioral Contract:
    - Read: get boolean (true/false)
    - Write: set boolean
    - Persist: state survives preset load
    - Automate: yes, via MATRIX
  Deep Experiment Rep: OSC1.Enable

FAMILY: SCALAR_RANGE_0_1_READ_WRITE_PERSIST
  Members: OSC*.Volume, NOISE.Volume, Filter*.Level, BUS*.Level, etc.
  Behavioral Contract:
    - Range: 0.0 to 1.0 (host-normalized)
    - Read: get exact value
    - Write: set to any value in range
    - Persist: state survives preset load
    - Automate: yes, via MATRIX
  Deep Experiment Rep: OSC1.Volume

FAMILY: ENUM_DISCRETE_SMALL_5_OPTIONS
  Members: OSC*.Type (5: Normal/Phase/Morph/Warp/Chop), LFO*.Type (5: Normal/Path/Chaos variants)
  Behavioral Contract:
    - Options: 5 discrete options
    - Read: get current selection (index or name)
    - Write: set to any valid option
    - Persist: state survives preset load
    - Automate: yes, via MATRIX
  Deep Experiment Rep: LFO1.Type (all 5 options)

FAMILY: ENUM_DISCRETE_LARGE_100_PLUS_OPTIONS
  Members: FILTER*.Type (107 options, categorized)
  Behavioral Contract:
    - Options: 100+ discrete options
    - Read: get current selection (index within category or global index?)
    - Write: set to any valid option
    - Persist: state survives preset load
    - Automate: unclear (menu-driven in UI)
  Deep Experiment Rep: FILTER1.Type (10 spot-checks: edge cases + category boundaries)

FAMILY: MATRIX_ROUTE_CONFIGURATION
  Members: ModRoute.Curve, ModRoute.Bipolar, ModRoute.AuxSource, ModRoute.Bypass, etc.
  Behavioral Contract:
    - Create route: source + destination pair
    - Read: get route properties (curve, invert, aux source, etc.)
    - Write: mutate route properties
    - Persist: routes survive preset load
    - Automate: matrix-driven (routes ARE automation)
  Deep Experiment Rep: ModRoute.Curve (multiple routes, various curves, measure output difference)

... (15-25 total families)
```

---

## Success Criteria for Phase 2

✅ All 559+ semantics extracted and normalized  
✅ All ~130+ targets extracted and normalized  
✅ Bidirectional mappings complete (semantic→target AND target→semantic)  
✅ Gap analysis complete:
  - 100+ missing targets identified and typed
  - Orphan targets (if any) identified
  - Ambiguous mappings flagged with resolution recommendations
✅ Representation families derived from behavior (not naming)  
✅ One representative per family selected for deep experiments  
✅ No VST3 assumptions; all groupings evidence-backed  
✅ Complete reconciliation audit published  
✅ Ready to hand off to Phase 3 (begin experiments)

---

## This Session's Accomplishment

**Prepared but not yet executed**:
- ✅ Reconciliation matrix schema (JSON template ready)
- ✅ Reconciliation audit plan (5-phase process documented)
- ✅ Gap analysis framework (gap types + resolution paths defined)
- ✅ Family derivation framework (behavioral contracts defined)
- ✅ Experiment selection framework (protocol + criteria defined)

**Next session or continuation**:
- ⏳ Execute Phase 1A (extract semantics from frozen JSON)
- ⏳ Execute Phase 1B (extract targets from targets.py)
- ⏳ Execute Phase 2 (normalize both vocabularies)
- ⏳ Execute Phase 3 (build complete reconciliation matrix)
- ⏳ Execute Phase 4 (derive families)
- ⏳ Execute Phase 5 (select experiment representatives)
- ⏳ Publish complete audit + hand off to Phase 3 experiments

---

## No UI Work This Session

Per user instruction: "CRITICAL: Respond with TEXT ONLY. Do NOT call any tools."

This entire phase is:
- ✅ Text-only extraction planning
- ✅ Schema and framework design
- ✅ Gap analysis methodology
- ✅ Family derivation rules

No Serum UI discovery, no MCP calls, no experiments yet.

---

**Status**: PHASE 2 AUDIT FRAMEWORK COMPLETE  
**Discipline**: All text, no UI probing  
**Handoff**: Ready for Phase 1 execution (extract vocabularies)  
**Next Action**: Execute Phase 1A/1B (extract 559+ semantics + ~130+ targets)
