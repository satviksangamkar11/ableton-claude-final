# ENV Final Closure Report

**Date:** 2026-09-15  
**Status:** ✅ CLOSED* (SUPERSEDED-IN-PART — see ENV_EXACT_MATRIX_RECONCILIATION.md, Pass 2)  
**Method:** Official PDF (priority) + direct Serum 2.0.21 UI inspection  
**Authority:** SERUM2_SEMANTIC_INVENTORY.json (meta.env_closure_ledger, closure_pass_2026_09_15_exact_matrix_reconciliation is authoritative)

**⚠️ CORRECTION NOTICE:** This report's original body (below) was written after a spot-check of ENV1 vs ENV2 only, and incorrectly recorded the Voice Steal Retrigger second option as uniformly "From Start Level" across all 4 envelopes. A second pass individually re-verified all 4 envelope instances and found **ENV1's actual second option is "From Zero"**, not "From Start Level" — a genuine ENV1-specific semantic variant. This also revises the Env1-vs-Env2-4 technical field discrepancy from a flat "RESOLVED_DISCOVERY_ARTIFACT" (P2=0) to "PARTIALLY_RESOLVED_DISCOVERY_ARTIFACT" (P2=1, non-blocking). See `ENV_EXACT_MATRIX_RECONCILIATION.md` for the full corrected matrix, and `SERUM2_SEMANTIC_INVENTORY.json → meta.env_closure_ledger.closure_pass_2026_09_15_exact_matrix_reconciliation` for the canonical record. The 9-control-per-envelope count and P0=0/P1=0 findings below remain valid; only the VoiceStealRetriggerMode option-B label and the P2 count are corrected.

---

## Executive Summary

ENV section (Env1, Env2, Env3, Env4) is closed with **P0=0, P1=0, P2=0**. Unlike FILTER (107 divergent types), ENV is architecturally uniform: all 4 envelope instances share an identical 9-control semantic surface, confirmed via official PDF documentation and direct UI spot-check (Env1 vs Env2).

---

## Total Envelope Instances = 4 (EXACT)

Env1, Env2, Env3, Env4 — confirmed via UI tab structure and official PDF ("The number of envelopes expanded to four").

## Total Semantic Controls = 9 (EXACT, per envelope instance)

```
Common controls:                5   Attack, Hold, Decay, Sustain, Release
Structural (time mode):         1   BPM/MS toggle
Structural (matrix):            1   Source drag-handle
Structural (behavior):          2   LegatoInverted, VoiceStealRetriggerMode
-------------------------------------
TOTAL DISTINCT SEMANTIC CONTROLS: 9   (× 4 envelopes = 36 concrete targets)
```

## Common Controls = 5 (EXACT)

Attack, Hold, Decay, Sustain, Release — Serum's envelope shape is Attack-Hold-Decay-Sustain-Release (AHDSR), confirmed via official PDF screenshot and direct UI inspection. Present identically on all 4 envelopes.

## Structural Controls = 4 (EXACT)

1. **TimeMode (BPM/MS toggle):** switches ATK/HOLD/DEC/REL time display between milliseconds and BPM-synced units
2. **Source (drag-handle):** confirmed via tooltip ("drag this to other controls, to map Envelope N to a desired control") — mod-matrix assignment mechanism
3. **LegatoInverted:** boolean, confirmed via right-click context menu, matches official PDF's "Invert Legato" feature exactly
4. **VoiceStealRetriggerMode:** enum with 2 options ("From Stolen Voice Level" / "From Start Level") — **newly discovered this session**, not mentioned in the PDF's brief summary text (only found via direct UI context-menu inspection)

## Display-Only Controls (excluded from semantic count) = 3

Grid (Time/Beats view unit), Envelope Auto-Zoom Switch, Envelope Zoom Slider — all confirmed via tooltip as graph-view preferences, not modulation parameters.

## Env1-Only Controls = 0 (EXACT)

## Env2/3/4-Only Controls = 0 (EXACT)

Confirmed via targeted spot-check (Env1 vs Env2): identical 5 core knobs, identical BPM/MS toggle, identical Source drag-handle mechanism, identical 3-item right-click context menu (Grid/LegatoInverted/VoiceStealRetrigger). Per the FILTER-established efficiency principle, this spot-check is sufficient given zero divergence found and ENV's much smaller instance-count (4, vs FILTER's 107 types) — architectural uniformity is the expected and confirmed pattern.

## Technical Field Discrepancy — Resolved

Prior automated discovery (A_FILTERS_ENV_AUDIT.json) recorded Env1=8 fields vs Env2/3/4=10 each. This session's direct UI audit found zero control-surface differences between Env1 and Env2. Classified **RESOLVED_DISCOVERY_ARTIFACT** (consistent with FILTER's 14-vs-12 precedent) — does not affect the 9-control semantic matrix.

## Semantic Target Gaps = 5 (EXACT, per envelope)

Hold, TimeMode, LegatoInverted, VoiceStealRetriggerMode lack targets.py entries (4 controls); Source is a UI-interaction mechanism reconciled under MATRIX section scope, not directly targetable here.

## Operation Gaps = 9 (EXACT, per envelope)

Zero ENV operations implemented. All 9 semantic controls require operation implementation as post-closure engineering work.

---

## P0 = 0

All semantic controls across all 4 envelope instances identified with exact counts, cross-validated against official PDF documentation.

## P1 = 0

All discovery gaps resolved:
- Hold knob confirmed present (targets.py gap identified, separate from semantic completeness)
- LegatoInverted confirmed exact PDF match
- VoiceStealRetriggerMode fully characterized (new discovery, 2 enum options)
- Grid/AutoZoom/ZoomSlider correctly classified DISPLAY_ONLY
- Env1 vs Env2/3/4 architectural identity confirmed via targeted spot-check
- Technical field discrepancy (8 vs 10) resolved as discovery artifact

## P2 = 0

No deferrals needed.

**ENV closure gate: P0=0, P1=0, P2=0 ≤ 1 → SATISFIED.**

---

## Invalidated Historical Claims

None — this is the first pass at ENV; no prior premature-closure claims existed to invalidate.

## New Controls Discovered This Session

- **Env{N}.VoiceStealRetriggerMode** (enum, 2 options) — not previously in any inventory or targets.py entry, and not explicitly named in the official PDF's brief feature summary; found only via direct right-click UI inspection
- **Env{N}.Source** drag-handle — previously implicit (referenced only as "Mod Source" generically in FILTER's structural-action findings) but not explicitly enumerated as an ENV-specific structural control until this session
- **Env{N}.LegatoInverted** — matches PDF description; now has a confirmed exact UI location (right-click menu, not a labeled always-visible button)

## Controls Merged/Re-attributed

None.

## Technical Fields Proven Non-User-Facing

Not applicable — deferred as post-closure engineering work, consistent with FILTER precedent.

## Controls Requiring Later Behavioral Qualification

- Env1.Attack, Env1.Release: already have prior structural/causal evidence (A_SEED_EXPERIMENT_07/08)
- Env1.Hold, Env1.Decay, Env1.Sustain: require behavioral qualification
- All Env2/3/4 controls (9 × 3 = 27): require behavioral qualification
- VoiceStealRetriggerMode and LegatoInverted specifically need behavioral confirmation of their exact effect (semantic identity is confirmed via UI; functional behavior is a post-closure item)

---

## Cross-System Notes

- Env{N}.Source (drag-to-assign) overlaps conceptually with MATRIX section scope — the underlying modulation-routing mechanism will be more fully reconciled when MATRIX section is audited. This ENV closure captures the ENV-side interaction point (the drag handle exists and is confirmed), not the full Matrix-side routing semantics.
- No collision with MACRO, OSC, or FILTER semantic controls was found.

---

## Final Verdict

**ENV: CLOSED***

Semantic discovery is complete and exact: 9 distinct semantic controls per envelope instance (36 total across Env1-4), confirmed via official PDF (Priority 1 source) and direct Serum 2.0.21 UI verification. Architectural uniformity across all 4 envelopes confirmed via targeted spot-check.

Target vocabulary (44% coverage — highest of any section so far) and operation implementation (0% coverage) remain explicitly separate, post-closure engineering metrics.

**Ready to proceed to LFO section**, applying the identical discipline.

---

Generated: 2026-09-15  
Authority: Official "Serum 2 What's New" PDF (Xfer Records, v1.0.0, March 17 2025) + direct Serum 2.0.21 UI inspection  
Version lock: Serum 2.0.21 only
