# Phase 2A-R.9: MATRIX Destination Reconciliation

**Date**: 2026-09-16  
**Method**: Full 16-family destination enumeration extracted from `matrix_closure_ledger`, each family checked against the 870-record baseline before any new record was added.

---

## The 16 Top-Level Destination Families, Disposed

| Family | Count | Multiplicity | Disposition |
|---|---|---|---|
| Off | — | n/a | Not a real destination, excluded |
| OSC A/B/C | 38 each (mode-conditional) | per-instance × per-mode | Already covered — cross-referenced to OSC section by the ledger itself |
| Noise OSC | 6 | per-instance | Already covered (added Phase 2A-R.6) |
| SUB OSC | 5 | per-instance | Already covered (added Phase 2A-R.6) |
| Filter 1 | 7 | per-instance | **5 already covered, 2 genuinely new** (Var, Stereo) |
| Filter 2 | 7 | per-instance | **5 already covered, 2 genuinely new** (Var, Stereo) |
| Env 1 | 8 | conditional destination family (curves not in ENV's own 9-control matrix) | **5 already covered, 3 genuinely new** (Atk/Dec/Rel Curve), applied × 4 envelopes |
| Macros | 8 | per-instance | Already covered, cross-ref to MACRO section |
| LFO Busses | 16 | single destination family, MATRIX-owned (distinct from LFO 1-10 sources) | Already atomic in baseline (pre-existing `MATRIX.LFO_BUS.01-16`) |
| Routing Matrix | 19 sub-items | consolidated into 1 structural/topological record | Already atomic (`MATRIX.ROUTING.SIGNAL_BALANCE`) |
| Clip Player | 39 (3 global + 12 clips × 3) | **structural multiplicity mismatch — flagged, not resolved** | See below |
| Arpeggiator | 14 | mostly per-instance/single | 13 already covered (label-verified against ARP's 49 records), **1 genuinely new** (Wrap Phantom Note) |
| Retriggers | 19 | per-source toggle, structurally distinct from all other families | **19 genuinely new** — a semantic concept (per-source retrigger-on-note-on) that exists nowhere else in the inventory |
| Global | 7 | single destinations | Already covered (Main Tuning, Amp→`MIXER.MAIN.LEVEL`, Porta Time, Swing→`KEYBOARD.SWING`, Transpose→`KEYBOARD.TRANSPOSE`, Envelope/LFO Scaling) |

---

## Genuinely New: 36 Records

```
FILTER  +4   Var, Stereo × 2 filters — missed by FILTER's own 2026-09-15 closure
              (not in its 6 common_controls, 20 type-specific, or 9 structural lists)
ENV     +12  Atk/Dec/Rel Curve × 4 envelopes — the ledger's OWN text explicitly named
              this as "a P1 cross-section reconciliation gap" but never itemized it
GLOBAL  +19  Per-source retrigger-enable toggle — deferred to GLOBAL's own closure
              pass by the original ledger; GLOBAL subsequently closed (32 records)
              WITHOUT capturing this family
ARP     +1   Wrap Phantom Note — missed by ARP's 2026-09-17 closure, which captured
              the three adjacent Wrap fields (Wrap, Wrap Transpose, Wrap Range) but not this one
────
36 total, A ∩ B = 0 (explicitly verified)
```

---

## Critical Distinction Applied (Per Your Instruction)

Not every "Matrix destination → Parameter" pair became a new semantic record. Explicit examples where the distinction was applied correctly:

- **OSC A/B/C's 38 mode-dependent destinations** → NOT 38×3 new records. They reference the *existing* OSC parameter semantics (already itemized in Phase 2A-R.5). The MATRIX destination is a routing pointer to an existing control, not a new one.
- **Filter's Wet/Freq/Res/Drive/Level** (5 of 7 Filter-family items) → reference existing `FILTER{n}.*`/`MIXER.FILTER{n}.*` records. Only `Var`/`Stereo` were new because no existing record covered them.
- **Macros 1-8** → reference existing `MACRO.0{n}.VALUE` records, not new.

Where a destination genuinely represented a *new user-facing state* not reducible to an existing parameter (the GLOBAL Retriggers per-source toggle family, ENV's curve-shape controls, FILTER's Var/Stereo knobs), it was added. Where it was a routing pointer to something already itemized, it was not.

---

## Flagged, Not Resolved: Clip Player Structural Multiplicity

The ledger describes Clip Player as "3 global params + 12 clips × 3 params each" (39 total). CLIP's own subsequent closure produced `CLIP.SETTINGS.TRANS` and `CLIP.SETTINGS.RATE` as **single** records (no per-slot instancing), and has **no Offset field at all**.

This is a genuine structural question, not a simple presence check: does modulating clip-slot-3's Transpose independently from clip-slot-5's Transpose actually work in Serum (supporting the ledger's 12×3 model), or is there only ever "the currently selected clip's" Trans/Rate (supporting CLIP's single-record model)? I did not fabricate 36 speculative per-slot records without behavioral evidence, and did not assume CLIP's single-record model is sufficient either. **Left open, explicitly logged**, for either a targeted behavioral check or a decision to defer.

---

## Result

```
870  (post-MATRIX.SOURCE)
+36  MATRIX.DESTINATION reconciliation (FILTER 4, ENV 12, GLOBAL 19, ARP 1)
────
906  current evidence-derived union
```

---

## GLOBAL SET RECONCILIATION — Status Check

Per your requested closing gate:

```
0 unexplained duplicates        ✅ every addition/exclusion across all of Phase 2A-R.4 through R.9
                                    traced to explicit evidence (cross_reference text, internal
                                    VST3 field-name match, or ledger's own itemized list)
0 unexplained aggregate ledgers ✅ all 6 sections with meta.*_closure_ledger structure checked
                                    (macro/osc/filter/env/lfo/matrix); matrix required both
                                    SOURCE (R.8) and DESTINATION (R.9) sub-passes
1 unaccounted item              ⚠️ Clip Player 3-global+12×3 multiplicity — flagged, not
                                    force-resolved (see above)
```

**Not yet zero on the third criterion.** One explicit open question remains before a clean freeze.

---

## Updated Phase State

```
PHASE 2A-R.9  MATRIX.DESTINATION reconciliation      ✅ COMPLETE (906)
PHASE 2A-R.10 Clip Player multiplicity resolution     ⏳ OPEN (flagged, not forced)

PHASE 2C+                                             🚫 still blocked
```

---

**Status**: 906 is the current machine-verified union. One structural ambiguity (Clip Player multiplicity) remains explicitly open. Recommend either a targeted behavioral check (does per-slot MATRIX routing to Clip Player Trans/Rate/Offset actually differ per slot?) or an explicit decision to defer it as CLIP-section follow-up work, before declaring the final freeze.
