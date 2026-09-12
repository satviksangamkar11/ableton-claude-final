# STEP 5.5 — KNOWLEDGE NORMALIZATION

**Phase:** Design (no implementation yet)  
**Status:** Proposal  
**Input:** 36 retained propositions from 5.4-Q (36 retained + 5 UNKNOWN)  
**Output:** Canonical KnowledgeItem instances ready for persistence (5.6)  
**Constraint:** Preserve meaning rather than improve interpretation  

---

## 1. INPUT/OUTPUT CONTRACT

### Input
- **Source:** `yt_74ab96e1f377_proposition_extraction_5_4_q_repaired.json`
- **Count:** 36 classified propositions + 5 explicitly UNKNOWN
- **Each proposition contains:**
  - `proposition_id`: Unique identifier
  - `original_text`: Exact source text (immutable)
  - `kind`: Semantic classification (CONCEPT, PROCEDURE, PRINCIPLE, etc.)
  - `source_segment_ids`: Exact transcript segments
  - `epistemic_status`: SOURCE_REPORTED, SOURCE_RECOMMENDED, or SOURCE_OBSERVED
  - `ambiguity`: Null or "semantic function unclear"
  - `candidate_classes`: For UNKNOWN, list of candidate interpretations
  - `semantic_classifier_rationale`: How classifier arrived at decision

### Output
- **Format:** List of `KnowledgeItem` instances (JSON)
- **File:** `yt_74ab96e1f377_knowledge_normalized_5_5.json`
- **Each KnowledgeItem contains:**
  ```json
  {
    "identity": {
      "knowledge_id": "know_000000",
      "source_id": "yt_74ab96e1f377",
      "created_phase": "5.5"
    },
    "source_reference": {
      "proposition_id": "prop_000000",
      "source_segment_ids": [...],
      "original_text": "...",
      "start_time_sec": 0.16,
      "end_time_sec": 44.36
    },
    "original_proposition": {
      "raw_text": "...",
      "classification": "CONTEXT"
    },
    "normalized_proposition": {
      "text": "...",
      "transformations_applied": [...]
    },
    "type": "CONTEXT",
    "semantic_bindings": [...],
    "confidence": 0.85,
    "epistemic_status": "SOURCE_REPORTED",
    "ambiguity": null,
    "conditions": [],
    "limitations": [],
    "extraction_metadata": {
      "normalization_status": "NORMALIZED",
      "refusal_reason": null
    }
  }
  ```

---

## 2. ALLOWED TRANSFORMATIONS

These preservations and light reformattings are acceptable:

### 2.1 Format Normalization
- Whitespace normalization (collapse multiple spaces, trim)
- Punctuation consistency (no semantic change)
- Line break removal for readability
- Example: `"Decay is   the amount..."` → `"Decay is the amount..."`

### 2.2 Deterministic ID Generation
- Generate `knowledge_id` from hash of (source_id + proposition_id)
- Ensures reproducibility without inventing meaning

### 2.3 Classification → KnowledgeType Mapping
- Map 5.4 semantic classification to KnowledgeType enum:
  ```
  CONCEPT      → KnowledgeType.CONCEPT (definition)
  PROCEDURE    → KnowledgeType.PROCEDURE (instruction)
  PRINCIPLE    → KnowledgeType.PRINCIPLE (causal/mechanism)
  OBSERVATION  → KnowledgeType.OBSERVATION (feature/property)
  RECOMMENDATION → KnowledgeType.RECOMMENDATION (suggestion)
  CONDITION    → KnowledgeType.CONDITION (scope)
  EXAMPLE      → KnowledgeType.EXAMPLE (illustration)
  CONTEXT      → KnowledgeType.CONTEXT (framing)
  LIMITATION   → KnowledgeType.LIMITATION (boundary)
  UNKNOWN      → KnowledgeType.AMBIGUOUS (unresolved)
  ```

### 2.4 Provenance Transfer
- Copy source_segment_ids, original_text, timestamps exactly
- Preserve epistemic_status unchanged
- Record extraction_confidence and classifier_rationale as metadata

### 2.5 Metadata Attachment
- Add normalization_status: "NORMALIZED", "UNCHANGED", "REJECTED"
- Add refusal_reason if item is rejected
- Record transformations_applied (list of transformation names)

### 2.6 Clearer Restatement (with conditions)
- **Only when:** Original text has grammatical issues or transcript artifacts (e.g., "[Music]" tags, partial words)
- **And:** The restatement is deterministically derivable from source
- **And:** Meaning is identical (not interpreted/improved)
- **Example allowed:** `"There's a [Music] arpeggiator that takes chords and sequences them."` → `"There is an arpeggiator that takes chords and sequences them."`
- **Example forbidden:** `"Decay controls note endings."` → `"Decay determines articulation."` (interpretation)

### 2.7 Semantic Bindings (explicit)
- Extract references to synthesis concepts when supported by schema
- Example: Text mentions "oscillator" → add `semantic_binding: { type: "device_reference", value: "oscillator" }`
- **Only for explicitly supported bindings** (no invented mappings)

---

## 3. FORBIDDEN TRANSFORMATIONS

These changes violate the normalization boundary and must trigger REJECTION:

### 3.1 Inventing Facts
- Adding details not in source text
- Example: Source says "Decay is the time to reach sustain" → **Forbidden:** Adding "approximately 100–500ms" if not stated

### 3.2 Inventing Targets
- Mapping to backend systems (Serum parameters, Ableton devices) not explicitly referenced
- Example: Source mentions envelope behavior → **Forbidden:** Mapping to `ADSR` device class if not named

### 3.3 Inventing Values
- Assigning quantitative bounds, ranges, or thresholds not in source
- Example: Source says "use short release" → **Forbidden:** Mapping to "< 500ms"

### 3.4 Inventing Causes
- Adding causal claims not directly stated
- Example: Source describes "shorter release sounds tighter" → **Forbidden:** Claiming "causes reduced resonance" if not stated

### 3.5 Strengthening Recommendations
- Turning tentative suggestions into stronger claims
- Example: Source says "try shorter release" → **Forbidden:** Normalizing to "use shorter release" (upgrading from suggestion to directive)

### 3.6 Removing Qualifiers
- Deleting uncertainty markers, conditions, or scope boundaries
- Example: Source says "In some cases, filters help with brightness" → **Forbidden:** Normalizing to "Filters help with brightness" (loses scope)

### 3.7 Silently Resolving Ambiguity
- Forcing an UNKNOWN into a class without evidence
- Example: UNKNOWN item with candidates [PRINCIPLE, OBSERVATION] → **Forbidden:** Picking PRINCIPLE and normalizing as if certain

### 3.8 Adding Backend-Specific Meaning
- Mapping to Serum-specific capabilities not mentioned in source
- Example: Source discusses "filter modulation" → **Forbidden:** Mapping to "CutoffFreq MATRIX routing" (invents backend binding)

### 3.9 Epistemic Upgrade
- Changing SOURCE_REPORTED to SOURCE_RECOMMENDED or SOURCE_OBSERVED without source evidence
- Example: Source says "many people use reverb" (reported) → **Forbidden:** Upgrading to "use reverb" (recommendation)

### 3.10 Loss of Meaningful Qualification
- Removing "except", "unless", "when", "for", "in this case" scope words
- Example: "For bright tone, use saw wave" → **Forbidden:** Dropping "for bright tone" context

### 3.11 Execution Authority
- Creating directives ("must", "do this", "required") not in source
- Example: "You can adjust decay" (observation) → **Forbidden:** "Adjust decay to achieve sustain"

### 3.12 CapabilityContract/EvidenceRecord Creation
- Normalization must not create, infer, or imply capability contracts
- **No:** "This proves OSC1 supports waveform modulation"
- **Yes:** "Source mentions waveform modulation in OSC1"

---

## 4. RULES FOR EACH KnowledgeType

### 4.1 CONCEPT
- **Semantic function:** Definition or explanation of what something is
- **Normalization rules:**
  - Preserve "is", "is a", "is the", "is defined as" structures exactly
  - Verify no procedure language ("click", "drag", "set") pollutes definition
  - Example: `"Decay is the time it takes the amplitude to reach sustain"` → No change (already clean)
  - If definition contains "[Music]" tag: Remove tag, preserve definition
- **Rejection trigger:** Definition requires causal claim or backend binding
  - Example: "Filter is a device that removes frequencies to prevent clipping" (causal) → REJECT if "prevent clipping" not in source

### 4.2 PROCEDURE
- **Semantic function:** Step-by-step actionable instruction
- **Normalization rules:**
  - Preserve imperative mood ("click", "drag", "set")
  - Verify each step is actionable (not aspirational)
  - If multiple steps span transcript segments, preserve order and segment IDs
  - Example: `"Click the oscillator, then select a saw wave"` → No change
- **Rejection trigger:** Procedure requires inventing steps or backend-specific UI paths
  - Example: Multi-platform procedure mixed together → May need splitting, not rejection

### 4.3 PRINCIPLE
- **Semantic function:** Generalized relationship, mechanism, or causal explanation
- **Normalization rules:**
  - Preserve causal language ("causes", "leads to", "results in")
  - Verify causality is stated/implied in source (not invented)
  - For comparative principles ("X does Y; Z does W"), preserve both clauses
  - Example: `"Shorter release creates tighter articulation"` → No change
- **Rejection trigger:** Causal claim requires evidence the source doesn't provide
  - Example: "Shorter release tightens notes" (source says) → Normalized as stated
  - Example: "Shorter release causes neural accommodation" (not mentioned) → REJECT

### 4.4 OBSERVATION
- **Semantic function:** Descriptive statement about existing property, feature, or capability
- **Normalization rules:**
  - Preserve "there is", "you can", "contains", "includes", "provides" structures
  - Verify statement describes capability/property, not instruction
  - Example: `"Serum contains three main sound generators"` → No change
- **Rejection trigger:** Observation requires backend-specific detail invention
  - Example: "The UI shows waveform options" (source says) → OK
  - Example: "The Sine waveform option uses 16-point interpolation" (not mentioned) → REJECT

### 4.5 RECOMMENDATION
- **Semantic function:** Source-endorsed preference or suggestion
- **Normalization rules:**
  - Preserve "I recommend", "try", "consider", "suggest" language
  - Verify recommendation is source-attributed (not invented)
  - Do NOT upgrade to directive ("must", "should")
  - Example: `"Try a shorter release for tighter plucks"` → No change
- **Rejection trigger:** Recommendation strengthened beyond source language
  - Example: "Use shorter release for tight plucks" (source says "try", we say "use") → Strengthen warning → REJECT

### 4.6 CONDITION
- **Semantic function:** Circumstance or constraint specifying when something applies
- **Normalization rules:**
  - Preserve "for", "when", "if", "unless", "in" scope words
  - Verify condition clause is complete (not fragmented)
  - Example: `"For plucks, shorter releases work better"` → No change
- **Rejection trigger:** Condition requires inventing scope not in source
  - Example: "When cutting frequencies, use resonance < 2.0" (threshold invented) → REJECT

### 4.7 EXAMPLE
- **Semantic function:** Concrete instance illustrating another concept
- **Normalization rules:**
  - Preserve "for example", "such as", "like" markers
  - Preserve specific instance (e.g., "saw wave")
  - Verify example serves to illustrate, not define
  - Example: `"Like a string resonator, this creates harmonic feedback"` → No change
- **Rejection trigger:** Example requires inventing specific instance not in source

### 4.8 CONTEXT
- **Semantic function:** Background, framing, credentials, or organizational information
- **Normalization rules:**
  - Preserve biographical/credentials language ("after teaching", "being one of")
  - Preserve transitions ("next", "so to summarize", "in this section")
  - **Filler rule:** CONTEXT that is purely organizational (no knowledge value) should NOT be persisted to canonical storage
  - Example: `"After teaching Serum for ten years..."` → Normalize
  - Example: `"We'll cover this in a dedicated video"` → REJECT (filler, not knowledge)
- **Rejection trigger:** Context that is pure filler/scope navigation

### 4.9 LIMITATION
- **Semantic function:** Restriction, exception, boundary, or statement about what does not apply
- **Normalization rules:**
  - Preserve "don't", "avoid", "cannot", "limited to" language
  - Verify limitation is absolute or well-scoped (not invented)
  - Example: `"Don't use extreme resonance on vocals"` → No change
- **Rejection trigger:** Limitation invented without source basis
  - Example: "Can't use more than 8 effect slots" (not mentioned) → REJECT

### 4.10 AMBIGUOUS (from UNKNOWN)
- **Semantic function:** Unresolved semantic function (multiple interpretations equally valid)
- **Normalization rules:**
  - Do NOT force into a class
  - Preserve original text verbatim
  - Enumerate candidate_interpretations (from classifier output)
  - Add resolution_attempt: Brief description of why classification failed
  - Example:
    ```json
    {
      "type": "AMBIGUOUS",
      "original_text": "now all you need to know is that these make up the building blocks of our sound",
      "candidate_interpretations": ["OBSERVATION", "PRINCIPLE", "PROCEDURE"],
      "resolution_attempt": "Could describe existing architecture (OBSERVATION), explain how components relate (PRINCIPLE), or prescribe mental model (PROCEDURE)",
      "normalization_status": "UNRESOLVED"
    }
    ```
- **Rejection trigger:** None — ambiguous items must be preserved and explicitly marked

---

## 5. AMBIGUITY POLICY

### 5.1 UNKNOWN Handling
- **Do NOT force classification.** Preserve as `type: AMBIGUOUS`
- **Record candidate_interpretations** from classifier output
- **Add resolution_attempt** explaining why disambiguation failed
- **Example:**
  ```json
  {
    "proposition_id": "prop_000003",
    "type": "AMBIGUOUS",
    "original_text": "now all you need to know is that these make up the building blocks of our sound",
    "candidate_classes": ["OBSERVATION", "PRINCIPLE", "PROCEDURE"],
    "ambiguity_reason": "semantic function unclear — could be describing architecture, explaining relationships, or prescribing mental model",
    "normalization_status": "UNRESOLVED"
  }
  ```

### 5.2 Context-Based Disambiguation (limited)
- If source provides immediate contextual clues (in adjacent segments), may attempt disambiguation
- **Only if:** The context is within the same source and explicitly resolves ambiguity
- **Example:** If preceding segment says "to understand signal flow", then ambiguous item becomes PRINCIPLE (contextually resolved)
- **Not allowed:** Importing context from Serum manual, other videos, or external knowledge

### 5.3 Ambiguity Preservation in Ledger
- Keep unresolved items in the normalization ledger with status "UNRESOLVED"
- These items are candidates for manual review or future refinement, not automatic forcing

---

## 6. MULTI-SEGMENT POLICY

### 6.1 Definition
- A proposition may span multiple transcript segments (e.g., prop spans seg_0100–seg_0115)
- Normalization must preserve all segment IDs and reconstruct meaning from concatenated source

### 6.2 Handling
- **Preserve segment structure:** Store full list of segment IDs
- **Do NOT split:** Multi-segment items stay as single KnowledgeItem (not broken into per-segment items)
- **Do NOT merge:** Separate propositions with separate segment lists remain separate
- **Example:** A 5-segment definition stays as one CONCEPT KnowledgeItem with 5 segment IDs

### 6.3 Concatenation Rule
- If source text spans segments: Join with single space, preserve order
- Remove transcript artifacts ("[Music]", "[Pause]") when joining

---

## 7. FILLER POLICY

### 7.1 Definition
- FILLER propositions: Promotional, organizational, or navigation statements with no knowledge value
- Examples: "Subscribe to the channel", "Thanks for watching", "Click the link below"

### 7.2 Storage
- **Do NOT persist FILLER to canonical knowledge storage**
- **Do preserve in extraction artifact** for auditability (already done in 5.4)
- **Ledger entry:** Record as "REJECTED — FILLER" with no knowledge_id

### 7.3 Boundary Cases
- "We'll cover this in a dedicated video" (meta-commentary) → FILLER (rejected)
- "In this section, we'll explore modulation" (CONTEXT framing) → Not filler (normalized)
- "Like and subscribe for more content" → FILLER (rejected)

---

## 8. DUPLICATE POLICY

### 8.1 Definition
- Two items are duplicates if they reference identical semantic meaning from the same source
- **Note:** Different phrasings of the same concept from the same source are NOT automatically merged

### 8.2 Handling
- **Do NOT automatically merge** similar-looking items
- **Do preserve source boundaries:** Each source observation stays separate unless a later deduplication design explicitly handles cross-proposition provenance
- **Rationale:** Future deduplication logic may need to know that the same fact was mentioned twice, or in different contexts

### 8.3 Example
- Prop A: "Decay is the time to reach sustain" (seg_0050)
- Prop B: "Decay measures the sustain transition" (seg_0200)
- **Action:** Keep both KnowledgeItems, with different knowledge_ids
- **Ledger:** Separate entries, noting semantic similarity but preserving source lineage

---

## 9. PROVENANCE POLICY

### 9.1 Immutable Source Reference
- Every KnowledgeItem must record:
  - Original transcript text (exact)
  - Source segment IDs (complete)
  - Start/end timestamps
  - Source ID (yt_74ab96e1f377)
  - Proposition ID (prop_XXXXXX)

### 9.2 Transformation Audit Trail
- Record all transformations applied:
  - format_normalization (yes/no)
  - artifact_removal ("[Music]" tags removed, count)
  - whitespace_collapsing (yes/no)
  - restatement_for_clarity (yes/no) + reason
- **No:** Do not hide transformations in "normalized_text"

### 9.3 Refusal Recording
- If item is rejected, record:
  - rejection_reason (e.g., "INVENTS_CAUSAL_CLAIM", "FILLER", "BACKEND_SPECIFIC")
  - rejected_text (original)
  - proposed_transformation (what normalization would have created, for review)

---

## 10. SEMANTIC-BINDING POLICY

### 10.1 Definition
- Semantic binding: Explicit connection between source text and a supported ontology term
- Examples:
  - Text mentions "oscillator" → binding: { type: "device_class", value: "oscillator" }
  - Text mentions "modulation" → binding: { type: "concept", value: "modulation" }

### 10.2 Allowed Bindings
- Only bindings explicitly supported by the schema (to be defined in 5.5 implementation)
- **Not allowed:** Inventing bindings for backend systems (e.g., mapping to Serum MATRIX if not mentioned)

### 10.3 Example
- Source: "An arpeggiator takes chords and sequences them into melodies"
- Binding: `{ type: "device_class", value: "arpeggiator" }` (explicit mention)
- **Not:** Mapping to "serum_arpeggiator" or adding backend-specific behavior

---

## 11. BACKEND-INDEPENDENCE POLICY

### 11.1 Core Rule
- Normalization must not create Serum-specific knowledge, mappings, or capability implications
- Example: "Envelopes modulate parameters" → OK (universal)
- Example: "Serum's envelope modulator uses ADSR stages" → Requires explicit source mention

### 11.2 Verification
- Before normalization, verify:
  - No invented backend mappings
  - No Serum-specific parameter names injected
  - No capability contracts inferred
  - No execution authority implied

---

## 12. NORMALIZATION LEDGER

### 12.1 Format
- JSON file: `yt_74ab96e1f377_normalization_ledger_5_5.json`
- Each entry records:
  ```json
  {
    "proposition_id": "prop_000000",
    "knowledge_id": "know_000000 OR null if rejected",
    "status": "NORMALIZED | UNCHANGED | REJECTED | UNRESOLVED",
    "rejection_reason": null or "INVENTS_FACT" / "FILLER" / "BACKEND_SPECIFIC" / etc.",
    "transformations_applied": ["format_normalization", "artifact_removal"],
    "confidence": 0.85,
    "notes": "..."
  }
  ```

### 12.2 Audit
- Ledger enables verification that:
  - Every proposition was processed
  - Rejections have documented reasons
  - Transformations are traceable
  - No silent discards

---

## 13. VALIDATION RULES

### 13.1 Per-Item Validation
- [ ] `original_text` matches source artifact exactly
- [ ] `source_segment_ids` are continuous and valid
- [ ] `normalized_text` (if changed) preserves meaning
- [ ] `type` matches a valid KnowledgeType enum
- [ ] If `type == AMBIGUOUS`, `candidate_interpretations` is not empty
- [ ] No forbidden transformations detected (causal upgrade, backend injection, etc.)
- [ ] Provenance is complete (source_id, proposition_id, segments, timestamps)

### 13.2 Artifact-Level Validation
- [ ] All 36 non-UNKNOWN propositions appear in output (as NORMALIZED, UNCHANGED, or REJECTED)
- [ ] All 5 UNKNOWN propositions appear as type AMBIGUOUS
- [ ] Ledger counts match (36 + 5 = 41 total items processed)
- [ ] No knowledge_ids collide (hash-based IDs are deterministic)
- [ ] No FILLER items in canonical storage
- [ ] Epistemic statuses match source (no upgrades)

---

## 14. TESTS

### 14.1 Unit Tests
- `test_normalization_no_invents_fact`: Verify proposed transformation doesn't add facts
- `test_normalization_preserves_meaning`: Verify normalized text means same as original
- `test_normalization_rejects_causal_upgrade`: Verify "try X" doesn't become "use X"
- `test_normalization_rejects_backend_binding`: Verify no Serum-specific mappings injected
- `test_unknown_not_forced`: Verify UNKNOWN items remain AMBIGUOUS, not forced

### 14.2 Integration Tests
- `test_full_extraction_to_normalized_pipeline`: 36+5 propositions → KnowledgeItems
- `test_ledger_completeness`: All 41 items in ledger, no gaps
- `test_provenance_immutable`: Original text unchanged, segment IDs preserved
- `test_filler_excluded`: No FILLER items in canonical output

### 14.3 Acceptance Criteria
- [ ] All unit tests PASS
- [ ] All integration tests PASS
- [ ] Ledger validation PASS (all 41 items accounted for)
- [ ] Manual spot check on 3 borderline cases (ambiguous, multi-segment, filler boundaries)
- [ ] Zero rejected items with unjustified rejection reasons
- [ ] Zero unresolved ambiguities that could be resolved from source

---

## 15. ACCEPTANCE GATES

### Gate 5.5-1: Design Approval
- [ ] STEP_5_5_PROPOSAL.md reviewed and approved
- [ ] All forbidden transformations explicitly listed
- [ ] All KnowledgeType rules defined
- [ ] Ambiguity policy documented
- [ ] Unresolved questions identified

### Gate 5.5-2: Implementation Readiness
- [ ] KnowledgeItem schema exists (from 5.2) and is accessible
- [ ] All 41 propositions loaded from 5.4 artifact
- [ ] Normalization rules coded and unit-tested
- [ ] Ledger format finalized

### Gate 5.5-3: Normalization Completeness
- [ ] All 36 classified propositions normalized
- [ ] All 5 UNKNOWN preserved as AMBIGUOUS
- [ ] Normalization ledger complete (41 items, no gaps)
- [ ] Zero FILLER in canonical output

### Gate 5.5-4: Validation
- [ ] All 13.1 per-item validations PASS
- [ ] All 13.2 artifact-level validations PASS
- [ ] Spot-check on 3 borderline cases approved
- [ ] Provenance audit confirms no data loss

### Gate 5.5-5: Semantics Verification
- [ ] No causal claims upgraded beyond source
- [ ] No backend-specific mappings invented
- [ ] No execution authority implied
- [ ] All rejections justified in ledger

---

## 16. UNRESOLVED DESIGN QUESTIONS

### 16.1 Semantic Bindings Schema
- **Open:** What is the complete set of supported semantic binding types?
- **Dependency:** 5.2 KnowledgeItem schema must be consulted
- **Action:** Extract from 5.2 schema; if not defined there, defer binding layer to 5.6

### 16.2 Ambiguity Resolution Criteria
- **Open:** If context from adjacent segments can disambiguate UNKNOWN, should normalization attempt it?
- **Current:** Limited — only if context is in source and unambiguous
- **Action:** Freeze this rule; allow future refinement based on implementation experience

### 16.3 CONTEXT Filler Boundary
- **Open:** Is "In this section, we'll explore X" knowledge or organizational filler?
- **Current:** Treated as CONTEXT (knowledge), not filler
- **Rationale:** Provides frame for understanding scope; not purely promotional
- **Action:** Accept current boundary; audit borderline cases during implementation

### 16.4 Deduplication Strategy
- **Open:** How should cross-source deduplication work (when multiple videos mention same fact)?
- **Current:** Deferred — preserve source boundaries in 5.5, handle in later design
- **Action:** Document for 5.5.1 or 5.6

### 16.5 Multi-Backend Support
- **Open:** Should normalization anticipate future backends (Live, Bitwig, etc.)?
- **Current:** No — remain backend-independent and universal
- **Action:** Design binding layer (16.6+) to handle backend-specific mappings separately

---

## IMPLEMENTATION GATE

**5.5 DESIGN COMPLETE**

Do not proceed to 5.5 implementation until:
- [ ] This proposal is reviewed
- [ ] All 16 sections are approved
- [ ] Unresolved questions (section 16) are either answered or confirmed deferred
- [ ] STEP_5_5_PROPOSAL.md is committed to git

**Next action:** Return to design review.
