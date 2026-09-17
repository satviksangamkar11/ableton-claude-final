#!/usr/bin/env python3
"""MATRIX LFO-bus destinations -- real Serum round-trip proof for the new
a3_modulation_route._DESTINATIONS entries (LFO2-10.Rate/Smooth/Rise/Delay/
Phase, Macro5-8), discovered by scanning all 745 real .SerumPreset files in
the local library for real ModSlot.destModuleTypeString=='LFO'/'Macro'
entries (Serum's own serialized destModuleParamName/destModuleParamID/
destModuleID -- not inferred).

Proves compound_create_modulation_route (already-wired COMPOUND resolver)
creates a route into a genuinely NEW destination (LFO3.Rate, moduleID=2,
previously absent from the table) that a REAL Serum instance accepts and
round-trips -- not just something our own dict lookup believes is valid.
"""

import sys
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
from serum2.qualification.a3_modulation_route import get_destination

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512


def make_contract():
    binding = ExecutionBinding(mutation_type="COMPOUND", resolver_operation_id="compound_create_modulation_route",
                                binding_source="test", binding_version="1.0")
    return CapabilityContract(target="T", allowed_operation="mutate_structured_value",
                               status="STRUCTURAL_ONLY", prerequisites=(), verified={},
                               measurement=None, scope={}, provenance={},
                               execution_binding=binding, limitations=())


def dispatch_route(body, source, destination, amount=0.5):
    contract = make_contract()
    request = MutationRequest(target="T", mutation_type=MutationType.COMPOUND, value=None,
                               resolver_parameters={"source": source, "destination": destination, "amount": amount})
    return execute_mutation_request_with_authority(
        request=request, body=body, contracts={("T", ""): contract}, synth=None,
    )


def real_serum_roundtrip(meta, body):
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


def test_lfo3_rate_destination_real_roundtrip():
    """LFO3.Rate (moduleID=2) previously had NO table entry at all."""
    dest = get_destination("LFO3.Rate")
    assert dest.dest_module_type_string == "LFO" and dest.dest_module_id == 2 and dest.dest_module_param_id == 0

    meta, body = bridge.capture_v8_skeleton(VST3)
    proof = dispatch_route(body, source="LFO1", destination="LFO3.Rate", amount=0.6)
    assert proof.executed, proof.detail
    assert proof.pathmerge_call_count == 1

    _, resaved = real_serum_roundtrip(meta, body)
    matched = [ms for k, ms in resaved.items()
               if k.startswith("ModSlot") and isinstance(ms, dict)
               and ms.get("destModuleTypeString") == "LFO" and ms.get("destModuleID") == 2
               and ms.get("destModuleParamID") == 0]
    assert matched, f"real Serum did not accept the LFO3.Rate route: {[k for k in resaved if k.startswith('ModSlot')]}"
    print(f"[PASS] LFO3.Rate destination: real Serum round-trip confirms {matched[0]}")


def test_macro5_destination_real_roundtrip():
    """Macro5 (moduleID=4) previously had NO table entry at all."""
    dest = get_destination("Macro5")
    assert dest.dest_module_type_string == "Macro" and dest.dest_module_id == 4

    meta, body = bridge.capture_v8_skeleton(VST3)
    proof = dispatch_route(body, source="LFO1", destination="Macro5", amount=0.4)
    assert proof.executed, proof.detail

    _, resaved = real_serum_roundtrip(meta, body)
    matched = [ms for k, ms in resaved.items()
               if k.startswith("ModSlot") and isinstance(ms, dict)
               and ms.get("destModuleTypeString") == "Macro" and ms.get("destModuleID") == 4]
    assert matched, f"real Serum did not accept the Macro5 route: {[k for k in resaved if k.startswith('ModSlot')]}"
    print(f"[PASS] Macro5 destination: real Serum round-trip confirms {matched[0]}")


if __name__ == "__main__":
    test_lfo3_rate_destination_real_roundtrip()
    test_macro5_destination_real_roundtrip()
    print("\nALL MATRIX LFO-BUS/MACRO DESTINATION REAL ROUND-TRIP TESTS PASSED")
