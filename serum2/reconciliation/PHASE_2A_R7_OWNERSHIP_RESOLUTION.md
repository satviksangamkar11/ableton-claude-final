# Phase 2A-R.7: Ownership Resolution for 11 Flagged Enable/Level/Pan Records

**Date**: 2026-09-16  
**Method**: Internal VST3 field name comparison — not inference from label similarity.

---

## The Decisive Evidence

MIXER's own pre-existing records already captured direct right-click tooltip text during their original discovery. That tooltip text **is the internal Serum parameter name** — and it matches the raw VST3 census field names exactly:

| Record | Tooltip captured (MIXER source, pre-existing) | VST3 census field name (independent source) |
|---|---|---|
| `MIXER.OSC_A.ENABLE` | *"A Enable"* | `A Enable` (idx 20) |
| `MIXER.OSC_A.LEVEL` | *"A Level"* | `A Level` (idx 21) |
| `MIXER.OSC_A.PAN` | *"A Pan"* | `A Pan` (idx 22) |
| `MIXER.NOISE.ENABLE` | *"Noise Enable"* | `Noise Enable` (idx 185) |
| `MIXER.SUB.ENABLE` | *"Sub Osc Enable"* | `Sub Enable` (idx 193) — near-exact, one extra word |

Two **independently sourced** pieces of evidence (a live-UI right-click tooltip captured in one closure pass, and a separate VST3 host-parameter census captured in a different pass) agree on the internal parameter name. This is technical identity evidence, not semantic-label inference — exactly the standard the FILTER case set and that this determination required.

---

## Determination: ONE_SEMANTIC_MULTIPLE_UI_SURFACES (11 of 11)

| Candidate | Canonical (MIXER) | Evidence strength |
|---|---|---|
| `OSC1.ENABLE/LEVEL/PAN` | `MIXER.OSC_A.*` | EXACT — directly right-clicked |
| `OSC2.ENABLE/LEVEL/PAN` | `MIXER.OSC_B.*` | STRUCTURAL — MIXER's own source admits B/C weren't independently right-clicked, generalized from OSC_A's layout. Honestly labeled as such, not claimed as EXACT. |
| `OSC3.ENABLE/LEVEL/PAN` | `MIXER.OSC_C.*` | STRUCTURAL (same caveat) |
| `SUB_OSC.ENABLE` | `MIXER.SUB.ENABLE` | NEAR-EXACT (tooltip has one extra word, same VST3 index) |
| `NOISE_OSC.ENABLE` | `MIXER.NOISE.ENABLE` | EXACT |

All 11 resolved the same direction. None were UNRESOLVED, none were SEPARATE_SEMANTIC_ID — the evidence was consistent across every case.

---

## Resolution Action

The 11 panel-side candidate records (created in Phase 2A-R.5/R.6) were **retracted**, not merged/renamed — they never should have been counted as new. The 11 MIXER records remain canonical, each now annotated with:
- An explicit cross-reference to the retracted candidate id (audit trail — nothing silently disappears)
- A notes-field explanation of the resolution evidence and verdict

This differs from the FILTER case (Phase 2A-R.4), where the *new* FILTER-owned records were created because MIXER's `GRAPHIC_CUTOFF_RESONANCE` explicitly stated FILTER was the primary owner and MIXER the secondary surface. Here, the evidence points the opposite way: MIXER's Enable/Level/Pan carry the direct verification; the OSC-panel candidates were speculative constructions from VST3 field names alone, with no independent UI confirmation.

---

## Result

```
839  (post-SUB/NOISE completeness)
-11  retracted (confirmed duplicates via internal VST3 name matching)
────
828  current evidence-derived union
```

---

## Updated Phase State

```
PHASE 2A-R.6  SUB/NOISE completeness                 ✅ COMPLETE (839)
PHASE 2A-R.7  Ownership resolution (11 flagged)       ✅ COMPLETE (828, all ONE_SEMANTIC_MULTIPLE_UI_SURFACES)
PHASE 2A-R.8  MATRIX.SOURCE atomization               ⏳ NEXT (kept separate, not mixed into OSC accounting)

PHASE 2C+                                             🚫 still blocked
```

---

**Status**: 828 is the current machine-verified union, with the largest identified ownership ambiguity fully resolved using cross-source technical evidence. MATRIX.SOURCE gap (Envelopes/LFOs listed in menu enumeration but not atomized) remains the last known open item before a freeze can be considered.
