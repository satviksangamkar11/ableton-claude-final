"""STEP 20B PART 4: Filter Level/Mix persistence - comprehensive regression suite.

Persistent representation (proven via real Serum UI text-entry + native save +
CBOR decode + DawDreamer VST3 host-param cross-check):

  VoiceFilter0.plainParams.kParamLevelOut / kParamWet   (FILTER1)
  VoiceFilter1.plainParams.kParamLevelOut / kParamWet   (FILTER2)

  kParamLevelOut: dB-scale amplitude curve, formula = 10^((dB-12)/40).
    Solved from 3 independent real-UI calibration points (-8.5dB, -6dB, +6dB,
    +12dB) which fit the formula with zero residual. The "explicit 0.0dB" UI
    entry was found to be an ANOMALOUS special case (stores literal 0.0,
    a reset-to-default sentinel) and is excluded from the fitted curve.
    Direct 1:1 passthrough to VST3 host param "Filter {N} Level".

  kParamWet: simple linear 0..100 percentage (0%, 25%, 42%, 55%, 78%, 100%
    all confirmed exact). Direct 1:1 (/100) passthrough to VST3 host param
    "Filter {N} Wet".

  Container is VoiceFilter{0,1}.plainParams — NOT Oscillator.plainParams
  (unlike Pan/Level from PART 1) and NOT RoutingSlot (unlike sends from
  PART 3). Filter index 0=FILTER1, 1=FILTER2, confirmed via real UI
  right-click parameter-name tooltips ("Filter 1 Wet" / "Filter 2 Wet").
"""
import os
import tempfile
import copy
import dawdreamer as daw
from serum2 import bridge, codec, vst3_state, pathmerge
from serum2.evidence import epoch as epoch_mod

VST3 = epoch_mod.SERUM_VST3
SR = 44100
BLOCK = 512


def level_out_from_db(db):
    return 10 ** ((db - 12) / 40)


def find_param(synth, name):
    for p in synth.get_plugin_parameters_description():
        if p["name"] == name:
            return synth.get_parameter(p["index"])
    return None


def load_body(body):
    meta = bridge.capture_v8_skeleton(VST3)[0]
    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)
    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)
    return engine, synth


def fresh_skeleton_body():
    return copy.deepcopy(bridge.capture_v8_skeleton(VST3)[1])


# ---------------------------------------------------------------------------
# PART 1: FILTER 1 LEVEL
# ---------------------------------------------------------------------------

def test_filter1_level_db_formula():
    """kParamLevelOut = 10^((dB-12)/40), verified against real UI calibration points."""
    calibration = [(-8.5, 0.30725574493408203), (-6.0, 0.3548133969306946),
                   (6.0, 0.7079457640647888), (12.0, 1.0)]
    for db, real_value in calibration:
        predicted = level_out_from_db(db)
        assert abs(predicted - real_value) < 1e-6, \
            f"dB={db}: predicted={predicted}, real UI value={real_value}"
    print("[PASS] Filter1 Level dB formula matches 4 real UI calibration points exactly")


def test_filter1_level_persistence():
    body = fresh_skeleton_body()
    value = level_out_from_db(-8.5)
    pathmerge.apply_path_value(body, "VoiceFilter0.plainParams.kParamLevelOut", value)

    engine, synth = load_body(body)
    assert abs(find_param(synth, "Filter 1 Level") - value) < 1e-6
    del engine
    print("[PASS] Filter1 Level persistence + VST3 readback (1:1 passthrough)")


# ---------------------------------------------------------------------------
# PART 2: FILTER 1 MIX/WET
# ---------------------------------------------------------------------------

def test_filter1_wet_scale_linearity():
    for pct, expected in [(0, 0.0), (25, 0.25), (42, 0.42), (78, 0.78), (100, 1.0)]:
        body = fresh_skeleton_body()
        pathmerge.apply_path_value(body, "VoiceFilter0.plainParams.kParamWet", float(pct))
        engine, synth = load_body(body)
        val = find_param(synth, "Filter 1 Wet")
        del engine
        assert abs(val - expected) < 1e-4, f"pct={pct}: expected {expected}, got {val}"
    print("[PASS] Filter1 Wet scale is linear 0..100 == host param 0..1")


# ---------------------------------------------------------------------------
# PART 3: SIBLING ISOLATION
# ---------------------------------------------------------------------------

def test_filter1_level_wet_sibling_isolation():
    body = fresh_skeleton_body()
    body["VoiceFilter0"]["plainParams"] = {
        "kParamLevelOut": level_out_from_db(-6.0),
        "kParamWet": 78.0,
    }
    before_wet = body["VoiceFilter0"]["plainParams"]["kParamWet"]

    # Mutate ONLY Level; Wet sibling must survive unchanged
    pathmerge.apply_path_value(body, "VoiceFilter0.plainParams.kParamLevelOut", level_out_from_db(6.0))
    assert body["VoiceFilter0"]["plainParams"]["kParamWet"] == before_wet, \
        "Wet sibling was affected by Level mutation!"

    before_level = body["VoiceFilter0"]["plainParams"]["kParamLevelOut"]
    # Mutate ONLY Wet; Level sibling must survive unchanged
    pathmerge.apply_path_value(body, "VoiceFilter0.plainParams.kParamWet", 30.0)
    assert body["VoiceFilter0"]["plainParams"]["kParamLevelOut"] == before_level, \
        "Level sibling was affected by Wet mutation!"

    print("[PASS] Filter1 Level/Wet sibling isolation (dict-merge)")


def test_isolation_from_other_state():
    """Filter1 Level/Wet mutation must not alter Filter2, BUS sends, OSC pan/level."""
    body = fresh_skeleton_body()
    pathmerge.apply_path_value(body, "Oscillator0.plainParams.kParamPan", -25.0)
    pathmerge.apply_path_value(body, "Oscillator0.plainParams.kParamVolume", 0.64)
    pathmerge.apply_path_value(body, "RoutingSlot0.plainParams.kParamFXBus1Level", 65.0)
    pathmerge.apply_path_value(body, "VoiceFilter1.plainParams.kParamLevelOut", level_out_from_db(3.0))
    pathmerge.apply_path_value(body, "VoiceFilter1.plainParams.kParamWet", 20.0)

    before_osc0 = copy.deepcopy(body["Oscillator0"]["plainParams"])
    before_routing0 = copy.deepcopy(body["RoutingSlot0"]["plainParams"])
    before_vf1 = copy.deepcopy(body["VoiceFilter1"]["plainParams"])

    pathmerge.apply_path_value(body, "VoiceFilter0.plainParams.kParamLevelOut", level_out_from_db(-6.0))
    pathmerge.apply_path_value(body, "VoiceFilter0.plainParams.kParamWet", 78.0)

    assert body["Oscillator0"]["plainParams"] == before_osc0, "OSC0 pan/level leaked!"
    assert body["RoutingSlot0"]["plainParams"] == before_routing0, "BUS send leaked!"
    assert body["VoiceFilter1"]["plainParams"] == before_vf1, "Filter2 leaked!"

    print("[PASS] Filter1 mutation isolated from OSC pan/level, BUS sends, and Filter2")


# ---------------------------------------------------------------------------
# PART 4: FILTER 2 (genericity — proven independently, not assumed)
# ---------------------------------------------------------------------------

def test_filter2_level_db_formula():
    """Filter2 uses the SAME formula, confirmed via a real UI calibration point (-4dB)."""
    real_value = 0.3981071710586548  # from real UI: -4.0 dB entry
    predicted = level_out_from_db(-4.0)
    assert abs(predicted - real_value) < 1e-6
    print("[PASS] Filter2 Level dB formula matches real UI calibration point (-4dB)")


def test_filter2_persistence_and_host_param():
    body = fresh_skeleton_body()
    body["VoiceFilter1"]["plainParams"] = {
        "kParamLevelOut": level_out_from_db(-4.0),
        "kParamWet": 55.0,
    }
    engine, synth = load_body(body)
    assert abs(find_param(synth, "Filter 2 Level") - level_out_from_db(-4.0)) < 1e-6
    assert abs(find_param(synth, "Filter 2 Wet") - 0.55) < 1e-4
    del engine
    print("[PASS] Filter2 Level/Wet persistence + VST3 readback")


def test_filter1_filter2_cross_isolation():
    body = fresh_skeleton_body()
    body["VoiceFilter0"]["plainParams"] = {"kParamLevelOut": level_out_from_db(-8.5), "kParamWet": 78.0}
    body["VoiceFilter1"]["plainParams"] = {"kParamLevelOut": level_out_from_db(-4.0), "kParamWet": 55.0}

    engine, synth = load_body(body)
    f1_level = find_param(synth, "Filter 1 Level")
    f1_wet = find_param(synth, "Filter 1 Wet")
    f2_level = find_param(synth, "Filter 2 Level")
    f2_wet = find_param(synth, "Filter 2 Wet")
    del engine

    assert abs(f1_level - level_out_from_db(-8.5)) < 1e-6
    assert abs(f1_wet - 0.78) < 1e-4
    assert abs(f2_level - level_out_from_db(-4.0)) < 1e-6
    assert abs(f2_wet - 0.55) < 1e-4
    print("[PASS] Filter1/Filter2 fully independent (different values coexist correctly)")


# ---------------------------------------------------------------------------
# Round-trip persistence (save -> decode -> reload -> readback), all 4 controls
# ---------------------------------------------------------------------------

def test_full_round_trip_all_four_controls():
    body = fresh_skeleton_body()
    pathmerge.apply_path_value(body, "VoiceFilter0.plainParams.kParamLevelOut", level_out_from_db(-8.5))
    pathmerge.apply_path_value(body, "VoiceFilter0.plainParams.kParamWet", 78.0)
    pathmerge.apply_path_value(body, "VoiceFilter1.plainParams.kParamLevelOut", level_out_from_db(-4.0))
    pathmerge.apply_path_value(body, "VoiceFilter1.plainParams.kParamWet", 55.0)

    engine, synth = load_body(body)

    fd, save_path = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    synth.save_state(save_path)

    raw = open(save_path, "rb").read()
    _, body_saved = codec.decode(vst3_state.unwrap_vc2(raw))

    assert abs(body_saved["VoiceFilter0"]["plainParams"]["kParamLevelOut"] - level_out_from_db(-8.5)) < 1e-6
    assert body_saved["VoiceFilter0"]["plainParams"]["kParamWet"] == 78.0
    assert abs(body_saved["VoiceFilter1"]["plainParams"]["kParamLevelOut"] - level_out_from_db(-4.0)) < 1e-6
    assert abs(body_saved["VoiceFilter1"]["plainParams"]["kParamWet"] - 55.0) < 1e-6

    engine2 = daw.RenderEngine(SR, BLOCK)
    synth2 = engine2.make_plugin_processor("serum", VST3)
    synth2.load_state(save_path)
    os.remove(save_path)

    assert abs(find_param(synth2, "Filter 1 Level") - level_out_from_db(-8.5)) < 1e-6
    assert abs(find_param(synth2, "Filter 1 Wet") - 0.78) < 1e-4
    assert abs(find_param(synth2, "Filter 2 Level") - level_out_from_db(-4.0)) < 1e-6
    assert abs(find_param(synth2, "Filter 2 Wet") - 0.55) < 1e-4

    del engine
    del engine2
    print("[PASS] Full round-trip persistence for all 4 controls (save -> decode -> reload -> readback)")


# ---------------------------------------------------------------------------
# Semantic-target route sanity: ensure targets.py / scalar_operations.py wiring
# resolves to exactly the proven paths.
# ---------------------------------------------------------------------------

def test_semantic_target_wiring():
    from serum2.compiler import targets as targets_mod
    from serum2.operations.scalar_operations import PHASE_9B_STRUCTURAL_PATHS

    expected = {
        "FILTER1.Level": "VoiceFilter0.plainParams.kParamLevelOut",
        "FILTER1.Mix": "VoiceFilter0.plainParams.kParamWet",
        "FILTER2.Level": "VoiceFilter1.plainParams.kParamLevelOut",
        "FILTER2.Mix": "VoiceFilter1.plainParams.kParamWet",
    }
    for semantic_name, expected_path in expected.items():
        ref = targets_mod.SEMANTIC_TARGETS[semantic_name]
        actual_path = PHASE_9B_STRUCTURAL_PATHS[ref.capability_key]
        assert actual_path == expected_path, \
            f"{semantic_name}: expected {expected_path}, wired to {actual_path}"
    print("[PASS] Semantic target wiring resolves to exactly the proven CBOR paths")


if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# STEP 20B PART 4: FILTER LEVEL/MIX — REGRESSION SUITE")
    print("#" * 70)

    tests = [
        test_filter1_level_db_formula,
        test_filter1_level_persistence,
        test_filter1_wet_scale_linearity,
        test_filter1_level_wet_sibling_isolation,
        test_isolation_from_other_state,
        test_filter2_level_db_formula,
        test_filter2_persistence_and_host_param,
        test_filter1_filter2_cross_isolation,
        test_full_round_trip_all_four_controls,
        test_semantic_target_wiring,
    ]

    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"[FAILED] {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {t.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "#" * 70)
    if failed == 0:
        print(f"# ALL {len(tests)} TESTS PASSED")
    else:
        print(f"# {failed}/{len(tests)} TESTS FAILED")
    print("#" * 70)

    if failed:
        exit(1)
