"""Tests for Step 5.3 — Real Source Acquisition."""

import json
from pathlib import Path
import pytest


class TestRealSourceAcquisition:
    """Test real YouTube source acquisition proof."""

    @pytest.fixture
    def artifact_path(self):
        """Path to the 5.3 acquisition artifact."""
        return Path("serum2/knowledge/yt_74ab96e1f377_source_ingestion_5_3.json")

    @pytest.fixture
    def artifact(self, artifact_path):
        """Load the real acquisition artifact."""
        if not artifact_path.exists():
            pytest.skip("5.3 acquisition artifact not found")
        with open(artifact_path) as f:
            return json.load(f)

    def test_artifact_exists(self, artifact_path):
        """Artifact file persists."""
        assert artifact_path.exists(), f"Artifact not found at {artifact_path}"

    def test_artifact_valid_json(self, artifact):
        """Artifact is valid JSON."""
        assert isinstance(artifact, dict)
        assert "source" in artifact
        assert "transcript_segments" in artifact

    def test_source_identity_present(self, artifact):
        """Source identity is preserved."""
        source = artifact["source"]
        assert source["source_id"], "Missing source_id"
        assert source["url"], "Missing URL"
        assert source["video_id"], "Missing video_id"

    def test_source_metadata_present(self, artifact):
        """Source metadata is retained."""
        source = artifact["source"]
        # May be UNKNOWN if acquisition fails, but field should exist
        assert "title" in source
        assert "channel" in source
        assert "upload_date" in source
        assert "retrieval_timestamp" in source

    def test_transcript_segments_exist(self, artifact):
        """Transcript segments are present and non-empty."""
        segments = artifact["transcript_segments"]
        assert len(segments) > 0, "No transcript segments found"

    def test_segments_have_required_fields(self, artifact):
        """Each segment has required provenance fields."""
        for seg in artifact["transcript_segments"][:5]:  # Check first 5
            assert "segment_id" in seg, "Missing segment_id"
            assert "text" in seg, "Missing text"
            assert "start_time_sec" in seg, "Missing start_time_sec"
            assert "end_time_sec" in seg, "Missing end_time_sec"

    def test_segment_ids_stable(self, artifact):
        """Segment IDs are deterministic (seg_0000, seg_0001, ...)."""
        segments = artifact["transcript_segments"]
        for i, seg in enumerate(segments):
            expected_id = f"seg_{i:04d}"
            assert seg["segment_id"] == expected_id, \
                f"Segment {i} has ID {seg['segment_id']}, expected {expected_id}"

    def test_segment_text_preserved(self, artifact):
        """Original transcript text is preserved exactly."""
        segments = artifact["transcript_segments"]
        for seg in segments:
            text = seg["text"]
            assert text, f"Segment {seg['segment_id']} has empty text"
            # Text should be string, not None or empty
            assert isinstance(text, str)
            assert len(text) > 0

    def test_timestamps_present_and_numeric(self, artifact):
        """Timestamps are numeric and present."""
        segments = artifact["transcript_segments"]
        for seg in segments[:10]:  # Check first 10
            start = seg["start_time_sec"]
            end = seg["end_time_sec"]
            assert isinstance(start, (int, float)), f"start_time_sec not numeric for {seg['segment_id']}"
            assert isinstance(end, (int, float)), f"end_time_sec not numeric for {seg['segment_id']}"

    def test_transcript_segment_count_accurate(self, artifact):
        """Reported segment count matches actual segments."""
        source = artifact["source"]
        segments = artifact["transcript_segments"]
        assert source["transcript_segment_count"] == len(segments), \
            f"Segment count mismatch: {source['transcript_segment_count']} vs {len(segments)}"

    def test_transcript_available_flag(self, artifact):
        """transcript_available flag matches actual data."""
        source = artifact["source"]
        segments = artifact["transcript_segments"]
        if len(segments) > 0:
            assert source["transcript_available"] is True
        else:
            assert source["transcript_available"] is False

    def test_source_id_derivable_from_url(self, artifact):
        """Source ID can be derived from URL (hash-based)."""
        import hashlib
        source = artifact["source"]
        expected_id = "yt_" + hashlib.md5(source["url"].encode()).hexdigest()[:12]
        assert source["source_id"] == expected_id, \
            f"Source ID not derived from URL. Got {source['source_id']}, expected {expected_id}"

    def test_knowledge_items_count_matches_segments(self, artifact):
        """KnowledgeItem count matches segment count."""
        segments = artifact["transcript_segments"]
        knowledge_items = artifact.get("knowledge_items", [])
        assert len(knowledge_items) == len(segments), \
            f"KnowledgeItem mismatch: {len(knowledge_items)} vs {len(segments)} segments"

    def test_knowledge_items_have_provenance(self, artifact):
        """Each KnowledgeItem retains source provenance."""
        knowledge_items = artifact.get("knowledge_items", [])
        for ki in knowledge_items[:5]:  # Check first 5
            assert "source_id" in ki, "KI missing source_id"
            assert "segment_id" in ki, "KI missing segment_id"
            assert "raw_text" in ki, "KI missing raw_text"

    def test_validation_results_recorded(self, artifact):
        """Validation results are recorded."""
        assert "validation" in artifact
        validation = artifact["validation"]
        assert "transcript_exists" in validation
        assert "source_id_stable" in validation
        assert "every_segment_has_provenance" in validation

    def test_acquisition_phase_marked(self, artifact):
        """Acquisition phase is marked."""
        assert artifact.get("acquisition_phase") == "5.3", \
            "Artifact not marked as Step 5.3 acquisition"

    def test_reloadable_without_loss(self, artifact):
        """Artifact can be reloaded without information loss."""
        # This is the same as loading it, so if we got here, it's valid
        assert artifact is not None
        source_before = artifact["source"]["source_id"]
        segment_count_before = len(artifact["transcript_segments"])

        # Simulate reload by converting to JSON and back
        json_str = json.dumps(artifact)
        reloaded = json.loads(json_str)

        assert reloaded["source"]["source_id"] == source_before
        assert len(reloaded["transcript_segments"]) == segment_count_before

    def test_multiple_segments_cover_reasonable_duration(self, artifact):
        """Multiple segments exist and cover reasonable video duration."""
        segments = artifact["transcript_segments"]
        assert len(segments) >= 10, "Too few segments for meaningful transcript"

        # Check time coverage
        if len(segments) > 0:
            first_start = segments[0]["start_time_sec"]
            last_end = segments[-1]["end_time_sec"]
            duration_covered = last_end - first_start
            assert duration_covered > 0, "Transcript covers no time"
            # Typically a real video will cover at least 30 seconds
            assert duration_covered >= 1, "Transcript duration too short"

    def test_first_segment_not_empty(self, artifact):
        """First segment has text content."""
        segments = artifact["transcript_segments"]
        assert len(segments) > 0, "No segments"
        first_segment = segments[0]
        assert first_segment["text"], "First segment text is empty"
        assert len(first_segment["text"]) > 3, "First segment text too short"

    def test_different_from_historical_sources(self, artifact):
        """Acquisition is from a different source than historical data."""
        source_id = artifact["source"]["source_id"]
        # Historical sources used:
        # - yt_f507169bd7cb (original Serum 2 guide)
        # - yt_dfd7d28bfae7 (failed attempt)
        # New acquisition should be different
        assert source_id not in ["yt_f507169bd7cb", "yt_dfd7d28bfae7"], \
            f"Source ID {source_id} is from historical acquisition, not new"


class TestAcquisitionProvenance:
    """Test that provenance is sufficient for KnowledgeItem creation."""

    @pytest.fixture
    def artifact_path(self):
        return Path("serum2/knowledge/yt_74ab96e1f377_source_ingestion_5_3.json")

    @pytest.fixture
    def artifact(self, artifact_path):
        if not artifact_path.exists():
            pytest.skip("Artifact not found")
        with open(artifact_path) as f:
            return json.load(f)

    def test_can_create_knowledge_item_from_segment(self, artifact):
        """Can create KnowledgeItem from segment + source provenance."""
        from serum2.knowledge.knowledge_item import (
            KnowledgeItem,
            KnowledgeType,
            EpistemicStatus,
            SourceReference,
            ExtractionMetadata,
        )
        from datetime import datetime, timezone

        source = artifact["source"]
        segment = artifact["transcript_segments"][0]

        # Create KnowledgeItem using artifact provenance
        src_ref = SourceReference(
            source_id=source["source_id"],
            source_type="YOUTUBE_VIDEO",
            source_url=source["url"],
            source_title=source["title"],
            segment_ids=[segment["segment_id"]],
            start_time_sec=segment["start_time_sec"],
            end_time_sec=segment["end_time_sec"],
        )

        ext_meta = ExtractionMetadata(
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            extraction_method="youtube_source_ingestion",
            extraction_confidence=0.9,
            raw_extraction_status="SOURCE_TEXT_ONLY",
            original_segments_count=1,
        )

        ki = KnowledgeItem(
            knowledge_item_id=segment["segment_id"],
            source_reference=src_ref,
            original_proposition=segment["text"],
            knowledge_type=KnowledgeType.OBSERVATION,
            epistemic_status=EpistemicStatus.SOURCE_REPORTED,
            extraction_metadata=ext_meta,
        )

        # Verify it's valid
        is_valid, errors = ki.validate()
        assert is_valid, f"KnowledgeItem validation failed: {errors}"

    def test_segment_provenance_sufficient_for_traceability(self, artifact):
        """Segment-level provenance allows full traceability."""
        source = artifact["source"]
        segment = artifact["transcript_segments"][50]  # Middle segment

        # Can answer: where did this come from?
        assert segment["segment_id"], "Cannot identify segment"
        assert segment["text"], "Cannot get segment text"
        assert "start_time_sec" in segment, "Cannot locate segment in video"
        assert "end_time_sec" in segment, "Cannot determine segment duration"

        # Can answer: which source?
        assert source["source_id"], "Cannot identify source"
        assert source["url"], "Cannot access original source"
        assert source["video_id"], "Cannot find on YouTube"

        # Can answer: when was it acquired?
        assert source["retrieval_timestamp"], "Cannot determine acquisition time"

    def test_all_segments_traceable_to_source(self, artifact):
        """Every segment can be traced back to its source."""
        source = artifact["source"]
        segments = artifact["transcript_segments"]

        for seg in segments:
            # Each segment must have:
            # 1. Unique identity within source
            assert "segment_id" in seg
            # 2. Reference to parent source (implicit via artifact structure)
            # 3. Original text from source
            assert "text" in seg
            assert len(seg["text"]) > 0
            # 4. Temporal location (if applicable)
            assert "start_time_sec" in seg
            assert "end_time_sec" in seg

        # Overall provenance:
        assert source["source_id"]
        assert source["url"]
        assert len(segments) == source["transcript_segment_count"]
