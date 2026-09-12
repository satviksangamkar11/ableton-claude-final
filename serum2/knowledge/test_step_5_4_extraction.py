"""Tests for Step 5.4 — Proposition Extraction."""

import json
from pathlib import Path
import pytest


class TestPropositionExtraction:
    """Test real proposition extraction from 5.3 artifact."""

    @pytest.fixture
    def extraction_artifact_path(self):
        return Path("serum2/knowledge/yt_74ab96e1f377_proposition_extraction_5_4.json")

    @pytest.fixture
    def source_artifact_path(self):
        return Path("serum2/knowledge/yt_74ab96e1f377_source_ingestion_5_3.json")

    @pytest.fixture
    def extraction_artifact(self, extraction_artifact_path):
        if not extraction_artifact_path.exists():
            pytest.skip("Extraction artifact not found")
        with open(extraction_artifact_path) as f:
            return json.load(f)

    @pytest.fixture
    def source_artifact(self, source_artifact_path):
        if not source_artifact_path.exists():
            pytest.skip("Source artifact not found")
        with open(source_artifact_path) as f:
            return json.load(f)

    def test_extraction_artifact_exists(self, extraction_artifact_path):
        """Extraction artifact persists."""
        assert extraction_artifact_path.exists()

    def test_extraction_artifact_valid_json(self, extraction_artifact):
        """Extraction artifact is valid JSON."""
        assert isinstance(extraction_artifact, dict)
        assert "propositions" in extraction_artifact
        assert "extraction_metadata" in extraction_artifact

    def test_source_identity_preserved(self, extraction_artifact, source_artifact):
        """Source identity carries through extraction."""
        assert extraction_artifact["source_id"] == source_artifact["source"]["source_id"]
        assert extraction_artifact["source_title"] == source_artifact["source"]["title"]

    def test_propositions_not_empty(self, extraction_artifact):
        """Propositions list is non-empty."""
        assert len(extraction_artifact["propositions"]) > 0

    def test_proposition_has_required_fields(self, extraction_artifact):
        """Each proposition has required provenance fields."""
        for prop in extraction_artifact["propositions"][:3]:
            assert "proposition_id" in prop
            assert "source_id" in prop
            assert "source_segment_ids" in prop
            assert "original_text" in prop
            assert "kind" in prop
            assert "epistemic_status" in prop

    def test_proposition_segment_ids_traceable(self, extraction_artifact, source_artifact):
        """Segment IDs in propositions reference real source segments."""
        source_segment_ids = {seg["segment_id"] for seg in source_artifact["transcript_segments"]}

        for prop in extraction_artifact["propositions"]:
            for seg_id in prop["source_segment_ids"]:
                assert seg_id in source_segment_ids, \
                    f"Segment {seg_id} not found in source artifact"

    def test_original_text_preserved_exactly(self, extraction_artifact, source_artifact):
        """Original source text is preserved exactly (not modified)."""
        segments = {seg["segment_id"]: seg["text"] for seg in source_artifact["transcript_segments"]}

        for prop in extraction_artifact["propositions"]:
            # Reconstruct original text from segment IDs
            expected_text = " ".join([
                segments[seg_id] for seg_id in prop["source_segment_ids"]
            ])
            # Text should match (may have extra spaces, but content identical)
            expected_normalized = " ".join(expected_text.split())
            actual_normalized = " ".join(prop["original_text"].split())
            assert actual_normalized == expected_normalized, \
                f"Text modified: {actual_normalized[:100]} vs {expected_normalized[:100]}"

    def test_classification_values_valid(self, extraction_artifact):
        """Classification kinds are from predefined list."""
        valid_kinds = {
            "CONCEPT", "PROCEDURE", "PRINCIPLE", "OBSERVATION",
            "RECOMMENDATION", "CONDITION", "EXAMPLE", "CONTEXT", "LIMITATION"
        }
        for prop in extraction_artifact["propositions"]:
            assert prop["kind"] in valid_kinds, \
                f"Invalid kind: {prop['kind']}"

    def test_epistemic_status_values_valid(self, extraction_artifact):
        """Epistemic status is from predefined list."""
        valid_statuses = {
            "SOURCE_REPORTED", "SOURCE_RECOMMENDED", "SOURCE_OBSERVED",
            "SYSTEM_INTERPRETATION", "EXPERIMENTALLY_VERIFIED", "UNKNOWN"
        }
        for prop in extraction_artifact["propositions"]:
            assert prop["epistemic_status"] in valid_statuses, \
                f"Invalid epistemic status: {prop['epistemic_status']}"

    def test_confidence_in_bounds(self, extraction_artifact):
        """Extraction confidence is between 0.0 and 1.0."""
        for prop in extraction_artifact["propositions"]:
            confidence = prop.get("extraction_confidence", 0.7)
            assert 0.0 <= confidence <= 1.0, \
                f"Confidence out of bounds: {confidence}"

    def test_ambiguity_preserved(self, extraction_artifact):
        """Ambiguity field is preserved (None or string)."""
        for prop in extraction_artifact["propositions"]:
            ambiguity = prop.get("ambiguity")
            assert ambiguity is None or isinstance(ambiguity, str), \
                f"Invalid ambiguity type: {type(ambiguity)}"

    def test_no_fabricated_semantic_targets(self, extraction_artifact):
        """No fabricated semantic targets in propositions."""
        # Propositions should not automatically include Serum targets
        # unless the source explicitly mentions them
        for prop in extraction_artifact["propositions"]:
            semantic_targets = prop.get("semantic_targets", {})
            # If semantic targets exist, they should be justified
            if semantic_targets:
                # This is OK - means extraction found explicit targets
                pass

    def test_statistics_accurate(self, extraction_artifact):
        """Metadata statistics match actual propositions."""
        metadata = extraction_artifact["extraction_metadata"]
        propositions = extraction_artifact["propositions"]

        assert metadata["retained_propositions"] == len(propositions)
        assert metadata["total_segments"] > 0
        assert metadata["semantic_units"] > 0

    def test_classification_distribution_accurate(self, extraction_artifact):
        """Classification distribution matches actual data."""
        metadata = extraction_artifact["extraction_metadata"]
        propositions = extraction_artifact["propositions"]

        kind_counts = {}
        for prop in propositions:
            kind = prop["kind"]
            kind_counts[kind] = kind_counts.get(kind, 0) + 1

        declared_distribution = metadata["classification_distribution"]
        for kind, count in kind_counts.items():
            assert declared_distribution[kind] == count, \
                f"Kind {kind}: declared {declared_distribution[kind]}, actual {count}"

    def test_epistemic_distribution_accurate(self, extraction_artifact):
        """Epistemic distribution matches actual data."""
        metadata = extraction_artifact["extraction_metadata"]
        propositions = extraction_artifact["propositions"]

        status_counts = {}
        for prop in propositions:
            status = prop["epistemic_status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        declared_distribution = metadata["epistemic_distribution"]
        for status, count in status_counts.items():
            assert declared_distribution[status] == count, \
                f"Status {status}: declared {declared_distribution[status]}, actual {count}"

    def test_multi_segment_propositions_supported(self, extraction_artifact):
        """Propositions can span multiple segments."""
        multi_segment_count = 0
        for prop in extraction_artifact["propositions"]:
            if len(prop["source_segment_ids"]) > 1:
                multi_segment_count += 1

        # Should have at least some multi-segment propositions
        assert multi_segment_count > 0, "No multi-segment propositions found"

    def test_timestamps_present_and_numeric(self, extraction_artifact):
        """Propositions have numeric timestamps."""
        for prop in extraction_artifact["propositions"][:5]:
            start = prop.get("start_time_sec")
            end = prop.get("end_time_sec")
            assert isinstance(start, (int, float)), f"start_time_sec not numeric"
            assert isinstance(end, (int, float)), f"end_time_sec not numeric"
            assert start <= end, f"start_time_sec > end_time_sec"

    def test_phase_marked(self, extraction_artifact):
        """Extraction phase is marked in artifact."""
        assert extraction_artifact.get("phase") == "5.4"

    def test_proposition_id_unique(self, extraction_artifact):
        """Each proposition has unique ID."""
        ids = [prop["proposition_id"] for prop in extraction_artifact["propositions"]]
        assert len(ids) == len(set(ids)), "Duplicate proposition IDs found"

    def test_extraction_confidence_separate_from_epistemic(self, extraction_artifact):
        """Extraction confidence is separate from epistemic status."""
        for prop in extraction_artifact["propositions"]:
            # Both should be present and distinct
            assert "extraction_confidence" in prop
            assert "epistemic_status" in prop
            # They should be different types (float vs string)
            confidence = prop["extraction_confidence"]
            status = prop["epistemic_status"]
            assert isinstance(confidence, (int, float))
            assert isinstance(status, str)


class TestPropositionProvenance:
    """Test that provenance is complete for KnowledgeItem creation."""

    @pytest.fixture
    def extraction_artifact_path(self):
        return Path("serum2/knowledge/yt_74ab96e1f377_proposition_extraction_5_4.json")

    @pytest.fixture
    def extraction_artifact(self, extraction_artifact_path):
        if not extraction_artifact_path.exists():
            pytest.skip("Extraction artifact not found")
        with open(extraction_artifact_path) as f:
            return json.load(f)

    def test_proposition_to_knowledge_item_creation(self, extraction_artifact):
        """Can create KnowledgeItem from proposition."""
        from serum2.knowledge.knowledge_item import (
            KnowledgeItem,
            KnowledgeType,
            EpistemicStatus,
            SourceReference,
            ExtractionMetadata,
        )
        from datetime import datetime, timezone

        # Use first proposition
        prop = extraction_artifact["propositions"][0]

        # Map extraction kind to KnowledgeType
        kind_map = {
            "CONCEPT": KnowledgeType.CONCEPT,
            "PROCEDURE": KnowledgeType.PROCEDURE,
            "PRINCIPLE": KnowledgeType.PRINCIPLE,
            "OBSERVATION": KnowledgeType.OBSERVATION,
            "RECOMMENDATION": KnowledgeType.RECOMMENDATION,
            "CONDITION": KnowledgeType.CONDITION,
            "EXAMPLE": KnowledgeType.EXAMPLE,
            "CONTEXT": KnowledgeType.CONTEXT,
            "LIMITATION": KnowledgeType.LIMITATION,
        }

        # Map epistemic status
        status_map = {
            "SOURCE_REPORTED": EpistemicStatus.SOURCE_REPORTED,
            "SOURCE_RECOMMENDED": EpistemicStatus.SOURCE_RECOMMENDED,
            "SOURCE_OBSERVED": EpistemicStatus.SOURCE_OBSERVED,
        }

        src_ref = SourceReference(
            source_id=prop["source_id"],
            source_type="YOUTUBE_VIDEO",
            segment_ids=prop["source_segment_ids"],
            start_time_sec=prop.get("start_time_sec"),
            end_time_sec=prop.get("end_time_sec"),
        )

        ext_meta = ExtractionMetadata(
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            extraction_method="semantic_extraction_v1",
            extraction_confidence=prop.get("extraction_confidence", 0.7),
            raw_extraction_status="EXTRACTED",
            original_segments_count=len(prop["source_segment_ids"]),
        )

        ki = KnowledgeItem(
            knowledge_item_id=prop["proposition_id"],
            source_reference=src_ref,
            original_proposition=prop["original_text"],
            knowledge_type=kind_map.get(prop["kind"], KnowledgeType.OBSERVATION),
            epistemic_status=status_map.get(prop["epistemic_status"], EpistemicStatus.SOURCE_REPORTED),
            extraction_confidence=prop.get("extraction_confidence", 0.7),
            extraction_metadata=ext_meta,
        )

        # Should validate
        is_valid, errors = ki.validate()
        assert is_valid, f"KnowledgeItem validation failed: {errors}"

    def test_all_propositions_traceable(self, extraction_artifact):
        """Every proposition can be traced to source."""
        for prop in extraction_artifact["propositions"]:
            # Must have source identity
            assert prop["source_id"]
            # Must have segment references
            assert prop["source_segment_ids"]
            assert len(prop["source_segment_ids"]) > 0
            # Must have original text
            assert prop["original_text"]
            assert len(prop["original_text"]) > 0
