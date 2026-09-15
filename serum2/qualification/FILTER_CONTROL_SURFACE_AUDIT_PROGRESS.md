# FILTER Control Surface Audit — Progress Report

**Date:** 2026-09-15  
**Status:** PHASE 2 IN PROGRESS — Critical pattern discovered, exhaustive per-type audit ongoing  
**Phase 1 status:** ✅ COMPLETE (107 types exactly enumerated — see FILTER_TYPE_COMPLETE_ENUMERATION.md)

---

## Critical Discovery: Control Surface Template

Every filter type (across all 107) shares this fixed physical layout:

```
[Type Selector: dropdown + step-arrows]
[Filter Response Graph: draggable curve]
[Routing row: S | A | B | C | N | grid-icon]
[Knob grid:]
  CUTOFF    | PAN
  RES       | (Pan continues)
  DRIVE     | MIX
  [4TH-KNOB]| LEVEL (vertical fader)
```

**7 slots always present:** Cutoff, Res, Drive, [4th-knob — VARIES], Pan, Mix, Level  
**Routing row:** S/A/B/C/N (Sub/OscA/OscB/OscC/Noise — which sources feed this filter)  
**Structural:** Enable toggle (circle icon before "FILTER 1" label), M (mute) button, grid icon (function TBD)

---

## CRITICAL FINDING: The 4th Knob Is Type-Specific

This is NOT a fixed "FAT" knob as initially assumed from Normal-category evidence. Direct verification across categories shows **at least 7 distinct 4th-knob identities**:

| Type Checked | Category | 4th Knob Label | Notes |
|---|---|---|---|
| MG Low 6/12/18/24, Low X, High X, Band X, Peak X, Notch X | Normal | **FAT** | Verified on MG Low 6/12 |
| LH 6, BP 12 (2-way morphs) | Multi | **FREQ** | Verified on 2 of 13 two-way types |
| L/B/H 12 (3-way morph) | Multi | **MORPH** | Verified on 1 of 8 three-way types |
| Cmb + | Flanges (Comb) | **DISABLED** (blank) | Verified |
| Flg + | Flanges (Flange) | **DISABLED** (blank) | Verified |
| Phs 12+ | Flanges (Phaser) | **DISABLED** (blank) | Verified |
| Low EQ 6 | Misc (EQ) | **DB +/-** | Verified |
| Ring Mod | Misc (RingMod) | **DISABLED** (blank) | Verified — graph also changes to waveform display |
| Ring Modx2 | Misc (RingMod2) | **SPREAD** | Verified — differs from Ring Mod despite same family name |
| SampHold | Misc (S&H) | **DISABLED** (blank) | Verified |
| MG Ladder | S2 Filters | **SMOOTH** | Verified |

**Implication:** The 4th knob CANNOT be assumed constant even within a named family (Ring Mod vs Ring Modx2 differ). Every individual type requires verification per the user's Phase 2 mandate: "Do not assume two types have identical controls because their panels initially look similar."

---

## Verified vs. Remaining (107 types total)

### Directly Verified (11 of 107 = 10.3%)
1. MG Low 6 — FAT (Normal)
2. MG Low 12 — FAT (Normal)
3. LH 6 — FREQ (Multi, 2-way)
4. BP 12 — FREQ (Multi, 2-way)
5. L/B/H 12 — MORPH (Multi, 3-way)
6. Cmb + — DISABLED (Flanges, Comb)
7. Flg + — DISABLED (Flanges, Flange)
8. Phs 12+ — DISABLED (Flanges, Phaser)
9. Low EQ 6 — DB+/- (Misc, EQ)
10. Ring Mod — DISABLED (Misc, RingMod) [distinct graph type: waveform, not filter curve]
11. Ring Modx2 — SPREAD (Misc, RingMod2)
12. SampHold — DISABLED (Misc, S&H)
13. MG Ladder — SMOOTH (S2 Filters, Ladder)

(13 verified, correcting count above)

### Remaining to verify (94 of 107 = 87.9%)

**Normal (16 remaining):** MG Low 18/24, Low 6/12/18/24, High 6/12/18/24, Band 12/24, Peak 12/24, Notch 12/24
- Hypothesis: FAT (same family as MG Low, all single-mode standard filters)
- Risk: LOW — these are pure slope/model variants of the same basic filter algorithm

**Multi (19 remaining):** LH 12, LB 12, LP 12, LN 12, HB 12, HP 12, HN 12, BN 12, PP 12, PN 12, NN 12 (2-way); L/B/H 24, L/P/H 12/24, L/N/H 12/24, B/P/N 12/24 (3-way)
- Hypothesis: 2-way→FREQ, 3-way→MORPH (pattern consistent across 3 verified samples)
- Risk: LOW-MEDIUM — need at least 1 more 3-way check to increase confidence

**Flanges (29 remaining):** All Cmb/Flg/Phs variants (polarity ±, slope L6/H6/HL6/12/24/36/48), FPhs
- Hypothesis: DISABLED (consistent across Comb/Flange/Phaser representatives)
- Risk: LOW — FPhs (Formant Phaser) not yet checked, may differ

**Misc (20 remaining):** Band EQ 12, High EQ 6/12 (EQ family); Combs, Allpasses, Reverb, French LP, German LP, Add Bass, Formant-I/II/III, Bandreject, Dist.Comb 1/2 LP/BP, Scream LP/BP
- Hypothesis: UNRELIABLE — Misc has proven to be the most heterogeneous category (EQ→DB+/-, RingMod→DISABLED, RingModx2→SPREAD, SampHold→DISABLED all within "similar-sounding" families)
- Risk: HIGH — every remaining Misc type needs individual verification; no safe inference

**S2 Filters (9 remaining):** Wsp, DJ Mixer, Diffusor, Acid Ladder, EMS Ladder, MG Dirty, PZ SVF, Comb 2, Exp MM, Exp BPF
- Hypothesis: Ladder-family (Acid Ladder, EMS Ladder, MG Dirty) may share SMOOTH with MG Ladder; others (Wsp, DJ Mixer, Diffusor, PZ SVF, Comb 2, Exp MM, Exp BPF) are structurally distinct and need individual checks
- Risk: HIGH — this is a small category (11 total) where full verification is feasible and required

---

## Tooling Note (for continuation)

UI interaction has significant reliability challenges in this Serum 2/Ableton session:
- Direct clicks on the type-selector dropdown/step-arrows require a "move mouse away, wait, click" pattern to reliably register (VST plugin debounce behavior)
- Approximately 40-50% of click attempts on the step-arrow require a retry
- Dropdown submenus for large categories (Flanges: 32 items, Misc: 25 items) render fully in one screenshot without needing scroll, EXCEPT when items would exceed screen height — verified boundary transitions (Misc→S2Filters, S2Filters→Normal wraparound) via sequential stepping

---

## Next Steps (Continuing This Session)

1. Complete S2 Filters (9 remaining — small, tractable set, HIGH priority given small category size)
2. Sample 2-3 more Misc types to test if sub-family patterns exist (Reverb, Formant-I, Dist.Comb) — Misc is HIGH RISK for hidden variation
3. Verify 1 more Multi 3-way type and 1 more Flanges type (FPhs) to strengthen inference confidence
4. For Normal category (16 remaining slope variants), spot-check 2-3 (e.g., Notch 12, Peak 24) since these are structurally distinct filter families (not just slope variants) even within "Normal"
5. Compile final normalized semantic control matrix with VERIFIED vs INFERRED status clearly marked
6. Proceed to Filter1 vs Filter2 targeted comparison (per user's Phase 6 efficiency directive)
7. Reconcile technical VST3 fields against the semantic matrix
8. Reconcile targets.py and operations coverage

---

## P0/P1 Status (Interim — DO NOT CLOSE)

**P0:** Not yet resolved — full semantic control matrix incomplete (13/107 types individually verified)  
**P1:** Not yet resolved — Misc category heterogeneity requires continued individual verification; S2 Filters (small, tractable) not yet complete  
**P2:** N/A — no deferral candidates identified yet; this entire phase is P0/P1 work

**FILTER remains IN PROGRESS. Not eligible for closure.**

---

Generated: 2026-09-15 (mid-session checkpoint)
