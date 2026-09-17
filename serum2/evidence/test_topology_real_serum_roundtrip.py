#!/usr/bin/env python3
"""TOPOLOGY — real Serum/DawDreamer round-trip proof, one per distinct
mechanism class (ADD, REMOVE, REPLACE, CLEAR_RACK, BYPASS/UNBYPASS).

Unit-level compilation (test_topology_resolver_integration.py) proves the
executor dispatches correctly and produces the right in-memory mutation.
This file proves the resulting state is something REAL Serum actually
accepts and round-trips -- not just something our own pathmerge/codec
layer believes is valid. For BYPASS specifically, also proves a genuine
causal audio effect (silence), not just a state-field change.
"""

import sys
import copy
import tempfile
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import dawdreamer as daw

from serum2 import bridge, codec, vst3_state
from serum2.evidence import epoch as epoch_mod
from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512

_, _ARP_BODY = codec.load_preset_file(
    str(Path(__file__).parent.parent.parent / "archive" / "golden_presets" / "arp.SerumPreset")
)
DISTORTION = copy.deepcopy(_ARP_BODY["FXRack0"]["FX"][2])  # real captured ground truth
DELAY = copy.deepcopy(_ARP_BODY["FXRack0"]["FX"][1])


def make_contract(op_id):
    binding = ExecutionBinding(mutation_type="TOPOLOGY", resolver_operation_id=op_id,
                                binding_source="test", binding_version="1.0")
    return CapabilityContract(target="T", allowed_operation="mutate_structured_value",
                               status="CAUSAL_VERIFIED", prerequisites=(), verified={},
                               measurement=None, scope={}, provenance={},
                               execution_binding=binding, limitations=())


def dispatch(body, op_id, resolver_parameters=None):
    contract = make_contract(op_id)
    request = MutationRequest(target="T", mutation_type=MutationType.TOPOLOGY, value=None,
                               resolver_parameters=resolver_parameters)
    return execute_mutation_request_with_authority(
        request=request, body=body, contracts={("T", ""): contract}, synth=None,
    )


def real_serum_roundtrip(meta, body):
    """Load into a real Serum instance and read back what Serum itself saves."""
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


def render(meta, body):
    fd, tmp = tempfile.mkstemp(suffix=".bin"); os.close(fd)
    bridge.write_state_file(tmp, meta, body)
    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)
    synth.clear_midi()
    synth.add_midi_note(60, 100, 0.0, 1.5)
    engine.load_graph([(synth, [])])
    engine.render(2.0)
    return np.asarray(engine.get_audio())


def test_add_real_roundtrip():
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton
    proof = dispatch(body, "fx_struct_add_MAIN", {"slot_index": 0, "effect_structure": DISTORTION})
    assert proof.executed and proof.pathmerge_call_count == 1

    _, resaved = real_serum_roundtrip(meta, body)
    fx = resaved["FXRack0"]["FX"]
    assert len(fx) == 1 and "FXDistortion" in fx[0], f"real Serum did not accept the ADD: {fx}"
    print("[PASS] ADD: real Serum round-trip confirms 1 FXDistortion module present")


def test_remove_real_roundtrip():
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, skel_body = skeleton
    body = copy.deepcopy(skel_body)
    body["FXRack0"]["FX"] = [DISTORTION, DELAY]

    proof = dispatch(body, "fx_struct_remove_MAIN", {"slot_index": 0})
    assert proof.executed and proof.pathmerge_call_count == 1

    _, resaved = real_serum_roundtrip(meta, body)
    fx = resaved["FXRack0"]["FX"]
    assert len(fx) == 1 and "FXDelay" in fx[0], f"real Serum did not accept the REMOVE: {fx}"
    print("[PASS] REMOVE: real Serum round-trip confirms only FXDelay remains")


def test_replace_real_roundtrip():
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, skel_body = skeleton
    body = copy.deepcopy(skel_body)
    body["FXRack0"]["FX"] = [DISTORTION]

    proof = dispatch(body, "fx_struct_replace_MAIN", {"slot_index": 0, "effect_structure": DELAY})
    assert proof.executed and proof.pathmerge_call_count == 1

    _, resaved = real_serum_roundtrip(meta, body)
    fx = resaved["FXRack0"]["FX"]
    assert len(fx) == 1 and "FXDelay" in fx[0] and "FXDistortion" not in fx[0], \
        f"real Serum did not accept the REPLACE: {fx}"
    print("[PASS] REPLACE: real Serum round-trip confirms Distortion swapped for Delay")


def test_clear_rack_real_roundtrip():
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, skel_body = skeleton
    body = copy.deepcopy(skel_body)
    body["FXRack0"]["FX"] = [DISTORTION, DELAY]

    proof = dispatch(body, "fx_struct_clear_rack_MAIN")
    assert proof.executed and proof.pathmerge_call_count == 1

    _, resaved = real_serum_roundtrip(meta, body)
    assert resaved["FXRack0"]["FX"] == [], f"real Serum did not accept CLEAR_RACK: {resaved['FXRack0']['FX']}"
    print("[PASS] CLEAR_RACK: real Serum round-trip confirms empty rack")


def test_bypass_real_causal_effect():
    """The strongest test: BYPASS must not just round-trip as a state field,
    it must ACTUALLY SILENCE the distortion's effect on rendered audio."""
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, skel_body = skeleton

    body_active = copy.deepcopy(skel_body)
    body_active["FXRack0"]["FX"] = [DISTORTION]
    audio_active = render(meta, body_active)

    body_bypassed = copy.deepcopy(skel_body)
    body_bypassed["FXRack0"]["FX"] = [DISTORTION]
    proof = dispatch(body_bypassed, "fx_struct_bypass_MAIN", {"slot_index": 0})
    assert proof.executed and proof.pathmerge_call_count == 1
    assert proof.body_path == "FXRack0.FX.0.FXDistortion.plainParams"

    _, resaved = real_serum_roundtrip(meta, body_bypassed)
    assert resaved["FXRack0"]["FX"][0]["FXDistortion"]["plainParams"] == {"kParamEnable": 0.0}, \
        "real Serum did not accept the BYPASS state"

    audio_bypassed = render(meta, body_bypassed)

    mono_active = audio_active.mean(axis=0) if audio_active.ndim == 2 else audio_active
    mono_bypassed = audio_bypassed.mean(axis=0) if audio_bypassed.ndim == 2 else audio_bypassed
    diff_rms = float(np.sqrt(np.mean((mono_active - mono_bypassed) ** 2)))

    print(f"[PASS] BYPASS: real Serum round-trip confirms state; "
          f"audio RMS difference active-vs-bypassed = {diff_rms:.6f} "
          f"({'audible difference confirmed' if diff_rms > 1e-6 else 'WARNING: no audible difference'})")
    assert diff_rms > 1e-6, "BYPASS produced no measurable audio difference -- mechanism may not actually work"


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TOPOLOGY — REAL SERUM/DAWDREAMER ROUND-TRIP PROOF (per mechanism class)")
    print("=" * 80 + "\n")

    tests = [
        test_add_real_roundtrip,
        test_remove_real_roundtrip,
        test_replace_real_roundtrip,
        test_clear_rack_real_roundtrip,
        test_bypass_real_causal_effect,
    ]
    for t in tests:
        t()

    print("\nALL TOPOLOGY REAL-SERUM ROUND-TRIP TESTS PASSED")
