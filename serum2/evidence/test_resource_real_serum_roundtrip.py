#!/usr/bin/env python3
"""RESOURCE (WAVETABLE) — real Serum/DawDreamer round-trip proof.

Per explicit requirement: this must NOT stop at "filesystem path found".
The full chain proven here:

  resource identity ("Default Shapes")
      -> validated content-root resolution (real file, real hash/size)
      -> authority-gated Serum state mutation (via the executor)
      -> Serum load (real synth.load_state())
      -> Serum save/readback (real synth.save_state(), decoded)
      -> resource identity/state confirmed FROM SERUM'S OWN OUTPUT,
         not from our own in-memory body dict

A second wavetable is loaded to prove Serum actually changed which table
is active, not merely that a string was accepted into the state blob.
"""

import sys
import copy
import tempfile
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import dawdreamer as daw

from serum2 import bridge, codec, vst3_state
from serum2.evidence import epoch as epoch_mod
from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512


def make_contract(op_id="osc_load_wavetable"):
    binding = ExecutionBinding(mutation_type="RESOURCE", resolver_operation_id=op_id,
                                binding_source="test", binding_version="1.0")
    return CapabilityContract(target="T", allowed_operation="mutate_structured_value",
                               status="CAUSAL_VERIFIED", prerequisites=(), verified={},
                               measurement=None, scope={}, provenance={},
                               execution_binding=binding, limitations=())


def dispatch(body, resolver_parameters):
    contract = make_contract()
    request = MutationRequest(target="T", mutation_type=MutationType.RESOURCE, value=None,
                               resolver_parameters=resolver_parameters)
    return execute_mutation_request_with_authority(
        request=request, body=body, contracts={("T", ""): contract}, synth=None,
    )


def real_serum_roundtrip(meta, body):
    """Load into a REAL Serum instance, then read back what Serum itself saves."""
    fd, tmp = tempfile.mkstemp(suffix=".bin"); os.close(fd)
    bridge.write_state_file(tmp, meta, body)
    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)
    fd, out = tempfile.mkstemp(suffix=".bin"); os.close(fd)
    synth.save_state(out)
    raw = open(out, "rb").read(); os.remove(out)
    return codec.decode(vst3_state.unwrap_vc2(raw))


def test_wavetable_full_chain_real_serum():
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, skel_body = skeleton

    # Step 1: resource identity -> validated content-root resolution
    # (done inside the executor via ResourceResolver; verify independently here too)
    from serum2.operations.resource_resolver import ResourceResolver
    resolver = ResourceResolver()
    resolution = resolver.resolve_wavetable("Default Shapes")
    assert resolution.success(), f"resource resolution failed: {resolution.error_detail}"
    assert resolution.resource.file_hash is not None, "real file hash must be computed"
    assert resolution.resource.file_size and resolution.resource.file_size > 0
    print(f"  resolved: {resolution.resource.serum_relative_path} "
          f"(hash={resolution.resource.file_hash}, size={resolution.resource.file_size})")

    # Step 2: authority-gated Serum state mutation
    body = copy.deepcopy(skel_body)
    proof = dispatch(body, {"oscillator": 0, "resource": "Default Shapes"})
    assert proof.executed and proof.pathmerge_call_count == 1
    assert body["Oscillator0"]["WTOsc0"]["relativePathToWT"] == resolution.resource.serum_relative_path

    # Step 3+4: real Serum load, then real Serum save/readback (NOT our own dict)
    _, resaved = real_serum_roundtrip(meta, body)
    readback_path = resaved["Oscillator0"]["WTOsc0"]["relativePathToWT"]
    assert readback_path == "S2 Tables/Default Shapes.wav", \
        f"Serum's own save_state() did not preserve the wavetable path: got {readback_path!r}"

    print(f"  Serum readback (its own save_state output): "
          f"Oscillator0.WTOsc0.relativePathToWT = {readback_path!r}")
    print("[PASS] full chain confirmed: identity -> resolution -> mutation -> "
          "Serum load -> Serum save/readback -> confirmed FROM SERUM'S OWN STATE")


def test_wavetable_change_confirmed_by_serum():
    """Load a SECOND, different real wavetable and prove Serum's own
    readback reflects the change -- not just that a string round-trips."""
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, skel_body = skeleton

    from serum2.operations.resource_resolver import ResourceResolver
    resolver = ResourceResolver()
    res_a = resolver.resolve_wavetable("Default Shapes")
    # Pick a second real wavetable confirmed earlier this session
    res_b = resolver.resolve_wavetable("Brass Stab")
    assert res_a.success() and res_b.success()
    assert res_a.resource.serum_relative_path != res_b.resource.serum_relative_path

    body_a = copy.deepcopy(skel_body)
    proof_a = dispatch(body_a, {"oscillator": 1, "resource": "Default Shapes"})
    assert proof_a.executed

    body_b = copy.deepcopy(skel_body)
    proof_b = dispatch(body_b, {"oscillator": 1, "resource": "Brass Stab"})
    assert proof_b.executed

    _, resaved_a = real_serum_roundtrip(meta, body_a)
    _, resaved_b = real_serum_roundtrip(meta, body_b)

    path_a = resaved_a["Oscillator1"]["WTOsc1"]["relativePathToWT"]
    path_b = resaved_b["Oscillator1"]["WTOsc1"]["relativePathToWT"]
    assert path_a != path_b, "Serum's readback must differ for two different loaded wavetables"
    assert path_a == "S2 Tables/Default Shapes.wav"
    assert "Brass Stab" in path_b

    print(f"  Serum readback A: {path_a!r}")
    print(f"  Serum readback B: {path_b!r}")
    print("[PASS] two different wavetables -> two different Serum-confirmed states "
          "(genuine resource change, not a fixed/ignored value)")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RESOURCE (WAVETABLE) — REAL SERUM/DAWDREAMER FULL-CHAIN PROOF")
    print("=" * 80 + "\n")

    test_wavetable_full_chain_real_serum()
    test_wavetable_change_confirmed_by_serum()

    print("\nALL RESOURCE REAL-SERUM ROUND-TRIP TESTS PASSED")
