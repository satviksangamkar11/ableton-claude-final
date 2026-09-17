# Phase 2A-R.5: OSC Atomization + Consolidated Evidence Universe

**Date**: 2026-09-16

---

## OSC Atomization Result

```
Baseline before OSC:                    704
Raw candidate fields (VST3 idx 20-62):   43   (uniform per oscillator A/B/C, verified via
                                                independently-discovered A_OSC2_INVENTORY_DISCOVERED.json,
                                                not merely assumed from OSC1)
  - VERIFIED (genuine semantic):         41   x 3 oscillators = 123
  - PROVEN_NOT_USER_CONTROL:              2   (Ratio, Hz Offset -- no UI control found in any of
                                                5 oscillator modes, per OSC_FINAL_CLOSURE_REPORT.md)
                                                x 3 oscillators = 6

New OSC records:                        129   (43 x 3, exact)
A ∩ new_OSC (explicitly checked):          0
```

**Not blindly turned into 43 flat semantic records** — each was checked against the existing baseline by constructed `semantic_id` before being added; 0 collisions found, so all 129 are genuinely new to the atomic-record layer (even though several already have *targets* in `targets.py` — target-existence and semantic-record-existence are still being kept as separate questions, per the project's own Population 2 vs Population 3 distinction).

### Mode-Dependent Applicability, Not Ignored

Fields at VST3 index ≥30 (Start, End, Reverse, Scan Rate, Loop controls, Slice controls, etc.) are conditionally meaningful depending on which of the 5 oscillator modes (Wavetable/Sample/Multisample/Granular/Spectral) is active — confirmed in the source evidence's `mode_by_mode_verification`. Each such record carries an explicit `conditional_visibility` note rather than being presented as always-visible. This is not a full per-mode breakdown (that would require knowing exactly which fields apply to which of the 5 modes, which the source evidence describes qualitatively but doesn't tabulate field-by-field) — flagged as a finer-grained follow-up if per-mode precision is later needed, not fabricated here.

### Unresolved: 9 Flagged, Not Merged

`Enable`, `Level`, `Pan` × 3 oscillators = 9 new records carry an explicit `POTENTIAL_DUPLICATE_UNRESOLVED` flag against `MIXER.OSC_{A,B,C}.ENABLE/LEVEL/PAN`, which already exist. **These were NOT merged or excluded**, for a specific reason: the baseline (704, untouched by me) already contains `SUB_OSC.LEVEL` / `SUB_OSC.PAN` sitting *alongside* `MIXER.SUB.LEVEL` / `MIXER.SUB.PAN` with **no cross-reference between them** — meaning whoever did the original evidence-gathering did not treat oscillator-panel Level/Pan and mixer-channel-strip Level/Pan as the same identity for SUB/NOISE. Since I have no stronger evidence for OSC1/2/3 than existed for SUB/NOISE, forcing a merge here (while leaving SUB/NOISE unmerged) would be an inconsistent, unjustified judgment call in the opposite direction of the FILTER case — where I *did* merge, but only because explicit `cross_references: ["FILTER.1.*"]` text already existed in the MIXER records themselves. No equivalent text exists for OSC or SUB/NOISE. Flagged, not decided.

---

## Consolidated Evidence-Derived Universe

```
516   Git-reconstructed baseline (Phase 2A-R.1)
+188  FILTER(62)/ENV(36)/LFO(90), duplicate-checked (Phase 2A-R.4)
+129  OSC1/OSC2/OSC3, duplicate-checked (Phase 2A-R.5)
────
 833  current evidence-derived union, 0 duplicate semantic_ids, machine-verified
```

By section:

| Section | Count | Section | Count |
|---|---|---|---|
| FX | 173 | GLOBAL | 32 |
| OSC | 140 | GLOBAL_KEYBOARD | 21 |
| LFO | 90 | ARP | 49 |
| MIXER | 66 | CLIP | 28 |
| FILTER | 62 | MATRIX | 39 |
| MACRO | 48 | VOICE | 8 |
| BROWSER | 41 | ENV | 36 |

---

## Explicitly NOT Resolved — Do Not Freeze Yet

These are real, evidence-surfaced open questions, not oversights swept under the rug:

1. **9 OSC Enable/Level/Pan records**: `POTENTIAL_DUPLICATE_UNRESOLVED` against MIXER equivalents (see above)
2. **2 SUB_OSC records** (`.LEVEL`, `.PAN`) already in the pre-existing baseline: same unresolved question, pre-dates this reconciliation, now explicitly connected to the OSC1/2/3 finding
3. **MATRIX.SOURCE domain gap** (found during ENV/LFO overlap-checking, Phase 2A-R.4): menu enumeration lists Envelopes/LFOs as source categories, but no atomic `MATRIX.SOURCE.ENV{n}` / `MATRIX.SOURCE.LFO{n}` records exist anywhere in the 833 — a genuine gap, not yet itemized
4. **SUB_OSC/NOISE_OSC completeness**: these two instances got only 11 records total from an earlier, narrower discovery pass (MATRIX-destination-sweep-based), never subjected to the same rigorous 55-field technical/semantic disposition that OSC1/2/3 (A/B/C) received. They may have their own itemization gap, structurally parallel to what FILTER/ENV/LFO/OSC1-3 had — **not investigated in this pass**.

---

## Updated Phase State

```
PHASE 2A-R.1  Git reconstruction                    ✅
PHASE 2A-R.2  43-delta investigation                 ✅ (explained as narrative artifact)
PHASE 2A-R.3  First atomization attempt              ❌ RETRACTED (712, unverified overlap)
PHASE 2A-R.4  FILTER/ENV/LFO, set-reconciled          ✅ COMPLETE (704, A∩B=0 verified)
PHASE 2A-R.5  OSC1/2/3, set-reconciled                ✅ COMPLETE (833, A∩B=0 verified)
PHASE 2A-R.6  Resolve 11 flagged ambiguities          ⏳ NEXT
              (9 OSC + 2 SUB_OSC dup flags, MATRIX.SOURCE gap, SUB/NOISE completeness)

PHASE 2C      Normalization                          🚫
PHASE 2D      Target reconciliation                  🚫
PHASE 2E      Gap audit                              🚫
PHASE 2F      Representation families                🚫
PHASE 3       Deep experiments                       🚫
```

---

## Artifacts

| File | Status |
|---|---|
| `SERUM2_SEMANTIC_INVENTORY_EVIDENCE_DERIVED_V3.json` | Current: 833 records, 0 duplicates, OSC1/2/3 atomized |
| `SERUM2_SEMANTIC_INVENTORY_EVIDENCE_DERIVED_V2.json` | Superseded (704) — retained for audit trail |
| `SERUM2_SEMANTIC_INVENTORY_EVIDENCE_DERIVED.json` | Superseded (712, retracted) — retained for audit trail |

---

**Status**: 833 is the current machine-verified evidence-derived union. **Still not frozen** — 4 categories of explicit, evidenced ambiguity remain open (listed above), none of them force-resolved. Recommend addressing the SUB_OSC/NOISE_OSC completeness check and the MATRIX.SOURCE gap next, since both follow the exact same itemization method already proven twice (FILTER/ENV/LFO, then OSC), before declaring a final number.
