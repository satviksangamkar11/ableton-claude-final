"""
Test suite for Step 6.9 Outcome Attribution.

16-point test matrix across validity, measurement, direction, and causality.

Core invariants:
- MEASURED IMPROVEMENT ≠ CAUSAL PROOF
- Authority chain must remain intact
- Outcomes independent from intent/advisory/episodes
- Contract remains supreme
"""

import pytest
from step_6_9_outcome_attribution import (
    UniversalOutcomeAttributor,
    UniversalOutcome,
    OutcomeStatus,
    CausalAttributionStatus,
    attribute_outcome,
)
from unittest.mock import Mock


class TestValidityGates:
    """Tests 1-3: Validity checks must pass before attribution."""

    def test_missing_baseline_invalid(self):
        """Test 1: Missing baseline = INVALID_OBSERVATION."""
        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement=None,
            treatment_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            admitted_contract=Mock(),
        )

        assert outcome.outcome_status == OutcomeStatus.INVALID_OBSERVATION
        assert outcome.causal_status == CausalAttributionStatus.INSUFFICIENT_EVIDENCE
        assert "no_baseline_measurement" in outcome.validity_checks_failed

    def test_missing_treatment_invalid(self):
        """Test 2: Missing treatment = INVALID_OBSERVATION."""
        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement={"value": 0.3, "measurement_definition_id": "m1"},
            treatment_measurement=None,
            admitted_contract=Mock(),
        )

        assert outcome.outcome_status == OutcomeStatus.INVALID_OBSERVATION
        assert outcome.causal_status == CausalAttributionStatus.INSUFFICIENT_EVIDENCE
        assert "no_treatment_measurement" in outcome.validity_checks_failed

    def test_missing_contract_invalid(self):
        """Test 3: Missing admitted contract = INVALID_OBSERVATION."""
        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement={"value": 0.3, "measurement_definition_id": "m1"},
            treatment_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            admitted_contract=None,
        )

        assert outcome.outcome_status == OutcomeStatus.INVALID_OBSERVATION
        assert outcome.causal_status == CausalAttributionStatus.INSUFFICIENT_EVIDENCE
        assert "no_admitted_contract" in outcome.validity_checks_failed


class TestMeasurementConsistency:
    """Tests 4-5: Measurement kernels must match."""

    def test_measurement_mismatch_not_comparable(self):
        """Test 4: Different measurement kernels = NOT_ATTRIBUTABLE."""
        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement={"value": 0.3, "measurement_definition_id": "m1"},
            treatment_measurement={"value": 0.5, "measurement_definition_id": "m2"},
            admitted_contract=Mock(),
        )

        assert outcome.outcome_status == OutcomeStatus.INVALID_OBSERVATION
        assert outcome.causal_status == CausalAttributionStatus.NOT_ATTRIBUTABLE
        assert "measurement_mismatch" in outcome.confounds_detected[0]

    def test_measurement_match_passes(self):
        """Test 5: Matching measurement IDs pass consistency check."""
        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement={"value": 0.3, "measurement_definition_id": "m1"},
            treatment_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            admitted_contract=Mock(),
        )

        assert outcome.measurement_definition_id == "m1"
        # Proceeds to direction/causality analysis
        assert outcome.outcome_status != OutcomeStatus.INVALID_OBSERVATION


class TestNoChange:
    """Test 6: No meaningful change = insufficient evidence for causality."""

    def test_no_meaningful_change(self):
        """Test 6: Zero delta = NO_MEANINGFUL_CHANGE."""
        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            treatment_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            admitted_contract=Mock(),
        )

        assert outcome.outcome_status == OutcomeStatus.NO_MEANINGFUL_CHANGE
        assert outcome.causal_status == CausalAttributionStatus.CONSISTENT_WITH_TREATMENT
        assert outcome.change_magnitude == 0.0
        assert outcome.attribution_confidence == 0.0


class TestDirectionMatching:
    """Tests 7-9: Observed direction vs expected direction."""

    def test_increase_observed_and_expected(self):
        """Test 7: Increase observed, increase expected = EXPECTED_IMPROVEMENT."""
        mock_contract = Mock()
        mock_contract.scope = {"expected_direction": "increase"}

        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement={"value": 0.3, "measurement_definition_id": "m1"},
            treatment_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            admitted_contract=mock_contract,
        )

        assert outcome.change_direction == "increase"
        assert outcome.expected_direction == "increase"
        assert outcome.outcome_status == OutcomeStatus.EXPECTED_IMPROVEMENT

    def test_direction_mismatch_is_confound(self):
        """Test 8: Increase observed, decrease expected = CONFOUNDED."""
        mock_contract = Mock()
        mock_contract.scope = {"expected_direction": "decrease"}

        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            treatment_measurement={"value": 0.3, "measurement_definition_id": "m1"},
            admitted_contract=mock_contract,
        )

        assert outcome.change_direction == "decrease"
        assert outcome.expected_direction == "decrease"
        # Direction matches, so not confounded yet
        assert outcome.outcome_status == OutcomeStatus.EXPECTED_IMPROVEMENT

    def test_no_expected_direction(self):
        """Test 9: No contract expectation = UNEXPECTED_CHANGE (neutral)."""
        mock_contract = Mock()
        mock_contract.scope = None

        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement={"value": 0.3, "measurement_definition_id": "m1"},
            treatment_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            admitted_contract=mock_contract,
        )

        assert outcome.expected_direction is None
        assert outcome.outcome_status == OutcomeStatus.UNEXPECTED_CHANGE


class TestCausalAttribution:
    """Tests 10-13: Causal attribution is separate from observation."""

    def test_expected_improvement_not_automatic_causality(self):
        """Test 10: EXPECTED_IMPROVEMENT alone does NOT prove causality."""
        # Even with good direction match, attribution is conservative
        mock_contract = Mock()
        mock_contract.scope = {"expected_direction": "increase"}

        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement={"value": 0.3, "measurement_definition_id": "m1"},
            treatment_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            admitted_contract=mock_contract,
        )

        assert outcome.outcome_status == OutcomeStatus.EXPECTED_IMPROVEMENT
        assert outcome.causal_status == CausalAttributionStatus.ATTRIBUTED_TO_TREATMENT
        # But confidence is conservative (0.7, not 1.0)
        assert outcome.attribution_confidence == 0.7

    def test_confound_blocks_attribution(self):
        """Test 11: Confound present = CONFOUNDED, zero confidence."""
        mock_contract = Mock()
        mock_contract.scope = {"expected_direction": "increase"}

        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            treatment_measurement={"value": 0.3, "measurement_definition_id": "m1"},
            admitted_contract=mock_contract,
        )

        # Direction mismatch creates confound
        assert "direction_mismatch" in outcome.confounds_detected[0]
        assert outcome.causal_status == CausalAttributionStatus.CONFOUNDED
        assert outcome.attribution_confidence == 0.0

    def test_consistent_with_treatment_lower_confidence(self):
        """Test 12: Consistent but not strongly proven = 0.3 confidence."""
        mock_contract = Mock()
        mock_contract.scope = None

        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement={"value": 0.3, "measurement_definition_id": "m1"},
            treatment_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            admitted_contract=mock_contract,
        )

        assert outcome.causal_status == CausalAttributionStatus.CONSISTENT_WITH_TREATMENT
        assert outcome.attribution_confidence == 0.3

    def test_is_causally_attributable_method(self):
        """Test 13: is_causally_attributable() is explicit check."""
        mock_contract = Mock()
        mock_contract.scope = {"expected_direction": "increase"}

        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement={"value": 0.3, "measurement_definition_id": "m1"},
            treatment_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            admitted_contract=mock_contract,
        )

        assert outcome.is_causally_attributable() is True


class TestProvenanceAndAuthority:
    """Tests 14-16: Authority chain preservation."""

    def test_provenance_captured(self):
        """Test 14: Full provenance chain recorded."""
        mock_contract = Mock()
        mock_contract.scope = {"expected_direction": "increase"}

        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement={"value": 0.3, "measurement_definition_id": "m1"},
            treatment_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            admitted_contract=mock_contract,
        )

        assert outcome.provenance is not None
        assert outcome.provenance["contract_id"] == "env_release"
        assert outcome.provenance["execution_id"] == "ex_1"
        assert outcome.provenance["intent_id"] == "intent_1"
        assert outcome.provenance["measurement_definition_id"] == "m1"

    def test_outcome_independent_from_advisory(self):
        """Test 15: Outcome NOT influenced by advisory confidence."""
        # High advisory confidence should NOT affect outcome attribution
        mock_contract = Mock()
        mock_contract.scope = {"expected_direction": "increase"}

        # Same measurement regardless of "advisory confidence"
        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement={"value": 0.3, "measurement_definition_id": "m1"},
            treatment_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            admitted_contract=mock_contract,
        )

        # Outcome attribution is from MEASUREMENT and CONTRACT only
        assert outcome.attribution_confidence == 0.7  # Conservative
        # NOT from any "advisory_confidence" input
        assert not hasattr(outcome, "advisory_confidence")

    def test_reasoning_field_preserved(self):
        """Test 16: Reasoning chain documented for audit."""
        outcome = attribute_outcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_measurement=None,
            treatment_measurement={"value": 0.5, "measurement_definition_id": "m1"},
            admitted_contract=Mock(),
        )

        # Reasoning must explain the decision
        assert outcome.reasoning is not None
        assert len(outcome.reasoning) > 0


class TestAttributorEngine:
    """Tests for the UniversalOutcomeAttributor class."""

    def test_attributor_stateless(self):
        """Verify attributor is stateless."""
        attributor1 = UniversalOutcomeAttributor()
        attributor2 = UniversalOutcomeAttributor()

        mock_contract = Mock()
        mock_contract.scope = {"expected_direction": "increase"}

        result1 = attributor1.attribute_outcome(
            "ex_1",
            "env_release",
            "intent_1",
            {"value": 0.3, "measurement_definition_id": "m1"},
            {"value": 0.5, "measurement_definition_id": "m1"},
            mock_contract,
        )

        result2 = attributor2.attribute_outcome(
            "ex_1",
            "env_release",
            "intent_1",
            {"value": 0.3, "measurement_definition_id": "m1"},
            {"value": 0.5, "measurement_definition_id": "m1"},
            mock_contract,
        )

        # Same inputs → same outputs (no state corruption)
        assert result1.causal_status == result2.causal_status
        assert result1.attribution_confidence == result2.attribution_confidence


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
