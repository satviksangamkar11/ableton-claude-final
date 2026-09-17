# SERUM2 Complete Executable Control Plan

**Date:** 2026-09-17
**Status:** Ready to Execute
**Total Semantics:** 908 (frozen)
**Total Targets:** 396 (frozen)
**Families:** 9

---

## Executive Summary

Converting 908 frozen semantic records into a complete executability matrix using **family-first qualification** instead of row-by-row.

**Key insight:** Most controls in a family share the same execution mechanism. Prove the family once, verify members lightly.

**Estimated deep experiments:** 12-20 (not 908)
**Estimated lightweight verifications:** 600+
**Estimated total effort:** 20-40 hours for complete matrix + admission integration

---

## Phase D — Minimum Deep Experiments (12-20 experiments)

### Family 1: HOST_PARAMETER_SCALAR (238 members)

**Challenge:** Covers OSC, ENV, FILTER, LFO, MACRO scalars. Need to prove: mutation, readback, persistence.

**Already proven:** ENV1.RELEASE (CAUSAL_VERIFIED) — one deep experiment for ENV done.

**Remaining need:**

| Priority | Experiment | Semantic | Rationale | Status |
|----------|---|---|---|---|
| 1 | OSC representative | OSC1.LEVEL | OSC is 120 members (50% of family). Replicate Release: mutate, readback, measure. | TODO |
| 2 | Filter scalar | FILTER1.CUTOFF | Filter is 12 members. Verify mutation to body field (not bare VST3). | TODO |
| 3 | LFO scalar | LFO1.RATE | LFO is 30 members. Verify conditional on LFO mode. | TODO |
| 4 | Macro scalar | MACRO.01.VALUE | Macro is 44 members. Verify knob assignment. | TODO |

**Acceptance criteria per experiment:**
- pre-state captured
- mutation to target value (contract-derived, not guess)
- readback matches mutation
- persistence across Serum save/load
- measurement indicates effect
- no contradictions

**Lightweight member verification:** For each family member post-representative:
1. Resolve target or operation
2. Attempt mutation
3. Readback value
4. Type/range check
5. No exceptions → LIGHTWEIGHT_VERIFIED
6. Exception or contradiction → escalate to deep experiment

---

### Family 2: BODY_STATE_FIELD_CONDITIONAL (88 members)

**Challenge:** Only meaningful when parent state has specific value (filter type, LFO mode).

**Already known:** Filter type is enum (FastLP, StateVar, etc.). LFO mode is enum.

**Remaining need:**

| Priority | Experiment | Semantic | Rationale | Status |
|----------|---|---|---|---|
| 1 | Filter type 1 params | FILTER1.TYPE_SPECIFIC.FREQ2 | Covers ~40 members. Set Filter1.Type to FastLP, verify FREQ2 readback, mutate, readback again. | TODO |
| 2 | LFO mode representative | LFO1.SHAPE_SPECIFIC.UNISON | Covers ~48 members. Set LFO1.Shape to Triangle, verify UNISON readback. | TODO |

**Acceptance criteria:**
- parent state set to required value
- target field is not null/absent when parent matches
- mutation succeeds
- readback confirms
- parent state change causes field to become absent/null (verification of dependence)

**Lightweight member verification:** For each conditional member:
1. Set parent state to required value
2. Readback field value
3. Attempt mutation
4. Readback post-mutation
5. Change parent state to other value; field should become N/A or change meaning

---

### Family 3: MATRIX_ROUTE_ASSIGNMENT (104 members)

**Challenge:** 70 members in MATRIX section (matrix rows 1-16, each with source/destination/amount).

**Status:** PARTIAL_ESTABLISHED (control path matrix marks as ESTABLISHED)

**Remaining need:**

| Priority | Experiment | Semantic | Rationale | Status |
|----------|---|---|---|---|
| 1 | Matrix source | MATRIX.ROW1.SOURCE | Prove source assignment readback and mutation. Assume applies to rows 2-16. | TODO |
| 2 | Matrix destination | MATRIX.ROW1.DESTINATION | Prove destination readback. | TODO |
| 3 | Matrix amount | MATRIX.ROW1.AMOUNT | Prove amount scalar readback and mutation. | TODO |

**Lightweight member verification:** Once ROW1 (source, dest, amount) proven:
- Rows 2-16: re-use same logic
- Other MATRIX semantics (ENV+GLOBAL): verify source/destination reference same mechanism

**Acceptance criteria:**
- source: readback shows actual assigned source (enum value or ID)
- destination: readback shows actual assigned destination (enum value or ID)
- amount: readback shows decimal value (0.0-1.0)
- all three persist across save/load

---

### Family 4: UI_ACTION_TOGGLE_BUTTON (198 members)

**Challenge:** No direct readback; success verified by UI state or side effect.

**Status:** CANDIDATE (needs verification across sections)

**Remaining need:**

| Priority | Experiment | Semantic | Rationale | Status |
|----------|---|---|---|---|
| 1 | Macro name toggle | MACRO.01.NAME | Toggle macro name edit mode in Live. Verify UI responds (name field becomes editable). | TODO |
| 2 | ARP sync toggle | ARP.PATTERN.SYNCED | Toggle ARP sync. Verify ARP pattern changes sync behavior. | TODO |
| 3 | FX UI action sample | FX.COMPRESSOR.ENABLED (if exists) | Verify effect enable toggle works via Live UI. | TODO |

**Lightweight member verification:** Per section:
- ARP: 26 members → test 2-3 representatives (pattern sync, pattern shape, etc.), apply to rest
- CLIP: 21 members → test 2-3 (play, stop, loop), apply to rest
- MACRO: 21 members → test 2-3 (name, type, assign), apply to rest
- GLOBAL_KEYBOARD: 13 members → test 2-3 (pedal assign, velocity curve), apply to rest
- Others: lighter sampling

**Acceptance criteria:**
- Action via Live UI succeeds (no error, UI responds)
- Serum state reflects change (visual inspection)
- Action repeatable
- No crash or exception

---

### Family 5: RESOURCE_OPERATION_BROWSER (41 members)

**Status:** FULLY_ESTABLISHED (pure UI navigation)

**No deep experiment required.** Browser operations (load preset, select sample, navigate folder) are user-facing UI actions.

**Lightweight verification:** Verify 3-5 representatives (load preset, load sample, navigate), assume rest work identically.

---

### Family 6: SHARED_PHYSICAL_PARAMETER_MULTI_SEMANTIC (46 members)

**Challenge:** One VST3 parameter or state field represents multiple semantic controls.

**Example:** MIXER.SUB.ENABLE and MIXER.SUB.PAN both read/write same SUB.Enable state.

**Remaining need:**

| Priority | Experiment | Semantic | Rationale | Status |
|----------|---|---|---|---|
| 1 | Mixer SUB enable | MIXER.SUB.ENABLE | Prove enable state mutation and readback for sub. Covers 2-3 semantics. | TODO |
| 2 | Mixer SEND enable | MIXER.SEND1.ENABLE | Prove send enable state mutation. Covers ~3 semantics per send. | TODO |

**Lightweight member verification:** For each shared physical parameter:
- Prove representative (SUB or SEND)
- All semantics sharing that parameter: readback only (no new mutation)

**Acceptance criteria:**
- Multiple semantics use same state field
- Mutation reflected in all semantics' readback
- State persists

---

### Family 7: STRUCTURAL_OPERATION_CONTEXT_MENU (10 members)

**Status:** FULLY_ESTABLISHED (pure UI structural)

**No deep experiment required.** Context menu operations (add module, reorder, bypass) are user-facing actions.

**Lightweight verification:** Verify 2-3 (add FX, bypass FX), assume rest work.

---

### Family 8: MULTI_TARGET_LINKED_CONTROL (2 members)

**Challenge:** One semantic controls multiple targets (graphic EQ affects both Filter 1 and 2).

**Remaining need:**

| Priority | Experiment | Semantic | Rationale | Status |
|----------|---|---|---|---|
| 1 | Graphic multi-target | MIXER.FILTER1.GRAPHIC_CUTOFF_RESONANCE | Mutate both Filter1.Cutoff and Filter1.Resonance; verify both readback. | TODO |

**Lightweight member verification:** MIXER.FILTER2 uses same mechanism; no separate experiment.

---

### Family 9: UNKNOWN_GAP_CLUSTER (169 members)

**Challenge:** 83 FX unknowns, 28 GLOBAL unknowns, others. Likely misclassified or incomplete.

**Investigation strategy:**

1. **FX unknowns (83):** Sample 5-10 semantics (BODE, CHORUS, DISTORTION, etc.). For each:
   - Check if VST3 parameter exists (DawDreamer interrogation)
   - If yes → reclassify as HOST_PARAMETER
   - If no → check Live UI → reclassify as UI_ACTION

2. **GLOBAL unknowns (28):** Sample 5-10. Check code for implementation route.
   - OVERSAMPLING, TUNING, QUALITY likely HOST_PARAMETER or settings
   - VOICE_CONTROL likely MATRIX_ROUTE or special handling

3. **Other unknowns (16 ARP + 17 MACRO + others):** Light categorization, then escalate as needed.

**Acceptance criteria:** Reclassify each unknown into proper family OR mark as BLOCKING_ISSUE if execution mechanism not found.

---

## Phase E — Lightweight Member Verification (600+)

For each family, after representatives are proven:

**HOST_PARAMETER:** 238 members
- OSC (120): 1 representative + 119 light verify
- ENV (32): 1 proven (Release) + 31 light verify  
- FILTER (12): 1 representative + 11 light verify
- LFO (30): 1 representative + 29 light verify
- MACRO (44): 1 representative + 43 light verify

**BODY_STATE_FIELD:** 88 members
- FILTER (40): 1 representative per condition + light verify
- LFO (48): 1 representative per condition + light verify

**UI_ACTION:** 198 members
- Per-section sampling: test 2-3 per section, apply to rest

**MATRIX_ROUTE:** 104 members
- Rows 2-16: reuse Row1 logic
- Other MATRIX: verify reference same mechanism

And so on for other families.

**Timeline:** 8-16 hours of systematic verification (mostly automated/scripted).

---

## Phase F — Exception Clusters

After main verification, identify:

- Controls that don't fit any family (resurface as BLOCKED)
- Controls with conflicting evidence (resurface as CONFLICTED)
- Controls with conditional behavior not yet modeled (escalate)
- Resource-dependent controls (e.g., IR loading, wavetable selection)

---

## Phase G — Capability Generation

Once families are qualified, generate CapabilityContracts for each:

```json
{
  "semantic_id": "OSC1.LEVEL",
  "execution_family": "HOST_PARAMETER_SCALAR",
  "status": "CAUSAL_VERIFIED",
  "target": "osc_level",
  "prerequisites": [],
  "measurement_definition_id": "...",
  "qualification_evidence": ["experiment_osc1_level_001.pkl"],
  "scope": {
    "tested_context_only": true,
    "mutation_value_used": 1.0
  },
  "limitations": "Single value tested; generalization pending 4.3"
}
```

**Count:** ~900 new contracts (one per admitted family member)

---

## Phase H — Admission Integration

Wire all 900+ new contracts into the existing ContractRegistry.

Update `serum2/producer/contract_registry.py` to load qualified semantics.

Maintain the admission gate (no bypass, no shortcut).

---

## Phase I — Final 908-Row Matrix

Produce `SERUM2_COMPLETE_EXECUTABLE_CONTROL_MATRIX.json`:

```json
{
  "records": [
    {
      "semantic_id": "ENV1.ATTACK",
      "section": "ENV",
      "module": "ENV1",
      "execution_family": "HOST_PARAMETER_SCALAR",
      "target_or_operation": "envelope_field_attack",
      "execution_status": "EXECUTABLE_CAUSAL_VERIFIED",
      "verification_status": "DEEP_EXPERIMENT",
      "qualification_status": "CAUSAL_VERIFIED",
      "admission_status": "ADMITTED",
      "evidence_refs": ["ep_producer_e2e_PASS_001.json", "experiments/_env_attack_qualified_complete_001.pkl"],
      "notes": "Prerequisite: Decay=0.02"
    },
    ...
  ]
}
```

All 908 rows, no silent rows.

---

## Phase J — Optimization Report

Produce `SERUM2_EXECUTION_COVERAGE_REPORT.json`:

```json
{
  "totals": {
    "total_semantics": 908,
    "total_targets": 396
  },
  "by_status": {
    "EXECUTABLE_CAUSAL_VERIFIED": 200+,
    "EXECUTABLE_VERIFIED": 400+,
    "EXECUTABLE_UNVERIFIED": 100+,
    "NO_CURRENT_PATH": X,
    "BLOCKED": Y,
    "CONFLICTED": Z
  },
  "by_family": {
    "HOST_PARAMETER_SCALAR": 238,
    ...
  },
  "experiments_performed": 12-20,
  "experiments_avoided_by_family_reuse": 880-888,
  "verification_methods": {
    "deep_experiment": 20,
    "lightweight_readback": 600,
    "ui_action_verify": 150,
    "structural_verify": 20
  }
}
```

---

## Completion Checklist

- [ ] Phase D: 12-20 deep experiments completed and documented
- [ ] Phase E: 600+ lightweight verifications completed
- [ ] Phase F: Exception clusters identified and resolved
- [ ] Phase G: 900+ CapabilityContracts generated
- [ ] Phase H: All contracts integrated into admission system
- [ ] Phase I: 908-row complete executability matrix produced
- [ ] Phase J: Coverage report and gap summary produced
- [ ] All 908 rows have explicit evidence-backed dispositions
- [ ] Frozen semantic count unchanged (908)
- [ ] Frozen target count unchanged (396)
- [ ] No target-specific hardcoding introduced
- [ ] Admission gate maintains fail-closed behavior
- [ ] Producer planner consumes only ADMITTED capabilities

---

## Next Action

Begin Phase D: Execute minimum deep experiments starting with highest-priority families.

**Start:** HOST_PARAMETER_SCALAR family (OSC representative experiment)
