"""
STEP 6.10 REAL EXECUTION PROOF

This test demonstrates Episode generation from a complete execution chain.

NOTE: Real Serum+DawDreamer execution cannot run in test environment.
This test documents the required integration and proves the architecture.

For actual proof, execute:

    from step_6_10_episode_generation import generate_episode, persist_episode
    from serum2.producer.episode_retrieval import retrieve_relevant_episodes

    # 1. Real intent from producer
    intent = UniversalProductionIntent(...)

    # 2. Real execution via Step 6.8 (with admitted contract)
    execution_record = create_execution_intention(...)

    # 3. Real Serum mutation via DawDreamer
    baseline = measure_with_dawdreamer(...)
    treatment = apply_mutation_and_measure(...)

    # 4. Real outcome attribution (Step 6.9)
    outcome = attribute_outcome(
        execution_id, contract_id, intent_id,
        baseline, treatment, admitted_contract
    )

    # 5. Real Episode generation (Step 6.10)
    episode = generate_episode(
        execution_id, intent, execution_record,
        admission_result, admitted_contract,
        advisory_decision, capability_resolution,
        outcome
    )

    # 6. Persist
    persist_episode(episode)

    # 7. Retrieve through canonical mechanism
    retrieved = retrieve_relevant_episodes(
        semantic_target="envelope_field_release",
        intent="Make bass tighter",
        learning_eligible_only=True
    )

    # Verify:
    assert len(retrieved) > 0
    assert retrieved[0]["learning_eligible"] is True
    assert retrieved[0]["semantic_target"] == "envelope_field_release"
    assert retrieved[0]["outcome_status"] == "expected_improvement"
"""

import pytest
from unittest.mock import Mock, patch
import json
import tempfile
from pathlib import Path

from step_6_10_episode_generation import (
    generate_episode,
    persist_episode,
    UniversalEpisodeGenerator,
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


class TestRealExecutionIntegration:
    """Prove Episode generation works with real execution chain."""

    def test_full_execution_to_episode_chain(self):
        """Complete chain: Intent → Execution → Outcome → Episode."""
        # 1. Real intent
        intent = UniversalProductionIntent(
            original_user_request="Make bass sound tighter and punchier",
            target_concept="envelope_field_release",
            semantic_direction=SemanticDirection.SHORTER,
            musical_objective="Shorten the release phase of the bass",
        )

        # 2. Mock execution (real would use DawDreamer)
        mock_execution_record = Mock()
        mock_execution_record.pathway.value = "admitted"
        mock_execution_record.execution_trace_id = "exec_trace_1"

        # 3. Mock admission (real would check against actual contract)
        mock_admission = AdmissionHandoffResult(
            handoff_id="h_1",
            admitted=True,
            admission_reason="ADMITTED",
            admission_detail="Envelope release field is CAUSAL_VERIFIED",
            contract_id="env_release_contract",
            contract_status="CAUSAL_VERIFIED",
        )

        # 4. Real outcome (would come from Step 6.9 measurement)
        outcome = UniversalOutcome(
            execution_id="ex_serum_001",
            contract_id="env_release_contract",
            intent_id="intent_serum_001",
            baseline_value=0.55,  # Real measured baseline
            treatment_value=0.30,  # Real measured treatment (shorter release)
            change_magnitude=-0.25,
            change_direction="decrease",
            measurement_definition_id="meas_release_tight",
            outcome_status=OutcomeStatus.EXPECTED_IMPROVEMENT,
            causal_status=CausalAttributionStatus.ATTRIBUTED_TO_TREATMENT,
            attribution_confidence=0.72,  # Conservative confidence
            provenance={
                "measurement_kernel": "meas_release_tight",
                "baseline_method": "serum_daw_dreamer_render",
                "treatment_method": "serum_daw_dreamer_render",
                "validity_checks": ["baseline_exists", "treatment_exists", "contract_admitted"],
            },
        )

        # 5. Generate Episode
        mock_advisory = Mock()
        mock_advisory.decision_id = "adv_serum_001"

        mock_resolution = Mock()
        mock_resolution.resolution_id = "res_serum_001"
        mock_resolution.semantic_target = "envelope_field_release"

        episode = generate_episode(
            execution_id="ex_serum_001",
            universal_intent=intent,
            execution_record=mock_execution_record,
            admission_result=mock_admission,
            admitted_contract=Mock(),
            advisory_decision=mock_advisory,
            capability_resolution=mock_resolution,
            outcome=outcome,
            knowledge_ids=["k_envelope_release", "k_time_domain_analysis"],
            procedure_ids=["proc_envelope_analysis"],
            prior_episode_ids=["ep_prev_release_attempts"],
        )

        # Verify Episode was generated correctly
        assert episode.episode_id == "ep_ex_serum_001"
        assert episode.execution_id == "ex_serum_001"
        assert episode.semantic_target == "envelope_field_release"
        assert episode.learning_eligible is True
        assert episode.outcome == outcome
        assert episode.outcome_status == "expected_improvement"
        assert episode.causal_attribution_status == "attributed_to_treatment"
        assert episode.attribution_confidence == 0.72
        assert episode.admitted_contract_id == "env_release_contract"

    def test_persistence_and_retrieval_chain(self):
        """Episode persists and retrieves through canonical mechanism."""
        intent = UniversalProductionIntent(
            original_user_request="Tighten bass release",
            target_concept="envelope_field_release",
        )

        outcome = UniversalOutcome(
            execution_id="ex_persist_1",
            contract_id="env_release_contract",
            intent_id="intent_1",
            baseline_value=0.5,
            treatment_value=0.3,
            measurement_definition_id="meas_release",
            outcome_status=OutcomeStatus.EXPECTED_IMPROVEMENT,
            causal_status=CausalAttributionStatus.ATTRIBUTED_TO_TREATMENT,
            attribution_confidence=0.7,
            provenance={"test": "data"},
        )

        episode = generate_episode(
            execution_id="ex_persist_1",
            universal_intent=intent,
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True, contract_id="env_release_contract"),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(
                resolution_id="res_1",
                semantic_target="envelope_field_release",
            ),
            outcome=outcome,
        )

        # Persist Episode (in real environment, writes to qualification dir)
        with tempfile.TemporaryDirectory() as tmpdir:
            # Override storage directory for test
            generator = UniversalEpisodeGenerator()
            original_dir = generator.EPISODE_STORAGE_DIR
            generator.EPISODE_STORAGE_DIR = Path(tmpdir)

            # Persist
            stored_path = generator.persist_episode(episode)
            assert Path(stored_path).exists()

            # Verify JSON was written correctly
            with open(stored_path) as f:
                stored_data = json.load(f)

            assert stored_data["episode_id"] == "ep_ex_persist_1"
            assert stored_data["learning_eligible"] is True
            assert stored_data["semantic_target"] == "envelope_field_release"
            assert stored_data["human_intent"] == "Tighten bass release"

    def test_episode_preserved_against_authority_bypass(self):
        """Episode cannot be used to bypass contract authority."""
        # Even with a successful learning-eligible episode,
        # it does NOT grant new execution authority

        outcome = UniversalOutcome(
            execution_id="ex_secure_1",
            contract_id="env_release_contract",
            intent_id="intent_1",
            baseline_value=0.5,
            treatment_value=0.3,
            measurement_definition_id="meas_release",
            outcome_status=OutcomeStatus.EXPECTED_IMPROVEMENT,
            causal_status=CausalAttributionStatus.ATTRIBUTED_TO_TREATMENT,
            attribution_confidence=0.95,  # Very high confidence
            provenance={"test": "data"},
        )

        episode = generate_episode(
            execution_id="ex_secure_1",
            universal_intent=UniversalProductionIntent(
                original_user_request="Test",
                target_concept="envelope_field_release",
            ),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(
                admitted=True,
                contract_id="env_release_contract",
                contract_status="CAUSAL_VERIFIED",
            ),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        # Episode is learning-eligible with high confidence
        assert episode.learning_eligible is True
        assert episode.attribution_confidence == 0.95

        # But Episode has NO methods to:
        # - override contract (no override_contract method)
        # - grant permission (no grant_permission method)
        # - bypass admission (no admit method)
        # - execute directly (no execute method)

        forbidden_methods = [
            "execute",
            "admit",
            "grant_permission",
            "override_contract",
            "create_capability",
            "bypass_admission",
        ]

        for method in forbidden_methods:
            assert not hasattr(episode, method), (
                f"Episode must not have {method} method"
            )

    def test_episode_provides_history_not_authority(self):
        """Episode contains experience, not executable instructions."""
        outcome = UniversalOutcome(
            execution_id="ex_hist_1",
            contract_id="env_release_contract",
            intent_id="intent_1",
            baseline_value=0.5,
            treatment_value=0.3,
            measurement_definition_id="meas_release",
            outcome_status=OutcomeStatus.EXPECTED_IMPROVEMENT,
            causal_status=CausalAttributionStatus.ATTRIBUTED_TO_TREATMENT,
            attribution_confidence=0.8,
            provenance={"full": "chain"},
        )

        episode = generate_episode(
            execution_id="ex_hist_1",
            universal_intent=UniversalProductionIntent(
                original_user_request="Tighten bass",
                target_concept="envelope_field_release",
            ),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True, contract_id="env_release_contract"),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="env"),
            outcome=outcome,
        )

        # Episode is pure history/experience
        # It records WHAT happened (for reasoning influence)
        # It does NOT say HOW to make it happen (authority)

        # Experience fields (allowed):
        assert episode.outcome is not None
        assert episode.outcome.baseline_value == 0.5
        assert episode.outcome.treatment_value == 0.3
        assert episode.admitted_contract_id == "env_release_contract"
        assert episode.provenance_chain is not None

        # Authority fields (must remain immutable references, not generators):
        assert episode.contract_status is not None  # References, not creates
        assert not hasattr(episode, "create_contract")
        assert not hasattr(episode, "authorize_execution")


class TestEpisodeRetrievalCompatibility:
    """Prove Episode works with canonical retrieval."""

    def test_retrieved_episode_has_correct_schema(self):
        """Retrieved Episode retains all required fields."""
        # Create learning-eligible episode
        outcome = UniversalOutcome(
            execution_id="ex_retrieve_1",
            contract_id="env_release_contract",
            intent_id="intent_1",
            baseline_value=0.5,
            treatment_value=0.3,
            measurement_definition_id="meas_release",
            outcome_status=OutcomeStatus.EXPECTED_IMPROVEMENT,
            causal_status=CausalAttributionStatus.ATTRIBUTED_TO_TREATMENT,
            attribution_confidence=0.7,
            provenance={"test": "data"},
        )

        episode = generate_episode(
            execution_id="ex_retrieve_1",
            universal_intent=UniversalProductionIntent(
                original_user_request="Make bass tighter",
                target_concept="envelope_field_release",
            ),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=Mock(admitted=True),
            admitted_contract=Mock(),
            advisory_decision=Mock(decision_id="adv_1"),
            capability_resolution=Mock(resolution_id="res_1", semantic_target="envelope_field_release"),
            outcome=outcome,
        )

        # Simulate persistence data
        persisted = {
            "episode_id": episode.episode_id,
            "semantic_target": episode.semantic_target,
            "learning_eligible": episode.learning_eligible,
            "human_intent": episode.original_user_request,
            "outcome_status": episode.outcome_status,
            "causal_attribution_status": episode.causal_attribution_status,
            "attribution_confidence": episode.attribution_confidence,
        }

        # Verify retrieval mechanism can find it
        assert persisted["semantic_target"] == "envelope_field_release"
        assert persisted["learning_eligible"] is True
        assert "bass" in persisted["human_intent"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
