# Measurement Kernel Registry V1

## Overview

This registry documents measurement strategies for causal qualification. Each kernel describes:
- **Function**: The actual measurement implementation
- **Applicable Families**: Parameter classes that this kernel is designed for
- **Principle**: Why and how this kernel works
- **Pass Criteria**: Threshold tuned to the parameter class's behavioral signature
- **Evidence**: Proven capabilities and root causes of blocking/failures

**Key principle**: Do NOT reuse a broad threshold when the parameter has a different behavioral signature. Measurement mismatch explains 5 of 7 non-VERIFIED findings. Body-path unavailability explains 2 FAILED findings.

---

## Kernels

### 1. Broad Amplitude (RMS)
- **Function**: `serum2.evidence.measure.rms_db` (alias: `overall_rms_db`)
- **Best For**: OSC Level, Filter Gain, broad energy changes
- **Principle**: RMS in dB captures total energy. Works for +24 dB (OSC Level), +4 dB (Gain), but misses 0.3–0.7 dB subtle effects
- **Threshold**: 0.5 dB
- **Proven**: OSC1.Level, OSC2.Level, OSC3.Level, FXEQ.Gain2, Env1.Attack (onset only)
- **Blocked**: Env1.Release, Filter1.Drive (both sub-0.5 dB effects)

### 2. Envelope Release/Tail (RMS, tail window)
- **Function**: `serum2.evidence.measure.tail_rms_db`
- **Best For**: Envelope release, delay/reverb tails
- **Principle**: Isolates energy after ~0.6s (post-note-off). Release effects accumulate over tail window, not visible in broad RMS
- **Threshold**: 1.0 dB
- **Status**: Env1.Release was tested with broad RMS (wrong kernel); should use this instead
- **Note**: Existing kernel in repo, underutilized in qualification

### 3. Broad Spectral Frequency (Centroid Hz)
- **Function**: `serum2.evidence.measure.spectral_centroid_hz`
- **Best For**: Filter cutoff, frequency shifts >50 Hz
- **Principle**: FFT-based weighted-average frequency. Works for +2684 Hz (Filter1), +7622 Hz (FXEQ.Freq1)
- **Threshold**: 200 Hz
- **Proven**: Filter1.Cutoff, FXEQ.Freq1
- **Failed**: OSC1.Detune, OSC2.Detune (0 Hz delta; parameter not exercised)

### 4. Resonance/Q Local Peak (NOT YET IMPLEMENTED)
- **Best For**: Filter resonance, EQ resonance parameters
- **Principle**: Measures spectral peak power in narrow band at cutoff, not broad centroid shift
- **Need**: High-Q peak adds 2–6 dB at cutoff but shifts centroid only −70 to −64 Hz (see FXEQ.Reso1/2)
- **Blocked**: FXEQ.Reso1 (−70.6 Hz), FXEQ.Reso2 (−64.3 Hz), Filter1.Resonance (+0.09 dB broad RMS)
- **Priority**: HIGH — 3 capabilities blocked by this missing kernel

### 5. Harmonic Distortion (NOT YET IMPLEMENTED)
- **Best For**: Filter drive, saturation parameters
- **Principle**: Could measure THD, spectral energy in harmonic bands, or high-frequency (>5 kHz) RMS
- **Need**: Drive/saturation adds harmonics (spreads energy) not captured by broad RMS (0.31 dB threshold miss)
- **Blocked**: Filter1.Drive (+0.31 dB broad RMS)
- **Priority**: MEDIUM — 1 capability blocked

### 6. Modulation Rate / Periodicity (Hz)
- **Function**: `serum2.evidence.kernels.modulation_frequency_hz.kernel`
- **Best For**: LFO rate, modulation frequency detection
- **Principle**: Windowed RMS envelope, detrend in log domain (removes ADSR shape), FFT for dominant modulation frequency
- **Gate**: Requires depth (min 0.28) and prominence (min 4.0) to confirm genuine periodicity
- **Returns**: 0.0 Hz if no confident modulation detected
- **Unproven**: LFO1.Rate (needs active modulation target; rate alone has no audible effect)
- **Note**: Existing kernel in repo; LFO.Rate cannot be validated without modulation destination context

---

## Blocked and Failed: Root Causes and Assignments

### CAUSAL_BLOCKED (5 capabilities)

| Capability | Evidence | Assigned Kernel | Root Cause |
|---|---|---|---|
| FXEQ.Reso1 | −70.6 Hz | spectral_resonance_peak | Real frequency shift but threshold inappropriate for resonance/Q (designed for cutoff shifts +2684 Hz) |
| FXEQ.Reso2 | −64.3 Hz | spectral_resonance_peak | Same measurement mismatch as Reso1; consistent pattern |
| Filter1.Resonance | +0.09 dB | spectral_resonance_peak | Real resonance effect but sub-threshold in broad RMS; exercise context insufficient or needs longer render |
| Env1.Release | +0.33 dB | amplitude_envelope_release | Wrong kernel used (broad RMS); should use tail_rms_db over [0.6s–2.0s] post-note-off |
| Filter1.Drive | +0.31 dB | spectral_harmonic_distortion | Real saturation/harmonic effect but broad RMS doesn't capture harmonic spread; needs THD or band-specific measurement |

### CAUSAL_FAILED (2 capabilities)

| Capability | Evidence | Root Cause |
|---|---|---|
| OSC1.Detune | 0.0 Hz delta | **Body-level kParamFine not exercised**: reads None from skeleton; VoiceOsc0.plainParams.kParamFine is uninitialized or unavailable. Only host-param (UI) controls effective (OSC1.Level proven). |
| OSC2.Detune | 0.0 Hz delta | **Same as OSC1**: suggests CBOR body Fine parameters are not authoritative for any oscillator. Either paths are wrong or shadowed by host control. |

---

## Priority Actions

1. **Implement spectral_resonance_peak kernel** — blocks 3 capabilities (FXEQ.Reso1/2, Filter1.Resonance)
   - Measure local spectral peak power in ~100 Hz band around cutoff frequency
   - Threshold: 2–6 dB (appropriate for resonance signature, not broad shifts)

2. **Re-test Env1.Release** — use tail_rms_db instead of broad RMS
   - Window: [0.6s, 2.0s] post-note-off
   - Threshold: 1.0 dB (designed for tail accumulation)

3. **Investigate OSC1/2 Detune body-path failure**
   - Confirm VoiceOsc0/1.plainParams.kParamFine is not authoritative
   - Check if alternate path (e.g., kParamDetune, or different skeleton key) exists and works
   - Determine if host-param only (no CBOR body path) is the intended architecture

4. **Implement spectral_harmonic_distortion kernel** — blocks 1 capability (Filter1.Drive)
   - Could measure THD or spectral energy in >5 kHz harmonic band
   - Threshold: parameter-specific (THD %, dB in harmonic band, etc.)

5. **Do NOT proceed with**:
   - OSC3.Detune (until OSC1/2 body-path root cause is determined)
   - LFO1.Rate (until active modulation target context is established)

---

## Files and Evidence

- **JSON Registry**: `serum2/qualification/MEASUREMENT_KERNEL_REGISTRY_V1.json` (this file's data)
- **Kernels source**: `serum2/evidence/kernels/*.py` (modulation_frequency_hz, tail_rms_db, attack_onset_rms_db, etc.)
- **Measure functions**: `serum2/evidence/measure.py` (spectral_centroid_hz, rms_db, etc.)
- **Harness**: `serum2/qualification/a3_behavior_harness.py` (currently uses only 2 metrics; needs expansion)
- **Evidence commits**: d9be3f0, e61d8dd, 3478b4a (8 new findings from this session)

---

## Golden Regression Status

- **7/7 CAUSAL_VERIFIED remain verified** (confirmed before each commit this session)
- **Next action**: Re-run after kernel registry integration to ensure no regression
