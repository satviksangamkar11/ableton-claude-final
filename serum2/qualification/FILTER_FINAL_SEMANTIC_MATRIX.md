# FILTER Final Semantic Matrix — Normalized Control Identity

**Date:** 2026-09-15  
**Status:** Phase 3 COMPLETE — Semantic normalization with full applicability  
**Authority:** Built from 107/107 individually-verified filter types (FILTER_CONTROL_SURFACE_AUDIT_PROGRESS.md)

---

## Common Controls (Apply to ALL 107 types × both filters)

These 6 controls form the fixed skeleton present on every single filter type:

| Semantic ID | UI Label | Control Type | Applicability | Classification |
|---|---|---|---|---|
| Filter{N}.Cutoff | Cutoff | scalar | ALL 107 types | COMMON_FILTER_CONTROL |
| Filter{N}.Resonance | Res | scalar | ALL 107 types | COMMON_FILTER_CONTROL |
| Filter{N}.Drive | Drive | scalar | ALL 107 types | COMMON_FILTER_CONTROL |
| Filter{N}.Pan | Pan | scalar | ALL 107 types | COMMON_FILTER_CONTROL |
| Filter{N}.Mix | Mix | scalar | ALL 107 types | COMMON_FILTER_CONTROL |
| Filter{N}.Level | Level | scalar | ALL 107 types | COMMON_FILTER_CONTROL |

Where {N} = 1 or 2 (Filter1 or Filter2). These 6 controls × 2 filters = **12 semantic control instances**, but normalize to **6 semantic control identities** (since the identity is shared, only the filter-instance context differs).

---

## Type-Specific 4th-Knob Controls (21 distinct semantic identities)

The 4th knob position carries genuinely distinct semantic meaning depending on filter type. Each identity below is a **separate semantic control** with an explicit applicability list.

### 1. Filter{N}.Fat — "FAT"
**Applicability (14 types):** MG Low 6/12/18/24, High 12/18/24, Band 12/24, Peak 12/24, Notch 12/24  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Normal

### 2. Filter{N}.Freq2 — "FREQ" (secondary morph frequency)
**Applicability (13 types):** All 2-way Multi morphs — LH6, LH12, LB12, LP12, LN12, HB12, HP12, HN12, BP12, BN12, PP12, PN12, NN12  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Multi

### 3. Filter{N}.Morph — "MORPH"
**Applicability (9 types):** All 8 three-way Multi morphs (L/B/H 12/24, L/P/H 12/24, L/N/H 12/24, B/P/N 12/24) + Wsp (S2 Filters)  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Multi, S2 Filters

### 4. Filter{N}.Smooth — "SMOOTH"
**Applicability (4 types):** MG Ladder, Acid Ladder, EMS Ladder, PZ SVF  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** S2 Filters

### 5. Filter{N}.LPFreq — "LP FRQ"
**Applicability (6 types):** Cmb L6+/-, Flg L6+/-, Phs 48L6+/-  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Flanges

### 6. Filter{N}.HPFreq — "HP FRQ"
**Applicability (6 types):** Cmb H6+/-, Flg H6+/-, Phs 48H6+/-  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Flanges

### 7. Filter{N}.HLWidth — "HL WID"
**Applicability (8 types):** Cmb HL6+/-, Flg HL6+/-, Phs 48HL6+/-, FPhs 12HL6+/-  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Flanges

### 8. Filter{N}.GainDB — "DB +/-"
**Applicability (5 types):** Low EQ 6/12, Band EQ 12, High EQ 6/12  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Misc

### 9. Filter{N}.Damp — "DAMP"
**Applicability (3 types):** Combs, Allpasses, Reverb  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Misc

### 10. Filter{N}.Formant — "FORMNT"
**Applicability (3 types):** Formant-I, Formant-II, Formant-III  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Misc

### 11. Filter{N}.CombFreq — "COMBFRQ"
**Applicability (4 types):** Dist.Comb 1 LP, Dist.Comb 1 BP, Dist.Comb 2 LP, Dist.Comb 2 BP  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Misc

### 12. Filter{N}.ScreamAmt — "SCREAM"
**Applicability (2 types):** Scream LP, Scream BP  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Misc

### 13. Filter{N}.Spread — "SPREAD"
**Applicability (1 type):** Ring Modx2  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Misc

### 14. Filter{N}.Stages — "STAGES"
**Applicability (1 type):** Diffusor  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** S2 Filters

### 15. Filter{N}.Pain — "PAIN"
**Applicability (1 type):** MG Dirty  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** S2 Filters

### 16. Filter{N}.Boeuf — "BOEUF"
**Applicability (1 type):** French LP  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Misc

### 17. Filter{N}.Thru — "THRU"
**Applicability (1 type):** Add Bass  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Misc

### 18. Filter{N}.Width — "WIDTH"
**Applicability (1 type):** Bandreject  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** Misc

### 19. Filter{N}.Freq2Comb — "FRQ2"
**Applicability (1 type):** Comb 2  
**Classification:** TYPE_SPECIFIC_CONTROL  
**Category:** S2 Filters

### 20. Filter{N}.MixAlt — "MIX" (duplicate label vs. common Mix control)
**Applicability (1 type):** Exp MM  
**Classification:** TYPE_SPECIFIC_CONTROL — AMBIGUOUS LABEL, requires CBOR path disambiguation to avoid collision with Filter{N}.Mix  
**Category:** S2 Filters  
**⚠️ NOTE:** This is a genuine naming collision in the Serum UI itself (both the common Mix knob and this type-specific knob show "MIX"). Semantic ID must disambiguate; UI label alone is insufficient for this one type.

### 21. (No 4th knob) — DISABLED
**Applicability (25 types):** Low 6/12/18/24, High 6, Cmb+/-, Flg+/-, Phs 12/24/36/48 +/- (8), DJ Mixer, Exp BPF, Ring Mod, SampHold, SampHold-, German LP  
**Classification:** DISPLAY_ONLY / NOT_APPLICABLE (no user-facing 4th control for this type; knob is present in UI but non-functional/unlabeled)

---

## Structural Controls (Apply across FILTER section, not per-type)

| Control | UI Location | Classification | Notes |
|---|---|---|---|
| Filter{N}.Enable | Circle icon before "FILTER N" label | STRUCTURAL_CONTROL | On/off toggle; confirmed via context-prerequisite evidence in all qualification experiments |
| Filter{N}.Type | Type dropdown + step-arrows | STRUCTURAL_CONTROL | Selects among 107 types; has its own semantic identity distinct from per-type controls |
| Filter{N}.Mute | "M" button next to FILTER{N} tab | STRUCTURAL_CONTROL | Distinct from Enable; needs behavioral verification (post-closure) |
| Filter{N}.RouteSub | "S" button in routing row | STRUCTURAL_CONTROL | Routes Sub oscillator into this filter |
| Filter{N}.RouteOscA | "A" button in routing row | STRUCTURAL_CONTROL | Routes OSC A into this filter |
| Filter{N}.RouteOscB | "B" button in routing row | STRUCTURAL_CONTROL | Routes OSC B into this filter |
| Filter{N}.RouteOscC | "C" button in routing row | STRUCTURAL_CONTROL | Routes OSC C into this filter |
| Filter{N}.RouteNoise | "N" button in routing row | STRUCTURAL_CONTROL | Routes Noise into this filter |
| Filter{N}.GridIcon | Grid icon next to routing row | UNRESOLVED | Function not yet determined (possibly pattern/matrix view toggle) |
| Filter{N}.BUS1Send | (existing target: routing_slot5/6_bus1_level) | STRUCTURAL_CONTROL | Already in targets.py; FILTER-triggered, MIX-owned destination |
| Filter{N}.BUS2Send | (existing target: routing_slot5/6_bus2_level) | STRUCTURAL_CONTROL | Already in targets.py |
| Filter{N}.Route | (existing target: routing_slot5/6_dest) | STRUCTURAL_CONTROL | Already in targets.py |
| Reset Control (per-knob) | Right-click context menu | STRUCTURAL_ACTION | Confirmed via right-click on Cutoff knob; generic across all knobs |
| MIDI Learn (per-knob) | Right-click context menu | STRUCTURAL_ACTION | Confirmed |
| Lock Parameter (per-knob) | Right-click context menu | STRUCTURAL_ACTION | Confirmed |
| Mod Source (per-knob) | Right-click context menu | STRUCTURAL_ACTION | Matrix assignment submenu |
| Bypass Modulator (per-knob) | Right-click context menu | STRUCTURAL_ACTION | Confirmed |
| Remove Modulator / Remove All Modulators | Right-click context menu | STRUCTURAL_ACTION | Confirmed |

---

## Conditional Controls Summary

Every type-specific 4th-knob control (items 1-20 above) is inherently **conditional** — it appears/has meaning ONLY when its applicable filter type(s) are selected. When any other type is selected, that specific 4th-knob semantic does not apply (the physical knob may show DISABLED or a different type's label instead).

**Condition:** `Filter{N}.Type == <applicable type from list>`

This is the single conditional-control rule governing all 20 type-specific 4th-knob identities.

---

## Total Semantic Control Count (EXACT)

```
Common controls (apply to all 107 types):        6  (Cutoff, Resonance, Drive, Pan, Mix, Level)
Type-specific 4th-knob controls (distinct IDs): 20  (Fat, Freq2, Morph, Smooth, LPFreq, HPFreq,
                                                       HLWidth, GainDB, Damp, Formant, CombFreq,
                                                       ScreamAmt, Spread, Stages, Pain, Boeuf,
                                                       Thru, Width, Freq2Comb, MixAlt)
Structural controls:                             9  (Enable, Type, Mute, RouteSub, RouteOscA,
                                                       RouteOscB, RouteOscC, RouteNoise, GridIcon[unresolved])
Existing routing targets (already in targets.py): 3  (BUS1Send, BUS2Send, Route)
Structural actions (generic, per-knob):           6  (Reset, MIDI Learn, Lock, Mod Source,
                                                       Bypass Modulator, Remove [All] Modulators)
-----------------------------------------------------
TOTAL DISTINCT SEMANTIC CONTROLS (per filter):   44
TOTAL ACROSS FILTER1 + FILTER2:                  88  (44 × 2, since each filter instance
                                                        has its own control values)
```

**Note on counting convention:** Semantic control IDENTITIES (the 44 number) represent unique control types. Since Filter1 and Filter2 are separate instances with independent state, the full semantic inventory requires 44 × 2 = 88 concrete semantic targets (Filter1.Cutoff, Filter2.Cutoff, etc.), consistent with existing targets.py naming convention (FILTER1.X / FILTER2.X).

---

## Classification Summary (Exact)

```
COMMON_FILTER_CONTROL:     6   (Cutoff, Resonance, Drive, Pan, Mix, Level)
TYPE_SPECIFIC_CONTROL:    20   (the 20 distinct 4th-knob identities)
STRUCTURAL_CONTROL:        9   (Enable, Type, Mute, 5x Routing, GridIcon)
STRUCTURAL_CONTROL (existing targets): 3  (BUS1Send, BUS2Send, Route)
STRUCTURAL_ACTION:         6   (Reset, MIDI Learn, Lock, ModSource, BypassMod, RemoveMod)
CONDITIONAL_CONTROL:       20  (all type-specific controls ARE conditional; not a separate count,
                                 cross-referenced with TYPE_SPECIFIC_CONTROL above)
DISPLAY_ONLY:               1  ("DISABLED" 4th-knob state across 25 types — not a control,
                                 the absence of one)
UNRESOLVED:                 1  (GridIcon function)
```

---

## Next Steps

1. **Technical field reconciliation** (Phase 5): Map 26 known VST3 fields (14 Filter1 + 12 Filter2) to this semantic matrix; resolve the 14-vs-12 discrepancy
2. **Target/operation gap analysis** (Phase 6): Compare this 44-control semantic matrix against existing targets.py entries; identify exact gaps
3. **P0/P1/P2 closure gate assessment**
4. **Update SERUM2_SEMANTIC_INVENTORY.json** with the canonical semantic record
5. **Final FILTER closure report** with exact numbers per the user's required format

---

Generated: 2026-09-15  
Authority: 107/107 individually-verified filter types (Direct Serum 2.0.21 UI inspection)
