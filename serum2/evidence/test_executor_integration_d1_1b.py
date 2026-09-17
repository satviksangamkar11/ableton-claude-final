#!/usr/bin/env python3
"""PHASE E-0.1D.1B — EXECUTOR INTEGRATION TESTS + ZERO-MUTATION ADVERSARIAL SUITE

Proof that:
1. Every refusal produces zero mutation
2. Authoritative binding comes from contract.execution_binding
3. Missing caller assertion is allowed when binding exists
4. Wrong caller assertion causes refusal
5. Invocation count independent from state_changed boolean
6. All admitted operations execute exactly once
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding
from serum2.evidence import admission
from serum2 import pathmerge


class InstrumentedSynth:
    """Fake synth that records all set_parameter calls."""

    def __init__(self):
        self.set_parameter_calls = []
        self.parameters = {
            0: 0.5,  # "Env 1 Release"
            1: 0.7,  # "Osc 1 Level"
            2: 0.3,  # "Filter Cutoff"
        }
        self.param_names = {
            "Env 1 Release": 0,
            "Osc 1 Level": 1,
            "Filter Cutoff": 2,
        }

    def get_parameters_description(self):
        return [
            {"name": "Env 1 Release", "index": 0},
            {"name": "Osc 1 Level", "index": 1},
            {"name": "Filter Cutoff", "index": 2},
        ]

    def set_parameter(self, index, value):
        """Record call, set value."""
        self.set_parameter_calls.append((index, value))
        self.parameters[index] = value

    def get_parameter(self, index):
        """Retrieve current value."""
        return self.parameters.get(index, 0.0)


class PathmergeCallCounter:
    """Wrapper to count pathmerge.apply_path_value invocations."""

    def __init__(self):
        self.call_count = 0
        self.original_apply = pathmerge.apply_path_value

    def wrapped_apply(self, body, path, value):
        """Record call and delegate to real apply_path_value."""
        self.call_count += 1
        return self.original_apply(body, path, value)

    def install(self):
        """Install wrapper."""
        pathmerge.apply_path_value = self.wrapped_apply

    def uninstall(self):
        """Restore original."""
        pathmerge.apply_path_value = self.original_apply

    def reset(self):
        """Reset counter."""
        self.call_count = 0


class TestExecutorIntegration:
    """Full integration test matrix for executor + instrumentation."""

    def setup_test_body(self):
        """Create minimal test body."""
        return {
            "Envelope0": {
                "plainParams": {
                    "kParamRelease": 0.5,
                    "kParamAttack": 0.1,
                }
            },
            "Oscillator0": {
                "plainParams": {
                    "kParamLevel": 0.7,
                }
            },
            "VoiceFilter0": {
                "plainParams": {
                    "kParamCutoff": 0.3,
                }
            }
        }

    def make_contract(self, target, status, has_binding=True, binding_type=None, body_path=None, host_param=None):
        """Factory for test contracts."""
        binding = None
        if has_binding and binding_type:
            binding = ExecutionBinding(
                mutation_type=binding_type,
                body_path=body_path,
                host_parameter_name=host_param,
                binding_source="test",
                binding_version="1.0",
            )

        return CapabilityContract(
            target=target,
            allowed_operation="mutate_numeric_value",
            status=status,
            prerequisites=(),
            verified={},
            measurement=None,
            scope={},
            provenance={},
            execution_binding=binding,
            limitations=(),
        )

    def test_no_contract_produces_zero_mutation(self):
        """No contract -> REFUSED_UNKNOWN -> 0 calls."""
        body = self.setup_test_body()
        synth = InstrumentedSynth()
        pm_counter = PathmergeCallCounter()
        pm_counter.install()

        try:
            baseline_level = synth.get_parameter(1)

            request = MutationRequest(
                target="OSC1.LEVEL",
                mutation_type=MutationType.HOST_PARAMETER,
                value=0.8,
                host_parameter_name="Osc 1 Level",
            )

            proof = execute_mutation_request_with_authority(
                request=request,
                body=body,
                contracts={},
                synth=synth,
            )

            assert not proof.admission_result.admitted, "Should refuse (no contract)"
            assert not proof.executed, "Should not execute"
            assert proof.set_parameter_call_count == 0, "Zero set_parameter calls"
            assert pm_counter.call_count == 0, "Zero pathmerge calls"
            assert synth.get_parameter(1) == baseline_level, "State unchanged"

            print("[PASS] no_contract -> REFUSED_UNKNOWN -> zero mutation")
        finally:
            pm_counter.uninstall()

    def test_structural_only_refused(self):
        """STRUCTURAL_ONLY -> REFUSED -> 0 calls."""
        body = self.setup_test_body()
        synth = InstrumentedSynth()

        contract = self.make_contract(
            "OSC1.LEVEL",
            "STRUCTURAL_ONLY",
            has_binding=True,
            binding_type="HOST_PARAMETER",
            host_param="Osc 1 Level",
        )
        contracts = {("OSC1.LEVEL", ""): contract}

        baseline_level = synth.get_parameter(1)

        request = MutationRequest(
            target="OSC1.LEVEL",
            mutation_type=MutationType.HOST_PARAMETER,
            value=0.8,
            required_causal=True,
        )

        proof = execute_mutation_request_with_authority(
            request=request,
            body=body,
            contracts=contracts,
            synth=synth,
        )

        assert not proof.admission_result.admitted, "Should refuse (STRUCTURAL_ONLY + causal)"
        assert proof.set_parameter_call_count == 0, "Zero set_parameter"
        assert synth.get_parameter(1) == baseline_level, "State unchanged"

        print("[PASS] STRUCTURAL_ONLY + causal -> refused -> zero mutation")

    def test_negative_evidence_refused(self):
        """NEGATIVE_EVIDENCE -> REFUSED -> 0 calls."""
        body = self.setup_test_body()
        synth = InstrumentedSynth()

        contract = self.make_contract(
            "OSC1.LEVEL",
            "NEGATIVE_EVIDENCE",
            has_binding=True,
            binding_type="HOST_PARAMETER",
            host_param="Osc 1 Level",
        )
        contracts = {("OSC1.LEVEL", ""): contract}

        baseline_level = synth.get_parameter(1)

        request = MutationRequest(
            target="OSC1.LEVEL",
            mutation_type=MutationType.HOST_PARAMETER,
            value=0.8,
        )

        proof = execute_mutation_request_with_authority(
            request=request,
            body=body,
            contracts=contracts,
            synth=synth,
        )

        assert not proof.admission_result.admitted, "Should refuse (NEGATIVE_EVIDENCE)"
        assert proof.set_parameter_call_count == 0, "Zero set_parameter"
        assert synth.get_parameter(1) == baseline_level, "State unchanged"

        print("[PASS] NEGATIVE_EVIDENCE -> refused -> zero mutation")

    def test_missing_binding_refused(self):
        """Admitted contract but no execution_binding -> REFUSED -> 0 calls."""
        body = self.setup_test_body()
        synth = InstrumentedSynth()

        contract = self.make_contract(
            "OSC1.LEVEL",
            "CAUSAL_VERIFIED",
            has_binding=False,
        )
        contracts = {("OSC1.LEVEL", ""): contract}

        baseline_level = synth.get_parameter(1)

        request = MutationRequest(
            target="OSC1.LEVEL",
            mutation_type=MutationType.HOST_PARAMETER,
            value=0.8,
        )

        proof = execute_mutation_request_with_authority(
            request=request,
            body=body,
            contracts=contracts,
            synth=synth,
        )

        assert proof.admission_result.admitted, "Admission should pass"
        assert not proof.executed, "Should not execute (no binding)"
        assert proof.set_parameter_call_count == 0, "Zero set_parameter"
        assert synth.get_parameter(1) == baseline_level, "State unchanged"

        print("[PASS] missing binding -> refused -> zero mutation")

    def test_type_mismatch_refused(self):
        """Binding type mismatch -> REFUSED -> 0 calls."""
        body = self.setup_test_body()
        synth = InstrumentedSynth()

        contract = self.make_contract(
            "FILTER.CUTOFF",
            "CAUSAL_VERIFIED",
            has_binding=True,
            binding_type="HOST_PARAMETER",
            host_param="Filter Cutoff",
        )
        contracts = {("FILTER.CUTOFF", ""): contract}

        baseline_cutoff = pathmerge.read_path_value(body, "VoiceFilter0.plainParams.kParamCutoff")

        request = MutationRequest(
            target="FILTER.CUTOFF",
            mutation_type=MutationType.BODY_STATE,
            value=0.5,
        )

        proof = execute_mutation_request_with_authority(
            request=request,
            body=body,
            contracts=contracts,
            synth=synth,
        )

        assert proof.admission_result.admitted, "Admission should pass"
        assert not proof.executed, "Should not execute (type mismatch)"
        assert proof.set_parameter_call_count == 0, "Zero set_parameter"
        assert pathmerge.read_path_value(body, "VoiceFilter0.plainParams.kParamCutoff") == baseline_cutoff

        print("[PASS] type mismatch -> refused -> zero mutation")

    def test_wrong_host_assertion_refused(self):
        """Wrong host_parameter_name assertion -> REFUSED -> 0 calls."""
        body = self.setup_test_body()
        synth = InstrumentedSynth()

        contract = self.make_contract(
            "OSC1.LEVEL",
            "CAUSAL_VERIFIED",
            has_binding=True,
            binding_type="HOST_PARAMETER",
            host_param="Osc 1 Level",
        )
        contracts = {("OSC1.LEVEL", ""): contract}

        baseline_level = synth.get_parameter(1)

        request = MutationRequest(
            target="OSC1.LEVEL",
            mutation_type=MutationType.HOST_PARAMETER,
            value=0.8,
            host_parameter_name="Wrong Name",
        )

        proof = execute_mutation_request_with_authority(
            request=request,
            body=body,
            contracts=contracts,
            synth=synth,
        )

        assert proof.admission_result.admitted, "Admission should pass"
        assert not proof.executed, "Should not execute (wrong assertion)"
        assert proof.set_parameter_call_count == 0, "Zero set_parameter"
        assert synth.get_parameter(1) == baseline_level, "State unchanged"

        print("[PASS] wrong host assertion -> refused -> zero mutation")

    def test_wrong_body_path_assertion_refused(self):
        """Wrong body_path assertion -> REFUSED -> 0 calls."""
        body = self.setup_test_body()
        synth = InstrumentedSynth()
        pm_counter = PathmergeCallCounter()
        pm_counter.install()

        try:
            contract = self.make_contract(
                "FILTER.CUTOFF",
                "CAUSAL_VERIFIED",
                has_binding=True,
                binding_type="BODY_STATE",
                body_path="VoiceFilter0.plainParams.kParamCutoff",
            )
            contracts = {("FILTER.CUTOFF", ""): contract}

            baseline_cutoff = pathmerge.read_path_value(body, "VoiceFilter0.plainParams.kParamCutoff")

            request = MutationRequest(
                target="FILTER.CUTOFF",
                mutation_type=MutationType.BODY_STATE,
                value=0.5,
                body_path="Wrong.Path.Here",
            )

            proof = execute_mutation_request_with_authority(
                request=request,
                body=body,
                contracts=contracts,
                synth=synth,
            )

            assert proof.admission_result.admitted, "Admission should pass"
            assert not proof.executed, "Should not execute (wrong assertion)"
            assert pm_counter.call_count == 0, "Zero pathmerge calls"
            assert pathmerge.read_path_value(body, "VoiceFilter0.plainParams.kParamCutoff") == baseline_cutoff

            print("[PASS] wrong body_path assertion -> refused -> zero mutation")
        finally:
            pm_counter.uninstall()

    def test_host_parameter_no_assertion_admitted(self):
        """HOST_PARAMETER, no assertion, valid binding -> ADMITTED, 1 call."""
        body = self.setup_test_body()
        synth = InstrumentedSynth()

        contract = self.make_contract(
            "OSC1.LEVEL",
            "CAUSAL_VERIFIED",
            has_binding=True,
            binding_type="HOST_PARAMETER",
            host_param="Osc 1 Level",
        )
        contracts = {("OSC1.LEVEL", ""): contract}

        request = MutationRequest(
            target="OSC1.LEVEL",
            mutation_type=MutationType.HOST_PARAMETER,
            value=0.8,
        )

        proof = execute_mutation_request_with_authority(
            request=request,
            body=body,
            contracts=contracts,
            synth=synth,
        )

        assert proof.admission_result.admitted, "Admission should pass"
        assert proof.executed, "Should execute"
        assert len(synth.set_parameter_calls) == 1, "Exactly 1 set_parameter call"
        assert proof.set_parameter_call_count == 1, "Proof reports 1 call"
        assert synth.get_parameter(1) == 0.8, "Value changed"

        print("[PASS] HOST_PARAMETER no assertion -> admitted -> 1 call")

    def test_host_parameter_correct_assertion_admitted(self):
        """HOST_PARAMETER, correct assertion, valid binding -> ADMITTED, 1 call."""
        body = self.setup_test_body()
        synth = InstrumentedSynth()

        contract = self.make_contract(
            "OSC1.LEVEL",
            "CAUSAL_VERIFIED",
            has_binding=True,
            binding_type="HOST_PARAMETER",
            host_param="Osc 1 Level",
        )
        contracts = {("OSC1.LEVEL", ""): contract}

        request = MutationRequest(
            target="OSC1.LEVEL",
            mutation_type=MutationType.HOST_PARAMETER,
            value=0.8,
            host_parameter_name="Osc 1 Level",
        )

        proof = execute_mutation_request_with_authority(
            request=request,
            body=body,
            contracts=contracts,
            synth=synth,
        )

        assert proof.admission_result.admitted, "Admission should pass"
        assert proof.executed, "Should execute"
        assert len(synth.set_parameter_calls) == 1, "Exactly 1 set_parameter call"
        assert proof.set_parameter_call_count == 1, "Proof reports 1 call"
        assert synth.get_parameter(1) == 0.8, "Value changed"

        print("[PASS] HOST_PARAMETER correct assertion -> admitted -> 1 call")

    def test_host_parameter_same_value_still_counts_invocation(self):
        """HOST_PARAMETER same value: invocation ≠ state_changed."""
        body = self.setup_test_body()
        synth = InstrumentedSynth()
        synth.parameters[1] = 0.8

        contract = self.make_contract(
            "OSC1.LEVEL",
            "CAUSAL_VERIFIED",
            has_binding=True,
            binding_type="HOST_PARAMETER",
            host_param="Osc 1 Level",
        )
        contracts = {("OSC1.LEVEL", ""): contract}

        request = MutationRequest(
            target="OSC1.LEVEL",
            mutation_type=MutationType.HOST_PARAMETER,
            value=0.8,
        )

        proof = execute_mutation_request_with_authority(
            request=request,
            body=body,
            contracts=contracts,
            synth=synth,
        )

        assert proof.executed, "Should execute"
        assert len(synth.set_parameter_calls) == 1, "Exactly 1 set_parameter call"
        assert proof.set_parameter_call_count == 1, "Proof reports 1 invocation"
        assert not proof.mutation_succeeded, "State did not change"

        print("[PASS] HOST_PARAMETER same-value: 1 call, 0 state_changed")

    def test_body_state_no_assertion_admitted(self):
        """BODY_STATE, no assertion, valid binding -> ADMITTED, 1 call."""
        body = self.setup_test_body()
        synth = InstrumentedSynth()
        pm_counter = PathmergeCallCounter()
        pm_counter.install()

        try:
            contract = self.make_contract(
                "FILTER.CUTOFF",
                "CAUSAL_VERIFIED",
                has_binding=True,
                binding_type="BODY_STATE",
                body_path="VoiceFilter0.plainParams.kParamCutoff",
            )
            contracts = {("FILTER.CUTOFF", ""): contract}

            request = MutationRequest(
                target="FILTER.CUTOFF",
                mutation_type=MutationType.BODY_STATE,
                value=0.5,
            )

            proof = execute_mutation_request_with_authority(
                request=request,
                body=body,
                contracts=contracts,
                synth=synth,
            )

            assert proof.executed, "Should execute"
            assert pm_counter.call_count == 1, "Exactly 1 pathmerge call"
            assert proof.pathmerge_call_count == 1, "Proof reports 1 call"
            assert pathmerge.read_path_value(body, "VoiceFilter0.plainParams.kParamCutoff") == 0.5

            print("[PASS] BODY_STATE no assertion -> admitted -> 1 call")
        finally:
            pm_counter.uninstall()

    def test_body_state_correct_assertion_admitted(self):
        """BODY_STATE, correct assertion, valid binding -> ADMITTED, 1 call."""
        body = self.setup_test_body()
        synth = InstrumentedSynth()
        pm_counter = PathmergeCallCounter()
        pm_counter.install()

        try:
            contract = self.make_contract(
                "FILTER.CUTOFF",
                "CAUSAL_VERIFIED",
                has_binding=True,
                binding_type="BODY_STATE",
                body_path="VoiceFilter0.plainParams.kParamCutoff",
            )
            contracts = {("FILTER.CUTOFF", ""): contract}

            request = MutationRequest(
                target="FILTER.CUTOFF",
                mutation_type=MutationType.BODY_STATE,
                value=0.5,
                body_path="VoiceFilter0.plainParams.kParamCutoff",
            )

            proof = execute_mutation_request_with_authority(
                request=request,
                body=body,
                contracts=contracts,
                synth=synth,
            )

            assert proof.executed, "Should execute"
            assert pm_counter.call_count == 1, "Exactly 1 pathmerge call"
            assert proof.pathmerge_call_count == 1, "Proof reports 1 call"

            print("[PASS] BODY_STATE correct assertion -> admitted -> 1 call")
        finally:
            pm_counter.uninstall()

    def test_body_state_same_value_still_counts_invocation(self):
        """BODY_STATE same value: invocation ≠ state_changed."""
        body = self.setup_test_body()
        synth = InstrumentedSynth()
        pm_counter = PathmergeCallCounter()
        pm_counter.install()

        try:
            pathmerge.apply_path_value(body, "VoiceFilter0.plainParams.kParamCutoff", 0.5)
            pm_counter.reset()

            contract = self.make_contract(
                "FILTER.CUTOFF",
                "CAUSAL_VERIFIED",
                has_binding=True,
                binding_type="BODY_STATE",
                body_path="VoiceFilter0.plainParams.kParamCutoff",
            )
            contracts = {("FILTER.CUTOFF", ""): contract}

            request = MutationRequest(
                target="FILTER.CUTOFF",
                mutation_type=MutationType.BODY_STATE,
                value=0.5,
            )

            proof = execute_mutation_request_with_authority(
                request=request,
                body=body,
                contracts=contracts,
                synth=synth,
            )

            assert proof.executed, "Should execute"
            assert pm_counter.call_count == 1, "Exactly 1 pathmerge call"
            assert proof.pathmerge_call_count == 1, "Proof reports 1 invocation"
            assert not proof.mutation_succeeded, "State did not change"

            print("[PASS] BODY_STATE same-value: 1 call, 0 state_changed")
        finally:
            pm_counter.uninstall()

    def test_topology_without_binding_refused(self):
        """TOPOLOGY with no execution_binding on the contract -> refused,
        zero mutation. (TOPOLOGY dispatch itself is now implemented for
        proven operations -- see test_topology_resolver_integration.py and
        test_topology_real_serum_roundtrip.py for the full adversarial and
        real-Serum suites; this test only proves the missing-binding case.)"""
        body = self.setup_test_body()
        synth = InstrumentedSynth()

        contract = self.make_contract(
            "FX.ENABLE",
            "CAUSAL_VERIFIED",
            has_binding=False,
        )
        contracts = {("FX.ENABLE", ""): contract}

        request = MutationRequest(
            target="FX.ENABLE",
            mutation_type=MutationType.TOPOLOGY,
            value=True,
        )

        proof = execute_mutation_request_with_authority(
            request=request,
            body=body,
            contracts=contracts,
            synth=synth,
        )

        assert not proof.executed, "Should not execute"
        assert proof.set_parameter_call_count == 0, "Zero calls"
        assert "No TOPOLOGY execution binding in contract" in (proof.detail or "")

        print("[PASS] TOPOLOGY without execution_binding -> refused -> zero mutation")

    def test_compound_without_binding_refused(self):
        """COMPOUND with no execution_binding on the contract -> refused,
        zero mutation. (COMPOUND dispatch itself is now implemented -- see
        test_compound_resolver_integration.py for the full resolver-backed
        adversarial suite; this test only proves the missing-binding case
        specifically, which is what this contract fixture represents.)"""
        body = self.setup_test_body()
        synth = InstrumentedSynth()

        contract = self.make_contract(
            "CHORD.VOICING",
            "CAUSAL_VERIFIED",
            has_binding=False,
        )
        contracts = {("CHORD.VOICING", ""): contract}

        request = MutationRequest(
            target="CHORD.VOICING",
            mutation_type=MutationType.COMPOUND,
            value={"root": 60, "voicing": [0, 4, 7]},
        )

        proof = execute_mutation_request_with_authority(
            request=request,
            body=body,
            contracts=contracts,
            synth=synth,
        )

        assert not proof.executed, "Should not execute"
        assert proof.set_parameter_call_count == 0, "Zero calls"
        assert "No COMPOUND execution binding in contract" in (proof.detail or "")

        print("[PASS] COMPOUND without execution_binding -> refused -> zero mutation")


if __name__ == "__main__":
    test = TestExecutorIntegration()

    print("\n" + "="*80)
    print("PHASE E-0.1D.1B — EXECUTOR INTEGRATION + ZERO-MUTATION ADVERSARIAL TESTS")
    print("="*80 + "\n")

    test.test_no_contract_produces_zero_mutation()
    test.test_structural_only_refused()
    test.test_negative_evidence_refused()
    test.test_missing_binding_refused()
    test.test_type_mismatch_refused()
    test.test_wrong_host_assertion_refused()
    test.test_wrong_body_path_assertion_refused()
    test.test_host_parameter_no_assertion_admitted()
    test.test_host_parameter_correct_assertion_admitted()
    test.test_host_parameter_same_value_still_counts_invocation()
    test.test_body_state_no_assertion_admitted()
    test.test_body_state_correct_assertion_admitted()
    test.test_body_state_same_value_still_counts_invocation()
    test.test_topology_without_binding_refused()
    test.test_compound_without_binding_refused()

    print("\n" + "="*80)
    print("ALL EXECUTOR INTEGRATION TESTS PASSED")
    print("="*80 + "\n")
    print("PHASE E-0.1D.1B VERDICT: AUTHORITY ENFORCEMENT + INSTRUMENTATION PROVEN")
    print("  -> All refusal classes produce zero mutation")
    print("  -> Missing caller assertion allowed when binding exists")
    print("  -> Wrong assertion causes refusal")
    print("  -> Invocation count independent from state_changed")
    print("  -> Authoritative binding from contract.execution_binding only")
    print("  -> COMPOUND and TOPOLOGY are now resolver-backed (see "
          "test_compound_resolver_integration.py / test_topology_resolver_integration.py) "
          "-- this suite only covers the missing-execution-binding refusal case for each")
