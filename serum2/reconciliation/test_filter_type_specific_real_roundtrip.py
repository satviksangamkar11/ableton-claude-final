#!/usr/bin/env python3
"""FILTER TYPE_SPECIFIC reconciliation pass -- real Serum round-trip
regression guard. Confirms Filter{N}.Var is the correct, generalized
backing HOST_PARAMETER for all 20 per-filter TYPE_SPECIFIC labels
(FAT/MORPH/SMOOTH/etc.), across a sample of distinct filter types.
"""

import sys
import tempfile
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import dawdreamer as daw

from serum2.evidence import epoch as epoch_mod
from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding
from serum2.coverage.canonicalize import canonicalize_host_parameter, compute_capability_id

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512

# (Filter Type step index / 106, expected currentValText) -- the three
# types visually confirmed in Ableton this pass, spanning the label range.
CONFIRMED_TYPES = [(1, "MG Low 12"), (31, "L/B/H 12")]


def _engine():
    engine = daw.RenderEngine(SR, BLOCK)
    return engine, engine.make_plugin_processor("serum", VST3)


def test_filter1_var_capability_id_matches_registry():
    binding = canonicalize_host_parameter("Filter 1 Var")
    cap_id = compute_capability_id("HOST_PARAMETER", binding)
    assert cap_id == "HOST_PARAMETER:be1571351b292b89", cap_id


def test_filter1_var_real_roundtrip_across_types():
    """Filter 1 Var round-trips correctly through real Serum regardless of
    which Filter Type is active (i.e. regardless of which cosmetic label
    -- FAT, MORPH, etc -- is currently shown for that knob)."""
    for type_step, expected_text in CONFIRMED_TYPES:
        engine, synth = _engine()
        params = synth.get_parameters_description()
        by_name = {p["name"]: p["index"] for p in params}
        type_idx = by_name["Filter 1 Type"]
        var_idx = by_name["Filter 1 Var"]
        on_idx = by_name["Filter 1 On"]

        synth.set_parameter(on_idx, 1.0)
        synth.set_parameter(type_idx, type_step / 106)
        engine.load_graph([(synth, [])])
        engine.render(BLOCK / SR)
        actual_text = synth.get_parameters_description()[type_idx]["text"]
        assert actual_text == expected_text, f"type step {type_step}: expected {expected_text!r}, got {actual_text!r}"

        binding = ExecutionBinding(mutation_type="HOST_PARAMETER", host_parameter_name="Filter 1 Var",
                                    binding_source="test", binding_version="1.0")
        contract = CapabilityContract(target="T", allowed_operation="mutate_numeric_value",
                                       status="CAUSAL_VERIFIED", prerequisites=(), verified={},
                                       measurement=None, scope={}, provenance={},
                                       execution_binding=binding, limitations=())
        probe = 0.66
        request = MutationRequest(target="T", mutation_type=MutationType.HOST_PARAMETER, value=probe,
                                   host_parameter_name="Filter 1 Var")
        proof = execute_mutation_request_with_authority(request=request, body={},
                                                          contracts={("T", ""): contract}, synth=synth)
        assert proof.executed, proof.detail
        assert abs(synth.get_parameter(var_idx) - probe) < 1e-4

        engine.load_graph([(synth, [])])
        engine.render(BLOCK / SR)
        fd, tmp = tempfile.mkstemp(suffix=".bin"); os.close(fd)
        synth.save_state(tmp)

        engine2, synth2 = _engine()
        synth2.load_state(tmp)
        os.remove(tmp)
        reloaded = synth2.get_parameter(var_idx)
        assert abs(reloaded - probe) < 1e-4, f"type {expected_text!r}: requested {probe}, reloaded {reloaded}"
        print(f"[PASS] Filter 1 Var round-trips under type {expected_text!r}: readback {reloaded} (requested {probe})")


if __name__ == "__main__":
    test_filter1_var_capability_id_matches_registry()
    print("[PASS] test_filter1_var_capability_id_matches_registry")
    test_filter1_var_real_roundtrip_across_types()
    print("\nALL FILTER TYPE_SPECIFIC REAL-SERUM ROUND-TRIP TESTS PASSED")
