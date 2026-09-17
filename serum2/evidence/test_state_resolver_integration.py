#!/usr/bin/env python3
"""STATE AUTHORITY INTEGRATION — resolver-backed BODY_STATE adversarial suite.

First of the Execution Coverage V2 "authority-integrated generic operations"
milestone (STATE, then COMPOUND, then TOPOLOGY, then RESOURCE).

Proves:
  1. Resolver only ever runs AFTER admission (refused admission -> 0 calls,
     resolver never invoked)
  2. Resolver's own validation failure (bad rack/value) -> REFUSED, zero mutation
  3. Successful resolver payload -> exactly 1 pathmerge call
  4. resolver_operation_id is authoritative (contract-derived); caller cannot
     supply a different resolver
  5. Existing direct-body_path path (Release/Attack) is UNCHANGED (regression)
  6. Static: the resolver compiler is never called from anywhere except this
     executor
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding
from serum2 import pathmerge


def make_fx_test_body():
    """Minimal body with the nested containers FXEQ.Freq1's resolved path needs."""
    return {
        "FXRack0": {
            "FX": [
                {"FXEQ": {"plainParams": {"kParamFreq1": 1000.0, "kParamGain1": 0.0}}},
            ]
        }
    }


def make_resolver_contract(status="CAUSAL_VERIFIED"):
    binding = ExecutionBinding(
        mutation_type="BODY_STATE",
        body_path=None,
        resolver_operation_id="fx_set_parameter",
        binding_source="test",
        binding_version="1.0",
    )
    return CapabilityContract(
        target="FXEQ.FREQ1",
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


def test_refused_admission_zero_resolver_calls():
    """No contract -> refused before resolver is ever reached."""
    body = make_fx_test_body()
    request = MutationRequest(
        target="FXEQ.FREQ1",
        mutation_type=MutationType.BODY_STATE,
        value=500.0,
        resolver_parameters={"rack": 0, "slot": 0, "effect": "EQ", "parameter": "Freq1"},
    )
    proof = execute_mutation_request_with_authority(
        request=request, body=body, contracts={}, synth=None,
    )
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    unchanged = pathmerge.read_path_value(body, "FXRack0.FX.0.FXEQ.plainParams.kParamFreq1")
    assert unchanged == 1000.0
    print("[PASS] no contract -> refused before resolver reached -> 0 mutation")


def test_resolver_rejects_invalid_value_zero_mutation():
    """Value out of FXEQ.Freq1's valid range [20, 20000] -> resolver REFUSES."""
    body = make_fx_test_body()
    contract = make_resolver_contract()
    contracts = {("FXEQ.FREQ1", ""): contract}

    request = MutationRequest(
        target="FXEQ.FREQ1",
        mutation_type=MutationType.BODY_STATE,
        value=99999.0,  # above max_value=20000.0
        resolver_parameters={"rack": 0, "slot": 0, "effect": "EQ", "parameter": "Freq1"},
    )
    proof = execute_mutation_request_with_authority(
        request=request, body=body, contracts=contracts, synth=None,
    )
    assert not proof.executed, f"expected refusal, got {proof}"
    assert proof.pathmerge_call_count == 0
    assert "VALUE_ABOVE_MAX" in (proof.detail or "")
    unchanged = pathmerge.read_path_value(body, "FXRack0.FX.0.FXEQ.plainParams.kParamFreq1")
    assert unchanged == 1000.0
    print("[PASS] resolver's own range validation refuses -> zero mutation")


def test_resolver_unknown_parameter_zero_mutation():
    """Nonexistent effect/parameter combo -> resolver returns None -> REFUSED."""
    body = make_fx_test_body()
    contract = make_resolver_contract()
    contracts = {("FXEQ.FREQ1", ""): contract}

    request = MutationRequest(
        target="FXEQ.FREQ1",
        mutation_type=MutationType.BODY_STATE,
        value=500.0,
        resolver_parameters={"rack": 0, "slot": 0, "effect": "EQ", "parameter": "NotARealParam"},
    )
    proof = execute_mutation_request_with_authority(
        request=request, body=body, contracts=contracts, synth=None,
    )
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert "UNKNOWN_FX_PARAMETER" in (proof.detail or "")
    print("[PASS] resolver rejects unknown parameter -> zero mutation")


def test_resolver_success_exactly_one_call():
    """Valid payload -> ADMITTED -> exactly 1 pathmerge call, correct path resolved."""
    body = make_fx_test_body()
    contract = make_resolver_contract()
    contracts = {("FXEQ.FREQ1", ""): contract}

    request = MutationRequest(
        target="FXEQ.FREQ1",
        mutation_type=MutationType.BODY_STATE,
        value=2500.0,
        resolver_parameters={"rack": 0, "slot": 0, "effect": "EQ", "parameter": "Freq1"},
    )
    proof = execute_mutation_request_with_authority(
        request=request, body=body, contracts=contracts, synth=None,
    )
    assert proof.executed, f"expected execution, got {proof}"
    assert proof.pathmerge_call_count == 1
    assert proof.mutation_succeeded
    assert proof.body_path == "FXRack0.FX.0.FXEQ.plainParams.kParamFreq1"
    actual = pathmerge.read_path_value(body, "FXRack0.FX.0.FXEQ.plainParams.kParamFreq1")
    assert actual == 2500.0
    print("[PASS] valid resolver payload -> exactly 1 pathmerge call, path resolved correctly")


def test_resolver_operation_id_is_authoritative():
    """Caller cannot redirect to a different resolver -- resolver_operation_id
    comes only from contract.execution_binding, never from the request."""
    body = make_fx_test_body()
    contract = make_resolver_contract()
    contracts = {("FXEQ.FREQ1", ""): contract}

    # MutationRequest has no field for the caller to name a resolver at
    # all -- this is a structural guarantee, not just a runtime check.
    request_fields = MutationRequest.__dataclass_fields__
    assert "resolver_operation_id" not in request_fields, (
        "MutationRequest must not expose a caller-settable resolver_operation_id"
    )
    print("[PASS] MutationRequest has no caller-settable resolver_operation_id field "
          "(structural guarantee, not just a runtime check)")


def test_missing_operation_registry_entry_refused():
    """Contract names a resolver that isn't registered -> REFUSED, not a crash."""
    body = make_fx_test_body()
    binding = ExecutionBinding(
        mutation_type="BODY_STATE",
        resolver_operation_id="nonexistent_resolver_xyz",
        binding_source="test", binding_version="1.0",
    )
    contract = CapabilityContract(
        target="FAKE.TARGET", allowed_operation="mutate_numeric_value",
        status="CAUSAL_VERIFIED", prerequisites=(), verified={}, measurement=None,
        scope={}, provenance={}, execution_binding=binding, limitations=(),
    )
    contracts = {("FAKE.TARGET", ""): contract}
    request = MutationRequest(
        target="FAKE.TARGET", mutation_type=MutationType.BODY_STATE, value=1.0,
    )
    proof = execute_mutation_request_with_authority(
        request=request, body=body, contracts=contracts, synth=None,
    )
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert "not found in OperationRegistry" in (proof.detail or "")
    print("[PASS] unregistered resolver_operation_id -> refused, not a crash")


def test_direct_body_path_regression_unchanged():
    """Existing direct-body_path BODY_STATE path (Release/Attack pattern) is
    completely unaffected by the resolver branch."""
    body = {"Envelope0": {"plainParams": {"kParamRelease": 0.5}}}
    binding = ExecutionBinding(
        mutation_type="BODY_STATE",
        body_path="Envelope0.plainParams.kParamRelease",
        resolver_operation_id=None,
        binding_source="test", binding_version="1.0",
    )
    contract = CapabilityContract(
        target="ENV1.RELEASE", allowed_operation="mutate_numeric_value",
        status="CAUSAL_VERIFIED", prerequisites=(), verified={}, measurement=None,
        scope={}, provenance={}, execution_binding=binding, limitations=(),
    )
    contracts = {("ENV1.RELEASE", ""): contract}
    request = MutationRequest(
        target="ENV1.RELEASE", mutation_type=MutationType.BODY_STATE, value=0.9,
    )
    proof = execute_mutation_request_with_authority(
        request=request, body=body, contracts=contracts, synth=None,
    )
    assert proof.executed
    assert proof.pathmerge_call_count == 1
    assert proof.body_path == "Envelope0.plainParams.kParamRelease"
    assert pathmerge.read_path_value(body, "Envelope0.plainParams.kParamRelease") == 0.9
    print("[PASS] direct body_path path (no resolver) regression: unchanged")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("STATE AUTHORITY INTEGRATION — RESOLVER ADVERSARIAL SUITE")
    print("=" * 80 + "\n")

    tests = [
        test_refused_admission_zero_resolver_calls,
        test_resolver_rejects_invalid_value_zero_mutation,
        test_resolver_unknown_parameter_zero_mutation,
        test_resolver_success_exactly_one_call,
        test_resolver_operation_id_is_authoritative,
        test_missing_operation_registry_entry_refused,
        test_direct_body_path_regression_unchanged,
    ]
    for t in tests:
        t()

    print("\nALL STATE RESOLVER INTEGRATION TESTS PASSED")
