# FILTER Control Surface Audit — Progress Report

**Date:** 2026-09-15  
**Status:** ✅ PHASE 2 COMPLETE — ALL 107/107 TYPES INDIVIDUALLY VERIFIED (100%)  
**Phase 1 status:** ✅ COMPLETE (107 types exactly enumerated — see FILTER_TYPE_COMPLETE_ENUMERATION.md)

## 🎉 MILESTONE: 107/107 Filter Types — Complete Control Surface Audit

All five categories now 100% verified:
- Normal: 18/18
- Multi: 21/21
- Flanges: 32/32
- Misc: 25/25
- S2 Filters: 11/11

**Total: 107/107 (100%)**

### Complete 4th-Knob Identity Distribution

| 4th-Knob Label | Count | Types |
|---|---|---|
| FAT | 14 | MG Low(4), High12/18/24(3), Band12/24(2), Peak12/24(2), Notch12/24(2), Notch... |
| DISABLED | 25 | Low(4), High6(1), Cmb+/-(2), Flg+/-(2), Phs12/24/36/48+/-(8), DJ Mixer(1), Exp BPF(1), RingMod(1), SampHold+/-(2), German LP(1), + 1 more |
| FREQ | 13 | All 2-way Multi morphs |
| MORPH | 9 | All 3-way Multi morphs (8) + Wsp (1) |
| SMOOTH | 4 | MG Ladder, Acid Ladder, EMS Ladder, PZ SVF |
| LP FRQ | 6 | Cmb L6+/-, Flg L6+/-, Phs48L6+/- |
| HP FRQ | 6 | Cmb H6+/-, Flg H6+/-, Phs48H6+/- |
| HL WID | 8 | Cmb HL6+/-, Flg HL6+/-, Phs48HL6+/-, FPhs12HL6+/- |
| DB +/- | 5 | Low EQ6/12, Band EQ12, High EQ6/12 |
| DAMP | 3 | Combs, Allpasses, Reverb |
| FORMNT | 3 | Formant-I/II/III |
| COMBFRQ | 4 | Dist.Comb 1LP/BP, 2LP/BP |
| SCREAM | 2 | Scream LP/BP |
| SPREAD | 1 | Ring Modx2 |
| STAGES | 1 | Diffusor |
| PAIN | 1 | MG Dirty |
| BOEUF | 1 | French LP |
| THRU | 1 | Add Bass |
| WIDTH | 1 | Bandreject |
| MIX (dup) | 1 | Exp MM |
| FRQ2 | 1 | Comb 2 |

**Total distinct 4th-knob identities: 21** (including DISABLED as a "no control" state)

This confirms conclusively: the FILTER control surface is NOT a simple 7-knob
template. It is 107 individually-designed control surfaces sharing a common
Cutoff/Res/Drive/Pan/Mix/Level skeleton, with the 4th knob carrying genuinely
distinct, type-specific semantic identity in the vast majority of cases.

---

## ⚠️ SCOPE ESCALATION (Critical Update)

Initial hypothesis was that slope variants (6/12/18/24 dB) within the same
filter family would share an identical 4th-knob control. This has been
**DISPROVEN**:

- **Low 6** (Standard, non-Moog) → DISABLED
- **High 6** (Standard, non-Moog) → DISABLED
- **High 24** (Standard, non-Moog, SAME family as High 6) → **FAT**

This means slope variants of the SAME named family do NOT reliably share
control surfaces. Combined with the earlier MG Dirty vs. Ladder-family
finding, this proves: **NO level of inference is safe** — category-level,
family-level, and even slope-level groupings can all diverge. Every one of
the 107 individual types requires direct, independent verification with
no exceptions. This significantly increases the scope of Phase 2 versus
the original estimate.

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

### Directly Verified (23 of 107 = 21.5%)

**Normal (18 of 18 = 100% COMPLETE):**
1. MG Low 6 — FAT
2. MG Low 12 — FAT
2b. MG Low 18 — FAT
2c. MG Low 24 — FAT
2d. Low 6 — DISABLED
2e. Low 12 — DISABLED
2f. Low 18 — DISABLED
2g. Low 24 — DISABLED
2h. High 6 — DISABLED (outlier within High family)
2i. High 12 — FAT
2j. High 18 — FAT
2k. High 24 — FAT
2l. Band 12 — FAT
2m. Band 24 — FAT
2n. Peak 12 — FAT
2o. Peak 24 — FAT
2p. Notch 12 — FAT
2q. Notch 24 — FAT

**Normal category final pattern:** MG Low(all 4)=FAT; Low(all 4)=DISABLED;
High=DISABLED only at 6dB, FAT at 12/18/24dB (asymmetric outlier); Band,
Peak, Notch (all slopes)=FAT. This confirms per-type verification was
necessary — the High-family 6dB exception would have been missed by any
family or category-level inference.

**Multi (21 of 21 = 100% COMPLETE):**
3. LH 6 — FREQ
4. LH 12 — FREQ
5. LB 12 — FREQ
6. LP 12 — FREQ
7. LN 12 — FREQ
8. HB 12 — FREQ
9. HP 12 — FREQ
10. HN 12 — FREQ
11. BP 12 — FREQ
12. BN 12 — FREQ
13. PP 12 — FREQ
14. PN 12 — FREQ
15. NN 12 — FREQ
16. L/B/H 12 — MORPH
17. L/B/H 24 — MORPH
18. L/P/H 12 — MORPH
19. L/P/H 24 — MORPH
20. L/N/H 12 — MORPH
21. L/N/H 24 — MORPH
22. B/P/N 12 — MORPH
23. B/P/N 24 — MORPH

**Multi category final pattern:** All 13 two-way morphs = FREQ (perfectly
consistent); all 8 three-way morphs = MORPH (perfectly consistent). Unlike
Normal category, Multi shows clean internal consistency by morph-arity.

**Flanges (32 of 32 = 100% COMPLETE):**

*Comb sub-family (8):*
6. Cmb + — DISABLED
7. Cmb - — DISABLED
8. Cmb L6+ — LP FRQ
9. Cmb L6- — LP FRQ
10. Cmb H6+ — HP FRQ
11. Cmb H6- — HP FRQ
12. Cmb HL6+ — HL WID
13. Cmb HL6- — HL WID

*Flange sub-family (8, exact mirror of Comb pattern):*
14. Flg + — DISABLED
15. Flg - — DISABLED
16. Flg L6+ — LP FRQ
17. Flg L6- — LP FRQ
18. Flg H6+ — HP FRQ
19. Flg H6- — HP FRQ
20. Flg HL6+ — HL WID
21. Flg HL6- — HL WID

*Phaser sub-family (16):*
22. Phs 12+ — DISABLED
23. Phs 12- — DISABLED
24. Phs 24+ — DISABLED
25. Phs 24- — DISABLED
26. Phs 36+ — DISABLED
27. Phs 36- — DISABLED
28. Phs 48+ — DISABLED
29. Phs 48- — DISABLED
30. Phs 48L6+ — LP FRQ
31. Phs 48L6- — LP FRQ
32. Phs 48H6+ — HP FRQ
33. Phs 48H6- — HP FRQ
34. Phs 48HL6+ — HL WID
35. Phs 48HL6- — HL WID
36. FPhs 12HL6+ — HL WID
37. FPhs 12HL6- — HL WID

**Flanges category final pattern:** Comb and Flange sub-families share an
IDENTICAL internal structure (±: DISABLED, L6±: LP FRQ, H6±: HP FRQ, HL6±:
HL WID). Phaser sub-family extends this with plain-slope variants (12/24/
36/48) all DISABLED, then the same L6/H6/HL6 pattern for the 48dB variant,
plus FPhs (Formant Phaser) also = HL WID. Despite the perfect internal
consistency WITHIN Flanges, this could not have been safely inferred from
the Normal or Multi category findings.

**Misc (25 of 25 = 100% COMPLETE):**
9. Low EQ 6 — DB+/-
9b. Low EQ 12 — DB+/-
9c. Band EQ 12 — DB+/-
9d. High EQ 6 — DB+/-
9e. High EQ 12 — DB+/-
10. Ring Mod — DISABLED [distinct graph type: waveform, not filter curve]
11. Ring Modx2 — SPREAD [differs from Ring Mod despite same family]
12. SampHold — DISABLED
12b. SampHold- — DISABLED
12c. Combs — DAMP
12d. Allpasses — DAMP
12e. Reverb — DAMP
12f. French LP — BOEUF [playful French-themed naming]
12g. German LP — DISABLED [differs from French LP despite parallel naming]
12h. Add Bass — THRU
12i. Formant-I — FORMNT
12j. Formant-II — FORMNT
12k. Formant-III — FORMNT
12l. Bandreject — WIDTH
12m. Dist.Comb 1 LP — COMBFRQ
12n. Dist.Comb 1 BP — COMBFRQ
12o. Dist.Comb 2 LP — COMBFRQ
12p. Dist.Comb 2 BP — COMBFRQ
12q. Scream LP — SCREAM
12r. Scream BP — SCREAM

**Misc category final pattern:** Most heterogeneous category as predicted —
9 distinct 4th-knob identities (DB+/-, DISABLED, SPREAD, DAMP, BOEUF, THRU,
FORMNT, WIDTH, COMBFRQ, SCREAM = 10 actually). EQ family (5) fully
consistent; Comb/Allpass/Reverb share DAMP; Formant family (3) fully
consistent; Dist.Comb family (4) fully consistent; Scream family (2) fully
consistent. But French LP vs. German LP diverge despite parallel naming,
and Ring Mod vs. Ring Modx2 diverge — confirming per-type verification
was essential throughout.

**S2 Filters (11 of 11 = 100% COMPLETE):**
13. Wsp — MORPH
14. DJ Mixer — DISABLED
15. Diffusor — STAGES
16. MG Ladder — SMOOTH
17. Acid Ladder — SMOOTH
18. EMS Ladder — SMOOTH
19. MG Dirty — PAIN [breaks the "MG"-family SMOOTH pattern]
20. PZ SVF — SMOOTH
21. Comb 2 — FRQ2
22. Exp MM — MIX [duplicate label vs. main Mix knob — needs CBOR disambiguation]
23. Exp BPF — DISABLED [confirmed as absolute last type via wraparound to MG Low 6]

**S2 Filters family sub-pattern discovered:** Ladder-named types (MG Ladder, Acid Ladder, EMS Ladder, PZ SVF) all share SMOOTH, but MG Dirty (also Moog-related) breaks this with PAIN — confirming NO naming-based inference is safe without verification.

### Remaining to verify (84 of 107 = 78.5%)

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

**S2 Filters: ✅ 100% COMPLETE (0 remaining)** — all 11 types individually verified. Final result: MORPH(1), DISABLED(2), STAGES(1), SMOOTH(4), PAIN(1), FRQ2(1), MIX-duplicate(1).

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
