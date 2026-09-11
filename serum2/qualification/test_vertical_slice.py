"""
Test: Knowledge → Intent → Admission → Real Execution → Measurement → Episode

Smallest vertical slice proving the complete loop with one qualified capability.
"""
import json
import pytest
from pathlib import Path
from serum2.knowledge.intent_bridge import resolve_intent_to_candidates
from serum2.qualification.vertical_slice_executor import (
    check_admission,
    select_measurement_metric,
    create_execution_record,
)


class TestKnowledgeRetrieval:
    """Verify existing YouTube knowledge can be retrieved."""

    def test_hypotheses_exist(self):
        """Hypotheses file exists and loads."""
        hyp_file = Path("serum2/knowledge/yt_f507169bd7cb_hypotheses.json")
        assert hyp_file.exists()
        with open(hyp_file) as f:
            data = json.load(f)
        assert data.get("version") == "1.0"
        assert len(data.get("hypotheses", [])) > 0

    def test_target_resolution_exists(self):
        """Target resolution file exists and loads."""
        target_file = Path("serum2/knowledge/yt_f507169bd7cb_target_resolution.json")
        assert target_file.exists()
        with open(target_file) as f:
            data = json.load(f)
        assert data.get("version") == "1.0"
        assert len(data.get("resolved_items", [])) > 0

    def test_env1_release_in_hypotheses(self):
        """Env1.Release target exists in YouTube hypotheses."""
        with open("serum2/knowledge/yt_f507169bd7cb_hypotheses.json") as f:
            data = json.load(f)
        targets = [h.get("target") for h in data.get("hypotheses", [])]
        assert "Env1.Release" in targets


class TestIntentBridge:
    """Verify intent can be resolved to semantic targets with provenance."""

    def test_sustain_intent_resolves_to_env1_release(self):
        """Intent 'make the note sustain longer' resolves to Env1.Release."""
        intent = "make the note sustain longer"
        resolution = resolve_intent_to_candidates(
            intent,
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        assert resolution.matched_hypotheses > 0
        assert any(op.target == "Env1.Release" for op in resolution.candidate_operations)
        assert resolution.provenance_preserved is True

    def test_candidate_operation_has_provenance(self):
        """Candidate operations preserve source provenance."""
        intent = "extend the release"
        resolution = resolve_intent_to_candidates(
            intent,
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        for op in resolution.candidate_operations:
            assert op.source_knowledge_item_id is not None
            assert op.source_hypothesis_id is not None
            assert op.source_confidence >= 0.0


class TestAdmission:
    """Verify admission layer works with qualified targets."""

    def test_env1_release_admitted(self):
        """Env1.Release is in SEMANTIC_TARGETS and admitted."""
        with open("serum2/knowledge/yt_f507169bd7cb_hypotheses.json") as f:
            hyp_data = json.load(f)

        env1_release_hyp = next(
            h for h in hyp_data["hypotheses"] if h.get("target") == "Env1.Release"
        )

        from serum2.knowledge.intent_bridge import CandidateOperation

        candidate = CandidateOperation(
            target="Env1.Release",
            operation=env1_release_hyp.get("operation"),
            reason="Test",
            source_knowledge_item_id=env1_release_hyp.get("knowledge_item_id"),
            source_hypothesis_id=env1_release_hyp.get("hypothesis_id"),
            source_confidence=env1_release_hyp.get("source_confidence", 0.9),
            measurement_plan=env1_release_hyp.get("measurement_plan", []),
            hypothesis_type=env1_release_hyp.get("hypothesis_type", "BEHAVIORAL"),
        )

        status, reason = check_admission("Env1.Release", candidate)
        assert status == "ADMITTED"

    def test_unknown_target_rejected(self):
        """Unknown targets are rejected, not downgraded."""
        from serum2.knowledge.intent_bridge import CandidateOperation

        candidate = CandidateOperation(
            target="UnknownParam.Foo",
            operation=None,
            reason="Test",
            source_knowledge_item_id="ki_unknown",
            source_hypothesis_id="hyp_unknown",
            source_confidence=0.5,
            measurement_plan=[],
            hypothesis_type="UNKNOWN",
        )

        status, reason = check_admission("UnknownParam.Foo", candidate)
        assert status == "UNKNOWN_TARGET"

    def test_unqualified_target_rejected(self):
        """Targets without CAUSAL_VERIFIED status are rejected."""
        from serum2.knowledge.intent_bridge import CandidateOperation

        candidate = CandidateOperation(
            target="Filter2.Cutoff",
            operation=None,
            reason="Test",
            source_knowledge_item_id="ki_test",
            source_hypothesis_id="hyp_test",
            source_confidence=0.5,
            measurement_plan=[],
            hypothesis_type="UNKNOWN",
        )

        status, reason = check_admission("Filter2.Cutoff", candidate)
        # Filter2.Cutoff is intentionally not in SEMANTIC_TARGETS (not qualified)
        # so it returns UNKNOWN_TARGET, not a fallback to host_param
        assert status == "UNKNOWN_TARGET"


class TestMeasurementSelection:
    """Verify correct measurement metric for each target."""

    @pytest.mark.parametrize(
        "target,expected_metric",
        [
            ("OSC1.Level", "rms_db"),
            ("OSC1.Detune", "pitch_shift_semitones"),
            ("OSC1.Octave", "pitch_shift_semitones"),
            ("Env1.Attack", "rms_db"),
            ("Env1.Release", "tail_rms_db"),
            ("Filter.Cutoff", "spectral_centroid_hz"),
        ],
    )
    def test_metric_selection(self, target, expected_metric):
        """Correct measurement metric is selected."""
        metric = select_measurement_metric(target)
        assert metric == expected_metric


class TestExecutionRecord:
    """Verify episode artifact can be created."""

    def test_episode_record_creation(self):
        """Episode record captures full execution context."""
        from serum2.knowledge.intent_bridge import CandidateOperation

        candidate = CandidateOperation(
            target="Env1.Release",
            operation="increase",
            reason="User intent",
            source_knowledge_item_id="ki_ext_123",
            source_hypothesis_id="hyp_001",
            source_confidence=0.9,
            measurement_plan=["tail_rms_db"],
            hypothesis_type="BEHAVIORAL",
        )

        record = create_execution_record(
            episode_id="ep_vertical_slice_001",
            human_intent="make the note sustain longer",
            candidate_op=candidate,
            admission_status="ADMITTED",
            admission_reason="Env1.Release has CAUSAL_VERIFIED capability",
        )

        assert record.episode_id == "ep_vertical_slice_001"
        assert record.admission_status == "ADMITTED"
        assert record.semantic_target == "Env1.Release"
        assert record.measurement_metric == "tail_rms_db"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
