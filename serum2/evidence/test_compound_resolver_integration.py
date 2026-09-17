#!/usr/bin/env python3
"""COMPOUND AUTHORITY INTEGRATION — resolver-backed MATRIX_ROUTE adversarial suite.

Second of the Execution Coverage V2 "authority-integrated generic
operations" milestone (STATE done, COMPOUND here, then TOPOLOGY, RESOURCE).

Required coverage (per the agreed COMPOUND milestone):
  - admission refusal -> 0 mutation
  - bad source/destination/slot -> 0 mutation
  - valid route -> generic dispatcher invoked
  - destination comes from authoritative binding
  - no caller-selected operation ID
  - exact mutation invocation count
  - no direct OperationRegistry bypass
  - existing BODY/HOST/Release/Attack regressions unchanged (checked by
    re-running test_state_resolver_integration.py and the D.1.2 suites
    alongside this file, not duplicated here)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding
from serum2 import pathmerge


def make_compound_contract(resolver_operation_id="compound_create_modulation_route", status="CAUSAL_VERIFIED"):
    binding = ExecutionBinding(
        mutation_type="COMPOUND",
        resolver_operation_id=resolver_operation_id,
        binding_source="test",
        binding_version="1.0",
    )
    return CapabilityContract(
        target="MATRIX.LFO1_TO_FILTER1_CUTOFF",
        allowed_operation="mutate_structured_value",
        status=status,
        prerequisites=(),
        verified={},
        measurement=None,
        scope={},
        provenance={},
        execution_binding=binding,
        limitations=(),
    )


def test_refused_admission_zero_mutation():
    """No contract -> refused before the compound dispatcher is ever reached."""
    body = {}
    request = MutationRequest(
        target="MATRIX.LFO1_TO_FILTER1_CUTOFF",
        mutation_type=MutationType.COMPOUND,
        value=0.5,
        resolver_parameters={"source": "LFO1", "destination": "Filter1.Cutoff", "amount": 0.5},
    )
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts={}, synth=None)
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert body == {}, "body must be completely untouched"
    print("[PASS] no contract -> refused -> 0 mutation, body untouched")


def test_bad_source_zero_mutation():
    body = {}
    contract = make_compound_contract()
    contracts = {("MATRIX.LFO1_TO_FILTER1_CUTOFF", ""): contract}
    request = MutationRequest(
        target="MATRIX.LFO1_TO_FILTER1_CUTOFF",
        mutation_type=MutationType.COMPOUND,
        value=0.5,
        resolver_parameters={"source": "NotARealSource", "destination": "Filter1.Cutoff", "amount": 0.5},
    )
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert "UNKNOWN_SOURCE" in (proof.detail or "")
    assert body == {}
    print("[PASS] bad source -> refused -> 0 mutation")


def test_bad_destination_zero_mutation():
    body = {}
    contract = make_compound_contract()
    contracts = {("MATRIX.LFO1_TO_FILTER1_CUTOFF", ""): contract}
    request = MutationRequest(
        target="MATRIX.LFO1_TO_FILTER1_CUTOFF",
        mutation_type=MutationType.COMPOUND,
        value=0.5,
        resolver_parameters={"source": "LFO1", "destination": "NotARealDestination", "amount": 0.5},
    )
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert "UNKNOWN_DESTINATION" in (proof.detail or "")
    assert body == {}
    print("[PASS] bad destination -> refused -> 0 mutation")


def test_bad_slot_zero_mutation():
    body = {}
    contract = make_compound_contract()
    contracts = {("MATRIX.LFO1_TO_FILTER1_CUTOFF", ""): contract}
    request = MutationRequest(
        target="MATRIX.LFO1_TO_FILTER1_CUTOFF",
        mutation_type=MutationType.COMPOUND,
        value=0.5,
        resolver_parameters={"source": "LFO1", "destination": "Filter1.Cutoff",
                              "amount": 0.5, "modslot_index": 999},
    )
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert "INVALID_MODSLOT" in (proof.detail or "")
    assert body == {}
    print("[PASS] out-of-range slot -> refused -> 0 mutation")


def test_valid_route_generic_dispatcher_invoked_exact_count():
    """Valid payload -> ADMITTED -> generic dispatcher runs -> exactly 1
    pathmerge call, destination correctly resolved from the request's
    payload via the FIXED (non-hard-coded) compiler."""
    body = {}
    contract = make_compound_contract()
    contracts = {("MATRIX.LFO1_TO_FILTER1_CUTOFF", ""): contract}
    request = MutationRequest(
        target="MATRIX.LFO1_TO_FILTER1_CUTOFF",
        mutation_type=MutationType.COMPOUND,
        value=0.5,
        resolver_parameters={"source": "LFO1", "destination": "Filter1.Cutoff", "amount": 0.5},
    )
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert proof.executed, f"expected execution, got {proof}"
    assert proof.pathmerge_call_count == 1
    assert proof.mutation_succeeded
    assert proof.body_path == "ModSlot0"
    slot = pathmerge.read_path_value(body, "ModSlot0")
    assert slot["destModuleTypeString"] == "VoiceFilter"
    assert slot["destModuleParamName"] == "kParamFreq"
    assert slot["source"] == [6, 0]
    print("[PASS] valid route -> generic dispatcher invoked -> exactly 1 pathmerge call, "
          "destination correctly resolved")


def test_second_route_different_destination_not_hardcoded():
    """Regression guard for the fixed defect at the authority-integration
    layer: a different destination in the SAME contract shape must produce
    a DIFFERENT resolved binding, not always VoiceFilter."""
    body = {}
    contract = make_compound_contract()
    contracts = {("MATRIX.LFO1_TO_FILTER1_CUTOFF", ""): contract}
    request = MutationRequest(
        target="MATRIX.LFO1_TO_FILTER1_CUTOFF",
        mutation_type=MutationType.COMPOUND,
        value=0.3,
        resolver_parameters={"source": "Env1", "destination": "Osc1.Volume", "amount": 0.3},
    )
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert proof.executed
    slot = pathmerge.read_path_value(body, proof.body_path)
    assert slot["destModuleTypeString"] == "Oscillator", "must NOT be hard-coded to VoiceFilter"
    assert slot["destModuleParamName"] == "kParamVolume"
    print("[PASS] different requested destination -> different resolved binding (not hard-coded)")


def test_no_caller_selected_operation_id():
    """MutationRequest has no field for the caller to choose which
    resolver runs -- structural guarantee, same as STATE."""
    assert "resolver_operation_id" not in MutationRequest.__dataclass_fields__
    print("[PASS] MutationRequest has no caller-settable resolver_operation_id (structural)")


def test_wrong_execution_binding_type_refused():
    """A contract whose execution_binding.mutation_type is NOT COMPOUND
    must refuse a COMPOUND request, even if a resolver_operation_id happens
    to be present."""
    body = {}
    binding = ExecutionBinding(
        mutation_type="BODY_STATE",  # wrong type for a COMPOUND request
        resolver_operation_id="compound_create_modulation_route",
        binding_source="test", binding_version="1.0",
    )
    contract = CapabilityContract(
        target="MATRIX.X", allowed_operation="mutate_structured_value",
        status="CAUSAL_VERIFIED", prerequisites=(), verified={}, measurement=None,
        scope={}, provenance={}, execution_binding=binding, limitations=(),
    )
    contracts = {("MATRIX.X", ""): contract}
    request = MutationRequest(
        target="MATRIX.X", mutation_type=MutationType.COMPOUND, value=0.5,
        resolver_parameters={"source": "LFO1", "destination": "Filter1.Cutoff", "amount": 0.5},
    )
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert "No COMPOUND execution binding" in (proof.detail or "")
    print("[PASS] mismatched execution_binding.mutation_type -> refused -> 0 mutation")


def test_no_direct_operation_registry_bypass():
    """Static check: get_registry() is called from exactly one production
    location -- inside mutation_executor_extended.py's shared resolver
    dispatch -- not from anywhere else in producer/evidence/compiler."""
    import subprocess
    result = subprocess.run(
        ["python", "-c", """
import re
from pathlib import Path
hits = []
for root in ["serum2/producer", "serum2/evidence", "serum2/compiler"]:
    for f in Path(root).rglob("*.py"):
        if f.name.startswith("test_"):
            continue
        text = f.read_text(encoding="utf-8")
        if "get_registry()" in text:
            hits.append(str(f))
print(len(hits))
for h in hits:
    print(h)
"""],
        capture_output=True, text=True, cwd=str(Path(__file__).parent.parent.parent),
    )
    lines = result.stdout.strip().splitlines()
    count = int(lines[0])
    files = lines[1:]
    assert count == 1, f"expected get_registry() called from exactly 1 file, found {count}: {files}"
    assert files[0].replace("\\", "/").endswith("serum2/evidence/mutation_executor_extended.py")
    print(f"[PASS] get_registry() called from exactly 1 file: {files[0]}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("COMPOUND AUTHORITY INTEGRATION — RESOLVER ADVERSARIAL SUITE")
    print("=" * 80 + "\n")

    tests = [
        test_refused_admission_zero_mutation,
        test_bad_source_zero_mutation,
        test_bad_destination_zero_mutation,
        test_bad_slot_zero_mutation,
        test_valid_route_generic_dispatcher_invoked_exact_count,
        test_second_route_different_destination_not_hardcoded,
        test_no_caller_selected_operation_id,
        test_wrong_execution_binding_type_refused,
        test_no_direct_operation_registry_bypass,
    ]
    for t in tests:
        t()

    print("\nALL COMPOUND RESOLVER INTEGRATION TESTS PASSED")
