# STEP 4.2 — Capability Qualification → Admission → Producer Readiness Audit

**Date:** 2026-09-17
**Method:** Live code execution against `serum2/evidence/admission.py`, source inspection of `serum2/producer/canonical_feedback_loop.py`, `serum2/producer/contract_registry.py`, `serum2/producer/planner.py`. No invariant claimed without either a passing executed test or a cited line range.

---

## Artifacts Inspected

| File | Role |
|---|---|
| `serum2/evidence/admission.py` | Admission gate (`admit()`) — the one function a compiler must call before mutation |
| `serum2/evidence/capability_contract.py` | CapabilityContract dataclass + status constants |
| `serum2/producer/contract_registry.py` | Loads fresh 4.1/4.2 pickle contracts; exposes `get_contracts_dict()` |
| `serum2/producer/canonical_feedback_loop.py` | Actual producer entry point (goal → diagnosis → admission → execution → measurement → episode) |
| `serum2/producer/planner.py` | Claude-reasoning decision layer (intent-level, consumes admissible candidates only) |
| `serum2/compiler/producer.py` | Grounding-condition / execution-policy layer (GROUNDED/PARTIALLY_GROUNDED/HYPOTHESIS/UNGROUNDED) |
| `experiments/_capability_contracts_4_1.pkl` | Contract store (Release) |
| `serum2/qualification/release_qualified_complete_001_{PASS,BLOCKED}.json` | Episodes |
| `serum2/qualification/attack_qualified_complete_001_PASS_FULL.json` | Episode (from STEP 4.1 gap closure) |

## Artifacts Created

| File | Purpose |
|---|---|
| `STEP_4_2_CAPABILITY_ADMISSION_REGISTRY.json` | Machine-readable qualification/admission registry |
| `STEP_4_2_CAPABILITY_ADMISSION_AUDIT.md` | This report |

No files modified. No frozen inventory touched.

---

## State Machine (Not Collapsed)

```
SEMANTIC              — semantic_id present in frozen 908-row inventory, status=VERIFIED
   ↓
TARGET/REPRESENTATION — VST3 field + control path known (e.g. Env0.plainParams.kParamRelease)
   ↓
EXECUTABLE            — a real mutation operation exists (DawDreamer-backed)
   ↓
QUALIFIED             — CapabilityContract.status ∈ {CAUSAL_VERIFIED, STRUCTURAL_ONLY,
                         NEGATIVE_EVIDENCE, BLOCKED_CONTRADICTED, UNSUPPORTED}
   ↓
ADMITTED              — admission.admit() returned admitted=True for THIS proposed context
   ↓
PRODUCER-USABLE       — contract_registry exposes it; canonical_feedback_loop consumes
                         only what admission.admit() approved
```

Each capability below is scored against every rung independently — a pass at QUALIFIED does not imply ADMITTED (a context mismatch can still refuse it), and neither implies PRODUCER-USABLE without the registry actually wiring it in.

---

## Admission Gate Verification (Executed, Not Asserted)

Nine adversarial cases were run directly against `admission.admit()` with synthetic and real contracts. All results below are actual `print()` output from execution, not claims:

| # | Case | Result | Refusal reason returned |
|---|---|---|---|
| 1 | No contract exists for target | REFUSED | `unknown_no_contract` |
| 2 | Prerequisite required, caller passes nothing | REFUSED | `prerequisite_unverified` |
| 3 | Prerequisite value-sensitive, caller passes wrong value (0.5 vs declared 0.02) | REFUSED | `prerequisite_unverified` |
| 4 | Prerequisite value matches exactly (0.02 == 0.02) | ADMITTED | — |
| 5 | Caller requests different measurement_definition_id than contract has | REFUSED | `measurement_definition_mismatch` |
| 6 | Contract status = NEGATIVE_EVIDENCE | REFUSED | `negative_evidence` |
| 7 | Contract status = BLOCKED_CONTRADICTED | REFUSED | `contradicted_reverify_required` |
| 8 | Contract status = STRUCTURAL_ONLY, caller requires causal | REFUSED | `structural_only_insufficient_for_causal_requirement` |
| 9 | Caller queries prefix (`"struct"`) instead of exact target (`"struct_target"`) | REFUSED | `unknown_no_contract` (no fuzzy match) |

**Finding: No bypass path exists in any of the 9 adversarial cases tested.**

---

## Producer-Loop Enforcement (Source-Verified)

`serum2/producer/canonical_feedback_loop.py:442-509`:

```
[3.5/10] Authority admission gate:
  1. contract = contract_registry.get(diagnosis.selected_target)
     → None means immediate return, no mutation attempted
  2. For each contract.prerequisite:
     → live_readback_prerequisite() reads ACTUAL Serum state (not caller-declared)
     → verify_prerequisite_for_admission() compares readback to declared_value
  3. admission_mod.admit(contracts_dict, target, required_causal=True,
                          proposed_prerequisites_verified=<live readbacks>,
                          required_measurement_definition_id=<contract's own id>)
  4. if not admission_result.admitted:
       → episode recorded with admission_status=refusal reason
       → learning_eligible=False, observation_only=True
       → RETURN — no execution, no mutation, no measurement below this line
```

**Finding:** prerequisite verification uses **live readback from Serum**, not a caller-supplied boolean — this closes the specific bypass class the admission layer's own prerequisite check (test #2/#3 above) is designed to catch. The gate is structurally before any mutation code path; refusal returns early with a fully-populated refused episode, never silently continuing.

---

## Capability State Table

| Capability | SEMANTIC | TARGET | EXECUTABLE | QUALIFIED | ADMITTED | PRODUCER-USABLE |
|---|---|---|---|---|---|---|
| **ENV1.RELEASE** | VERIFIED (908-row) | Env1.Release (396-target) | YES | CAUSAL_VERIFIED | YES (PASS ep. + BLOCKED ep. both demonstrated) | YES |
| **ENV1.ATTACK** | VERIFIED (908-row) | Env1.Attack (396-target) | YES | CAUSAL_VERIFIED | YES (PASS ep. demonstrated) | YES |
| *(remaining 906 semantics)* | VERIFIED (908-row, per section closure) | mixed (298 OWNED / 447 CONTROL_PATH_KNOWN_NO_TARGET / 140 UNKNOWN, per 2D.6J) | NO (no experiment run) | UNQUALIFIED | N/A | NO |

---

## State Distinctions (As Required)

- **QUALIFIED**: contract exists with status CAUSAL_VERIFIED or STRUCTURAL_ONLY. Release and Attack both qualify here.
- **ADMITTED**: `admit()` returned `admitted=True` for a *specific proposed context*. Release is admitted only when Decay=0.02 is live-verified — the SAME contract is REFUSED (not admitted) when Decay=0.3, proving admission is context-scoped, not target-scoped.
- **QUALIFIED_BUT_NOT_ADMITTED**: no real example currently exists in the repo (would require a CAUSAL_VERIFIED contract with an unmet prerequisite in the current session) — the BLOCKED episode is the closest analog: Release IS admitted in general (PASS episode) but was REFUSED in that one BLOCKED episode's specific proposed context. This is the mechanism, demonstrated.
- **UNQUALIFIED**: the remaining 906 semantics. No CapabilityContract exists. `admit()` on any of them returns `unknown_no_contract` (verified by test #1, which used a synthetic never-tested target).
- **BLOCKED**: would be `BLOCKED_CONTRADICTED` status (test #7) — no live example in current contracts; FX.FLANGER.PHASE from Phase 2D.6J reconciliation is a semantic-level contradiction, not yet a contract-level one.
- **INSUFFICIENT_EVIDENCE**: would be `STRUCTURAL_ONLY` refused under `required_causal=True` (test #8) — no live example in current contracts.

---

## Invariant Checks

| Invariant | Status | Evidence |
|---|---|---|
| Frozen semantic inventory unchanged (908) | PASS | No writes to `SERUM2_SEMANTIC_NORMALIZED.json` this session |
| Frozen target vocabulary unchanged (396) | PASS | No writes to `SERUM2_TARGET_NORMALIZED_V4.json` this session |
| No semantic IDs created | PASS | Zero new `semantic_id` values introduced anywhere in this session's outputs |
| No target-specific hardcoding introduced | PASS | Admission gate is generic (`admit(contracts, target, ...)`); no `if target == "Env1.Release"` branch exists in `admission.py` or `canonical_feedback_loop.py`'s admission block |
| Admission cannot bypass prerequisites | PASS | Tests #2, #3 — omission and value-mismatch both refused |
| Failed qualification cannot become admitted | PASS | Tests #6, #7, #8 — NEGATIVE_EVIDENCE, BLOCKED_CONTRADICTED, STRUCTURAL_ONLY(causal-required) all refused |
| Producer planner consumes only ADMITTED capabilities | PASS | `canonical_feedback_loop.py:471` — execution code is unreachable when `admission_result.admitted` is False |

---

## Weaknesses / Architectural Gaps Found

**Correction:** an earlier draft of this audit claimed `_capability_contracts_4_2.pkl` did not exist and treated this as a registry-wiring gap blocking Attack from production use. That claim was made without directly checking the file and was **wrong** — `os.path.exists()` and a direct pickle load confirm the file is present with one entry (`envelope_field_attack`, `status=CAUSAL_VERIFIED`). `ContractRegistry()` was then run live and printed `Loaded Attack contract: CAUSAL_VERIFIED`, and `admission.admit()` run against the registry's real `get_contracts_dict()` output returned `admitted=True` for `envelope_field_attack`. There is no registry gap. This correction is left in place rather than silently edited out, per the evidence-discipline rule against overwriting a wrong finding without a visible trail.

Actual findings, re-verified by execution:

1. **Attack's `prerequisites=()` is evidentially UNDERSTATED, not a clean "no prerequisites" fact.** The contract's own `limitations` field states: *"baseline_overrides not captured in this EvidenceRecord's schema (predates this field being added) — shared-context prerequisites for this contract are UNDERSTATED, not absent."* The STEP 4.1 audit and the `attack_qualified_complete_001_PASS_FULL.json` episode both characterized this as "Attack has no prerequisites (unlike Release)" — that phrasing is not wrong about what admission enforced in this run, but it obscures that absence-of-prerequisites here is a **schema gap**, not a proven fact about Attack's control isolation. This should be corrected in the STEP 4.1 artifacts as a caveat, not left implied as a clean result.
2. **Single-value authority scope** — both contracts' `scope.tested_context_only=True` with one mutation value each (Release=1.0, Attack=0.8). Admission does not currently reject a caller proposing a different value within [0,1] — `allowed_operation=mutate_numeric_value` has no value-range enforcement in `admit()` itself (that lives in `structural_admission.py`, not exercised in this audit).
3. **No `BLOCKED_CONTRADICTED` or `NEGATIVE_EVIDENCE` capability exists in the live contract store to demonstrate producer behavior on a real refusal** (only the synthetic tests above cover this).

---

## Capability Counts

```
Total semantic records (frozen):        908
Total targets (frozen):                 396
Currently QUALIFIED:                      2  (ENV1.RELEASE, ENV1.ATTACK)
Currently ADMITTED (in-context):          2
QUALIFIED_BUT_NOT_ADMITTED (live):        0  (BLOCKED episode demonstrates the mechanism, not a standing state)
UNQUALIFIED:                            906  (no CapabilityContract exists)
BLOCKED (BLOCKED_CONTRADICTED):           0  (mechanism proven by synthetic test only)
INSUFFICIENT_EVIDENCE (STRUCTURAL_ONLY):  0  (mechanism proven by synthetic test only)
```

---

## Verdict

**Capability-admission gate: PASS.**

- The admission architecture itself has **no bypass** across 9 adversarial cases, tested by execution.
- The producer entry point (`canonical_feedback_loop.py`) enforces the gate correctly and uses **live Serum readback** for prerequisite verification, not caller-declared trust.
- `ContractRegistry()` run live loads both contracts (`Loaded Release contract: CAUSAL_VERIFIED`, `Loaded Attack contract: CAUSAL_VERIFIED`).
- `admission.admit()` run against the registry's real `get_contracts_dict()` output returns `admitted=True` for both `envelope_field_release` and `envelope_field_attack`.
- **Both Release and Attack are PRODUCER-USABLE today**, verified end-to-end through the actual registry and admission code, not through documentation artifacts alone.

**One evidentiary caveat carried forward (not a gate defect):** Attack's contract records its own `prerequisites=()` as understated rather than proven-absent (see Weaknesses §1). This does not block admission today because no caller currently requires a prerequisite Attack doesn't declare — but a future qualification pass should capture Attack's `baseline_overrides` explicitly rather than leave this as a schema gap.

---

## Smallest Representative Capability Set for End-to-End Producer Exercise

**Recommendation: Release alone is sufficient for a first end-to-end producer run; Attack is available as the second target for the 4.2 target-independence re-check once Release is proven live.**

Rationale:
- Release has both a PASS and a BLOCKED episode, proving the admission gate exercises both branches (admit + refuse) in one capability
- Release has a real, captured prerequisite (Decay=0.02), exercising the live-readback verification path that Attack's current evidence does not exercise
- Attack is confirmed PRODUCER-USABLE (registry loads it, admission admits it) but should be run through the live producer loop at least once before being trusted operationally, since its only existing episode (`attack_qualified_complete_001_PASS_FULL.json`) was reconstructed from the evidence record in STEP 4.1's gap-closure pass, not generated by a fresh `canonical_feedback_loop.py` run in this session.

No further registry or admission work is required before producer generation begins. The gate is proven; what remains is running the actual producer loop.
