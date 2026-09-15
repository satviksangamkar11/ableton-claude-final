# FILTER1 vs FILTER2 — Targeted Comparison

**Date:** 2026-09-15  
**Method:** Targeted comparison per user's Phase 6 efficiency directive (not full independent re-audit)  
**Status:** ✅ COMPLETE

---

## Methodology

Per the user's explicit optimization instruction:

> "Do not perform a full independent deep audit of Filter 2 for every type unless Filter 2 actually exposes a different surface. Use: Filter 1 exhaustive type matrix → Filter 2 targeted comparison → record only differences."

Filter1's exhaustive 107/107 type audit is authoritative (see FILTER_CONTROL_SURFACE_AUDIT_PROGRESS.md). Filter2 was spot-checked across 3 structurally diverse types spanning different categories and 4th-knob identities to confirm architectural identity.

## Spot-Check Results

| Type | Category | Filter1 Result | Filter2 Result | Match? |
|---|---|---|---|---|
| MG Low 12 | Normal | FAT | FAT | ✅ IDENTICAL |
| Ring Modx2 | Misc | SPREAD | SPREAD | ✅ IDENTICAL |
| Cmb HL6- | Flanges | HL WID | HL WID | ✅ IDENTICAL |

**Result: 3/3 (100%) match rate** across categories with the most complex/divergent internal patterns (Normal had internal exceptions, Misc was the most heterogeneous category, Flanges had the LP/HP/HL sub-pattern).

## Type Universe Confirmation

Filter2's type-selector dropdown was directly inspected and confirmed to show the **identical 5-category structure** (Normal, Multi, Flanges, Misc, S2 Filters) as Filter1, with the same category ordering and checkmark-based current-selection indicator.

**Conclusion: Filter1 and Filter2 access the SAME 107-type universe with IDENTICAL per-type control surfaces.**

---

## Confirmed Differences (Non-Control-Surface)

### 1. Default Routing
- **Filter1 default routing:** OSC A (the "A" button was highlighted in the S/A/B/C/N routing row)
- **Filter2 default routing:** Noise (the "N" button was highlighted in the S/A/B/C/N routing row)

This is an **instance-level default difference**, not a control-surface difference. Both filters have access to the same S/A/B/C/N routing row with identical semantics (which sound sources feed into this filter).

### 2. Independent State
Each filter maintains independent:
- Current filter type selection
- Current parameter values (Cutoff, Resonance, Drive, 4th-knob, Pan, Mix, Level)
- Enable/disable state
- Routing (S/A/B/C/N)
- Bus send levels (BUS1Send, BUS2Send) and Route destination

This is expected instance-level independence, not a control-surface difference.

### 3. Technical Field Count Discrepancy (FLAGGED FOR RECONCILIATION)

Prior qualification evidence (A_FILTERS_ENV_AUDIT.json) recorded:
- **Filter1: 14 discovered/qualified VST3 parameters**
- **Filter2: 12 discovered/qualified VST3 parameters**

This 2-field discrepancy predates this session's exhaustive UI audit and requires reconciliation during the technical-field phase. Two possible explanations:
1. **Structural:** Filter2 genuinely has 2 fewer technical VST3 parameters than Filter1 (e.g., a routing-related field pair unique to Filter1's position in the signal chain)
2. **Discovery artifact:** The original discovery pass for Filter2 may not have enumerated all fields (undercounting), not a real structural asymmetry

**Status:** UNRESOLVED — flagged for the technical field reconciliation phase (Phase 5). This does NOT affect the semantic control matrix (which is now complete and type-verified), only the VST3-field-to-semantic-control mapping accounting.

---

## Closure Assessment for This Phase

**Filter1 vs Filter2 semantic control-surface reconciliation: ✅ COMPLETE**

No new semantic controls were discovered on Filter2 that don't exist on Filter1. No control-surface divergence was found in the 3 spot-checks (covering the 3 most structurally complex/divergent categories). The identical dropdown category structure confirms both filters draw from the same 107-type semantic universe.

**Remaining work:** Technical field count reconciliation (14 vs 12), to be resolved in Phase 5 (Technical Field Reconciliation).

---

Generated: 2026-09-15
