# Phase 5: Oscillator State Representation Investigation

**Date:** 2026-09-13  
**Source:** FORENSIC_V8_STATE_ANALYSIS.md + serum2 skeleton inspection

## Findings

### OSC1 (Second Oscillator)

**State representation:** CONFIRMED
- Oscillator1 explicitly mentioned in FORENSIC_V8_STATE_ANALYSIS.md
- Same structure as Oscillator0:
  - WTOsc1, SampleOsc1, MultiSampleOsc1, SpectralOsc1, GranularOsc1 (type selectors)
  - plainParams (oscillator-level parameters)
- **Executable via operations:** YES (set_oscillator_type, set_oscillator_parameter work identically)
- **Activation mechanism:** NOT INVESTIGATED (per Phase 5 spec: use existing evidence only)

**Classification:** `REPRESENTED_EXECUTABLE`

### OSC2+ (Additional Oscillators)

**State representation:** STRUCTURE UNCERTAIN (per forensic: "verify skeleton for Oscillator1, Oscillator2 presence")
- FORENSIC notes: "Do Oscillator1, Oscillator2, etc. exist in skeleton? Are they always present, or sparse?"
- Not explicitly listed in forensic body structure
- Skeleton interrogation blocked (Serum VST3 not loaded in current environment)

**Execution:** SPECULATIVE
- IF represented in skeleton, THEN operations would work identically to OSC1
- BUT representation not confirmed by forensic analysis

**Activation mechanism:** UNKNOWN
- No documented enable/disable field for OSC2+
- FORENSIC notes: "Structure uncertainty" and "Need: verify skeleton"

**Classification:** `NOT_REPRESENTED` (unconfirmed by forensic evidence)

---

## Operating Scope for Phase 5

Phase 5 operations assume:
- **OSC0 (Oscillator0):** Fully supported (proven in Phase 2)
- **OSC1 (Oscillator1):** Supported (structure confirmed in forensic)
- **OSC2/OSC3:** Support created (compiles and generates paths), but NOT recommended for production use without skeleton verification

## Phase 6 Recommendation

Investigate actual Serum skeleton when DawDreamer harness is available:
1. Capture v8 skeleton from Serum VST3
2. Check for Oscillator2, Oscillator3, ... presence
3. Determine activation semantics if present
4. Update Phase 5 classification if needed

---

## Authority Status

No change to admission.py or CapabilityContracts.
All Phase 5 oscillator operations remain `UNQUALIFIED` (no CAUSAL_VERIFIED contracts).
Expressible and executable, but not authority-gated.
