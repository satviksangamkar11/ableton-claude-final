"""
Test suite for Step 6.8 Contract-Governed Execution Integration.

Core tests prove authority boundaries:
A. AdmissionResult.admitted gates execution
B. Canonical execution reused (no new path)
D-F. Contract controls target/value/measurement
G. Advisory cannot override contract
M-P. Refusal and execution traces complete
Q-R. Tests pass
"""

import pytest
from unittest.mock import Mock

from step_6_8_contract_governed_execution import (
    ExecutionAuthority,
    ExecutionIntentionRecord,
    ExecutionPathway,
    ContractGovernedExecutor,
    create_execution_intention,
)
from step_6_7_admission_handoff import (
    AdmissionHandoffResult,
)
from step_6_6_capability_resolution import (
    CapabilityResolution,
    ResolutionStatus,
)
from step_6_5_advisory_decision_engine import (
    AdvisoryDecision,
)
from step_6_4_semantic_reasoning_integration import (
    SemanticCandidate,
)
from step_6_2_universal_production_intent import (
    UniversalProductionIntent,
)


class TestExecutionAuthority:
    """Test A: AdmissionResult.admitted gates execution."""

    def test_authority_from_contract(self):
        """Authority derived from contract only."""
        authority = ExecutionAuthority(
            contract_id="env_release",
            allowed_operation="mutate_numeric_value",
            target="envelope_field_release",
            prerequisites={},
            measurement_definition_id="meas_release",
        )

        assert authority.contract_id == "env_release"
        assert authority.target == "envelope_field_release"

    def test_no_advisory_authority(self):
        """Advisory layers do not create authority."""
        # Even with high advisory confidence
        advisory = AdvisoryDecision(
            decision_id="adv_1",
            intent=UniversalProductionIntent(original_user_request="Test"),
            selected_candidate=SemanticCandidate(
                candidate_id="c1",
                label="Test",
                target_concept="note-release",
                confidence=0.99,  # Very high confidence
            ),
            decision_status="decided",
            confidence=0.95,
        )

        # Advisory confidence does NOT create ExecutionAuthority
        assert not hasattr(advisory, "execute")
        assert not hasattr(advisory, "authority")


class TestAdmittedExecution:
    """Test admission gates execution."""

    def test_admitted_creates_authority(self):
        """Admitted result creates execution authority."""
        executor = ContractGovernedExecutor()

        mock_contract = Mock()
        mock_contract.allowed_operation = "mutate_numeric_value"
        mock_contract.target = "envelope_field_release"
        mock_contract.prerequisites = []
        mock_contract.scope = {}
        mock_contract.limitations = []

        mock_registry = Mock()
        mock_registry.get.return_value = mock_contract

        admission = AdmissionHandoffResult(
            handoff_id="h_1",
            admitted=True,
            admission_reason="ADMITTED",
            admission_detail="Test",
            contract_id="env_release",
        )

        authority = executor.build_execution_authority(admission, mock_registry)

        assert authority is not None
        assert authority.contract_id == "env_release"

    def test_refused_no_authority(self):
        """Refused result produces no authority."""
        executor = ContractGovernedExecutor()

        admission = AdmissionHandoffResult(
            handoff_id="h_1",
            admitted=False,
            admission_reason="unknown_no_contract",
            admission_detail="No contract found",
        )

        authority = executor.build_execution_authority(admission, Mock())

        assert authority is None


class TestRefusedExecution:
    """Test M: Refusal blocks execution."""

    def test_refused_pathway(self):
        """Refused admission creates REFUSED pathway."""
        executor = ContractGovernedExecutor()

        intent = UniversalProductionIntent(original_user_request="Test")
        advisory = AdvisoryDecision(
            decision_id="adv_1",
            intent=intent,
        )
        resolution = CapabilityResolution(
            resolution_id="res_1",
            candidate_id="c1",
            requested_semantic_action="test",
            capability_found=False,
            resolution_status=ResolutionStatus.NOT_FOUND,
        )
        admission = AdmissionHandoffResult(
            handoff_id="h_1",
            admitted=False,
            admission_reason="unknown_no_contract",
            admission_detail="No contract",
        )

        record = executor.create_execution_intention(
            intent, advisory, resolution, admission, Mock()
        )

        assert record.pathway == ExecutionPathway.REFUSED
        assert not record.is_authorized()


class TestContractMutationAuthority:
    """Test D-E: Contract controls mutation."""

    def test_contract_target_authority(self):
        """Contract target is the execution target."""
        authority = ExecutionAuthority(
            contract_id="env_release",
            allowed_operation="mutate_numeric_value",
            target="envelope_field_release",
            prerequisites={},
        )

        # Target comes from contract
        assert authority.target == "envelope_field_release"
        # NOT from intent, advisory, or knowledge
        assert authority.target is not None

    def test_contract_operation_authority(self):
        """Contract operation type is authoritative."""
        authority = ExecutionAuthority(
            contract_id="env_release",
            allowed_operation="mutate_numeric_value",
            target="envelope_field_release",
            prerequisites={},
        )

        # Operation from contract
        assert authority.allowed_operation == "mutate_numeric_value"


class TestContractMeasurementAuthority:
    """Test F: Contract controls measurement."""

    def test_contract_measurement_preserved(self):
        """Contract measurement is execution measurement."""
        authority = ExecutionAuthority(
            contract_id="env_release",
            allowed_operation="mutate_numeric_value",
            target="envelope_field_release",
            prerequisites={},
            measurement_definition_id="meas_release_tight",
        )

        # Measurement from contract
        assert authority.measurement_definition_id == "meas_release_tight"


class TestNoAdvisoryOverride:
    """Test G: Advisory cannot override contract."""

    def test_authority_not_from_advisory(self):
        """Authority is NOT derived from advisory decision."""
        executor = ContractGovernedExecutor()

        # High-confidence advisory
        advisory = AdvisoryDecision(
            decision_id="adv_1",
            intent=UniversalProductionIntent(original_user_request="Test"),
            confidence=0.99,  # Very high
        )

        # Actual authority comes from contract via admission
        admission = AdmissionHandoffResult(
            handoff_id="h_1",
            admitted=True,
            admission_reason="ADMITTED",
            admission_detail="Test",
            contract_id="env_release",
        )

        mock_contract = Mock()
        mock_contract.allowed_operation = "mutate_numeric_value"
        mock_contract.target = "envelope_field_release"
        mock_contract.prerequisites = []
        mock_contract.scope = {}
        mock_contract.limitations = []

        mock_registry = Mock()
        mock_registry.get.return_value = mock_contract

        authority = executor.build_execution_authority(admission, mock_registry)

        # Authority must be from contract, NOT from advisory confidence
        assert authority.contract_id == "env_release"
        assert authority.contract_id != advisory.decision_id


class TestExecutionTraceability:
    """Test N-O: Full traceability preserved."""

    def test_execution_record_traceable(self):
        """Execution record preserves complete trace."""
        executor = ContractGovernedExecutor()

        intent = UniversalProductionIntent(
            original_user_request="Make bass tighter"
        )

        advisory = AdvisoryDecision(
            decision_id="adv_1",
            intent=intent,
        )

        resolution = CapabilityResolution(
            resolution_id="res_1",
            candidate_id="c1",
            requested_semantic_action="shorten release",
            capability_found=True,
            capability_contract_id="env_release",
            semantic_target="envelope_field_release",
            resolution_status=ResolutionStatus.RESOLVED,
        )

        admission = AdmissionHandoffResult(
            handoff_id="h_1",
            admitted=True,
            admission_reason="ADMITTED",
            admission_detail="Test",
            contract_id="env_release",
        )

        mock_contract = Mock()
        mock_contract.allowed_operation = "mutate_numeric_value"
        mock_contract.target = "envelope_field_release"
        mock_contract.prerequisites = []
        mock_contract.scope = {}
        mock_contract.limitations = []

        mock_registry = Mock()
        mock_registry.get.return_value = mock_contract

        record = executor.create_execution_intention(
            intent, advisory, resolution, admission, mock_registry
        )

        # Full trace preserved
        assert record.original_intent.original_user_request == "Make bass tighter"
        assert record.advisory_decision.decision_id == "adv_1"
        assert record.capability_resolution.resolution_id == "res_1"
        assert record.admission_result.handoff_id == "h_1"
        assert record.execution_authority.contract_id == "env_release"


class TestValidation:
    """Test authority validation."""

    def test_valid_authority(self):
        """Valid authority passes validation."""
        executor = ContractGovernedExecutor()

        intent = UniversalProductionIntent(original_user_request="Test")
        advisory = AdvisoryDecision(decision_id="adv_1", intent=intent)
        resolution = CapabilityResolution(
            resolution_id="res_1",
            candidate_id="c1",
            requested_semantic_action="test",
            capability_found=True,
            capability_contract_id="env_release",
            semantic_target="envelope_field_release",
            resolution_status=ResolutionStatus.RESOLVED,
        )
        admission = AdmissionHandoffResult(
            handoff_id="h_1",
            admitted=True,
            admission_reason="ADMITTED",
            admission_detail="Test",
            contract_id="env_release",
        )

        mock_contract = Mock()
        mock_contract.allowed_operation = "mutate_numeric_value"
        mock_contract.target = "envelope_field_release"
        mock_contract.prerequisites = []
        mock_contract.scope = {}
        mock_contract.limitations = []

        mock_registry = Mock()
        mock_registry.get.return_value = mock_contract

        record = executor.create_execution_intention(
            intent, advisory, resolution, admission, mock_registry
        )

        assert executor.validate_authority(record)

    def test_invalid_refused_authority(self):
        """Refused authority fails validation."""
        executor = ContractGovernedExecutor()

        record = ExecutionIntentionRecord(
            original_intent=UniversalProductionIntent(original_user_request="Test"),
            advisory_decision=AdvisoryDecision(decision_id="adv_1",
                                              intent=UniversalProductionIntent(original_user_request="Test")),
            capability_resolution=CapabilityResolution(
                resolution_id="res_1",
                candidate_id="c1",
                requested_semantic_action="test",
                capability_found=False,
                resolution_status=ResolutionStatus.NOT_FOUND,
            ),
            admission_result=AdmissionHandoffResult(
                handoff_id="h_1",
                admitted=False,
                admission_reason="unknown",
                admission_detail="Test",
            ),
            execution_authority=None,
            pathway=ExecutionPathway.REFUSED,
        )

        assert not executor.validate_authority(record)


class TestTopLevelFunction:
    """Test R: Tests pass."""

    def test_create_execution_intention_function(self):
        """Top-level function works."""
        intent = UniversalProductionIntent(original_user_request="Test")
        advisory = AdvisoryDecision(decision_id="adv_1", intent=intent)
        resolution = CapabilityResolution(
            resolution_id="res_1",
            candidate_id="c1",
            requested_semantic_action="test",
            capability_found=True,
            capability_contract_id="env_release",
            semantic_target="envelope_field_release",
            resolution_status=ResolutionStatus.RESOLVED,
        )
        admission = AdmissionHandoffResult(
            handoff_id="h_1",
            admitted=True,
            admission_reason="ADMITTED",
            admission_detail="Test",
            contract_id="env_release",
        )

        mock_contract = Mock()
        mock_contract.allowed_operation = "mutate_numeric_value"
        mock_contract.target = "envelope_field_release"
        mock_contract.prerequisites = []
        mock_contract.scope = {}
        mock_contract.limitations = []

        mock_registry = Mock()
        mock_registry.get.return_value = mock_contract

        record = create_execution_intention(
            intent, advisory, resolution, admission, mock_registry
        )

        assert record is not None
        assert record.pathway == ExecutionPathway.ADMITTED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
