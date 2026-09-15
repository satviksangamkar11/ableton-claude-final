# ENV Section — Exact Matrix Reconciliation (Pass 2)

**Date:** 2026-09-15
**Status:** Reconciliation COMPLETE — supersedes ENV_SEMANTIC_RECONCILIATION.md on one factual point (Voice Steal Retrigger option label)
**Method:** Official PDF (Priority 1) + direct Serum 2.0.21 UI re-verification of all 4 envelope instances individually (not spot-check only)
**Trigger:** User correction — "do not finalize ENV yet based on the summary alone" + explicit 10-point re-reconciliation instruction

---

## 0. Why this pass exists

The prior pass (ENV_SEMANTIC_RECONCILIATION.md) closed on a 4-envelope spot-check (ENV1 vs ENV2 only) and recorded the Voice Steal Retrigger second option as "From Start Level" for all envelopes. Direct re-verification this pass — checking **all 4 envelope tabs individually**, not just ENV1/ENV2 — found this was **WRONG for ENV1**. ENV1's actual second option is **"From Zero"**, not "From Start Level". This is exactly the kind of error the user's instruction was designed to catch, and it directly informs the Env1-vs-Env2/3/4 asymmetry question (Section 2 below).

---

## 1. Exact ENV1–4 Matrix

For each of Attack, Hold, Decay, Sustain, Release, BPM/MS, Legato Inverted, Voice Steal Retrigger, Mod-source drag handle, graph/editor controls, and menu/context actions — recorded per envelope, with classification.

| # | Control | ENV1 | ENV2 | ENV3 | ENV4 | Classification |
|---|---|---|---|---|---|---|
| 1 | Attack (ATK knob) | 1.0 ms | 0.5 ms | present | present | COMMON_TO_ENV1-4 |
| 2 | Hold (HOLD knob) | 0.0 ms | 0.0 ms | present | present | COMMON_TO_ENV1-4 |
| 3 | Decay (DEC knob) | 1.00 s | present | present | present | COMMON_TO_ENV1-4 |
| 4 | Sustain (SUS knob) | 0.0 dB | present (unit: %) | present | present | COMMON_TO_ENV1-4 (unit varies: dB on ENV1 since hardwired to amplitude, % on ENV2-4 since freely routable — value-representation difference, not a control-surface difference) |
| 5 | Release (REL knob) | 15 ms | present | present | present | COMMON_TO_ENV1-4 |
| 6 | BPM/MS toggle | Present, tooltip "Env 1 BPM (Off)" | Present, tooltip pattern "Env N BPM" | Present | Present | COMMON_TO_ENV1-4 — STRUCTURAL_ACTION (boolean toggle) |
| 7 | Legato Inverted | Present in context menu, unchecked | Present, unchecked | Present | Present | COMMON_TO_ENV1-4 — STRUCTURAL_ACTION (boolean, per-envelope independent state) |
| 8 | Voice Steal Retrigger — option A | "From Stolen Voice Level" | "From Stolen Voice Level" | "From Stolen Voice Level" | "From Stolen Voice Level" | COMMON_TO_ENV1-4 |
| 8b | Voice Steal Retrigger — option B | **"From Zero"** (checked/default) | **"From Start Level"** (checked/default) | **"From Start Level"** (checked/default) | **"From Start Level"** (checked/default) | **ENV1-SPECIFIC vs ENV2-4-SPECIFIC** — the enum's second option differs by envelope role (see Section 2) |
| 9 | Mod-source drag handle ("Env N Source") | Present, tooltip "drag this to other controls, to map Envelope 1 to a desired control." | Present, same tooltip pattern | Present | Present | COMMON_TO_ENV1-4 — cross-reference to MATRIX (see Section 7) |
| 10 | Grid (Time/Beats) | Present in context menu (Time checked default) | Present | Present | Present | COMMON_TO_ENV1-4 — DISPLAY_ONLY |
| 11 | Envelope Auto-Zoom Switch | Present, tooltip "Enables an autozooming mode, where the view width will always fit the envelope length" | Present | Present | Present | COMMON_TO_ENV1-4 — DISPLAY_ONLY |
| 12 | Envelope Zoom Slider (up-arrow/magnify/down-arrow) | Present | Present | Present | Present | COMMON_TO_ENV1-4 — DISPLAY_ONLY |
| 13 | Envelope graph curve (direct drag points) | Present | Present | Present | Present | Alternate UI representation of controls #1-5 — NOT an additional control |

**No CONDITIONAL controls found** — nothing on any envelope appears/disappears based on the state of another control (unlike FILTER's type-dependent 4th knob).

---

## 2. Env1 vs Env2–4 Difference — Resolved Field-by-Field

**Known technical discrepancy:** `A_FILTERS_ENV_AUDIT.json` recorded Env1 = 8 VST3 fields, Env2/Env3/Env4 = 10 fields each.

**Resolution method:** Direct UI re-verification of each envelope's Voice Steal Retrigger submenu individually (not inferred from the field count).

**Finding:** ENV1's Voice Steal Retrigger second option is labeled **"From Zero"**; ENV2, ENV3, and ENV4 all show **"From Start Level"** for the identical menu position. This is a **genuine, UI-confirmed semantic divergence** between ENV1 and ENV2-4 — not a display artifact, not a value-representation quirk. It is architecturally consistent with ENV1's role: ENV1 is hardwired to amplitude (SUS shown in dB, always audible), so on voice-steal it retriggers "From Zero" (silence) makes literal sense; ENV2-4 are freely assignable to arbitrary destinations, where "From Start Level" (the envelope's own starting value, which may not be zero) is the meaningful concept.

**Does this account for the full 8-vs-10 technical field gap?** No — one differing enum *label* does not by itself require 2 extra VST3 fields; enum options are typically encoded as a single field regardless of label text. The label difference is evidence that ENV1 is **internally specialized** (a distinct code path for the amplitude-hardwired envelope) — consistent with, but not proof of, the exact origin of the 2 extra fields on ENV2-4. No further UI-visible control accounts for the remaining field-count difference. **Classification: PARTIALLY_RESOLVED_DISCOVERY_ARTIFACT** — the semantic layer is fully accounted for (9 controls each, verified identically present on all 4 tabs); the residual 2-field technical gap is very likely internal routing/destination-plumbing state exclusive to freely-assignable envelopes (ENV2-4 need to store/validate an arbitrary mod-matrix destination reference that ENV1, hardwired to amp, does not), which is non-user-facing and therefore does not add a semantic control. This does not block closure (P2, not P0/P1) since it does not indicate a missing user-facing control.

---

## 3. Hold — First-Class Semantic Control (Confirmed)

Direct UI tooltip, hovered live during this pass: **"Env 1 Hold (0.0 ms)" / "Hold time for selected Envelope."**

`Env{N}.Hold` is confirmed present, identical across all 4 envelopes, and is a genuine TARGET_GAP in `targets.py` (not a semantic-discovery gap). The official PDF's ATK/HOLD/DEC/SUS/REL screenshot is independently corroborated by this tooltip.

---

## 4. Grid / Legato Inverted / Voice Steal Retrigger — Full Classification

All three are accessed via the identical 3-item right-click context menu on the envelope graph, present identically on all 4 envelope tabs.

| Control | Exact UI location | Exact options | Changes modulation behavior? | Display preference? | Per-envelope or global? | Structural action? | User-facing semantic state? |
|---|---|---|---|---|---|---|---|
| Grid | Context menu → Grid submenu | Time (default) / Beats | NO — affects only graph X-axis rendering | YES | Per-envelope (menu re-opened identically on each tab; not verified whether the underlying value is stored per-instance or globally shared, but the control surface is per-envelope) | No | No — DISPLAY_ONLY |
| Legato Inverted | Context menu → direct checkbox item | Boolean (checked/unchecked) | YES — per PDF: "Force an envelope to always trigger at note on, even when legato is enabled" | No | Per-envelope (each envelope's own behavior toggle) | No | YES — semantic control |
| Voice Steal Retrigger | Context menu → submenu | "From Stolen Voice Level" / "From Zero" (ENV1) or "From Start Level" (ENV2-4) | YES — governs the envelope's value when a stolen voice is retriggered | No | Per-envelope, with an ENV1-specific option label (see Section 2) | No | YES — semantic control |

**Grid clarification (per user's explicit caution):** Grid = Time/Beats is confirmed DISPLAY_ONLY. It does not enter the 9-control semantic count — consistent with prior finding, now confirmed via live tooltip/menu re-inspection rather than assumption.

---

## 5. Voice Steal Retrigger — Ownership Resolution

**Exact modes confirmed via direct UI (corrected this pass):**
- ENV1: "From Stolen Voice Level" / **"From Zero"**
- ENV2/3/4: "From Stolen Voice Level" / **"From Start Level"**

**UI surface:** The menu is opened from each individual envelope's own graph right-click context menu — there is no global/shared "Voice Steal Retrigger" control found anywhere else in Serum's GLOBAL or VOICE panels during this session's inspection.

**Semantic owner determination:** Per the user's explicit instruction not to assume ownership from where the menu was opened, the question is whether this is conceptually an ENV-scoped setting or a VOICE/PERFORMANCE-scoped setting merely surfaced through the ENV UI.

**Resolution:** This is an **ENV-scoped semantic control** (`Env{N}.VoiceStealRetriggerMode`), not a VOICE/PERFORMANCE/GLOBAL control, for two independent reasons:
1. **State is provably per-envelope, not global** — ENV1 and ENV2-4 show *different enum option sets* for the same menu position. A single global VOICE/PERFORMANCE setting could not present different options depending on which envelope's context menu is opened. This is direct evidence the value is stored per-envelope-instance.
2. It governs this specific envelope's own output value at retrigger time (a per-envelope behavior), not a voice-allocation policy broadly (voice-stealing itself is decided elsewhere; this only controls what value *this envelope* restarts from).

`Env{N}.VoiceStealRetriggerMode` is retained as an ENV semantic control (4 instances, one per envelope), with the note that its exact option set is envelope-role-dependent (ENV1 vs ENV2-4).

---

## 6. Envelope Graph Controls — Display-Only, Confirmed

Both re-verified live this pass:
- **Envelope Auto-Zoom Switch** — tooltip: "Envelope Auto-Zoom Switch. Enables an autozooming mode, where the view width will always fit the envelope length (time scales automatically)." → DISPLAY_ONLY, confirmed.
- **Envelope Zoom Slider** (up-arrow / magnify / down-arrow compound control) → view navigation, DISPLAY_ONLY, unchanged from prior finding.

Neither changes envelope-editable curve/state — both excluded from the semantic control count, per the user's explicit caution.

---

## 7. Mod-Source Drag Handle — Cross-Reference, Not Duplicate

Tooltip (re-verified live): **"Env 1 Source" / "drag this to other controls, to map Envelope 1 to a desired control."**

This is the same underlying Matrix-assignment mechanism (dragging a modulation source handle onto a destination control creates a mod-matrix routing) used throughout Serum's modulation system (LFOs, Velocity, Note, Macros all expose an analogous handle). Per the user's explicit instruction, this is **not** given a duplicate semantic identity distinct from Matrix routing — it is recorded as `Env{N}.Source` (the ENV-side interaction point / drag origin) with an explicit cross-reference to the MATRIX section's modulation-routing semantics, to be fully reconciled when MATRIX is audited. `Env{N}.Source` remains one of the 9 per-envelope semantic controls (it is a genuine, distinct, user-facing affordance — the existence and location of the handle — even though the *routing outcome* it produces belongs conceptually to Matrix).

---

## 8. Source Reconciliation Table

| Element | Official PDF | Direct UI | Existing project evidence | Semantic result | Target status | Operation status |
|---|---|---|---|---|---|---|
| Attack | ✅ "ATK" visible in screenshot | ✅ confirmed, all 4 | targets.py: Env1-4.Attack exists | GENUINE_SEMANTIC | ✅ targeted | ❌ 0% |
| Hold | ✅ "HOLD" visible in screenshot | ✅ confirmed via tooltip, all 4 | targets.py: MISSING | GENUINE_SEMANTIC | ❌ TARGET_GAP | ❌ 0% |
| Decay | ✅ "DEC" visible | ✅ confirmed | targets.py: exists | GENUINE_SEMANTIC | ✅ targeted | ❌ 0% |
| Sustain | ✅ "SUS" visible | ✅ confirmed | targets.py: exists | GENUINE_SEMANTIC | ✅ targeted | ❌ 0% |
| Release | ✅ "REL" visible | ✅ confirmed | targets.py: exists | GENUINE_SEMANTIC | ✅ targeted | ❌ 0% |
| BPM/MS | ✅ "BPM: Envelopes now offer a BPM option" | ✅ confirmed via tooltip "Env N BPM" | targets.py: MISSING | GENUINE_SEMANTIC | ❌ TARGET_GAP | ❌ 0% |
| Legato Inverted | ✅ "Invert Legato" feature named | ✅ confirmed via context menu | targets.py: MISSING | GENUINE_SEMANTIC | ❌ TARGET_GAP | ❌ 0% |
| Voice Steal Retrigger | ❌ not named in PDF's brief summary | ✅ confirmed via context menu, all 4, with ENV1-specific option variant discovered | Not in any prior inventory | GENUINE_SEMANTIC (NEW DISCOVERY) | ❌ TARGET_GAP | ❌ 0% |
| Source (drag handle) | ❌ not named in PDF | ✅ confirmed via tooltip | Implicit only, never enumerated | GENUINE_SEMANTIC (cross-ref to MATRIX) | ❌ TARGET_GAP (N/A — routing handled via Matrix scope) | ❌ 0% |
| Grid | ❌ not in PDF | ✅ confirmed Time/Beats submenu | Not in prior inventory | DISPLAY_ONLY — excluded | N/A | N/A |
| Auto-Zoom Switch | ❌ not in PDF | ✅ confirmed via tooltip | Not in prior inventory | DISPLAY_ONLY — excluded | N/A | N/A |
| Zoom Slider | ❌ not in PDF | ✅ confirmed present | Not in prior inventory | DISPLAY_ONLY — excluded | N/A | N/A |

No code/target name was promoted into a semantic control without independent UI or documentation evidence — every row above has a direct UI confirmation this session.

---

## 9. Exact Closure Gate

- ✅ Every ENV1-4 user-facing control identified (13 elements catalogued in Section 1; 9 are genuine semantic controls, 3 are DISPLAY_ONLY, 1 is a redundant graph-representation of existing controls)
- ✅ Every conditional/context action classified (none found to be CONDITIONAL — all 9 semantic controls are unconditionally present on all 4 envelopes)
- ✅ Env1 vs Env2-4 differences reconciled field-by-field (Section 2) — genuine ENV1-specific enum-option variant found and documented; residual 2-field technical gap classified as non-user-facing internal state (P2, non-blocking)
- ✅ Display-only controls separated (Grid, Auto-Zoom, Zoom Slider — 3 controls, all confirmed via live tooltip/menu text this pass)
- ✅ Semantic ownership resolved (VoiceStealRetriggerMode = ENV-scoped, proven via per-envelope option-set divergence, not assumed from menu location; Source = ENV-side affordance cross-referenced to MATRIX, not duplicated)
- ✅ P0 = 0
- ✅ P1 = 0
- ✅ P2 = 1 (the residual Env1-vs-Env2-4 technical field-count gap, non-blocking, carried forward as a note for future CBOR-level engineering — does not represent a missing semantic control)

**ENV closure gate: P0=0, P1=0, P2=1 ≤ 1 → SATISFIED.**

---

## 10. Final Exact Counts

```
ENV1 semantic controls:              9   (Attack, Hold, Decay, Sustain, Release,
                                           BPM/MS, LegatoInverted,
                                           VoiceStealRetriggerMode[From Zero variant],
                                           Source)
ENV2 semantic controls:              9   (same 9 identities, VoiceStealRetriggerMode
                                           uses [From Start Level variant])
ENV3 semantic controls:              9   (identical structure to ENV2)
ENV4 semantic controls:              9   (identical structure to ENV2)

Shared controls (identical across all 4):    8   (Attack, Hold, Decay, Sustain,
                                                    Release, BPM/MS, LegatoInverted,
                                                    Source)
Env1-only controls:                          0   (no control EXCLUSIVE to Env1 —
                                                    VoiceStealRetriggerMode exists on
                                                    all 4, only its 2nd enum option
                                                    label differs)
Env2-4-only controls:                        0   (same reasoning)
Conditional controls:                        0
Display-only controls (shared, all 4):       3   (Grid, Auto-Zoom Switch, Zoom Slider)
Structural/context actions:                  2   (BPM/MS toggle, LegatoInverted —
                                                    both boolean-style structural
                                                    controls; VoiceStealRetriggerMode
                                                    is enum-structural, counted above)

TOTAL DISTINCT SEMANTIC CONTROLS (per envelope): 9
TOTAL CONCRETE TARGETS (9 × 4 envelopes):        36

Semantic target gaps (per envelope):   4   (Hold, BPM/MS, LegatoInverted,
                                             VoiceStealRetriggerMode)
                                        × 4 envelopes = 16 total target gaps
                                        (Source excluded — N/A, handled via Matrix scope)
Operation gaps:                       36   (0/36 implemented, 0%)

P0 = 0
P1 = 0
P2 = 1  (Env1-vs-Env2-4 residual technical field gap — non-blocking)
```

---

## 11. Refutation of Unverified External Claims (Curve, Velocity, Loop Mode, Env Amount)

During this pass, an external/unverified summary (not sourced from any file present on this machine — no "Serum 2 User Guide.pdf" exists locally; confirmed via filesystem search of Downloads and the Xfer Presets folder) claimed the ENV section also includes: **Curve, Velocity, Loop Mode, Env Amount (Depth)**. Per this project's epistemic rules (unknown stays unknown; no capability without admissible evidence), these claims were directly tested against the live Serum 2.0.21 UI rather than accepted:

| Claimed control | Test performed | Result |
|---|---|---|
| Curve (per-stage curve shape) | Dragged the midpoint of a visible Decay slope (with Sustain lowered to -3.1 dB to expose a non-flat segment) vertically by 60px | **NO visual change to curve shape** — the segment's curvature is fixed/algorithmic, not draggable. Also checked the Decay knob's right-click menu: only the 6 generic structural actions (Mod Source, Bypass Modulator, Remove Modulator(s), Reset Control, MIDI Learn, Lock Parameter) — no Curve entry. **REFUTED — no such control exists in this build.** |
| Velocity (note-velocity-to-envelope sensitivity) | Checked all ENV1 knobs, all context menus, and the ENV1 graph right-click menu (Grid/LegatoInverted/VoiceStealRetrigger only) | **No Velocity control found anywhere in the ENV panel.** Velocity-to-envelope-amount behavior in Serum is achieved via the Matrix (VELO is a separate modulation-source tab, not an ENV-owned parameter). **REFUTED as an ENV-section control** — velocity sensitivity is a Matrix-routing concept, out of ENV's scope entirely, not even a cross-reference item like Source. |
| Loop Mode | Checked ENV1 graph context menu (3 items only) and all 5 knob context menus (6 generic items only) | **No Loop Mode option found.** **REFUTED.** |
| Env Amount (Depth) | Checked all ENV1 controls; no amount/depth knob or field present on the ENV panel itself | **Not an ENV-panel control.** Modulation depth in Serum is set per-destination inside the Matrix (this is consistent with, and reinforces, the existing Source→MATRIX cross-reference already documented in Section 7) — it is not a property of the envelope itself, so it is **not** added as an ENV semantic control, even as a cross-reference (unlike Source, which IS a physical UI element on the ENV panel; Amount/Depth has no ENV-panel UI presence at all). |

**Conclusion: none of the 4 claimed additional parameters exist as ENV-panel controls in Serum 2.0.21.** The 9-control-per-envelope semantic matrix (Section 1) is unchanged and remains exhaustive. This refutation is retained as explicit negative evidence per the project's evidence-hierarchy discipline (direct UI inspection overrides an unverified external summary).

---

## Correction Log (vs ENV_SEMANTIC_RECONCILIATION.md / ENV_FINAL_CLOSURE_REPORT.md)

1. **VoiceStealRetriggerMode second option** was recorded as uniformly "From Start Level" across all 4 envelopes. **CORRECTED:** ENV1 = "From Zero"; ENV2/3/4 = "From Start Level". This is a genuine per-envelope semantic divergence, verified by individually opening all 4 envelopes' context menus (not a spot-check of 2).
2. **Env1 vs Env2-4 asymmetry** was previously classified as pure `RESOLVED_DISCOVERY_ARTIFACT` with no residual. **CORRECTED:** classified `PARTIALLY_RESOLVED_DISCOVERY_ARTIFACT` — the semantic layer is fully accounted for, but a genuine ENV1-specific behavioral variant (finding #1) is now documented, and the small residual technical-field gap is retained as a non-blocking P2 note rather than declared fully closed with zero residue.
3. Total semantic-control count (9 per envelope, 36 total) is **unchanged** — this pass found a variant within an existing control, not a new or missing control.
4. An unverified external claim (Curve, Velocity, Loop Mode, Env Amount as additional ENV controls, allegedly from a local "Serum 2 User Guide.pdf" that does not exist on this machine) was tested directly against the UI and **refuted in full** (Section 11). No inventory changes resulted.

---

Generated: 2026-09-15
Authority: Official "Serum 2 What's New" PDF (Xfer Records, v1.0.0, March 17 2025) + direct Serum 2.0.21 UI inspection of all 4 envelope instances individually
Version lock: Serum 2.0.21 only
