#!/usr/bin/env python3
"""LFO Dotted/Triplet reconciliation pass -- real Serum round-trip
regression guard. Forensic method: manual UI toggle (TRIP/DOT buttons on
the LFO panel) -> Serum's own save -> CBOR diff -- same as the
FXPhaser.Phase (kParamWidth) finding. Discovered LFO{N}.plainParams.
kParamDotted / kParamTriplets as direct BODY_STATE fields, no HOST_PARAMETER
equivalent exists (checked: no "Sync"/"Trip"/"Dott" live VST3 param name).

Also guards a distinct, real Serum behavior found while verifying this in
bulk: Serum's CBOR writer sparse-prunes an individual field at ITS OWN
default value even when a sibling field in the same dict is non-default --
not just the whole-dict collapse-to-"default"-string seen elsewhere. A
readback of None for a field explicitly set to its own default (0.0) is
the CORRECT persisted representation, not a failure.
"""

import sys
import copy
import tempfile
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import dawdreamer as daw

from serum2 import bridge, codec, vst3_state, pathmerge
from serum2.evidence import epoch as epoch_mod
from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding
from serum2.coverage.canonicalize import canonicalize_body_state, compute_capability_id

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512


def _rt(meta, body):
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


def _mutate(body, path, value):
    binding = ExecutionBinding(mutation_type="BODY_STATE", body_path=path,
                                binding_source="test", binding_version="1.0")
    contract = CapabilityContract(target="T", allowed_operation="mutate_numeric_value",
                                   status="CAUSAL_VERIFIED", prerequisites=(), verified={},
                                   measurement=None, scope={}, provenance={},
                                   execution_binding=binding, limitations=())
    request = MutationRequest(target="T", mutation_type=MutationType.BODY_STATE, value=value, body_path=path)
    proof = execute_mutation_request_with_authority(request=request, body=body,
                                                      contracts={("T", ""): contract}, synth=None)
    assert proof.executed, proof.detail


def test_lfo0_dotted_capability_id_matches_registry():
    binding = canonicalize_body_state("LFO0.plainParams.kParamDotted")
    cap_id = compute_capability_id("BODY_STATE_FIELD", binding)
    assert cap_id == "BODY_STATE_FIELD:b15467af8508a265", cap_id


def test_lfo0_triplets_capability_id_matches_registry():
    binding = canonicalize_body_state("LFO0.plainParams.kParamTriplets")
    cap_id = compute_capability_id("BODY_STATE_FIELD", binding)
    assert cap_id == "BODY_STATE_FIELD:e80065f698dc353e", cap_id


def test_lfo0_dotted_and_triplets_real_roundtrip():
    meta, skel = bridge.capture_v8_skeleton(VST3)
    body = copy.deepcopy(skel)
    _mutate(body, "LFO0.plainParams.kParamDotted", 1.0)
    _mutate(body, "LFO0.plainParams.kParamTriplets", 1.0)
    _, resaved = _rt(meta, body)
    dotted = pathmerge.read_path_value(resaved, "LFO0.plainParams.kParamDotted")
    triplets = pathmerge.read_path_value(resaved, "LFO0.plainParams.kParamTriplets")
    assert dotted == 1.0, f"kParamDotted did not round-trip: {dotted}"
    assert triplets == 1.0, f"kParamTriplets did not round-trip: {triplets}"
    print(f"[PASS] LFO0: kParamDotted={dotted}, kParamTriplets={triplets} (both requested 1.0)")


def test_lfo0_dotted_sparse_pruned_at_default_regression_guard():
    """Permanent regression guard for the sparse-pruning finding: setting
    kParamDotted to ITS OWN default (0.0) while a sibling (kParamTriplets)
    stays non-default must NOT round-trip as an explicit 0.0 key -- Serum
    omits it. If this ever starts round-tripping as an explicit 0.0, the
    bulk verifier's sparse-collapse handling may need re-investigation."""
    meta, skel = bridge.capture_v8_skeleton(VST3)
    body = copy.deepcopy(skel)
    _mutate(body, "LFO0.plainParams.kParamTriplets", 1.0)
    _mutate(body, "LFO0.plainParams.kParamDotted", 0.0)
    _, resaved = _rt(meta, body)
    dotted = pathmerge.read_path_value(resaved, "LFO0.plainParams.kParamDotted")
    triplets = pathmerge.read_path_value(resaved, "LFO0.plainParams.kParamTriplets")
    assert dotted is None, (
        f"kParamDotted=0.0 unexpectedly round-tripped as an explicit key (readback={dotted}) -- "
        f"if this is now real, the bulk verifier's sparse-pruning handling may need re-investigation"
    )
    assert triplets == 1.0, f"sibling kParamTriplets should stay 1.0: {triplets}"
    print(f"[PASS] LFO0: kParamDotted=0.0 correctly sparse-pruned (readback=None) "
          f"while sibling kParamTriplets={triplets} stayed materialized")


def test_lfo0_beatsync_capability_id_matches_registry():
    binding = canonicalize_body_state("LFO0.plainParams.kParamBeatSync")
    cap_id = compute_capability_id("BODY_STATE_FIELD", binding)
    assert cap_id == "BODY_STATE_FIELD:cae5fd974a19fe44", cap_id


def test_lfo0_beatsync_real_roundtrip():
    """kParamBeatSync default is 1.0 (BPM-synced) -- the inverse of
    Dotted/Triplets' default (0.0) -- found via the manual BPM/HZ toggle
    UI check -> Serum-own-save -> CBOR diff (HZ mode produced an explicit
    kParamBeatSync=0.0 alongside the existing Dotted/Triplets keys)."""
    meta, skel = bridge.capture_v8_skeleton(VST3)
    body = copy.deepcopy(skel)
    _mutate(body, "LFO0.plainParams.kParamDotted", 1.0)
    _mutate(body, "LFO0.plainParams.kParamBeatSync", 0.0)
    _, resaved = _rt(meta, body)
    beatsync = pathmerge.read_path_value(resaved, "LFO0.plainParams.kParamBeatSync")
    dotted = pathmerge.read_path_value(resaved, "LFO0.plainParams.kParamDotted")
    assert beatsync == 0.0, f"kParamBeatSync=0.0 did not round-trip: {beatsync}"
    assert dotted == 1.0, f"sibling kParamDotted should stay 1.0: {dotted}"
    print(f"[PASS] LFO0: kParamBeatSync={beatsync} (Hz mode), sibling kParamDotted={dotted}")


if __name__ == "__main__":
    test_lfo0_dotted_capability_id_matches_registry()
    print("[PASS] test_lfo0_dotted_capability_id_matches_registry")
    test_lfo0_triplets_capability_id_matches_registry()
    print("[PASS] test_lfo0_triplets_capability_id_matches_registry")
    test_lfo0_dotted_and_triplets_real_roundtrip()
    test_lfo0_dotted_sparse_pruned_at_default_regression_guard()
    test_lfo0_beatsync_capability_id_matches_registry()
    print("[PASS] test_lfo0_beatsync_capability_id_matches_registry")
    test_lfo0_beatsync_real_roundtrip()
    print("\nALL LFO DOTTED/TRIPLET/BEATSYNC REAL-SERUM ROUND-TRIP TESTS PASSED")
