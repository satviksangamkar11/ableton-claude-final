#!/usr/bin/env python3
"""TOPOLOGY AUTHORITY INTEGRATION — resolver-backed FX structural adversarial suite.

Third of the Execution Coverage V2 "authority-integrated generic
operations" milestone (STATE, COMPOUND done; TOPOLOGY here; RESOURCE next).

Only PROVEN operations are wired: ADD, REMOVE, REPLACE, CLEAR_RACK,
BYPASS, UNBYPASS (+ bus-level bypass/unbypass). REORDER and
MOVE_BETWEEN_BUSES remain unresolved and unreachable -- proven by an
explicit allowlist check in the executor, not merely by absence of a
compiler.

Required coverage:
  admission refusal                  -> 0 mutation
  wrong binding type                 -> refusal
  caller-selected operation ID       -> impossible
  invalid bus/operation_id           -> 0 mutation
  invalid slot                       -> 0 mutation
  ADD                                -> exactly expected topology mutation
  REMOVE                             -> exactly expected topology mutation
  REPLACE                            -> exactly expected topology mutation
  CLEAR_RACK                         -> only intended rack mutated
  BYPASS                             -> only intended FX modules mutated
  UNBYPASS                           -> only intended FX modules mutated
  cross-bus isolation                -> unaffected buses unchanged
  direct OperationRegistry bypass    -> none
"""

import sys
import copy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding
from serum2 import pathmerge

# Real FX entry structures captured from archive/golden_presets/arp.SerumPreset
# (ground truth, not fabricated).
REAL_DISTORTION_ENTRY = {
    "FXDistortion": {"plainParams": {
        "kParamDrive": 36.74789369106293, "kParamLevelOut": 0.5023294687271118,
        "kParamMode": "kOverdrive", "kParamWet": 56.083983182907104,
    }},
    "flex": [{}, {}],
    "kUIParamMixOrGain": 0.0,
    "type": 0,
}
REAL_DELAY_ENTRY = {
    "FXDelay": {"plainParams": {
        "kParamBW": 3.2793322652578354, "kParamFeedback": 47.19850718975067,
        "kParamFreq": 2301.2985114436656, "kParamMode": 1.0,
        "kParamOffsetL": 0.5, "kParamOffsetR": 0.5506209023296833,
        "kParamTimeL": 0.04933726956749931, "kParamTimeR": 0.04933726956749931,
        "kParamWet": 22.105523943901062,
    }},
    "kUIParamMixOrGain": 0.0,
    "type": 4,
}


def make_body_with_fx(main_fx=None, bus1_fx=None):
    return {
        "FXRack0": {"FX": copy.deepcopy(main_fx) if main_fx else [], "displayName": "", "plainParams": "default"},
        "FXRack1": {"FX": copy.deepcopy(bus1_fx) if bus1_fx else [], "displayName": "", "plainParams": "default"},
        "FXRack2": {"FX": [], "displayName": "", "plainParams": "default"},
    }


def make_topology_contract(resolver_operation_id, status="CAUSAL_VERIFIED", target="TOPOLOGY.X"):
    binding = ExecutionBinding(
        mutation_type="TOPOLOGY",
        resolver_operation_id=resolver_operation_id,
        binding_source="test", binding_version="1.0",
    )
    return CapabilityContract(
        target=target,
        allowed_operation="mutate_structured_value",
        status=status, prerequisites=(), verified={}, measurement=None,
        scope={}, provenance={}, execution_binding=binding, limitations=(),
    )


def test_refused_admission_zero_mutation():
    body = make_body_with_fx(main_fx=[REAL_DISTORTION_ENTRY])
    request = MutationRequest(
        target="TOPOLOGY.X", mutation_type=MutationType.TOPOLOGY, value=None,
        resolver_parameters={"slot_index": 1},
    )
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts={}, synth=None)
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert body["FXRack0"]["FX"] == [REAL_DISTORTION_ENTRY]
    print("[PASS] no contract -> refused -> 0 mutation")


def test_wrong_binding_type_refused():
    body = make_body_with_fx()
    binding = ExecutionBinding(mutation_type="BODY_STATE", resolver_operation_id="fx_struct_add_MAIN",
                                binding_source="test", binding_version="1.0")
    contract = CapabilityContract(target="TOPOLOGY.X", allowed_operation="mutate_structured_value",
                                   status="CAUSAL_VERIFIED", prerequisites=(), verified={}, measurement=None,
                                   scope={}, provenance={}, execution_binding=binding, limitations=())
    contracts = {("TOPOLOGY.X", ""): contract}
    request = MutationRequest(target="TOPOLOGY.X", mutation_type=MutationType.TOPOLOGY, value=None,
                               resolver_parameters={"slot_index": 0, "effect_structure": REAL_DISTORTION_ENTRY})
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert "No TOPOLOGY execution binding" in (proof.detail or "")
    print("[PASS] wrong execution_binding.mutation_type -> refused -> 0 mutation")


def test_no_caller_selected_operation_id():
    assert "resolver_operation_id" not in MutationRequest.__dataclass_fields__
    print("[PASS] MutationRequest has no caller-settable resolver_operation_id (structural)")


def test_unproven_operation_id_refused():
    """REORDER/MOVE_BETWEEN_BUSES (or any made-up operation_id, standing in
    for 'invalid bus' since bus is baked into which allowlisted operation_id
    a contract may point to) -> refused via the explicit allowlist, zero
    mutation, even though nothing here depends on whether a compiler
    happens to be registered under that name."""
    body = make_body_with_fx(main_fx=[REAL_DISTORTION_ENTRY])
    for bad_op_id in ["fx_struct_reorder_MAIN", "fx_struct_move_between_buses_MAIN", "fx_struct_add_BUS99"]:
        contract = make_topology_contract(bad_op_id)
        contracts = {("TOPOLOGY.X", ""): contract}
        request = MutationRequest(target="TOPOLOGY.X", mutation_type=MutationType.TOPOLOGY, value=None,
                                   resolver_parameters={"slot_index": 0})
        proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
        assert not proof.executed, f"{bad_op_id} should have been refused"
        assert proof.pathmerge_call_count == 0
        assert "not in PROVEN_TOPOLOGY_OPERATION_IDS" in (proof.detail or "")
    assert body["FXRack0"]["FX"] == [REAL_DISTORTION_ENTRY]
    print("[PASS] unproven/invalid operation_id (REORDER, MOVE_BETWEEN_BUSES, bad bus) -> refused -> 0 mutation")


def test_invalid_slot_zero_mutation():
    body = make_body_with_fx(main_fx=[REAL_DISTORTION_ENTRY])
    contract = make_topology_contract("fx_struct_remove_MAIN")
    contracts = {("TOPOLOGY.X", ""): contract}
    request = MutationRequest(target="TOPOLOGY.X", mutation_type=MutationType.TOPOLOGY, value=None,
                               resolver_parameters={"slot_index": 99})
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert "INVALID_SLOT" in (proof.detail or "")
    assert body["FXRack0"]["FX"] == [REAL_DISTORTION_ENTRY]
    print("[PASS] out-of-range slot -> refused -> 0 mutation")


def test_add_exact_mutation():
    body = make_body_with_fx(main_fx=[REAL_DISTORTION_ENTRY])
    contract = make_topology_contract("fx_struct_add_MAIN")
    contracts = {("TOPOLOGY.X", ""): contract}
    request = MutationRequest(target="TOPOLOGY.X", mutation_type=MutationType.TOPOLOGY, value=None,
                               resolver_parameters={"slot_index": 1, "effect_structure": REAL_DELAY_ENTRY})
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert proof.executed, f"expected execution, got {proof}"
    assert proof.pathmerge_call_count == 1
    assert body["FXRack0"]["FX"] == [REAL_DISTORTION_ENTRY, REAL_DELAY_ENTRY]
    print("[PASS] ADD -> exactly 1 mutation, correct array state")


def test_remove_exact_mutation():
    body = make_body_with_fx(main_fx=[REAL_DISTORTION_ENTRY, REAL_DELAY_ENTRY])
    contract = make_topology_contract("fx_struct_remove_MAIN")
    contracts = {("TOPOLOGY.X", ""): contract}
    request = MutationRequest(target="TOPOLOGY.X", mutation_type=MutationType.TOPOLOGY, value=None,
                               resolver_parameters={"slot_index": 0})
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert proof.executed
    assert proof.pathmerge_call_count == 1
    assert body["FXRack0"]["FX"] == [REAL_DELAY_ENTRY]
    print("[PASS] REMOVE -> exactly 1 mutation, correct array state")


def test_replace_exact_mutation():
    body = make_body_with_fx(main_fx=[REAL_DISTORTION_ENTRY])
    contract = make_topology_contract("fx_struct_replace_MAIN")
    contracts = {("TOPOLOGY.X", ""): contract}
    request = MutationRequest(target="TOPOLOGY.X", mutation_type=MutationType.TOPOLOGY, value=None,
                               resolver_parameters={"slot_index": 0, "effect_structure": REAL_DELAY_ENTRY})
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert proof.executed
    assert proof.pathmerge_call_count == 1
    assert body["FXRack0"]["FX"] == [REAL_DELAY_ENTRY]
    print("[PASS] REPLACE -> exactly 1 mutation, correct array state")


def test_clear_rack_only_intended_rack():
    body = make_body_with_fx(main_fx=[REAL_DISTORTION_ENTRY], bus1_fx=[REAL_DELAY_ENTRY])
    contract = make_topology_contract("fx_struct_clear_rack_MAIN")
    contracts = {("TOPOLOGY.X", ""): contract}
    request = MutationRequest(target="TOPOLOGY.X", mutation_type=MutationType.TOPOLOGY, value=None)
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert proof.executed
    assert proof.pathmerge_call_count == 1
    assert body["FXRack0"]["FX"] == [], "MAIN rack must be cleared"
    assert body["FXRack1"]["FX"] == [REAL_DELAY_ENTRY], "BUS1 rack must be untouched"
    print("[PASS] CLEAR_RACK -> only intended rack mutated, sibling bus untouched")


def test_bypass_only_intended_fx():
    body = make_body_with_fx(main_fx=[REAL_DISTORTION_ENTRY, REAL_DELAY_ENTRY])
    contract = make_topology_contract("fx_struct_bypass_MAIN")
    contracts = {("TOPOLOGY.X", ""): contract}
    request = MutationRequest(target="TOPOLOGY.X", mutation_type=MutationType.TOPOLOGY, value=None,
                               resolver_parameters={"slot_index": 0})
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert proof.executed
    assert proof.pathmerge_call_count == 1
    assert body["FXRack0"]["FX"][0]["FXDistortion"]["plainParams"] == {"kParamEnable": 0.0}
    assert body["FXRack0"]["FX"][1] == REAL_DELAY_ENTRY, "slot 1 (Delay) must be untouched"
    print("[PASS] BYPASS -> only intended FX module mutated")


def test_unbypass_only_intended_fx():
    bypassed_distortion = copy.deepcopy(REAL_DISTORTION_ENTRY)
    bypassed_distortion["FXDistortion"]["plainParams"] = {"kParamEnable": 0.0}
    body = make_body_with_fx(main_fx=[bypassed_distortion, REAL_DELAY_ENTRY])
    contract = make_topology_contract("fx_struct_unbypass_MAIN")
    contracts = {("TOPOLOGY.X", ""): contract}
    request = MutationRequest(target="TOPOLOGY.X", mutation_type=MutationType.TOPOLOGY, value=None,
                               resolver_parameters={"slot_index": 0})
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert proof.executed
    assert proof.pathmerge_call_count == 1
    assert body["FXRack0"]["FX"][0]["FXDistortion"]["plainParams"] == "default"
    assert body["FXRack0"]["FX"][1] == REAL_DELAY_ENTRY
    print("[PASS] UNBYPASS -> only intended FX module mutated")


def test_bypass_bus_cross_bus_isolation():
    body = make_body_with_fx(main_fx=[REAL_DISTORTION_ENTRY, REAL_DELAY_ENTRY], bus1_fx=[REAL_DELAY_ENTRY])
    contract = make_topology_contract("fx_struct_bypass_bus_MAIN")
    contracts = {("TOPOLOGY.X", ""): contract}
    request = MutationRequest(target="TOPOLOGY.X", mutation_type=MutationType.TOPOLOGY, value=None)
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert proof.executed
    assert proof.pathmerge_call_count == 2, "both MAIN FX modules should be bypassed"
    assert body["FXRack0"]["FX"][0]["FXDistortion"]["plainParams"] == {"kParamEnable": 0.0}
    assert body["FXRack0"]["FX"][1]["FXDelay"]["plainParams"] == {"kParamEnable": 0.0}
    assert body["FXRack1"]["FX"] == [REAL_DELAY_ENTRY], "BUS1 must be completely unaffected"
    print("[PASS] bus-level BYPASS -> both intended FX bypassed, sibling bus (BUS1) unaffected")


def test_wildcard_defect_actually_fixed():
    """Direct regression guard: neither bypass_effect() nor unbypass_effect()
    produce a literal '*' path segment anymore."""
    body = make_body_with_fx(main_fx=[REAL_DISTORTION_ENTRY])
    contract = make_topology_contract("fx_struct_bypass_MAIN")
    contracts = {("TOPOLOGY.X", ""): contract}
    request = MutationRequest(target="TOPOLOGY.X", mutation_type=MutationType.TOPOLOGY, value=None,
                               resolver_parameters={"slot_index": 0})
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert proof.executed
    assert proof.body_path == "FXRack0.FX.0.FXDistortion.plainParams"
    assert "*" not in proof.body_path
    print(f"[PASS] bypass resolved to concrete path (no wildcard): {proof.body_path}")


def test_no_direct_operation_registry_bypass():
    import subprocess
    result = subprocess.run(
        ["python", "-c", """
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
    assert count == 1, f"expected get_registry() called from exactly 1 file, found {count}: {lines[1:]}"
    print(f"[PASS] get_registry() called from exactly 1 file: {lines[1]}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TOPOLOGY AUTHORITY INTEGRATION — RESOLVER ADVERSARIAL SUITE")
    print("=" * 80 + "\n")

    tests = [
        test_refused_admission_zero_mutation,
        test_wrong_binding_type_refused,
        test_no_caller_selected_operation_id,
        test_unproven_operation_id_refused,
        test_invalid_slot_zero_mutation,
        test_add_exact_mutation,
        test_remove_exact_mutation,
        test_replace_exact_mutation,
        test_clear_rack_only_intended_rack,
        test_bypass_only_intended_fx,
        test_unbypass_only_intended_fx,
        test_bypass_bus_cross_bus_isolation,
        test_wildcard_defect_actually_fixed,
        test_no_direct_operation_registry_bypass,
    ]
    for t in tests:
        t()

    print("\nALL TOPOLOGY RESOLVER INTEGRATION TESTS PASSED")
