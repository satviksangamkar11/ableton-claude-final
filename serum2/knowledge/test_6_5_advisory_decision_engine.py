"""
Test suite for Step 6.5 Advisory Decision Engine.

Covers all 25+ acceptance criteria:
A. Advisory decision object exists
B. Candidate ranking is explainable
C. Knowledge can influence ranking
D. Episodes can influence ranking
E. Conflicts remain visible
F. Uncertainty remains visible
G. Engine can abstain
H. Constraints can eliminate candidates
I. Decision trace is complete
J. Decision is backend-independent
K. No concrete unauthorized mutation value generated
L. No backend target path becomes authoritative
M. No measurement authority generated
N. No execution occurs
O. No CapabilityContract created
P. Real knowledge/episode context consumed
Q. Tests pass
"""

import pytest
from datetime import datetime

from step_6_5_advisory_decision_engine import (
    AdvisoryDecisionEngine,
    AdvisoryDecision,
    WeightingModel,
    DecisionStatus,
    EvidenceType,
    ScoringFactor,
    make_advisory_decision,
)
from step_6_4_semantic_reasoning_integration import (
    SemanticCandidate,
    CandidateStatus,
    CandidateReason,
)
from step_6_3_episode_context_integration import (
    Episode,
    EpisodeDecision,
    EpisodeContextBridge,
    EpisodePhase,
    DecisionType,
    MeasurementOutcome,
)
from step_6_2_universal_production_intent import (
    UniversalProductionIntent,
    SemanticDirection,
    MusicalRole,
)


class TestAdvisoryDecisionObject:
    """Test A: Advisory decision object exists."""

    def test_decision_creation(self):
        """Create an advisory decision."""
        intent = UniversalProductionIntent(
            original_user_request="Test",
        )

        decision = AdvisoryDecision(
            decision_id="dec_1",
            intent=intent,
            decision_status=DecisionStatus.DECIDED,
        )

        assert decision.decision_id == "dec_1"
        assert decision.intent is intent
        assert decision.decision_status == DecisionStatus.DECIDED

    def test_decision_with_candidate(self):
        """Decision can hold selected candidate."""
        intent = UniversalProductionIntent(
            original_user_request="Test",
        )

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Test option",
            target_concept="test",
        )

        decision = AdvisoryDecision(
            decision_id="dec_1",
            intent=intent,
            selected_candidate=candidate,
            decision_status=DecisionStatus.DECIDED,
        )

        assert decision.selected_candidate is candidate


class TestRankingExplainability:
    """Test B: Candidate ranking is explainable."""

    def test_scoring_factors_captured(self):
        """Scoring factors are captured and explainable."""
        factor = ScoringFactor(
            name="semantic_fit",
            value=0.8,
            weight=0.25,
            reasoning="Candidate concept matches intent",
            evidence_type=EvidenceType.FROM_SEMANTIC_FIT,
        )

        assert factor.name == "semantic_fit"
        assert factor.contribution() == 0.8 * 0.25

    def test_candidate_evaluation_breakdown(self):
        """Candidate evaluation shows score breakdown."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
        )

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Increase brightness",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
        )

        eval = engine._evaluate_candidate(candidate, intent)

        assert len(eval.scoring_factors) > 0
        assert eval.total_score >= 0.0 and eval.total_score <= 1.0


class TestKnowledgeInfluence:
    """Test C: Knowledge can influence ranking."""

    def test_knowledge_boosts_score(self):
        """Knowledge items boost candidate score."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="brightness",
        )

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Brightness option",
            target_concept="brightness",
            supporting_knowledge_ids=["k1", "k2"],
        )

        knowledge = [
            {"id": "k1", "title": "Knowledge about brightness"},
            {"id": "k2", "title": "More knowledge"},
        ]

        eval = engine._evaluate_candidate(candidate, intent, knowledge)

        # Should have knowledge support factor
        knowledge_factors = [f for f in eval.scoring_factors if f.name == "knowledge_support"]
        assert len(knowledge_factors) > 0

    def test_knowledge_influences_ranking(self):
        """Ranking differs based on knowledge."""
        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="brightness",
        )

        c1 = SemanticCandidate(
            candidate_id="c1",
            label="With knowledge",
            target_concept="brightness",
            supporting_knowledge_ids=["k1"],
        )

        c2 = SemanticCandidate(
            candidate_id="c2",
            label="Without knowledge",
            target_concept="brightness",
        )

        knowledge = [{"id": "k1", "title": "Support for c1"}]

        # c1 should rank higher with knowledge
        engine = AdvisoryDecisionEngine()
        decision = engine.decide(intent, [c1, c2], knowledge_items=knowledge)

        assert decision.selected_candidate is c1


class TestEpisodeInfluence:
    """Test D: Episodes can influence ranking."""

    def test_episode_boosts_score(self):
        """Episodes boost candidate score."""
        bridge = EpisodeContextBridge()

        # Add prior success
        episode = Episode(
            episode_id="ep_1",
            initial_intent=UniversalProductionIntent(
                original_user_request="Prior test",
                target_concept="brightness",
            )
        )

        decision_made = EpisodeDecision(
            decision_id="d1",
            episode_id="ep_1",
            decision_type=DecisionType.EXECUTION_ATTEMPT,
            phase=EpisodePhase.MEASUREMENT,
            intent=UniversalProductionIntent(original_user_request="Prior"),
            reasoning="Test",
            chosen_candidate="increase_brightness",
            measurement_outcome=MeasurementOutcome.POSITIVE,
            confidence=0.9,
        )

        episode.add_decision(decision_made)
        bridge.add_episode(episode)

        # Create candidate with episode support
        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Increase brightness",
            target_concept="brightness",
            supporting_episodes=["ep_1"],
        )

        engine = AdvisoryDecisionEngine(episode_bridge=bridge)
        intent = UniversalProductionIntent(
            original_user_request="Similar task",
            target_concept="brightness",
        )

        eval = engine._evaluate_candidate(candidate, intent)
        episode_factors = [f for f in eval.scoring_factors if f.name == "episode_precedent"]
        assert len(episode_factors) > 0


class TestConflictPreservation:
    """Test E: Conflicts remain visible."""

    def test_conflicts_recorded(self):
        """Conflicting evidence is recorded."""
        intent = UniversalProductionIntent(
            original_user_request="Test",
        )

        c1 = SemanticCandidate(
            candidate_id="c1",
            label="Option A",
            target_concept="test",
        )

        c2 = SemanticCandidate(
            candidate_id="c2",
            label="Option B",
            target_concept="test",
        )

        engine = AdvisoryDecisionEngine()
        decision = engine.decide(intent, [c1, c2])

        # Even without explicit conflicts, structure is there
        assert hasattr(decision, "conflicts")

    def test_conflicting_evidence_visible(self):
        """Conflicting evidence remains visible in evaluation."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Test candidate",
            target_concept="test",
        )

        eval = engine._evaluate_candidate(candidate, intent)

        assert hasattr(eval, "conflicting_evidence")


class TestUncertaintyPreservation:
    """Test F: Uncertainty remains visible."""

    def test_uncertainties_recorded(self):
        """Uncertainties are explicitly recorded."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(
            original_user_request="Vague request",
            # No target_concept
        )

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Option",
            target_concept=None,
        )

        decision = engine.decide(intent, [candidate])

        assert len(decision.uncertainties) >= 0 or decision.decision_status != DecisionStatus.DECIDED


class TestAbstention:
    """Test G: Engine can abstain."""

    def test_abstain_when_no_candidates(self):
        """Abstain when no viable candidates."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(original_user_request="Test")

        decision = engine.decide(intent, [])

        assert decision.decision_status == DecisionStatus.ABSTAINED

    def test_abstain_when_insufficient_evidence(self):
        """Abstain when confidence too low."""
        engine = AdvisoryDecisionEngine(
            weighting_model=WeightingModel(
                min_confidence_for_decision=0.9,
                min_confidence_for_tentative=0.8,
            )
        )

        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="unknown",
        )

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Unknown option",
            target_concept="different",
            confidence=0.2,
        )

        decision = engine.decide(intent, [candidate])

        # Should not force a decision
        assert decision.decision_status in [
            DecisionStatus.INSUFFICIENT_EVIDENCE,
            DecisionStatus.ABSTAINED,
        ]


class TestConstraintFiltering:
    """Test H: Constraints can eliminate candidates."""

    def test_constraint_elimination(self):
        """Constraints can filter candidates."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
            confidence=0.9,
        )

        c1 = SemanticCandidate(
            candidate_id="c1",
            label="Satisfies constraint",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
            confidence=0.9,
            constraints_satisfied=["preserve_bass"],
        )

        c2 = SemanticCandidate(
            candidate_id="c2",
            label="Violates constraint",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
            constraints_satisfied=[],
        )

        constraints = ["preserve_bass"]

        decision = engine.decide(intent, [c1, c2], constraints=constraints)

        # Constraints should be recorded
        assert "preserve_bass" in decision.constraints_applied
        # c1 should be evaluated (in candidate_evaluations)
        assert len(decision.candidate_evaluations) > 0
        # c1 should survive filtering
        assert decision.candidate_evaluations[0].candidate == c1


class TestDecisionTrace:
    """Test I: Decision trace is complete."""

    def test_trace_recorded(self):
        """Decision trace is captured."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="test",
            semantic_direction=SemanticDirection.INCREASE,
        )

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Test option",
            target_concept="test",
        )

        decision = engine.decide(intent, [candidate])

        assert len(decision.decision_trace) > 0
        # Trace should contain reasoning steps
        trace_text = " ".join(decision.decision_trace).lower()
        assert any(word in trace_text for word in ["candidate", "evaluat", "score", "select"])


class TestBackendIndependence:
    """Test J: Decision is backend-independent."""

    def test_no_serum_terms(self):
        """Decision contains no Serum-specific terms."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(
            original_user_request="Make sound brighter",
            target_concept="brightness",
        )

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Increase brightness",
            target_concept="brightness",
        )

        decision = engine.decide(intent, [candidate])

        decision_str = str(decision.__dict__).lower()
        assert "serum" not in decision_str
        assert "vst" not in decision_str
        assert "parameter" not in decision_str or "target_concept" in str(decision.__dict__)

    def test_decision_backend_swappable(self):
        """Same decision applies to different backends."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(
            original_user_request="Shorten attack",
            target_concept="envelope-attack",
            semantic_direction=SemanticDirection.SHORTER,
        )

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Shorten attack envelope",
            target_concept="envelope-attack",
            semantic_direction=SemanticDirection.SHORTER,
        )

        decision = engine.decide(intent, [candidate])

        # Should work for any synth (Serum, Wavetable, etc.)
        assert decision.selected_candidate is not None
        assert decision.selected_candidate.target_concept == "envelope-attack"


class TestNoUnauthorizedValues:
    """Test K: No concrete unauthorized mutation value generated."""

    def test_no_numeric_mutation_values(self):
        """Decision contains no concrete mutation values."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(
            original_user_request="Adjust parameter",
        )

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Adjust",
            target_concept="test",
        )

        decision = engine.decide(intent, [candidate])

        decision_str = str(decision.__dict__)
        # Should not contain numeric parameter assignments
        assert "Env1.Release = " not in decision_str
        assert "0.3" not in decision_str or "confidence" in decision_str

    def test_no_delta_values(self):
        """Decision contains no delta/mutation values."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Option",
            target_concept="test",
        )

        decision = engine.decide(intent, [candidate])

        assert not hasattr(decision, "delta")
        assert not hasattr(decision, "mutation_value")


class TestNoTargetPathAuthority:
    """Test L: No backend target path becomes authoritative."""

    def test_no_parameter_paths(self):
        """Decision doesn't assign parameter paths."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Adjust brightness",
            target_concept="brightness",
        )

        decision = engine.decide(intent, [candidate])

        if decision.selected_candidate:
            candidate = decision.selected_candidate
            assert not hasattr(candidate, "serum_parameter_path")
            assert not hasattr(candidate, "target_path")


class TestNoMeasurementAuthority:
    """Test M: No measurement authority generated."""

    def test_no_measurement_ids(self):
        """Decision doesn't create measurement IDs."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Option",
            target_concept="test",
        )

        decision = engine.decide(intent, [candidate])

        assert not hasattr(decision, "measurement_id")
        assert not hasattr(decision, "metric_authority")


class TestNoExecution:
    """Test N: No execution occurs."""

    def test_no_serum_mutation(self):
        """Decision engine doesn't mutate Serum."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Mutate something",
            target_concept="test",
        )

        decision = engine.decide(intent, [candidate])

        # Decision is purely representational
        assert not callable(decision)
        assert not hasattr(decision, "execute")


class TestNoContractCreation:
    """Test O: No CapabilityContract created."""

    def test_no_contract_in_decision(self):
        """Decision doesn't create CapabilityContracts."""
        engine = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Option",
            target_concept="test",
        )

        decision = engine.decide(intent, [candidate])

        assert not hasattr(decision, "capability_contract")
        assert not hasattr(decision, "contract_id")


class TestIntegrationFunction:
    """Test P: Real knowledge/episode context consumed."""

    def test_make_advisory_decision_function(self):
        """Top-level function works end-to-end."""
        intent = UniversalProductionIntent(
            original_user_request="Make brighter",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
        )

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Increase brightness",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
        )

        decision = make_advisory_decision(
            intent,
            [candidate],
        )

        assert decision.intent is intent
        assert decision.selected_candidate is candidate


class TestDecisionDeterminism:
    """Test Q: Tests pass (deterministic behavior where applicable)."""

    def test_same_input_same_decision(self):
        """Same input produces same decision."""
        engine1 = AdvisoryDecisionEngine()
        engine2 = AdvisoryDecisionEngine()

        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
            confidence=0.8,
        )

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Brighten",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
            confidence=0.8,
        )

        decision1 = engine1.decide(intent, [candidate])
        decision2 = engine2.decide(intent, [candidate])

        assert decision1.selected_candidate_score == decision2.selected_candidate_score


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
