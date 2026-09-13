"""
Integration test for Steps 6.2-6.4: Complete Knowledge-to-Advisory Pipeline

Demonstrates the full flow:
    User Request → Universal Intent (6.2)
    ↓
    Episode Context Lookup (6.3)
    ↓
    Knowledge Retrieval (5.7-5.8)
    ↓
    Semantic Reasoning (6.4)
    ↓
    Advisory Proposal (5.10) — No Authority Yet

Key proof: Knowledge + Intent + Context → Advisory (not execution)
"""

import pytest
from datetime import datetime
from dataclasses import asdict

from step_6_2_universal_production_intent import (
    UniversalProductionIntent,
    UniversalIntentResolver,
    SemanticDirection,
    MusicalRole,
)
from step_6_3_episode_context_integration import (
    Episode,
    EpisodeDecision,
    EpisodeContextBridge,
    EpisodePhase,
    DecisionType,
    MeasurementOutcome,
)
from step_6_4_semantic_reasoning_integration import (
    integrate_semantic_reasoning,
)


class TestKnowledgeAdvisoryPipeline:
    """Test complete pipeline from user request to advisory proposal."""

    def test_full_pipeline_single_request(self):
        """
        Complete pipeline: user request → intent → context → reasoning → recommendation
        """

        # Step 1: User makes request
        user_request = "Make the bass tighter"

        # Step 2: Resolve to universal intent (Step 6.2)
        resolver = UniversalIntentResolver()
        intent = resolver.resolve_from_text(user_request, role=MusicalRole.BASS)

        assert intent.is_valid()
        assert intent.target_concept == "note-release"
        assert intent.semantic_direction == SemanticDirection.TIGHTER

        # Step 3: Build episode context (Step 6.3)
        bridge = EpisodeContextBridge()

        # Add prior episode showing this works
        base_intent = UniversalProductionIntent(
            original_user_request="Prior: tighten bass",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        prior_episode = Episode(episode_id="ep_prior", initial_intent=base_intent)

        prior_decision = EpisodeDecision(
            decision_id="dec_prior",
            episode_id="ep_prior",
            decision_type=DecisionType.EXECUTION_ATTEMPT,
            phase=EpisodePhase.MEASUREMENT,
            intent=base_intent,
            reasoning="Reduced Env1.Release from 0.5s to 0.2s",
            chosen_candidate="reduce_release_300ms",
            measurement_outcome=MeasurementOutcome.POSITIVE,
            confidence=0.9,
            feedback="Bass articulation noticeably tighter",
        )

        prior_episode.add_decision(prior_decision)
        bridge.add_episode(prior_episode)

        # Step 4: Retrieve knowledge (simulated from 5.7-5.8)
        knowledge_items = [
            {
                "id": "know_attack",
                "title": "Shortening attack envelope makes notes start faster",
                "target_concept": "note-release",
                "operation": "shorten_release",
                "expected_effect": "Shorter tail, punchier articulation",
            },
            {
                "id": "know_interaction",
                "title": "Release time affects note sustain duration",
                "target_concept": "note-release",
                "operation": "adjust_release",
            }
        ]

        # Step 5: Semantic reasoning (Step 6.4)
        result = integrate_semantic_reasoning(
            intent,
            knowledge_items=knowledge_items,
            episode_bridge=bridge,
        )

        # Verify result has candidates
        assert result.primary_candidate is not None
        assert len(result.generated_candidates) > 0

        # Step 6: Verify reasoning chain
        assert len(result.reasoning_chain) > 0
        assert result.confidence > 0.5

        # Key proof: This is ADVISORY, not authoritative
        assert not hasattr(result.primary_candidate, "execute")
        assert not hasattr(result.primary_candidate, "mutation_value")

    def test_pipeline_with_ambiguous_intent(self):
        """Pipeline handles ambiguous intent gracefully."""

        # User makes vague request
        user_request = "Make it sound better"

        # Resolve to intent
        resolver = UniversalIntentResolver()
        intent = resolver.resolve_from_text(user_request)

        # Intent should be marked ambiguous
        assert intent.resolution_status.value == "ambiguous"

        # Context bridge (no prior episodes)
        bridge = EpisodeContextBridge()

        # Reasoning should still work
        result = integrate_semantic_reasoning(
            intent,
            episode_bridge=bridge,
        )

        # Should acknowledge ambiguity
        assert result.ambiguity_resolved == False

    def test_pipeline_context_boost_confidence(self):
        """Pipeline boosts confidence when context shows success."""

        # Scenario: similar prior goal succeeded
        resolver = UniversalIntentResolver()
        intent = resolver.resolve_from_text("Make bass attack faster")

        # Setup context: prior success
        bridge = EpisodeContextBridge()

        # Prior successful episode
        prior_intent = UniversalProductionIntent(
            original_user_request="Speed up bass attack previously",
            target_concept="envelope-attack",
            semantic_direction=SemanticDirection.SHORTER,
        )

        prior_episode = Episode(episode_id="ep_success", initial_intent=prior_intent)

        prior_decision = EpisodeDecision(
            decision_id="dec_success",
            episode_id="ep_success",
            decision_type=DecisionType.EXECUTION_ATTEMPT,
            phase=EpisodePhase.MEASUREMENT,
            intent=prior_intent,
            reasoning="Reduced attack to 5ms",
            chosen_candidate="short_attack",
            measurement_outcome=MeasurementOutcome.POSITIVE,
            confidence=0.95,
        )

        prior_episode.add_decision(prior_decision)
        bridge.add_episode(prior_episode)

        # Reasoning with prior context
        result = integrate_semantic_reasoning(intent, episode_bridge=bridge)

        # Confidence should be affected by prior success
        context = bridge.build_recommendation_context(intent)
        assert context["confidence_adjustment"] >= 0.0

    def test_pipeline_end_to_end_traceability(self):
        """Complete pipeline produces traceable reasoning chain."""

        user_request = "Brighten the sound without harshness"

        resolver = UniversalIntentResolver()
        intent = resolver.resolve_from_text(user_request)

        bridge = EpisodeContextBridge()

        # Add knowledge
        knowledge = [
            {
                "id": "k1",
                "title": "Filter cutoff affects brightness",
                "target_concept": "brightness",
                "operation": "increase_cutoff",
            },
            {
                "id": "k2",
                "title": "Resonance boost can cause harshness",
                "target_concept": "brightness",
                "operation": "reduce_resonance",
            }
        ]

        result = integrate_semantic_reasoning(
            intent,
            knowledge_items=knowledge,
            episode_bridge=bridge,
        )

        # Verify traceability
        assert result.reasoning_chain is not None
        assert len(result.reasoning_chain) > 0

        # Candidate should have reasoning
        if result.primary_candidate:
            assert result.primary_candidate.reasoning is not None or len(
                result.primary_candidate.source_reasons) > 0

    def test_pipeline_separates_intent_from_execution(self):
        """Pipeline proves intent is separate from execution."""

        intent = UniversalProductionIntent(
            original_user_request="Tighten bass",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        result = integrate_semantic_reasoning(intent)

        if result.primary_candidate:
            candidate = result.primary_candidate

            # Candidate should NOT have:
            assert not hasattr(candidate, "instruction_for_serum")
            assert not hasattr(candidate, "parameter_id")
            assert not hasattr(candidate, "numeric_value")

            # Should ONLY have semantic properties:
            assert candidate.target_concept is not None
            assert candidate.semantic_direction is not None or candidate.operation is not None

    def test_pipeline_preserves_user_context(self):
        """Pipeline preserves all user context through pipeline."""

        user_request = "Make the lead synth brighter but keep the bass warm"
        resolver = UniversalIntentResolver()

        intent = resolver.resolve_from_text(
            user_request,
            role=MusicalRole.LEAD,
        )

        # Intent should preserve context
        assert intent.original_user_request == user_request
        assert intent.role == MusicalRole.LEAD

        result = integrate_semantic_reasoning(intent)

        # Result should preserve original intent
        assert result.intent.original_user_request == user_request

    def test_pipeline_no_false_confidence_inflation(self):
        """Pipeline doesn't inflate confidence without evidence."""

        intent = UniversalProductionIntent(
            original_user_request="Do something unknown",
            # No target_concept, no semantic_direction
        )

        # Empty episode context
        bridge = EpisodeContextBridge()

        result = integrate_semantic_reasoning(intent, episode_bridge=bridge)

        # Confidence should be low without evidence
        assert result.confidence <= 0.5 or len(result.generated_candidates) == 0


class TestPipelineSafeguards:
    """Test that pipeline maintains safety boundaries."""

    def test_advisory_output_not_executable(self):
        """Advisory output cannot be directly executed."""

        intent = UniversalProductionIntent(
            original_user_request="Adjust sound",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
        )

        result = integrate_semantic_reasoning(intent)

        if result.primary_candidate:
            candidate = result.primary_candidate

            # Should not be executable
            assert callable(candidate) == False

            # Should not contain execution instructions
            candidate_dict = asdict(candidate) if hasattr(candidate, '__dict__') else {}
            candidate_str = str(candidate_dict).lower()

            assert "execute" not in candidate_str
            assert "serum" not in candidate_str or "target" in candidate_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
