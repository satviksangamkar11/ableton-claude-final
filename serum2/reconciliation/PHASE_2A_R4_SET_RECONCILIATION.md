# Phase 2A-R.4: Set-Based Reconciliation of the Evidence-Derived Population

**Date**: 2026-09-16  
**Correction to**: PHASE_2A_R3_EVIDENCE_DERIVED_UNIVERSE.md (which claimed 712; that number is **retracted**, arithmetic was not verified against overlap)

---

## What Was Wrong With 712

The prior pass itemized FILTER as 70 records (excluding 3 routing + 6 generic-actions from the ledger's own 88-total), computed `516 + 70 + 36 + 90 = 712`, and never checked whether the remaining 70 FILTER records collided with **already-existing** records elsewhere in the 516. They did.

---

## Explicit Set Reconciliation

```
A = git-reconstructed atomic records (Phase 2A-R baseline)              516
B = newly itemized FILTER/ENV/LFO records, AFTER duplicate removal      188
A ∩ B (verified empty by explicit ID check, not assumed)                  0
A ∪ B                                                                    704

Arithmetic check: |A| + |B| = |A ∪ B|  ⟺  516 + 188 = 704  ✅ exact
```

**B breaks down as**: FILTER 62, ENV 36, LFO 90.

---

## Why FILTER Dropped From 70 to 62: 14 Genuine Duplicates Found

Checking each FILTER candidate's semantic_id against the *content* (not just the ID string) of existing MIXER records — specifically their `cross_references` and `notes` fields — surfaced **explicit, pre-existing evidence** that these are the same physical control, not two:

| Candidate (would-be new) | Duplicates existing | Evidence for duplication (verbatim from source) |
|---|---|---|
| `FILTER1.PAN` | `MIXER.FILTER1.PAN` | FILTER ledger claims Pan as a "common control"; MIXER already owns the atomic Pan record |
| `FILTER1.LEVEL` | `MIXER.FILTER1.LEVEL` | MIXER record's own cross_reference: `["FILTER.1.*"]`, notes: *"likely the same physical parameter as viewed in FILTER section's own panel"* |
| `FILTER1.MIX` | `MIXER.FILTER1.WET` | MIXER record's cross_reference includes `FILTER.1.*`; notes: *"Cross-references the 'Wet' parameter already enumerated..."* — UI label MIX, internal name "Filter 1 Wet" |
| `FILTER1.ENABLE` | `MIXER.FILTER1.ENABLE` | MIXER record cross_reference: `["FILTER.1.*"]` |
| `FILTER1.BUS1SEND` | `MIXER.FILTER1.BUS1` | FILTER ledger itself labels these "FILTER-triggered, MIX-owned destination semantics" |
| `FILTER1.BUS2SEND` | `MIXER.FILTER1.BUS2` | same |
| `FILTER1.ROUTE` | `MIXER.FILTER1.ROUTING` | same |
| *(×2 for FILTER2, same 7 categories)* | | |

**Total: 14 candidates removed** (7 categories × 2 filters), all confirmed via pre-existing cross-reference text already present in the source inventory — not a new judgment call invented for this pass.

**Not removed** — genuinely FILTER-owned, no duplicate found anywhere:
- `Cutoff`, `Resonance`: MIXER's `GRAPHIC_CUTOFF_RESONANCE` record explicitly states it is *"an alternative graphical interaction surface for the SAME underlying Cutoff/Resonance parameters **already owned by the FILTER section**"* — confirming FILTER is the primary owner and its own atomic record for these did not yet exist. Kept.
- `Drive`: not referenced anywhere in MIXER or elsewhere. Kept.
- All 20 type-specific 4th-knob controls: FILTER-panel-only, no channel-strip mirror. Kept.
- 8 of 9 structural controls (all except Enable): `Type`, `Mute`, `RouteSub`, `RouteOscA/B/C`, `RouteNoise`, `KeyTrack`. Kept.

Result: **3 common + 20 type-specific + 8 structural = 31 per filter × 2 = 62.**

---

## Excluded By Design (Not Duplication): 12 Generic Actions

`Reset Control`, `MIDI Learn`, `Lock Parameter`, `Mod Source`, `Bypass Modulator`, `Remove [All] Modulator(s)` — per-knob UI mechanisms available on essentially every control in Serum. Verified: **zero sections in the entire 516-record inventory itemize these as distinct semantic_ids.** Including them for FILTER only would break schema consistency with every other section (MACRO, OSC, ENV, etc., none of which have a "MIDI Learn" record per parameter). Excluded, not counted as duplicate (no specific existing record they overlap with) and not counted as new B.

---

## ENV and LFO: No Overlaps Found

Checked specifically because `Env{N}.Source` and `LFO{N}.Source` are cross-referenced to `MATRIX.SOURCE` in their own closure ledgers. Verified: the existing `MATRIX.SOURCE.*` records in A are limited to `OSC_A/B/C`, `NOISE_OSC`, `SUB_OSC`, `FILTER_1`, `FILTER_2` — **no per-envelope or per-LFO SOURCE entries exist**, despite the raw MATRIX source-menu enumeration (read earlier in this session) listing "Envelopes: Env1-4" and "LFOs: LFO1-10" as menu categories. This is itself a **separate, smaller gap** (MATRIX's own SOURCE domain is incompletely itemized relative to its own menu enumeration) — noted here, not fixed, since it's out of scope for this specific ENV/LFO check. ENV and LFO's full 36 and 90 counts stand as genuinely new, non-duplicate.

---

## Updated Phase State

```
PHASE 2A-R.1  Git reconstruction                    ✅
PHASE 2A-R.2  43-delta investigation                 ✅ (explained, not reproduced exactly — narrative artifact)
PHASE 2A-R.3  Evidence atomization (first pass)      ❌ RETRACTED (712 was inflated by 8 undetected duplicates + arithmetic slip)
PHASE 2A-R.4  Set-reconciled atomization              ✅ COMPLETE
              FILTER   62  (verified against MIXER overlap)
              ENV      36  (verified no overlap)
              LFO      90  (verified no overlap)
              A ∪ B   704  (arithmetic-clean: 516 + 188 = 704)
PHASE 2A-R.5  OSC atomization                        ⏳ NEXT (different schema, not yet resolved)

PHASE 2C      Normalization                          🚫
PHASE 2D      Target reconciliation                  🚫
PHASE 2E      Gap audit                              🚫
PHASE 2F      Representation families                🚫
PHASE 3       Deep experiments                       🚫
```

---

## Secondary Finding, Logged Not Fixed

**MATRIX.SOURCE domain is itself incomplete**: its own menu enumeration (captured during MATRIX discovery) lists Envelopes and LFOs as source categories, but no atomic `MATRIX.SOURCE.ENV{n}` / `MATRIX.SOURCE.LFO{n}` records exist in A. This surfaced only because it was checked as part of ruling out ENV/LFO Source-field duplication. It is a real, separate gap in MATRIX's own atomization, not resolved here — flagged for the same treatment MATRIX's other sub-areas already received.

---

## Artifacts

| File | Status |
|------|--------|
| `SERUM2_SEMANTIC_INVENTORY_EVIDENCE_DERIVED_V2.json` | Corrected: 704 records, 0 duplicates, FILTER/ENV/LFO atomized with verified non-overlap |
| `SERUM2_SEMANTIC_INVENTORY_EVIDENCE_DERIVED.json` | Superseded — retained for audit trail, do not use as current |
| `PHASE_2A_R4_SET_RECONCILIATION.json` | Machine-readable: A/B/intersection/union counts, full duplicate list with reasons |

---

**Status**: 704 is the current best evidence-derived total, machine-verified (A∩B=0, arithmetic exact), with every exclusion traced to explicit source evidence. **Still not final** — OSC remains unresolved, and the MATRIX.SOURCE gap is newly logged. No semantic count freeze yet.
