# Step 5.2 — Canonical KnowledgeItem Schema

**Status:** COMPLETE (26/26 tests passing)

**Date:** 2026-09-12

---

## Objective

Define and implement the canonical `KnowledgeItem` representation for the Step 5 knowledge layer. This schema serves as the stable semantic and provenance contract for all subsequent Step 5 phases.

---

## Implementation Summary

### Files Created

1. **`serum2/knowledge/knowledge_item.py`** (main implementation)
   - Canonical `KnowledgeItem` dataclass
   - Supporting enums and dataclasses
   - Serialization/deserialization (dict, JSON)
   - Validation logic
   - Stable ID generation

2. **`serum2/knowledge/test_knowledge_item.py`** (core tests)
   - 20 comprehensive unit tests
   - Coverage: construction, validation, serialization, identity, authority boundary

3. **`serum2/knowledge/test_schema_real_data_conversion.py`** (real data proof)
   - 3 test functions + 3 pytest test methods
   - Tests conversion of real YouTube extraction data
   - Verifies no information loss
   - Demonstrates semantic binding support

---

## Schema Definition

### Core Classes

```python
class KnowledgeType(Enum):
    """Types of knowledge a source can provide."""
    CONCEPT, PROCEDURE, PRINCIPLE, OBSERVATION,
    RECOMMENDATION, CONDITION, EXAMPLE, CONTEXT, LIMITATION

class EpistemicStatus(Enum):
    """Epistemic status of a knowledge item."""
    SOURCE_REPORTED, SOURCE_RECOMMENDED, SOURCE_OBSERVED,
    SYSTEM_INTERPRETATION, EXPERIMENTALLY_VERIFIED, UNKNOWN

@dataclass
class SemanticBinding:
    """A semantic dimension binding (e.g., target, role, technique, intent)."""
    dimension: str
    value: str
    confidence: float  # 0.0-1.0
    ambiguity: Optional[str]  # Preserve unresolved ambiguity

@dataclass
class SourceReference:
    """Reference to source material (immutable)."""
    source_id: str
    source_type: str  # YOUTUBE_VIDEO, MANUAL, USER_EXPLANATION
    source_url: Optional[str]
    source_title: Optional[str]
    segment_ids: List[str]
    start_time_sec: Optional[float]
    end_time_sec: Optional[float]

@dataclass
class ExtractionMetadata:
    """Metadata about extraction."""
    extraction_timestamp: str  # ISO 8601
    extraction_method: str
    extraction_confidence: float  # 0.0-1.0
    raw_extraction_status: str  # EXTRACTED, SOURCE_ONLY, HYPOTHESIZED, IMPORTED
    original_segments_count: Optional[int]

@dataclass
class KnowledgeItem:
    """Canonical representation of a knowledge item."""
    # Identity
    knowledge_item_id: str

    # Source (immutable)
    source_reference: SourceReference
    original_proposition: str  # NEVER MODIFIED

    # Semantics
    knowledge_type: KnowledgeType
    epistemic_status: EpistemicStatus
    normalized_proposition: Optional[str]
    semantic_bindings: List[SemanticBinding]

    # Uncertainty
    extraction_confidence: float  # 0.0-1.0
    ambiguity: Optional[str]

    # Constraints
    conditions: List[str]
    limitations: List[str]

    # Metadata
    extraction_metadata: Optional[ExtractionMetadata]
    notes: Optional[str]
```

---

## Field Semantics

### Identity
- **`knowledge_item_id`**: Deterministic stable ID
  - Can be computed as hash of (source_id, segment_ids, proposition_hash)
  - Remains stable across serialization
  - Format: `ki_<16-char-hex>`

### Source (Immutable)
- **`source_reference`**: Complete provenance
  - source_id, source_type, source_url, source_title
  - segment_ids (specific source segments)
  - start_time_sec / end_time_sec (for video/audio)

- **`original_proposition`**: Original source text
  - Preserved exactly as acquired
  - NEVER modified by normalization
  - Required to reconstruct source context

### Semantics
- **`knowledge_type`**: CONCEPT | PROCEDURE | PRINCIPLE | OBSERVATION | RECOMMENDATION | CONDITION | EXAMPLE | CONTEXT | LIMITATION
  - Distinguishes different kinds of knowledge
  - Inferred from extraction method or explicitly provided

- **`epistemic_status`**: Clarity about source claim
  - SOURCE_REPORTED: source explicitly stated this
  - SOURCE_RECOMMENDED: source recommends this
  - SOURCE_OBSERVED: source claims observation
  - SYSTEM_INTERPRETATION: system derived from source
  - EXPERIMENTALLY_VERIFIED: evidence qualifies capability
  - UNKNOWN: unclear or ambiguous

- **`normalized_proposition`**: System-derived interpretation
  - Distinct from original text
  - Can be None (if original is clear enough)
  - May evolve as understanding improves

- **`semantic_bindings`**: Independent dimensions
  - Each binding is (dimension, value, confidence, ambiguity?)
  - Examples:
    - dimension="target", value="Env1.Release"
    - dimension="role", value="bass"
    - dimension="technique", value="envelope shaping"
    - dimension="intent", value="longer sustain"
    - dimension="context", value="pluck"
    - dimension="genre", value="house"

### Uncertainty
- **`extraction_confidence`**: Quality of extraction
  - 0.0-1.0
  - Separate from epistemic_status
  - High confidence ≠ experimental verification

- **`ambiguity`**: Unresolved ambiguity preserved
  - None if clear
  - Describes alternatives if ambiguous
  - Example: "Could refer to Env1.Release or Env1.Decay"

### Constraints
- **`conditions`**: When this knowledge applies
  - List of condition strings
  - Example: ["bass instruments", "upbeat genre"]

- **`limitations`**: Scope restrictions
  - Explicit qualifiers on scope
  - Example: ["very long release may cause mud", "genre-dependent"]

### Metadata
- **`extraction_metadata`**: How extracted
  - timestamp, method, confidence, status, segment_count

- **`notes`**: System notes (not source material)
  - Additional context or flags

---

## Validation Rules

All KnowledgeItems must pass validation:

1. ✓ `knowledge_item_id` present and non-empty
2. ✓ `source_reference.source_id` present
3. ✓ `source_reference.source_type` present
4. ✓ `original_proposition` present and non-empty
5. ✓ `knowledge_type` is valid enum value
6. ✓ `epistemic_status` is valid enum value
7. ✓ `extraction_confidence` in bounds [0.0, 1.0]
8. ✓ Each semantic binding has dimension and value
9. ✓ Each semantic binding confidence in bounds [0.0, 1.0]
10. ✓ NO authority fields (admission_status, capability_status, etc.)

Validation errors are explicit and logged.

---

## Serialization

### to_dict() → from_dict()
- All fields preserved exactly
- Enums converted to string values
- Round-trip successful

### to_json() → from_json()
- JSON representation with UTF-8 encoding
- Pretty-printed for readability
- Suitable for file storage

---

## Authority Boundary

### What KnowledgeItem IS
- Source-derived observation
- Advisory input
- Learning material
- Production proposal substrate

### What KnowledgeItem IS NOT
- CapabilityContract (contract authority)
- EvidenceRecord (experimental evidence)
- Causal proof (requires evidence)
- Execution permission (requires admission)
- Production authority (requires admission + contract)

### Enforcement
- Validation explicitly rejects authority fields
- If fields injected, validation fails
- Clear separation from Step 4 authority chain

---

## Test Results

### Unit Tests (20 tests)
- ✓ Construction (3 tests)
- ✓ Validation (6 tests: pass, missing fields, bounds, authority injection)
- ✓ Serialization (3 tests: dict, round-trip, JSON)
- ✓ Stable ID (3 tests: deterministic, collision, proposition hash)
- ✓ Real data samples (3 tests: procedure, recommendation, ambiguous)
- ✓ Authority boundary (2 tests: no authority, injection detected)

### Real Data Conversion (3 tests)
- ✓ YouTube extraction conversion (317 items, 5 samples)
  - Validated: 5/5 items pass schema validation
  - Round-trip serialization: successful
  - Original text preserved exactly

- ✓ Hypotheses with semantic bindings (71 items, 3 samples)
  - Converted with target/context/operation bindings
  - All validated successfully

- ✓ Information loss test
  - knowledge_item_id preserved
  - Original proposition preserved (652 chars example)
  - Segment IDs preserved (19 segments example)
  - Extraction confidence preserved (0.7 example)

**TOTAL: 26/26 tests PASS**

---

## Acceptance Criteria

✓ **A. Canonical KnowledgeItem schema exists**
   - `serum2/knowledge/knowledge_item.py` with full definition

✓ **B. All required semantic/provenance fields explicit**
   - identity, source, original_text, normalized, type, bindings, confidence, ambiguity, conditions, limitations, metadata

✓ **C. Original source wording preserved**
   - `original_proposition` field immutable
   - Proven with real data: 652-char text preserved exactly

✓ **D. Ambiguity can be represented without fabrication**
   - `ambiguity` field supports unresolved alternatives
   - Real example tested: "Make it longer" with alternatives

✓ **E. Epistemic status separate from extraction confidence**
   - `epistemic_status` enum distinct
   - `extraction_confidence` float separate
   - Both validated independently

✓ **F. Stable identity exists**
   - Deterministic ID derivation: hash(source_id, segment_ids, proposition_hash)
   - Tested: same input → same ID, different input → different ID

✓ **G. Serialization round-trip passes**
   - to_dict() → from_dict() → identical KnowledgeItem
   - to_json() → from_json() → identical KnowledgeItem
   - Tested with real data

✓ **H. Validation tests pass**
   - 26/26 tests pass
   - All validation paths covered
   - Authority injection detected

✓ **I. Representative real extracted items representable**
   - 5 PROCEDURE items from YouTube extraction
   - 3 items with semantic bindings from hypotheses
   - 1 ambiguous item with unresolved targets
   - All validate successfully

✓ **J. KnowledgeItem cannot be mistaken for authority**
   - No admission_status, capability_status, authorized_mutation, execution_permission fields
   - Validation explicitly rejects if injected
   - Clear semantic boundary enforced

---

## Known Limitations & Future Work

### Current Scope (Intentional)
- Scalar semantic bindings (not graph-like relationships yet)
- No automatic target resolution (ambiguity preserved)
- No cross-item linking (that's Step 5.6+)
- No enforcement of INTENT_SEMANTIC_MAP mapping

### Schema Stability
- Schema is frozen for Steps 5.3-5.12
- Additive changes only (no breaking changes to existing fields)
- Serialization format stable for round-trip

### Not Implemented Yet
- Persistent storage layer (Step 5.6)
- Retrieval interface (Step 5.7)
- Teaching runtime (Step 5.8)
- Production advisory bridge (Step 5.10)

---

## Files Modified

None (all new files).

---

## Verdict

### 5.2 IMPLEMENTATION RESULT

**✓ PASS**

All acceptance criteria met:
- Schema complete and tested
- Provenance preserved
- Authority boundary enforced
- Real data conversion proven
- 26/26 tests pass
- No blockers identified

Canonical KnowledgeItem schema is ready for:
- Step 5.3 (real source acquisition)
- Step 5.4 (proposition extraction)
- Step 5.5 (knowledge normalization)
- Step 5.6 (persistence)
- Steps 5.7+ (retrieval, teaching, production bridge)

**Ready to proceed to Step 5.3.**
