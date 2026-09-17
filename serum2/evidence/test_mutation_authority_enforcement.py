#!/usr/bin/env python3
"""PHASE E-0.1B ADVERSARIAL TESTS — ZERO MUTATION ON REFUSAL

Prove that every refusal class produces ZERO Serum mutation.

These tests MUST ALL PASS before Phase E-1 begins.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2.evidence.mutation_executor import execute_mutation_with_authority, assert_mutation_authority
from serum2.evidence.capability_contract import CapabilityContract
from serum2.evidence import admission
from serum2 import pathmerge


class TestMutationAuthorityEnforcement:
    """Prove zero mutation when admission refuses."""

    def setup_test_body(self):
        """Create a minimal test Serum body."""
        return {
            "Oscillator0": {
                "plainParams": {
                    "kParamLevel": 0.5,
                    "kParamDetune": 0.0,
                }
            },
            "VoiceFilter0": {
                "plainParams": {
                    "kParamCutoff": 0.7,
                }
            }
        }

    def test_no_contract_produces_zero_mutation(self):
        """No contract -> REFUSED_UNKNOWN -> no mutation."""
        body = self.setup_test_body()
        baseline_cutoff = pathmerge.read_path_value(body, "VoiceFilter0.plainParams.kParamCutoff")

        # Execute with no contracts
        proof = execute_mutation_with_authority(
            body,
            target="FILTER1.CUTOFF",
            mutation_value=0.9,
            contracts={},  # Empty: no contract
        )

        # Verify refusal
        assert not proof.admission_result.admitted
        assert proof.admission_result.reason == admission.REFUSED_UNKNOWN

        # Verify zero mutation
        assert_mutation_authority(proof)
        assert not proof.executed
        assert not proof.serum_state_changed

        # Verify Serum state unchanged
        post_cutoff = pathmerge.read_path_value(body, "VoiceFilter0.plainParams.kParamCutoff")
        assert post_cutoff == baseline_cutoff, "ZERO MUTATION VIOLATED: state changed despite REFUSED"

        print("[PASS] no_contract -> REFUSED_UNKNOWN -> zero mutation")

    def test_structural_only_produces_zero_mutation(self):
        """STRUCTURAL_ONLY contract + causal requirement -> refused -> no mutation."""
        body = self.setup_test_body()
        baseline_level = pathmerge.read_path_value(body, "Oscillator0.plainParams.kParamLevel")

        # Contract with STRUCTURAL_ONLY
        contract = CapabilityContract(
            target="osc_level",
            allowed_operation="set",
            status="STRUCTURAL_ONLY",
            prerequisites=(),
            verified={},
            measurement=None,
            scope={},
            provenance={},
            limitations=(),
        )
        contracts_dict = {("osc_level", ""): contract}

        # Execute with required_causal=True
        proof = execute_mutation_with_authority(
            body,
            target="osc_level",
            mutation_value=0.8,
            contracts=contracts_dict,
            required_causal=True,  # Demand CAUSAL_VERIFIED
        )

        # Verify refusal
        assert not proof.admission_result.admitted
        assert proof.admission_result.reason == admission.REFUSED_STRUCTURAL_ONLY_FOR_CAUSAL

        # Verify zero mutation
        assert_mutation_authority(proof)
        assert not proof.executed
        assert not proof.serum_state_changed

        # Verify Serum state unchanged
        post_level = pathmerge.read_path_value(body, "Oscillator0.plainParams.kParamLevel")
        assert post_level == baseline_level, "ZERO MUTATION VIOLATED"

        print("[PASS] STRUCTURAL_ONLY + causal -> refused -> zero mutation")

    def test_negative_evidence_produces_zero_mutation(self):
        """NEGATIVE_EVIDENCE -> refused -> no mutation."""
        body = self.setup_test_body()
        baseline_level = pathmerge.read_path_value(body, "Oscillator0.plainParams.kParamLevel")

        contract = CapabilityContract(
            target="osc_level",
            allowed_operation="set",
            status="NEGATIVE_EVIDENCE",
            prerequisites=(),
            verified={},
            measurement=None,
            scope={},
            provenance={},
            limitations=("Failed gate during qualification",),
        )
        contracts_dict = {("osc_level", ""): contract}

        proof = execute_mutation_with_authority(
            body,
            target="osc_level",
            mutation_value=0.8,
            contracts=contracts_dict,
        )

        assert not proof.admission_result.admitted
        assert proof.admission_result.reason == admission.REFUSED_NEGATIVE_EVIDENCE
        assert_mutation_authority(proof)

        post_level = pathmerge.read_path_value(body, "Oscillator0.plainParams.kParamLevel")
        assert post_level == baseline_level

        print("[PASS] NEGATIVE_EVIDENCE -> refused -> zero mutation")

    def test_prerequisite_unverified_produces_zero_mutation(self):
        """Unverified prerequisite -> REFUSED_PREREQUISITE_UNVERIFIED -> no mutation."""
        body = self.setup_test_body()
        baseline_cutoff = pathmerge.read_path_value(body, "VoiceFilter0.plainParams.kParamCutoff")

        contract = CapabilityContract(
            target="filter_cutoff",
            allowed_operation="set",
            status="CAUSAL_VERIFIED",
            prerequisites=({"field_path": "FilterType", "value": "LP"},),  # Prerequisite required
            verified={},
            measurement=None,
            scope={},
            provenance={},
            limitations=(),
        )
        contracts_dict = {("filter_cutoff", ""): contract}

        # Attempt WITHOUT verifying prerequisites
        proof = execute_mutation_with_authority(
            body,
            target="filter_cutoff",
            mutation_value=0.5,
            contracts=contracts_dict,
            proposed_prerequisites_verified={},  # Empty: not verified
        )

        assert not proof.admission_result.admitted
        assert proof.admission_result.reason == admission.REFUSED_PREREQUISITE_UNVERIFIED
        assert_mutation_authority(proof)

        post_cutoff = pathmerge.read_path_value(body, "VoiceFilter0.plainParams.kParamCutoff")
        assert post_cutoff == baseline_cutoff

        print("[PASS] prerequisite_unverified -> REFUSED_PREREQUISITE_UNVERIFIED -> zero mutation")

    def test_measurement_mismatch_produces_zero_mutation(self):
        """Measurement ID mismatch -> REFUSED_MEASUREMENT_MISMATCH -> no mutation."""
        body = self.setup_test_body()
        baseline_level = pathmerge.read_path_value(body, "Oscillator0.plainParams.kParamLevel")

        contract = CapabilityContract(
            target="osc_level",
            allowed_operation="set",
            status="CAUSAL_VERIFIED",
            prerequisites=(),
            verified={},
            measurement=None,
            scope={},
            provenance={},
            limitations=(),
        )
        contracts_dict = {("osc_level", ""): contract}

        # Request with measurement ID that doesn't match contract
        proof = execute_mutation_with_authority(
            body,
            target="osc_level",
            mutation_value=0.8,
            contracts=contracts_dict,
            required_measurement_definition_id="tone_brightness",  # Specific ID required
        )

        assert not proof.admission_result.admitted
        assert proof.admission_result.reason == admission.REFUSED_MEASUREMENT_MISMATCH
        assert_mutation_authority(proof)

        post_level = pathmerge.read_path_value(body, "Oscillator0.plainParams.kParamLevel")
        assert post_level == baseline_level

        print("[PASS] measurement_mismatch -> REFUSED_MEASUREMENT_MISMATCH -> zero mutation")

    def test_scope_expansion_produces_zero_mutation(self):
        """Scope expansion (contract for different target) -> refused -> no mutation."""
        body = self.setup_test_body()
        baseline_cutoff = pathmerge.read_path_value(body, "VoiceFilter0.plainParams.kParamCutoff")

        contract = CapabilityContract(
            target="oscillator_level",  # Contract is for OSC level
            allowed_operation="set",
            status="CAUSAL_VERIFIED",
            prerequisites=(),
            verified={},
            measurement=None,
            scope={},
            provenance={},
            limitations=(),
        )
        contracts_dict = {("oscillator_level", ""): contract}

        # Attempt to use contract for DIFFERENT target
        proof = execute_mutation_with_authority(
            body,
            target="filter_cutoff",  # Requesting filter cutoff
            mutation_value=0.5,
            contracts=contracts_dict,
        )

        assert not proof.admission_result.admitted
        # This may be REFUSED_UNKNOWN (no contract for filter_cutoff) or REFUSED_SCOPE_EXPANSION
        assert_mutation_authority(proof)

        post_cutoff = pathmerge.read_path_value(body, "VoiceFilter0.plainParams.kParamCutoff")
        assert post_cutoff == baseline_cutoff

        print("[PASS] scope_expansion -> refused -> zero mutation")

    def test_admitted_contract_allows_mutation(self):
        """CAUSAL_VERIFIED -> ADMITTED -> mutation occurs."""
        body = self.setup_test_body()
        baseline_level = pathmerge.read_path_value(body, "Oscillator0.plainParams.kParamLevel")

        contract = CapabilityContract(
            target="osc_level",
            allowed_operation="set",
            status="CAUSAL_VERIFIED",
            prerequisites=(),
            verified={},
            measurement=None,
            scope={"mutation_target_path": "Oscillator0.plainParams.kParamLevel"},
            provenance={},
            limitations=(),
        )
        contracts_dict = {("osc_level", ""): contract}

        proof = execute_mutation_with_authority(
            body,
            target="osc_level",
            mutation_value=0.8,
            contracts=contracts_dict,
        )

        assert proof.admission_result.admitted
        assert proof.executed
        assert proof.serum_state_changed

        post_level = pathmerge.read_path_value(body, "Oscillator0.plainParams.kParamLevel")
        assert post_level == 0.8, "CAUSAL_VERIFIED mutation should have executed"

        print("[PASS] CAUSAL_VERIFIED -> ADMITTED -> mutation executed")


if __name__ == "__main__":
    test = TestMutationAuthorityEnforcement()

    print("\n" + "="*80)
    print("PHASE E-0.1B ADVERSARIAL ZERO-MUTATION TESTS")
    print("="*80 + "\n")

    test.test_no_contract_produces_zero_mutation()
    test.test_structural_only_produces_zero_mutation()
    test.test_negative_evidence_produces_zero_mutation()
    test.test_prerequisite_unverified_produces_zero_mutation()
    test.test_measurement_mismatch_produces_zero_mutation()
    test.test_scope_expansion_produces_zero_mutation()
    test.test_admitted_contract_allows_mutation()

    print("\n" + "="*80)
    print("ALL ZERO-MUTATION TESTS PASSED")
    print("="*80 + "\n")
    print("PHASE E-0.1B VERDICT: AUTHORITY ENFORCEMENT FUNCTIONAL")
    print("Refused operations -> zero mutation: PROVEN")

