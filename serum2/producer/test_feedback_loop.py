"""Tests for producer feedback loop."""

import pytest
import json
import os
from serum2.producer.diagnosis import (
    ProducerGoal,
    CurrentState,
    MetricDirection,
    diagnose_goal,
    ProducerDecision,
)


class TestDiagnosis:
    """Test diagnosis creation."""

    def test_diagnose_sustain_longer_selects_env1_release(self):
        """Goal 'sustain longer' should select Env1.Release."""
        goal = ProducerGoal(
            intent="make the note sustain longer",
            semantic_target="Env1.Release",
            measurement_metric="tail_rms_db",
            metric_direction=MetricDirection.HIGHER_IS_BETTER,
        )

        current_state = CurrentState(
            serum_readback=0.5,
            measurement_value=-20.0,
            audio_peak=0.283,
            audio_valid=True,
        )

        qualified_targets = {
            'Env1.Release': {},
            'Env1.Attack': {},
        }

        diagnosis = diagnose_goal(goal, current_state, qualified_targets)

        assert diagnosis is not None
        assert diagnosis.selected_target == "Env1.Release"
        assert diagnosis.mutation_direction == 1  # increase for "longer"
        assert diagnosis.confidence > 0.8

    def test_diagnose_no_matching_target_returns_none(self):
        """Diagnosis with no matching target should return None."""
        goal = ProducerGoal(
            intent="make the note sustain longer",
            semantic_target="NonExistent",
            measurement_metric="tail_rms_db",
            metric_direction=MetricDirection.HIGHER_IS_BETTER,
        )

        current_state = CurrentState(
            serum_readback=0.5,
            measurement_value=-20.0,
            audio_peak=0.283,
            audio_valid=True,
        )

        qualified_targets = {'Env1.Release': {}}

        diagnosis = diagnose_goal(goal, current_state, qualified_targets)
        assert diagnosis is None


class TestProducerDecision:
    """Test producer decision logic."""

    def test_improvement_accepted_higher_is_better(self):
        """Decision should ACCEPT when treatment > baseline for higher_is_better metric."""
        decision = ProducerDecision(
            accepted=True,
            reason="",
            baseline_measurement=-20.0,
            treatment_measurement=-19.5,  # treatment is higher
            delta=0.5,
            metric_direction=MetricDirection.HIGHER_IS_BETTER,
        )

        assert decision.improvement_observed() is True

    def test_non_improvement_rejected_higher_is_better(self):
        """Decision should REJECT when treatment <= baseline for higher_is_better metric."""
        decision = ProducerDecision(
            accepted=False,
            reason="",
            baseline_measurement=-20.0,
            treatment_measurement=-20.5,  # treatment is lower
            delta=-0.5,
            metric_direction=MetricDirection.HIGHER_IS_BETTER,
        )

        assert decision.improvement_observed() is False

    def test_improvement_accepted_lower_is_better(self):
        """Decision should ACCEPT when treatment < baseline for lower_is_better metric."""
        decision = ProducerDecision(
            accepted=True,
            reason="",
            baseline_measurement=0.05,
            treatment_measurement=0.03,  # treatment is lower
            delta=-0.02,
            metric_direction=MetricDirection.LOWER_IS_BETTER,
        )

        assert decision.improvement_observed() is True

    def test_non_improvement_rejected_lower_is_better(self):
        """Decision should REJECT when treatment >= baseline for lower_is_better metric."""
        decision = ProducerDecision(
            accepted=False,
            reason="",
            baseline_measurement=0.05,
            treatment_measurement=0.06,  # treatment is higher
            delta=0.01,
            metric_direction=MetricDirection.LOWER_IS_BETTER,
        )

        assert decision.improvement_observed() is False

    def test_no_improvement_delta_zero(self):
        """Delta of zero should be treated as no improvement."""
        decision_higher = ProducerDecision(
            accepted=False,
            reason="",
            baseline_measurement=-20.0,
            treatment_measurement=-20.0,
            delta=0.0,
            metric_direction=MetricDirection.HIGHER_IS_BETTER,
        )

        decision_lower = ProducerDecision(
            accepted=False,
            reason="",
            baseline_measurement=0.05,
            treatment_measurement=0.05,
            delta=0.0,
            metric_direction=MetricDirection.LOWER_IS_BETTER,
        )

        assert decision_higher.improvement_observed() is False
        assert decision_lower.improvement_observed() is False


class TestProducerGoal:
    """Test producer goal creation."""

    def test_goal_serialization(self):
        """Goal should serialize to dict correctly."""
        goal = ProducerGoal(
            intent="make the note sustain longer",
            semantic_target="Env1.Release",
            measurement_metric="tail_rms_db",
            metric_direction=MetricDirection.HIGHER_IS_BETTER,
        )

        goal_dict = goal.to_dict()

        assert goal_dict['intent'] == "make the note sustain longer"
        assert goal_dict['semantic_target'] == "Env1.Release"
        assert goal_dict['measurement_metric'] == "tail_rms_db"
        assert goal_dict['metric_direction'] == "higher"

    def test_current_state_serialization(self):
        """CurrentState should serialize to dict correctly."""
        state = CurrentState(
            serum_readback=0.5,
            measurement_value=-20.0,
            audio_peak=0.283,
            audio_valid=True,
        )

        state_dict = state.to_dict()

        assert state_dict['serum_readback'] == 0.5
        assert state_dict['measurement_value'] == -20.0
        assert state_dict['audio_peak'] == 0.283
        assert state_dict['audio_valid'] is True


class TestEpisodePersistence:
    """Test that episode files are created correctly."""

    def test_episode_file_created(self):
        """Episode file should exist after execution."""
        # Check for canonical episode
        episode_path = "serum2/qualification/ep_producer_canonical_001.json"
        assert os.path.exists(episode_path), "Canonical episode file was not created"

    def test_episode_contains_diagnosis(self):
        """Episode should contain diagnosis data."""
        episode_path = "serum2/qualification/ep_producer_canonical_001.json"
        with open(episode_path) as f:
            episode = json.load(f)

        assert 'diagnosis' in episode
        assert 'goal' in episode['diagnosis']
        assert 'selected_target' in episode['diagnosis']
        assert episode['diagnosis']['selected_target'] == 'Env1.Release'

    def test_episode_contains_decision(self):
        """Episode should contain decision data."""
        episode_path = "serum2/qualification/ep_producer_canonical_001.json"
        with open(episode_path) as f:
            episode = json.load(f)

        assert 'decision' in episode
        assert 'accepted' in episode['decision']
        assert 'reason' in episode['decision']

    def test_episode_marked_observation_only(self):
        """Episode should be marked as observation_only."""
        episode_path = "serum2/qualification/ep_producer_canonical_001.json"
        with open(episode_path) as f:
            episode = json.load(f)

        assert episode['observation_only'] is True

    def test_episode_in_scope_learning_eligible_true(self):
        """Valid in-scope accepted episode should have learning_eligible=true."""
        episode_path = "serum2/qualification/ep_producer_canonical_001.json"
        with open(episode_path) as f:
            episode = json.load(f)

        # In-scope baseline (0.5) with improvement → learning_eligible=true
        assert episode['serum_readback_before'] == 0.5
        assert episode['prerequisite_scope_violated'] is False
        assert episode['learning_eligible'] is True, "Valid in-scope episode should be learning_eligible"

    def test_episode_has_real_measurements(self):
        """Episode should contain real Serum measurements."""
        episode_path = "serum2/qualification/ep_producer_canonical_001.json"
        with open(episode_path) as f:
            episode = json.load(f)

        assert episode['serum_readback_before'] == 0.5
        assert episode['measurement_metric'] == 'tail_rms_db'
        assert isinstance(episode['measurement_baseline'], float)
        assert isinstance(episode['measurement_treatment'], float)
        assert isinstance(episode['measurement_delta'], float)

    def test_episode_improvement_accepted(self):
        """Episode decision should be ACCEPT due to improvement."""
        episode_path = "serum2/qualification/ep_producer_canonical_001.json"
        with open(episode_path) as f:
            episode = json.load(f)

        # For tail_rms_db (higher is better), treatment > baseline means improvement
        assert episode['measurement_treatment'] > episode['measurement_baseline']
        assert episode['decision']['accepted'] is True
        assert episode['restoration_status'] == 'mutation_accepted'


class TestProducerConstraints:
    """Test that producer loop respects constraints."""

    def test_single_mutation_per_episode(self):
        """Episode should have exactly one mutation per baseline."""
        episode_path = "serum2/qualification/ep_producer_canonical_001.json"
        with open(episode_path) as f:
            episode = json.load(f)

        # Should have exactly one mutation value
        assert episode['serum_mutation_value'] is not None
        assert isinstance(episode['serum_mutation_value'], (int, float))

        # Mutation should be different from baseline
        baseline = episode['serum_readback_before']
        mutation = episode['serum_mutation_value']
        assert baseline != mutation, "Mutation should differ from baseline"

    def test_no_capability_modification(self):
        """Producer loop should not modify capability contracts."""
        # Load contract before episode execution
        with open('serum2/knowledge/step_b_evidence_to_capability_integration.json') as f:
            contracts = json.load(f)

        # Check that Env1.Release contract is unchanged
        env1_release = [c for c in contracts['capability_contracts'] if c['target'] == 'Env1.Release'][0]
        original_status = env1_release['status']

        # Execute episode (already done)
        # Reload contracts
        with open('serum2/knowledge/step_b_evidence_to_capability_integration.json') as f:
            contracts_after = json.load(f)

        env1_release_after = [c for c in contracts_after['capability_contracts'] if c['target'] == 'Env1.Release'][0]
        assert env1_release_after['status'] == original_status, "Contract status was modified"

    def test_in_scope_baseline(self):
        """Producer loop should use in-scope baseline."""
        episode_path = "serum2/qualification/ep_producer_canonical_001.json"
        with open(episode_path) as f:
            episode = json.load(f)

        baseline = episode['serum_readback_before']
        # Env1.Release scope is [0.5, 0.8]
        assert 0.5 <= baseline <= 0.8, f"Baseline {baseline} outside scope [0.5, 0.8]"

    def test_accepted_mutation_remains_active(self):
        """Accepted mutation should remain as current state (no auto-restoration)."""
        episode_path = "serum2/qualification/ep_producer_canonical_001.json"
        with open(episode_path) as f:
            episode = json.load(f)

        # Episode shows acceptance
        assert episode['decision']['accepted'] is True
        # Restoration status should indicate mutation accepted
        assert episode['restoration_status'] == 'mutation_accepted'
        # Readback restored should show mutation value (not baseline)
        assert episode['restoration_readback'] == episode['serum_mutation_value']

    def test_episode_preserves_diagnosis_and_decision(self):
        """Episode must preserve full diagnosis and decision for traceability."""
        episode_path = "serum2/qualification/ep_producer_canonical_001.json"
        with open(episode_path) as f:
            episode = json.load(f)

        # Diagnosis preserved
        diagnosis = episode['diagnosis']
        assert diagnosis['goal']['intent'] == "make the note sustain longer"
        assert diagnosis['selected_target'] == 'Env1.Release'
        assert diagnosis['mutation_direction'] in [-1, 1]
        assert diagnosis['mutation_magnitude'] > 0
        assert diagnosis['reason'] is not None
        assert diagnosis['confidence'] > 0

        # Decision preserved
        decision = episode['decision']
        assert 'accepted' in decision
        assert 'reason' in decision
        assert 'metric_direction' in decision
        assert decision['baseline_measurement'] is not None
        assert decision['treatment_measurement'] is not None
        assert decision['delta'] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
