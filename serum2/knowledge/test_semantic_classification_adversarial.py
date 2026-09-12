"""
STEP 5.4-Q ADVERSARIAL CLASSIFICATION TEST SET

Universal semantic classification tests.

These tests verify that classification is based on semantic function,
not permissive keyword heuristics.

Includes cases where keywords and semantic function disagree.
"""

import pytest
from step_5_4_q_semantic_contract import classify_semantic


class TestSemanticClassification:
    """Adversarial tests for semantic classification."""

    # =====================================================================
    # CONCEPT TESTS
    # =====================================================================

    def test_concept_definition_decay(self):
        """Decay definition should be CONCEPT, not PROCEDURE."""
        text = "Decay is the amount of time it takes the amplitude to reach the sustain level."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONCEPT", f"Got {result['classification']}"

    def test_concept_definition_release(self):
        """Release definition should be CONCEPT."""
        text = "Release is the time from key release to silence."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONCEPT"

    def test_concept_definition_arpeggiator(self):
        """Arpeggiator definition should be CONCEPT."""
        text = "An arpeggiator takes chords and sequences them into melodies."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONCEPT"

    def test_concept_definition_lfo(self):
        """LFO definition should be CONCEPT."""
        text = "An LFO is a low-frequency oscillator that repeats cyclically."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONCEPT"

    # =====================================================================
    # PROCEDURE TESTS
    # =====================================================================

    def test_procedure_imperative_sequence(self):
        """Imperative sequence should be PROCEDURE."""
        text = "Click the oscillator, then select a saw wave."
        result = classify_semantic(text, [])
        assert result["classification"] == "PROCEDURE"

    def test_procedure_click_and_drag(self):
        """Click-and-drag instruction should be PROCEDURE."""
        text = "Click and drag the cutoff slider to the right."
        result = classify_semantic(text, [])
        assert result["classification"] == "PROCEDURE"

    def test_procedure_first_then(self):
        """First... then... sequence should be PROCEDURE."""
        text = "First, open the filter menu. Then drag the cutoff down."
        result = classify_semantic(text, [])
        assert result["classification"] == "PROCEDURE"

    def test_procedure_to_verb(self):
        """'To verb' instruction should be PROCEDURE."""
        text = "To create a tighter pluck, set the release shorter."
        result = classify_semantic(text, [])
        assert result["classification"] == "PROCEDURE"

    def test_procedure_set_verb(self):
        """Direct 'set' instruction should be PROCEDURE."""
        text = "Set the attack time to 0 for immediate response."
        result = classify_semantic(text, [])
        assert result["classification"] == "PROCEDURE"

    # =====================================================================
    # PRINCIPLE TESTS
    # =====================================================================

    def test_principle_causal_shorter_release(self):
        """Causal statement should be PRINCIPLE, not PROCEDURE."""
        text = "Shorter release creates tighter articulation."
        result = classify_semantic(text, [])
        assert result["classification"] == "PRINCIPLE", f"Got {result['classification']}"

    def test_principle_signal_flow(self):
        """Signal flow explanation should be PRINCIPLE."""
        text = "The signal passes through generators, then filters, then effects."
        result = classify_semantic(text, [])
        assert result["classification"] == "PRINCIPLE"

    def test_principle_envelope_behavior(self):
        """Behavioral principle should be PRINCIPLE."""
        text = "Envelopes behave the same way when modulating any parameter."
        result = classify_semantic(text, [])
        assert result["classification"] == "PRINCIPLE"

    def test_principle_filter_mechanism(self):
        """Mechanism explanation should be PRINCIPLE."""
        text = "Filters remove frequencies to shape tone."
        result = classify_semantic(text, [])
        assert result["classification"] == "PRINCIPLE"

    def test_principle_lfo_vs_envelope(self):
        """Comparative principle should be PRINCIPLE."""
        text = "LFOs repeat cyclically; envelopes play once per note."
        result = classify_semantic(text, [])
        assert result["classification"] == "PRINCIPLE"

    # =====================================================================
    # OBSERVATION TESTS
    # =====================================================================

    def test_observation_there_is_not_procedure(self):
        """'There is' statement should be OBSERVATION, not PROCEDURE."""
        text = "There is a delay effect included in Serum."
        result = classify_semantic(text, [])
        assert result["classification"] == "OBSERVATION"

    def test_observation_you_can_not_procedure(self):
        """'You can' capability statement should be OBSERVATION, not PROCEDURE."""
        text = "You can save effects as presets."
        result = classify_semantic(text, [])
        assert result["classification"] == "OBSERVATION"

    def test_observation_contains(self):
        """'Contains' statement should be OBSERVATION."""
        text = "Serum contains three main sound generators."
        result = classify_semantic(text, [])
        assert result["classification"] == "OBSERVATION"

    def test_observation_provides(self):
        """'Provides' statement should be OBSERVATION."""
        text = "The UI provides easy access to all major controls."
        result = classify_semantic(text, [])
        assert result["classification"] == "OBSERVATION"

    def test_observation_i_notice(self):
        """First-person observation should be OBSERVATION."""
        text = "I notice that longer releases sound smoother."
        result = classify_semantic(text, [])
        assert result["classification"] == "OBSERVATION"

    # =====================================================================
    # RECOMMENDATION TESTS
    # =====================================================================

    def test_recommendation_i_recommend(self):
        """'I recommend' should be RECOMMENDATION."""
        text = "I recommend starting with saw waves."
        result = classify_semantic(text, [])
        assert result["classification"] == "RECOMMENDATION"

    def test_recommendation_try(self):
        """'Try' suggestion should be RECOMMENDATION."""
        text = "Try a shorter release for tighter plucks."
        result = classify_semantic(text, [])
        assert result["classification"] == "RECOMMENDATION"

    def test_recommendation_consider(self):
        """'Consider' suggestion should be RECOMMENDATION."""
        text = "Consider using a low-pass filter first."
        result = classify_semantic(text, [])
        assert result["classification"] == "RECOMMENDATION"

    def test_recommendation_for_music_type(self):
        """'For X use Y' recommendation should be RECOMMENDATION."""
        text = "For smooth bass, use longer releases."
        result = classify_semantic(text, [])
        # This could be CONDITION or RECOMMENDATION
        assert result["classification"] in ["RECOMMENDATION", "CONDITION"]

    # =====================================================================
    # CONDITION TESTS
    # =====================================================================

    def test_condition_for_plucks(self):
        """'For X' scope statement should be CONDITION."""
        text = "For plucks, shorter releases work better."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONDITION"

    def test_condition_when_soloing(self):
        """'When' scope statement should be CONDITION."""
        text = "When soloing, increase the cutoff frequency."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONDITION"

    def test_condition_if_statement(self):
        """'If' conditional should be CONDITION."""
        text = "If you want a brighter tone, use a saw wave."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONDITION"

    def test_condition_unless(self):
        """'Unless' conditional should be CONDITION."""
        text = "Unless the envelope is very long, it will sound tight."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONDITION"

    # =====================================================================
    # EXAMPLE TESTS
    # =====================================================================

    def test_example_for_example(self):
        """'For example' should be EXAMPLE."""
        text = "For example, a saw wave provides brightness."
        result = classify_semantic(text, [])
        assert result["classification"] == "EXAMPLE"

    def test_example_such_as(self):
        """'Such as' should be EXAMPLE."""
        text = "Effects such as delay and reverb add space."
        result = classify_semantic(text, [])
        assert result["classification"] == "EXAMPLE"

    def test_example_like(self):
        """'Like' illustration should be EXAMPLE."""
        text = "Like a string resonator, this creates harmonic feedback."
        result = classify_semantic(text, [])
        assert result["classification"] == "EXAMPLE"

    # =====================================================================
    # CONTEXT TESTS
    # =====================================================================

    def test_context_biographical(self):
        """Biographical statement should be CONTEXT."""
        text = "After teaching Serum for over 10 years, I decided to create this course."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONTEXT", f"Got {result['classification']}"

    def test_context_credentials(self):
        """Credentialing statement should be CONTEXT."""
        text = "Being one of the sound designers who worked on Serum 2, I have deep knowledge."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONTEXT"

    def test_context_transition(self):
        """Transitional statement should be CONTEXT."""
        text = "Next, let's look at the filters in detail."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONTEXT"

    def test_context_summary(self):
        """Summary statement should be CONTEXT."""
        text = "So to summarize, the signal flow goes through generators, filters, and effects."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONTEXT"

    def test_context_framing(self):
        """Framing statement should be CONTEXT."""
        text = "In this section, we'll explore modulation techniques."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONTEXT"

    # =====================================================================
    # LIMITATION TESTS
    # =====================================================================

    def test_limitation_dont(self):
        """'Don't' statement should be LIMITATION."""
        text = "Don't use extreme resonance settings on vocals."
        result = classify_semantic(text, [])
        assert result["classification"] == "LIMITATION"

    def test_limitation_avoid(self):
        """'Avoid' statement should be LIMITATION."""
        text = "Avoid stacking too many effects in series."
        result = classify_semantic(text, [])
        assert result["classification"] == "LIMITATION"

    def test_limitation_cannot(self):
        """'Cannot' statement should be LIMITATION."""
        text = "You cannot use more than 8 effect slots."
        result = classify_semantic(text, [])
        assert result["classification"] == "LIMITATION"

    def test_limitation_limited(self):
        """'Limited' statement should be LIMITATION."""
        text = "This mode is limited to monophonic playback."
        result = classify_semantic(text, [])
        assert result["classification"] == "LIMITATION"

    # =====================================================================
    # FILLER TESTS
    # =====================================================================

    def test_filler_subscribe(self):
        """Subscribe request should be FILLER."""
        text = "Please subscribe to the channel."
        result = classify_semantic(text, [])
        assert result["classification"] == "FILLER"

    def test_filler_thanks_for_watching(self):
        """Outro should be FILLER."""
        text = "Thanks for watching this tutorial."
        result = classify_semantic(text, [])
        assert result["classification"] == "FILLER"

    def test_filler_click_link(self):
        """Navigation should be FILLER."""
        text = "Click the link below for more info."
        result = classify_semantic(text, [])
        assert result["classification"] == "FILLER"

    # =====================================================================
    # ADVERSARIAL CASES
    # =====================================================================

    def test_adversarial_you_can_hear_is_observation_not_procedure(self):
        """'You can hear' should be OBSERVATION, not PROCEDURE."""
        text = "You can hear that the oscillator provides the fundamental frequency."
        result = classify_semantic(text, [])
        # Should not be PROCEDURE
        assert result["classification"] != "PROCEDURE"
        assert result["classification"] in ["OBSERVATION", "PRINCIPLE"]

    def test_adversarial_set_with_purpose_is_procedure(self):
        """'Set... to achieve X' should be PROCEDURE."""
        text = "Set the filter cutoff to 5000 Hz to remove harshness."
        result = classify_semantic(text, [])
        assert result["classification"] == "PROCEDURE"

    def test_adversarial_this_is_could_be_concept_or_observation(self):
        """'This is' could be CONCEPT or OBSERVATION depending on meaning."""
        text = "This is the modulation matrix."
        result = classify_semantic(text, [])
        # Both CONCEPT (definition) and OBSERVATION (feature) are defensible
        assert result["classification"] in ["CONCEPT", "OBSERVATION"]

    def test_adversarial_something_affects_is_principle_not_procedure(self):
        """'Something affects' should be PRINCIPLE."""
        text = "Resonance affects the filter peak."
        result = classify_semantic(text, [])
        assert result["classification"] == "PRINCIPLE"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
