# Producer Learning Architecture — 9-Checkpoint Roadmap

**Current status:** Step 0 complete. Step 1 next.

**Checkpoint count:** 9 steps

---

## Completed Checkpoints

### ✅ Step 0: Repository Reconciliation

**Status:** COMPLETE (2026-09-12)

Local state verified:
```
branch: serum2-behavioral-qualification-complete
HEAD: 8e7f97faff3c7f68770c5b20b0dc0f11ff90630a
work: canonical_feedback_loop.py present, tests passing
commits: 13 ahead of origin (not yet pushed)
working tree: CLEAN
```

Deliverable: Local implementation truth established.

---

## Active Roadmap

### ▶ Step 1: External Tooling Audit

Inventory of actual available control surfaces:
- DawDreamer + Serum VST3 parameter access
- Ableton MCP available functions
- Window automation (if any)
- Measurement harness (METRICS)

Document exactly what each tool can observe and mutate.

**Deliverable:** Tooling inventory report with capability matrix.

---

### Step 2: Canonical Serum Runtime Slice

Single, measurable Serum operation:
- semantic goal → **decision / mutation planning** (deterministic target selection)
- baseline → ONE mutation → treatment
- render + measure both
- accept/reject by improvement logic
- persist episode with learning_eligible status

**Note:** Currently performs *deterministic target selection + mutation planning*, not rich diagnosis. Reserve "diagnosis" for when actual diagnostic reasoning exists.

**Status:** canonical_feedback_loop.py complete; 24 tests passing.

**Deliverable:** Production-ready single-target feedback loop.

---

### Step 3: Retrieval-Driven Learning Proof

Prove that episode retrieval influences downstream planning:

```
Episode N
  ↓
stored + learning_eligible
  ↓
retrieved by planner
  ↓
candidate decisions differ from baseline

CONTROL:
same conditions, Episode N unavailable
  ↓
planner makes different mutation choice
```

**Level 1 (Retrieval Influence):** Did the episode change the decision?  
**Level 2 (Decision Improvement):** Did the changed decision produce better outcomes?

Step 3 must prove Level 1. Level 2 can follow as stronger validation.

**Deliverable:** Two-episode experiment with counterfactual verification proving retrieval causally influenced decision.

---

### Step 4: Broaden Serum / Observe Operation Shape

Expand from single control to multiple targets:
- OSC1.Octave, OSC1.Level, OSC1.Detune
- Filter.Cutoff, Filter.Resonance
- Env1.Release, Env1.Attack
- FXEQ controls

For each, observe:
- `ProducerGoal`: intent, semantic_target, measurement_metric, metric_direction
- `Decision` / mutation planning: selected_target, mutation_direction, mutation_magnitude
- `ExecutionResult`: accepted, reason, measurement_delta
- `Episode`: stored with learning_eligible, experience_polarity

**Deliverable:** 5-10 multi-target episodes. Identify common fields across operations.

---

### Step 5: General Knowledge Ingestion

Add teaching-from-transcripts layer:
- Ableton Knowledge extraction
- Synthesis/mixing heuristics
- User feedback patterns

Feed into ProducerGoal intent resolution without modifying capability authority.

Knowledge is advisory; authority chain (Evidence → Claim → Capability) is unchanged.

**Deliverable:** Knowledge layer with advisory-only semantics.

---

### Step 6: Ableton MCP Slice

Single meaningful Ableton operation via MCP:
- Set track volume
- Arm recording
- Fire a clip
- Observe result via readback

Observe:
- `ProducerGoal`: intent, semantic_target, measurement_metric
- `ExecutionResult`: accepted, reason, measurement outcome
- `Episode`: stored with learning_eligible, experience_polarity

**Purpose:** Test whether Serum + Ableton operations share enough structure to justify unified abstraction.

**Note:** Ableton is added to TEST for shared shape, not because we assume universal architecture exists.

**Deliverable:** 3-5 Ableton MCP episodes with structure documented.

---

### Step 7: Determine Shared Shape

Analyze operations from Steps 4 and 6:

Do they share a common shape?
```
semantic goal
    ↓
capability request
    ↓
backend-specific action
    ↓
measurement
    ↓
episode
```

Or does each backend require its own pipeline?

Preserve the distinction between what is shared and what is backend-specific.

**Deliverable:** Operation shape analysis. Document what unifies; document what diverges.

---

### Step 8: Conditional Routing

If Step 7 identifies a shared shape:
- Build a router that dispatches semantic requests to backend handlers
- Each handler (Serum, Ableton) implements the common interface

If Step 7 finds no shared shape:
- Document why
- Preserve separate execution paths
- Revisit in future phases

Do not build a router speculatively.

**Deliverable:** Router implementation (if justified) or analysis (if not).

---

### Step 9: Architecture Freeze + Benchmark

Freeze the producer architecture:
- Semantic goal → Capability request → Backend dispatch
- Learning via episode retrieval + episode polarity
- Knowledge as advisory layer
- Authority chain separate from learning chain

Run benchmark suite:
- Execution correctness
- Learning influence (Step 3 proof)
- Decision quality improvement (Step 3 Level 2)
- Multi-target breadth

**Deliverable:** Frozen architecture documentation + benchmark results.

---

## Key Principles

**Evidence-driven, not design-first:**
- Abstractions are extracted from concrete observation
- No universal schema until observation justifies it
- Ableton is added to test for shared shape, not validate assumed shape

**Learning ladder:**
```
Episode storage
    ↓
Retrieval influence
    ↓
Decision improvement
    ↓
Knowledge promotion
```

**Authority separation:**
```
EPISODE LAYER (learning)       vs    EVIDENCE LAYER (capability authority)
├─ learning_eligible                 ├─ EvidenceRecord
├─ experience_polarity               ├─ ClaimDefinition
├─ decision                          ├─ ClaimEngine
└─ measurement                       ├─ CapabilityContract
                                     └─ Admission gate

No shortcut between them.
```

**Semantic IR (no indices):**
- Targets: `Env1.Release`, `Filter.Cutoff`, `FXEQ.Freq1`
- Not: numeric indices or family names
- Resolution happens in compiler context layer

**Provenance:**

Tutorial statements and experimental observations have different provenance.

Both MAY contribute to EvidenceRecords under the evidence policy, with their provenance preserved.

A source-backed record alone cannot authorize execution.

---

## Removed from Scope

**serum-mcp** is OUT of the architecture (not deferred).

Reason: Serum control via DawDreamer + VST3 is sufficient to test producer feedback semantics. A separate preset ecosystem is not a prerequisite.

If preset authoring becomes necessary in a future phase, it can be added then.

---

## Current Hypothesis

```
Claude Code (producer intent)
    ↓
Semantic producer goal
    ↓
Capability request
    ↓
Backend-specific execution
    ↓
Measurement + episode
    ↓
Learning retrieval
```

This is a working hypothesis, not a frozen architecture. Step 7 will test it.

---

## Relationship to Numbered Roadmap

This roadmap (Steps 0–9) defines the producer-learning proof sequence.

The numbered roadmap (16.5.x → 16.6) defines the full end-to-end production path.

They are orthogonal:
- Producer learning validates the feedback loop in isolation
- Numbered roadmap validates integration into a full Ableton production

The numbered roadmap assumes producer learning is sound. This roadmap proves it.

---

**Last updated:** 2026-09-12  
**Status:** Ready for Step 1

