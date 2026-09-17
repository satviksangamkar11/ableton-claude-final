# PHASE 4: 16-BAR PRODUCTION TARGET SPECIFICATION

**Date:** 2026-09-18  
**Status:** SPECIFICATION DEFINED  
**Purpose:** Prove governed production pipeline end-to-end

---

## Musical Intent

Create a minimal, deterministic 16-bar synthesizer track demonstrating:
- Serum as the primary sound source
- Governed parameter mutations from admitted capability set
- Ableton arrangement and rendering
- Full evidence chain from intent through audio output

**Musical Goal:** C-major pad with EQ sculpting and bass evolution

---

## Arrangement Specification

### Session Parameters
- **BPM:** 120
- **Time Signature:** 4/4
- **Duration:** 16 bars (exactly 32 seconds at 120 BPM)
- **Sample Rate:** 44100 Hz
- **Key:** C Major
- **Scale:** C D E F G A B

### Track Structure

**Track 1: Pad (Serum)**
- Instrument: Serum VST3 (fresh instance)
- Polyphony: 4 voices
- Note Pattern: C3 held for 16 bars (legato pad)
- Velocity: 100/127
- Role: Harmonic foundation

### Serum Patch Configuration

**Initial State:** Serum 2.0.21 with default oscillator configuration

**Governed Mutations (using admitted capabilities only):**

| Bar | Target | Mechanism | Baseline | Mutation | Effect |
|---|---|---|---|---|---|
| 1-4 | (none) | — | — | — | Baseline pad |
| 5 | Env1.Attack | HOST_PARAMETER (MCP) | 0.10 | 0.30 | Slower attack |
| 9 | Filter.Cutoff | HOST_PARAMETER (MCP) | 0.50 | 0.65 | Brighter tone |
| 12 | FXEQ.Freq1 | BODY_STATE | 639.84 Hz | 1200.0 Hz | Brighten mid-lows |
| 14 | Filter.Resonance | HOST_PARAMETER (MCP) | 0.10 | 0.35 | Add resonance peak |

**Mutation Justification:**
- All targets are CAUSAL_VERIFIED from Phase 1/2
- All use admitted execution mechanisms (MCP or BODY_STATE)
- Mutations are audible but not extreme
- No undeclared parameters touched

### MIDI Content

**Single MIDI clip (Pad Track):**
```
Note: C3
Velocity: 100
Start: Bar 1, Beat 1
End: Bar 16, Beat 4 (full 16 bars)
```

No note automation. Serum parameter mutations come from governed execution, not MIDI.

### Automation/Modulation

None. All synthesis changes come from explicit Serum parameter mutations via the governor.

---

## Execution Flow

### Phase 4 Governed Path

```
1. MUSICAL INTENT
   "Create a 16-bar C3 pad with EQ evolution"

2. PLAN
   - Tempo: 120 BPM
   - Arrangement: 1 track, 1 MIDI clip
   - Mutations: 5 admitted Serum parameter changes
   - Render target: 32-second stereo WAV

3. CAPABILITY SELECTION
   Env1.Attack → CONTRACT (CAUSAL_VERIFIED)
   Filter.Cutoff → CONTRACT (CAUSAL_VERIFIED)
   Filter.Resonance → CONTRACT (CAUSAL_VERIFIED)
   FXEQ.Freq1 → CONTRACT (CAUSAL_VERIFIED)
   (No unadmitted capabilities used)

4. ADMISSION GATE
   All 5 targets ADMITTED via respective contracts
   No prerequisites needed for this spec

5. EXECUTION
   - Ableton project created via MCP
   - Serum loaded into track
   - MIDI clip created with C3 note
   - Parameter mutations applied at specified bars
   - Tempo/signature set via MCP

6. SERUM STATE VERIFICATION
   Each mutation verified in Serum parameter space

7. ARRANGEMENT STRUCTURE VERIFICATION
   - Track present in Ableton
   - MIDI clip present
   - Duration correct (16 bars)
   - No manual intervention

8. RENDER
   Export to 44.1kHz stereo WAV (32 seconds)

9. MEASUREMENT
   - RMS/loudness envelope
   - Spectral content at mutation points
   - Audio validity (no clipping/silence)
   - Duration verification

10. EVIDENCE CHAIN
    INTENT → PLAN → CAPABILITY → EXECUTION → RENDER → MEASUREMENT
```

---

## Constraints Compliance

✓ Uses ONLY admitted Serum capabilities (Phase 3 verified)  
✓ No frozen artifacts modified (Phases 1-3 read-only)  
✓ No parallel producer architecture (uses existing serum2 pipeline)  
✓ No undeclared mechanisms  
✓ Fully auditable and reproducible  
✓ Deterministic (no randomness or manual intervention)  

---

## Success Criteria

Phase 4 is complete when:

1. ✓ Ableton project file created successfully
2. ✓ Serum instance loads and initializes in track
3. ✓ C3 MIDI note present for full 16 bars
4. ✓ All 5 Serum parameter mutations applied at correct bars
5. ✓ Each mutation uses an ADMITTED contract
6. ✓ Arrangement renders to audio file (32 seconds, stereo, 44.1kHz)
7. ✓ Audio is valid (finite samples, no silent/clipped stretches)
8. ✓ Full evidence chain captured in JSON
9. ✓ Clean replay succeeds (same plan → identical evidence)
10. ✓ No manual intervention required

---

## Test Artifacts

**Input:**
- Phase 3 contract registry (32 CAUSAL_VERIFIED)
- FXEQ corpus fixture (_corpus_cache.pkl bodies[4])

**Output:**
- `experiments/phase4_production_spec.md` (this document)
- `experiments/phase4_arrangement.als` (Ableton Live set)
- `experiments/phase4_render.wav` (audio output)
- `experiments/phase4_evidence.json` (full execution log)
- `experiments/phase4_audit.json` (measurements)

---

## Notes

- First production is intentionally minimal: one track, one note, five mutations.
- Purpose is to prove the pipeline works, not to create a complex arrangement.
- Future phases can extend to multi-track, longer patterns, more complex mutations.
- This serves as the replicable baseline for Phase 4 reproducibility testing.

---

## Next Action

Proceed to STEP 3: Build Ableton arrangement using admitted capabilities.
