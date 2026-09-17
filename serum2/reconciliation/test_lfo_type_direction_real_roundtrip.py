#!/usr/bin/env python3
"""LFO TYPE / DIRECTION -- real Serum/DawDreamer round-trip proof.

Real evidence source: scanned all 745 real .SerumPreset files under the
local Serum 2 Presets library. No preset has `kParamDivision` or a
non-default `kParamBeatSync`, but 4 presets contain `kParamType` (values:
Lorenz, Path, RandomSH, Rossler) and several contain `kParamDirection`
(values: 1.0, 2.0) inside an LFO's plainParams dict alongside the
already-bound kParamMode/kParamRate/kParamBeatSync/kParamTriplets/
kParamDotted fields (see LFO1.TEMPO_SYNC's existing binding_provenance for
the established LFOx.plainParams.kParam<Name> pattern this generalizes).

This file proves TYPE (kParamType) and DIRECTION (kParamDirection) survive
a REAL Serum round trip (DawDreamer engine, the same standard as every
other BODY_STATE_FIELD binding in this registry) -- not just our own
codec's file format.

It ALSO records a genuine NEGATIVE finding for LFO.PRESET (curveDisplayName):
unlike TYPE/DIRECTION, curveDisplayName does NOT survive the DawDreamer
live-Serum round trip at all -- it collapses to None even with ZERO
mutation applied (Serum's VST3 processor-state save recomputes/drops it).
It DOES survive serum2.codec's own .SerumPreset file-format round trip
(same evidence tier as META_STRING). Because this project's BODY_STATE_FIELD
family's standing evidence bar is DawDreamer-verified, and curveDisplayName
demonstrably fails that bar, LFO.PRESET is NOT bound this pass -- binding it
under BODY_STATE_FIELD without flagging this would silently misrepresent
its evidence tier. Left NOT_YET_DERIVED, documented here so this negative
result is never re-discovered accidentally as a "surprise" regression.
"""

import copy
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import dawdreamer as daw

from serum2 import bridge, codec, vst3_state, pathmerge
from serum2.evidence import epoch as epoch_mod
from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding, STRUCTURAL_ONLY

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512
GOLDEN_PRESET = str(Path(__file__).parent.parent.parent / "archive" / "golden_presets" / "arp.SerumPreset")


def make_contract(path: str) -> CapabilityContract:
    binding = ExecutionBinding(mutation_type="BODY_STATE", body_path=path,
                                binding_source="test", binding_version="1.0")
    return CapabilityContract(target="T", allowed_operation="mutate_enum_value",
                               status=STRUCTURAL_ONLY, prerequisites=(), verified={},
                               measurement=None, scope={}, provenance={},
                               execution_binding=binding, limitations=())


def dispatch(body: dict, path: str, value):
    contract = make_contract(path)
    request = MutationRequest(target="T", mutation_type=MutationType.BODY_STATE, value=value, body_path=path)
    return execute_mutation_request_with_authority(
        request=request, body=body, contracts={("T", ""): contract}, synth=None,
    )


def real_serum_roundtrip(meta8: dict, body8: dict):
    fd, tmp = tempfile.mkstemp(suffix=".bin"); os.close(fd)
    bridge.write_state_file(tmp, meta8, body8)
    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)
    fd, out = tempfile.mkstemp(suffix=".bin"); os.close(fd)
    synth.save_state(out)
    raw = open(out, "rb").read(); os.remove(out)
    return codec.decode(vst3_state.unwrap_vc2(raw))


def _lfo_body():
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta8, body8, _ = bridge.build_v8_state(GOLDEN_PRESET, skeleton, module_prefixes=("LFO",))
    return meta8, body8


def test_type_roundtrip_active_lfo():
    """LFO0 (semantic LFO1) is an already-active modulation source in the
    golden arp preset (real curveData present) -- proves the mutation
    generalizes to an in-use LFO, not just a fresh default one."""
    meta8, body8 = _lfo_body()
    proof = dispatch(body8, "LFO0.plainParams.kParamType", "RandomSH")
    assert proof.executed and proof.mutation_succeeded

    _, resaved = real_serum_roundtrip(meta8, body8)
    got = pathmerge.read_path_value(resaved, "LFO0.plainParams.kParamType")
    assert got == "RandomSH", f"real Serum did not persist kParamType: {got!r}"
    print("[PASS] LFO1.TYPE (LFO0.plainParams.kParamType): real Serum round-trip confirms persistence")


def test_type_roundtrip_default_lfo():
    """LFO5 (semantic LFO6) starts completely unused (plainParams=='default'
    string sentinel) in the golden preset -- proves the mutation also works
    from a cold/inactive LFO slot, generalizing across all 6 LFOs."""
    meta8, body8 = _lfo_body()
    if not isinstance(body8["LFO5"].get("plainParams"), dict):
        body8["LFO5"]["plainParams"] = {}
    proof = dispatch(body8, "LFO5.plainParams.kParamType", "Rossler")
    assert proof.executed and proof.mutation_succeeded

    _, resaved = real_serum_roundtrip(meta8, body8)
    got = pathmerge.read_path_value(resaved, "LFO5.plainParams.kParamType")
    assert got == "Rossler", f"real Serum did not persist kParamType on a cold LFO slot: {got!r}"
    print("[PASS] LFO6.TYPE (LFO5.plainParams.kParamType): real Serum round-trip confirms persistence from cold slot")


def test_direction_roundtrip_active_lfo():
    meta8, body8 = _lfo_body()
    proof = dispatch(body8, "LFO0.plainParams.kParamDirection", 2.0)
    assert proof.executed and proof.mutation_succeeded

    _, resaved = real_serum_roundtrip(meta8, body8)
    got = pathmerge.read_path_value(resaved, "LFO0.plainParams.kParamDirection")
    assert got == 2.0, f"real Serum did not persist kParamDirection: {got!r}"
    print("[PASS] LFO1.DIRECTION (LFO0.plainParams.kParamDirection): real Serum round-trip confirms persistence")


def test_direction_roundtrip_default_lfo():
    meta8, body8 = _lfo_body()
    if not isinstance(body8["LFO5"].get("plainParams"), dict):
        body8["LFO5"]["plainParams"] = {}
    proof = dispatch(body8, "LFO5.plainParams.kParamDirection", 2.0)
    assert proof.executed and proof.mutation_succeeded

    _, resaved = real_serum_roundtrip(meta8, body8)
    got = pathmerge.read_path_value(resaved, "LFO5.plainParams.kParamDirection")
    assert got == 2.0, f"real Serum did not persist kParamDirection on a cold LFO slot: {got!r}"
    print("[PASS] LFO6.DIRECTION (LFO5.plainParams.kParamDirection): real Serum round-trip confirms persistence from cold slot")


def test_preset_curve_display_name_negative_evidence():
    """NEGATIVE EVIDENCE, not a guess: curveDisplayName does not survive the
    DawDreamer live-Serum round trip -- confirmed here even with ZERO
    mutation applied. LFO.PRESET is correctly left unbound this pass."""
    meta8, body8 = _lfo_body()
    assert body8["LFO0"]["curveDisplayName"] == "Custom"

    _, resaved_unmutated = real_serum_roundtrip(meta8, copy.deepcopy(body8))
    assert resaved_unmutated["LFO0"].get("curveDisplayName") is None, \
        "curveDisplayName unexpectedly survived an unmutated DawDreamer round trip -- re-investigate LFO.PRESET binding"

    mutated = copy.deepcopy(body8)
    proof = dispatch(mutated, "LFO0.curveDisplayName", "square")
    assert proof.executed and proof.mutation_succeeded  # in-memory mutation succeeds
    _, resaved_mutated = real_serum_roundtrip(meta8, mutated)
    assert resaved_mutated["LFO0"].get("curveDisplayName") != "square", \
        "curveDisplayName unexpectedly persisted through DawDreamer -- LFO.PRESET may now be bindable, re-investigate"

    # But it DOES survive our own .SerumPreset file-codec round trip (same
    # evidence tier as META_STRING) -- confirming this is a real
    # VST3-processor-state-vs-file-format distinction, not a broken test.
    meta5, body5 = codec.load_preset_file(GOLDEN_PRESET)
    body5["LFO0"]["curveDisplayName"] = "square"
    tmp = tempfile.mktemp(suffix=".SerumPreset")
    codec.dump_preset_file(tmp, meta5, body5)
    _, reloaded = codec.load_preset_file(tmp)
    os.remove(tmp)
    assert reloaded["LFO0"]["curveDisplayName"] == "square"
    print("[PASS] LFO1.PRESET: confirmed NEGATIVE for DawDreamer/live-Serum round-trip, "
          "confirmed POSITIVE for .SerumPreset file-codec round-trip -- correctly left unbound "
          "(evidence tier mismatch with BODY_STATE_FIELD's DawDreamer standard)")


if __name__ == "__main__":
    test_type_roundtrip_active_lfo()
    test_type_roundtrip_default_lfo()
    test_direction_roundtrip_active_lfo()
    test_direction_roundtrip_default_lfo()
    test_preset_curve_display_name_negative_evidence()
    print("\nALL LFO TYPE/DIRECTION REAL ROUND-TRIP TESTS PASSED")
