"""
Test suite for Step 6.2 Universal Production Intent Model.

Tests prove:
  - Backend independence
  - Ambiguity preservation
  - Provenance tracking
  - Separation of concerns (intent ≠ target ≠ authority)
  - Compatibility with existing ProducerGoal
"""

import pytest
from step_6_2_universal_production_intent import (
    UniversalProductionIntent,
    UniversalIntentResolver,
    IntentResolutionStatus,
    SemanticDirection,
    MusicalRole,
    MusicalContext,
    AmbiguityInfo,
    intent_to_producer_goal_requirements,
)


class TestUniversalIntentModel:
    """Test the canonical universal production intent model."""

    def test_intent_creation_basic(self):
        """Create a simple intent."""
        intent = UniversalProductionIntent(
            original_user_request="Make the bass tighter",
            musical_objective="tighter bass articulation",
            desired_change="shorter note tail",
        )

        assert intent.is_valid()
        assert intent.original_user_request == "Make the bass tighter"
        assert intent.musical_objective == "tighter bass articulation"

    def test_intent_backend_independent(self):
        """Intent should not contain backend terms."""
        intent = UniversalProductionIntent(
            original_user_request="Make it warmer",
            target_concept="brightness",
            semantic_direction=SemanticDirection.BRIGHTER,
        )

        # Should not have Serum-specific fields
        assert "Env1" not in str(intent.to_dict())
        assert "Release" not in str(intent.to_dict())
        assert "parameter" not in str(intent.to_dict()).lower()

    def test_intent_preserves_ambiguity(self):
        """Ambiguity should be explicitly marked."""
        ambiguity = AmbiguityInfo(
            is_ambiguous=True,
            candidate_interpretations=["brightness", "saturation"],
            reason="'warmer' could mean multiple things",
        )

        intent = UniversalProductionIntent(
            original_user_request="Make it warmer",
            ambiguity=ambiguity,
            resolution_status=IntentResolutionStatus.AMBIGUOUS,
        )

        assert intent.ambiguity is not None
        assert intent.ambiguity.is_ambiguous
        assert len(intent.ambiguity.candidate_interpretations) > 0

    def test_intent_with_role_context(self):
        """Intent can include role and context."""
        intent = UniversalProductionIntent(
            original_user_request="Make the bass tighter",
            musical_objective="tighter bass articulation",
            role=MusicalRole.BASS,
            musical_context=MusicalContext.ELECTRONIC,
        )

        assert intent.role == MusicalRole.BASS
        assert intent.musical_context == MusicalContext.ELECTRONIC

    def test_intent_serializes_correctly(self):
        """Intent should serialize to dict without None fields."""
        intent = UniversalProductionIntent(
            original_user_request="Make the bass tighter",
            musical_objective="tighter articulation",
            target_concept="release",
        )

        data = intent.to_dict()

        # Should not have None values
        assert None not in data.values()
        # Should have the key fields
        assert "original_user_request" in data
        assert "musical_objective" in data

    def test_intent_separate_from_target(self):
        """Intent objective ≠ backend target path."""
        intent = UniversalProductionIntent(
            original_user_request="Make the bass tighter",
            target_concept="note-release",  # Universal concept
            musical_objective="shorter note tail",
        )

        # Intent should NOT specify:
        # - Env1.Release (backend target)
        # - 0.3 (concrete value)
        # - meas_release_tight_bass (measurement ID)

        intent_dict = intent.to_dict()
        intent_str = str(intent_dict)

        assert "Env1" not in intent_str
        assert "Release" not in intent_str or "note-release" in intent_str

    def test_intent_does_not_control_measurement(self):
        """Intent verification_goal ≠ authoritative measurement."""
        intent = UniversalProductionIntent(
            original_user_request="Make the note stop sooner",
            target_concept="note-release",
            verification_goal="shorter tail",  # User's aspiration
        )

        # This is NOT a measurement authority field
        # Actual measurement comes from CapabilityContract later
        assert intent.verification_goal == "shorter tail"
        assert not hasattr(intent, "measurement_id")
        assert not hasattr(intent, "metric_authority")

    def test_intent_does_not_specify_mutation_value(self):
        """Intent should not encode concrete mutation values."""
        intent = UniversalProductionIntent(
            original_user_request="Make the bass tighter",
            semantic_direction=SemanticDirection.SHORTER,  # Semantic, not numeric
        )

        # Should NOT have:
        # - magnitude: 0.05
        # - mutation_value: 0.3
        # - delta: -0.2

        intent_dict = intent.to_dict()
        assert "magnitude" not in intent_dict or intent_dict.get("magnitude") is None
        assert "mutation_value" not in intent_dict

    def test_resolver_basic(self):
        """Test intent resolver on simple case."""
        resolver = UniversalIntentResolver()

        intent = resolver.resolve_from_text("Make the bass sound shorter")

        assert intent.is_valid()
        assert intent.resolution_status == IntentResolutionStatus.RESOLVED
        assert intent.confidence > 0.5

    def test_resolver_with_role(self):
        """Resolver respects role hint."""
        resolver = UniversalIntentResolver()

        intent = resolver.resolve_from_text(
            "Make it tighter",
            role=MusicalRole.BASS
        )

        assert intent.role == MusicalRole.BASS

    def test_resolver_ambiguous(self):
        """Resolver marks ambiguous intent."""
        resolver = UniversalIntentResolver()

        intent = resolver.resolve_from_text("Make it sound better")

        # Should be marked ambiguous
        assert intent.resolution_status == IntentResolutionStatus.AMBIGUOUS
        assert intent.confidence < 0.5

    def test_resolver_longer_sustain(self):
        """Test sustain lengthening."""
        resolver = UniversalIntentResolver()

        intent = resolver.resolve_from_text("Make the pad sustain longer")

        assert intent.target_concept == "note-sustain"
        assert intent.semantic_direction == SemanticDirection.LONGER
        assert intent.operation == "lengthen"

    def test_resolver_brightness(self):
        """Test brightness adjustment."""
        resolver = UniversalIntentResolver()

        intent = resolver.resolve_from_text("Make the sound brighter")

        assert intent.target_concept == "brightness"
        assert intent.semantic_direction == SemanticDirection.BRIGHTER
        assert intent.operation == "increase"

    def test_intent_to_producer_goal_requirements(self):
        """Test compatibility bridge to ProducerGoal."""
        intent = UniversalProductionIntent(
            original_user_request="Make the bass tighter",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
            confidence=0.8,
        )

        reqs = intent_to_producer_goal_requirements(intent)

        assert reqs["confidence"] == 0.8
        assert reqs["suggested_metric_direction"] == "lower_is_better"  # shorter is better

    def test_intent_authority_separation(self):
        """Intent cannot authorize execution."""
        intent = UniversalProductionIntent(
            original_user_request="Make the bass tighter",
            musical_objective="tighter bass",
        )

        # Intent should not have authority-related fields
        assert not hasattr(intent, "capability_contract_id")
        assert not hasattr(intent, "admission_authorized")
        assert not hasattr(intent, "execution_command")

    def test_multiple_interpretations(self):
        """Ambiguous intent can hold multiple interpretations."""
        ambiguity = AmbiguityInfo(
            is_ambiguous=True,
            candidate_interpretations=[
                "increase spectral brightness via filter cutoff",
                "add saturation for warmth",
                "shift tone with filter resonance",
            ],
            reason="'warmer' in music production context is multi-dimensional",
        )

        intent = UniversalProductionIntent(
            original_user_request="Make it warmer",
            ambiguity=ambiguity,
            resolution_status=IntentResolutionStatus.AMBIGUOUS,
        )

        assert len(intent.ambiguity.candidate_interpretations) == 3

    def test_intent_without_role(self):
        """Intent without role context is still valid."""
        intent = UniversalProductionIntent(
            original_user_request="Shorten the release",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        assert intent.is_valid()
        assert intent.role is None  # Optional

    def test_backend_hint_non_authoritative(self):
        """Backend hint is advisory, not authoritative."""
        intent = UniversalProductionIntent(
            original_user_request="Make the bass tighter",
            target_concept="note-release",
            backend_hint="Serum",  # Suggested backend
        )

        # Hint should be preserved but not be authoritative
        assert intent.backend_hint == "Serum"
        # Should not determine execution
        assert not hasattr(intent, "authorized_backend")

    def test_intent_without_semantic_direction(self):
        """Intent can exist without explicit semantic direction."""
        intent = UniversalProductionIntent(
            original_user_request="Change the envelope",
            target_concept="envelope",
        )

        assert intent.is_valid()
        assert intent.semantic_direction is None

    def test_serialization_roundtrip(self):
        """Intent should serialize/deserialize correctly."""
        intent1 = UniversalProductionIntent(
            original_user_request="Make the bass tighter",
            musical_objective="tighter bass",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
            role=MusicalRole.BASS,
            confidence=0.85,
        )

        data = intent1.to_dict()

        # Create new intent from dict
        intent2 = UniversalProductionIntent(
            original_user_request=data["original_user_request"],
            musical_objective=data.get("musical_objective"),
            target_concept=data.get("target_concept"),
            confidence=data.get("confidence", 0.5),
        )

        assert intent2.original_user_request == intent1.original_user_request
        assert intent2.confidence == intent1.confidence


class TestUniversalityProof:
    """Prove backend independence."""

    def test_intent_meaningful_without_serum(self):
        """Intent is meaningful even without Serum context."""
        intent = UniversalProductionIntent(
            original_user_request="Make the bass articulation tighter",
            musical_objective="tighter bass articulation",
            desired_change="shorter note tail",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        # Should be understandable to non-Serum users
        assert "note" in intent.desired_change.lower()
        assert "release" in intent.target_concept.lower()
        assert intent.semantic_direction == SemanticDirection.SHORTER

        # Works without any Serum references
        intent_dict = intent.to_dict()
        intent_str = str(intent_dict).lower()
        assert "serum" not in intent_str
        assert "vst" not in intent_str

    def test_intent_survives_backend_swap(self):
        """Same intent could apply to any synth backend."""
        # Create intent for generic synth
        intent = UniversalProductionIntent(
            original_user_request="Shorten the attack",
            target_concept="envelope-attack",
            semantic_direction=SemanticDirection.SHORTER,
        )

        # Should work for:
        # - Serum (Env1.Attack)
        # - Wavetable (Env.Attack)
        # - Sylenth1 (Amp Env Attack)
        # - Any synth with attack control

        assert intent.target_concept == "envelope-attack"  # Universal
        assert "serum" not in str(intent.to_dict()).lower()


class TestBoundaryProof:
    """Prove separation from authority."""

    def test_intent_cannot_authorize(self):
        """Intent cannot become authority."""
        intent = UniversalProductionIntent(
            original_user_request="Shorten release",
        )

        # Intent is advisory
        assert not hasattr(intent, "authorization_status")
        assert not hasattr(intent, "capability_contract")
        assert not hasattr(intent, "admits_execution")

    def test_intent_separate_from_measurement(self):
        """Intent verification ≠ measurement authority."""
        intent = UniversalProductionIntent(
            original_user_request="Make it tighter",
            verification_goal="tighter feel",
        )

        # Verification goal is user's hope, not measurement spec
        assert intent.verification_goal == "tighter feel"
        assert not hasattr(intent, "measurement_id")
        assert not hasattr(intent, "metric_authority")

    def test_intent_produces_no_mutation(self):
        """Intent alone cannot mutate state."""
        intent = UniversalProductionIntent(
            original_user_request="Change the sound",
            target_concept="brightness",
        )

        # Intent is purely representational
        assert not hasattr(intent, "execute")
        assert not hasattr(intent, "apply")
        assert not hasattr(intent, "mutate")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
