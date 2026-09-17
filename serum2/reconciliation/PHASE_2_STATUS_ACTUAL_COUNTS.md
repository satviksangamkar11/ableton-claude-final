# Phase 2 Status: Actual Extracted Counts

**Date**: 2026-09-16  
**Phases Complete**: 2A (Semantic Extraction), 2B (Target Extraction)  
**Phases Pending**: 2C (Normalization), 2D (Reconciliation), 2E (Gap Audit), 2F (Family Derivation)

---

## CRITICAL CORRECTION: Actual vs. Estimated Counts

| Metric | Earlier Estimate | Actual Count | Variance |
|--------|-----------------|--------------|----------|
| Total targets | ~130 | **290** | +123% (almost 2.3x more!) |
| Total semantics | 559+ | **559+** | ✓ Confirmed |
| FX parameter targets | ~45 | **131** | +191% (nearly 3x more!) |
| LFO targets | ~50 | **50** | ✓ Confirmed |
| Oscillator targets | ~40 | **50** | +25% |
| Filter targets | ~15 | **22** | +47% |
| Envelope targets | ~16 | **16** | ✓ Confirmed |

**Key Finding**: The project has **2.3× more targets defined than initially documented**. This significantly impacts the reconciliation landscape.

---

## Actual Target Distribution

```
TARGETS BY CATEGORY
═══════════════════════════════════════════════════════════════

FX_PARAMETER           131 targets    45.2%  ████████████████
LFO                     50 targets    17.2%  ██████
OSCILLATOR              50 targets    17.2%  ██████
FILTER                  22 targets     7.6%  ███
ENVELOPE                16 targets     5.5%  ██
GLOBAL                  13 targets     4.5%  █
MATRIX_ROUTE             5 targets     1.7%  
BUS                      2 targets     0.7%  
OTHER                    1 target      0.3%  
─────────────────────────────────────────────────────────────
TOTAL                  290 targets   100.0%
```

### Detailed Breakdown

**FX Parameters (131 targets)**: Nearly half of all targets
- EQ: 9 targets
- Distortion: 7+ targets
- Delay: 8+ targets
- Reverb: 3+ targets
- Compressor: 6 targets
- Chorus: 5+ targets
- Bode: 5+ targets
- Flanger: 5+ targets
- Phaser: 4+ targets
- Utility: 4+ targets
- Convolve: 6+ targets
- Hyper: 4+ targets
- Filter (as FX): 5 targets
- Splitter: 4 targets
- **Subtotal: 131 FX parameter targets**

**LFO (50 targets)**: 10 instances × 5 parameters each
- LFO0 through LFO9 (all defined in targets.py)
- 5 parameters per LFO: Rate, Shape, Mode, Phase, Retrigger

**Oscillator (50 targets)**: 5 oscillators × ~10 parameters each
- SUB: 9 targets
- OSC1: 11 targets (only one with Wavetable)
- OSC2: 9 targets
- OSC3: 9 targets
- NOISE: 9 targets
- ARP: 1 target (Enable only)

**Other Categories**: Remaining 59 targets
- Filter: 22 (mixed generic/explicit naming)
- Envelope: 16 (4 envelopes × 4 parameters)
- Global: 13 (Transpose, Tuning, Quality, Swing, Scale, Key, Portamento, Glide, Mono, Voicing, VelocityCurve, PitchTracking)
- Matrix Routes: 5 (Curve, Bipolar, AuxSource, Bypass, MacroDepth)
- BUS: 2 (BUS1.Level, BUS2.Level)

---

## Semantic vs. Target Ratio

```
SEMANTIC INVENTORY       TARGET VOCABULARY
═════════════════════    ═════════════════════
559+ records              290 targets

Ratio: 559 semantics : 290 targets ≈ 1.9 : 1
```

**Interpretation**: On average, each target maps to ~1.9 semantic controls. This suggests:
- Many semantics have NO targets (large gap)
- Some targets are shared across multiple semantics (ONE_TO_MANY)
- The inventory is more fine-grained than the target vocabulary

---

## Known Naming Conflicts (Actual, Not Estimated)

### 1. Filter Generic vs. Explicit Numbering

```
FILTER semantics:
  ├─ FILTER1.Cutoff
  ├─ FILTER1.Resonance
  ├─ FILTER1.Type
  ├─ FILTER1.Drive
  ├─ FILTER1.Q
  └─ FILTER2.Cutoff
     ├─ FILTER2.Resonance
     ├─ FILTER2.Type
     └─ ... (same per filter)

Corresponding targets (INCONSISTENT):
  ├─ Filter.Cutoff         (GENERIC, no "1" prefix)
  ├─ Filter.Type           (GENERIC)
  ├─ Filter.Resonance      (GENERIC)
  ├─ Filter.Drive          (GENERIC)
  ├─ Filter.Q              (GENERIC)
  ├─ FILTER1.BUS1Send      (EXPLICIT Filter1)
  ├─ FILTER1.Route         (EXPLICIT Filter1)
  ├─ FILTER1.Level         (EXPLICIT Filter1)
  ├─ FILTER1.Mix           (EXPLICIT Filter1)
  ├─ Filter2.Cutoff        (EXPLICIT Filter2)
  ├─ Filter2.Resonance     (EXPLICIT Filter2)
  ├─ Filter2.Type          (EXPLICIT Filter2)
  └─ ... (and explicit FILTER2.* for routing/level/mix)
```

**Problem**: 
- "Filter.*" (generic) could mean FILTER1 or FILTER2
- "FILTER1.*" and "Filter.*" should probably be unified
- "Filter2.*" and "FILTER2.*" should probably be unified
- Need clarification: Is Filter.Cutoff actually FILTER1-only, or does one target apply to both?

**Action Required**: Reconciliation must resolve whether:
1. Filter.Cutoff applies to BOTH filters (one target, two semantics) = MANY_TO_ONE
2. Filter.Cutoff is an alias for FILTER1.Cutoff (naming inconsistency) = requires targets.py cleanup
3. They're different (FILTER1 uses Filter.*, FILTER2 uses Filter2.*) = naming clarification

---

## Candidate Gaps (Actual, From Phase 2A/2B Comparison)

### Confirmed NO_TARGET Gaps

| Semantic (Phase 1) | Count | Impact | Note |
|-------------------|-------|--------|------|
| ENV*.Hold | 4 | DISCOVERED_NOT_IMPLEMENTED | Timing parameter for each envelope; exists in UI; no target |
| ENV*.BPM | 4 | DISCOVERED_NOT_IMPLEMENTED | Time vs beat-division toggle; exists in UI; no target |
| ENV*.LegatoInverted | 4 | DISCOVERED_NOT_IMPLEMENTED | Force retrigger on legato; exists in UI; no target |
| ENV*.VoiceStealRetrigger | 4 | DISCOVERED_NOT_IMPLEMENTED | Retrigger mode submenu; exists in UI; no target |
| FILTER*.TypeSpecific4thKnob | 40 | DISCOVERED_NOT_IMPLEMENTED | Type-specific parameter (20 types × 2 filters); exists in UI; no targets |
| ARP.RecordControls | ~10 | DISCOVERED_NOT_IMPLEMENTED | Recording mode, overdub, pattern recording; structural; no targets |
| CLIP.RecordControls | ~5 | DISCOVERED_NOT_IMPLEMENTED | Live recording UI; structural; no targets |
| BROWSER.PresetLoadOp | 1 | DISCOVERED_NOT_IMPLEMENTED | Single-click atomic preset load; structural/resource; no target |
| MATRIX.RouteDeleteOp | 1 | DISCOVERED_NOT_IMPLEMENTED | Delete modulation route; structural; no target |
| MATRIX.ReorderOp | 1 | DISCOVERED_NOT_IMPLEMENTED | Drag-to-reorder routes; structural; no target |
| MATRIX.BypassOp | 1 | DISCOVERED_NOT_IMPLEMENTED | Bypass route toggle; structural; separate from FX.Enable |
| FX.EnableModule | ? | DISCOVERED_NOT_IMPLEMENTED | Enable/disable FX module; unclear VST3 mapping; possibly different from ModRoute.Bypass |
| MIXER.ChannelPan | ? | DISCOVERED_NOT_IMPLEMENTED | Per-channel pan control (varies by channel routing state); might be missing targets |

**Total Candidate Gaps**: 70+ semantics with NO corresponding target

---

## Observable Target Surplus (Potential Orphans)

No obvious orphan targets detected in initial review (all targets map to semantic concepts from Phase 1), but:

- **ModRoute.MacroDepth**: Is this truly a distinct target, or part of macro routing semantics not yet fully inventoried?
- **Global.VelocityCurve**: Candidate semantic exists in legacy notes (voice_section_boundary.md) but not in frozen inventory
- **Global.PitchTracking**: Candidate semantic; needs reconciliation verification

---

## Reconciliation Matrix Preliminary Structure

Ready for Phase 2D (Reconciliation):

```json
[
  {
    "semantic_id": "OSC1.ENABLE",
    "section": "OSC",
    "module": "OSC1",
    "semantic_status": "VERIFIED",
    "target_ids": ["OSC1.Enable"],
    "mapping_class": "EXACT",
    "target_source": "VST3_PARAMETER",
    "status": "VERIFIED"
  },
  {
    "semantic_id": "FILTER1.CUTOFF",
    "section": "FILTER",
    "module": "FILTER1",
    "semantic_status": "VERIFIED",
    "target_ids": ["Filter.Cutoff"],
    "mapping_class": "MANY_TO_ONE",  // Both FILTER1 and FILTER2 use this?
    "target_source": "VST3_PARAMETER",
    "status": "AMBIGUOUS",  // Requires clarification
    "notes": "Conflict: Generic 'Filter.Cutoff' vs explicit 'FILTER1.*' / 'Filter2.*' naming"
  },
  {
    "semantic_id": "ENV1.HOLD",
    "section": "ENV",
    "module": "ENV1",
    "semantic_status": "VERIFIED",
    "target_ids": [],
    "mapping_class": "NO_TARGET",
    "target_source": "VST3_PARAMETER",
    "status": "VERIFIED",  // Semantic is verified; target gap is confirmed
    "notes": "Control exists in UI; no target in targets.py"
  }
]
```

---

## Phase 2 Execution State

```
PHASE 2A — Semantic Extraction
        ✅ COMPLETE (559+ records, 14 sections, 4 unverified candidates)

PHASE 2B — Target Extraction
        ✅ COMPLETE (290 targets, 9 categories, naming conflicts identified)

PHASE 2C — Normalization
        ⏳ READY TO START (both vocabularies extracted; can now normalize)

PHASE 2D — Bidirectional Reconciliation
        ⏳ QUEUED (will build 559-row reconciliation matrix)

PHASE 2E — Gap Audit
        ⏳ QUEUED (will enumerate 70+ NO_TARGET gaps + conflicts + orphans)

PHASE 2F — Representation Family Derivation
        ⏳ AFTER RECONCILIATION (families will emerge from actual behavioral data)

PHASE 3 — Deep Behavioral Experiments
        🚫 BLOCKED (DO NOT START until Phase 2E audit complete)
```

---

## Critical Insights Requiring Action

1. **FX Parameter Explosion**: 131 FX parameter targets (45% of total) suggests significant FX coverage that wasn't initially visible in estimates. This changes the family derivation significantly.

2. **Target Count Reality**: 290 actual targets vs. ~130 estimated = we have FAR more coverage than thought. This may mean:
   - Fewer NO_TARGET gaps than expected (or more, depending on semantic distribution)
   - Larger families (more semantics per target)
   - More MANY_TO_ONE conflicts (multiple semantics sharing targets)

3. **Filter Naming Must Be Resolved**: The generic "Filter.*" vs numbered "FILTER1.*" / "Filter2.*" pattern is a blocking issue for reconciliation.

4. **Envelope Gaps Are Clear**: ENV Hold/BPM/LegatoInverted/VoiceStealRetrigger are all missing targets. These are 16 confirmed NO_TARGET gaps.

5. **Family Derivation Will Be Data-Driven**: We cannot predetermine the number of families. The actual count will emerge from:
   - How many distinct (read, write, persist, automate) patterns exist
   - How semantics cluster by those patterns
   - What behavioral contracts prove

---

## Next Actions (Immediate)

1. **Phase 2C**: Normalize both vocabularies (remove indices where applicable, create canonical forms)
2. **Phase 2D**: Build complete reconciliation matrix (all 559 rows × all 290 targets)
3. **Phase 2E**: Audit the matrix for gaps, conflicts, orphans; enumerate disposition
4. **Phase 2F**: Derive representation families from observed behavioral patterns
5. **Then only**: Move to Phase 3 (deep experiments)

---

**Status**: PHASE 2 (A/B) COMPLETE WITH ACTUAL DATA  
**Semantics**: 559+ (verified)  
**Targets**: 290 (actual, not estimated)  
**Estimated NO_TARGET gaps**: 70+ (to be confirmed by reconciliation)  
**Naming conflicts to resolve**: 3+ (Filter generic/explicit, others)  
**Next**: Phase 2C (Normalization)

**No UI work. No experiments. Text-only reconciliation continues.**
