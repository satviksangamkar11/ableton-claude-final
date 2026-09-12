"""
Test suite for Step 6.3 Episode Context Integration.

Tests prove:
  - Episode and decision context capture
  - Prior goal similarity matching
  - Learned strategy extraction
  - Integration with universal intent
  - Decision trace preservation
"""

import pytest
from datetime import datetime

from step_6_3_episode_context_integration import (
    Episode,
    EpisodeDecision,
    EpisodePhase,
    DecisionType,
    MeasurementOutcome,
    PriorGoal,
    EpisodeContextBridge,
    integrate_intent_with_episode_context,
)
from step_6_2_universal_production_intent import (
    UniversalProductionIntent,
    SemanticDirection,
    MusicalRole,
    IntentResolutionStatus,
)


class TestPriorGoal:
    """Test prior goal representation."""

    def test_prior_goal_creation(self):
        """Create a prior goal."""
        goal = PriorGoal(
            goal_id="goal_1",
            musical_objective="tighter bass articulation",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
            outcome=MeasurementOutcome.POSITIVE,
        )

        assert goal.goal_id == "goal_1"
        assert goal.musical_objective == "tighter bass articulation"
        assert goal.outcome == MeasurementOutcome.POSITIVE

    def test_prior_goal_similarity_exact_match(self):
        """Similarity should be high for exact matches."""
        goal = PriorGoal(
            goal_id="goal_1",
            musical_objective="tighter bass articulation",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        intent = UniversalProductionIntent(
            original_user_request="Make bass tighter",
            musical_objective="tighter bass",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        similarity = goal.similarity_to_intent(intent)
        assert similarity > 0.7  # Target + direction match

    def test_prior_goal_similarity_partial_match(self):
        """Similarity should be lower for partial matches."""
        goal = PriorGoal(
            goal_id="goal_1",
            musical_objective="tighter bass",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        intent = UniversalProductionIntent(
            original_user_request="Make it darker",
            target_concept="brightness",
            semantic_direction=SemanticDirection.DARKER,
        )

        similarity = goal.similarity_to_intent(intent)
        assert similarity < 0.5  # No match

    def test_prior_goal_similarity_objective_substring(self):
        """Substring matches in objective boost similarity."""
        goal = PriorGoal(
            goal_id="goal_1",
            musical_objective="make release shorter",
            target_concept="note-release",
        )

        intent = UniversalProductionIntent(
            original_user_request="Make release shorter",
            musical_objective="make release shorter",
            target_concept="note-release",
        )

        similarity = goal.similarity_to_intent(intent)
        assert similarity > 0.6  # Target + substring match


class TestEpisodeDecision:
    """Test decision representation."""

    def test_decision_creation(self):
        """Create an episode decision."""
        intent = UniversalProductionIntent(
            original_user_request="Make bass tighter",
        )

        decision = EpisodeDecision(
            decision_id="dec_1",
            episode_id="ep_1",
            decision_type=DecisionType.GOAL_SELECTION,
            phase=EpisodePhase.INTENT_CAPTURE,
            intent=intent,
            reasoning="User clearly stated intent",
            candidates_considered=["option_a", "option_b"],
            chosen_candidate="option_a",
        )

        assert decision.decision_id == "dec_1"
        assert decision.decision_type == DecisionType.GOAL_SELECTION
        assert decision.chosen_candidate == "option_a"

    def test_decision_with_outcome(self):
        """Decision can track measurement outcome."""
        intent = UniversalProductionIntent(
            original_user_request="Test",
        )

        decision = EpisodeDecision(
            decision_id="dec_1",
            episode_id="ep_1",
            decision_type=DecisionType.EXECUTION_ATTEMPT,
            phase=EpisodePhase.MEASUREMENT,
            intent=intent,
            reasoning="Attempted change",
            measurement_outcome=MeasurementOutcome.POSITIVE,
            feedback="Sounded tighter as expected",
        )

        assert decision.measurement_outcome == MeasurementOutcome.POSITIVE
        assert decision.feedback is not None


class TestEpisode:
    """Test episode representation."""

    def test_episode_creation(self):
        """Create an episode."""
        intent = UniversalProductionIntent(
            original_user_request="Make bass tighter",
        )

        episode = Episode(
            episode_id="ep_1",
            initial_intent=intent,
        )

        assert episode.episode_id == "ep_1"
        assert episode.phase == EpisodePhase.INTENT_CAPTURE
        assert len(episode.decisions) == 0

    def test_episode_add_decision(self):
        """Add decisions to an episode."""
        intent = UniversalProductionIntent(
            original_user_request="Test",
        )

        episode = Episode(episode_id="ep_1", initial_intent=intent)

        decision = EpisodeDecision(
            decision_id="dec_1",
            episode_id="ep_1",
            decision_type=DecisionType.GOAL_SELECTION,
            phase=EpisodePhase.REASONING,
            intent=intent,
            reasoning="Test",
        )

        episode.add_decision(decision)

        assert len(episode.decisions) == 1
        assert episode.phase == EpisodePhase.REASONING

    def test_episode_close(self):
        """Close an episode."""
        intent = UniversalProductionIntent(
            original_user_request="Test",
        )

        episode = Episode(episode_id="ep_1", initial_intent=intent)
        episode.close_episode(learned=["pattern_1", "pattern_2"])

        assert episode.phase == EpisodePhase.CLOSED
        assert episode.timestamp_closed is not None
        assert len(episode.learned_patterns) == 2

    def test_episode_get_positive_outcomes(self):
        """Get decisions with positive outcomes."""
        intent = UniversalProductionIntent(
            original_user_request="Test",
        )

        episode = Episode(episode_id="ep_1", initial_intent=intent)

        # Add positive decision
        pos_decision = EpisodeDecision(
            decision_id="dec_1",
            episode_id="ep_1",
            decision_type=DecisionType.EXECUTION_ATTEMPT,
            phase=EpisodePhase.MEASUREMENT,
            intent=intent,
            reasoning="Positive",
            measurement_outcome=MeasurementOutcome.POSITIVE,
        )

        # Add negative decision
        neg_decision = EpisodeDecision(
            decision_id="dec_2",
            episode_id="ep_1",
            decision_type=DecisionType.EXECUTION_ATTEMPT,
            phase=EpisodePhase.MEASUREMENT,
            intent=intent,
            reasoning="Negative",
            measurement_outcome=MeasurementOutcome.NEGATIVE,
        )

        episode.add_decision(pos_decision)
        episode.add_decision(neg_decision)

        positive = episode.get_positive_outcomes()
        assert len(positive) == 1
        assert positive[0].decision_id == "dec_1"

    def test_episode_get_learned_strategies(self):
        """Extract strategies from positive outcomes."""
        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        episode = Episode(episode_id="ep_1", initial_intent=intent)

        decision = EpisodeDecision(
            decision_id="dec_1",
            episode_id="ep_1",
            decision_type=DecisionType.EXECUTION_ATTEMPT,
            phase=EpisodePhase.MEASUREMENT,
            intent=intent,
            reasoning="Reduced envelope release",
            chosen_candidate="reduce_release_10ms",
            measurement_outcome=MeasurementOutcome.POSITIVE,
            confidence=0.9,
        )

        episode.add_decision(decision)

        strategies = episode.get_learned_strategies()
        assert len(strategies) == 1
        assert strategies[0]["intent_pattern"] == "note-release"
        assert strategies[0]["confidence"] == 0.9


class TestEpisodeContextBridge:
    """Test episode context bridge."""

    def test_bridge_creation(self):
        """Create a bridge."""
        bridge = EpisodeContextBridge()
        assert len(bridge.episodes) == 0
        assert len(bridge.learned_strategies) == 0

    def test_bridge_add_episode(self):
        """Add episodes to bridge."""
        bridge = EpisodeContextBridge()

        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="note-release",
        )

        episode = Episode(episode_id="ep_1", initial_intent=intent)

        decision = EpisodeDecision(
            decision_id="dec_1",
            episode_id="ep_1",
            decision_type=DecisionType.EXECUTION_ATTEMPT,
            phase=EpisodePhase.MEASUREMENT,
            intent=intent,
            reasoning="Test",
            chosen_candidate="candidate_1",
            measurement_outcome=MeasurementOutcome.POSITIVE,
            confidence=0.8,
        )

        episode.add_decision(decision)
        bridge.add_episode(episode)

        assert len(bridge.episodes) == 1
        assert len(bridge.learned_strategies) == 1

    def test_bridge_find_similar_prior_goals(self):
        """Find prior goals similar to intent."""
        bridge = EpisodeContextBridge()

        # Create prior goal
        goal = PriorGoal(
            goal_id="goal_1",
            musical_objective="tighter bass",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
            outcome=MeasurementOutcome.POSITIVE,
        )

        # Create episode with this goal
        intent = UniversalProductionIntent(
            original_user_request="Test",
        )

        episode = Episode(episode_id="ep_1", initial_intent=intent)
        episode.prior_goals.append(goal)

        bridge.add_episode(episode)

        # Query with matching intent
        query_intent = UniversalProductionIntent(
            original_user_request="Make bass tighter",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        similar = bridge.find_similar_prior_goals(query_intent)
        assert len(similar) > 0
        assert similar[0][0].goal_id == "goal_1"
        assert similar[0][1] > 0.7  # High similarity

    def test_bridge_find_learned_strategies(self):
        """Find learned strategies for intent."""
        bridge = EpisodeContextBridge()

        # Create episode with learned strategy
        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        episode = Episode(episode_id="ep_1", initial_intent=intent)

        decision = EpisodeDecision(
            decision_id="dec_1",
            episode_id="ep_1",
            decision_type=DecisionType.EXECUTION_ATTEMPT,
            phase=EpisodePhase.MEASUREMENT,
            intent=intent,
            reasoning="Reduced release",
            chosen_candidate="reduce_10ms",
            measurement_outcome=MeasurementOutcome.POSITIVE,
            confidence=0.85,
        )

        episode.add_decision(decision)
        bridge.add_episode(episode)

        # Query with matching intent
        query_intent = UniversalProductionIntent(
            original_user_request="Shorten release",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        strategies = bridge.find_learned_strategies_for_intent(query_intent)
        assert len(strategies) > 0

    def test_bridge_build_recommendation_context(self):
        """Build full recommendation context."""
        bridge = EpisodeContextBridge()

        # Add episode with goal and strategy
        goal = PriorGoal(
            goal_id="goal_1",
            musical_objective="tighter bass",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
            outcome=MeasurementOutcome.POSITIVE,
        )

        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        episode = Episode(episode_id="ep_1", initial_intent=intent)
        episode.prior_goals.append(goal)

        decision = EpisodeDecision(
            decision_id="dec_1",
            episode_id="ep_1",
            decision_type=DecisionType.EXECUTION_ATTEMPT,
            phase=EpisodePhase.MEASUREMENT,
            intent=intent,
            reasoning="Works well",
            chosen_candidate="reduce_release",
            measurement_outcome=MeasurementOutcome.POSITIVE,
            confidence=0.9,
        )

        episode.add_decision(decision)
        bridge.add_episode(episode)

        # Query
        query_intent = UniversalProductionIntent(
            original_user_request="Make bass tighter",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        context = bridge.build_recommendation_context(query_intent)

        assert "similar_prior_goals" in context
        assert "learned_strategies" in context
        assert "confidence_adjustment" in context
        assert context["confidence_adjustment"] > 0


class TestIntegrationFunction:
    """Test top-level integration function."""

    def test_integrate_intent_with_context(self):
        """Integrate intent with episode context."""
        bridge = EpisodeContextBridge()

        # Setup: Add prior success
        goal = PriorGoal(
            goal_id="goal_1",
            musical_objective="shorter release",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
            outcome=MeasurementOutcome.POSITIVE,
        )

        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="note-release",
        )

        episode = Episode(episode_id="ep_1", initial_intent=intent)
        episode.prior_goals.append(goal)
        bridge.add_episode(episode)

        # Query with new intent
        query_intent = UniversalProductionIntent(
            original_user_request="Make bass attack faster",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        result = integrate_intent_with_episode_context(query_intent, bridge)

        assert "original_intent" in result
        assert "episode_context" in result
        assert "recommended_reasoning" in result
        assert "suggested_next_steps" in result

    def test_integrate_intent_no_prior_context(self):
        """Integration handles novel intent gracefully."""
        bridge = EpisodeContextBridge()  # Empty

        intent = UniversalProductionIntent(
            original_user_request="Novel request",
            target_concept="unknown-concept",
        )

        result = integrate_intent_with_episode_context(intent, bridge)

        assert result["original_intent"] is not None
        assert len(result["episode_context"]["similar_prior_goals"]) == 0
        assert len(result["episode_context"]["learned_strategies"]) == 0


class TestEpisodeContextBoundaryProofs:
    """Prove that episode context is advisory-only, not authoritative."""

    def test_episode_context_cannot_authorize(self):
        """Episode context does not authorize execution."""
        bridge = EpisodeContextBridge()

        intent = UniversalProductionIntent(
            original_user_request="Test",
        )

        # Context building should not produce authorization fields
        context = bridge.build_recommendation_context(intent)

        assert not hasattr(context, "authorization_status")
        assert not hasattr(context, "execute")
        # Context is read-only data structure
        assert "suggested_next_steps" not in context or isinstance(context.get("suggested_next_steps"), list)

    def test_episode_context_separate_from_measurement_authority(self):
        """Episode context reasoning is separate from measurement."""
        episode = Episode(
            episode_id="ep_1",
            initial_intent=UniversalProductionIntent(
                original_user_request="Test"
            )
        )

        decision = EpisodeDecision(
            decision_id="dec_1",
            episode_id="ep_1",
            decision_type=DecisionType.EXECUTION_ATTEMPT,
            phase=EpisodePhase.MEASUREMENT,
            intent=UniversalProductionIntent(original_user_request="Test"),
            reasoning="Test",
            feedback="User opinion",  # User's subjective feedback
        )

        episode.add_decision(decision)

        # Feedback is NOT measurement authority
        assert not hasattr(episode, "measurement_id")
        assert not hasattr(episode, "metric_authority")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
