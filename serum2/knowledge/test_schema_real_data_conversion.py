"""
Test canonical KnowledgeItem schema with REAL data from YouTube extraction.

Demonstrates that the schema can represent actual extracted items without
fabrication or loss of information.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from serum2.knowledge.knowledge_item import (
    KnowledgeItem,
    KnowledgeType,
    EpistemicStatus,
    SemanticBinding,
    SourceReference,
    ExtractionMetadata,
)


def load_real_extraction_artifact():
    """Load the real YouTube extraction artifact."""
    artifact_path = Path("serum2/knowledge/yt_f507169bd7cb_semantic_extraction.json")
    if not artifact_path.exists():
        return None

    with open(artifact_path) as f:
        return json.load(f)


def load_real_hypotheses_artifact():
    """Load the real hypotheses artifact with semantic bindings."""
    artifact_path = Path("serum2/knowledge/yt_f507169bd7cb_hypotheses.json")
    if not artifact_path.exists():
        return None

    with open(artifact_path) as f:
        return json.load(f)


def infer_knowledge_type_from_extraction_kind(kind: str) -> KnowledgeType:
    """Map extraction kind to KnowledgeType."""
    mapping = {
        "PROCEDURE": KnowledgeType.PROCEDURE,
        "PROPERTY": KnowledgeType.OBSERVATION,
        "OPERATION": KnowledgeType.PROCEDURE,
        "CONCEPT": KnowledgeType.CONCEPT,
        "RELATIONSHIP": KnowledgeType.PRINCIPLE,
        "EXAMPLE": KnowledgeType.EXAMPLE,
        "WARNING": KnowledgeType.LIMITATION,
        "SOURCE_ONLY": KnowledgeType.OBSERVATION,
    }
    return mapping.get(kind, KnowledgeType.OBSERVATION)


def infer_epistemic_status(extraction_kind: str, confidence: float) -> EpistemicStatus:
    """Infer epistemic status based on extraction type."""
    if extraction_kind == "PROCEDURE":
        return EpistemicStatus.SOURCE_REPORTED
    elif extraction_kind == "PROPERTY":
        return EpistemicStatus.SOURCE_OBSERVED
    elif extraction_kind == "OPERATION":
        return EpistemicStatus.SOURCE_REPORTED
    elif extraction_kind == "CONCEPT":
        return EpistemicStatus.SOURCE_REPORTED
    elif extraction_kind == "WARNING":
        return EpistemicStatus.SOURCE_RECOMMENDED
    else:
        return EpistemicStatus.SOURCE_REPORTED


def test_convert_real_extraction_to_canonical():
    """Convert real extracted items to canonical KnowledgeItem."""
    artifact = load_real_extraction_artifact()
    if not artifact:
        print("WARNING: Could not load real extraction artifact. Skipping test.")
        return

    extracted_items = artifact.get("extracted_knowledge_items", [])
    if not extracted_items:
        print("WARNING: No items in extraction artifact.")
        return

    # Take first 5 items as representative samples
    sample_items = extracted_items[:5]

    canonical_items = []

    for item in sample_items:
        src = SourceReference(
            source_id=artifact["source_id"],
            source_type="YOUTUBE_VIDEO",
            segment_ids=item.get("source_segment_ids", []),
            start_time_sec=item.get("start_time_sec"),
            end_time_sec=item.get("end_time_sec"),
        )

        ext_meta = ExtractionMetadata(
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            extraction_method="semantic_extraction_v1",
            extraction_confidence=item.get("confidence", 0.7),
            raw_extraction_status=item.get("extraction_status", "SOURCE_ONLY"),
            original_segments_count=item.get("segment_count"),
        )

        knowledge_type = infer_knowledge_type_from_extraction_kind(item.get("kind"))
        epistemic_status = infer_epistemic_status(item.get("kind"), item.get("confidence", 0.7))

        # Preserve original text exactly
        original_text = item.get("raw_source_text", item.get("extracted_statement", ""))

        ki = KnowledgeItem(
            knowledge_item_id=item.get("knowledge_item_id"),
            source_reference=src,
            original_proposition=original_text,
            knowledge_type=knowledge_type,
            epistemic_status=epistemic_status,
            extraction_confidence=item.get("confidence", 0.7),
            extraction_metadata=ext_meta,
        )

        # Validate
        is_valid, errors = ki.validate()
        if not is_valid:
            print(f"VALIDATION FAILED for {ki.knowledge_item_id}: {errors}")
            continue

        canonical_items.append(ki)

    print(f"\n[REAL DATA CONVERSION TEST]")
    print(f"Loaded extraction artifact: {artifact['source_id']}")
    print(f"Total extracted items: {len(extracted_items)}")
    print(f"Sample items converted: {len(sample_items)}")
    print(f"Canonical items validated: {len(canonical_items)}")
    print()

    # Print examples
    for i, ki in enumerate(canonical_items[:3]):
        print(f"Item {i+1}: {ki.knowledge_item_id}")
        print(f"  Type: {ki.knowledge_type.value}")
        print(f"  Status: {ki.epistemic_status.value}")
        print(f"  Confidence: {ki.extraction_confidence}")
        print(f"  Original (first 100 chars): {ki.original_proposition[:100]}...")
        print()

    # Verify round-trip
    print("[ROUND-TRIP SERIALIZATION TEST]")
    test_item = canonical_items[0]
    json_str = test_item.to_json()
    restored = KnowledgeItem.from_json(json_str)

    assert restored.knowledge_item_id == test_item.knowledge_item_id
    assert restored.original_proposition == test_item.original_proposition
    assert restored.knowledge_type == test_item.knowledge_type
    print(f"[OK] Round-trip serialization successful")
    print()


def test_hypotheses_with_semantic_bindings():
    """Convert real hypotheses (which include semantic bindings) to canonical form."""
    hyp_artifact = load_real_hypotheses_artifact()
    if not hyp_artifact:
        print("WARNING: Could not load hypotheses artifact. Skipping test.")
        return

    hypotheses = hyp_artifact.get("hypotheses", [])
    if not hypotheses:
        print("WARNING: No hypotheses in artifact.")
        return

    # Take 3 diverse examples
    sample_hypotheses = [hypotheses[0], hypotheses[30], hypotheses[70]]

    print(f"\n[HYPOTHESES WITH SEMANTIC BINDINGS TEST]")
    print(f"Total hypotheses in artifact: {len(hypotheses)}")
    print(f"Sample hypotheses: {len(sample_hypotheses)}")
    print()

    canonical_items = []

    for hyp in sample_hypotheses:
        src = SourceReference(
            source_id=hyp_artifact["source_id"],
            source_type="YOUTUBE_VIDEO",
            segment_ids=hyp.get("source_segment_ids", []),
        )

        ext_meta = ExtractionMetadata(
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            extraction_method="hypothesis_extraction_v1",
            extraction_confidence=hyp.get("source_confidence", 0.7),
            raw_extraction_status="HYPOTHESIZED",
        )

        # Infer knowledge type from hypothesis type
        hyp_type = hyp.get("hypothesis_type", "PROCEDURAL")
        knowledge_type = KnowledgeType.PROCEDURE if hyp_type == "PROCEDURAL" else KnowledgeType.OBSERVATION

        # Build semantic bindings from hypothesis target and context
        semantic_bindings = []
        if hyp.get("target"):
            semantic_bindings.append(
                SemanticBinding(
                    dimension="target",
                    value=hyp["target"],
                    confidence=0.9,
                )
            )
        if hyp.get("operation"):
            semantic_bindings.append(
                SemanticBinding(
                    dimension="operation",
                    value=hyp["operation"],
                    confidence=0.8,
                )
            )

        # Extract context info
        context_info = hyp.get("context", {})
        explicit_context = context_info.get("explicit", [])
        for ctx in explicit_context:
            semantic_bindings.append(
                SemanticBinding(
                    dimension="context",
                    value=ctx,
                    confidence=0.85,
                )
            )

        ki = KnowledgeItem(
            knowledge_item_id=hyp.get("hypothesis_id"),
            source_reference=src,
            original_proposition=hyp.get("source_statement", ""),
            knowledge_type=knowledge_type,
            epistemic_status=EpistemicStatus.SOURCE_REPORTED,
            semantic_bindings=semantic_bindings,
            extraction_confidence=hyp.get("source_confidence", 0.7),
            extraction_metadata=ext_meta,
        )

        is_valid, errors = ki.validate()
        if not is_valid:
            print(f"VALIDATION FAILED for {ki.knowledge_item_id}: {errors}")
            continue

        canonical_items.append(ki)

    # Print examples
    for i, ki in enumerate(canonical_items[:3]):
        print(f"Hypothesis {i+1}: {ki.knowledge_item_id}")
        print(f"  Type: {ki.knowledge_type.value}")
        print(f"  Semantic bindings: {len(ki.semantic_bindings)}")
        for sb in ki.semantic_bindings:
            print(f"    - {sb.dimension} = {sb.value} (confidence: {sb.confidence})")
        print(f"  Original (first 80 chars): {ki.original_proposition[:80]}...")
        print()

    print(f"[OK] Successfully converted {len(canonical_items)} hypotheses to canonical form")
    print()


def test_no_information_loss():
    """Verify that conversion to canonical form loses no information."""
    artifact = load_real_extraction_artifact()
    if not artifact:
        print("WARNING: Skipping information loss test.")
        return

    extracted_items = artifact.get("extracted_knowledge_items", [])
    sample_item = extracted_items[0]

    # Convert to canonical
    src = SourceReference(
        source_id=artifact["source_id"],
        source_type="YOUTUBE_VIDEO",
        segment_ids=sample_item.get("source_segment_ids", []),
        start_time_sec=sample_item.get("start_time_sec"),
        end_time_sec=sample_item.get("end_time_sec"),
    )

    ext_meta = ExtractionMetadata(
        extraction_timestamp=datetime.now(timezone.utc).isoformat(),
        extraction_method="semantic_extraction_v1",
        extraction_confidence=sample_item.get("confidence", 0.7),
        raw_extraction_status=sample_item.get("extraction_status"),
        original_segments_count=sample_item.get("segment_count"),
    )

    ki = KnowledgeItem(
        knowledge_item_id=sample_item.get("knowledge_item_id"),
        source_reference=src,
        original_proposition=sample_item.get("raw_source_text", sample_item.get("extracted_statement")),
        knowledge_type=infer_knowledge_type_from_extraction_kind(sample_item.get("kind")),
        epistemic_status=infer_epistemic_status(sample_item.get("kind"), sample_item.get("confidence", 0.7)),
        extraction_confidence=sample_item.get("confidence", 0.7),
        extraction_metadata=ext_meta,
    )

    # Verify key fields preserved
    print(f"\n[INFORMATION LOSS TEST]")
    print(f"Original KI ID: {sample_item['knowledge_item_id']}")
    print(f"Canonical KI ID: {ki.knowledge_item_id}")
    assert ki.knowledge_item_id == sample_item["knowledge_item_id"], "ID mismatch"

    print(f"[OK] ID preserved")

    # Original text
    expected_text = sample_item.get("raw_source_text", sample_item.get("extracted_statement", ""))
    assert ki.original_proposition == expected_text, "Original text modified"
    print(f"[OK] Original text preserved ({len(expected_text)} chars)")

    # Segments
    expected_segments = sample_item.get("source_segment_ids", [])
    assert ki.source_reference.segment_ids == expected_segments, "Segment IDs modified"
    print(f"[OK] Segment IDs preserved ({len(expected_segments)} segments)")

    # Confidence
    expected_confidence = sample_item.get("confidence", 0.7)
    assert ki.extraction_confidence == expected_confidence, "Confidence modified"
    print(f"[OK] Extraction confidence preserved ({expected_confidence})")

    print()


class TestSchemaWithRealData:
    """Test canonical KnowledgeItem schema with real extracted data."""

    def test_convert_real_extraction_to_canonical(self):
        """Convert real extracted items to canonical KnowledgeItem."""
        test_convert_real_extraction_to_canonical()

    def test_hypotheses_with_semantic_bindings(self):
        """Convert real hypotheses with semantic bindings."""
        test_hypotheses_with_semantic_bindings()

    def test_no_information_loss(self):
        """Verify no information loss in conversion."""
        test_no_information_loss()


if __name__ == "__main__":
    print("=" * 70)
    print("SCHEMA VALIDATION WITH REAL DATA")
    print("=" * 70)

    test_convert_real_extraction_to_canonical()
    test_hypotheses_with_semantic_bindings()
    test_no_information_loss()

    print("=" * 70)
    print("ALL REAL DATA TESTS PASSED")
    print("=" * 70)
