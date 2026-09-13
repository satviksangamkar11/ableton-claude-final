# Serum 2.0.21 Reference-Derived Operation Inventory

**Source:** serum2_complete_reference.md (frozen Serum 2.0.21)  
**Date:** 2026-09-13  
**Scope:** Complete human-facing operations from UI reference  

---

## Inventory Methodology

Each UI control from the Serum reference is classified:
- **IMPLEMENTED** — Already in SerumOperation registry (30 ops)
- **IMPLEMENTABLE** — Can be added with existing framework
- **ADAPTER_NEEDED** — Needs simple semantic wrapper (same pattern as existing ops)
- **PRIMITIVE_NEEDED** — Requires new mutation strategy (harness enhancement)
- **RESOURCE_DEP** — Blocked on resource system
- **TOPOLOGY_DEP** — Blocked on topology semantics
- **UNRESOLVED** — No evidence (SEMANTIC_TARGETS missing or corpus gap)

---

## 1. Top Row & Global Controls

| Control | Category | Status | Notes |
|---------|----------|--------|-------|
| ARTIST Field | Metadata | ADAPTER_NEEDED | Text field, semantic target needed |
| DISC Field | Metadata | ADAPTER_NEEDED | Text field, semantic target needed |
| SERUM 2 Logo | UI | N/A | Window control, not a musical operation |

---

## 2. Oscillators & Waveforms

### Sub Oscillator (SUB)

| Control | Reference | Status | Implementation |
|---------|-----------|--------|-----------------|
| SUB LEVEL | LEVEL knob | ADAPTER_NEEDED | Create semantic target: SUB.Volume |
| SUB WARP | WARP knob | ADAPTER_NEEDED | Create semantic target: SUB.Warp |
| SUB PITCH (OCT, SEM, FIN, CRS) | Pitch controls | ADAPTER_NEEDED | Create semantic targets |

**Decision:** Implement as scalar operations (same as OSC1)

### Oscillator A (OSC A)

| Control | Reference | Status | Implementation |
|---------|-----------|--------|-----------------|
| OSC A LEVEL | LEVEL knob | ADAPTER_NEEDED | Create semantic target: OSCA.Volume |
| OSC A WARP | WARP knob | ADAPTER_NEEDED | Create semantic target: OSCA.Warp |
| OSC A PITCH (OCT, SEM, FIN) | Phase 5 partial | IMPLEMENTED | set_oscillator_parameter |
| OSC A TYPE | Phase 5 | IMPLEMENTED | set_oscillator_type |
| OSC A WAVETABLE | Phase 6 | IMPLEMENTED | load_wavetable |

**Decision:** Extend Phase 5 to cover full OSCA/B/C (add to SEMANTIC_TARGETS)

### Oscillator B (OSC B) & C (OSC C)

Same as OSC A, but with indices 1, 2.

**Current state:** OSC1.Enable only (Phase 2); Phase 5 supports indices but no separate semantic targets  
**Decision:** Create OSC2.*, OSC3.* semantic targets if activation mechanism confirmed

### Noise Oscillator (NOISE)

| Control | Reference | Status | Implementation |
|---------|-----------|--------|-----------------|
| NOISE LEVEL | LEVEL knob | UNRESOLVED | No semantic target; structure unknown |
| NOISE TYPE | Noise control | UNRESOLVED | No evidence |

---

## 3. Filters

### Filter 1

| Control | Reference | Status | Implementation |
|---------|-----------|--------|-----------------|
| FILTER 1 TYPE | Filter.Type | IMPLEMENTED | Phase 2 |
| FILTER 1 CUTOFF | Filter.Cutoff | IMPLEMENTED | Phase 2 |
| FILTER 1 RESONANCE | Filter.Resonance | IMPLEMENTED | Phase 2 |
| FILTER 1 DRIVE | Phase 4 (FX) | ADAPTER_NEEDED | Add as scalar: Filter.Drive |
| FILTER 1 Q | Phase 4 (FX) | ADAPTER_NEEDED | Add as scalar: Filter.Q |

### Filter 2

| Control | Reference | Status | Implementation |
|---------|-----------|--------|-----------------|
| FILTER 2 TYPE | Not in targets | UNRESOLVED | No Filter2.* semantic targets |
| FILTER 2 CUTOFF | Not in targets | UNRESOLVED | No Filter2.* semantic targets |
| FILTER 2 RESONANCE | Not in targets | UNRESOLVED | No Filter2.* semantic targets |

**Decision:** Create Filter2.* targets if evidence exists (likely similar to Filter1)

---

## 4. Modulation Sources

### Envelopes

| Control | Reference | Status | Implementation |
|---------|-----------|--------|-----------------|
| ENV 1 ATTACK | Phase 2 | IMPLEMENTED | scalar_envelope_field_attack |
| ENV 1 DECAY | Phase 2 | IMPLEMENTED | scalar_envelope_field_decay |
| ENV 1 SUSTAIN | Phase 2 | IMPLEMENTED | scalar_envelope_field_sustain |
| ENV 1 RELEASE | Phase 2 | IMPLEMENTED | scalar_envelope_field_release |
| ENV 2-4 (similar) | Reference mentions | ADAPTER_NEEDED | Create Env2.*, Env3.*, Env4.* targets |

### LFO

| Control | Reference | Status | Implementation |
|---------|-----------|--------|-----------------|
| LFO 0-5 RATE | Phase 2 partial | ADAPTER_NEEDED | Extend coverage to LFO 0-9 |
| LFO 0-5 SHAPE | Phase 2 partial | ADAPTER_NEEDED | Extend coverage |
| LFO 0-5 MODE | Phase 2 partial | ADAPTER_NEEDED | Extend coverage |
| LFO PHASE (0°, 180°) | Reference mentions | UNRESOLVED | No semantic target |
| LFO RETRIG/FREE | Reference mentions | UNRESOLVED | No semantic targets |

### Other Sources

| Control | Reference | Status | Implementation |
|---------|-----------|--------|-----------------|
| VELO (Velocity) | Reference | UNRESOLVED | No semantic target (modulation source, not parameter) |
| NOTE (Keyboard) | Reference | UNRESOLVED | No semantic target |

---

## 5. Voice & Performance Controls

| Control | Reference | Status | Implementation |
|---------|-----------|--------|-----------------|
| MONO (Monophonic) | Reference | UNRESOLVED | No semantic target, activation mechanism unknown |
| VOICING (Polyphony) | Reference | UNRESOLVED | No semantic target |
| TRANSPOSE (0-±12) | Reference | ADAPTER_NEEDED | Create semantic target: Global.Transpose |
| KEY (Root key) | Reference | ADAPTER_NEEDED | Create semantic target: Global.Key |
| SCALE (Major/Minor) | Reference | ADAPTER_NEEDED | Create semantic target: Global.Scale |
| SWING (OFF/%) | Reference | ADAPTER_NEEDED | Create semantic target: Global.Swing |
| CURVE (Velocity) | Reference | ADAPTER_NEEDED | Create semantic target: Global.VelocityCurve |
| CLIP (Launcher) | Reference | UNRESOLVED | Topology operation, not a scalar |
| ARP (Arpeggiator) | Reference | UNRESOLVED | Topology operation, not a scalar |

---

## 6. FX Rack Effects

### Already Covered (Phase 4)

**25+ parameters across 6 effects:**
- Distortion (Drive, Tone, LevelOut)
- EQ (Freq1-2, Reso1-2, Gain1-2, LevelOut)
- Delay (Time, Feedback, Mix)
- Reverb (Time, Damping, Mix)
- Compressor (Threshold, Ratio, Attack, Release)
- Chorus (Rate, Depth, Mix)

### Additional FX from Reference (14 total)

| Effect | Parameters | Status | Notes |
|--------|-----------|--------|-------|
| BODE (Freq Shifter) | SHIFT, RANGE, DIR, MIX | ADAPTER_NEEDED | New effect, create resolver |
| CONVOLVE (Convolution) | IR, IR GAIN, ATTACK, DECAY, DAMP, DIFFUSER, MIX | ADAPTER_NEEDED | New, resource + parameters |
| FLANGER | RATE, DEPTH, FEEDBACK, PHASE, MIX | ADAPTER_NEEDED | Create resolver |
| HYPER/DIMENSION | RATE, UNISON, DETUNE, MIX (or SIZE, MIX) | ADAPTER_NEEDED | Create resolver |
| PHASER | FREQ, FEEDBACK, PHASE, MIX | ADAPTER_NEEDED | Create resolver |
| SPLITTER | SPLITTER TYPE, Crossover Points | UNRESOLVED | Topology, not scalar |
| UTILITY | GAIN, PHASE, MONO, MIX | ADAPTER_NEEDED | Create resolver |
| Filter (FX version) | FILTER TYPE, CUTOFF, RES, DRIVE, MIX | ADAPTER_NEEDED | Similar to Filter 1 |

**Summary:** 8 additional FX effects with parameters (5 new, 3 extended)

---

## 7. MATRIX Tab

| Operation | Reference | Status | Implementation |
|-----------|-----------|--------|-----------------|
| create_modulation_route | Matrix row | IMPLEMENTED | Phase 3 |
| delete_modulation_route | Matrix row | IMPLEMENTED | Phase 3 |
| set_modulation_depth | Matrix depth | IMPLEMENTED | Phase 3 (amount parameter) |
| set_modulation_curve | Matrix curve | ADAPTER_NEEDED | Create operation: set_modulation_curve |
| set_modulation_aux_source | Matrix aux | ADAPTER_NEEDED | Create operation: set_modulation_aux |
| bypass_modulation_route | Matrix bypass | ADAPTER_NEEDED | Create operation: bypass_modulation |
| Macro modulation (NEW) | Macro column | ADAPTER_NEEDED | set_modulation_depth with macro target |

---

## 8. GLOBAL Tab

| Control | Reference | Status | Implementation |
|---------|-----------|--------|---|
| QUALITY (Ultra/Good) | Setting | ADAPTER_NEEDED | Create semantic target: Global.Quality |
| QUALITY LOCK | Setting | UNRESOLVED | Not a musical operation |
| PITCH TRACKING | Setting | UNRESOLVED | Structure unknown |
| TUNING (A=440) | Setting | ADAPTER_NEEDED | Create semantic target: Global.Tuning |
| NOISE FINE | Setting | UNRESOLVED | Related to NOISE oscillator (unresolved) |
| WAVETABLE DISPLAY (2D/3D) | Setting | ADAPTER_NEEDED | Create semantic target: Global.WavetableDisplay |
| BANK (Preset) | Selector | UNRESOLVED | Not a real-time parameter; preset management |
| CLIP SETTINGS | Setting | UNRESOLVED | Topology, not scalar |
| PREFERENCES | Various | UNRESOLVED | Not musical operations |

---

## Summary by Category

### Implemented (30 operations)

All Phase 1-6 operations.

### Implementable (ADAPTER_NEEDED - 25+ new ops)

- SUB oscillator (4 parameters)
- OSC A/B full coverage (4 parameters each = 8 total)
- Filter 1 extended (2 parameters: Drive, Q)
- Filter 2 (if targets created; 5 parameters)
- Envelope 2-4 (12 parameters total)
- LFO extended (if targets created)
- Global controls (Transpose, Key, Scale, Swing, Curve, Tuning, Quality, WavetableDisplay)
- Additional FX (8 effects, ~35 parameters)
- Matrix operations (4 new: curve, aux, bypass, macro_depth)

**Estimated new operations:** 25-35 scalar + 4 compound = ~40 new operations

### Requires Investigation (TOPOLOGY_DEP / UNRESOLVED)

- MONO/VOICING (activation mechanism unknown)
- NOISE oscillator (structure unknown)
- Filter 2 (semantic targets missing)
- LFO PHASE, RETRIG, FREE (semantic targets missing)
- CLIP/ARP/SPLITTER (topology operations, not scalars)
- Advanced modulation features (beyond current routing)

### Resource Dependent

- CONVOLVE (IR file loading) - needs resource system extension

---

## Control Completeness Estimate

**Current:** 30 operations / ~100 estimated Serum operations = 30%

**After ADAPTER_NEEDED implementations:** (30 + 40) / ~100 = 70%

**Unresolved ceiling:** ~100 - 30 - 40 = 30 operations (TOPOLOGY_DEP, UNRESOLVED, or unknown)

---

## Next Steps

1. **Create missing SEMANTIC_TARGETS** for implementable operations
2. **Extend existing FX resolvers** for new effects
3. **Implement scalar operations** (25-35 new)
4. **Implement compound operations** (4 new: modulation curve/aux/bypass/macro)
5. **Test all new operations** (A/B/C verification)
6. **Report final control completeness** against reference

---

**Goal:** Achieve ~70% coverage of Serum reference UI through ADAPTER_NEEDED implementations, leaving only TOPOLOGY_DEP and UNRESOLVED operations for Phase 8+.
