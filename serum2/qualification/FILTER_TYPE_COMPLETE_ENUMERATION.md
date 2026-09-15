# FILTER Complete Type Enumeration — EXACT COUNTS

**Date:** 2026-09-15  
**Method:** Direct Serum 2.0.21 UI inspection (dropdown menus + step-arrow verification + wraparound confirmation)  
**Status:** PHASE 1 COMPLETE — Exact type universe enumerated  
**Verification:** Wraparound test confirms total is closed-loop (Exp BPF → wraps to → MG Low 6)

---

## TOTAL: 107 Individual Filter Types (EXACT)

```
Normal:     18 types
Multi:      21 types
Flanges:    32 types
Misc:       25 types
S2 Filters: 11 types
-----------------------
TOTAL:     107 types
```

---

## CATEGORY 1: Normal (18 types — EXACT)

| # | Exact UI Label | Slope | Model | Family |
|---|---|---|---|---|
| 1 | MG Low 6 | 6 dB/oct | Moog | Low Pass |
| 2 | MG Low 12 | 12 dB/oct | Moog | Low Pass |
| 3 | MG Low 18 | 18 dB/oct | Moog | Low Pass |
| 4 | MG Low 24 | 24 dB/oct | Moog | Low Pass |
| 5 | Low 6 | 6 dB/oct | Standard | Low Pass |
| 6 | Low 12 | 12 dB/oct | Standard | Low Pass |
| 7 | Low 18 | 18 dB/oct | Standard | Low Pass |
| 8 | Low 24 | 24 dB/oct | Standard | Low Pass |
| 9 | High 6 | 6 dB/oct | Standard | High Pass |
| 10 | High 12 | 12 dB/oct | Standard | High Pass |
| 11 | High 18 | 18 dB/oct | Standard | High Pass |
| 12 | High 24 | 24 dB/oct | Standard | High Pass |
| 13 | Band 12 | 12 dB/oct | Standard | Band Pass |
| 14 | Band 24 | 24 dB/oct | Standard | Band Pass |
| 15 | Peak 12 | 12 dB/oct | Standard | Peak/Bell |
| 16 | Peak 24 | 24 dB/oct | Standard | Peak/Bell |
| 17 | Notch 12 | 12 dB/oct | Standard | Notch |
| 18 | Notch 24 | 24 dB/oct | Standard | Notch |

**Verification method:** Dropdown menu fully visible in single screenshot (Normal category submenu), all 18 items directly observed.

---

## CATEGORY 2: Multi (21 types — EXACT)

Morphing/multi-mode filters that blend between filter types on one control axis.

| # | Exact UI Label | Meaning (inferred from abbreviation) |
|---|---|---|
| 19 | LH 6 | Low-High morph, 6 dB/oct |
| 20 | LH 12 | Low-High morph, 12 dB/oct |
| 21 | LB 12 | Low-Band morph, 12 dB/oct |
| 22 | LP 12 | Low-Peak morph, 12 dB/oct |
| 23 | LN 12 | Low-Notch morph, 12 dB/oct |
| 24 | HB 12 | High-Band morph, 12 dB/oct |
| 25 | HP 12 | High-Peak morph, 12 dB/oct |
| 26 | HN 12 | High-Notch morph, 12 dB/oct |
| 27 | BP 12 | Band-Peak morph, 12 dB/oct |
| 28 | BN 12 | Band-Notch morph, 12 dB/oct |
| 29 | PP 12 | Peak-Peak morph, 12 dB/oct |
| 30 | PN 12 | Peak-Notch morph, 12 dB/oct |
| 31 | NN 12 | Notch-Notch morph, 12 dB/oct |
| 32 | L/B/H 12 | Low-Band-High 3-way morph, 12 dB/oct |
| 33 | L/B/H 24 | Low-Band-High 3-way morph, 24 dB/oct |
| 34 | L/P/H 12 | Low-Peak-High 3-way morph, 12 dB/oct |
| 35 | L/P/H 24 | Low-Peak-High 3-way morph, 24 dB/oct |
| 36 | L/N/H 12 | Low-Notch-High 3-way morph, 12 dB/oct |
| 37 | L/N/H 24 | Low-Notch-High 3-way morph, 24 dB/oct |
| 38 | B/P/N 12 | Band-Peak-Notch 3-way morph, 12 dB/oct |
| 39 | B/P/N 24 | Band-Peak-Notch 3-way morph, 24 dB/oct |

**Verification method:** Dropdown menu fully visible in single screenshot (Multi category submenu), all 21 items directly observed; scroll test confirmed no additional items beyond B/P/N 24.

---

## CATEGORY 3: Flanges (32 types — EXACT)

Not true filters — sound-shaping tools (comb, flange, phaser).

| # | Exact UI Label | Family |
|---|---|---|
| 40 | Cmb + | Comb, positive polarity |
| 41 | Cmb - | Comb, negative polarity |
| 42 | Cmb L6+ | Comb + Low 6dB, positive |
| 43 | Cmb L6- | Comb + Low 6dB, negative |
| 44 | Cmb H6+ | Comb + High 6dB, positive |
| 45 | Cmb H6- | Comb + High 6dB, negative |
| 46 | Cmb HL6+ | Comb + High/Low 6dB, positive |
| 47 | Cmb HL6- | Comb + High/Low 6dB, negative |
| 48 | Flg + | Flange, positive polarity |
| 49 | Flg - | Flange, negative polarity |
| 50 | Flg L6+ | Flange + Low 6dB, positive |
| 51 | Flg L6- | Flange + Low 6dB, negative |
| 52 | Flg H6+ | Flange + High 6dB, positive |
| 53 | Flg H6- | Flange + High 6dB, negative |
| 54 | Flg HL6+ | Flange + High/Low 6dB, positive |
| 55 | Flg HL6- | Flange + High/Low 6dB, negative |
| 56 | Phs 12+ | Phaser 12dB, positive |
| 57 | Phs 12- | Phaser 12dB, negative |
| 58 | Phs 24+ | Phaser 24dB, positive |
| 59 | Phs 24- | Phaser 24dB, negative |
| 60 | Phs 36+ | Phaser 36dB, positive |
| 61 | Phs 36- | Phaser 36dB, negative |
| 62 | Phs 48+ | Phaser 48dB, positive |
| 63 | Phs 48- | Phaser 48dB, negative |
| 64 | Phs 48L6+ | Phaser 48dB + Low 6dB, positive |
| 65 | Phs 48L6- | Phaser 48dB + Low 6dB, negative |
| 66 | Phs 48H6+ | Phaser 48dB + High 6dB, positive |
| 67 | Phs 48H6- | Phaser 48dB + High 6dB, negative |
| 68 | Phs 48HL6+ | Phaser 48dB + High/Low 6dB, positive |
| 69 | Phs 48HL6- | Phaser 48dB + High/Low 6dB, negative |
| 70 | FPhs 12HL6+ | Formant Phaser 12dB + High/Low 6dB, positive |
| 71 | FPhs 12HL6- | Formant Phaser 12dB + High/Low 6dB, negative |

**Verification method:** Dropdown submenu (32 items directly visible on screen without scrolling); confirmed EXACT via keyboard wraparound test (Down key from FPhs 12HL6- wraps to Cmb+, confirming this is the complete cyclical list).

---

## CATEGORY 4: Misc (25 types — EXACT)

Unique Serum-specific processors (EQ, ring mod, reverb, formant, comb variants).

| # | Exact UI Label | Type |
|---|---|---|
| 72 | Low EQ 6 | Low shelf EQ, 6dB |
| 73 | Low EQ 12 | Low shelf EQ, 12dB |
| 74 | Band EQ 12 | Band EQ, 12dB |
| 75 | High EQ 6 | High shelf EQ, 6dB |
| 76 | High EQ 12 | High shelf EQ, 12dB |
| 77 | Ring Mod | Ring modulator |
| 78 | Ring Mod2 | Ring modulator, variant 2 |
| 79 | SampHold | Sample & Hold |
| 80 | SampHold- | Sample & Hold, negative/inverted |
| 81 | Combs | Comb filter (Misc variant) |
| 82 | Allpasses | All-pass filter |
| 83 | Reverb | Reverb |
| 84 | French LP | French-style low pass |
| 85 | German LP | German-style low pass |
| 86 | Add Bass | Bass enhancement |
| 87 | Formant-I | Formant filter, variant I |
| 88 | Formant-II | Formant filter, variant II |
| 89 | Formant-III | Formant filter, variant III |
| 90 | Bandreject | Band-reject filter |
| 91 | Dist.Comb 1 LP | Distorted Comb 1, Low Pass |
| 92 | Dist.Comb 1 BP | Distorted Comb 1, Band Pass |
| 93 | Dist.Comb 2 LP | Distorted Comb 2, Low Pass |
| 94 | Dist.Comb 2 BP | Distorted Comb 2, Band Pass |
| 95 | Scream LP | Scream distortion, Low Pass |
| 96 | Scream BP | Scream distortion, Band Pass |

**Verification method:** Dropdown submenu (25 items directly visible on screen); boundary confirmed via step-forward test (Scream BP → steps directly to Wsp, the first S2 Filters item, with NO additional Misc items between).

---

## CATEGORY 5: S2 Filters (11 types — EXACT)

New Serum 2 filter types — saturating, nonlinear resonance (hardware-emulation style).

| # | Exact UI Label | Type |
|---|---|---|
| 97 | Wsp | Warp/Wasp-style filter |
| 98 | DJ Mixer | DJ mixer-style filter (isolator-like) |
| 99 | Diffusor | Diffusion-based filter |
| 100 | MG Ladder | Moog Ladder filter emulation |
| 101 | Acid Ladder | Acid-style ladder filter |
| 102 | EMS Ladder | EMS synthesizer ladder filter emulation |
| 103 | MG Dirty | Moog "Dirty" (saturated) filter |
| 104 | PZ SVF | Pole-Zero State Variable Filter |
| 105 | Comb 2 | Comb filter, S2 variant |
| 106 | Exp MM | Experimental Multi-Mode |
| 107 | Exp BPF | Experimental Band Pass Filter |

**Verification method:** Full dropdown submenu directly visible in single screenshot (all 11 items, no scrolling needed). CONFIRMED as the absolute LAST category: stepping forward from "Exp BPF" wraps back to "MG Low 6" (first item of Normal category), proving this is the definitive end of the entire 107-type universe.

---

## Verification Chain Summary

1. **Normal (18):** Full dropdown screenshot — direct count
2. **Multi (21):** Full dropdown screenshot — direct count, scroll-tested for completeness
3. **Flanges (32):** Full dropdown screenshot — direct count, keyboard-wraparound verified
4. **Misc (25):** Full dropdown screenshot showed 25 visible; step-arrow test confirmed transition directly to S2 Filters with no gap
5. **S2 Filters (11):** Full dropdown screenshot — direct count; step-arrow wraparound confirmed as absolute last category (Exp BPF → MG Low 6)

**Cross-validation:** The step-arrow method independently traversed Misc→S2Filters boundary (Scream BP → Wsp → ... → Exp BPF) and the wraparound (Exp BPF → MG Low 6), which is fully consistent with the dropdown-observed category contents. Both methods agree.

---

## Next Phase: Control Surface Audit

With the type universe now EXACTLY enumerated (107 types, 5 categories), the next phase is:

1. Audit control surface for ONE representative type per family (e.g., MG Low 12 represents MG Low 6/18/24)
2. Verify slope/polarity variants share identical control surface (differ only in filter curve shape, not available controls)
3. Flag any type that visually/structurally differs from its family's representative
4. Build normalized semantic control matrix with full applicability lists
5. Compare Filter 1 vs Filter 2 (targeted — only check for differences, not full re-audit)
6. Reconcile technical VST3 fields against semantic controls
7. Reconcile targets.py and operations coverage separately

---

**Authority:** Direct Serum 2.0.21 UI inspection, 2026-09-15  
**Version Lock:** Serum 2.0.21  
**Confidence:** HIGH — cross-validated via two independent methods (dropdown full-list view + step-arrow sequential traversal with wraparound closure proof)
