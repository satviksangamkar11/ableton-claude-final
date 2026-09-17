#!/usr/bin/env python3
"""MATRIX_ROUTE reconciliation pass -- real Serum round-trip regression
guard for the one binding derived this pass: MATRIX.OUT -> HOST_PARAMETER
'Mod 1 Out'. Same rigor as test_v3_fx_parameter_real_roundtrip.py: not a
mock, a real load into Serum via DawDreamer and readback from its own
save_state() output.
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


def test_matrix_out_capability_id_matches_registry():
    """The capability_id recorded in the registry for MATRIX.OUT must be
    reproducible from the canonicalization function, not a typed-in guess."""
    binding = canonicalize_host_parameter("Mod 1 Out")
    cap_id = compute_capability_id("HOST_PARAMETER", binding)
    assert cap_id == "HOST_PARAMETER:67031f6d900603a5", cap_id


def test_mod_1_out_real_roundtrip():
    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    params = synth.get_parameters_description()
    by_name = {p["name"]: p for p in params}
    assert "Mod 1 Out" in by_name, "live VST3 param list no longer has 'Mod 1 Out'"
    idx = by_name["Mod 1 Out"]["index"]

    binding = ExecutionBinding(mutation_type="HOST_PARAMETER", host_parameter_name="Mod 1 Out",
                                binding_source="test", binding_version="1.0")
    contract = CapabilityContract(target="T", allowed_operation="mutate_numeric_value",
                                   status="CAUSAL_VERIFIED", prerequisites=(), verified={},
                                   measurement=None, scope={}, provenance={},
                                   execution_binding=binding, limitations=())
    probe = 0.72
    request = MutationRequest(target="T", mutation_type=MutationType.HOST_PARAMETER, value=probe,
                               host_parameter_name="Mod 1 Out")
    proof = execute_mutation_request_with_authority(request=request, body={},
                                                      contracts={("T", ""): contract}, synth=synth)
    assert proof.executed, proof.detail
    assert abs(synth.get_parameter(idx) - probe) < 1e-4

    # settle + save/reload (same systemic fix as serum2/verify/bulk.py)
    engine.load_graph([(synth, [])])
    engine.render(BLOCK / SR)
    fd, tmp = tempfile.mkstemp(suffix=".bin"); os.close(fd)
    synth.save_state(tmp)

    engine2 = daw.RenderEngine(SR, BLOCK)
    synth2 = engine2.make_plugin_processor("serum", VST3)
    synth2.load_state(tmp)
    os.remove(tmp)
    reloaded = synth2.get_parameter(idx)
    assert abs(reloaded - probe) < 1e-4, f"requested {probe}, reloaded as {reloaded}"
    print(f"[PASS] Mod 1 Out: real Serum readback {reloaded} (requested {probe})")


if __name__ == "__main__":
    test_matrix_out_capability_id_matches_registry()
    print("[PASS] test_matrix_out_capability_id_matches_registry")
    test_mod_1_out_real_roundtrip()
    print("\nALL MATRIX_ROUTE V4 REAL-SERUM ROUND-TRIP TESTS PASSED")
