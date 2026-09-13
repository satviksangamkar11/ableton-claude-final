"""
Test suite for Step 6.4 Semantic Reasoning Integration.

Tests prove:
  - Semantic candidate generation
  - Integration with knowledge items
  - Integration with episode context
  - Candidate ranking
  - Reasoning chain preservation
"""

import pytest

from step_6_4_semantic_reasoning_integration import (
    SemanticCandidate,
    SemanticReasoningResult,
    SemanticReasoningEngine,
    CandidateReason,
    CandidateStatus,
    integrate_semantic_reasoning,
)
from step_6_3_episode_context_integration import (
    Episode,
    EpisodeDecision,
    EpisodePhase,
    DecisionType,
    MeasurementOutcome,
    EpisodeContextBridge,
)
from step_6_2_universal_production_intent import (
    UniversalProductionIntent,
    SemanticDirection,
)


class TestSemanticCandidate:
    """Test semantic candidate representation."""

    def test_candidate_creation(self):
        """Create a semantic candidate."""
        candidate = SemanticCandidate(
            candidate_id="cand_1",
            label="Shorten release",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
            confidence=0.85,
        )

        assert candidate.candidate_id == "cand_1"
        assert candidate.label == "Shorten release"
        assert candidate.confidence == 0.85

    def test_candidate_with_risks(self):
        """Candidate can track potential risks."""
        candidate = SemanticCandidate(
            candidate_id="cand_1",
            label="Aggressive EQ boost",
            target_concept="brightness",
            confidence=0.6,
            status=CandidateStatus.RISKY,
            risks=["may cause harshness", "could lose bass"],
        )

        assert candidate.status == CandidateStatus.RISKY
        assert len(candidate.risks) > 0

    def test_candidate_with_constraints(self):
        """Candidate can track constraint satisfaction."""
        candidate = SemanticCandidate(
            candidate_id="cand_1",
            label="Subtle change",
            target_concept="brightness",
            constraints_satisfied=["maintain bass weight", "keep tone natural"],
        )

        assert len(candidate.constraints_satisfied) == 2


class TestSemanticReasoningEngine:
    """Test semantic reasoning engine."""

    def test_engine_creation(self):
        """Create reasoning engine."""
        engine = SemanticReasoningEngine()
        assert len(engine.reasoning_steps) == 0

    def test_engine_with_episode_bridge(self):
        """Engine can use episode context."""
        bridge = EpisodeContextBridge()
        engine = SemanticReasoningEngine(bridge)
        assert engine.episode_bridge is bridge

    def test_reason_about_simple_intent(self):
        """Engine reasons about simple intent."""
        engine = SemanticReasoningEngine()

        intent = UniversalProductionIntent(
            original_user_request="Make the bass tighter",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
            confidence=0.8,
        )

        result = engine.reason_about_intent(intent)

        assert result.intent is intent
        assert len(result.generated_candidates) > 0
        assert len(result.reasoning_chain) > 0

    def test_reason_with_knowledge_items(self):
        """Engine augments with knowledge items."""
        engine = SemanticReasoningEngine()

        intent = UniversalProductionIntent(
            original_user_request="Make brighter",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
        )

        knowledge_items = [
            {
                "id": "know_1",
                "title": "Increase filter cutoff for brightness",
                "target_concept": "brightness",
                "operation": "increase_cutoff",
                "expected_effect": "Higher frequencies more prominent",
            },
            {
                "id": "know_2",
                "title": "Reduce filter resonance to avoid harshness",
                "target_concept": "brightness",
                "operation": "reduce_resonance",
            },
        ]

        result = engine.reason_about_intent(intent, knowledge_items)

        # Should have semantic candidates + knowledge candidates
        assert len(result.generated_candidates) >= 3
        assert any(
            CandidateReason.FROM_KNOWLEDGE in c.source_reasons
            for c in result.generated_candidates
        )

    def test_reason_with_episode_context(self):
        """Engine uses learned patterns from episodes."""
        bridge = EpisodeContextBridge()

        # Setup: learned strategy from prior episode
        intent_base = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="brightness",
        )

        episode = Episode(episode_id="ep_1", initial_intent=intent_base)

        decision = EpisodeDecision(
            decision_id="dec_1",
            episode_id="ep_1",
            decision_type=DecisionType.EXECUTION_ATTEMPT,
            phase=EpisodePhase.MEASUREMENT,
            intent=intent_base,
            reasoning="Boost high frequencies",
            chosen_candidate="boost_highs",
            measurement_outcome=MeasurementOutcome.POSITIVE,
            confidence=0.9,
        )

        episode.add_decision(decision)
        bridge.add_episode(episode)

        # Now reason about new intent
        engine = SemanticReasoningEngine(bridge)

        new_intent = UniversalProductionIntent(
            original_user_request="Make it brighter",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
        )

        result = engine.reason_about_intent(new_intent)

        # Should have context-based candidates
        assert any(
            CandidateReason.FROM_EPISODE_PATTERN in c.source_reasons
            for c in result.generated_candidates
        )

    def test_candidate_ranking(self):
        """Engine ranks candidates by appropriateness."""
        engine = SemanticReasoningEngine()

        intent = UniversalProductionIntent(
            original_user_request="Adjust sound",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
        )

        result = engine.reason_about_intent(intent)

        # Candidates should be ranked
        assert len(result.ranked_candidates) > 0

        # Ranking should be in descending score order
        scores = [score for _, score in result.ranked_candidates]
        assert scores == sorted(scores, reverse=True)

    def test_primary_candidate_selection(self):
        """Engine selects primary candidate."""
        engine = SemanticReasoningEngine()

        intent = UniversalProductionIntent(
            original_user_request="Tighten the sound",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
            confidence=0.9,
        )

        result = engine.reason_about_intent(intent)

        assert result.primary_candidate is not None
        assert result.primary_candidate == result.ranked_candidates[0][0]
        assert result.confidence > 0.5

    def test_reasoning_chain_logged(self):
        """Reasoning steps are captured."""
        engine = SemanticReasoningEngine()

        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        result = engine.reason_about_intent(intent)

        # Should have logged reasoning steps
        assert len(result.reasoning_chain) > 0
        assert any("intent" in step.lower() for step in result.reasoning_chain)

    def test_ambiguous_intent_handling(self):
        """Engine handles ambiguous intent."""
        engine = SemanticReasoningEngine()

        intent = UniversalProductionIntent(
            original_user_request="Make it better",
            # No target_concept specified
        )

        result = engine.reason_about_intent(intent)

        # Should still produce result but with caveats
        assert result.intent is intent
        assert result.ambiguity_resolved == False


class TestRankingLogic:
    """Test candidate ranking logic."""

    def test_ranking_by_confidence(self):
        """Higher confidence candidates ranked higher."""
        engine = SemanticReasoningEngine()

        candidates = [
            SemanticCandidate(
                candidate_id="c1",
                label="Option 1",
                target_concept="test",
                confidence=0.5,
            ),
            SemanticCandidate(
                candidate_id="c2",
                label="Option 2",
                target_concept="test",
                confidence=0.9,
            ),
        ]

        intent = UniversalProductionIntent(original_user_request="Test")

        ranked = engine._rank_candidates(candidates, intent)

        # c2 should be ranked higher (confidence 0.9 > 0.5)
        assert ranked[0][0].candidate_id == "c2"

    def test_ranking_penalizes_risky(self):
        """Risky candidates penalized in ranking."""
        engine = SemanticReasoningEngine()

        candidates = [
            SemanticCandidate(
                candidate_id="c1",
                label="Safe approach",
                target_concept="test",
                confidence=0.8,
                status=CandidateStatus.VIABLE,
            ),
            SemanticCandidate(
                candidate_id="c2",
                label="Risky approach",
                target_concept="test",
                confidence=0.9,  # Higher confidence but risky
                status=CandidateStatus.RISKY,
            ),
        ]

        intent = UniversalProductionIntent(original_user_request="Test")

        ranked = engine._rank_candidates(candidates, intent)

        # c1 should rank higher despite lower confidence
        assert ranked[0][0].candidate_id == "c1"

    def test_ranking_boosts_supported(self):
        """Candidates with knowledge/episode support ranked higher."""
        engine = SemanticReasoningEngine()

        candidates = [
            SemanticCandidate(
                candidate_id="c1",
                label="Unsupported option",
                target_concept="test",
                confidence=0.8,
                supporting_knowledge_ids=[],
            ),
            SemanticCandidate(
                candidate_id="c2",
                label="Well-supported option",
                target_concept="test",
                confidence=0.8,
                supporting_knowledge_ids=["know_1", "know_2"],
                supporting_episodes=["ep_1"],
            ),
        ]

        intent = UniversalProductionIntent(original_user_request="Test")

        ranked = engine._rank_candidates(candidates, intent)

        # c2 should rank higher due to support
        assert ranked[0][0].candidate_id == "c2"


class TestIntegrationFunction:
    """Test top-level integration function."""

    def test_integrate_semantic_reasoning_minimal(self):
        """Top-level integration with minimal input."""
        intent = UniversalProductionIntent(
            original_user_request="Make bass tighter",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        result = integrate_semantic_reasoning(intent)

        assert result.intent is intent
        assert len(result.generated_candidates) > 0
        assert result.primary_candidate is not None

    def test_integrate_with_knowledge(self):
        """Integration with knowledge items."""
        intent = UniversalProductionIntent(
            original_user_request="Make brighter",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
        )

        knowledge = [
            {
                "id": "k1",
                "title": "Increase filter cutoff",
                "target_concept": "brightness",
                "operation": "increase",
            }
        ]

        result = integrate_semantic_reasoning(intent, knowledge_items=knowledge)

        assert len(result.generated_candidates) >= 2  # Semantic + knowledge

    def test_integrate_with_episode_context(self):
        """Integration with episode context bridge."""
        bridge = EpisodeContextBridge()

        # Setup episode with matching target
        base_intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
        )

        episode = Episode(
            episode_id="ep_1",
            initial_intent=base_intent
        )

        decision = EpisodeDecision(
            decision_id="d1",
            episode_id="ep_1",
            decision_type=DecisionType.EXECUTION_ATTEMPT,
            phase=EpisodePhase.MEASUREMENT,
            intent=base_intent,
            reasoning="Boost high frequencies",
            chosen_candidate="approach_1",
            measurement_outcome=MeasurementOutcome.POSITIVE,
            confidence=0.85,
        )

        episode.add_decision(decision)
        bridge.add_episode(episode)

        # Query with matching target
        intent = UniversalProductionIntent(
            original_user_request="Similar task - make brighter",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
        )

        result = integrate_semantic_reasoning(intent, episode_bridge=bridge)

        assert result.primary_candidate is not None


class TestSemanticReasoningBoundaryProofs:
    """Prove semantic reasoning is advisory-only, not authoritative."""

    def test_reasoning_cannot_authorize(self):
        """Semantic reasoning cannot authorize execution."""
        engine = SemanticReasoningEngine()

        intent = UniversalProductionIntent(original_user_request="Test")

        result = engine.reason_about_intent(intent)

        # Result should not have authorization fields
        assert not hasattr(result, "authorization_status")
        assert not hasattr(result, "execute")
        assert not hasattr(result, "admission_gate")

    def test_candidates_separate_from_values(self):
        """Candidates are semantic, not numeric values."""
        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Shorten release",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        # Should NOT contain:
        assert not hasattr(candidate, "mutation_value")
        assert not hasattr(candidate, "target_parameter_id")
        assert not hasattr(candidate, "concrete_measurement")

    def test_reasoning_preserves_uncertainty(self):
        """Reasoning preserves ambiguity rather than resolving it."""
        engine = SemanticReasoningEngine()

        intent = UniversalProductionIntent(
            original_user_request="Make it sound better",
            # Intentionally ambiguous, no target_concept
        )

        result = engine.reason_about_intent(intent)

        # Should acknowledge ambiguity
        assert result.ambiguity_resolved == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
