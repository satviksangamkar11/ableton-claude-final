# STEP 5.5 — KNOWLEDGE NORMALIZATION

**Phase:** Design (no implementation yet)  
**Status:** Proposal (REVISION 1 — addresses 5.2 schema conformance)  
**Input:** 36 retained propositions from 5.4-Q (31 classified + 5 UNKNOWN)  
**Output:** Canonical KnowledgeItem instances ready for persistence (5.6)  
**Constraint:** Preserve meaning rather than improve interpretation  
**Schema:** Use frozen 5.2 KnowledgeItem structure (no modifications)  

---

## 1. INPUT/OUTPUT CONTRACT

### Input
- **Source:** `yt_74ab96e1f377_proposition_extraction_5_4_q_repaired.json`
- **Exact count breakdown from 5.4-Q artifact:**
  ```
  36 total propositions retained
  
  CONCEPT        = 3
  PROCEDURE      = 3
  PRINCIPLE      = 6
  OBSERVATION    = 6
  RECOMMENDATION = 0
  CONDITION      = 0
  EXAMPLE        = 11
  CONTEXT        = 2
  LIMITATION     = 0
  ────────────────────
  Classified     = 31
  
  UNKNOWN        = 5 (unresolved semantic function)
  ────────────────────
  TOTAL          = 36
  ```
- **Each proposition contains:**
  - `proposition_id`: Unique identifier
  - `original_text`: Exact source text (immutable)
  - `kind`: Semantic classification (CONCEPT, PROCEDURE, PRINCIPLE, OBSERVATION, RECOMMENDATION, CONDITION, EXAMPLE, CONTEXT, LIMITATION, or UNKNOWN)
  - `source_segment_ids`: Exact transcript segments
  - `epistemic_status`: SOURCE_REPORTED, SOURCE_RECOMMENDED, or SOURCE_OBSERVED
  - `ambiguity`: Null or "semantic function unclear"
  - `candidate_classes`: For UNKNOWN items only, list of candidate interpretations
  - `semantic_classifier_rationale`: How classifier arrived at decision

### Output
- **Format:** List of `KnowledgeItem` instances (JSON), conforming to 5.2 schema
- **File:** `yt_74ab96e1f377_knowledge_normalized_5_5.json`
- **Uses frozen 5.2 KnowledgeItem structure:**
  - `knowledge_item_id`: Deterministic stable ID (hash of source_id + segment_ids)
  - `source_reference`: SourceReference (source_id, source_type, segment_ids, start_time_sec, end_time_sec)
  - `original_proposition`: Original text (NEVER modified)
  - `knowledge_type`: One of 9 KnowledgeTypes (CONCEPT, PROCEDURE, PRINCIPLE, OBSERVATION, RECOMMENDATION, CONDITION, EXAMPLE, CONTEXT, LIMITATION)
  - `epistemic_status`: EpistemicStatus enum (SOURCE_REPORTED, SOURCE_RECOMMENDED, SOURCE_OBSERVED, or UNKNOWN for unresolved)
  - `normalized_proposition`: Optional clearer restatement (null if original is clear)
  - `semantic_bindings`: List of SemanticBinding instances (dimension, value, confidence, ambiguity)
  - `extraction_confidence`: 0.0-1.0 (from 5.4 classifier)
  - `ambiguity`: Null or explanation string
  - `conditions`: List of scope constraints
  - `limitations`: List of boundaries
  - `extraction_metadata`: ExtractionMetadata (timestamp, method, confidence, status)
  - `notes`: Optional transformation audit trail

**CRITICAL:** Do NOT add new fields or modify the 5.2 schema during 5.5 normalization.

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

### 2.3 Classification → KnowledgeType Mapping (Frozen 5.2 Schema)
- Map 5.4 semantic classification to the 9 frozen KnowledgeType enum values:
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
  UNKNOWN      → Pick best-guess from candidates; use epistemic_status=UNKNOWN (see section 5)
  ```
- Do NOT add new KnowledgeType values; use frozen 5.2 enum only

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
  - Preserve transitions that frame knowledge scope ("next", "so to summarize", "in this section")
  - **CRITICAL BOUNDARY (issue #4):** CONTEXT vs course/video metadata
    - **CONTEXT (retain):** Information that orients the learner's understanding of the music/production knowledge itself
      - Example: `"After teaching Serum for ten years, I've learned..."` (credentials for expertise)
      - Example: `"In this section, we'll explore how filters affect tone"` (scopes knowledge to filters)
    - **NOT CONTEXT / FILLER (reject):** Information about the course structure, video production, or platform navigation
      - Example: `"We'll cover this in a dedicated video"` (meta-commentary about video production)
      - Example: `"Click the link below for more content"` (platform/social navigation)
      - Example: `"I'll make a separate video about effects"` (course planning, not music knowledge)
  - **Decision rule:** Ask: "Does this help me understand the music/production knowledge, or does it describe the course/video/platform?" If the latter, it's filler/not-knowledge.
- **Rejection trigger:** Course/video metadata or navigation statements

### 4.9 LIMITATION
- **Semantic function:** Restriction, exception, boundary, or statement about what does not apply
- **Normalization rules:**
  - Preserve "don't", "avoid", "cannot", "limited to" language
  - Verify limitation is absolute or well-scoped (not invented)
  - Example: `"Don't use extreme resonance on vocals"` → No change
- **Rejection trigger:** Limitation invented without source basis
  - Example: "Can't use more than 8 effect slots" (not mentioned) → REJECT

### 4.10 Handling UNKNOWN from 5.4 (Uses 5.2 EpistemicStatus.UNKNOWN)
- **Semantic function:** Unresolved semantic function (multiple interpretations equally valid)
- **Normalization rules (see section 5 for details):**
  - Do NOT force into a final class
  - Pick best-guess KnowledgeType from classifier's candidates
  - Set `epistemic_status` to UNKNOWN (5.2 enum value)
  - Set `ambiguity` field to explain why classification failed
  - Set `extraction_confidence` LOW (0.4–0.6)
  - Preserve candidate_interpretations in `notes` field
  - Example:
    ```json
    {
      "knowledge_item_id": "ki_...",
      "knowledge_type": "OBSERVATION",  // best guess
      "epistemic_status": "UNKNOWN",    // signals unresolved
      "original_proposition": "now all you need to know is that these make up the building blocks of our sound",
      "ambiguity": "Could describe existing architecture (OBSERVATION), explain how components relate (PRINCIPLE), or prescribe mental model (PROCEDURE)",
      "notes": "Candidates: [OBSERVATION, PRINCIPLE, PROCEDURE]. Classifier could not determine semantic function.",
      "extraction_confidence": 0.5
    }
    ```
- **Rejection trigger:** None — unresolved items must be preserved and explicitly marked

---

## 5. AMBIGUITY POLICY (ISSUE #6 FIX)

### 5.1 UNKNOWN Handling — Use 5.2 EpistemicStatus.UNKNOWN
- **Do NOT invent new KnowledgeType.** Use the frozen 5.2 schema
- **For UNKNOWN propositions from 5.4:**
  1. Pick the best-candidate KnowledgeType from the classifier's candidate_classes
  2. Set `epistemic_status` to `UNKNOWN` (not `SOURCE_REPORTED`)
  3. Set `ambiguity` field to explain why semantic function is unresolved
  4. Preserve `candidate_classes` information in `notes` field (audit trail)
  5. Set `extraction_confidence` LOW (0.4–0.6) to signal uncertainty

- **Real example from 5.4-Q (prop_000003):**
  ```
  Source text: "now all you need to know is that these make up the building 
               blocks of our sound"
  Candidates: [OBSERVATION, PRINCIPLE, PROCEDURE]
  
  Normalized KnowledgeItem (using frozen 5.2 schema only):
  {
    "knowledge_item_id": "ki_a7f3e2b1c4d5e6f8",
    "source_reference": {
      "source_id": "yt_74ab96e1f377",
      "source_type": "YOUTUBE_VIDEO",
      "segment_ids": ["seg_0003", "seg_0004"],
      "start_time_sec": 5.2,
      "end_time_sec": 8.7
    },
    "original_proposition": "now all you need to know is that these make up the building blocks of our sound",
    "knowledge_type": "OBSERVATION",      // BEST GUESS from candidates
    "epistemic_status": "UNKNOWN",         // EXPLICIT UNRESOLVED FLAG
    "normalized_proposition": null,
    "semantic_bindings": [],
    "extraction_confidence": 0.5,         // LOW confidence signals ambiguity
    "ambiguity": "semantic function unclear — could be describing architecture (OBSERVATION), explaining relationships (PRINCIPLE), or prescribing mental model (PROCEDURE)",
    "notes": "Candidates from classifier: [OBSERVATION, PRINCIPLE, PROCEDURE]. No clear semantic function markers in text. Best guess: OBSERVATION (neutral).",
    "conditions": [],
    "limitations": [],
    "extraction_metadata": {
      "extraction_timestamp": "2026-09-12T20:35:00Z",
      "extraction_method": "semantic_classification_5_4_q",
      "extraction_confidence": 0.5,
      "raw_extraction_status": "EXTRACTED"
    }
  }
  ```

- **Why this is valid 5.2 conformance:**
  - Uses one of 9 frozen KnowledgeType values (OBSERVATION, not invented AMBIGUOUS)
  - Uses EpistemicStatus.UNKNOWN from frozen 5.2 enum
  - Uses existing `ambiguity` field (5.2 schema supports it)
  - Uses existing `notes` field for audit trail
  - Sets extraction_confidence LOW to signal uncertainty
  - No new fields; no schema modification

### 5.2 Assigning Best-Guess KnowledgeType for UNKNOWN
- **Deterministic rule:** When 5.4 gives candidates `[A, B, C]`, normalization picks ONE:
  1. If one candidate appears clearly dominant in text, choose it
  2. If tied or unclear, apply priority order (lowest risk first):
     - OBSERVATION (safest: just describes, no causal claim)
     - PRINCIPLE (moderate: explains relationships)
     - PROCEDURE (higher risk: implies action/imperative)
     - Never pick CONCEPT, RECOMMENDATION, CONDITION, LIMITATION, EXAMPLE, CONTEXT as defaults
  3. Set `extraction_confidence` = 0.4–0.6 (always LOW for UNKNOWN)
  4. Set `epistemic_status` = UNKNOWN (not SOURCE_REPORTED, not SOURCE_RECOMMENDED)
  5. Set `ambiguity` = exact reason for unresolved status
  
- **Example:** Candidates [OBSERVATION, PRINCIPLE, PROCEDURE] → Pick OBSERVATION (safest)
- **Example:** Candidates [PRINCIPLE, PROCEDURE] → Pick PRINCIPLE (avoids implied action)
- **Invariant:** `extraction_confidence` stays LOW; never upgrade to 0.7+ for UNKNOWN items

### 5.3 Context-Based Disambiguation (limited)
- If source provides immediate contextual clues (in adjacent segments), may attempt disambiguation
- **Only if:** The context is within the same source and explicitly resolves ambiguity
- **Example:** If preceding segment says "to understand signal flow", then ambiguous item clarifies as PRINCIPLE (contextually resolved)
- **If disambiguated:** Upgrade `epistemic_status` to `SOURCE_REPORTED`, set `ambiguity` to null, raise `extraction_confidence`
- **Not allowed:** Importing context from Serum manual, other videos, or external knowledge

### 5.4 Ambiguity Preservation in Ledger
- Keep unresolved items in the normalization ledger with status "UNRESOLVED"
- Record best-guess KnowledgeType and confidence in ledger for audit
- These items are candidates for manual review or future refinement

---

## 5.5 PROVISIONAL TYPE SEMANTICS (CRITICAL FOR UNKNOWN ITEMS)

**This section clarifies semantics to prevent misinterpretation of UNKNOWN items.**

### 5.5.1 What Provisional Type Means
When an UNKNOWN item is normalized with:
```json
{
  "type": "OBSERVATION",          // ← PROVISIONAL, not resolved truth
  "epistemic_status": "UNKNOWN",
  "extraction_confidence": 0.5,
  "ambiguity": "semantic function unclear — could be OBSERVATION, PRINCIPLE, or PROCEDURE"
}
```

**This does NOT mean:** "This proposition is definitely an observation."

**This DOES mean:** "The normalization pipeline provisionally assigns OBSERVATION as the best-guess representation because the frozen 5.2 schema requires a type field, while the actual semantic function remains unresolved."

### 5.5.2 Mandatory Fields for Provisional Types
Every UNKNOWN item MUST have:
- `type`: One of 9 frozen KnowledgeTypes (best guess from candidates)
- `epistemic_status`: UNKNOWN (not SOURCE_REPORTED, not SOURCE_RECOMMENDED)
- `extraction_confidence`: LOW (0.4–0.6) — signals provisional nature
- `ambiguity`: Explains unresolved status
- `notes`: Contains `candidate_types` list from classifier

If ANY of these fields are missing, the item fails validation.

### 5.5.3 System Interpretation Rule
When consuming a normalized KnowledgeItem where `epistemic_status == UNKNOWN`:
- Treat `type` as provisional working hypothesis, not fact
- Always check `ambiguity` field before using the item
- Consult `candidate_types` (in notes) for alternative interpretations
- Never assert this as resolved knowledge without additional evidence
- Do NOT use this item to satisfy a contract that requires non-UNKNOWN epistemic status

### 5.5.4 Example — Correct Interpretation
Ledger entry:
```json
{
  "proposition_id": "prop_000003",
  "classification_from_5_4": "UNKNOWN",
  "status": "UNRESOLVED"
}
```

Corresponding KnowledgeItem:
```json
{
  "knowledge_type": "OBSERVATION",
  "epistemic_status": "UNKNOWN",
  "extraction_confidence": 0.5,
  "ambiguity": "semantic function unclear",
  "notes": "Candidates: [OBSERVATION, PRINCIPLE, PROCEDURE]"
}
```

**Correct interpretation:** "We provisionally represent this as OBSERVATION pending resolution; other interpretations are equally plausible."

**Incorrect interpretation:** "This is an observation."

---

## 6. MULTI-SEGMENT POLICY

### 6.1 Definition
- A proposition may span multiple transcript segments (e.g., prop spans seg_0100–seg_0115)
- Normalization must preserve all segment IDs and reconstruct meaning from concatenated source

### 6.2 Core Invariant (REPLACES "don't split/merge")
- **Meaning preservation rule:** Do not change proposition identity or meaning merely for normalization convenience
- Implications:
  - A multi-segment proposition remains one KnowledgeItem (don't split into per-segment items)
  - Separate propositions with distinct segment lists remain separate (don't merge for deduplication)
  - However, if 5.4 extraction accidentally grouped two independent propositions into one semantic unit, normalization MAY separate them if doing so clarifies meaning without inventing content

### 6.3 When to Separate (Issue #7)
- **Signal:** Original text contains explicit breaks in thought (e.g., "First... Second..." or "; " + semantic shift)
- **Example OK to separate:**
  - Extracted as one: `"Decay is the sustain transition time. For bright tone, shorten release."`
  - Two independent ideas: CONCEPT (decay definition) + RECOMMENDATION (bright tone advice)
  - Action: Create two KnowledgeItems, each with their own segment references
  - Ledger entry: "SEPARATED — two independent propositions detected in single extraction unit"
- **Example DO NOT separate:**
  - Extracted as one: `"Decay is the time from peak to sustain level, measured in milliseconds."`
  - Single continuous definition (no independent break)
  - Action: Keep as one CONCEPT KnowledgeItem

### 6.4 Concatenation Rule
- If source text spans segments: Join with single space, preserve order
- Remove transcript artifacts ("[Music]", "[Pause]") when joining
- If separation occurs, preserve exact segment IDs for each resulting KnowledgeItem

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

### 10.1 Use Frozen 5.2 SemanticBinding Structure
- Normalization uses the canonical SemanticBinding from 5.2 schema:
  ```python
  @dataclass
  class SemanticBinding:
    dimension: str         # e.g., "device_class", "concept", "technique"
    value: str            # e.g., "oscillator", "modulation"
    confidence: float     # 0.0-1.0
    ambiguity: Optional[str]  # Preserve unresolved ambiguity per binding
  ```
- Do NOT invent new dimensions or fields

### 10.2 Allowed Bindings
- Only extract explicit mentions from source text
- Examples:
  - Text mentions "oscillator" → binding: `{ dimension: "device_reference", value: "oscillator", confidence: 0.95, ambiguity: null }`
  - Text mentions "filter modulation" → binding: `{ dimension: "technique", value: "filter_modulation", confidence: 0.85, ambiguity: null }`
- **Not allowed:** Inventing bindings for backend systems (e.g., mapping to Serum MATRIX if not mentioned)
- **Not allowed:** Creating new dimension names not in 5.2 schema

### 10.3 Example
- Source: "An arpeggiator takes chords and sequences them into melodies"
- Binding: `{ dimension: "device_class", value: "arpeggiator", confidence: 1.0, ambiguity: null }`
- **Not:** Mapping to "serum_arpeggiator" or adding backend-specific behavior

### 10.4 Ambiguity in Bindings
- If a binding's value is ambiguous (multiple interpretations), use the `ambiguity` field:
  ```json
  { "dimension": "technique", "value": "resonance_shaping", 
    "confidence": 0.6, "ambiguity": "could mean peak emphasis or frequency carving" }
  ```

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

### 12.1 Format & Cardinality
- JSON file: `yt_74ab96e1f377_normalization_ledger_5_5.json`
- **CRITICAL: Ledger contains exactly 36 items** (31 classified + 5 UNKNOWN)
  - Do NOT confuse with "36 + 5 = 41" (incorrect earlier thinking)
  - Input is 36 propositions; ledger has 36 records; output has 36 KnowledgeItems
- Each entry records:
  ```json
  {
    "proposition_id": "prop_000000",
    "knowledge_id": "know_000000 OR null if rejected",
    "classification_from_5_4": "CONCEPT | PROCEDURE | ... | UNKNOWN",
    "status": "NORMALIZED | UNCHANGED | REJECTED | UNRESOLVED",
    "rejection_reason": null or "INVENTS_FACT" / "FILLER" / "BACKEND_SPECIFIC" / etc.",
    "transformations_applied": ["format_normalization", "artifact_removal"],
    "extraction_confidence": 0.85,
    "notes": "..."
  }
  ```

### 12.2 Audit
- Ledger enables verification that:
  - All 36 propositions were processed (31 classified + 5 UNKNOWN)
  - Rejections have documented reasons
  - Transformations are traceable
  - No silent discards or missing items

---

## 13. VALIDATION RULES

### 13.1 Per-Item Validation
- [ ] `original_text` matches source artifact exactly
- [ ] `source_segment_ids` are continuous and valid
- [ ] `normalized_text` (if changed) preserves meaning
- [ ] `knowledge_type` matches one of 9 frozen KnowledgeType enum values
- [ ] If `epistemic_status == UNKNOWN`, `ambiguity` field explains why
- [ ] If `epistemic_status == UNKNOWN`, `notes` field contains candidate_classes
- [ ] `extraction_confidence` is LOW (0.4–0.6) when `epistemic_status == UNKNOWN`
- [ ] No forbidden transformations detected (causal upgrade, backend injection, etc.)
- [ ] Provenance is complete (source_id, segment_ids, timestamps)

### 13.2 Artifact-Level Validation
- [ ] All 36 input propositions processed (31 classified + 5 UNKNOWN)
- [ ] All 36 appear in ledger with status (NORMALIZED, UNCHANGED, REJECTED, or UNRESOLVED)
- [ ] All 31 classified propositions appear in canonical storage
- [ ] All 5 UNKNOWN propositions appear with `epistemic_status == UNKNOWN` (provisional type, not resolved)
- [ ] All 5 UNKNOWN items have `ambiguity` field + `candidate_types` in notes
- [ ] All 5 UNKNOWN items have LOW `extraction_confidence` (0.4–0.6)
- [ ] No knowledge_ids collide (hash-based IDs are deterministic)
- [ ] No FILLER items in canonical storage
- [ ] Epistemic statuses preserved (no SOURCE_REPORTED→SOURCE_RECOMMENDED upgrades)
- [ ] All 9 KnowledgeType values used only from frozen 5.2 enum

---

## 14. TESTS

### 14.1 Unit Tests
- `test_normalization_no_invents_fact`: Verify proposed transformation doesn't add facts
- `test_normalization_preserves_meaning`: Verify normalized text means same as original
- `test_normalization_rejects_causal_upgrade`: Verify "try X" doesn't become "use X"
- `test_normalization_rejects_backend_binding`: Verify no Serum-specific mappings injected
- `test_unknown_uses_epistemic_status`: Verify UNKNOWN items use EpistemicStatus.UNKNOWN (not invented type)
- `test_unknown_extraction_confidence_low`: Verify epistemic_status=UNKNOWN always has extraction_confidence 0.4-0.6

### 14.2 Integration Tests
- `test_full_extraction_to_normalized_pipeline`: 31 classified + 5 UNKNOWN propositions → KnowledgeItems
- `test_unknown_preserved_with_candidates`: Verify 5 UNKNOWN items preserved with candidate_classes in notes
- `test_ledger_completeness`: All 36 items in ledger, no gaps
- `test_provenance_immutable`: Original text unchanged, segment IDs preserved
- `test_filler_excluded`: No FILLER items in canonical storage

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
- [ ] All 31 classified propositions normalized (NORMALIZED, UNCHANGED, or REJECTED)
- [ ] All 5 UNKNOWN preserved with epistemic_status=UNKNOWN (provisional type + ambiguity)
- [ ] Normalization ledger complete (36 items: 31 classified + 5 UNKNOWN, no gaps)
- [ ] Zero FILLER in canonical storage
- [ ] All UNKNOWN items have low extraction_confidence + ambiguity + candidate_types

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

### 16.1 Semantic Binding Dimensions (Issue #3)
- **Status:** RESOLVED — 5.2 schema defines SemanticBinding structure
- **Answer:** Use frozen 5.2 fields: (dimension, value, confidence, ambiguity)
- **Action:** Identify valid dimensions during implementation; do not invent new ones

### 16.2 Ambiguity Resolution Criteria (Issue #6)
- **Status:** RESOLVED — Use 5.2 EpistemicStatus.UNKNOWN
- **Answer:** Pick best-guess KnowledgeType; set epistemic_status=UNKNOWN
- **Action:** Implement context-based disambiguation only if source clarifies

### 16.3 CONTEXT vs Course/Video Metadata (Issue #4)
- **Status:** RESOLVED — Added explicit boundary rule in section 4.8
- **Answer:** CONTEXT helps understand the knowledge; metadata describes the course structure
- **Action:** Apply decision rule: "Does this help me understand the music/production knowledge, or the course?"

### 16.4 Multi-Segment Handling (Issue #5)
- **Status:** RESOLVED — Meaning-preservation rule replaces "don't split/merge"
- **Answer:** Allow separation if 5.4 grouped independent propositions; preserve segment IDs
- **Action:** Implement separation detection (explicit breaks in thought, semantic shifts)

### 16.5 Improperly Grouped Propositions (Issue #7)
- **Status:** RESOLVED — Section 6 defines separation criteria
- **Answer:** If original unit contains two independent ideas, create separate KnowledgeItems
- **Action:** Document in ledger as "SEPARATED — independent propositions detected"

### 16.6 Cross-Source Deduplication (future design question)
- **Open:** How should cross-source deduplication work (when multiple videos mention same fact)?
- **Current:** Deferred — preserve source boundaries in 5.5, handle in later design
- **Action:** Document for 5.5.1 or 5.6

### 16.7 Multi-Backend Support (future design question)
- **Open:** Should normalization anticipate future backends (Live, Bitwig, etc.)?
- **Current:** No — remain backend-independent and universal
- **Action:** Design binding layer (future phase) to handle backend-specific mappings separately

---

## IMPLEMENTATION GATE

**5.5 DESIGN COMPLETE**

Do not proceed to 5.5 implementation until:
- [ ] This proposal is reviewed
- [ ] All 16 sections are approved
- [ ] Unresolved questions (section 16) are either answered or confirmed deferred
- [ ] STEP_5_5_PROPOSAL.md is committed to git

**Next action:** Return to design review.
