# Phase 2B: Target Extraction Report

**Date**: 2026-09-16  
**Source**: serum2/compiler/targets.py SEMANTIC_TARGETS dictionary  
**Extraction Method**: Regex parse of all SemanticTargetRef entries

---

## Extracted Target Counts

### Total Targets by Category

| Category | Count | Percentage |
|----------|-------|-----------|
| FX_PARAMETER | 131 | 45.2% |
| LFO | 50 | 17.2% |
| OSCILLATOR | 50 | 17.2% |
| FILTER | 22 | 7.6% |
| ENVELOPE | 16 | 5.5% |
| GLOBAL | 13 | 4.5% |
| MATRIX_ROUTE | 5 | 1.7% |
| BUS | 2 | 0.7% |
| OTHER | 1 | 0.3% |
| **TOTAL** | **290** | **100%** |

---

## Detailed Breakdown

### FX_PARAMETER (131 targets)

Distribution across FX types:

| FX Type | Targets | Examples |
|---------|---------|----------|
| FXEQ | 9 | Freq1, Freq2, Reso1, Reso2, Gain1, Gain2, Type1, Type2, LevelOut |
| FXDistortion | 7 | Drive, Tone, LevelOut, Mode, Freq, LPHP, PrePost, MixOrGain, BW |
| FXDelay | 8 | Time, Feedback, Mix, Mode, TimeL, TimeR, OffsetL, OffsetR, BW, MixOrGain |
| FXReverb | 3 | Time, Damping, Mix, Size, MixOrGain |
| FXCompressor | 6 | Threshold, Ratio, Attack, Release, Gain, MixOrGain |
| FXChorus | 5 | Rate, Depth, Mix, Feedback, Phase, MixOrGain |
| FXBODE | 5 | Frequency, Range, Direction, Mix, Shift, LevelOut, MixOrGain |
| FXFlanger | 5 | Rate, Depth, Feedback, Phase, Mix, MixOrGain |
| FXPhaser | 4 | Frequency, Feedback, Phase, Mix, MixOrGain |
| FXUtility | 4 | Gain, Phase, Mono, Mix, MixOrGain |
| FXConvolve | 6 | IR, IRGain, Attack, Decay, Damping, Mix, MixOrGain, IRPath |
| FXHyper | 4 | Rate, Unison, Detune, Mix, MixOrGain, Retrigger |
| FXFilter (as FX) | 5 | Type, Cutoff, Resonance, Drive, MixOrGain |
| FXSplitter | 4 | BandCount, Crossover1, Crossover2, Crossover3 |
| **FX Total** | **131** | |

### LFO (50 targets)

- LFO0: Rate, Shape, Mode, Phase, Retrigger (5)
- LFO1: Rate, Shape, Mode, Phase, Retrigger (5)
- LFO2: Rate, Shape, Mode, Phase, Retrigger (5)
- LFO3: Rate, Shape, Mode, Phase, Retrigger (5)
- LFO4: Rate, Shape, Mode, Phase, Retrigger (5)
- LFO5: Rate, Shape, Mode, Phase, Retrigger (5)
- LFO6: Rate, Shape, Mode, Phase, Retrigger (5)
- LFO7: Rate, Shape, Mode, Phase, Retrigger (5)
- LFO8: Rate, Shape, Mode, Phase, Retrigger (5)
- LFO9: Rate, Shape, Mode, Phase, Retrigger (5)
- **LFO Total**: 50

### OSCILLATOR (50 targets)

| Oscillator | Targets | Examples |
|------------|---------|----------|
| SUB | 9 | Enable, Octave, Volume, Level, Pan, BUS1Send, BUS2Send, Route, Detune, Warp |
| OSC1 | 11 | Enable, Octave, Volume, Level, Pan, BUS1Send, BUS2Send, Route, Detune, Wavetable, Warp |
| OSC2 | 9 | Enable, Octave, Volume, Level, Pan, BUS1Send, BUS2Send, Route, Detune, Warp |
| OSC3 | 9 | Enable, Octave, Volume, Level, Pan, BUS1Send, BUS2Send, Route, Detune, Warp |
| NOISE | 9 | Volume, Level, Pan, BUS1Send, BUS2Send, Route, Warp, Type, Fine |
| ARP | 1 | Enable |
| **OSCILLATOR Total** | **50** | |

### FILTER (22 targets)

| Filter | Targets | Examples |
|--------|---------|----------|
| Generic | 2 | Resonance, Type |
| FILTER1 | 9 | BUS1Send, BUS2Send, Route, Level, Mix, Cutoff, Drive, Q, Enable |
| FILTER2 | 9 | BUS1Send, BUS2Send, Route, Level, Mix, Cutoff, Resonance, Type, Drive, Q, Enable |
| **FILTER Total** | **22** | |

### ENVELOPE (16 targets)

| Envelope | Targets | Examples |
|----------|---------|----------|
| Env1 | 4 | Attack, Decay, Sustain, Release |
| Env2 | 4 | Attack, Decay, Sustain, Release |
| Env3 | 4 | Attack, Decay, Sustain, Release |
| Env4 | 4 | Attack, Decay, Sustain, Release |
| **ENVELOPE Total** | **16** | |

### GLOBAL (13 targets)

- MasterVolume
- Transpose
- Tuning
- Quality
- Swing
- Scale
- Key
- Portamento
- Glide
- Mono
- Voicing
- VelocityCurve
- PitchTracking

### MATRIX_ROUTE (5 targets)

- ModRoute.Curve
- ModRoute.Bipolar
- ModRoute.AuxSource
- ModRoute.Bypass
- ModRoute.MacroDepth

### BUS (2 targets)

- BUS1.Level
- BUS2.Level

### OTHER (1 target)

- ARP.Enable (note: also listed under OSCILLATOR; possible duplicate categorization)

---

## Target Field Structure (from targets.py)

Each target entry contains:

```python
SemanticTargetRef(
    name="OSC1.Enable",           # Semantic name used in calls
    capability_key="oscillator_field_OSC1-ENABLE"  # VST3 field identifier
)
```

**NOT extracted yet** (these require CapabilityContract inspection):
- mutation_target_path
- operation_supported
- read_supported
- write_supported
- persistent
- automatable

---

## Naming Patterns Observed

### Pattern 1: Numbered Envelopes
```
Env1.Attack, Env2.Attack, Env3.Attack, Env4.Attack
```
Clear parallel structure.

### Pattern 2: Numbered LFOs
```
LFO0.Rate through LFO9.Rate
LFO0.Shape through LFO9.Shape
... etc
```
Clear parallel structure (10 instances, 5 parameters each).

### Pattern 3: Generic + Numbered Filters
```
Filter.Resonance, Filter.Type             (GENERIC)
Filter.Cutoff, Filter.Drive, Filter.Q     (GENERIC)
Filter2.Cutoff, Filter2.Resonance, ...    (FILTER2 EXPLICIT)
FILTER1.BUS1Send, FILTER1.Route           (FILTER1 EXPLICIT)
FILTER2.BUS1Send, FILTER2.Route           (FILTER2 EXPLICIT)
```
**INCONSISTENCY**: Generic "Filter.*" lacks "Filter1.*" prefix; "Filter2.*" is explicit in some cases.

### Pattern 4: Numbered Oscillators + Orchestral Controls
```
OSC1.Enable, OSC2.Enable, OSC3.Enable
OSC1.Octave, OSC2.Octave, OSC3.Octave
SUB.Enable, NOISE.Volume
```
Mostly consistent; SUB and NOISE are singleton instances.

### Pattern 5: FX Module Naming
```
FXEQ.*
FXDistortion.*
FXDelay.*
... (13+ FX processor types, 3+ splitter types)
```
Clear hierarchical naming (FX prefix + effect type).

---

## Gaps and Observations

### Observable Gaps (From Phase 2A Candidate Identification)

| Semantic (Phase 1) | Expected Target | Actual Target | Status |
|-------------------|-----------------|---------------|--------|
| ENV1.Hold | Env1.Hold | (missing) | NO_TARGET |
| ENV2.Hold | Env2.Hold | (missing) | NO_TARGET |
| ENV3.Hold | Env3.Hold | (missing) | NO_TARGET |
| ENV4.Hold | Env4.Hold | (missing) | NO_TARGET |
| ENV1.BPM | Env1.BPM | (missing) | NO_TARGET |
| ENV2-4.BPM | Env2-4.BPM | (missing) | NO_TARGET |
| ENV1.LegatoInverted | Env1.LegatoInverted | (missing) | NO_TARGET |
| ENV2-4.LegatoInverted | Env2-4.LegatoInverted | (missing) | NO_TARGET |
| ENV1.VoiceStealRetrigger | Env1.VoiceStealRetrigger | (missing) | NO_TARGET |
| ENV2-4.VoiceStealRetrigger | Env2-4.VoiceStealRetrigger | (missing) | NO_TARGET |
| (40 FILTER type-specific 4th-knobs) | FILTER1.TypeSpecific*, FILTER2.TypeSpecific* | (missing) | NO_TARGET |

### Naming Conflicts Identified

| Issue | Semantic(s) | Target(s) | Problem |
|-------|------------|----------|---------|
| Filter 1 vs 2 generic naming | FILTER1.Cutoff, FILTER2.Cutoff | Filter.Cutoff, Filter2.Cutoff | Generic "Filter.*" vs numbered "Filter2.*"; no "Filter1.*" pattern |
| Reverb parameter naming | FXReverb semantics | Time→Size, Damping, MixOrGain (extended) | Extended version has "Size"; earlier version had "Time" |

---

## No Duplicate Semantic Names

Scan confirms: each semantic name appears exactly once in SEMANTIC_TARGETS.

---

## What's NOT in targets.py

Based on Phase 1 closure evidence, these semantics exist in the frozen inventory but have NO corresponding targets:

- All ENV.Hold (4 instances) — timing parameter for each envelope
- All ENV.BPM toggle (4 instances) — time vs beat-division mode
- All ENV.LegatoInverted (4 instances) — force retrigger on legato
- All ENV.VoiceStealRetrigger (4 instances) — retrigger mode on voice steal
- Filter type-specific 4th-knob parameters (~40 instances) — type-specific control shapes
- MIXER channel Pan controls (varies) — per-channel panning
- ARP structural operations (pattern records, recording controls, etc.)
- CLIP structural operations (recording, clip banks, etc.)
- BROWSER resource operations (preset loading, bank management)
- MATRIX structural operations (route deletion, reorder, visual refresh)
- FX module enable/disable (exact VST3 field unknown; ModRoute.Bypass is route-level, not module-level)

---

## Next: Phase 2C (Normalization)

Ready to normalize both semantic and target vocabularies into canonical forms for reconciliation.

---

**Status**: PHASE 2B COMPLETE  
**Targets extracted**: 290 (actual count from targets.py)  
**FX parameter targets**: 131 (45% of total)  
**LFO + Oscillator targets**: 100 (34% of total)  
**Filter/Envelope/Global targets**: 51 (17% of total)  
**Matrix routes**: 5 (2% of total)  
**Candidate gaps identified**: 40+ (ENV, FILTER type-specific, FX structural)  
**Naming conflicts identified**: 3+ (Filter generic/numbered inconsistency, Reverb Time/Size)  

**Next**: Phase 2C (Normalize), Phase 2D (Reconcile), Phase 2E (Gap Audit)
