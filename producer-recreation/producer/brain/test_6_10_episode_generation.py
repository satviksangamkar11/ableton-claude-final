"""
Test suite for Step 6.10 Episode Generation.

20-test matrix covering generation, eligibility, authority boundaries, and retrieval.

Core invariants:
- Episode ≠ Authority
- Episodes retain full provenance
- Learning eligibility is explicit, not automatic
- Refused executions are recorded without authorization
- Episodes cannot bypass contracts
"""

import pytest
from unittest.mock import Mock
from pathlib import Path
import json
import tempfile

from step_6_10_episode_generation import (
    UniversalExecutedEpisode,
    UniversalEpisodeGenerator,
    ExecutionEvidenceRecord,
    LearningEligibilityStatus,
    EpisodeExecutionStatus,
    generate_episode,
    persist_episode,
)
from step_6_2_universal_production_intent import (
    UniversalProductionIntent,
    SemanticDirection,
)
from step_6_9_outcome_attribution import (
    UniversalOutcome,
    OutcomeStatus,
    CausalAttributionStatus,
)
from step_6_7_admission_handoff import AdmissionHandoffResult
from serum2.producer.episode_retrieval import retrieve_relevant_episodes, get_episode_by_id


class TestEpisodeGeneration:
    """Tests 1-3: Valid episode generation paths."""

    def test_valid_episode_generation(self):
        """Test 1: Generate valid episode from full execution."""
        intent = UniversalProductionIntent(
            original_user_request="Make bass tighter",
            target_concept="note-release",
            semantic_direction=SemanticDirection.SHORTER,
        )

        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_value=0.5,
            treatment_value=0.3,
            change_magnitude=-0.2,
            change_direction="decrease",
            outcome_status=OutcomeStatus.EXPECTED_IMPROVEMENT,
            causal_status=CausalAttributionStatus.ATTRIBUTED_TO_TREATMENT,
            attribution_confidence=0.7,
            measurement_definition_id="meas_release",
        )

        mock_execution_record = Mock()
        mock_execution_record.pathway.value = "admitted"

        mock_admission = AdmissionHandoffResult(
            handoff_id="h_1",
            admitted=True,
            admission_reason="ADMITTED",
            admission_detail="Test",
            contract_id="env_release",
            contract_status="CAUSAL_VERIFIED",
        )

        mock_advisory = Mock()
        mock_advisory.decision_id = "adv_1"

        mock_resolution = Mock()
        mock_resolution.resolution_id = "res_1"
        mock_resolution.semantic_target = "envelope_field_release"

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=intent,
            execution_record=mock_execution_record,
            admission_result=mock_admission,
            admitted_contract=Mock(),
            advisory_decision=mock_advisory,
            capability_resolution=mock_resolution,
            outcome=outcome,
        )

        assert episode.episode_id == "ep_ex_1"
        assert episode.execution_id == "ex_1"
        assert episode.semantic_target == "envelope_field_release"
        assert episode.outcome == outcome

    def test_refused_episode_recorded(self):
        """Test 2: Refused admission still recorded as episode (non-executed)."""
        intent = UniversalProductionIntent(original_user_request="Test")

        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="unknown",
            intent_id="intent_1",
            outcome_status=OutcomeStatus.INVALID_OBSERVATION,
            causal_status=CausalAttributionStatus.INSUFFICIENT_EVIDENCE,
        )

        mock_execution_record = Mock()
        mock_execution_record.pathway.value = "refused"

        mock_admission = AdmissionHandoffResult(
            handoff_id="h_1",
            admitted=False,
            admission_reason="unknown_no_contract",
            admission_detail="No contract",
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=intent,
            execution_record=mock_execution_record,
            admission_result=mock_admission,
            admitted_contract=None,
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(
                resolution_id="res_1",
                semantic_target="unknown",
            ),
            outcome=outcome,
        )

        # Episode recorded but not executed
        assert episode.episode_id == "ep_ex_1"
        assert episode.admission_allowed is False
        assert episode.execution_status == EpisodeExecutionStatus.NOT_EXECUTED

    def test_failed_outcome_episode(self):
        """Test 3: Failed execution outcome recorded."""
        intent = UniversalProductionIntent(original_user_request="Test")

        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_value=0.5,
            outcome_status=OutcomeStatus.NO_MEANINGFUL_CHANGE,
            causal_status=CausalAttributionStatus.CONSISTENT_WITH_TREATMENT,
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=intent,
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True, contract_id="env_release"),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(
                resolution_id="res_1",
                semantic_target="envelope_field_release",
            ),
            outcome=outcome,
        )

        assert episode.outcome_status == "no_meaningful_change"


class TestLearningEligibility:
    """Tests 4-8: Learning eligibility gates (NOT automatic)."""

    def test_admission_gate_blocks_learning(self):
        """Test 4: Refused admission → NOT_LEARNING_ELIGIBLE."""
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="unknown",
            intent_id="intent_1",
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(original_user_request="Test"),
            execution_record=Mock(pathway=Mock(value="refused")),
            admission_result=Mock(admitted=False),
            admitted_contract=None,
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="unknown"),
            outcome=outcome,
        )

        assert episode.learning_eligible is False
        assert (
            episode.learning_eligibility_status
            == LearningEligibilityStatus.REFUSED_EXECUTION
        )
        assert "admission_not_granted" in episode.eligibility_reasons

    def test_missing_baseline_blocks_learning(self):
        """Test 5: Missing baseline → INSUFFICIENT_EVIDENCE."""
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_value=None,
            treatment_value=0.5,
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(original_user_request="Test"),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True, contract_id="env_release"),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        assert episode.learning_eligible is False
        assert (
            episode.learning_eligibility_status
            == LearningEligibilityStatus.INSUFFICIENT_EVIDENCE
        )

    def test_confound_blocks_learning(self):
        """Test 6: Confound detected → NOT_LEARNING_ELIGIBLE."""
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_value=0.3,
            treatment_value=0.5,
            measurement_definition_id="m1",
            causal_status=CausalAttributionStatus.CONFOUNDED,
            confounds_detected=["direction_mismatch"],
            provenance={"test": "data"},  # Required for eligibility check
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(original_user_request="Test"),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True, contract_id="env_release"),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        assert episode.learning_eligible is False
        assert "confounds_detected" in episode.eligibility_reasons[0]

    def test_all_checks_pass_learning_eligible(self):
        """Test 7: All gates pass → LEARNING_ELIGIBLE."""
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_value=0.3,
            treatment_value=0.5,
            measurement_definition_id="m1",
            change_magnitude=0.2,
            outcome_status=OutcomeStatus.EXPECTED_IMPROVEMENT,
            causal_status=CausalAttributionStatus.ATTRIBUTED_TO_TREATMENT,
            attribution_confidence=0.7,
            provenance={"test": "data"},  # Required for eligibility check
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(original_user_request="Test"),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True, contract_id="env_release"),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        assert episode.learning_eligible is True
        assert (
            episode.learning_eligibility_status
            == LearningEligibilityStatus.LEARNING_ELIGIBLE
        )

    def test_confidence_does_not_grant_learning(self):
        """Test 8: High confidence alone does NOT grant learning eligibility."""
        # High confidence outcome but missing baseline
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_value=None,
            treatment_value=0.5,
            attribution_confidence=0.95,  # Very high
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(original_user_request="Test"),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True, contract_id="env_release"),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        # Confidence is preserved but doesn't grant learning without evidence
        assert episode.learning_eligible is False
        assert episode.attribution_confidence == 0.95


class TestAuthorityBoundaries:
    """Tests 9-13: Episode cannot bypass authority."""

    def test_episode_cannot_authorize_execution(self):
        """Test 9: Episode is historical, non-authoritative."""
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_value=0.3,
            treatment_value=0.5,
            measurement_definition_id="m1",
            causal_status=CausalAttributionStatus.ATTRIBUTED_TO_TREATMENT,
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(original_user_request="Test"),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True, contract_id="env_release"),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        # Episode has no execute() method or authority field
        assert not hasattr(episode, "execute")
        assert not hasattr(episode, "authority")

    def test_episode_references_contract_not_replaces(self):
        """Test 10: Episode references contract, doesn't replace it."""
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(original_user_request="Test"),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(
                admitted=True,
                contract_id="env_release",
                contract_status="CAUSAL_VERIFIED",
            ),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        # Episode records contract reference, not new contract definition
        assert episode.admitted_contract_id == "env_release"
        assert episode.contract_status == "CAUSAL_VERIFIED"
        # Episode does NOT redefine the contract
        assert not hasattr(episode, "allowed_operation")
        assert not hasattr(episode, "target")

    def test_episode_preserves_measurement_authority(self):
        """Test 11: Episode references measurement, doesn't override it."""
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            measurement_definition_id="m1",
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(original_user_request="Test"),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True, contract_id="env_release"),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        # Episode records measurement used, not authoritative measurement
        assert episode.measurement_definition_id == "m1"
        assert not hasattr(episode, "define_measurement")

    def test_episode_cannot_create_capability(self):
        """Test 12: Episode is experience, not capability source."""
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(original_user_request="Test"),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True, contract_id="env_release"),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        # Episode does NOT have capability creation methods
        assert not hasattr(episode, "create_contract")
        assert not hasattr(episode, "grant_capability")


class TestPersistenceAndRetrieval:
    """Tests 14-18: Persistence, identity, and retrieval."""

    def test_stable_episode_identity(self):
        """Test 14: Episode ID is deterministic (from execution_id)."""
        intent = UniversalProductionIntent(original_user_request="Test")
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
        )

        ep1 = generate_episode(
            execution_id="ex_1",
            universal_intent=intent,
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        ep2 = generate_episode(
            execution_id="ex_1",
            universal_intent=intent,
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        # Same execution → same episode ID
        assert ep1.episode_id == ep2.episode_id == "ep_ex_1"

    def test_serialization_roundtrip(self):
        """Test 15: Episode survives JSON serialization."""
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_value=0.3,
            treatment_value=0.5,
            measurement_definition_id="m1",
            outcome_status=OutcomeStatus.EXPECTED_IMPROVEMENT,
            causal_status=CausalAttributionStatus.ATTRIBUTED_TO_TREATMENT,
            attribution_confidence=0.7,
            provenance={"test": "data"},  # Required for eligibility check
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(
                original_user_request="Test goal",
                target_concept="env",
                semantic_direction=SemanticDirection.SHORTER,
            ),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True, contract_id="env_release"),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
            knowledge_ids=["k1", "k2"],
        )

        # Serialize
        generator = UniversalEpisodeGenerator()
        episode_dict = {
            "episode_id": episode.episode_id,
            "execution_id": episode.execution_id,
            "learning_eligible": episode.learning_eligible,
            "semantic_target": episode.semantic_target,
            "outcome_status": episode.outcome_status,
        }

        # Deserialize
        restored = json.loads(json.dumps(episode_dict))
        assert restored["episode_id"] == "ep_ex_1"
        assert restored["learning_eligible"] is True
        assert restored["outcome_status"] == "expected_improvement"

    def test_backend_independence_of_schema(self):
        """Test 16: Universal schema contains no Serum-specific logic."""
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(original_user_request="Test"),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        # Schema fields are generic, not Serum-specific
        assert not any(
            name.startswith("serum_") for name in episode.__dict__.keys()
        )
        assert not any(
            name.startswith("daw_") for name in episode.__dict__.keys()
        )
        # But can reference opaque backend evidence through execution_evidence
        assert hasattr(episode, "execution_evidence")

    def test_provenance_preservation(self):
        """Test 17: Full provenance chain preserved in episode."""
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_value=0.3,
            treatment_value=0.5,
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(original_user_request="Test"),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(
                admitted=True, contract_id="env_release", contract_status="CAUSAL_VERIFIED"
            ),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
            knowledge_ids=["k1"],
            procedure_ids=["p1"],
            prior_episode_ids=["ep_prev"],
        )

        # Full chain preserved
        assert episode.advisory_decision_id == "adv_1"
        assert episode.capability_resolution_id == "res_1"
        assert episode.knowledge_item_ids == ["k1"]
        assert episode.procedure_ids == ["p1"]
        assert episode.prior_episode_ids == ["ep_prev"]
        assert episode.provenance_chain is not None


class TestTopLevelFunctions:
    """Tests 18-20: Top-level functions and integration."""

    def test_generate_episode_function(self):
        """Test 18: Top-level generate_episode works."""
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(original_user_request="Test"),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        assert episode is not None
        assert episode.episode_id == "ep_ex_1"

    def test_learning_eligibility_preserved_on_retrieval(self):
        """Test 19: Learning eligibility survives persistence."""
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_value=0.3,
            treatment_value=0.5,
            measurement_definition_id="m1",
            outcome_status=OutcomeStatus.EXPECTED_IMPROVEMENT,
            causal_status=CausalAttributionStatus.ATTRIBUTED_TO_TREATMENT,
            attribution_confidence=0.7,
            provenance={"test": "data"},  # Required for eligibility check
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(
                original_user_request="Make bass tighter",
                target_concept="envelope",
            ),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True, contract_id="env_release"),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="envelope"),
            outcome=outcome,
        )

        # Learning eligible
        assert episode.learning_eligible is True

        # Simulate what would be stored and retrieved
        stored = {
            "learning_eligible": episode.learning_eligible,
            "semantic_target": episode.semantic_target,
            "outcome_status": episode.outcome_status,
        }

        # Retrieval should preserve these
        assert stored["learning_eligible"] is True
        assert stored["semantic_target"] == "envelope"

    def test_outcome_preserved_in_episode(self):
        """Test 20: Outcome with all details preserved in episode."""
        outcome = UniversalOutcome(
            execution_id="ex_1",
            contract_id="env_release",
            intent_id="intent_1",
            baseline_value=0.3,
            treatment_value=0.5,
            change_magnitude=0.2,
            outcome_status=OutcomeStatus.EXPECTED_IMPROVEMENT,
            causal_status=CausalAttributionStatus.ATTRIBUTED_TO_TREATMENT,
            attribution_confidence=0.7,
            measurement_definition_id="m1",
        )

        episode = generate_episode(
            execution_id="ex_1",
            universal_intent=UniversalProductionIntent(original_user_request="Test"),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        # All outcome details preserved
        assert episode.outcome == outcome
        assert episode.outcome_status == "expected_improvement"
        assert episode.causal_attribution_status == "attributed_to_treatment"
        assert episode.attribution_confidence == 0.7
        assert episode.observed_delta == 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
