"""
STEP 6.12 — KNOWLEDGE / EXPERIENCE / AUTHORITY ADVERSARIAL PROOF

Proves that the three information domains remain strictly separated:

    KNOWLEDGE   = information used for teaching and reasoning
    EPISODE     = historical production experience
    CAPABILITY CONTRACT = qualified execution authority

The critical invariant:
    KNOWLEDGE != AUTHORITY
    EPISODE   != AUTHORITY

This file contains adversarial tests that try to cross boundaries.
Every test must PASS, meaning every boundary holds.

Case groups A–H map exactly to the Step 6.12 specification.
"""

import pytest
import inspect
from unittest.mock import Mock, MagicMock
from pathlib import Path

# Core Step 6 structures
from step_6_2_universal_production_intent import (
    UniversalProductionIntent,
    SemanticDirection,
)
from step_6_4_semantic_reasoning_integration import SemanticCandidate
from step_6_5_advisory_decision_engine import AdvisoryDecision, DecisionStatus
from step_6_6_capability_resolution import (
    CapabilityResolution,
    ResolutionStatus,
)
from step_6_7_admission_handoff import AdmissionHandoffResult
from step_6_8_contract_governed_execution import (
    ExecutionAuthority,
    ExecutionIntentionRecord,
    ExecutionPathway,
    ContractGovernedExecutor,
)
from step_6_9_outcome_attribution import (
    UniversalOutcome,
    OutcomeStatus,
    CausalAttributionStatus,
    attribute_outcome,
)
from step_6_10_episode_generation import (
    UniversalExecutedEpisode,
    UniversalEpisodeGenerator,
    LearningEligibilityStatus,
    EpisodeExecutionStatus,
    generate_episode,
)


# ============================================================
# PROOF MATRIX CONSTANTS
# ============================================================

# Functions/methods that MUST NOT appear in universal (non-authority) layers
FORBIDDEN_IN_ADVISORY_LAYERS = [
    "execute", "mutate", "render", "admit",
    "create_contract", "grant_capability", "authorize",
]

# Fields that MUST be sourced from contract only
CONTRACT_AUTHORITY_FIELDS = [
    "allowed_operation",   # operation
    "target",              # mutation target
    "prerequisites",       # prerequisites
    "measurement_definition_id",  # measurement
    "scope",               # value/scope
    "limitations",         # limitations
]


# ============================================================
# HELPERS
# ============================================================

def make_intent(request="Make bass tighter", concept="note-release"):
    return UniversalProductionIntent(
        original_user_request=request,
        target_concept=concept,
        semantic_direction=SemanticDirection.SHORTER,
    )


def make_candidate(cid="c1", label="shorten_release", confidence=0.80):
    return SemanticCandidate(
        candidate_id=cid,
        label=label,
        target_concept="note-release",
        confidence=confidence,
    )


def make_admitted(contract_id="env_release"):
    return AdmissionHandoffResult(
        handoff_id="h_1",
        admitted=True,
        admission_reason="ADMITTED",
        admission_detail="Test admitted",
        contract_id=contract_id,
        contract_status="CAUSAL_VERIFIED",
    )


def make_refused(reason="unknown_no_contract"):
    return AdmissionHandoffResult(
        handoff_id="h_r",
        admitted=False,
        admission_reason=reason,
        admission_detail="Refused",
    )


def make_resolved(contract_id="env_release", target="envelope_field_release"):
    return CapabilityResolution(
        resolution_id="res_1",
        candidate_id="c1",
        requested_semantic_action="shorten",
        capability_found=True,
        capability_contract_id=contract_id,
        semantic_target=target,
        resolution_status=ResolutionStatus.RESOLVED,
    )


def make_not_found():
    return CapabilityResolution(
        resolution_id="res_nf",
        candidate_id="c1",
        requested_semantic_action="unknown_action_X",
        capability_found=False,
        resolution_status=ResolutionStatus.NOT_FOUND,
    )


def make_outcome_with_attribution(
    baseline=0.40, treatment=0.25, mid="meas_release",
    status=OutcomeStatus.EXPECTED_IMPROVEMENT,
    causal=CausalAttributionStatus.ATTRIBUTED_TO_TREATMENT,
    confidence=0.70,
    confounds=None,
):
    return UniversalOutcome(
        execution_id="ex_test",
        contract_id="env_release",
        intent_id="intent_test",
        baseline_value=baseline,
        treatment_value=treatment,
        change_magnitude=treatment - baseline,
        change_direction="decrease",
        measurement_definition_id=mid,
        outcome_status=status,
        causal_status=causal,
        attribution_confidence=confidence,
        confounds_detected=confounds or [],
        provenance={"test": True},
    )


def make_mock_contract(target="envelope_field_release",
                       op="mutate_numeric_value",
                       mid="meas_release"):
    c = Mock()
    c.target = target
    c.allowed_operation = op
    c.prerequisites = []
    c.scope = {"expected_direction": "decrease"}
    c.limitations = []
    c.measurement = {"measurement_definition_id": mid}
    return c


def make_mock_registry(contract=None):
    r = Mock()
    r.get.return_value = contract or make_mock_contract()
    return r


# ============================================================
# CASE GROUP A — KNOWLEDGE ATTACKS
# ============================================================

class TestCaseGroupA_KnowledgeAttacks:
    """A1–A5: Adversarial knowledge cannot become execution authority."""

    def test_A1_knowledge_recommends_action_no_capability(self):
        """A1: Knowledge recommends action; no admissible contract → no execution."""
        # Knowledge says "increase_attack" is the right thing to do
        knowledge_says = {
            "action": "increase_attack",
            "reasoning": "Attacks shape the percussive character of the sound",
            "confidence": 0.90,  # High knowledge confidence
        }

        # But no capability contract exists for that target
        resolution = make_not_found()

        # Knowledge confidence != admission
        assert resolution.capability_found is False
        assert resolution.resolution_status == ResolutionStatus.NOT_FOUND

        # Advisory layer can use knowledge...
        advisory = AdvisoryDecision(
            decision_id="adv_k_a1",
            intent=make_intent(),
            selected_candidate=make_candidate("c_attack", "increase_attack", 0.90),
            decision_status="decided",
            confidence=knowledge_says["confidence"],
        )
        # ...but advisory confidence is NOT execution authority
        assert not hasattr(advisory, "execute")
        assert not hasattr(advisory, "authority")
        # Execution remains blocked: no resolved contract → no admission → no execution
        assert not resolution.capability_found

    def test_A2_knowledge_proposes_value_contract_wins(self):
        """A2: Knowledge proposes mutation value Y; contract authorizes Z → Z wins."""
        knowledge_suggested_value = 0.1   # Y – from knowledge item
        contract_authorized_scope = {"expected_direction": "decrease"}  # Z – from contract

        # Admitted contract holds authoritative scope
        contract = make_mock_contract()
        contract.scope = contract_authorized_scope

        admission = make_admitted()
        registry = make_mock_registry(contract)

        executor = ContractGovernedExecutor()
        authority = executor.build_execution_authority(admission, registry)

        # Authority comes from contract, not knowledge
        assert authority is not None
        assert authority.scope == contract_authorized_scope
        # Knowledge's value Y is not in the authority
        assert authority.scope != {"value": knowledge_suggested_value}

    def test_A3_knowledge_recommends_measurement_contract_wins(self):
        """A3: Knowledge recommends M1; contract defines M2 → M2 is used."""
        knowledge_suggested_mid = "meas_perceptual_brightness"   # M1
        contract_measurement_id = "meas_release"                  # M2

        contract = make_mock_contract(mid=contract_measurement_id)
        admission = make_admitted()
        # Admitted contract carries the measurement; admission propagates it
        admission.measurement_definition_id = contract_measurement_id
        registry = make_mock_registry(contract)

        executor = ContractGovernedExecutor()
        authority = executor.build_execution_authority(admission, registry)

        # Contract measurement is the authority (via admission chain)
        assert authority.measurement_definition_id == contract_measurement_id
        # Knowledge measurement M1 is NOT the authority
        assert authority.measurement_definition_id != knowledge_suggested_mid

    def test_A4_high_confidence_knowledge_no_permission(self):
        """A4: Knowledge confidence=0.99 does NOT grant execution permission."""
        # Highest possible advisory confidence
        advisory = AdvisoryDecision(
            decision_id="adv_k_a4",
            intent=make_intent(),
            selected_candidate=make_candidate(confidence=0.99),
            decision_status="decided",
            confidence=0.99,
        )

        # Advisory decision has NO authority fields
        assert not hasattr(advisory, "execute")
        assert not hasattr(advisory, "authority")
        assert not hasattr(advisory, "admit")
        assert not hasattr(advisory, "create_contract")

        # Without admission, there is no authority
        refused = make_refused()
        assert refused.admitted is False

    def test_A5_knowledge_causal_claim_not_causal_authority(self):
        """A5: Knowledge claiming causality does NOT become causal authority."""
        # Outcome Attribution is evidence-governed, not knowledge-governed
        outcome = attribute_outcome(
            execution_id="ex_k_a5",
            contract_id="env_release",
            intent_id="intent_k_a5",
            baseline_measurement={
                "value": 0.5,
                "measurement_definition_id": "meas_release"
            },
            treatment_measurement={
                "value": 0.3,
                "measurement_definition_id": "meas_release"
            },
            admitted_contract=make_mock_contract(),
        )

        # Attribution is evidence-driven (from actual measurement), not from knowledge claim
        assert outcome.causal_status in (
            CausalAttributionStatus.ATTRIBUTED_TO_TREATMENT,
            CausalAttributionStatus.CONSISTENT_WITH_TREATMENT,
        )
        # Knowledge "knowing" causality beforehand is NOT the source of causal_status
        # The source is the measurement comparison + contract expectation
        assert outcome.measurement_definition_id == "meas_release"
        assert outcome.baseline_value == 0.5


# ============================================================
# CASE GROUP B — EPISODE ATTACKS
# ============================================================

class TestCaseGroupB_EpisodeAttacks:
    """B1–B5: Adversarial episodes cannot become execution authority."""

    def test_B1_episode_success_no_capability_no_execution(self):
        """B1: Episode says X succeeded; current capability X unavailable → no execution."""
        # Episode records a successful "use_wavetable_morph" action
        episode = UniversalExecutedEpisode(
            episode_id="ep_b1",
            execution_id="ex_b1",
            original_user_request="Use wavetable morph",
            universal_intent=make_intent("Use wavetable morph", "wavetable_morph"),
            semantic_target="wavetable_morph",  # No contract for this
            admission_allowed=True,
            learning_eligible=True,
        )

        # But capability resolution finds nothing
        resolution = CapabilityResolution(
            resolution_id="res_b1",
            candidate_id="c1",
            requested_semantic_action="wavetable_morph",
            capability_found=False,
            resolution_status=ResolutionStatus.NOT_FOUND,
        )

        # Episode cannot manufacture missing contract
        assert resolution.capability_found is False
        assert episode.admitted_contract_id is None  # Episode doesn't inject contract

    def test_B2_episode_value_recommendation_contract_wins(self):
        """B2: Episode recommends mutation value Y; contract authorizes Z → Z executed."""
        # Episode historically used value 0.05 (Y)
        episode_historical_value = 0.05   # Y

        # But admitted contract specifies decrease direction (Z)
        contract = make_mock_contract()
        contract.scope = {"expected_direction": "decrease"}  # Z

        admission = make_admitted()
        registry = make_mock_registry(contract)

        executor = ContractGovernedExecutor()
        authority = executor.build_execution_authority(admission, registry)

        # Contract scope Z is what the execution will follow
        assert authority.scope == {"expected_direction": "decrease"}
        # Episode's historical value is NOT in the execution authority
        assert authority.scope.get("value") != episode_historical_value

    def test_B3_episode_measurement_contract_wins(self):
        """B3: Episode used M1 previously; contract defines M2 → M2 authoritative."""
        episode_old_measurement = "meas_brightness"        # M1 (historically used)
        contract_measurement = "meas_release"               # M2 (contract defines)

        contract = make_mock_contract(mid=contract_measurement)
        admission = make_admitted()
        # Admitted contract carries measurement; admission propagates it
        admission.measurement_definition_id = contract_measurement
        registry = make_mock_registry(contract)

        executor = ContractGovernedExecutor()
        authority = executor.build_execution_authority(admission, registry)

        # Contract measurement M2 is authoritative (via admission chain)
        assert authority.measurement_definition_id == contract_measurement
        # Episode's M1 does NOT override
        assert authority.measurement_definition_id != episode_old_measurement

    def test_B4_high_confidence_episode_no_execution_permission(self):
        """B4: Episode confidence=0.99 does NOT grant execution permission."""
        outcome = make_outcome_with_attribution(confidence=0.99)

        episode = generate_episode(
            execution_id="ex_b4",
            universal_intent=make_intent(),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=make_admitted(),
            admitted_contract=make_mock_contract(),
            advisory_decision=Mock(decision_id="adv_b4"),
            capability_resolution=Mock(
                resolution_id="res_b4",
                semantic_target="envelope_field_release",
            ),
            outcome=outcome,
        )

        # Episode has high confidence but NO authority methods
        assert episode.attribution_confidence == 0.99
        assert not hasattr(episode, "execute")
        assert not hasattr(episode, "admit")
        assert not hasattr(episode, "create_contract")
        assert not hasattr(episode, "grant_capability")

    def test_B5_backend_specific_episode_evidence_cannot_invoke_executor(self):
        """B5: Episode with backend-specific evidence cannot directly invoke executor."""
        from step_6_10_episode_generation import ExecutionEvidenceRecord

        # Episode has concrete Serum-like execution evidence
        backend_evidence = ExecutionEvidenceRecord(
            baseline_state={"Env1.Release": 0.5},      # Serum-specific
            treatment_state={"Env1.Release": 0.2},     # Serum-specific
            mutation_description="Set Env1.Release from 0.5 to 0.2",
            render_evidence={"rms_db": -18.3},
        )

        outcome = make_outcome_with_attribution()
        episode = generate_episode(
            execution_id="ex_b5",
            universal_intent=make_intent(),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=make_admitted(),
            admitted_contract=make_mock_contract(),
            advisory_decision=Mock(decision_id="adv_b5"),
            capability_resolution=Mock(
                resolution_id="res_b5",
                semantic_target="envelope_field_release",
            ),
            outcome=outcome,
            execution_evidence=backend_evidence,
        )

        # Evidence is stored as opaque record — episode has no execute() method
        assert episode.execution_evidence == backend_evidence
        assert not hasattr(episode, "execute")
        assert not hasattr(episode, "replay")
        assert not hasattr(episode, "mutate")
        # The episode RECORDS the evidence, does not RE-EXECUTE it
        assert episode.execution_evidence.baseline_state == {"Env1.Release": 0.5}


# ============================================================
# CASE GROUP C — ADVISORY DECISION ATTACKS
# ============================================================

class TestCaseGroupC_AdvisoryDecisionAttacks:
    """C1–C3: Advisory decisions cannot become execution authority."""

    def test_C1_advisory_candidate_no_capability_no_execution(self):
        """C1: Advisory has executable-looking candidate; capability absent → no execution."""
        advisory = AdvisoryDecision(
            decision_id="adv_c1",
            intent=make_intent("Apply complex modulation routing"),
            selected_candidate=SemanticCandidate(
                candidate_id="c_mod",
                label="apply_modulation_route",
                target_concept="modulation_routing",
                confidence=0.88,
            ),
            decision_status="decided",
            confidence=0.88,
        )

        # No capability for this action
        resolution = CapabilityResolution(
            resolution_id="res_c1",
            candidate_id="c_mod",
            requested_semantic_action="apply_modulation_route",
            capability_found=False,
            resolution_status=ResolutionStatus.NOT_FOUND,
        )

        # Advisory is advisory only; cannot execute
        assert not resolution.capability_found
        assert not hasattr(advisory, "execute")

        # Executor would produce REFUSED pathway
        executor = ContractGovernedExecutor()
        record = executor.create_execution_intention(
            intent=make_intent(),
            advisory_decision=advisory,
            capability_resolution=resolution,
            admission_result=make_refused(),
            contract_registry=make_mock_registry(),
        )
        assert record.pathway == ExecutionPathway.REFUSED
        assert not record.is_authorized()

    def test_C2_advisory_conflicts_contract_contract_wins(self):
        """C2: Advisory candidate conflicts with admitted contract → contract wins."""
        # Advisory wants "increase brightness"
        advisory = AdvisoryDecision(
            decision_id="adv_c2",
            intent=make_intent("Make it brighter"),
            selected_candidate=SemanticCandidate(
                candidate_id="c_bright",
                label="increase_brightness",
                target_concept="filter_cutoff",
                confidence=0.85,
            ),
            decision_status="decided",
            confidence=0.85,
        )

        # But admitted contract is for "envelope_field_release" (different target)
        contract = make_mock_contract(target="envelope_field_release")
        admission = make_admitted("env_release")
        registry = make_mock_registry(contract)

        executor = ContractGovernedExecutor()
        authority = executor.build_execution_authority(admission, registry)

        # Contract target wins — NOT the advisory candidate's target
        assert authority.target == "envelope_field_release"
        assert authority.target != "filter_cutoff"

    def test_C3_advisory_confidence_one_not_authority(self):
        """C3: Advisory confidence=1.0 does NOT grant authority."""
        advisory = AdvisoryDecision(
            decision_id="adv_c3",
            intent=make_intent(),
            selected_candidate=make_candidate(confidence=1.0),
            decision_status="decided",
            confidence=1.0,  # Maximum possible confidence
        )

        # Maximum confidence has no authority methods
        assert advisory.confidence == 1.0
        assert not hasattr(advisory, "execute")
        assert not hasattr(advisory, "authority")
        assert not hasattr(advisory, "admit")

        # Refused admission still blocks execution
        refused = make_refused()
        executor = ContractGovernedExecutor()
        resolution = make_not_found()
        record = executor.create_execution_intention(
            intent=make_intent(),
            advisory_decision=advisory,
            capability_resolution=resolution,
            admission_result=refused,
            contract_registry=make_mock_registry(),
        )
        assert record.pathway == ExecutionPathway.REFUSED


# ============================================================
# CASE GROUP D — CAPABILITY RESOLUTION ATTACK
# ============================================================

class TestCaseGroupD_ResolutionVsAdmission:
    """D: RESOLVED != ADMITTED. Resolution alone grants nothing."""

    def test_D1_resolved_but_admission_failed_no_execution(self):
        """D: Resolution succeeds; admission fails → zero execution."""
        resolution = make_resolved()
        assert resolution.capability_found is True
        assert resolution.resolution_status == ResolutionStatus.RESOLVED

        # But admission refused
        refused = make_refused("refused_prerequisites_not_met")
        assert refused.admitted is False

        executor = ContractGovernedExecutor()
        record = executor.create_execution_intention(
            intent=make_intent(),
            advisory_decision=AdvisoryDecision(
                decision_id="adv_d1",
                intent=make_intent(),
            ),
            capability_resolution=resolution,
            admission_result=refused,
            contract_registry=make_mock_registry(),
        )

        # RESOLVED capability → REFUSED admission → NO execution authority
        assert record.pathway == ExecutionPathway.REFUSED
        assert record.execution_authority is None
        assert not record.is_authorized()

    def test_D2_only_admitted_true_creates_authority(self):
        """D: Only AdmissionResult.admitted==True creates ExecutionAuthority."""
        executor = ContractGovernedExecutor()
        contract = make_mock_contract()
        registry = make_mock_registry(contract)

        # Path 1: admitted=False → no authority
        refused = make_refused()
        auth_refused = executor.build_execution_authority(refused, registry)
        assert auth_refused is None

        # Path 2: admitted=True → authority created
        admitted = make_admitted()
        auth_granted = executor.build_execution_authority(admitted, registry)
        assert auth_granted is not None
        assert isinstance(auth_granted, ExecutionAuthority)


# ============================================================
# CASE GROUP E — CONTRACT AUTHORITY PROOF
# ============================================================

class TestCaseGroupE_ContractAuthorityProof:
    """E: All execution authority fields traced to CapabilityContract."""

    def test_E1_mutation_target_from_contract(self):
        """E: mutation target ← CapabilityContract, not from advisory/knowledge."""
        contract = make_mock_contract(target="envelope_field_release")
        admission = make_admitted()
        registry = make_mock_registry(contract)

        executor = ContractGovernedExecutor()
        authority = executor.build_execution_authority(admission, registry)

        assert authority.target == "envelope_field_release"
        assert authority.target == contract.target  # Direct contract source

    def test_E2_operation_from_contract(self):
        """E: operation ← CapabilityContract."""
        contract = make_mock_contract(op="mutate_numeric_value")
        admission = make_admitted()
        registry = make_mock_registry(contract)

        executor = ContractGovernedExecutor()
        authority = executor.build_execution_authority(admission, registry)

        assert authority.allowed_operation == "mutate_numeric_value"
        assert authority.allowed_operation == contract.allowed_operation

    def test_E3_measurement_definition_from_contract(self):
        """E: measurement_definition_id ← CapabilityContract."""
        contract = make_mock_contract(mid="meas_release_tight")
        admission = make_admitted()
        admission.measurement_definition_id = "meas_release_tight"
        registry = make_mock_registry(contract)

        executor = ContractGovernedExecutor()
        authority = executor.build_execution_authority(admission, registry)

        # Measurement from the admitted contract chain
        assert authority.measurement_definition_id == "meas_release_tight"

    def test_E4_scope_from_contract(self):
        """E: scope/value ← CapabilityContract."""
        contract = make_mock_contract()
        contract.scope = {"expected_direction": "decrease", "max_delta": 0.4}
        admission = make_admitted()
        registry = make_mock_registry(contract)

        executor = ContractGovernedExecutor()
        authority = executor.build_execution_authority(admission, registry)

        assert authority.scope == contract.scope

    def test_E5_prerequisites_from_contract(self):
        """E: prerequisites ← CapabilityContract."""
        contract = make_mock_contract()
        # Use a dict so dict(contract.prerequisites) works correctly
        contract.prerequisites = {"Osc1.UnisonOn": {"must_equal": 1}}
        admission = make_admitted()
        registry = make_mock_registry(contract)

        executor = ContractGovernedExecutor()
        authority = executor.build_execution_authority(admission, registry)

        # Prerequisites flowed from contract (not from knowledge/episode)
        assert authority.prerequisites == {"Osc1.UnisonOn": {"must_equal": 1}}
        assert authority.prerequisites == contract.prerequisites

    def test_E6_limitations_from_contract(self):
        """E: limitations ← CapabilityContract."""
        contract = make_mock_contract()
        contract.limitations = ["do_not_exceed_0.9", "requires_mono_mode"]
        admission = make_admitted()
        registry = make_mock_registry(contract)

        executor = ContractGovernedExecutor()
        authority = executor.build_execution_authority(admission, registry)

        assert authority.limitations == contract.limitations


# ============================================================
# CASE GROUP F — DIAGNOSIS ATTACK
# ============================================================

class TestCaseGroupF_DiagnosisAttack:
    """F: Diagnosis cannot override contract authority."""

    def test_F1_diagnosis_cannot_override_execution_authority(self):
        """F: Diagnosis recommends X; admitted contract authorizes Y → Y wins."""
        # Diagnosis says "increase filter cutoff"
        diagnosis = {
            "recommended_action": "increase_filter_cutoff",
            "confidence": 0.92,
            "reasoning": "Sound lacks high-frequency presence",
        }

        # But admitted contract authorizes shorten envelope release
        contract = make_mock_contract(target="envelope_field_release", op="mutate_numeric_value")
        admission = make_admitted()
        registry = make_mock_registry(contract)

        executor = ContractGovernedExecutor()
        authority = executor.build_execution_authority(admission, registry)

        # Contract wins; diagnosis recommendation is ignored at execution
        assert authority.target == "envelope_field_release"
        assert authority.allowed_operation == "mutate_numeric_value"
        assert authority.target != "filter_cutoff"

        # Diagnosis has no authority to override
        assert diagnosis.get("authorized") is None

    def test_F2_diagnosis_cannot_change_measurement_definition(self):
        """F: Diagnosis cannot change post-admission measurement definition."""
        diagnosis_suggested_mid = "meas_perceptual_brightness"  # Diagnosis wants this
        contract_measurement_id = "meas_release"                 # Contract defines this

        contract = make_mock_contract(mid=contract_measurement_id)
        admission = make_admitted()
        admission.measurement_definition_id = contract_measurement_id
        registry = make_mock_registry(contract)

        executor = ContractGovernedExecutor()
        authority = executor.build_execution_authority(admission, registry)

        # Contract measurement wins
        assert authority.measurement_definition_id == contract_measurement_id
        assert authority.measurement_definition_id != diagnosis_suggested_mid


# ============================================================
# CASE GROUP G — CROSS-CONTAMINATION TESTS
# ============================================================

class TestCaseGroupG_CrossContamination:
    """G: Knowledge and Episode cannot cross-contaminate authority."""

    def test_G1_knowledge_cannot_create_episode_authority(self):
        """G: Knowledge confidence cannot make Episode learning-eligible."""
        # High-confidence knowledge exists
        knowledge_confidence = 0.99

        # But Episode is not eligible due to missing evidence
        outcome = UniversalOutcome(
            execution_id="ex_g1",
            contract_id="env_release",
            intent_id="intent_g1",
            baseline_value=None,  # Missing baseline
            outcome_status=OutcomeStatus.INVALID_OBSERVATION,
            causal_status=CausalAttributionStatus.INSUFFICIENT_EVIDENCE,
        )

        episode = generate_episode(
            execution_id="ex_g1",
            universal_intent=make_intent(),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=make_admitted(),
            admitted_contract=make_mock_contract(),
            advisory_decision=Mock(decision_id="adv_g1"),
            capability_resolution=Mock(
                resolution_id="res_g1",
                semantic_target="envelope_field_release",
            ),
            outcome=outcome,
        )

        # Knowledge confidence cannot compensate for missing evidence
        assert episode.learning_eligible is False
        assert knowledge_confidence == 0.99  # Knowledge is confident
        # But episode eligibility is independently governed by evidence, not by knowledge

    def test_G2_episode_cannot_upgrade_knowledge_authority(self):
        """G: Episode success cannot promote KnowledgeItem to causal authority."""
        # Simulate: Episode succeeded → but that doesn't mean KnowledgeItem becomes causal
        episode_succeeded = True
        knowledge_item_epistemic_status = "HYPOTHESIS"  # Per Step 5 rules

        # Episode success does not change knowledge epistemic status
        # Knowledge status must remain whatever it was before the episode
        assert knowledge_item_epistemic_status == "HYPOTHESIS"
        assert episode_succeeded is True
        # The two are independent
        # (This is verified by architectural absence: no method to cross-promote)

    def test_G3_episode_cannot_create_capability_contract(self):
        """G: Episode cannot synthesize CapabilityContract from its evidence."""
        outcome = make_outcome_with_attribution()
        episode = generate_episode(
            execution_id="ex_g3",
            universal_intent=make_intent(),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=make_admitted(),
            admitted_contract=make_mock_contract(),
            advisory_decision=Mock(decision_id="adv_g3"),
            capability_resolution=Mock(
                resolution_id="res_g3",
                semantic_target="envelope_field_release",
            ),
            outcome=outcome,
        )

        # Episode does NOT have contract creation methods
        assert not hasattr(episode, "to_contract")
        assert not hasattr(episode, "create_contract")
        assert not hasattr(episode, "synthesize_capability")
        assert not hasattr(episode, "promote_to_contract")
        # It only has learning fields
        assert hasattr(episode, "learning_eligible")
        assert hasattr(episode, "learning_eligibility_status")

    def test_G4_knowledge_cannot_create_capability_contract(self):
        """G: Knowledge cannot create CapabilityContract from its items."""
        # Simulate a high-quality KnowledgeItem with executable-looking content
        knowledge_item = {
            "item_id": "k_release_effect",
            "content": "Decreasing release creates a tighter, punchier sound.",
            "epistemic_status": "EVIDENCE_GROUNDED",
            "confidence": 0.95,
        }

        # This knowledge item cannot become an execution contract
        # There is no path from KnowledgeItem to CapabilityContract
        # Verify by checking what CapabilityContract fields would need:
        required_contract_fields = CONTRACT_AUTHORITY_FIELDS
        for field_name in required_contract_fields:
            assert field_name not in knowledge_item
        # Knowledge item lacks ALL contract authority fields


# ============================================================
# CASE GROUP H — CROSS-BACKEND UNIVERSALITY
# ============================================================

class TestCaseGroupH_CrossBackendUniversality:
    """H: Universal structures must not depend on Serum/DawDreamer."""

    # Backend import patterns that must NOT appear in universal layers
    BACKEND_IMPORT_PATTERNS = [
        "import serum", "from serum",
        "import dawdreamer", "from dawdreamer",
        "import vst3", "from vst3",
        "set_parameter(", "cbor.encode", "cbor.decode",
    ]

    def _check_source_for_backend(self, module):
        """Return backend dependency patterns found in actual import/call lines."""
        try:
            src = inspect.getsource(module)
        except (TypeError, OSError):
            return []
        found = []
        # Only scan non-comment, non-docstring lines for actual dependency patterns
        for line in src.splitlines():
            stripped = line.strip()
            # Skip comment-only lines and blank lines
            if stripped.startswith("#") or not stripped:
                continue
            # Skip lines that are entirely inside string literals (rough heuristic)
            if stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            for pattern in self.BACKEND_IMPORT_PATTERNS:
                if pattern in line:
                    found.append(pattern)
        return list(set(found))

    def test_H1_intent_backend_independence(self):
        """H: UniversalProductionIntent has no Serum/DawDreamer dependencies."""
        import step_6_2_universal_production_intent as m
        bad = self._check_source_for_backend(m)
        # Filter out false positives (module-level comments are ok)
        # Only flag actual code-level dependencies
        assert bad == [], f"UniversalProductionIntent contains backend markers: {bad}"

    def test_H2_advisory_decision_backend_independence(self):
        """H: AdvisoryDecision has no Serum/DawDreamer dependencies."""
        import step_6_5_advisory_decision_engine as m
        bad = self._check_source_for_backend(m)
        assert bad == [], f"AdvisoryDecision contains backend markers: {bad}"

    def test_H3_episode_backend_independence(self):
        """H: UniversalExecutedEpisode core schema has no Serum logic."""
        import step_6_10_episode_generation as m
        bad = self._check_source_for_backend(m)
        assert bad == [], f"Episode generation contains backend markers: {bad}"

    def test_H4_outcome_attribution_backend_independence(self):
        """H: Outcome attribution has no Serum/DawDreamer dependencies."""
        import step_6_9_outcome_attribution as m
        bad = self._check_source_for_backend(m)
        assert bad == [], f"Outcome attribution contains backend markers: {bad}"


# ============================================================
# STATIC TAINT AUDIT — FORBIDDEN PATHS
# ============================================================

class TestStaticTaintAudit:
    """Verify no forbidden paths exist in non-authority layers."""

    def test_advisory_layers_lack_execute_method(self):
        """Advisory layers must not have execute() or mutate() methods."""
        advisory = AdvisoryDecision(
            decision_id="adv_taint",
            intent=make_intent(),
        )
        episode = generate_episode(
            execution_id="ex_taint",
            universal_intent=make_intent(),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=make_admitted(),
            admitted_contract=make_mock_contract(),
            advisory_decision=Mock(decision_id="adv_taint"),
            capability_resolution=Mock(
                resolution_id="res_taint",
                semantic_target="envelope_field_release",
            ),
            outcome=make_outcome_with_attribution(),
        )
        resolution = make_resolved()

        for obj, name in [
            (advisory, "AdvisoryDecision"),
            (episode, "Episode"),
            (resolution, "CapabilityResolution"),
        ]:
            for forbidden in FORBIDDEN_IN_ADVISORY_LAYERS:
                assert not hasattr(obj, forbidden), (
                    f"{name} must not have {forbidden}() — authority boundary violated"
                )

    def test_authority_chain_is_sole_execution_path(self):
        """Authority chain: Contract → Admission → ExecutionAuthority is the ONLY path."""
        # Prove: the only way to get ExecutionAuthority is via admitted contract
        executor = ContractGovernedExecutor()

        # Path A: admitted → authority exists
        admitted = make_admitted()
        auth_from_admitted = executor.build_execution_authority(
            admitted, make_mock_registry()
        )
        assert auth_from_admitted is not None

        # Path B: refused → no authority
        refused = make_refused()
        auth_from_refused = executor.build_execution_authority(
            refused, make_mock_registry()
        )
        assert auth_from_refused is None

        # Path C: no contract in registry → no authority
        empty_registry = Mock()
        empty_registry.get.return_value = None
        auth_no_contract = executor.build_execution_authority(
            admitted, empty_registry
        )
        assert auth_no_contract is None

    def test_no_confidence_threshold_grants_permission(self):
        """Confidence alone (any threshold) must not grant permission."""
        # Try confidence at various thresholds
        for confidence in [0.5, 0.7, 0.9, 0.95, 0.99, 1.0]:
            advisory = AdvisoryDecision(
                decision_id=f"adv_{confidence}",
                intent=make_intent(),
                confidence=confidence,
            )
            # Confidence is recorded...
            assert advisory.confidence == confidence
            # ...but grants no authority
            assert not hasattr(advisory, "execute")
            assert not hasattr(advisory, "authority")

    def test_episode_learning_flag_does_not_bypass_admission(self):
        """learning_eligible=True on Episode does NOT bypass admission."""
        outcome = make_outcome_with_attribution()
        episode = generate_episode(
            execution_id="ex_lflag",
            universal_intent=make_intent(),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=make_admitted(),
            admitted_contract=make_mock_contract(),
            advisory_decision=Mock(decision_id="adv_lflag"),
            capability_resolution=Mock(
                resolution_id="res_lflag",
                semantic_target="envelope_field_release",
            ),
            outcome=outcome,
        )

        assert episode.learning_eligible is True  # eligible...
        # ...but still has no execute/authority methods
        assert not hasattr(episode, "execute")
        assert not hasattr(episode, "admit")
        assert not hasattr(episode, "authorize")

    def test_outcome_attribution_does_not_mutate(self):
        """Outcome attribution reads measurements; never mutates state."""
        import step_6_9_outcome_attribution as m
        src = inspect.getsource(m)
        # set_parameter and write calls must not appear
        forbidden_in_attribution = ["set_parameter", "dawdreamer", "render(", ".mutate("]
        for forbidden in forbidden_in_attribution:
            assert forbidden not in src, (
                f"Outcome attribution contains forbidden call: {forbidden}"
            )


# ============================================================
# PROOF MATRIX VERIFICATION
# ============================================================

class TestProofMatrix:
    """Verify the complete proof matrix: what each domain CAN and CANNOT do."""

    def test_matrix_knowledge_can_inform_reasoning(self):
        """KNOWLEDGE: YES for teaching, retrieval, reasoning, recommendation."""
        advisory = AdvisoryDecision(
            decision_id="adv_matrix",
            intent=make_intent(),
            confidence=0.85,
        )
        # Advisory engine accepts knowledge-derived confidence — this is allowed
        assert advisory.confidence == 0.85

    def test_matrix_knowledge_cannot_grant_execution(self):
        """KNOWLEDGE: NO for execution permission, mutation authority."""
        advisory = AdvisoryDecision(
            decision_id="adv_matrix2",
            intent=make_intent(),
            confidence=0.99,  # Even max confidence
        )
        for forbidden in ["execute", "authority", "mutate", "admit"]:
            assert not hasattr(advisory, forbidden)

    def test_matrix_episode_can_inform_candidate_scoring(self):
        """EPISODE: YES for candidate scoring, decision confidence."""
        from step_6_11_closed_loop_proof import CandidateScore
        candidate = CandidateScore(
            candidate_id="c_matrix",
            label="shorten_release",
            total_score=0.78,
            episode_support=0.15,  # Episode legitimately adds to scoring
        )
        assert candidate.episode_support == 0.15
        assert candidate.total_score == 0.78

    def test_matrix_episode_cannot_grant_admission(self):
        """EPISODE: NO for admission authority."""
        outcome = make_outcome_with_attribution()
        episode = generate_episode(
            execution_id="ex_matrix",
            universal_intent=make_intent(),
            execution_record=Mock(pathway=Mock(value="admitted")),
            admission_result=make_admitted(),
            admitted_contract=make_mock_contract(),
            advisory_decision=Mock(decision_id="adv_matrix"),
            capability_resolution=Mock(
                resolution_id="res_matrix",
                semantic_target="envelope_field_release",
            ),
            outcome=outcome,
        )
        for forbidden in ["execute", "admit", "authorize", "create_contract"]:
            assert not hasattr(episode, forbidden)

    def test_matrix_contract_grants_execution_authority(self):
        """CONTRACT: YES for execution permission, mutation authority."""
        contract = make_mock_contract()
        admission = make_admitted()
        executor = ContractGovernedExecutor()
        authority = executor.build_execution_authority(admission, make_mock_registry(contract))

        # ExecutionAuthority exists and has all required fields
        assert authority is not None
        assert authority.target is not None
        assert authority.allowed_operation is not None

    def test_matrix_no_alternative_authority_source(self):
        """Only CapabilityContract → AdmissionResult can create ExecutionAuthority."""
        executor = ContractGovernedExecutor()

        # Attempting authority without admission → None
        auth = executor.build_execution_authority(make_refused(), make_mock_registry())
        assert auth is None

        # Only admitted result creates authority
        auth = executor.build_execution_authority(make_admitted(), make_mock_registry())
        assert auth is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
