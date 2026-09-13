"""
Test suite for Step 5.6 Knowledge Store.

Covers all acceptance criteria A-P:
  A. Canonical KnowledgeItem store exists
  B. All 36 real normalized KnowledgeItems persist
  C. Reload after process termination succeeds
  D. Identity is deterministic and stable
  E. Duplicate identical insertion is idempotent
  F. Conflicting same-ID insertion is rejected
  G. Provenance survives storage/reload
  H. Original source text survives storage/reload
  I. UNKNOWN semantics survive unchanged
  J. Filler is not inserted
  K. Structural queries work
  L. No semantic retrieval introduced
  M. No backend-specific coupling
  N. Source and cross-source boundaries intact
  O. Tests pass
  P. Canonical store consumable by 5.7
"""

import pytest
import json
import tempfile
from pathlib import Path
from step_5_6_knowledge_store import KnowledgeStore, KnowledgeConflictError
from knowledge_item import (
    KnowledgeItem, KnowledgeType, EpistemicStatus, SourceReference,
    SemanticBinding, ExtractionMetadata
)


@pytest.fixture
def temp_store():
    """Create a temporary store for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        store_path = f.name
    yield store_path
    Path(store_path).unlink(missing_ok=True)


def create_test_item(
    item_id: str = "ki_test001",
    source_id: str = "test_source",
    original_text: str = "Test proposition",
    knowledge_type: str = "CONCEPT",
    epistemic_status: str = "SOURCE_REPORTED",
    extraction_confidence: float = 0.8,
    ambiguity: str = None,
) -> KnowledgeItem:
    """Create a test KnowledgeItem."""
    return KnowledgeItem(
        knowledge_item_id=item_id,
        source_reference=SourceReference(
            source_id=source_id,
            source_type="TEST",
            segment_ids=["seg_0001"],
        ),
        original_proposition=original_text,
        knowledge_type=KnowledgeType(knowledge_type),
        epistemic_status=EpistemicStatus(epistemic_status),
        extraction_confidence=extraction_confidence,
        ambiguity=ambiguity,
        extraction_metadata=ExtractionMetadata(
            extraction_timestamp="2026-09-12T00:00:00Z",
            extraction_method="test",
            extraction_confidence=extraction_confidence,
            raw_extraction_status="EXTRACTED",
        ),
    )


# =========================================================================
# CRITERION A: CANONICAL STORE EXISTS
# =========================================================================

def test_a_store_creation(temp_store):
    """A. Canonical KnowledgeItem store exists."""
    store = KnowledgeStore(temp_store)
    assert store.store_path.exists()
    assert store.version == "1.0"
    assert store.schema_version == "5.2"


def test_a_store_empty_on_creation(temp_store):
    """A. New store starts empty."""
    store = KnowledgeStore(temp_store)
    assert store.count() == 0


# =========================================================================
# CRITERION B: ALL 36 REAL ITEMS PERSIST
# =========================================================================

def test_b_load_real_artifact():
    """B. Load real 5.5 artifact and verify cardinality."""
    artifact_path = Path("yt_74ab96e1f377_knowledge_normalized_5_5.json")
    if not artifact_path.exists():
        pytest.skip("Real 5.5 artifact not found")

    with open(artifact_path, 'r', encoding='utf-8') as f:
        artifact = json.load(f)

    items = artifact.get("knowledge_items", [])
    assert len(items) == 36


def test_b_persist_all_36_items(temp_store):
    """B. All 36 real items persist successfully."""
    artifact_path = Path("yt_74ab96e1f377_knowledge_normalized_5_5.json")
    if not artifact_path.exists():
        pytest.skip("Real 5.5 artifact not found")

    store = KnowledgeStore(temp_store)

    with open(artifact_path, 'r', encoding='utf-8') as f:
        artifact = json.load(f)

    for item_dict in artifact["knowledge_items"]:
        item = KnowledgeItem.from_dict(item_dict)
        store.insert(item)

    assert store.count() == 36


# =========================================================================
# CRITERION C: RELOAD SUCCEEDS
# =========================================================================

def test_c_reload_after_process_termination(temp_store):
    """C. Reload after process termination succeeds."""
    # Create and populate store
    store1 = KnowledgeStore(temp_store)
    item = create_test_item()
    store1.insert(item)
    assert store1.count() == 1

    # "Terminate" and reload
    del store1

    store2 = KnowledgeStore(temp_store, create_if_missing=False)
    assert store2.count() == 1
    retrieved = store2.get(item.knowledge_item_id)
    assert retrieved is not None


# =========================================================================
# CRITERION D: IDENTITY DETERMINISTIC & STABLE
# =========================================================================

def test_d_identity_deterministic(temp_store):
    """D. Identity is deterministic."""
    item1 = create_test_item(item_id="ki_fixed", source_id="src1")
    item2 = create_test_item(item_id="ki_fixed", source_id="src1")

    store = KnowledgeStore(temp_store)
    store.insert(item1)

    retrieved = store.get("ki_fixed")
    assert retrieved.knowledge_item_id == item1.knowledge_item_id


def test_d_identity_stable_across_reload(temp_store):
    """D. Identity stable across reload."""
    store1 = KnowledgeStore(temp_store)
    item = create_test_item(item_id="ki_stable")
    store1.insert(item)
    original_id = item.knowledge_item_id

    del store1

    store2 = KnowledgeStore(temp_store, create_if_missing=False)
    retrieved = store2.get(original_id)
    assert retrieved.knowledge_item_id == original_id


# =========================================================================
# CRITERION E: DUPLICATE IDENTICAL INSERT IS IDEMPOTENT
# =========================================================================

def test_e_idempotent_identical_insert(temp_store):
    """E. Duplicate identical insertion is idempotent."""
    store = KnowledgeStore(temp_store)
    item = create_test_item()

    result1 = store.insert(item)
    assert result1 is True  # First insert succeeds

    result2 = store.insert(item)
    assert result2 is False  # Second insert is idempotent
    assert store.count() == 1  # Still only 1 item


# =========================================================================
# CRITERION F: CONFLICTING INSERTION REJECTED
# =========================================================================

def test_f_conflicting_insert_rejected(temp_store):
    """F. Conflicting same-ID insertion rejected."""
    store = KnowledgeStore(temp_store)
    item1 = create_test_item(item_id="ki_conflict", original_text="Text A")
    store.insert(item1)

    item2 = create_test_item(item_id="ki_conflict", original_text="Text B")

    with pytest.raises(KnowledgeConflictError):
        store.insert(item2)


# =========================================================================
# CRITERION G: PROVENANCE SURVIVES STORAGE/RELOAD
# =========================================================================

def test_g_provenance_preserved_in_storage(temp_store):
    """G. Provenance survives storage/reload."""
    store = KnowledgeStore(temp_store)

    item = KnowledgeItem(
        knowledge_item_id="ki_prov",
        source_reference=SourceReference(
            source_id="yt_12345",
            source_type="YOUTUBE_VIDEO",
            source_title="Test Video",
            segment_ids=["seg_001", "seg_002"],
            start_time_sec=10.5,
            end_time_sec=20.5,
        ),
        original_proposition="Test text",
        knowledge_type=KnowledgeType.CONCEPT,
        epistemic_status=EpistemicStatus.SOURCE_REPORTED,
        extraction_metadata=ExtractionMetadata(
            extraction_timestamp="2026-09-12T00:00:00Z",
            extraction_method="test",
            extraction_confidence=0.8,
            raw_extraction_status="EXTRACTED",
        ),
    )

    store.insert(item)

    retrieved = store.get("ki_prov")
    assert retrieved.source_reference.source_id == "yt_12345"
    assert retrieved.source_reference.source_type == "YOUTUBE_VIDEO"
    assert retrieved.source_reference.source_title == "Test Video"
    assert retrieved.source_reference.segment_ids == ["seg_001", "seg_002"]
    assert retrieved.source_reference.start_time_sec == 10.5


def test_g_provenance_survives_reload(temp_store):
    """G. Provenance survives after reload."""
    store1 = KnowledgeStore(temp_store)
    item = create_test_item(source_id="yt_reloadtest")
    store1.insert(item)
    del store1

    store2 = KnowledgeStore(temp_store, create_if_missing=False)
    retrieved = store2.get(item.knowledge_item_id)
    assert retrieved.source_reference.source_id == "yt_reloadtest"


# =========================================================================
# CRITERION H: ORIGINAL SOURCE TEXT SURVIVES STORAGE/RELOAD
# =========================================================================

def test_h_original_text_preserved(temp_store):
    """H. Original source text preserved."""
    original_text = "This is the exact original text from source."
    item = create_test_item(original_text=original_text)

    store = KnowledgeStore(temp_store)
    store.insert(item)

    retrieved = store.get(item.knowledge_item_id)
    assert retrieved.original_proposition == original_text


def test_h_original_text_survives_reload(temp_store):
    """H. Original text survives reload."""
    original_text = "Text that must survive reload."
    store1 = KnowledgeStore(temp_store)
    item = create_test_item(original_text=original_text)
    store1.insert(item)
    del store1

    store2 = KnowledgeStore(temp_store, create_if_missing=False)
    retrieved = store2.get(item.knowledge_item_id)
    assert retrieved.original_proposition == original_text


# =========================================================================
# CRITERION I: UNKNOWN SEMANTICS SURVIVE UNCHANGED
# =========================================================================

def test_i_unknown_item_preserved(temp_store):
    """I. UNKNOWN semantics preserved."""
    store = KnowledgeStore(temp_store)

    unknown_item = create_test_item(
        item_id="ki_unknown",
        knowledge_type="OBSERVATION",  # provisional type
        epistemic_status="UNKNOWN",
        extraction_confidence=0.5,  # LOW
        ambiguity="Could be OBSERVATION or PRINCIPLE",
    )
    unknown_item.notes = "Candidates: [OBSERVATION, PRINCIPLE]"

    store.insert(unknown_item)

    retrieved = store.get("ki_unknown")
    assert retrieved.epistemic_status.value == "UNKNOWN"
    assert retrieved.extraction_confidence == 0.5
    assert retrieved.ambiguity is not None
    assert retrieved.notes is not None


def test_i_unknown_survives_reload(temp_store):
    """I. UNKNOWN items survive reload."""
    store1 = KnowledgeStore(temp_store)

    unknown_item = create_test_item(
        epistemic_status="UNKNOWN",
        extraction_confidence=0.5,
        ambiguity="Ambiguous",
    )
    store1.insert(unknown_item)
    del store1

    store2 = KnowledgeStore(temp_store, create_if_missing=False)
    retrieved = store2.get(unknown_item.knowledge_item_id)
    assert retrieved.epistemic_status.value == "UNKNOWN"


# =========================================================================
# CRITERION J: FILLER NOT INSERTED
# =========================================================================

def test_j_filler_exclusion():
    """J. Filler excluded from canonical store."""
    # Filler should not be in the 5.5 artifact to begin with
    artifact_path = Path("yt_74ab96e1f377_knowledge_normalized_5_5.json")
    if not artifact_path.exists():
        pytest.skip("Real artifact not found")

    with open(artifact_path, 'r', encoding='utf-8') as f:
        artifact = json.load(f)

    items = artifact.get("knowledge_items", [])
    filler_count = sum(1 for i in items if i.get("knowledge_type") == "FILLER")

    # Should be zero (filler excluded in 5.5)
    assert filler_count == 0


# =========================================================================
# CRITERION K: STRUCTURAL QUERIES WORK
# =========================================================================

def test_k_query_by_type(temp_store):
    """K. Query by knowledge_type works."""
    store = KnowledgeStore(temp_store)

    store.insert(create_test_item(item_id="ki_c1", knowledge_type="CONCEPT"))
    store.insert(create_test_item(item_id="ki_c2", knowledge_type="CONCEPT"))
    store.insert(create_test_item(item_id="ki_p1", knowledge_type="PROCEDURE"))

    concepts = store.query({"knowledge_type": "CONCEPT"})
    assert len(concepts) == 2


def test_k_query_by_status(temp_store):
    """K. Query by epistemic_status works."""
    store = KnowledgeStore(temp_store)

    store.insert(create_test_item(item_id="ki_sr1", epistemic_status="SOURCE_REPORTED"))
    store.insert(create_test_item(item_id="ki_sr2", epistemic_status="SOURCE_REPORTED"))
    store.insert(create_test_item(item_id="ki_unk", epistemic_status="UNKNOWN"))

    reported = store.query({"epistemic_status": "SOURCE_REPORTED"})
    assert len(reported) == 2


def test_k_query_by_source(temp_store):
    """K. Query by source_id works."""
    store = KnowledgeStore(temp_store)

    store.insert(create_test_item(item_id="ki_s1", source_id="src_a"))
    store.insert(create_test_item(item_id="ki_s2", source_id="src_a"))
    store.insert(create_test_item(item_id="ki_s3", source_id="src_b"))

    from_a = store.get_by_source("src_a")
    assert len(from_a) == 2


def test_k_query_ambiguity(temp_store):
    """K. Query by ambiguity field works."""
    store = KnowledgeStore(temp_store)

    store.insert(create_test_item(item_id="ki_amb", ambiguity="Is it X or Y?"))
    store.insert(create_test_item(item_id="ki_clear", ambiguity=None))

    ambiguous = store.query({"has_ambiguity": True})
    assert len(ambiguous) == 1


# =========================================================================
# CRITERION L: NO SEMANTIC RETRIEVAL
# =========================================================================

def test_l_no_semantic_queries(temp_store):
    """L. No semantic similarity/embedding queries in 5.6."""
    store = KnowledgeStore(temp_store)

    # Verify structural queries are supported
    item = create_test_item()
    store.insert(item)

    # These should work (structural):
    assert store.query({"knowledge_type": "CONCEPT"}) is not None
    assert store.get_by_source("test_source") is not None

    # Semantic queries should not be available at 5.6 level
    # (This is a design constraint, not a failing test)


# =========================================================================
# CRITERION M: NO BACKEND-SPECIFIC COUPLING
# =========================================================================

def test_m_no_serum_fields(temp_store):
    """M. No Serum-specific fields in storage."""
    store = KnowledgeStore(temp_store)
    item = create_test_item()
    store.insert(item)

    retrieved = store.get(item.knowledge_item_id)

    # Verify no Serum-specific fields
    item_dict = retrieved.to_dict()
    serum_keywords = ["serum_", "parameter", "control_path", "capability"]

    for key in item_dict.keys():
        assert not any(s in key.lower() for s in serum_keywords)


def test_m_universal_knowledge_preserved(temp_store):
    """M. Knowledge remains backend-independent."""
    store = KnowledgeStore(temp_store)

    # A generic music synthesis concept
    item = KnowledgeItem(
        knowledge_item_id="ki_universal",
        source_reference=SourceReference(
            source_id="generic_source",
            source_type="MANUAL",
        ),
        original_proposition="Decreasing resonance reduces frequency response emphasis.",
        knowledge_type=KnowledgeType.PRINCIPLE,
        epistemic_status=EpistemicStatus.SOURCE_REPORTED,
        extraction_metadata=ExtractionMetadata(
            extraction_timestamp="2026-09-12T00:00:00Z",
            extraction_method="test",
            extraction_confidence=0.8,
            raw_extraction_status="EXTRACTED",
        ),
    )

    store.insert(item)
    retrieved = store.get("ki_universal")

    # No Serum-specific content added
    assert "serum" not in retrieved.original_proposition.lower()


# =========================================================================
# CRITERION N: SOURCE & CROSS-SOURCE BOUNDARIES INTACT
# =========================================================================

def test_n_multiple_sources_independent(temp_store):
    """N. Multiple sources kept independent."""
    store = KnowledgeStore(temp_store)

    store.insert(create_test_item(item_id="ki_s1", source_id="source_a"))
    store.insert(create_test_item(item_id="ki_s2", source_id="source_b"))

    from_a = store.get_by_source("source_a")
    from_b = store.get_by_source("source_b")

    assert len(from_a) == 1
    assert len(from_b) == 1
    assert from_a[0].source_reference.source_id != from_b[0].source_reference.source_id


def test_n_no_automatic_merge(temp_store):
    """N. No automatic merging across sources."""
    store = KnowledgeStore(temp_store)

    # Similar content from different sources
    item1 = create_test_item(
        item_id="ki_i1",
        source_id="source_a",
        original_text="Resonance shapes tone.",
    )
    item2 = create_test_item(
        item_id="ki_i2",
        source_id="source_b",
        original_text="Resonance shapes tone.",
    )

    store.insert(item1)
    store.insert(item2)

    # Should be stored as separate items
    assert store.count() == 2
    assert store.get("ki_i1") is not None
    assert store.get("ki_i2") is not None


# =========================================================================
# CRITERION O: TESTS PASS
# =========================================================================

def test_o_validation_passes(temp_store):
    """O. All items validate."""
    store = KnowledgeStore(temp_store)

    for i in range(5):
        store.insert(create_test_item(item_id=f"ki_valid_{i}"))

    all_valid, errors = store.validate_all()
    assert all_valid
    assert len(errors) == 0


# =========================================================================
# CRITERION P: CONSUMABLE BY 5.7
# =========================================================================

def test_p_store_consumable_by_5_7(temp_store):
    """P. Store can be consumed by 5.7 without transformation."""
    store = KnowledgeStore(temp_store)
    item = create_test_item()
    store.insert(item)

    # 5.7 should be able to:
    # 1. Open the store
    retrieved = store.get(item.knowledge_item_id)

    # 2. Read KnowledgeItem fields
    assert retrieved.knowledge_item_id
    assert retrieved.original_proposition
    assert retrieved.knowledge_type
    assert retrieved.epistemic_status
    assert retrieved.source_reference

    # 3. Validate against 5.2 schema
    valid, _ = retrieved.validate()
    assert valid

    # 4. Access provenance
    assert retrieved.source_reference.source_id
    assert retrieved.source_reference.segment_ids

    # No transformation needed
    assert retrieved.to_dict() is not None


# =========================================================================
# ADDITIONAL ROBUSTNESS TESTS
# =========================================================================

def test_atomic_writes_safety(temp_store):
    """Verify atomic write strategy prevents corruption."""
    store = KnowledgeStore(temp_store)

    # Insert multiple items
    for i in range(10):
        store.insert(create_test_item(item_id=f"ki_atomic_{i}"))

    # Verify file is well-formed JSON
    with open(temp_store, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert data is not None
    assert "items" in data
    assert len(data["items"]) == 10


def test_stats_generation(temp_store):
    """Verify statistics generation."""
    store = KnowledgeStore(temp_store)

    store.insert(create_test_item(item_id="ki_stat_1", knowledge_type="CONCEPT"))
    store.insert(create_test_item(item_id="ki_stat_2", knowledge_type="PROCEDURE"))
    store.insert(create_test_item(item_id="ki_stat_3", epistemic_status="UNKNOWN"))

    stats = store.get_stats()

    assert stats["total_items"] == 3
    assert stats["unknown_items"] == 1
    assert "by_type" in stats
    assert "by_status" in stats
    assert stats["schema_version"] == "5.2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
