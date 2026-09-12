"""Tests for canonical KnowledgeItem schema."""

import pytest
from datetime import datetime, timezone
from serum2.knowledge.knowledge_item import (
    KnowledgeItem,
    KnowledgeType,
    EpistemicStatus,
    SemanticBinding,
    SourceReference,
    ExtractionMetadata,
)


class TestKnowledgeItemConstruction:
    """Test KnowledgeItem construction and validation."""

    def test_minimal_knowledge_item(self):
        """Construct minimal valid KnowledgeItem."""
        src = SourceReference(
            source_id="yt_test",
            source_type="YOUTUBE_VIDEO",
            segment_ids=["seg_0000"],
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            extraction_method="manual",
            extraction_confidence=0.9,
            raw_extraction_status="EXTRACTED",
        )
        ki = KnowledgeItem(
            knowledge_item_id="ki_test_001",
            source_reference=src,
            original_proposition="Lower the sustain to shorten the note.",
            knowledge_type=KnowledgeType.PROCEDURE,
            epistemic_status=EpistemicStatus.SOURCE_RECOMMENDED,
            extraction_metadata=ext_meta,
        )

        assert ki.knowledge_item_id == "ki_test_001"
        assert ki.original_proposition == "Lower the sustain to shorten the note."
        assert ki.knowledge_type == KnowledgeType.PROCEDURE
        assert ki.epistemic_status == EpistemicStatus.SOURCE_RECOMMENDED

    def test_knowledge_item_with_semantic_bindings(self):
        """Construct KnowledgeItem with semantic bindings."""
        src = SourceReference(
            source_id="yt_test",
            source_type="YOUTUBE_VIDEO",
            segment_ids=["seg_0100"],
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            extraction_method="semantic_extraction",
            extraction_confidence=0.85,
            raw_extraction_status="EXTRACTED",
        )
        ki = KnowledgeItem(
            knowledge_item_id="ki_test_002",
            source_reference=src,
            original_proposition="For this style, a slightly longer release can make the bass feel smoother.",
            knowledge_type=KnowledgeType.RECOMMENDATION,
            epistemic_status=EpistemicStatus.SOURCE_OBSERVED,
            semantic_bindings=[
                SemanticBinding(
                    dimension="target",
                    value="Env1.Release",
                    confidence=0.9,
                ),
                SemanticBinding(
                    dimension="role",
                    value="bass",
                    confidence=0.95,
                ),
                SemanticBinding(
                    dimension="intent",
                    value="smoother tail",
                    confidence=0.8,
                ),
                SemanticBinding(
                    dimension="context",
                    value="bass_pluck",
                    confidence=0.7,
                ),
            ],
            conditions=["bass instruments"],
            limitations=["may cause mud if release too long"],
            extraction_metadata=ext_meta,
        )

        assert len(ki.semantic_bindings) == 4
        assert ki.semantic_bindings[0].dimension == "target"
        assert ki.semantic_bindings[0].value == "Env1.Release"
        assert len(ki.conditions) == 1
        assert len(ki.limitations) == 1

    def test_knowledge_item_with_ambiguity(self):
        """Construct KnowledgeItem with explicit ambiguity."""
        src = SourceReference(
            source_id="yt_test",
            source_type="YOUTUBE_VIDEO",
            segment_ids=["seg_0050"],
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            extraction_method="semantic_extraction",
            extraction_confidence=0.5,
            raw_extraction_status="EXTRACTED",
        )
        ki = KnowledgeItem(
            knowledge_item_id="ki_test_003",
            source_reference=src,
            original_proposition="Make it longer",
            knowledge_type=KnowledgeType.PROCEDURE,
            epistemic_status=EpistemicStatus.SOURCE_REPORTED,
            ambiguity="Could refer to: Env1.Release (longer tail), Env1.Decay (longer decay), or note duration (longer in DAW)",
            extraction_metadata=ext_meta,
        )

        assert ki.ambiguity is not None
        assert "Env1.Release" in ki.ambiguity

    def test_validation_pass(self):
        """Validation passes for valid KnowledgeItem."""
        src = SourceReference(
            source_id="yt_test",
            source_type="YOUTUBE_VIDEO",
            segment_ids=["seg_0000"],
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            extraction_method="manual",
            extraction_confidence=0.9,
            raw_extraction_status="EXTRACTED",
        )
        ki = KnowledgeItem(
            knowledge_item_id="ki_test_valid",
            source_reference=src,
            original_proposition="Test proposition",
            knowledge_type=KnowledgeType.CONCEPT,
            epistemic_status=EpistemicStatus.SOURCE_REPORTED,
            extraction_metadata=ext_meta,
        )

        is_valid, errors = ki.validate()
        assert is_valid, f"Validation failed: {errors}"
        assert len(errors) == 0

    def test_validation_missing_id(self):
        """Validation fails when knowledge_item_id missing."""
        src = SourceReference(
            source_id="yt_test",
            source_type="YOUTUBE_VIDEO",
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            extraction_method="manual",
            extraction_confidence=0.9,
            raw_extraction_status="EXTRACTED",
        )
        ki = KnowledgeItem(
            knowledge_item_id="",
            source_reference=src,
            original_proposition="Test",
            knowledge_type=KnowledgeType.CONCEPT,
            epistemic_status=EpistemicStatus.SOURCE_REPORTED,
            extraction_metadata=ext_meta,
        )

        is_valid, errors = ki.validate()
        assert not is_valid
        assert any("knowledge_item_id" in e for e in errors)

    def test_validation_missing_source(self):
        """Validation fails when source missing."""
        src = SourceReference(
            source_id="",
            source_type="",
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            extraction_method="manual",
            extraction_confidence=0.9,
            raw_extraction_status="EXTRACTED",
        )
        ki = KnowledgeItem(
            knowledge_item_id="ki_test",
            source_reference=src,
            original_proposition="Test",
            knowledge_type=KnowledgeType.CONCEPT,
            epistemic_status=EpistemicStatus.SOURCE_REPORTED,
            extraction_metadata=ext_meta,
        )

        is_valid, errors = ki.validate()
        assert not is_valid
        assert any("source_id" in e or "source_type" in e for e in errors)

    def test_validation_empty_proposition(self):
        """Validation fails when original_proposition empty."""
        src = SourceReference(
            source_id="yt_test",
            source_type="YOUTUBE_VIDEO",
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            extraction_method="manual",
            extraction_confidence=0.9,
            raw_extraction_status="EXTRACTED",
        )
        ki = KnowledgeItem(
            knowledge_item_id="ki_test",
            source_reference=src,
            original_proposition="",
            knowledge_type=KnowledgeType.CONCEPT,
            epistemic_status=EpistemicStatus.SOURCE_REPORTED,
            extraction_metadata=ext_meta,
        )

        is_valid, errors = ki.validate()
        assert not is_valid
        assert any("proposition" in e for e in errors)

    def test_validation_invalid_confidence(self):
        """Validation fails when confidence out of bounds."""
        src = SourceReference(
            source_id="yt_test",
            source_type="YOUTUBE_VIDEO",
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            extraction_method="manual",
            extraction_confidence=1.5,  # Invalid
            raw_extraction_status="EXTRACTED",
        )
        ki = KnowledgeItem(
            knowledge_item_id="ki_test",
            source_reference=src,
            original_proposition="Test",
            knowledge_type=KnowledgeType.CONCEPT,
            epistemic_status=EpistemicStatus.SOURCE_REPORTED,
            extraction_confidence=1.5,  # Invalid
            extraction_metadata=ext_meta,
        )

        is_valid, errors = ki.validate()
        assert not is_valid
        assert any("confidence" in e for e in errors)

    def test_validation_authority_field_rejected(self):
        """Validation rejects if authority fields present."""
        src = SourceReference(
            source_id="yt_test",
            source_type="YOUTUBE_VIDEO",
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            extraction_method="manual",
            extraction_confidence=0.9,
            raw_extraction_status="EXTRACTED",
        )
        ki = KnowledgeItem(
            knowledge_item_id="ki_test",
            source_reference=src,
            original_proposition="Test",
            knowledge_type=KnowledgeType.CONCEPT,
            epistemic_status=EpistemicStatus.SOURCE_REPORTED,
            extraction_metadata=ext_meta,
        )
        # Inject authority field
        ki.admission_status = "ADMITTED"

        is_valid, errors = ki.validate()
        assert not is_valid
        assert any("authority" in e for e in errors)


class TestKnowledgeItemSerialization:
    """Test serialization/deserialization."""

    def test_to_dict_preserves_all_fields(self):
        """to_dict() preserves all fields."""
        src = SourceReference(
            source_id="yt_f507169bd7cb",
            source_type="YOUTUBE_VIDEO",
            source_url="https://www.youtube.com/watch?v=test",
            source_title="Serum 2 Guide",
            segment_ids=["seg_0000", "seg_0001"],
            start_time_sec=0.16,
            end_time_sec=53.76,
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp="2026-09-11T12:34:56Z",
            extraction_method="semantic_extraction_v1",
            extraction_confidence=0.85,
            raw_extraction_status="EXTRACTED",
            original_segments_count=2,
        )
        ki = KnowledgeItem(
            knowledge_item_id="ki_abc123",
            source_reference=src,
            original_proposition="Original text from source",
            knowledge_type=KnowledgeType.PROCEDURE,
            epistemic_status=EpistemicStatus.SOURCE_RECOMMENDED,
            normalized_proposition="Normalized interpretation",
            semantic_bindings=[
                SemanticBinding(
                    dimension="target",
                    value="Env1.Release",
                    confidence=0.9,
                )
            ],
            extraction_confidence=0.85,
            ambiguity=None,
            conditions=["bass"],
            limitations=["long release may cause mud"],
            extraction_metadata=ext_meta,
            notes="Test note",
        )

        d = ki.to_dict()
        assert d["knowledge_item_id"] == "ki_abc123"
        assert d["original_proposition"] == "Original text from source"
        assert d["normalized_proposition"] == "Normalized interpretation"
        assert d["knowledge_type"] == "PROCEDURE"
        assert d["epistemic_status"] == "SOURCE_RECOMMENDED"
        assert len(d["semantic_bindings"]) == 1
        assert d["semantic_bindings"][0]["value"] == "Env1.Release"
        assert d["conditions"] == ["bass"]
        assert d["limitations"] == ["long release may cause mud"]

    def test_round_trip_serialization(self):
        """to_dict() → from_dict() preserves all data."""
        src = SourceReference(
            source_id="yt_test",
            source_type="YOUTUBE_VIDEO",
            source_url="https://example.com/video",
            source_title="Test Video",
            segment_ids=["seg_100", "seg_101"],
            start_time_sec=100.0,
            end_time_sec=200.0,
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp="2026-09-11T12:34:56Z",
            extraction_method="test_method",
            extraction_confidence=0.75,
            raw_extraction_status="EXTRACTED",
            original_segments_count=2,
        )
        original = KnowledgeItem(
            knowledge_item_id="ki_original",
            source_reference=src,
            original_proposition="Original source text",
            knowledge_type=KnowledgeType.RECOMMENDATION,
            epistemic_status=EpistemicStatus.SOURCE_OBSERVED,
            normalized_proposition="System interpretation",
            semantic_bindings=[
                SemanticBinding("target", "Env1.Attack", 0.95),
                SemanticBinding("intent", "faster attack", 0.85),
            ],
            extraction_confidence=0.75,
            ambiguity="Could also mean decay",
            conditions=["fast drums"],
            limitations=["may click"],
            extraction_metadata=ext_meta,
            notes="Test notes",
        )

        # Serialize and deserialize
        d = original.to_dict()
        restored = KnowledgeItem.from_dict(d)

        assert restored.knowledge_item_id == original.knowledge_item_id
        assert restored.original_proposition == original.original_proposition
        assert restored.normalized_proposition == original.normalized_proposition
        assert restored.knowledge_type == original.knowledge_type
        assert restored.epistemic_status == original.epistemic_status
        assert len(restored.semantic_bindings) == 2
        assert restored.semantic_bindings[0].value == "Env1.Attack"
        assert restored.extraction_confidence == original.extraction_confidence
        assert restored.ambiguity == original.ambiguity
        assert restored.conditions == original.conditions
        assert restored.limitations == original.limitations
        assert restored.notes == original.notes

    def test_json_serialization_round_trip(self):
        """to_json() → from_json() preserves all data."""
        src = SourceReference(
            source_id="yt_json_test",
            source_type="YOUTUBE_VIDEO",
            segment_ids=["seg_json_test"],
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp="2026-09-11T12:00:00Z",
            extraction_method="json_test",
            extraction_confidence=0.8,
            raw_extraction_status="EXTRACTED",
        )
        original = KnowledgeItem(
            knowledge_item_id="ki_json_test",
            source_reference=src,
            original_proposition="Test JSON serialization",
            knowledge_type=KnowledgeType.CONCEPT,
            epistemic_status=EpistemicStatus.SOURCE_REPORTED,
            extraction_metadata=ext_meta,
        )

        json_str = original.to_json()
        restored = KnowledgeItem.from_json(json_str)

        assert restored.knowledge_item_id == original.knowledge_item_id
        assert restored.original_proposition == original.original_proposition
        assert restored.knowledge_type == original.knowledge_type


class TestStableID:
    """Test deterministic stable ID generation."""

    def test_stable_id_deterministic(self):
        """Stable ID is deterministic."""
        source_id = "yt_test"
        segments = ["seg_000", "seg_001"]
        proposition = "Test proposition"

        prop_hash = KnowledgeItem.compute_proposition_hash(proposition)
        id1 = KnowledgeItem.compute_stable_id(source_id, segments, prop_hash)
        id2 = KnowledgeItem.compute_stable_id(source_id, segments, prop_hash)

        assert id1 == id2
        assert id1.startswith("ki_")

    def test_stable_id_differs_for_different_input(self):
        """Stable ID differs for different input."""
        source_id = "yt_test"
        segments1 = ["seg_000", "seg_001"]
        segments2 = ["seg_002", "seg_003"]
        proposition = "Test"

        prop_hash = KnowledgeItem.compute_proposition_hash(proposition)
        id1 = KnowledgeItem.compute_stable_id(source_id, segments1, prop_hash)
        id2 = KnowledgeItem.compute_stable_id(source_id, segments2, prop_hash)

        assert id1 != id2

    def test_proposition_hash_deterministic(self):
        """Proposition hash is deterministic."""
        prop = "Lower the sustain to shorten the note."
        h1 = KnowledgeItem.compute_proposition_hash(prop)
        h2 = KnowledgeItem.compute_proposition_hash(prop)

        assert h1 == h2


class TestRealDataSamples:
    """Test with real data from YouTube extraction."""

    def test_real_extraction_procedure_item(self):
        """Create KnowledgeItem from real YouTube extraction (PROCEDURE)."""
        # From yt_f507169bd7cb_semantic_extraction.json, item ki_ext_000000
        src = SourceReference(
            source_id="yt_f507169bd7cb",
            source_type="YOUTUBE_VIDEO",
            source_url="https://www.youtube.com/watch?v=ItRL3FNpd-8",
            source_title="Serum 2 Complete Guide",
            segment_ids=[f"seg_{i:04d}" for i in range(19)],
            start_time_sec=0.16,
            end_time_sec=53.76,
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp="2026-09-11T12:00:00Z",
            extraction_method="semantic_extraction_v1",
            extraction_confidence=0.7,
            raw_extraction_status="EXTRACTED",
            original_segments_count=19,
        )
        ki = KnowledgeItem(
            knowledge_item_id="ki_ext_000000_canonical",
            source_reference=src,
            original_proposition=(
                "Hello everybody. I decided to read the entire serum manual so you don't have to. "
                "And today I'm going to explain you exactly how the plug-in works."
            ),
            knowledge_type=KnowledgeType.PROCEDURE,
            epistemic_status=EpistemicStatus.SOURCE_REPORTED,
            extraction_confidence=0.7,
            extraction_metadata=ext_meta,
        )

        is_valid, errors = ki.validate()
        assert is_valid, f"Validation failed: {errors}"

    def test_real_extraction_recommendation_item(self):
        """Create KnowledgeItem from source recommendation."""
        src = SourceReference(
            source_id="yt_f507169bd7cb",
            source_type="YOUTUBE_VIDEO",
            segment_ids=["seg_0200", "seg_0201"],
            start_time_sec=150.0,
            end_time_sec=160.0,
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp="2026-09-11T12:00:00Z",
            extraction_method="semantic_extraction_v1",
            extraction_confidence=0.85,
            raw_extraction_status="EXTRACTED",
            original_segments_count=2,
        )
        ki = KnowledgeItem(
            knowledge_item_id="ki_recommendation_001",
            source_reference=src,
            original_proposition="For this style, a slightly longer release can make the bass feel smoother.",
            knowledge_type=KnowledgeType.RECOMMENDATION,
            epistemic_status=EpistemicStatus.SOURCE_RECOMMENDED,
            normalized_proposition="Longer Env1.Release may improve bass smoothness in certain genres.",
            semantic_bindings=[
                SemanticBinding("target", "Env1.Release", 0.85, "Could also refer to decay"),
                SemanticBinding("role", "bass", 0.95),
                SemanticBinding("intent", "smoother tail", 0.80),
                SemanticBinding("context", "bass_pluck", 0.70),
            ],
            extraction_confidence=0.85,
            conditions=["bass instruments", "certain genres"],
            limitations=["very long release may cause mud", "genre-dependent"],
            extraction_metadata=ext_meta,
        )

        is_valid, errors = ki.validate()
        assert is_valid, f"Validation failed: {errors}"
        assert len(ki.semantic_bindings) == 4

    def test_real_extraction_ambiguous_item(self):
        """Create KnowledgeItem with ambiguity from source."""
        src = SourceReference(
            source_id="yt_f507169bd7cb",
            source_type="YOUTUBE_VIDEO",
            segment_ids=["seg_0300"],
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp="2026-09-11T12:00:00Z",
            extraction_method="semantic_extraction_v1",
            extraction_confidence=0.5,
            raw_extraction_status="EXTRACTED",
            original_segments_count=1,
        )
        ki = KnowledgeItem(
            knowledge_item_id="ki_ambiguous_001",
            source_reference=src,
            original_proposition="Make it longer",
            knowledge_type=KnowledgeType.PROCEDURE,
            epistemic_status=EpistemicStatus.SOURCE_REPORTED,
            extraction_confidence=0.5,
            ambiguity=(
                "Ambiguous target: Could refer to Env1.Release (longer tail), "
                "Env1.Decay (longer decay phase), or note duration in DAW. "
                "Context does not disambiguate."
            ),
            extraction_metadata=ext_meta,
        )

        is_valid, errors = ki.validate()
        assert is_valid, f"Validation failed: {errors}"
        assert ki.ambiguity is not None


class TestAuthorityBoundary:
    """Test that KnowledgeItem cannot be mistaken for authority."""

    def test_knowledge_item_not_authority(self):
        """KnowledgeItem has no authority fields."""
        src = SourceReference(
            source_id="yt_test",
            source_type="YOUTUBE_VIDEO",
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp="2026-09-11T12:00:00Z",
            extraction_method="test",
            extraction_confidence=0.8,
            raw_extraction_status="EXTRACTED",
        )
        ki = KnowledgeItem(
            knowledge_item_id="ki_boundary_test",
            source_reference=src,
            original_proposition="Test proposition",
            knowledge_type=KnowledgeType.CONCEPT,
            epistemic_status=EpistemicStatus.SOURCE_REPORTED,
            extraction_metadata=ext_meta,
        )

        # Check that authority-related attributes don't exist
        assert not hasattr(ki, "admission_status")
        assert not hasattr(ki, "capability_status")
        assert not hasattr(ki, "authorized_mutation")
        assert not hasattr(ki, "execution_permission")

    def test_knowledge_item_injection_of_authority_detected(self):
        """Injected authority fields are detected by validation."""
        src = SourceReference(
            source_id="yt_test",
            source_type="YOUTUBE_VIDEO",
        )
        ext_meta = ExtractionMetadata(
            extraction_timestamp="2026-09-11T12:00:00Z",
            extraction_method="test",
            extraction_confidence=0.8,
            raw_extraction_status="EXTRACTED",
        )
        ki = KnowledgeItem(
            knowledge_item_id="ki_injection_test",
            source_reference=src,
            original_proposition="Test",
            knowledge_type=KnowledgeType.CONCEPT,
            epistemic_status=EpistemicStatus.SOURCE_REPORTED,
            extraction_metadata=ext_meta,
        )

        # Try to inject authority
        ki.capability_status = "CAUSAL_VERIFIED"

        is_valid, errors = ki.validate()
        assert not is_valid
        assert any("authority" in e for e in errors)
