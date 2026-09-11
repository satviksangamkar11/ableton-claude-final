"""Tests for semantic integrity validation (directional + scope)."""

import pytest
import json
import tempfile
import os
from serum2.qualification.execute_vertical_slice import (
    validate_semantic_direction,
    validate_scope_prerequisite,
)


class TestDirectionalConsistency:
    """Test semantic direction validation against capability claims."""

    def test_env1_attack_faster_requires_increase(self):
        """Intent 'make the attack faster' requires parameter INCREASE."""
        valid, error = validate_semantic_direction(
            "make the attack faster",
            "Env1.Attack",
            baseline=0.5,
            mutation=0.6,  # INCREASE
        )
        assert valid is True, f"Should be valid but got error: {error}"

    def test_env1_attack_faster_rejects_decrease(self):
        """Intent 'make the attack faster' rejects parameter DECREASE."""
        valid, error = validate_semantic_direction(
            "make the attack faster",
            "Env1.Attack",
            baseline=0.6,
            mutation=0.5,  # DECREASE - wrong direction
        )
        assert valid is False
        assert "directional mismatch" in error.lower()

    def test_osc1_octave_higher_no_contract(self):
        """Intent 'oscillator one octave higher' with OSC1.Octave (no contract in step_b)."""
        valid, error = validate_semantic_direction(
            "make the oscillator one octave higher",
            "OSC1.Octave",
            baseline=0.5,
            mutation=0.625,
        )
        # OSC1.Octave is not in step_b contracts, so validation should fail
        assert valid is False
        assert "no capability contract" in error.lower()

    def test_env1_release_longer_requires_increase(self):
        """Intent 'note sustain longer' requires parameter INCREASE."""
        valid, error = validate_semantic_direction(
            "make the note sustain longer",
            "Env1.Release",
            baseline=0.2,
            mutation=0.8,  # INCREASE
        )
        assert valid is True, f"Should be valid but got error: {error}"

    def test_direction_validation_requires_contract(self):
        """Direction validation requires an existing capability contract."""
        valid, error = validate_semantic_direction(
            "make the attack faster",
            "NonExistentTarget",
            baseline=0.5,
            mutation=0.6,
        )
        assert valid is False
        assert "no capability contract" in error.lower() or "not found" in error.lower()

    def test_direction_validation_unparseable_intent(self):
        """Direction validation rejects unparseable intent."""
        valid, error = validate_semantic_direction(
            "do something mysterious",
            "Env1.Attack",
            baseline=0.5,
            mutation=0.6,
        )
        assert valid is False
        assert "could not infer" in error.lower()


class TestScopePrerequisiteValidation:
    """Test scope prerequisite validation."""

    def test_env1_attack_baseline_0_5_within_scope(self):
        """Env1.Attack baseline 0.5 is within qualified scope [0.5-0.6]."""
        valid, error, scope_info = validate_scope_prerequisite(
            "Env1.Attack",
            baseline=0.5,
        )
        assert valid is True
        assert scope_info is not None
        assert scope_info['scope_min'] == 0.5
        assert scope_info['scope_max'] == 0.6

    def test_env1_attack_baseline_0_6_within_scope(self):
        """Env1.Attack baseline 0.6 is within qualified scope [0.5-0.6]."""
        valid, error, scope_info = validate_scope_prerequisite(
            "Env1.Attack",
            baseline=0.6,
        )
        assert valid is True

    def test_env1_attack_baseline_0_126_outside_scope(self):
        """Env1.Attack baseline 0.126 is OUTSIDE qualified scope [0.5-0.6]."""
        valid, error, scope_info = validate_scope_prerequisite(
            "Env1.Attack",
            baseline=0.126,
        )
        assert valid is False
        assert "outside qualified scope" in error.lower()
        assert scope_info['baseline'] == 0.126
        assert scope_info['scope_min'] == 0.5
        assert scope_info['scope_max'] == 0.6

    def test_env1_attack_baseline_0_7_outside_scope_high(self):
        """Env1.Attack baseline 0.7 is OUTSIDE qualified scope [0.5-0.6] (too high)."""
        valid, error, scope_info = validate_scope_prerequisite(
            "Env1.Attack",
            baseline=0.7,
        )
        assert valid is False
        assert "outside" in error.lower()

    def test_scope_validation_requires_contract(self):
        """Scope validation requires an existing capability contract."""
        valid, error, scope_info = validate_scope_prerequisite(
            "NonExistentTarget",
            baseline=0.5,
        )
        assert valid is False
        assert "no capability contract" in error.lower() or "not found" in error.lower()

    def test_env1_release_has_scope_restriction(self):
        """Env1.Release has scope limitation [0.5-0.8]."""
        valid, error, scope_info = validate_scope_prerequisite(
            "Env1.Release",
            baseline=0.5,  # Within scope [0.5-0.8]
        )
        assert valid is True
        assert scope_info['scope_min'] == 0.5
        assert scope_info['scope_max'] == 0.8


class TestIntegration:
    """Integration tests combining direction + scope validation."""

    def test_env1_attack_0_5_to_0_6_faster_intent_passes(self):
        """Env1.Attack 0.5->0.6 with 'faster' intent passes both validations."""
        # Scope validation
        scope_valid, scope_error, _ = validate_scope_prerequisite("Env1.Attack", 0.5)
        assert scope_valid is True, f"Scope check failed: {scope_error}"

        # Direction validation
        dir_valid, dir_error = validate_semantic_direction(
            "make the attack faster",
            "Env1.Attack",
            baseline=0.5,
            mutation=0.6,
        )
        assert dir_valid is True, f"Direction check failed: {dir_error}"

    def test_env1_attack_0_126_to_0_6_faster_intent_fails_scope(self):
        """Env1.Attack 0.126->0.6 with 'faster' intent fails scope check."""
        scope_valid, scope_error, _ = validate_scope_prerequisite("Env1.Attack", 0.126)
        assert scope_valid is False
        assert "outside" in scope_error.lower()

    def test_env1_attack_0_5_to_0_4_faster_intent_fails_direction(self):
        """Env1.Attack 0.5->0.4 (DECREASE) with 'faster' intent fails direction check."""
        # Scope passes
        scope_valid, _, _ = validate_scope_prerequisite("Env1.Attack", 0.5)
        assert scope_valid is True

        # Direction fails
        dir_valid, dir_error = validate_semantic_direction(
            "make the attack faster",
            "Env1.Attack",
            baseline=0.5,
            mutation=0.4,  # Wrong direction
        )
        assert dir_valid is False
        assert "directional mismatch" in dir_error.lower()

    def test_env1_release_0_5_to_0_8_longer_intent_passes(self):
        """Env1.Release 0.5->0.8 with 'longer' intent passes both validations."""
        # Scope validation
        scope_valid, scope_error, _ = validate_scope_prerequisite("Env1.Release", 0.5)
        assert scope_valid is True, f"Scope check failed: {scope_error}"

        # Direction validation
        dir_valid, dir_error = validate_semantic_direction(
            "make the note sustain longer",
            "Env1.Release",
            baseline=0.5,
            mutation=0.8,
        )
        assert dir_valid is True, f"Direction check failed: {dir_error}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
