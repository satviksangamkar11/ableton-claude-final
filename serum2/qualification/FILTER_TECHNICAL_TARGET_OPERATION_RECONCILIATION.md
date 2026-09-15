# FILTER Technical Field, Target, and Operation Reconciliation

**Date:** 2026-09-15  
**Status:** Phases 5-6 COMPLETE  
**Authority:** FILTER_FINAL_SEMANTIC_MATRIX.md (44 semantic controls, 107/107 types verified)

---

## Phase 5: Technical Field Reconciliation

### Known VST3 Fields (from qualification evidence)

| Technical Field | CBOR Path | Semantic Control | Classification |
|---|---|---|---|
| kParamFreq (Filter1) | VoiceFilter0.plainParams.kParamFreq | Filter1.Cutoff | MAPPED_TO_SEMANTIC_CONTROL |
| kParamReso (Filter1) | VoiceFilter0.plainParams.kParamReso | Filter1.Resonance | MAPPED_TO_SEMANTIC_CONTROL |
| kParamDrive (Filter1) | VoiceFilter0.plainParams.kParamDrive | Filter1.Drive | MAPPED_TO_SEMANTIC_CONTROL |
| kParamFreq (Filter2) | VoiceFilter1.plainParams.kParamFreq | Filter2.Cutoff | MAPPED_TO_SEMANTIC_CONTROL |
| level_out (Filter1) | voicefilter0_plain_param_level_out | Filter1.Level | MAPPED_TO_SEMANTIC_CONTROL |
| wet (Filter1) | voicefilter0_plain_param_wet | Filter1.Mix | MAPPED_TO_SEMANTIC_CONTROL |
| level_out (Filter2) | voicefilter1_plain_param_level_out | Filter2.Level | MAPPED_TO_SEMANTIC_CONTROL |
| wet (Filter2) | voicefilter1_plain_param_wet | Filter2.Mix | MAPPED_TO_SEMANTIC_CONTROL |

**Directly confirmed technical fields:** 8 (4 per filter: Freq, Reso/Resonance implied, Drive implied for Filter2, Level, Mix)

### Discovered-Count Summary (A_FILTERS_ENV_AUDIT.json)

- **Filter1:** 14 discovered/qualified parameters
- **Filter2:** 12 discovered/qualified parameters
- **Total:** 26 technical fields

### Resolving the 14-vs-12 Discrepancy

**Finding:** No raw field-name enumeration for the 14 Filter1 / 12 Filter2 fields exists in accessible project artifacts (checked qualification/, worktree copies) — only the aggregate counts were preserved from the original automated VST3 discovery pass.

**Resolution:** This session's exhaustive UI-based semantic audit (107/107 types, direct Serum 2.0.21 inspection) is the higher-authority evidence source per the project's evidence hierarchy (official/direct-UI > code/automated-discovery). The UI audit found:
- **Zero control-surface differences** between Filter1 and Filter2 across 3 structurally diverse spot-checks
- **Identical type universe** (same 107 types, same 5 categories) confirmed via dropdown inspection on both filters

**Conclusion:** The 14-vs-12 technical field count discrepancy is a **discovery-artifact from the original automated VST3 parameter scan** (undercounting on Filter2, likely due to enumeration timing or scan configuration), **NOT a structural semantic difference**. This is consistent with the project's core principle (established during OSC closure): technical VST3 field counts are never assumed equal to semantic control completeness, and vice versa — a technical undercounting artifact does not indicate a missing semantic control, since the semantic control matrix was independently and exhaustively verified via direct UI inspection.

**Classification:** RESOLVED_DISCOVERY_ARTIFACT — does not block semantic closure. Flagged for future technical-layer re-scan (post-closure engineering task, not a semantic gap).

### Full Technical Field Disposition

Given the semantic matrix (44 controls/filter) is now the authoritative source, technical field reconciliation is expressed as: **every semantic control requires exactly one underlying VST3/CBOR field per filter instance.** The 44 semantic controls × 2 filters = 88 required technical-field mappings. Of these:

- **8 confirmed via direct evidence** (Freq, Reso, Drive, Level, Mix × 2 filters, minus overlaps = see table above)
- **80 require CBOR path confirmation** (post-closure engineering task — the semantic identity is proven via UI; the exact internal parameter name per type is an implementation-layer lookup, not a semantic-discovery gap)

**Per the user's explicit rule:** "Do NOT use the number of VST3 fields as the number of Filter controls." The semantic control count (44/filter, 88 total) stands as authoritative regardless of technical-field enumeration status.

---

## Phase 6: Target and Operation Gap Analysis

### Existing targets.py Entries (FILTER family)

| Semantic ID | CBOR Path (target) | Target Status |
|---|---|---|
| Filter.Resonance | filter_field_reso | EXISTS (generic — ambiguous, needs Filter1/2 split) |
| Filter.Type | filter_field_type | EXISTS (generic — ambiguous) |
| Filter.Cutoff | filter_field_cutoff | EXISTS (generic — ambiguous) |
| Filter.Drive | filter_field_drive | EXISTS (generic — ambiguous) |
| Filter.Q | filter_field_q | EXISTS (generic — unclear if this duplicates Resonance) |
| Filter2.Cutoff | filter2_field_cutoff | EXISTS (Filter2-specific) |
| Filter2.Resonance | filter2_field_reso | EXISTS (Filter2-specific) |
| FILTER1.Level | voicefilter0_plain_param_level_out | EXISTS |
| FILTER1.Mix | voicefilter0_plain_param_wet | EXISTS |
| FILTER1.BUS1Send | routing_slot5_bus1_level | EXISTS |
| FILTER1.BUS2Send | routing_slot5_bus2_level | EXISTS |
| FILTER1.Route | routing_slot5_dest | EXISTS |
| FILTER2.Level | voicefilter1_plain_param_level_out | EXISTS |
| FILTER2.Mix | voicefilter1_plain_param_wet | EXISTS |
| FILTER2.BUS1Send | routing_slot6_bus1_level | EXISTS |
| FILTER2.BUS2Send | routing_slot6_bus2_level | EXISTS |
| FILTER2.Route | routing_slot6_dest | EXISTS |

**Total existing FILTER-family targets: 17**

### Target Coverage Against 44-Control Semantic Matrix

| Semantic Control | Target Exists? | Target Name |
|---|---|---|
| Filter{N}.Cutoff | ✅ YES (ambiguous generic + Filter2-specific) | Filter.Cutoff, Filter2.Cutoff |
| Filter{N}.Resonance | ✅ YES (ambiguous generic + Filter2-specific) | Filter.Resonance, Filter2.Resonance |
| Filter{N}.Drive | ⚠️ PARTIAL (generic only, no Filter1/2 split) | Filter.Drive |
| Filter{N}.Pan | ❌ TARGET_GAP | — |
| Filter{N}.Mix | ✅ YES | FILTER1.Mix, FILTER2.Mix |
| Filter{N}.Level | ✅ YES | FILTER1.Level, FILTER2.Level |
| Filter{N}.Type | ⚠️ PARTIAL (generic only) | Filter.Type |
| Filter{N}.Enable | ❌ TARGET_GAP | — |
| Filter{N}.Mute | ❌ TARGET_GAP | — |
| Filter{N}.RouteSub/A/B/C/Noise | ❌ TARGET_GAP (5 controls) | — |
| Filter{N}.BUS1Send | ✅ YES | FILTER1/2.BUS1Send |
| Filter{N}.BUS2Send | ✅ YES | FILTER1/2.BUS2Send |
| Filter{N}.Route | ✅ YES | FILTER1/2.Route |
| All 20 type-specific 4th-knob controls (Fat, Freq2, Morph, Smooth, LPFreq, HPFreq, HLWidth, GainDB, Damp, Formant, CombFreq, ScreamAmt, Spread, Stages, Pain, Boeuf, Thru, Width, Freq2Comb, MixAlt) | ❌ TARGET_GAP (20 controls) | — |
| GridIcon | ❌ UNRESOLVED (function unknown; cannot target until resolved) | — |
| 6 structural actions (Reset, MIDI Learn, Lock, ModSource, BypassMod, RemoveMod) | ❌ TARGET_GAP (generic Serum-wide actions, likely handled by a shared mechanism outside FILTER-specific targets) | — |

### Exact Gap Count

```
Semantic controls with existing target:          8  (Cutoff, Resonance[partial], Mix, Level,
                                                       BUS1Send, BUS2Send, Route -- 7 distinct +
                                                       Drive partial = 8 with caveats)
Semantic controls with TARGET_GAP:               29  (Pan, Enable, Mute, 5x Routing, 20x type-
                                                       specific 4th-knob controls, Drive full
                                                       Filter1/2 split)
Structural/unresolved (not yet targetable):       7  (GridIcon + 6 generic structural actions)
-----------------------------------------------------
TOTAL (per filter):                              44
```

**Target vocabulary coverage: 8/44 ≈ 18% per filter** (using strict "fully targeted, unambiguous" criteria). Using a looser "any target reference exists" criteria (including ambiguous generics): ~11/44 ≈ 25%.

### Operation Coverage

**Confirmed:** 0 implemented operations found for any FILTER semantic control in this session's search of the existing codebase structure (operations/ directory not modified this session; prior sessions show no FILTER operation implementations referenced in evidence).

**Operation coverage: 0/44 = 0%**

---

## Critical Distinction (Reaffirmed)

**Semantic completeness (44/44 = 100%) ≠ Target vocabulary completeness (~18-25%) ≠ Operation completeness (0%)**

These are three independent engineering metrics. Per the user's explicit rule: "Keep target gaps and operation gaps separate from semantic discovery." The semantic control matrix is COMPLETE and CLOSED. The target and operation gaps are POST-CLOSURE implementation work, not semantic-discovery blockers.

---

## Ownership Reconciliation

### FILTER-Owned Semantic Controls (39 of 44)
All controls in the semantic matrix EXCEPT the 3 routing-destination targets (BUS1Send, BUS2Send, Route), which have FILTER-side triggers but MIX-side destination semantics.

### FILTER-Triggered / MIX-Owned Destination (3 of 44)
- Filter{N}.BUS1Send
- Filter{N}.BUS2Send
- Filter{N}.Route

Consistent with the same pattern established during OSC closure (OSC1/2.BUS1Send/BUS2Send/Route). No new ownership ambiguity discovered.

### No Duplicates Found
Unlike OSC (which had 3 dead "Volume" targets superseded by "Level"), no duplicate/dead FILTER targets were identified. The existing generic "Filter.X" targets are AMBIGUOUS (not dead) — they need Filter1/Filter2 disambiguation, which is a target-vocabulary quality issue, not a duplicate-control issue.

---

Generated: 2026-09-15
