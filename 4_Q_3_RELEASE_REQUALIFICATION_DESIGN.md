# 4.Q.3 — RELEASE REQUALIFICATION DESIGN (4.1 Scope)

**READ-ONLY DESIGN. Constrained to authority substrate proof (4.1). Do not implement. Do not run experiments.**

---

## PURPOSE

Build a single fresh Release CapabilityContract with complete context provenance and independent causal determination to support 4.1 authority substrate proof.

The fresh qualification must independently establish whether the tested mutation produces EFFECT_OBSERVED. If NO_OBSERVED_EFFECT is measured, the fresh qualification fails and does not produce an authorizing contract. The archived Release contract is NOT a fallback.

---

## 1. QUALIFICATION OBJECTIVE

Establish, through fresh independent evidence:

- **Semantic target:** `envelope_field_release`
- **Allowed operation:** `mutate_numeric_value`
- **Mutation tested (singular):** Release parameter = 1.0 (absolute parameter value, not a delta)
- **Context tested:** Decay parameter = 0.02 (captured from live Serum readback)
- **Measurement:** tail_rms_db using kernel `tail_rms_db:c6a68e551ef9`
- **Isolation:** Single-field
- **Causal outcome:** To be determined by measurement. If EFFECT_OBSERVED → CAUSAL_VERIFIED contract. If NO_OBSERVED_EFFECT → NEGATIVE_EVIDENCE contract (non-authorizing).

**NOT attempting:**
- Multi-value mutation authority
- Context ranges or generalization
- Candidate grid extension
- Detune or Attack scope
- Architectural changes beyond contract schema

**Design principle:** The causal result is an experimental outcome, not a design assumption. The qualification succeeds if it proves the effect; it fails if it does not.

---

## 2. CONTEXT CAPTURE SPECIFICATION

### 2.1 Authoritative Context Source

**Definition:** The baseline parameter state at which the experiment begins.

**Capture method:** Live Serum readback via get_parameter() before any mutation.

**Baseline_overrides required:**

| Parameter | Required Value | Capture Method | Authority |
|-----------|---|---|---|
| Env0.plainParams.kParamDecay | 0.02 | get_parameter at baseline | Live readback (NOT inferred) |

**Context must be verified to be exactly 0.02 before mutation occurs.** If Decay ≠ 0.02 at baseline, the experiment cannot proceed (context precondition violated).

### 2.2 EvidenceRecord Structure

EvidenceRecord.experiment dict MUST contain:

| Field | Value | Source | Authoritative |
|-------|-------|--------|---|
| `mutations` | `[{target_path: "Env0.plainParams.kParamRelease", value: 1.0}]` | Measured | set_parameter + readback verification |
| `isolation_level` | `"single_field"` | Declared | SINGLE_FIELD required |
| `prerequisites` | `[]` | Declared | No uncontrolled dependencies |
| `baseline_overrides` | `[{target_path: "Env0.plainParams.kParamDecay", value: 0.02}]` | **Live readback** | **Non-negotiable** |
| `experiment_condition_signature` | Computed | Deterministic | `canonical.experiment_condition_signature({prerequisites: [], baseline_overrides: [["Env0.plainParams.kParamDecay", 0.02]]})` |
| `claim_subject` | `"Env1.Release"` | Semantic | Intent mapping |
| `claim_predicate` | `"extends"` | Semantic | Effect type |
| `notes` | Qualitative description | Free text | Traceability; no authority |

**CRITICAL:** baseline_overrides MUST be populated from actual live Serum readback at experiment baseline. NOT inferred from archived evidence, design documents, or prior experiments.

---

## 3. STIMULUS SPECIFICATION

**Exact provenance:**

The stimulus is informed by but NOT copied from the archived ENV-RELEASE evidence (experiment ID: `ENV-RELEASE`, condition_signature_hash: `2ad6168671cfac32`).

The fresh qualification must use the same **nominal** stimulus to maintain measurement comparability, but it is a fresh independent experiment.

**Stimulus definition:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| MIDI note | 60 (C3) | Same as ENV-RELEASE for comparability |
| Velocity | 110 | Same as ENV-RELEASE for comparability |
| Note length | 0.4s | Same as ENV-RELEASE for comparability |
| Render window | 2.0s | Same as ENV-RELEASE for comparability |
| Tail measurement | last 0.2s (0.6–2.0s) | Same as ENV-RELEASE for comparability |

**Measurement justification:** The archived ENV-RELEASE experiment used these parameters and produced EFFECT_OBSERVED (delta=+204.48 dB). Using the same stimulus in the fresh qualification allows direct comparison and avoids confounding stimulus variance with the requalification question.

**Stimulus source attribution:** Archived ENV-RELEASE evidence (experiment_id: "ENV-RELEASE", collected during prior Step 3.2 qualification).

---

## 4. MEASUREMENT SPECIFICATION

### 4.1 Causal Measurement

**CausalMeasurement schema:**

| Field | Value | Notes |
|-------|-------|-------|
| metric | `"tail_rms_db"` | Tail region RMS in dB |
| target.field_path | `"Env0.plainParams.kParamRelease"` | The mutated parameter |
| measurement_definition_id | `"tail_rms_db:c6a68e551ef9"` | Exact kernel ID from archived evidence |
| baseline | Live measurement (0.6–2.0s window) | Measured from control arm |
| treatment | Live measurement (0.6–2.0s window) | Measured from treatment arm (Release=1.0) |
| delta | treatment - baseline | Computed difference |
| expected_direction | `"increase"` | Longer release → higher tail RMS |
| threshold | 1.0 dB | Minimum delta to pass |

### 4.2 Causal Outcome Determination

**Measurement gates:**

```
Render and measure both arms
  ↓
Extract delta = treatment - baseline
  ↓
Compare to threshold (1.0 dB)
  ↓
Check direction: observed_direction == expected_direction
  ↓
Outcome?
   ├─ delta passes threshold AND direction correct
   │  → status = EFFECT_OBSERVED
   │
   ├─ delta fails threshold OR direction wrong
   │  → status = NO_OBSERVED_EFFECT
   │
   └─ measurement error / inconclusive
      → status = INCONCLUSIVE or NOT_RUN
```

### 4.3 Contract Status Consequence

**Fresh qualification outcome → Contract status:**

| Measurement Outcome | Contract Status | Authorizing? | Proceed to 4.1? |
|---|---|---|---|
| **EFFECT_OBSERVED** (delta ≥ 1.0, direction correct) | **CAUSAL_VERIFIED** | YES | YES → execution test |
| **NO_OBSERVED_EFFECT** (delta < 1.0 or direction wrong) | **NEGATIVE_EVIDENCE** | NO | **STOP. 4.1 FAILS.** |
| **INCONCLUSIVE** or **NOT_RUN** | **STRUCTURAL_ONLY** | NO | **STOP. 4.1 FAILS.** |

**CRITICAL RULE:** If the fresh qualification does NOT produce EFFECT_OBSERVED:
- Do NOT lower the threshold
- Do NOT reinterpret the measurement
- Do NOT reuse the archived CAUSAL_VERIFIED contract
- Do NOT proceed to runtime execution test (4.1B)
- DO: Report qualification failure; 4.1 is BLOCKED; investigation required

The purpose of 4.1 is to establish the authority substrate. A non-authorizing fresh qualification means the substrate was not established and must be revisited before implementation.

---

## 5. CLAIMDEFINITION SPECIFICATION

**Exact ClaimDefinition identity (to be resolved in ClaimEngine):**

```
claim_type: "envelope_field_release"
subject_pattern: {
  "semantic_target": "Env1.Release",
  "parameter_path": "Env0.plainParams.kParamRelease"
}
predicate: "extends"
required_gate: {
  "load": "PASS",
  "causal": "PASS",
  "persistence": "PASS"
}
required_isolation: ("single_field",)
breadth_rule: {"sampled_min": 1}
coverage_rule: {"generalizing_dimensions": [], "family_min_distinct": 1}
measurability: "OBJECTIVELY_MEASURABLE"
required_measurement: {
  "metric_name": "tail_rms_db",
  "target": "Env0.plainParams.kParamRelease",
  "measurement_definition_id": "tail_rms_db:c6a68e551ef9"
}
claim_definition_id: <computed by ClaimDefinition.digest()>
```

**The exact claim_definition_id will be known after ClaimDefinition is constructed. Document it in the implementation artifact.**

---

## 6. CONTRACT GENERATION PATHWAY

### 6.1 ClaimEngine & ClaimGroup

```
Fresh EvidenceRecord loaded
  ↓
ClaimEngine creates entry:
  key = (claim_definition_id, condition_signature_hash)
  supporting_evidence = ["release_qualified_complete_001"]
  ↓
ClaimGroup.condition_signature_hash = 
    experiment_condition_signature(
      prerequisites=[],
      baseline_overrides=[["Env0.plainParams.kParamDecay", 0.02]]
    ).hash
  ↓
Gates evaluated:
  - load: record loaded? PASS
  - persistence: mutation persisted? check readback
  - causal: EFFECT_OBSERVED? check measurement
```

### 6.2 CapabilityContract Generation

**If measurement shows EFFECT_OBSERVED:**

```python
CapabilityContract(
  target="envelope_field_release",
  allowed_operation="mutate_numeric_value",
  status="CAUSAL_VERIFIED",  # earned by EFFECT_OBSERVED + required_gate.causal==PASS
  prerequisites=(
    {
      "field_path": "body:Env0.plainParams.kParamDecay",
      "declared_value": 0.02,
      "must_hold_identical": True
    },
  ),
  verified={
    "load": "PASS",
    "persistence": "PASS",
    "causal": "EFFECT_OBSERVED"
  },
  measurement={
    "metric": "tail_rms_db",
    "target_field": "Env0.plainParams.kParamRelease",
    "baseline": <measured>,
    "treatment": <measured>,
    "delta": <delta>,
    "expected_direction": "increase",
    "observed_direction": "increase",  # must match expected
    "threshold": 1.0,
    "status": "EFFECT_OBSERVED",
    "measurement_definition_id": "tail_rms_db:c6a68e551ef9"
  },
  scope={
    "tested_context_only": True,
    "condition_signature_hash": <hash>,
    "mutation_target_path": "Env0.plainParams.kParamRelease",
    "mutation_value_used": 1.0,  # SINGLETON; ABSOLUTE_PARAMETER_VALUE semantics
    "mutation_value_semantics": "ABSOLUTE_PARAMETER_VALUE"  # Explicit: NOT a delta
  },
  provenance={
    "claim_definition_id": <resolved>,
    "condition_signature_hash": <hash>,
    "supporting_evidence": ["release_qualified_complete_001"],
    "witness_experiment_id": "release_qualified_complete_001"
  },
  limitations=(
    "Tested only with Release parameter = 1.0; generalization to other Release values not established",
    "Tested only with Decay parameter = 0.02; generalization to other Decay contexts not established",
    "Single-field isolated mutation; multi-field interactions not tested",
    "Measurement via tail_rms_db kernel tail_rms_db:c6a68e551ef9; other measurement kernels not validated"
  )
)
```

**If measurement shows NO_OBSERVED_EFFECT:**

```python
CapabilityContract(
  target="envelope_field_release",
  allowed_operation="mutate_numeric_value",
  status="NEGATIVE_EVIDENCE",  # NO_OBSERVED_EFFECT with required_gate.causal==PASS
  prerequisites=(),
  verified={
    "load": "PASS",
    "persistence": "PASS",
    "causal": "NO_OBSERVED_EFFECT"  # Honest outcome
  },
  measurement={...observed values...},  # Records the actual measurement, not assumed
  scope={"tested_context_only": True, ...},
  provenance={...},
  limitations=(
    "Fresh qualification produced NO_OBSERVED_EFFECT under tested conditions",
    "NO causal effect established; this contract does NOT authorize Release capability",
    "Contract exists for audit/historical record only; admission will REFUSE this target"
  )
)
```

**CRITICAL:** Both outcomes produce a contract object. The difference is status (CAUSAL_VERIFIED vs NEGATIVE_EVIDENCE) and therefore admissibility.

---

## 7. RUNTIME ADMISSION SPECIFICATION

### 7.1 N=1 PASS Demonstration

**Setup:**

- Load Release contract from `_capability_contracts_4_1.pkl` (fresh contract store; see 7.3)
- Verify contract.status == CAUSAL_VERIFIED (must be true, else fail)
- Read current Release value (readback)
- Read current Decay value (readback)
- Verify Decay readback == 0.02 (context precondition)

**Admission call:**

```python
result = admit(
  contracts=fresh_contract_store,
  target="envelope_field_release",
  required_causal=True,
  proposed_prerequisites_verified={
    "body:Env0.plainParams.kParamDecay": 0.02  # Exact value from readback
  },
  required_measurement_definition_id="tail_rms_db:c6a68e551ef9"
)
```

**Expected result:** AdmissionResult(admitted=True, reason="ADMITTED", contract=<Release contract>)

**Gate sequence:**
1. Lookup: target exists? ✓
2. Status: CAUSAL_VERIFIED? ✓
3. Causal: required_causal=True? ✓
4. Persistence: verified["persistence"]=="PASS"? ✓
5. Prerequisite: Decay verified as 0.02? ✓
6. Measurement: definition_id matches? ✓
7. **Result: PASS → proceed to execution**

**Candidate generation:**

```python
candidates = generic_candidate_generation(contract)
# Expected: [{"target": "envelope_field_release", "mutation_value": 1.0, ...}]
```

**Execution:**
- set_parameter(Env0.plainParams.kParamRelease, 1.0)
- Readback: get_parameter() → verify == 1.0
- Render note (same stimulus as qualification)
- Measure tail_rms_db (same kernel)
- Record episode with all readbacks, measurements, admission result

### 7.2 N=1 BLOCKED Demonstration (Refusal Proof)

**Setup:**

- Load Release contract from `_capability_contracts_4_1.pkl`
- Read current Decay value
- **Intentionally introduce context mismatch:** Set Decay to 0.015 (or other mismatched value)
- Verify Decay readback != 0.02 (intentional precondition violation)

**Admission call:**

```python
result = admit(
  contracts=fresh_contract_store,
  target="envelope_field_release",
  required_causal=True,
  proposed_prerequisites_verified={
    "body:Env0.plainParams.kParamDecay": 0.015  # MISMATCH: declared 0.02, verified as 0.015
  },
  required_measurement_definition_id="tail_rms_db:c6a68e551ef9"
)
```

**Expected result:** AdmissionResult(admitted=False, reason="REFUSED_PREREQUISITE_UNVERIFIED", ...)

**Gate sequence:**
1. Lookup: target exists? ✓
2. Status: CAUSAL_VERIFIED? ✓
3. Causal: required_causal=True? ✓
4. Persistence: verified["persistence"]=="PASS"? ✓
5. Prerequisite: Decay verified as 0.02?
   - Caller proposed: 0.015
   - Contract declared: 0.02
   - p.must_hold_identical == True? ✓
   - Match? 0.015 == 0.02? **NO**
   - **Unverified!**
6. **Result: REFUSE → BLOCKED episode, NO execution**

**Episode record:**

```json
{
  "episode_id": "release_qualified_complete_001_blocked_context",
  "timestamp": "...",
  "human_intent": "make the note sustain longer",
  "semantic_target": "Env1.Release",
  "admission_status": "REFUSED",
  "admission_reason": "prerequisite_unverified",
  "admission_detail": "... requires prerequisite(s) ['body:Env0.plainParams.kParamDecay'] to be verified...",
  "context_verification": {
    "prerequisite_field": "body:Env0.plainParams.kParamDecay",
    "declared_value": 0.02,
    "actual_readback": 0.015,
    "verification_passed": false,
    "reason": "readback value 0.015 ≠ declared 0.02"
  },
  "execution_blocked": true,
  "serum_readback_before": null,
  "serum_readback_after": null,
  "audio_baseline": null,
  "measurement_baseline": null,
  "measurement_treatment": null,
  "measurement_delta": null,
  "decision": {
    "accepted": false,
    "reason": "admission_refused_prerequisite_unverified"
  },
  "notes": "Intentional context mismatch to demonstrate refusal pathway; admission correctly refused; mutation not executed"
}
```

**Outcome:** Refusal pathway proven. Admission enforcement works.

### 7.3 Authoritative Contract Store Selection

**Design decision:**

- **Archived store:** `experiments/_capability_contracts.pkl` — immutable historical record of all prior contracts (37 entries)
- **Fresh 4.1 store:** `experiments/_capability_contracts_4_1.pkl` — authoritative source for 4.1 runtime proof; contains ONLY Release contract (fresh qualification)

**Runtime loading rule (for 4.1):**

```python
# Load fresh 4.1 authority source explicitly
contracts_4_1 = load_contracts_from_pickle("experiments/_capability_contracts_4_1.pkl")

# Admission uses only 4.1 store for this proof
result = admit(contracts=contracts_4_1, target="envelope_field_release", ...)
```

**Rationale:**

The archived store is a historical artifact. For 4.1, we must prove a fresh authority substrate. Loading from a separate store makes the distinction explicit and prevents accidental fallback to archived contracts.

**After 4.1 succeeds:** The 4.1 contract will be merged into a unified authoritative store for 4.2. But 4.1 must isolate the fresh qualification to prove it works independently.

---

## 8. SUCCESS CRITERIA (4.1 Authority Substrate)

**QUALIFICATION SUCCESS (Precondition for 4.1 execution test):**

- [ ] Fresh EvidenceRecord generated with complete context provenance
- [ ] baseline_overrides: Decay=0.02 from live Serum readback (NOT inferred)
- [ ] Measurement conducted with exact stimulus (MIDI 60, velocity 110, 0.4s note, 2.0s render, 0.6–2.0s tail window)
- [ ] Measurement kernel: tail_rms_db:c6a68e551ef9 (exact match to archived)
- [ ] Causal outcome determined: EFFECT_OBSERVED or NO_OBSERVED_EFFECT
- [ ] If NO_OBSERVED_EFFECT: **STOP. 4.1 qualification FAILED. Do not proceed to execution test.**
- [ ] If EFFECT_OBSERVED: contract.status = CAUSAL_VERIFIED; proceed to execution test

**EXECUTION TEST PASS (N=1 PASS episode):**

- [ ] Contract loaded from fresh `_capability_contracts_4_1.pkl`
- [ ] Context precondition verified: Decay readback == 0.02
- [ ] Admission gate passes (all 6 gates PASS)
- [ ] Generic candidate generation produces: [{"target": "envelope_field_release", "mutation_value": 1.0}]
- [ ] Mutation executes: Release parameter changes to 1.0
- [ ] Readback confirms: Release == 1.0
- [ ] Measurement recorded (same kernel, same stimulus)
- [ ] Episode published with authority state and admission result
- [ ] No Release-specific planner hardcoding in decision path

**REFUSAL TEST PASS (N=1 BLOCKED episode):**

- [ ] Context precondition deliberately violated: Decay set to ≠0.02
- [ ] Admission gate REFUSES (prerequisite check fails)
- [ ] Mutation does NOT execute
- [ ] Render does NOT occur
- [ ] Measurement does NOT occur
- [ ] BLOCKED episode published with refusal reason and context mismatch recorded

**FAIL if any of:**
- Qualification measurement shows NO_OBSERVED_EFFECT and contract.status != CAUSAL_VERIFIED
- Archived contract is used as fallback in 4.1
- Admission passes and execution proceeds despite context mismatch
- Refusal episode not generated when context fails verification
- Planner contains Release-specific hardcoding (scope_min, scope_max, magnitude_steps, current_value)

---

## 9. ARTIFACTS

### 9.1 Qualification Artifacts (Input to ClaimEngine)

**Authoritative evidence:**
- `serum2/qualification/release_qualified_complete_001_EVIDENCE.json` — EvidenceRecord JSON export (human-readable audit trail)
- `experiments/_env_release_qualified_complete_001.pkl` — EvidenceRecord pickle (ClaimEngine input)

**Metadata:**
- `serum2/qualification/release_qualified_complete_001_QUALIFICATION_REPORT.txt` — Measurement outcomes, gate results, contract status decision

### 9.2 Contract Artifacts (Output from ClaimEngine)

**Fresh 4.1 authoritative store:**
- `experiments/_capability_contracts_4_1.pkl` — Contract dict with Release entry (key: (claim_definition_id, condition_signature_hash)); archive-only; never modified by runtime

**Contract metadata:**
- `serum2/qualification/release_qualified_complete_001_CONTRACT.json` — Contract fields in JSON for audit

### 9.3 Execution Artifacts (4.1 Demonstration)

**PASS episode:**
- `serum2/qualification/release_qualified_complete_001_PASS.json` — N=1 execution with admission PASS, mutation success, measurement recorded

**BLOCKED episode:**
- `serum2/qualification/release_qualified_complete_001_BLOCKED_CONTEXT.json` — N=1 refusal with admission REFUSE, no mutation, no measurement

---

## 10. GATE

**4.Q.3 DESIGN COMPLETE when:**

- [ ] Purpose (section 0): substrate proof, fresh evidence, independent causal determination
- [ ] Objective (section 1): singleton mutation, context capture, causal as outcome not assumption
- [ ] Context capture (section 2): baseline_overrides from live readback; non-negotiable
- [ ] Stimulus (section 3): exact provenance (ENV-RELEASE); comparability rationale; fresh experiment marker
- [ ] Measurement (section 4): gates, outcome determination, consequence mapping (EFFECT_OBSERVED → CAUSAL_VERIFIED; NO_OBSERVED_EFFECT → stop)
- [ ] ClaimDefinition (section 5): exact identity to be resolved; digest computed at build time
- [ ] Contract generation (section 6): two outcome branches (PASS and FAIL); non-empty limitations for singleton scope
- [ ] Admission (section 7): N=1 PASS + N=1 BLOCKED; explicit store selection (_capability_contracts_4_1.pkl)
- [ ] Success criteria (section 8): qualification failure = STOP; execution test requires PASS; refusal must be demonstrated
- [ ] Artifacts (section 9): evidence, contract, pass episode, blocked episode enumerated
- [ ] NO assumption of CAUSAL_VERIFIED; outcome determined by measurement

**Design is FROZEN when:**
- All ten sections reviewed and approved
- Contingency for NO_OBSERVED_EFFECT explicitly accepted (qualification fails, do not proceed)
- Contract store separation (fresh vs archived) explicit
- Both execution (PASS) and refusal (BLOCKED) tests enumerated

**Do not implement until 4.Q.3 design is approved and all corrections accepted.**

---

## CRITICAL RULES (Non-Negotiable for 4.1 Authority Proof)

1. **Causal result is an outcome.** If measurement shows NO_OBSERVED_EFFECT, the qualification fails. Do not reinterpret, do not lower threshold, do not reuse archived contract.

2. **Context is from live readback.** Decay=0.02 MUST come from Serum get_parameter() at baseline, not from documents or inference.

3. **Stimulus is comparable, not copied.** Use same nominal parameters as ENV-RELEASE for measurement continuity, but this is a fresh independent experiment.

4. **Both pathways tested.** N=1 PASS and N=1 BLOCKED episodes are both required to prove authority works.

5. **No Release-specific hardcoding.** Planner uses generic policy; contract-specific scope and thresholds are kept in the contract, not in code branches.

6. **Contract store is explicit.** Use _capability_contracts_4_1.pkl for 4.1 authority, not archived store.

7. **Limitations are honest.** Do not claim generalization (Release=1.0 only; Decay=0.02 only; single-field only).

8. **Admission is enforced.** If context fails to verify, execution does not proceed. No bypass, no fallback.

---

## END 4.Q.3

Design complete. Constrained to 4.1 substrate proof only. Includes contingency for measurement failure. Both execution pathways (PASS and BLOCKED) specified.

Ready for approval.
