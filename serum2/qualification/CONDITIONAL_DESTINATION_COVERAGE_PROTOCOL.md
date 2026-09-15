# MATRIX Conditional Destination Coverage Protocol

**Status:** CRITICAL DISCOVERY VERIFIED  
**Date:** 2026-09-15 (Session Continuation, Phase 2A-Extended)  
**Authority:** Direct Serum UI mode-switching verification

---

## DISCOVERY: Matrix Destination Coverage Is MODE-DEPENDENT

### Verified Conditional Difference

**OSC A (Same Oscillator, Different Modes):**

| Mode | Parameter Count | Feature Set | Evidence |
|------|-----------------|-------------|----------|
| Wavetable | 23 | Wavetable synthesis controls (WT Pos, Phase, etc.) | VERIFIED |
| Spectral | 38+ | Sampling + spectral features (Start/End, Scan Rate, Freq Lo/Hi, etc.) | VERIFIED |

**Critical Implication:**
- The original "OSC A=38 vs OSC B=23" difference was **NOT** due to permanent oscillator architecture difference
- It was due to **synthesis mode difference** (Spectral vs Wavetable)
- **Matrix destination universe is conditional on module state** (mode, settings, context)

### Lesson from Filter Audit
> "Never infer from family-level similarity"

### New Lesson from OSC Testing  
> "Never infer a destination universe from one module's current state"

The Matrix destination list can itself be **state-dependent**, especially for mode-driven modules.

---

## Complete Testing Protocol (OSC A/B/C)

### For Each OSC (A, B, C):

**Step 1: Determine Available Modes**
```
Click OSC X mode dropdown
Record ALL modes supported by that OSC
Note: Not all modes may be supported (e.g., OSC B/C may be locked to Wavetable)
```

**Step 2: For Each Supported Mode:**
```
1. Switch OSC to that mode
2. Navigate: MATRIX → DESTINATION → OSC X
3. Expand OSC X submenu
4. Scroll to END (verify completeness)
5. Record EXACT parameter count
6. Record EXACT parameter list (copy labels from UI)
7. Screenshot final view (proof of completion)
8. Note any mode-specific parameters (only appear in this mode)
```

**Step 3: Build Conditional Destination Table**
```
OSC A
├── Wavetable → 23 params [exact list]
├── Multisample → ? params [exact list]
├── Sample → ? params [exact list]
├── Granular → ? params [exact list]
└── Spectral → 38+ params [exact list]

(repeat for OSC B, OSC C)
```

**Step 4: Cross-Compare**
```
For each OSC:
  - Are parameter sets identical across all modes? (unlikely)
  - Do some modes share parameter subsets? (likely)
  - Are there mode-exclusive parameters?
  - Do counts change based on mode? (already proven for OSC A)
```

---

## Current Evidence State

### Verified
- ✅ OSC A exists and supports 5 synthesis modes (Wavetable, Multisample, Sample, Granular, Spectral)
- ✅ OSC A (Wavetable mode) → 23 Matrix destinations
- ✅ OSC A (Spectral mode) → 38+ Matrix destinations (includes sampling + spectral features)
- ✅ OSC B (Wavetable mode, same as OSC C) → 23 Matrix destinations
- ✅ OSC C (Wavetable mode, same as OSC B) → 23 Matrix destinations

### Unverified (Next Session Testing)
- ❓ OSC A (Multisample mode) → ? destinations
- ❓ OSC A (Sample mode) → ? destinations
- ❓ OSC A (Granular mode) → ? destinations
- ❓ OSC B mode flexibility (locked to Wavetable? or multi-mode?)
- ❓ OSC C mode flexibility (locked to Wavetable? or multi-mode?)
- ❓ Do OSC B/C change destination count when mode switched (if supported)?

### Remaining Destination Families (8 unchanged)
- Noise OSC (unknown if mode-conditional)
- SUB OSC (unknown if mode-conditional)
- Macros
- LFO Busses
- Routing Matrix
- Clip Player
- Arpeggiator
- Retriggers

---

## Exact Next Session Execution (Phase 2A-Extended)

### Part 1: Complete OSC A/B/C Conditional Testing (Priority)

```
FOR OSC A:
  1. Test Multisample mode → record destinations
  2. Test Sample mode → record destinations
  3. Test Granular mode → record destinations
  (already done: Spectral=38+, Wavetable=23)

FOR OSC B:
  1. Determine if multi-mode or locked to Wavetable
  2. If multi-mode, test each supported mode
  3. If locked to Wavetable, verify and document

FOR OSC C:
  1. Determine if multi-mode or locked to Wavetable
  2. If multi-mode, test each supported mode
  3. If locked to Wavetable, verify and document
```

### Part 2: Build Conditional Destination Table

```
Create MATRIX_OSC_CONDITIONAL_DESTINATIONS.md:

OSC A
├── Wavetable (23 params) — VERIFIED
│   Level, Pan, Octave, Semi, Fine, Coarse Pitch, Ratio, Hz Offset,
│   Uni Detune, Uni Blend, Uni Width, Uni Range, Uni Rotate, Uni Warp, Uni Warp 2,
│   Warp, Warp Var, Warp 2, Warp 2 Var, WT Pos, Uni WT Pos, Phase, Rand Phase
│
├── Spectral (38 params) — VERIFIED
│   Level, Pan, Octave, Semi, Fine, Coarse Pitch, Ratio, Hz Offset,
│   Start, End, Reverse, Scan Rate, Scan BPM Rate, Position,
│   Loop Start, Loop End, Loop X-Fade, Loop Mode, Relative Loop,
│   Slice Play Mode, Single Slice,
│   Uni Detune, Uni Blend, Uni Width, Uni Range, Uni Rotate, Uni Span, Uni Rand Start, Uni Warp, Uni Warp 2,
│   Warp, Warp Var, Warp 2, Warp 2 Var,
│   Spec Fit Cutoff, Spec Fit Wet/Dry, Freq Lo, Freq Hi
│
├── Multisample (? params) — TESTING NEEDED
├── Sample (? params) — TESTING NEEDED
└── Granular (? params) — TESTING NEEDED

(repeat for OSC B, OSC C)
```

### Part 3: Complete Remaining 8 Families

Only after OSC conditional testing is complete, enumerate remaining families (unchanged protocol):
```
Noise OSC, SUB OSC, Macros, LFO Busses, Routing Matrix, 
Clip Player, Arpeggiator, Retriggers
```

### Part 4: Route Mechanics (if tokens permit)

---

## Key Accounting Corrections

**Fixed Destination Universe:**
- Top-level: 16 entries (Off + 15 families)
- Verified: 7 categories (7 families)
- Remaining: 8 families + OSC conditional testing

**Previous Error:**
- "42% complete" was based on wrong denominator
- Correct accounting: 7/15 = 47%, but OSC A/B/C now require conditional sub-testing

---

## Documentation Standard

For each mode tested:
```
OSC X / Mode
├── Parameter Count: N
├── Parameter List: [exact labels from UI]
├── Feature Set: [synthesis engine features]
├── Screenshot: [proof of completion]
├── Conditional State: [what triggers this mode's availability?]
└── Difference from other OSC X modes: [what's unique?]
```

Never use:
- "similar to"
- "likely"
- "expected"
- "parity with"
- Approximations ("23+")

Only use evidence from direct UI testing.

---

## Why This Matters

The **three-population separation** discipline requires:
1. **Semantic controls** (what exists in UI) 
2. **Matrix destination coverage** (what can be routed)
3. **Compiler/operation coverage** (implementation details)

Adding a fourth dimension:
4. **Conditional applicability** (when/how destination is available)

Without capturing conditions, the final inventory will be incomplete and misleading.

Example:
```
INCOMPLETE: "OSC A has 38 destinations"
COMPLETE: "OSC A in Spectral mode has 38 destinations; in Wavetable mode has 23"
```

---

## Token Budget Note

Estimated work remaining:
- OSC A/B/C conditional testing: ~3-4K tokens
- Remaining 8 families enumeration: ~5-6K tokens  
- Route mechanics: ~3-4K tokens
- Documentation/closure: ~2-3K tokens

Current budget: ~14.9M remaining (no constraint)

Recommend committing this protocol before continuation to preserve exact test order and avoid re-discovery.

---

**Generated:** 2026-09-15  
**Authority:** Direct Serum UI verification of OSC A mode-conditional destination differences  
**Next Action:** Test OSC A (Multisample, Sample, Granular); verify OSC B/C mode support; complete 8 remaining families
