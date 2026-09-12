# PROJECT BOOTSTRAP

**Quick link for new agents:** This file is the canonical entry point. It reconstructs project state from the repository without requiring conversation history.

---

## 1. Project Identity

**Serum 2.0.21 AI Producer** — A trustworthy music synthesis advisor for Ableton Live 12.3 Suite, grounding all claims in measured evidence.

- **Repository:** GitHub (local, Windows)
- **Language:** Python 3.14
- **Core Tools:** DawDreamer 0.9.0 (Serum VST3 host), Ableton MCP (session control)
- **Frozen Environment:** Serum 2.0.21, DawDreamer 0.9.0, Python 3.14, Ableton Live 12.3 Suite — never patched, upgraded, or downgraded during this project.

---

## 2. Current Milestone Status

### ✅ STEP 6 — FROZEN & CLOSED

**Completion Date:** 2026-09-13

**Status:** `COMPLETE` `FROZEN` `LIVE_VALIDATED`

Step 6 delivered the frozen producer architecture through six major components:

- **6.1** → `step_6_1_universal_production_intent.py` — Backend-independent intent representation
- **6.2–6.4** → `step_6_2/3/4_*.py` — Intent mapping → Semantic reasoning → Semantic candidates
- **6.5–6.8** → `step_6_5/6/7/8_*.py` — Advisory decision → Capability resolution → Admission handoff → Execution authority
- **6.9–6.11** → `step_6_9/10/11_*.py` — Outcome attribution → Episode generation + persistence → Closed-loop proof
- **6.12–6.14** → Tests proving KNOWLEDGE ≠ AUTHORITY, EPISODE ≠ AUTHORITY (42 adversarial cases + 493 total tests)

**Architecture Invariants (Non-negotiable):**

```
Reasoning Chain (Advisory Only)
  Intent → Knowledge + Episodes → Semantic Candidates → Advisory Decision
                      ↓ (influences, does not authorize)
Authority Chain (Execution Permitting)
  CapabilityContract (ONLY source of mutation authority)
    ↓
  Step 4 admission.admit() gate (ONLY source of execution permission)
    ↓
  ExecutionAuthority (scoped to contract + prerequisites verified)
    ↓
  DawDreamer + Real Serum VST3 (ONLY execution)
    ↓
  Real Audio Measurement (outcome attribution)
    ↓
  Episode: learning_eligible ≠ execution_permitted (both gated separately)
```

**Key Definitions:**
- **RESOLVED ≠ ADMITTED** — Capability resolution (6.6) succeeds; admission (Step 4) independently refuses if prerequisites unverified.
- **KNOWLEDGE ≠ AUTHORITY** — Knowledge items inform reasoning; they do not grant execution permission.
- **EPISODE ≠ AUTHORITY** — Prior episodes improve future reasoning; they do not override contract constraints.

---

## 3. Frozen Architecture

### Core Components (Read-Only)

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `serum2/knowledge/step_6_1_universal_production_intent.py` | Intent representation | ~100 | FROZEN |
| `serum2/knowledge/step_6_2_universal_production_intent.py` | Intent mapping to semantic concepts | ~150 | FROZEN |
| `serum2/knowledge/step_6_3_episode_context_integration.py` | Episode retrieval and context building | ~200 | FROZEN |
| `serum2/knowledge/step_6_4_semantic_reasoning_integration.py` | Semantic candidate generation | ~350 | FROZEN |
| `serum2/knowledge/step_6_5_advisory_decision_engine.py` | Advisory ranking and selection | ~500 | FROZEN |
| `serum2/knowledge/step_6_6_capability_resolution.py` | Contract resolution + prerequisite checking | ~350 | FROZEN |
| `serum2/knowledge/step_6_7_admission_handoff.py` | Admission integration layer | ~150 | FROZEN |
| `serum2/knowledge/step_6_8_contract_governed_execution.py` | Authority construction from admitted contracts | ~200 | FROZEN |
| `serum2/knowledge/step_6_9_outcome_attribution.py` | Measurement interpretation | ~200 | FROZEN |
| `serum2/knowledge/step_6_10_episode_generation.py` | Episode creation and persistence | ~250 | FROZEN |
| `serum2/knowledge/step_6_11_closed_loop_proof.py` | Learning influence detection (Cycle A/B) | ~350 | FROZEN |

### Critical Decision Points (Never Reopen)

1. **Authority Source:** CapabilityContract + admission.admit() only. No advisory override, no knowledge-granted execution, no episode-based bypasses.
2. **Admission Gate:** Frozen Step 4 `admission.admit()` method used without modification. All prerequisite verification delegated to caller context.
3. **Measurement Authority:** Contract's measurement_definition_id is the single source of truth for outcome validation. Wrong ID = REFUSED.
4. **Prerequisites:** Must be independently verified by caller in their own execution context. Contract's prerequisites encode what the original evidence established.

### Recorded Implementation Fixes (Not Architecture Weakening)

**6.8 Representation Compatibility Fix** (lines 150–170 of `step_6_8_contract_governed_execution.py`):
- **Issue:** `dict(contract.prerequisites)` assumed prerequisites were a dict, but actual `CapabilityContract.prerequisites` is a tuple of dicts (each with `field_path`, `declared_value`, `must_hold_identical`).
- **Fix:** Added isinstance() checking to normalize tuple-of-dicts to {field_path: prereq_dict} before passing to ExecutionAuthority constructor.
- **No Authority Impact:** This is a representation compatibility fix, not a new authority pathway. The frozen authority semantics remain unchanged. All 493 knowledge tests pass before and after.

---

## 4. Non-Negotiable Invariants

These are architectural truths derived from Step 6 proof; they cannot be questioned or weakened without explicit user authorization.

### KNOWLEDGE ≠ AUTHORITY

- Knowledge items (stored in `serum2/knowledge/`) inform semantic reasoning.
- Knowledge **never** grants execution permission.
- Knowledge confidence (HYPOTHESIS, CAUSAL_VERIFIED, etc.) **never** becomes execution authority.
- **Test Coverage:** `test_6_12_knowledge_experience_authority_proof.py` — cases A1–A5 (Knowledge Attacks)

### EPISODE ≠ AUTHORITY

- Episodes (stored in `serum2/qualification/ep_*.json`) demonstrate successful patterns.
- Episodes **never** override contract scope, measurement, or prerequisites.
- Episodes **never** grant execution permission independently.
- High-confidence episodes still require admission gate to execute.
- **Test Coverage:** cases B1–B5 (Episode Attacks) + case study: Cycle B must re-pass admission even with Cycle A's episode.

### RESOLVED ≠ ADMITTED

- CapabilityResolution.resolve() checks contract existence + prerequisites + scope + operation compatibility.
- resolve() returning RESOLVED means "a contract exists and resolves"; it does NOT mean "admitted to execute."
- Admission is a separate decision made by frozen Step 4 `admission.admit()` based on caller-verified prerequisites.
- **Test Coverage:** cases D1–D2 (Resolution vs Admission); live test negative run demonstrates RESOLVED==True but ADMITTED==False when prerequisites unverified.

### MEASUREMENT AUTHORITY

- Contract.measurement_definition_id is the authoritative kernel for outcome validation.
- No outcome is valid without the exact measurement kernel that the contract requires.
- Mismatched measurement IDs trigger REFUSED, not adaptation.
- **Test Coverage:** outcome attribution logic in `step_6_9_outcome_attribution.py` lines 175–186.

---

## 5. Completed Steps

### Step 1–5: Backward History

Completed in prior context windows. Evidence preserved in `regression/` and `experiments/` directories. See ROADMAP.md for phase descriptions.

### Step 6: Knowledge Layer + Frozen Producer

**Completed:** 2026-09-13

**Evidence:**
- `serum2/knowledge/*.py` — 11 frozen modules (6.1–6.11)
- `serum2/knowledge/test_*.py` — 42 adversarial tests + 493 total tests passing
- `experiments/step6_live_vertical_slice.py` — Live validation against real Serum 2.0.21 + DawDreamer 0.9.0
- `experiments/_step6_live_evidence.json` — Live execution evidence artifact

**Live Validation Results:**

```
POSITIVE RUN (full pipeline 6.2→6.8):
  Intent: "Make the note sustain longer." (note-release, LONGER)
  Knowledge: k_envelope_release_tail (advisory, HYPOTHESIS)
  Resolution: 6.6 RESOLVED (with real current_context supplied)
  Admission: ADMITTED (prerequisites verified)
  Authority: ExecutionAuthority created from contract
  Execution: Real Serum VST3 mutation: Env0.plainParams.kParamRelease=1.0
  Measurement: tail_rms_db baseline=-240.00 dB, treatment=-35.52 dB, delta=+204.48 dB
  Result: LIVE_EXECUTED, outcome_status=unexpected_change, causal=consistent_with_treatment

NEGATIVE RUN (6.6 RESOLVED but 6.7 admission refused):
  Same intent, same 6.6 resolution
  Admission prerequisite confirmation withheld
  Result: REFUSED_AT_ADMISSION_BOUNDARY, execution_authority=None
  Proof: RESOLVED ≠ ADMITTED
```

---

## 6. Evidence & Artifact Index

### Live Validation Evidence

```
D:\ableton claude\experiments\_step6_live_evidence.json
```

Contains:
- Parameter identity proof (UI "Env 1 Release" → VST3 index 228 → body path Env0.plainParams.kParamRelease)
- Real audio measurements (baseline=-240 dB, treatment=-35.52 dB, delta=+204.48 dB)
- Complete reasoning chain (intent → knowledge → candidate → decision → resolution → admission)
- Complete authority chain (resolution → admission → authority → execution)
- Closed-loop structure (positive run with admitted execution, negative run with refused admission)

### Test Results

```
serum2/knowledge/test_6_12_knowledge_experience_authority_proof.py
→ 42 adversarial tests, all PASS
→ Proof of KNOWLEDGE ≠ AUTHORITY, EPISODE ≠ AUTHORITY

pytest serum2/knowledge/ -q --tb=short
→ 493 passed, 27 skipped (all knowledge tests)
```

### Contract & Knowledge Storage

```
serum2/knowledge/
  contracts.py         — CapabilityContract definitions
  step_6_6_*.py       — Capability resolution logic

serum2/qualification/
  ep_ex_live_001.json — Generated episode from live execution
```

---

## 7. Test & Proof Index

### Architectural Proofs

| Proof | File | Status |
|-------|------|--------|
| KNOWLEDGE ≠ AUTHORITY | `test_6_12.py` cases A1–A5 | ✅ PASS (5/5) |
| EPISODE ≠ AUTHORITY | `test_6_12.py` cases B1–B5 | ✅ PASS (5/5) |
| ADVISORY ≠ AUTHORITY | `test_6_12.py` cases C1–C3 | ✅ PASS (3/3) |
| RESOLVED ≠ ADMITTED | `test_6_12.py` cases D1–D2 + live neg run | ✅ PASS (2/2 + live) |
| CONTRACT AUTHORITY | `test_6_12.py` cases E1–E6 | ✅ PASS (6/6) |
| DIAGNOSIS ≠ AUTHORITY | `test_6_12.py` cases F1–F2 | ✅ PASS (2/2) |
| CROSS-CONTAMINATION | `test_6_12.py` cases G1–G4 | ✅ PASS (4/4) |
| CROSS-BACKEND UNIVERSALITY | `test_6_12.py` cases H1–H4 | ✅ PASS (4/4) |

### Live Execution Proofs

| Proof | Evidence | Status |
|-------|----------|--------|
| SERUM 2.0.21 LIVE | DawDreamer render, real audio | ✅ PASS (delta=+204.48 dB observed) |
| DAWDREAMER 0.9.0 LIVE | Render execution + measurement | ✅ PASS |
| PARAMETER IDENTITY | VST3 index readback + display text | ✅ PASS ("15 ms" → "1.00 s" confirmed) |
| EPISODE RETRIEVAL | Canonical persistence + re-read | ✅ PASS |
| CLOSED-LOOP REASONING | Cycle A → Cycle B with episode | ✅ PASS (learning influence detected) |

---

## 8. Known Limitations & Historical Defects

### Pre-Step 7 Limitations (By Design)

These are not bugs; they are intentional boundaries:

1. **Serum Control Coverage**
   - Only `FXEQ.Freq1` (SCALAR mutation) proven as CAUSAL_VERIFIED with tail_rms_db measurement.
   - Remaining Serum controls in qualification phase (Step 16.5.69 scope).
   - `release` (Env 1 Release) only proven in the context: Decay=0.02, tail_rms_db measurement kernel.

2. **Single-Context Qualification**
   - Contract `envelope_field_release` tested only with `Decay=0.02` baseline_overrides.
   - Generalization to other Decay values or other prerequisite contexts is BLOCKED_CONTRADICTED until new evidence.
   - Caller must independently verify prerequisites in their own execution context.

3. **Ableton Live Integration**
   - Serum is hosted under DawDreamer (VST3), not Ableton native.
   - Ableton MCP used for session reference truth only; not for Serum control.
   - 127-slot parameter limitation applies to Ableton's own send/control surface, not to VST3 full control.

### Recorded Defects

**None currently.** The 6.8 representation compatibility fix is not a defect — it's a pre-existing integration mismatch resolved without weakening authority.

---

## 9. Current Next Step

**Awaiting explicit user specification.** Step 6 is frozen; Step 7 does not begin until the user provides a scoped Step 7 specification.

If the user's goal is to run new source (e.g., YouTube transcript) through the frozen Step 6 pipeline:

```
New Source (e.g., YouTube transcript)
  ↓
[No Step 6 modification — use as-is]
  ↓
Step 5 Knowledge Ingestion (insert new source)
  ↓
Run frozen Step 6 pipeline
  ↓
Report: reasoning chain, authority chain, constraints
```

If the user's goal is a new capability (e.g., Reverb size control):

```
Step 7 Definition Required:
  - Goal (what capability to prove)
  - Scope (single Serum target, multiple targets, cross-plugin)
  - Measurement kernel (which metrics)
  - Context constraints (what prerequisites or Ableton states)
  - Coverage requirement (instance-only vs generalized)
```

---

## 10. Where Detailed Information Lives

### Architecture

- **Frozen Code:** `serum2/knowledge/step_6_*.py` — read these for exact definitions.
- **Policy:** `CLAUDE.md` in this repository — authority rules, change discipline, epistemic guarantees.
- **Proof:** `serum2/knowledge/test_6_12_knowledge_experience_authority_proof.py` — all invariant proofs.

### Evidence & Artifacts

- **Live Validation:** `experiments/_step6_live_evidence.json` — complete positive + negative run evidence.
- **Episodes:** `serum2/qualification/ep_*.json` — persisted episode records.
- **Contracts:** `serum2/knowledge/contracts.py` — CapabilityContract definitions.

### Historical Context

- **Roadmap:** `ROADMAP.md` — phase history and step definitions.
- **Prior Milestones:** `experiments/`, `regression/` directories — evidence from Steps 1–5.
- **User Memory:** `.claude/projects/D--ableton-claude/memory/MEMORY.md` — key decisions and constraints (persists across conversations).

---

## 11. For New Agents

**Quick Orientation:**

1. **Frozen Code is Frozen.** Do NOT modify `step_6_*.py` or frozen Step 4 `admission.admit()` without explicit authorization.
2. **Read CLAUDE.md First.** It contains all authority rules and change discipline.
3. **Live Evidence Exists.** Reference `_step6_live_evidence.json` to understand real execution, not mock data.
4. **Tests are Contracts.** All 493 knowledge tests are regression contracts. Passing tests prove Step 6 stability.
5. **Ask Before Specifying Step 7.** The user is the sole authority on what Step 7 should do. Get an explicit scope definition before planning.

---

**Last Updated:** 2026-09-13  
**Status:** FROZEN  
**Next Revision:** After Step 7 specification or when new evidence requires invariant updates (rare).
