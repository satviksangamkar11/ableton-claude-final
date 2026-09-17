#!/usr/bin/env python3
"""V3 population pass -- real Serum/DawDreamer round-trip proof for the
FX_PARAMETER (BODY_STATE_FIELD) bindings, using the same rigor applied to
every other primitive this session: not just a real dispatch against an
in-memory body, but a real load into Serum and readback from Serum's own
save_state() output.

Also the same class of caught bug as elsewhere this session: the initial
V3 matching pass trusted fx_resolver_complete.py's catalog (disconnected
from the real dispatch path) and would have shipped 19 non-dispatchable
bindings. Re-verified here against real Serum for one representative
capability per distinct effect family bound this pass.
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
from serum2.operations.fx_resolver import resolve_fx_parameter

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512


def make_contract():
    binding = ExecutionBinding(mutation_type="BODY_STATE", resolver_operation_id="fx_set_parameter",
                                binding_source="test", binding_version="1.0")
    return CapabilityContract(target="T", allowed_operation="mutate_numeric_value",
                               status="CAUSAL_VERIFIED", prerequisites=(), verified={},
                               measurement=None, scope={}, provenance={},
                               execution_binding=binding, limitations=())


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


# Real (type_index -> FX-type-key) mapping, captured from Serum's own
# output across archive/golden_presets/*.SerumPreset this session. Serum's
# `type` integer field is AUTHORITATIVE at load time -- it determines the
# actual effect, not whichever dict key sits next to it (found the hard
# way: a body with type=0 alongside an "FXDelay" key round-tripped back as
# FXDistortion, silently discarding the mismatched key). Only entries
# confirmed against a real preset are listed; guessing the rest is exactly
# what this whole session has been avoiding. Note "FXBode" (title case),
# NOT "FXBODE" -- an earlier draft of this file had the wrong casing,
# caught by this same real-round-trip check.
CONFIRMED_FX_TYPE_INDEX = {
    "FXDistortion": 0, "FXPhaser": 2, "FXDelay": 4, "FXComp": 5,
    "FXReverb": 6, "FXEQ": 7, "FXHyperD": 9, "FXBode": 10, "FXConv": 11,
    "FXUtils": 12,
}


def check_one(effect, parameter, fx_type_key, probe_value):
    if fx_type_key not in CONFIRMED_FX_TYPE_INDEX:
        raise ValueError(f"{fx_type_key}: no confirmed real type index captured this "
                          f"session -- would have to guess, refusing")
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, skel_body = skeleton
    body = copy.deepcopy(skel_body)
    body["FXRack0"]["FX"] = [{"type": CONFIRMED_FX_TYPE_INDEX[fx_type_key], fx_type_key: {"plainParams": {}}}]

    contract = make_contract()
    request = MutationRequest(target="T", mutation_type=MutationType.BODY_STATE, value=probe_value,
                               resolver_parameters={"rack": 0, "slot": 0, "effect": effect, "parameter": parameter})
    proof = execute_mutation_request_with_authority(
        request=request, body=body, contracts={("T", ""): contract}, synth=None,
    )
    assert proof.executed and proof.pathmerge_call_count == 1, f"{effect}/{parameter}: {proof.detail}"

    _, resaved = real_serum_roundtrip(meta, body)
    fx = resaved["FXRack0"]["FX"]
    assert len(fx) == 1 and fx_type_key in fx[0], f"real Serum did not accept the FX module: {fx}"
    param_key = f"kParam{parameter}"
    plain_params = fx[0][fx_type_key].get("plainParams")
    assert isinstance(plain_params, dict), \
        f"real Serum did not preserve a plainParams dict for {fx_type_key}: {fx[0][fx_type_key]!r}"
    readback = plain_params.get(param_key)
    assert readback is not None, f"real Serum did not preserve {param_key}: {fx[0][fx_type_key]}"

    print(f"[PASS] {effect}/{parameter}: real Serum readback {param_key}={readback} "
          f"(requested {probe_value})")


def test_distortion_drive_real_roundtrip():
    resolved = resolve_fx_parameter("Distortion", "Drive", 0, 0)
    mid = (resolved.min_value + resolved.max_value) / 2.0
    check_one("Distortion", "Drive", "FXDistortion", mid)


def test_delay_feedback_real_roundtrip():
    resolved = resolve_fx_parameter("Delay", "Feedback", 0, 0)
    mid = (resolved.min_value + resolved.max_value) / 2.0
    check_one("Delay", "Feedback", "FXDelay", mid)


def test_compressor_attack_real_roundtrip():
    resolved = resolve_fx_parameter("Compressor", "Attack", 0, 0)
    mid = (resolved.min_value + resolved.max_value) / 2.0
    check_one("Compressor", "Attack", "FXComp", mid)


def test_bode_range_real_roundtrip():
    resolved = resolve_fx_parameter("BODE", "Range", 0, 0)
    mid = (resolved.min_value + resolved.max_value) / 2.0
    check_one("BODE", "Range", "FXBode", mid)


def test_hyper_rate_real_roundtrip():
    resolved = resolve_fx_parameter("Hyper", "Rate", 0, 0)
    mid = (resolved.min_value + resolved.max_value) / 2.0
    check_one("Hyper", "Rate", "FXHyperD", mid)


def test_phaser_phase_real_roundtrip_and_kparamphase_regression_guard():
    """Permanent regression guard for the Phaser/Phase finding (V3 Pass 2
    UI Truth Gate, real-Serum-in-Ableton manual-UI-edit forensic diff):
    the UI's "Phase" knob is genuinely controlled by kParamWidth, not
    kParamPhase. Confirmed by manually setting the Phase knob to 90 in a
    real running Serum instance and inspecting Serum's OWN saved
    .SerumPreset output -- it contained kParamWidth=90.0 and no
    kParamPhase key at all (Serum silently drops unrecognized plainParams
    keys rather than erroring, so the old binding was a false positive
    that never reached the real control).

    resolve_fx_parameter("Phaser", "Phase", ...) must resolve to
    kParamWidth: if this ever points back at kParamPhase, this is the
    same defect regressing."""
    resolved = resolve_fx_parameter("Phaser", "Phase", 0, 0)
    assert resolved.state_path.endswith("kParamWidth"), (
        f"Phaser/Phase must resolve to kParamWidth (real Serum-confirmed "
        f"binding), got: {resolved.state_path}"
    )
    # NOT the range midpoint: Phase's default is 180.0 (the exact midpoint
    # of its 0-360 range), and writing a param to its own default value
    # correctly collapses Serum's presence-preserving plainParams back to
    # the "default" sentinel string -- real, correct Serum behavior, not a
    # round-trip failure. Use an off-default probe so this test actually
    # exercises persistence.
    probe = 90.0
    assert probe != (resolved.min_value + resolved.max_value) / 2.0

    # Positive: the real (fixed) binding round-trips through actual Serum.
    # (Not check_one() -- it derives the expected key as kParam{parameter}
    # ("kParamPhase"), but the real persisted key is kParamWidth, exactly
    # the mismatch this test exists to catch.)
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, skel_body = skeleton
    body = copy.deepcopy(skel_body)
    body["FXRack0"]["FX"] = [{"type": CONFIRMED_FX_TYPE_INDEX["FXPhaser"], "FXPhaser": {"plainParams": {}}}]
    contract = make_contract()
    request = MutationRequest(target="T", mutation_type=MutationType.BODY_STATE, value=probe,
                               resolver_parameters={"rack": 0, "slot": 0, "effect": "Phaser", "parameter": "Phase"})
    proof = execute_mutation_request_with_authority(
        request=request, body=body, contracts={("T", ""): contract}, synth=None,
    )
    assert proof.executed and proof.pathmerge_call_count == 1, f"Phaser/Phase: {proof.detail}"
    _, resaved = real_serum_roundtrip(meta, body)
    fx = resaved["FXRack0"]["FX"]
    assert len(fx) == 1 and "FXPhaser" in fx[0], f"real Serum did not accept the FX module: {fx}"
    plain_params = fx[0]["FXPhaser"].get("plainParams")
    assert isinstance(plain_params, dict), \
        f"real Serum did not preserve a plainParams dict for FXPhaser: {plain_params!r}"
    readback = plain_params.get("kParamWidth")
    assert readback is not None, f"real Serum did not preserve kParamWidth: {plain_params}"
    print(f"[PASS] Phaser/Phase: real Serum readback kParamWidth={readback} (requested {probe})")

    # Negative: kParamPhase (the old, wrong binding) must NOT round-trip --
    # proving the original defect was real, not a fluke of the test harness.
    # (check_one's minimal skeleton -- plainParams: {} with no other seeded
    # fields -- is what every other passing effect in this file uses; Serum
    # fills in structural siblings like "lfophasor" itself on save.)
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, skel_body = skeleton
    body = copy.deepcopy(skel_body)
    body["FXRack0"]["FX"] = [{"type": CONFIRMED_FX_TYPE_INDEX["FXPhaser"],
                               "FXPhaser": {"plainParams": {"kParamPhase": probe}}}]
    _, resaved = real_serum_roundtrip(meta, body)
    fx = resaved["FXRack0"]["FX"]
    plain_params_neg = fx[0]["FXPhaser"].get("plainParams")
    phase_readback = plain_params_neg.get("kParamPhase") if isinstance(plain_params_neg, dict) else None
    assert phase_readback is None, (
        f"kParamPhase unexpectedly round-tripped through real Serum "
        f"(readback={phase_readback}) -- if this is now real, the resolver "
        f"fix this test guards may need re-investigation"
    )
    print("[PASS] Phaser/Phase: kParamPhase confirmed still silently dropped by real Serum")


def test_convolve_correctly_excluded_regression_guard():
    """Permanent regression guard for the Convolve finding: a real captured
    Convolve entry has no "plainParams" at all, so mutating kParamIRGain
    genuinely does not round-trip. This proves the exclusion in
    serum2_execution_coverage_registry_v3_builder.py's CONFIRMED_SAFE_EFFECTS
    is evidence-based, not just asserted -- if this test ever starts
    passing, Convolve may be safe to re-include."""
    resolved = resolve_fx_parameter("Convolve", "IRGain", 0, 0)
    mid = (resolved.min_value + resolved.max_value) / 2.0
    try:
        check_one("Convolve", "IRGain", "FXConv", mid)
        raise AssertionError(
            "Convolve/IRGain round-tripped successfully -- if this is now "
            "real, un-exclude Convolve in CONFIRMED_SAFE_EFFECTS instead of "
            "leaving this guard stale"
        )
    except AssertionError as e:
        if "did not preserve" in str(e) or "did not accept" in str(e):
            print("[PASS] Convolve/IRGain confirmed still non-functional against real Serum "
                  "(no plainParams materializes) -- exclusion remains correct")
        else:
            raise


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("V3 POPULATION — FX_PARAMETER (BODY_STATE_FIELD) REAL SERUM ROUND-TRIP")
    print("=" * 80 + "\n")

    tests = [
        test_distortion_drive_real_roundtrip,
        test_delay_feedback_real_roundtrip,
        test_compressor_attack_real_roundtrip,
        test_bode_range_real_roundtrip,
        test_hyper_rate_real_roundtrip,
        test_phaser_phase_real_roundtrip_and_kparamphase_regression_guard,
        test_convolve_correctly_excluded_regression_guard,
    ]
    for t in tests:
        t()

    print("\nALL V3 FX_PARAMETER REAL-SERUM ROUND-TRIP TESTS PASSED")
