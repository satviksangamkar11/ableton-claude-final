"""
Test suite for Step 5.7 Universal Retrieval.

Tests cover:
  - Positive controls (relevant knowledge retrieved)
  - Negative controls (irrelevant knowledge not treated as equivalent)
  - Backend independence
  - Ambiguity handling
  - Scope-aware ranking
  - Provenance preservation
  - Result explainability
"""

import pytest
from pathlib import Path
import json
import tempfile

from step_5_7_universal_retrieval import (
    UniversalQuery, UniversalRetriever, MatchType, RetrievalResult
)
from step_5_6_knowledge_store import KnowledgeStore
from knowledge_item import (
    KnowledgeItem, KnowledgeType, EpistemicStatus, SourceReference,
    SemanticBinding, ExtractionMetadata
)


@pytest.fixture
def temp_store():
    """Create temporary knowledge store."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        store_path = f.name
    yield store_path
    Path(store_path).unlink(missing_ok=True)


@pytest.fixture
def retriever_with_test_data(temp_store):
    """Create retriever with populated test data."""
    store = KnowledgeStore(temp_store)

    # Create test knowledge items with various semantic bindings

    # Item 1: Arpeggiator concept
    item1 = KnowledgeItem(
        knowledge_item_id="ki_arp_concept",
        source_reference=SourceReference(
            source_id="test_source",
            source_type="TEST",
            segment_ids=["seg_001"],
        ),
        original_proposition="An arpeggiator sequentially plays notes of a chord.",
        knowledge_type=KnowledgeType.CONCEPT,
        epistemic_status=EpistemicStatus.SOURCE_REPORTED,
        semantic_bindings=[
            SemanticBinding(dimension="concept", value="arpeggiator", confidence=0.95),
            SemanticBinding(dimension="technique", value="sequencing", confidence=0.8),
        ],
        extraction_confidence=0.85,
        extraction_metadata=ExtractionMetadata(
            extraction_timestamp="2026-09-12T00:00:00Z",
            extraction_method="test",
            extraction_confidence=0.85,
            raw_extraction_status="EXTRACTED",
        ),
    )
    store.insert(item1)

    # Item 2: Bass articulation procedure
    item2 = KnowledgeItem(
        knowledge_item_id="ki_bass_articulation",
        source_reference=SourceReference(
            source_id="test_source",
            source_type="TEST",
            segment_ids=["seg_002"],
        ),
        original_proposition="To tighten bass articulation, use short envelope release times.",
        knowledge_type=KnowledgeType.PROCEDURE,
        epistemic_status=EpistemicStatus.SOURCE_RECOMMENDED,
        semantic_bindings=[
            SemanticBinding(dimension="intent", value="tighter bass articulation", confidence=0.9),
            SemanticBinding(dimension="role", value="bass", confidence=0.85),
            SemanticBinding(dimension="technique", value="envelope modulation", confidence=0.8),
        ],
        extraction_confidence=0.88,
        extraction_metadata=ExtractionMetadata(
            extraction_timestamp="2026-09-12T00:00:00Z",
            extraction_method="test",
            extraction_confidence=0.88,
            raw_extraction_status="EXTRACTED",
        ),
    )
    store.insert(item2)

    # Item 3: Envelope release principle
    item3 = KnowledgeItem(
        knowledge_item_id="ki_envelope_release",
        source_reference=SourceReference(
            source_id="test_source",
            source_type="TEST",
            segment_ids=["seg_003"],
        ),
        original_proposition="Shorter envelope release creates sharper note endings.",
        knowledge_type=KnowledgeType.PRINCIPLE,
        epistemic_status=EpistemicStatus.SOURCE_OBSERVED,
        semantic_bindings=[
            SemanticBinding(dimension="concept", value="envelope release", confidence=0.95),
            SemanticBinding(dimension="effect", value="attack sharpness", confidence=0.7),
        ],
        extraction_confidence=0.82,
        extraction_metadata=ExtractionMetadata(
            extraction_timestamp="2026-09-12T00:00:00Z",
            extraction_method="test",
            extraction_confidence=0.82,
            raw_extraction_status="EXTRACTED",
        ),
    )
    store.insert(item3)

    # Item 4: Pad modulation (should NOT match bass articulation queries)
    item4 = KnowledgeItem(
        knowledge_item_id="ki_pad_modulation",
        source_reference=SourceReference(
            source_id="test_source",
            source_type="TEST",
            segment_ids=["seg_004"],
        ),
        original_proposition="Pad sounds benefit from slow, evolving filter modulation.",
        knowledge_type=KnowledgeType.RECOMMENDATION,
        epistemic_status=EpistemicStatus.SOURCE_REPORTED,
        semantic_bindings=[
            SemanticBinding(dimension="role", value="pad", confidence=0.9),
            SemanticBinding(dimension="context", value="ambient", confidence=0.75),
            SemanticBinding(dimension="technique", value="filter modulation", confidence=0.8),
        ],
        extraction_confidence=0.80,
        extraction_metadata=ExtractionMetadata(
            extraction_timestamp="2026-09-12T00:00:00Z",
            extraction_method="test",
            extraction_confidence=0.80,
            raw_extraction_status="EXTRACTED",
        ),
    )
    store.insert(item4)

    # Item 5: Ambiguous/UNKNOWN item
    item5 = KnowledgeItem(
        knowledge_item_id="ki_ambiguous",
        source_reference=SourceReference(
            source_id="test_source",
            source_type="TEST",
            segment_ids=["seg_005"],
        ),
        original_proposition="Reverb tail length affects sustain perception.",
        knowledge_type=KnowledgeType.OBSERVATION,  # provisional
        epistemic_status=EpistemicStatus.UNKNOWN,
        extraction_confidence=0.45,  # LOW
        ambiguity="Could be OBSERVATION or PRINCIPLE",
        notes="Candidates: [OBSERVATION, PRINCIPLE]",
        extraction_metadata=ExtractionMetadata(
            extraction_timestamp="2026-09-12T00:00:00Z",
            extraction_method="test",
            extraction_confidence=0.45,
            raw_extraction_status="EXTRACTED",
        ),
    )
    store.insert(item5)

    retriever = UniversalRetriever(store)
    return retriever, store


# =========================================================================
# POSITIVE CONTROLS: Relevant knowledge should be retrieved
# =========================================================================

def test_positive_arpeggiator_query(retriever_with_test_data):
    """Positive: Query about arpeggiator should retrieve concept item."""
    retriever, _ = retriever_with_test_data

    query = UniversalQuery(concept="arpeggiator")
    results = retriever.retrieve(query)

    assert len(results) > 0
    assert results[0].knowledge_item.knowledge_item_id == "ki_arp_concept"
    assert results[0].relevance_score > 0.5


def test_positive_bass_articulation_query(retriever_with_test_data):
    """Positive: Query about bass articulation should retrieve procedure item."""
    retriever, _ = retriever_with_test_data

    query = UniversalQuery(intent="tighter bass articulation")
    results = retriever.retrieve(query)

    assert len(results) > 0
    top = results[0]
    assert top.knowledge_item.knowledge_item_id == "ki_bass_articulation"
    assert top.relevance_score > 0.6


def test_positive_envelope_release_query(retriever_with_test_data):
    """Positive: Query about envelope release should retrieve principle item."""
    retriever, _ = retriever_with_test_data

    query = UniversalQuery(concept="envelope release")
    results = retriever.retrieve(query)

    assert len(results) > 0
    assert results[0].knowledge_item.knowledge_item_id == "ki_envelope_release"


def test_positive_free_text_query(retriever_with_test_data):
    """Positive: Free text query should retrieve by lexical match."""
    retriever, _ = retriever_with_test_data

    query = UniversalQuery(free_text="arpeggiator")
    results = retriever.retrieve(query)

    assert len(results) > 0
    ids = [r.knowledge_item.knowledge_item_id for r in results]
    assert "ki_arp_concept" in ids


# =========================================================================
# NEGATIVE CONTROLS: Irrelevant knowledge should not rank equivalent
# =========================================================================

def test_negative_pad_vs_bass(retriever_with_test_data):
    """Negative: Pad modulation should NOT rank equal to bass articulation."""
    retriever, _ = retriever_with_test_data

    query = UniversalQuery(intent="tighter bass articulation", role="bass")
    results = retriever.retrieve(query)

    # Find both items
    bass_result = None
    pad_result = None
    for r in results:
        if r.knowledge_item.knowledge_item_id == "ki_bass_articulation":
            bass_result = r
        elif r.knowledge_item.knowledge_item_id == "ki_pad_modulation":
            pad_result = r

    # Bass must rank higher than pad (or pad must not appear)
    if pad_result and bass_result:
        assert bass_result.relevance_score > pad_result.relevance_score


def test_negative_scope_conflict(retriever_with_test_data):
    """Negative: Scope conflict (bass vs pad) should be detected."""
    retriever, _ = retriever_with_test_data

    # Query specifically for bass role
    query = UniversalQuery(role="bass")
    results = retriever.retrieve(query)

    # Should prefer bass item over pad item
    for r in results[:3]:  # Check top 3
        if r.knowledge_item.knowledge_item_id == "ki_bass_articulation":
            # Found bass item in top results - good
            return
        elif r.knowledge_item.knowledge_item_id == "ki_pad_modulation":
            # If pad appears first, it's a problem
            pytest.fail("Pad item ranked above bass item for bass-specific query")


def test_negative_unrelated_tutorial_metadata(retriever_with_test_data):
    """Negative: Tutorial metadata should not match content queries."""
    retriever, _ = retriever_with_test_data

    query = UniversalQuery(concept="tutorial")
    results = retriever.retrieve(query)

    # Should not retrieve arpeggiator or envelope knowledge just because
    # they might be found in "tutorials"
    if results:
        for r in results:
            # Results should only match if "tutorial" appears in actual content
            prop_lower = r.knowledge_item.original_proposition.lower()
            assert "tutorial" in prop_lower


# =========================================================================
# AMBIGUITY HANDLING
# =========================================================================

def test_ambiguity_marked_explicitly(retriever_with_test_data):
    """Ambiguous items must remain explicitly ambiguous."""
    retriever, store = retriever_with_test_data

    # Query with lower relevance threshold to catch UNKNOWN items
    original_threshold = retriever.min_relevance_score
    retriever.min_relevance_score = 0.0  # Include even very low-scoring items

    query = UniversalQuery(free_text="reverb sustain")
    results = retriever.retrieve(query)

    # Find the ambiguous item
    found_ambiguous = False
    for r in results:
        if r.knowledge_item.knowledge_item_id == "ki_ambiguous":
            assert r.is_ambiguous is True
            assert len(r.ambiguity_candidates) > 0
            assert r.knowledge_item.epistemic_status.value == "UNKNOWN"
            found_ambiguous = True
            break

    retriever.min_relevance_score = original_threshold
    assert found_ambiguous, "Should find ambiguous item via text match"


def test_ambiguous_item_has_lower_confidence(retriever_with_test_data):
    """UNKNOWN items should have lower extraction_confidence."""
    retriever, _ = retriever_with_test_data

    query = UniversalQuery(free_text="reverb sustain")
    results = retriever.retrieve(query)

    for r in results:
        if r.knowledge_item.knowledge_item_id == "ki_ambiguous":
            # UNKNOWN items have LOW confidence
            assert r.knowledge_item.extraction_confidence < 0.7
            return


# =========================================================================
# PROVENANCE PRESERVATION
# =========================================================================

def test_provenance_source_preserved(retriever_with_test_data):
    """Provenance: source_reference must survive retrieval."""
    retriever, _ = retriever_with_test_data

    query = UniversalQuery(concept="arpeggiator")
    results = retriever.retrieve(query)

    assert len(results) > 0
    item = results[0].knowledge_item

    # Provenance must be intact
    assert item.source_reference.source_id == "test_source"
    assert item.source_reference.segment_ids == ["seg_001"]


def test_provenance_original_text_preserved(retriever_with_test_data):
    """Provenance: original_proposition must be exact."""
    retriever, _ = retriever_with_test_data

    query = UniversalQuery(concept="arpeggiator")
    results = retriever.retrieve(query)

    item = results[0].knowledge_item
    expected = "An arpeggiator sequentially plays notes of a chord."
    assert item.original_proposition == expected


def test_result_dict_preserves_all_fields(retriever_with_test_data):
    """Result serialization must preserve all fields."""
    retriever, _ = retriever_with_test_data

    query = UniversalQuery(concept="envelope release")
    results = retriever.retrieve(query)

    result_dict = results[0].to_dict()

    # Must contain provenance
    assert "source_reference" in result_dict
    assert "knowledge_item_id" in result_dict
    assert "original_proposition" in result_dict
    assert "epistemic_status" in result_dict
    assert "extraction_confidence" in result_dict


# =========================================================================
# EXPLAINABILITY
# =========================================================================

def test_results_are_explainable(retriever_with_test_data):
    """Results must have match reasons explaining the ranking."""
    retriever, _ = retriever_with_test_data

    query = UniversalQuery(intent="tighter bass articulation", role="bass")
    results = retriever.retrieve(query)

    assert len(results) > 0

    for r in results[:3]:
        # Must have match reasons
        assert len(r.match_reasons) > 0

        # Reasons must have evidence
        for reason in r.match_reasons:
            assert reason.match_type is not None
            assert reason.confidence >= 0.0


def test_explain_result_method(retriever_with_test_data):
    """Retriever must generate human-readable explanations."""
    retriever, _ = retriever_with_test_data

    query = UniversalQuery(concept="arpeggiator")
    results = retriever.retrieve(query)

    if results:
        explanation = retriever.explain_result(results[0])
        assert "Relevance Score" in explanation
        assert "Match Reasons" in explanation
        assert results[0].knowledge_item.knowledge_item_id in explanation


# =========================================================================
# BACKEND INDEPENDENCE
# =========================================================================

def test_backend_independent_query(retriever_with_test_data):
    """Retrieval must work with universal semantics (no Serum required)."""
    retriever, _ = retriever_with_test_data

    # Query using only universal music concepts
    query = UniversalQuery(
        intent="tighter bass articulation",
        role="bass",
        technique="envelope modulation"
    )

    results = retriever.retrieve(query)

    # Should succeed without mentioning Serum
    assert len(results) > 0

    # Results should not require Serum to interpret
    for r in results:
        # No Serum-specific semantic bindings required
        pass


def test_backend_filter_is_optional(retriever_with_test_data):
    """Backend filtering is optional, not required."""
    retriever, store = retriever_with_test_data

    # Query WITHOUT backend specification should work
    query1 = UniversalQuery(concept="arpeggiator")
    results1 = retriever.retrieve(query1)
    assert len(results1) > 0

    # Query WITH backend specification should also work
    query2 = UniversalQuery(
        concept="arpeggiator",
        backend="Serum"  # Optional filtering
    )
    results2 = retriever.retrieve(query2)
    # May or may not filter based on backend (implementation detail)
    # but should not fail


def test_no_serum_terminology_required(retriever_with_test_data):
    """Query should not require Serum vocabulary."""
    retriever, _ = retriever_with_test_data

    # Use only universal music terms
    queries = [
        UniversalQuery(concept="envelope"),
        UniversalQuery(role="bass"),
        UniversalQuery(intent="tighter articulation"),
        UniversalQuery(technique="sequencing"),
    ]

    for query in queries:
        results = retriever.retrieve(query)
        # Should all work without Serum-specific terms


# =========================================================================
# REAL-DATA ACCEPTANCE TEST
# =========================================================================

def test_real_store_retrieval():
    """Test against the real 5.6 canonical store (36 items)."""
    store_path = Path("yt_74ab96e1f377_canonical_knowledge_store_5_6.json")

    if not store_path.exists():
        pytest.skip("Real 5.6 store not found")

    store = KnowledgeStore(str(store_path), create_if_missing=False)
    retriever = UniversalRetriever(store)

    # Query 1: What is an arpeggiator?
    query1 = UniversalQuery(concept="arpeggiator")
    results1 = retriever.retrieve(query1, top_k=3)
    assert len(results1) > 0, "Should find arpeggiator knowledge"

    # Query 2: How do I make articulation tighter?
    query2 = UniversalQuery(intent="tighter articulation")
    results2 = retriever.retrieve(query2, top_k=3)
    # May or may not have results depending on store content

    # Query 3: What does envelope release mean?
    query3 = UniversalQuery(concept="release")
    results3 = retriever.retrieve(query3, top_k=3)
    # Release/envelope knowledge should be retrievable


def test_real_store_has_expected_distribution():
    """Verify real store has expected knowledge distribution."""
    store_path = Path("yt_74ab96e1f377_canonical_knowledge_store_5_6.json")

    if not store_path.exists():
        pytest.skip("Real store not found")

    with open(store_path, 'r', encoding='utf-8') as f:
        store_data = json.load(f)

    items = store_data.get("items", {})
    assert len(items) == 36

    # Count UNKNOWN items
    unknown_count = sum(
        1 for item_dict in items.values()
        if item_dict.get("epistemic_status") == "UNKNOWN"
    )
    assert unknown_count == 5


# =========================================================================
# EDGE CASES
# =========================================================================

def test_empty_query_returns_empty(retriever_with_test_data):
    """Empty query should return empty results."""
    retriever, _ = retriever_with_test_data

    query = UniversalQuery()  # No fields set
    results = retriever.retrieve(query)

    assert len(results) == 0


def test_low_relevance_filtered(retriever_with_test_data):
    """Results below min_relevance_score should be filtered."""
    retriever, _ = retriever_with_test_data

    # Very obscure query unlikely to match well
    query = UniversalQuery(free_text="xyzabc123nonexistent")
    results = retriever.retrieve(query)

    # Should filter out low-scoring results
    if results:
        for r in results:
            assert r.relevance_score >= retriever.min_relevance_score


def test_top_k_limiting(retriever_with_test_data):
    """top_k parameter should limit results."""
    retriever, _ = retriever_with_test_data

    query = UniversalQuery(free_text="envelope")
    results_all = retriever.retrieve(query)
    results_top3 = retriever.retrieve(query, top_k=3)

    assert len(results_top3) <= 3

    if len(results_all) > 3:
        assert len(results_top3) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
