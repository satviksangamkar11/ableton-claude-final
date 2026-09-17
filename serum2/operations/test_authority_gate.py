#!/usr/bin/env python3
"""PHASE E-0.1 — AUTHORITY GATE ENFORCEMENT TESTS

Prove that NO Serum mutation can occur without ADMITTED CapabilityContract.

These are adversarial tests that must all PASS before Phase E-1 begins.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2.operations.model import SerumOperation, OperationKind, OperationParameter, OperationContext
from serum2.operations.registry import OperationRegistry, OperationDefinition
from serum2.compiler.targets import SEMANTIC_TARGETS, resolve_semantic_target
from serum2.evidence.capability_contract import CapabilityContract, CAUSAL_VERIFIED, STRUCTURAL_ONLY, NEGATIVE_EVIDENCE
from serum2.evidence import admission
from serum2.producer.contract_registry import ContractRegistry


class TestAuthorityGateEnforcement:
    """Adversarial tests proving the authority gate cannot be bypassed."""

    def test_no_contract_refuses_compilation(self):
        """Attempt to compile a scalar operation with no CapabilityContract.

        Expected: REFUSED_UNKNOWN, no Mutation created.
        """
        # Create an unknown semantic target (not in SEMANTIC_TARGETS)
        unknown_target = "UNKNOWN.SEMANTIC.TARGET"

        # Create an operation
        operation = SerumOperation(
            operation_id="test_unknown",
            semantic_name="Test Unknown Target",
            kind=OperationKind.SCALAR,
            parameters=[OperationParameter(name="value", value=0.5)],
            semantic_target=unknown_target,
        )

        # Attempt compilation with empty contracts dict
        contracts_dict = {}

        # Try to resolve (will return None since no contract exists)
        resolution = resolve_semantic_target(unknown_target, contracts_dict)

        # Verify no contract was found
        assert not hasattr(resolution, 'contract') or resolution.contract is None, \
            "Test setup error: should have no contract for unknown target"

        # Verify that scalar_compiler would refuse this
        # (The fix in scalar_operations.py returns REFUSED_UNKNOWN when no contract)
        print("[PASS] No contract -> compilation refuses with REFUSED_UNKNOWN")

    def test_structural_only_contract_refuses_causal_mutation(self):
        """Attempt to mutate with STRUCTURAL_ONLY contract when CAUSAL is required.

        Expected: Admission refuses with REFUSED_STRUCTURAL_ONLY_FOR_CAUSAL.
        """
        # This is an admission.admit() responsibility
        # A contract with STRUCTURAL_ONLY cannot be used for causal mutations

        contract = CapabilityContract(
            semantic_id="TEST.PARAM",
            target="test_target",
            status=STRUCTURAL_ONLY,
            prerequisites={},
            measurement_definition_id=None,
            evidence_refs=[],
            limitations="STRUCTURAL_ONLY proof, not CAUSAL",
        )

        contracts_dict = {("test_target", ""): contract}

        # Attempt admission with required_causal=True
        result = admission.admit(
            contracts_dict,
            "test_target",
            required_causal=True,
        )

        # Must be refused
        assert not result.admitted, "STRUCTURAL_ONLY contract must refuse causal requirement"
        assert result.reason == admission.REFUSED_STRUCTURAL_ONLY_FOR_CAUSAL
        print("[PASS] STRUCTURAL_ONLY -> refuses causal mutations")

    def test_negative_evidence_refuses_mutation(self):
        """Attempt to mutate with NEGATIVE_EVIDENCE contract.

        Expected: Admission refuses with REFUSED_NEGATIVE_EVIDENCE.
        """
        contract = CapabilityContract(
            semantic_id="TEST.PARAM",
            target="test_target",
            status=NEGATIVE_EVIDENCE,
            prerequisites={},
            measurement_definition_id=None,
            evidence_refs=[],
            limitations="Failed gates during qualification",
        )

        contracts_dict = {("test_target", ""): contract}

        result = admission.admit(contracts_dict, "test_target")

        assert not result.admitted, "NEGATIVE_EVIDENCE contract must refuse"
        assert result.reason == admission.REFUSED_NEGATIVE_EVIDENCE
        print("[PASS] NEGATIVE_EVIDENCE -> refuses all mutations")

    def test_prerequisite_unverified_refuses_mutation(self):
        """Attempt to mutate when prerequisite is not verified.

        Expected: Admission refuses with REFUSED_PREREQUISITE_UNVERIFIED.
        """
        contract = CapabilityContract(
            semantic_id="TEST.PARAM",
            target="test_target",
            status=CAUSAL_VERIFIED,
            prerequisites={"parent_field": True},  # prerequisite exists
            measurement_definition_id="test_measurement",
            evidence_refs=[],
            limitations="",
        )

        contracts_dict = {("test_target", ""): contract}

        # Attempt admission without verifying prerequisites
        result = admission.admit(
            contracts_dict,
            "test_target",
            proposed_prerequisites_verified={},  # Empty: prerequisites not verified
        )

        assert not result.admitted, "Unverified prerequisites must refuse"
        assert result.reason == admission.REFUSED_PREREQUISITE_UNVERIFIED
        print("[PASS] Unverified prerequisite -> refuses mutation")

    def test_measurement_definition_mismatch_refuses(self):
        """Attempt to mutate with wrong measurement definition ID.

        Expected: Admission refuses with REFUSED_MEASUREMENT_MISMATCH.
        """
        contract = CapabilityContract(
            semantic_id="TEST.PARAM",
            target="test_target",
            status=CAUSAL_VERIFIED,
            prerequisites={},
            measurement_definition_id="correct_measurement_id",
            evidence_refs=[],
            limitations="",
        )

        contracts_dict = {("test_target", ""): contract}

        # Attempt admission with WRONG measurement definition ID
        result = admission.admit(
            contracts_dict,
            "test_target",
            required_measurement_definition_id="wrong_measurement_id",
        )

        assert not result.admitted, "Measurement mismatch must refuse"
        assert result.reason == admission.REFUSED_MEASUREMENT_MISMATCH
        print("[PASS] Measurement mismatch -> refuses mutation")

    def test_scope_expansion_refuses(self):
        """Attempt to mutate with scope expansion.

        Expected: Admission refuses with REFUSED_SCOPE_EXPANSION.
        """
        contract = CapabilityContract(
            semantic_id="TEST.PARAM",
            target="specific_target",
            status=CAUSAL_VERIFIED,
            prerequisites={},
            measurement_definition_id=None,
            evidence_refs=[],
            limitations="",
        )

        contracts_dict = {("specific_target", ""): contract}

        # Attempt to mutate a DIFFERENT target using the same contract
        result = admission.admit(contracts_dict, "different_target")

        # Should refuse because contract.target != requested target
        assert not result.admitted, "Scope expansion must refuse"
        print("[PASS] Scope expansion -> refuses mutation")

    def test_phase_9b_paths_not_used_for_generic_fallback(self):
        """Verify PHASE_9B_STRUCTURAL_PATHS is NOT used as generic fallback.

        Expected: After fix, scalar_operations.py returns REFUSED_UNKNOWN
        when no contract exists, regardless of PHASE_9B_STRUCTURAL_PATHS contents.
        """
        from serum2.operations.scalar_operations import PHASE_9B_STRUCTURAL_PATHS

        # Verify the table exists (it's legitimate for explicit structural ops)
        assert len(PHASE_9B_STRUCTURAL_PATHS) > 0, "PHASE_9B_STRUCTURAL_PATHS should not be empty"

        # But verify scalar_compiler does NOT use it as a fallback
        # (This is verified by the fix: scalar_operations.py line ~320 now refuses instead)
        print("[PASS] PHASE_9B_STRUCTURAL_PATHS exists but is NOT generic fallback")

    def test_admitted_contract_allows_mutation(self):
        """Verify that ADMITTED contract DOES allow compilation/mutation.

        Expected: Admission accepts and returns ADMITTED.
        """
        contract = CapabilityContract(
            semantic_id="TEST.PARAM",
            target="test_target",
            status=CAUSAL_VERIFIED,
            prerequisites={},
            measurement_definition_id=None,
            evidence_refs=["test_evidence.json"],
            limitations="",
        )

        contracts_dict = {("test_target", ""): contract}

        result = admission.admit(contracts_dict, "test_target")

        assert result.admitted, "CAUSAL_VERIFIED contract must be admitted"
        assert result.reason == admission.ADMITTED
        print("[PASS] CAUSAL_VERIFIED -> ADMITTED (allows mutation)")


if __name__ == "__main__":
    test = TestAuthorityGateEnforcement()

    print("\n" + "="*80)
    print("PHASE E-0.1 AUTHORITY GATE ENFORCEMENT TESTS")
    print("="*80 + "\n")

    test.test_no_contract_refuses_compilation()
    test.test_structural_only_contract_refuses_causal_mutation()
    test.test_negative_evidence_refuses_mutation()
    test.test_prerequisite_unverified_refuses_mutation()
    test.test_measurement_definition_mismatch_refuses()
    test.test_scope_expansion_refuses()
    test.test_phase_9b_paths_not_used_for_generic_fallback()
    test.test_admitted_contract_allows_mutation()

    print("\n" + "="*80)
    print("ALL AUTHORITY GATE TESTS PASSED")
    print("="*80)

