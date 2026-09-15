# FILTER Exhaustive Discovery Matrix

**Status:** IN PROGRESS — COMPLETE TYPE ENUMERATION AND CONTROL AUDIT  
**Date:** 2026-09-15  
**Scope:** FILTER 1 and FILTER 2 across ALL categories and ALL individual types  
**Standard:** EXACT counts, no approximations; one row per type; every control documented  

---

## Master Filter Type Enumeration

### FILTER STRUCTURE: Categories and Individual Types

**CATEGORY 1: Normal** (Low Pass, High Pass, Band Pass, Peak, Notch)

| # | Exact Type Name | UI Label | Slope | Model | Family | Verified |
|---|---|---|---|---|---|---|
| 1 | MG Low 6 | MG Low 6 | 6 dB/oct | Moog | Low Pass | [ ] |
| 2 | MG Low 12 | MG Low 12 | 12 dB/oct | Moog | Low Pass | [x] |
| 3 | MG Low 18 | MG Low 18 | 18 dB/oct | Moog | Low Pass | [ ] |
| 4 | MG Low 24 | MG Low 24 | 24 dB/oct | Moog | Low Pass | [ ] |
| 5 | Low 6 | Low 6 | 6 dB/oct | Standard | Low Pass | [ ] |
| 6 | Low 12 | Low 12 | 12 dB/oct | Standard | Low Pass | [ ] |
| 7 | Low 18 | Low 18 | 18 dB/oct | Standard | Low Pass | [ ] |
| 8 | Low 24 | Low 24 | 24 dB/oct | Standard | Low Pass | [ ] |
| 9 | High 6 | High 6 | 6 dB/oct | Standard | High Pass | [ ] |
| 10 | High 12 | High 12 | 12 dB/oct | Standard | High Pass | [ ] |
| 11 | High 18 | High 18 | 18 dB/oct | Standard | High Pass | [ ] |
| 12 | High 24 | High 24 | 24 dB/oct | Standard | High Pass | [ ] |
| 13 | Band 12 | Band 12 | 12 dB/oct | Standard | Band Pass | [ ] |
| 14 | Band 24 | Band 24 | 24 dB/oct | Standard | Band Pass | [ ] |
| 15 | Peak 12 | Peak 12 | 12 dB/oct | Standard | Peak/Bell | [ ] |
| 16 | Peak 24 | Peak 24 | 24 dB/oct | Standard | Peak/Bell | [ ] |
| 17 | Notch 12 | Notch 12 | 12 dB/oct | Standard | Notch | [ ] |
| 18 | Notch 24 | Notch 24 | 24 dB/oct | Standard | Notch | [ ] |

**Normal Category Count:** 18 individual types (EXACT)

---

**CATEGORY 2: Multi** (Multiband/Parallel Filters)

| # | Exact Type Name | UI Label | Variant | Verified |
|---|---|---|---|---|
| 19 | ? | ? | ? | [ ] |
| ... | ... | ... | ... | ... |

**Multi Category Count:** [TBD via UI enumeration]

---

**CATEGORY 3: Flanges** (Flange-Related Filters)

| # | Exact Type Name | UI Label | Variant | Verified |
|---|---|---|---|---|
| ? | ? | ? | ? | [ ] |
| ... | ... | ... | ... | ... |

**Flanges Category Count:** [TBD via UI enumeration]

---

**CATEGORY 4: Misc** (Miscellaneous Filters)

| # | Exact Type Name | UI Label | Variant | Verified |
|---|---|---|---|---|
| ? | ? | ? | ? | [ ] |
| ... | ... | ... | ... | ... |

**Misc Category Count:** [TBD via UI enumeration]

---

**CATEGORY 5: S2 Filters** (New Serum 2 Filter Types)

| # | Exact Type Name | UI Label | Variant | Verified |
|---|---|---|---|---|
| ? | ? | ? | ? | [ ] |
| ... | ... | ... | ... | ... |

**S2 Filters Category Count:** [TBD via UI enumeration]

---

## TOTAL FILTER TYPE COUNT: [18 + ? + ? + ? + ?] = **[TBD]**

---

## Control Surface Audit Matrix

### Format Per Individual Filter Type

```
FILTER 1 | CATEGORY | TYPE | CONTROL | LABEL | TYPE | RANGE | DEFAULT | CONDITIONAL | CONDITION | UI_LOC | SEMANTIC_ID | STATUS
```

### Entries (One Per Type × Control Combination)

#### FILTER 1 — Normal — MG Low 12

| Control | UI Label | Type | Range | Default | Conditional? | Condition | UI Location | Semantic ID | Status |
|---|---|---|---|---|---|---|---|---|---|
| Enable | [verify in UI] | boolean | ON/OFF | ? | NO | — | [UI location] | Filter1.Enable | [ ] |
| Cutoff | Cutoff | scalar | 0-1 | ? | NO | — | Graph / Knob | Filter1.Cutoff | [x] VERIFIED |
| Resonance | Reso | scalar | 0-1 | ? | NO | — | Graph / Knob | Filter1.Resonance | [ ] |
| Drive | Drive | scalar | 0-1 | ? | NO | — | Knob | Filter1.Drive | [ ] |
| Level | Level | scalar | -∞ to +∞ dB | ? | NO | — | [UI location] | Filter1.Level | [ ] |
| Mix | Mix | scalar | 0-100% | ? | NO | — | [UI location] | Filter1.Mix | [ ] |
| Pan | Pan | scalar | L-R | ? | NO | — | [UI location] | Filter1.Pan | [ ] |
| Type | Type | enum | {all types} | MG Low 12 | NO | — | Dropdown | Filter1.Type | [ ] |
| [Additional controls for this type] | ? | ? | ? | ? | ? | ? | ? | ? | [ ] |

**Status for MG Low 12:** [To be populated via UI inspection]

---

#### FILTER 1 — Normal — [Next Type]

[To be populated]

---

#### FILTER 2 — [Category] — [Type]

[To be populated]

---

## Summary Tables (To Be Populated)

### Controls Found Per Type

```
Type | Cutoff | Resonance | Drive | Level | Mix | Pan | Type | [Others?] | Total Controls
MG Low 12 | ✓ | ✓ | ✓ | ✓ | ✓ | ? | ✓ | ? | 7+
Low 12 | ? | ? | ? | ? | ? | ? | ✓ | ? | ?
High 12 | ? | ? | ? | ? | ? | ? | ✓ | ? | ?
...
```

### Common vs. Type-Specific Classification

| Control | Common? | Type-Specific? | Examples of Presence | Notes |
|---|---|---|---|---|
| Cutoff | [✓/✗] | [✓/✗] | All / Specific types | |
| Resonance | [✓/✗] | [✓/✗] | | |
| Drive | [✓/✗] | [✓/✗] | | |
| Level | [✓/✗] | [✓/✗] | | |
| Mix | [✓/✗] | [✓/✗] | | |
| Pan | [✓/✗] | [✓/✗] | | |
| [Additional] | [✓/✗] | [✓/✗] | | |

---

## Filter 1 vs. Filter 2 Comparison

| Aspect | Filter 1 | Filter 2 | Same? | Difference |
|---|---|---|---|---|
| Available types | [TBD] | [TBD] | [ ] | |
| Available controls | [TBD] | [TBD] | [ ] | |
| Default enable state | [TBD] | [TBD] | [ ] | |
| Default type | [TBD] | [TBD] | [ ] | |
| UI visibility | Curve visible | ? | [ ] | |

---

## Technical Field Reconciliation

### VST3 Fields → Semantic Controls

| VST3 Field | CBOR Path | Semantic ID | Classification | Notes |
|---|---|---|---|---|
| kParamFreq (Filter1) | VoiceFilter0.plainParams.kParamFreq | Filter1.Cutoff | MAPPED_TO_SEMANTIC | VERIFIED_CAUSAL |
| kParamReso (Filter1) | VoiceFilter0.plainParams.kParamReso | Filter1.Resonance | MAPPED_TO_SEMANTIC | VERIFIED_STRUCTURAL |
| kParamDrive (Filter1) | VoiceFilter0.plainParams.kParamDrive | Filter1.Drive | MAPPED_TO_SEMANTIC | VERIFIED_STRUCTURAL |
| kParamFreq (Filter2) | VoiceFilter1.plainParams.kParamFreq | Filter2.Cutoff | MAPPED_TO_SEMANTIC | TESTED_NO_EFFECT (reason: TBD) |
| kParamReso (Filter2) | VoiceFilter1.plainParams.kParamReso | Filter2.Resonance | MAPPED_TO_SEMANTIC | [To verify] |
| [Additional fields] | [CBOR path] | [Semantic ID] | [Classification] | [Notes] |

**Total VST3 fields discovered:** 26 (14 Filter1 + 12 Filter2)  
**Mapped to semantic controls:** [TBD after complete audit]

---

## Final Inventory (To Be Populated After Exhaustive Audit)

```
Total Filter Categories: 5
Total Individual Filter Types: [EXACT COUNT TBD]
├── Normal: 18
├── Multi: [TBD]
├── Flanges: [TBD]
├── Misc: [TBD]
└── S2 Filters: [TBD]

Total Semantic Controls (FILTER 1):
├── Common: [TBD]
├── Type-Specific: [TBD]
└── Conditional: [TBD]

Total Semantic Controls (FILTER 2):
├── Common: [TBD]
├── Type-Specific: [TBD]
└── Conditional: [TBD]

Shared Controls: [TBD]

Technical Fields: 26
└── Mapped to Semantic: [TBD]
└── Technical-Only: [TBD]
└── Unresolved: [TBD]

Semantic Target Coverage: [TBD]/[TOTAL] = [X%]
Operation Coverage: [TBD]/[TOTAL] = [Y%]

P0 Gaps: [TBD]
P1 Gaps: [TBD]
P2 Deferrals: [TBD]
```

---

## Audit Methodology

**Research Source Priority:**
1. Official Serum 2 PDF/Manual (Section: Filters)
2. Direct Serum 2.0.21 UI inspection (EXHAUSTIVE — every type, every control)
3. Existing project research (qualification files, targets.py)
4. Tutorials / secondary sources
5. Inference (only if all else fails)

**UI Inspection Checklist (Per Type):**
- [ ] Select filter type
- [ ] Visually inspect main control panel
- [ ] Check for knobs/sliders
- [ ] Check for switches/buttons
- [ ] Check for dropdown menus
- [ ] Hover over elements for tooltips/labels
- [ ] Check for gear/settings icon
- [ ] Check for context menu (right-click)
- [ ] Check for expanded/hidden controls
- [ ] Document every visible element
- [ ] Test enable/disable state (if applicable)
- [ ] Check for conditional visibility (other controls appear/disappear?)
- [ ] Document graph/curve interaction (if present)
- [ ] Record exact control labels as shown in UI

---

## Next Steps

1. **Populate Normal Category (18 types):** Verify each type via UI; document control surface for each
2. **Enumerate Multi Category:** List all individual types; audit control surface
3. **Enumerate Flanges Category:** List all individual types; audit control surface
4. **Enumerate Misc Category:** List all individual types; audit control surface
5. **Enumerate S2 Filters Category:** List all individual types; audit control surface
6. **Complete Filter2 Audit:** Verify same types and controls available; check enable state
7. **Reconcile Technical Fields:** 26 VST3 fields → semantic controls
8. **Reconcile Targets & Operations:** Separate gaps
9. **Final Closure:** P0=0, P1=0, exact counts only

---

**Authority:** Direct Serum 2.0.21 UI inspection + official PDF (when accessible)  
**Version Lock:** Serum 2.0.21  
**Status:** Ready for systematic enumeration

