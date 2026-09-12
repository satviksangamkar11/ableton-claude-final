# Bootstrap Workflow for New Agents

This document describes how a new agent (or a new conversation session) reconstructs project understanding from the repository without re-reading the full prior conversation history.

## The Problem

**Before:**
- New chat → Only file paths and git history visible
- Agent must infer architecture from code inspection
- No way to know what was frozen, what was proven, what was rejected
- Risk of reopening frozen code, re-proving invariants, or ignoring known limitations

**After:**
- New chat → Read PROJECT_BOOTSTRAP.md
- Complete orientation in ~5 minutes
- Exact frozen boundaries, invariants, evidence locations
- Clear signal: "Stop here, this is frozen"

## The Solution: Three-Layer Bootstrap

### Layer 1: BOOTSTRAP FILE (your entry point)

**File:** `PROJECT_BOOTSTRAP.md`

**Content:**
- Project identity and frozen environment
- Current milestone status (STEP 6 FROZEN)
- Frozen architecture (which code never to touch)
- Non-negotiable invariants (KNOWLEDGE ≠ AUTHORITY, etc.)
- Completed steps + evidence index
- Test & proof index
- Known limitations
- Current next step
- Where to find detailed information

**Read Time:** ~5 minutes  
**Token Cost:** ~2000 tokens  
**Purpose:** Answer "What is done? What is frozen? What can I touch?"

### Layer 2: MACHINE-READABLE MANIFEST

**File:** `architecture/milestone_index.json`

**Content:**
- Structural metadata (modules, invariants, test results)
- Live validation summary (baseline, treatment, delta)
- Environment fingerprint (Serum 2.0.21, DawDreamer 0.9.0, etc.)
- Known limitations (single-context qualification, blocked generalizations)
- Implementation fixes (6.8 representation compatibility)

**Read Time:** ~2 minutes (JSON parsing)  
**Token Cost:** ~1000 tokens  
**Purpose:** Machine-assisted navigation, CI validation, cross-checking

### Layer 3: LIVE EVIDENCE ARTIFACT

**File:** `experiments/_step6_live_evidence.json`

**Content:**
- Complete positive run (intent → resolution → admission → execution → measurement)
- Complete negative run (RESOLVED==True, ADMITTED==False, proves RESOLVED ≠ ADMITTED)
- Parameter identity proof (VST3 index, body path, readback text)
- Real audio measurements (baseline, treatment, delta in dB)

**Read Time:** ~3 minutes (skim for structure)  
**Token Cost:** ~3000 tokens (full read for evidence validation)  
**Purpose:** See actual execution results, parameter identity, measurement values

---

## Workflow: New Agent Orientation

### Step 1: Bootstrap (2 minutes)

```
1. Read PROJECT_BOOTSTRAP.md
2. Skim architecture/milestone_index.json
3. Ask yourself: "What is frozen? What am I allowed to modify?"
```

**After Step 1, you know:**
- Step 6 is frozen, closed, and live-validated
- KNOWLEDGE ≠ AUTHORITY, EPISODE ≠ AUTHORITY, RESOLVED ≠ ADMITTED
- All 493 knowledge tests pass
- Live execution against real Serum 2.0.21 succeeded
- Parameters: tail_rms_db baseline=-240, treatment=-35.52, delta=+204.48

### Step 2: Detailed Code Reading (5 minutes)

Only if the task requires understanding specific frozen code:

```
Task: "Understand how admission works"
  → Read: serum2/knowledge/step_6_7_admission_handoff.py
  → See: how resolve() result feeds into admission gate
  → See: frozen Step 4 admission.admit() called without modification
  → Verify: all calls match bootstrap invariant
```

### Step 3: Evidence Validation (5 minutes)

Only if the task requires validating claims:

```
Task: "Prove that 6.6 CapabilityResolution actually resolved"
  → Read: experiments/_step6_live_evidence.json
  → Extract: positive run → resolution_diagnostic
  → Observe: current_context_supplied, resolution_status=resolved, prerequisite_status=unknown
  → Confirm: matches CLAUDE.md rule "caller verifies prerequisites in own context"
```

### Step 4: Understand Next Step (3 minutes)

If the task involves Step 7 or beyond:

```
Read: PROJECT_BOOTSTRAP.md section 9 (Current Next Step)
See: "Awaiting explicit user specification"
Ask: "What is Step 7?" if not explicit in the task description
Do not guess or invent Step 7 scope
```

---

## When NOT to Touch Frozen Code

**Frozen means frozen.** These files have proven invariants and must never be modified without explicit user authorization:

| Component | Files | Why |
|-----------|-------|-----|
| Intent representation | `step_6_2_*.py` | Defines semantic IR; changes break all downstream |
| Semantic reasoning | `step_6_4_*.py` | Frozen logic for candidate generation |
| Advisory decision | `step_6_5_*.py` | Frozen logic for ranking |
| Capability resolution | `step_6_6_*.py` | Must match contract lookup and prerequisite checking |
| Admission handoff | `step_6_7_*.py` | Integrates with frozen Step 4 admission.admit() |
| Execution authority | `step_6_8_*.py` | Authority derived from contract only; no policy changes |
| Outcome attribution | `step_6_9_*.py` | Measurement interpretation frozen |
| Episode generation | `step_6_10_*.py` | Learning eligibility gated separately from permission |
| Closed-loop proof | `step_6_11_*.py` | Cycle A/B comparison logic frozen |

**Exception:** Implementation compatibility fixes (like the 6.8 dict normalization) are allowed if they:
1. Do not change authority semantics
2. Maintain all passing regression tests
3. Are recorded in BOOTSTRAP file and milestone_index.json
4. Do not introduce new execution pathways

---

## The Contract Hierarchy

When you inherit this project, this is the order of authority:

1. **CLAUDE.md** — Project policy, epistemic rules, change discipline (read this first for policy)
2. **PROJECT_BOOTSTRAP.md** — Milestone status, frozen boundaries, invariants
3. **architecture/milestone_index.json** — Structured metadata for machine reading
4. **experiments/_step6_live_evidence.json** — The actual evidence: execution traces, measurements
5. **serum2/knowledge/test_6_12_*.py** — Proof contracts (all 493 tests must pass)
6. **Frozen source code** — Implementation, but never change it without authorization

If there's a conflict between layers, the higher layer wins. If CLAUDE.md says "don't modify step_6_6", don't. If the test file says `test_must_pass`, it stays.

---

## Common Tasks

### Task: "Run new source through the frozen pipeline"

```
1. Bootstrap (PROJECT_BOOTSTRAP.md, section 2)
2. New source → Step 5 knowledge ingestion
3. Frozen Step 6 pipeline (no modifications)
4. Report: reasoning chain, authority chain, constraints
5. Do not modify Step 6; it is frozen
```

### Task: "Prove a new Serum control works"

```
1. Bootstrap + understand Step 6 is frozen
2. This is a new capability, not Step 6 work
3. Ask user: "Is this Step 7 or a new Step 16.5.69 experiment?"
4. Wait for explicit authorization to create new evidence
5. Do not attempt to modify Step 6 to accommodate new capability
```

### Task: "Fix a bug in Step 6"

```
1. Bootstrap + review CLAUDE.md section "Safety Constraints"
2. Is it an authority semantics bug? → Blocked, requires explicit user authorization
3. Is it a representation compatibility bug (like 6.8)? → Fix it, record in milestone_index.json, re-run all 493 tests
4. If any test fails after the fix, revert; do not weaken tests
```

### Task: "Understand the live validation"

```
1. Bootstrap (PROJECT_BOOTSTRAP.md, section 5)
2. Read experiments/_step6_live_evidence.json
3. Trace positive run: intent → resolution → admission → execution → measurement
4. Trace negative run: same intent, same resolution, but admission refused (RESOLVED ≠ ADMITTED proof)
5. Inspect parameter identity proof and audio measurements
```

---

## Quick Reference: Frozen Invariants

Memorize these:

```
KNOWLEDGE ≠ AUTHORITY
  Knowledge informs reasoning.
  Knowledge never grants execution permission.
  Test: test_6_12.py cases A1–A5

EPISODE ≠ AUTHORITY
  Episodes improve reasoning.
  Episodes never override contract constraints or prerequisites.
  Test: test_6_12.py cases B1–B5

RESOLVED ≠ ADMITTED
  6.6 CapabilityResolution returns RESOLVED when contract exists.
  Step 4 admission.admit() independently decides on execution permission.
  Test: test_6_12.py cases D1–D2 + live test negative run

MEASUREMENT AUTHORITY
  Contract.measurement_definition_id is the sole authority for outcome validation.
  Wrong measurement ID = REFUSED.
  Test: step_6_9_outcome_attribution.py lines 175–186
```

---

## Updating This Document

After Step 7 is specified and completed:

1. Update PROJECT_BOOTSTRAP.md section 5 (Completed Steps)
2. Add new milestone entry to architecture/milestone_index.json
3. Create new live evidence artifact if applicable
4. DO NOT modify section 3 (Frozen Architecture) retroactively
5. Only ADD new frozen boundaries, never remove or weaken existing ones

---

**Purpose:** Enable rapid, confident onboarding without losing architectural context  
**Maintained by:** Manual curation after each milestone completes  
**Authority:** User is sole authority on what is frozen; this document records their decisions  
**Last Updated:** 2026-09-13
