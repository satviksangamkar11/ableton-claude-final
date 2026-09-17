#!/usr/bin/env python3
"""RESOURCE AUTHORITY INTEGRATION — resolver-backed WAVETABLE adversarial suite.

Fourth and final primitive of the "authority-integrated generic operations"
milestone (STATE, COMPOUND, TOPOLOGY done; RESOURCE here).

Scope restriction, explicit: WAVETABLE only.
  RESOURCE.WAVETABLE   -> AUTHORITY_INTEGRATED (verified this session)
  RESOURCE.SAMPLE      -> REFUSED_UNSUPPORTED (claimed field
                           SampleOsc{N}.relativePathToSample contradicted
                           by a real granular-oscillator preset, whose
                           actual field is GranularOsc{N}.samplePathRelative)
  RESOURCE.MULTISAMPLE -> REFUSED_UNSUPPORTED (uses embedded SFZ text, not
                           a path field at all)

Required coverage:
  1. no RESOURCE admission                    -> refused, 0 mutation
  2. wrong execution_binding.mutation_type    -> refused
  3. caller cannot select arbitrary resolver  -> structurally impossible
  4. unsupported resource kind = SAMPLE       -> explicit refusal, 0 mutation
  5. unsupported resource kind = MULTISAMPLE  -> explicit refusal, 0 mutation
  6. invalid/nonexistent wavetable            -> resolver refusal, 0 mutation
  7. valid wavetable                          -> exactly expected mutation
  8. path traversal / outside-root identifier -> refused, 0 mutation
  9. wrong owner/slot (bad oscillator index)  -> refused, 0 mutation
  10. no direct OperationRegistry bypass
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding
from serum2 import pathmerge


def make_resource_contract(resolver_operation_id, target="RESOURCE.X"):
    binding = ExecutionBinding(
        mutation_type="RESOURCE",
        resolver_operation_id=resolver_operation_id,
        binding_source="test", binding_version="1.0",
    )
    return CapabilityContract(
        target=target, allowed_operation="mutate_structured_value",
        status="CAUSAL_VERIFIED", prerequisites=(), verified={}, measurement=None,
        scope={}, provenance={}, execution_binding=binding, limitations=(),
    )


def make_body_with_oscillators():
    return {f"Oscillator{i}": {
        "WTOsc" + str(i): {"plainParams": "default", "relativePathToWT": None,
                            "numChannels": 1, "numFrames": 0, "sampleRate": 44100, "flex": {}},
        "plainParams": "default",
    } for i in range(5)}


def test_1_no_admission_zero_mutation():
    body = make_body_with_oscillators()
    request = MutationRequest(
        target="RESOURCE.X", mutation_type=MutationType.RESOURCE, value=None,
        resolver_parameters={"oscillator": 0, "resource": "Default Shapes"},
    )
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts={}, synth=None)
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert body["Oscillator0"]["WTOsc0"]["relativePathToWT"] is None
    print("[PASS] 1. no contract -> refused -> 0 mutation")


def test_2_wrong_binding_type_refused():
    body = make_body_with_oscillators()
    binding = ExecutionBinding(mutation_type="BODY_STATE", resolver_operation_id="osc_load_wavetable",
                                binding_source="test", binding_version="1.0")
    contract = CapabilityContract(target="RESOURCE.X", allowed_operation="mutate_structured_value",
                                   status="CAUSAL_VERIFIED", prerequisites=(), verified={}, measurement=None,
                                   scope={}, provenance={}, execution_binding=binding, limitations=())
    contracts = {("RESOURCE.X", ""): contract}
    request = MutationRequest(target="RESOURCE.X", mutation_type=MutationType.RESOURCE, value=None,
                               resolver_parameters={"oscillator": 0, "resource": "Default Shapes"})
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert "No RESOURCE execution binding" in (proof.detail or "")
    print("[PASS] 2. wrong execution_binding.mutation_type -> refused")


def test_3_no_caller_selected_resolver():
    """Structural guarantee: neither resolver_operation_id nor any
    resource_resolver_id field exists on MutationRequest -- the caller can
    supply resource payload data (oscillator, resource identifier) but
    cannot choose which resolver/operation runs."""
    fields = MutationRequest.__dataclass_fields__
    assert "resolver_operation_id" not in fields
    assert "resource_resolver_id" not in fields
    print("[PASS] 3. no caller-selectable resolver field exists on MutationRequest (structural)")


def test_4_sample_kind_refused():
    body = make_body_with_oscillators()
    contract = make_resource_contract("osc_load_sample")
    contracts = {("RESOURCE.X", ""): contract}
    request = MutationRequest(target="RESOURCE.X", mutation_type=MutationType.RESOURCE, value=None,
                               resolver_parameters={"oscillator": 0, "resource": "Kick"})
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert "not in PROVEN_RESOURCE_OPERATION_IDS" in (proof.detail or "")
    print("[PASS] 4. SAMPLE (osc_load_sample) -> explicit refusal, unverified field name")


def test_5_multisample_kind_refused():
    body = make_body_with_oscillators()
    contract = make_resource_contract("osc_load_multisample")
    contracts = {("RESOURCE.X", ""): contract}
    request = MutationRequest(target="RESOURCE.X", mutation_type=MutationType.RESOURCE, value=None,
                               resolver_parameters={"oscillator": 0, "resource": "Oud"})
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert "not in PROVEN_RESOURCE_OPERATION_IDS" in (proof.detail or "")
    print("[PASS] 5. MULTISAMPLE (osc_load_multisample) -> explicit refusal, embedded-SFZ representation")


def test_6_nonexistent_wavetable_refused():
    body = make_body_with_oscillators()
    contract = make_resource_contract("osc_load_wavetable")
    contracts = {("RESOURCE.X", ""): contract}
    request = MutationRequest(target="RESOURCE.X", mutation_type=MutationType.RESOURCE, value=None,
                               resolver_parameters={"oscillator": 0, "resource": "ThisWavetableDoesNotExist12345"})
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert not proof.executed
    assert proof.pathmerge_call_count == 0
    assert "RESOURCE_NOT_FOUND" in (proof.detail or "")
    assert body["Oscillator0"]["WTOsc0"]["relativePathToWT"] is None
    print("[PASS] 6. nonexistent wavetable identifier -> resolver refusal (real filesystem check), 0 mutation")


def test_7_valid_wavetable_exact_mutation():
    body = make_body_with_oscillators()
    contract = make_resource_contract("osc_load_wavetable")
    contracts = {("RESOURCE.X", ""): contract}
    request = MutationRequest(target="RESOURCE.X", mutation_type=MutationType.RESOURCE, value=None,
                               resolver_parameters={"oscillator": 0, "resource": "Default Shapes"})
    proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
    assert proof.executed, f"expected execution, got {proof}"
    assert proof.pathmerge_call_count == 1
    assert proof.body_path == "Oscillator0.WTOsc0.relativePathToWT"
    assert body["Oscillator0"]["WTOsc0"]["relativePathToWT"] == "S2 Tables/Default Shapes.wav"
    print("[PASS] 7. valid wavetable -> exactly 1 mutation, correct path + value")


def test_8_path_traversal_refused():
    body = make_body_with_oscillators()
    contract = make_resource_contract("osc_load_wavetable")
    contracts = {("RESOURCE.X", ""): contract}
    for traversal_id in ["../../../Windows/System32/notepad", "..\\..\\..\\Windows\\win.ini", "/etc/passwd"]:
        request = MutationRequest(target="RESOURCE.X", mutation_type=MutationType.RESOURCE, value=None,
                                   resolver_parameters={"oscillator": 0, "resource": traversal_id})
        proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
        assert not proof.executed, f"traversal identifier {traversal_id!r} should have been refused"
        assert proof.pathmerge_call_count == 0
        assert "RESOURCE_NOT_FOUND" in (proof.detail or "")
    assert body["Oscillator0"]["WTOsc0"]["relativePathToWT"] is None
    print("[PASS] 8. path-traversal-shaped identifiers -> refused (identifier is never joined into a "
          "literal path; resolver only substring-matches real filenames within fixed search roots)")


def test_9_invalid_oscillator_index_refused():
    body = make_body_with_oscillators()
    contract = make_resource_contract("osc_load_wavetable")
    contracts = {("RESOURCE.X", ""): contract}
    for bad_idx in [-1, 99]:
        request = MutationRequest(target="RESOURCE.X", mutation_type=MutationType.RESOURCE, value=None,
                                   resolver_parameters={"oscillator": bad_idx, "resource": "Default Shapes"})
        proof = execute_mutation_request_with_authority(request=request, body=body, contracts=contracts, synth=None)
        assert not proof.executed, f"oscillator index {bad_idx} should have been refused"
        assert proof.pathmerge_call_count == 0
        assert "OSCILLATOR_INDEX" in (proof.detail or "")
    print("[PASS] 9. wrong owner/slot (invalid oscillator index, negative and out-of-range) -> refused")


def test_10_no_direct_operation_registry_bypass():
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
    print(f"[PASS] 10. get_registry() called from exactly 1 file: {lines[1]}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RESOURCE AUTHORITY INTEGRATION — RESOLVER ADVERSARIAL SUITE (WAVETABLE only)")
    print("=" * 80 + "\n")

    tests = [
        test_1_no_admission_zero_mutation,
        test_2_wrong_binding_type_refused,
        test_3_no_caller_selected_resolver,
        test_4_sample_kind_refused,
        test_5_multisample_kind_refused,
        test_6_nonexistent_wavetable_refused,
        test_7_valid_wavetable_exact_mutation,
        test_8_path_traversal_refused,
        test_9_invalid_oscillator_index_refused,
        test_10_no_direct_operation_registry_bypass,
    ]
    for t in tests:
        t()

    print("\nALL RESOURCE RESOLVER INTEGRATION TESTS PASSED")
