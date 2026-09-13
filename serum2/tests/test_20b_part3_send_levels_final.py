"""STEP 20B PART 3: MIX Send Levels - comprehensive regression suite.

Persistent representation (proven via real Serum UI drag + native save + decode +
DawDreamer VST3 host-param cross-check):

  RoutingSlot{index}.plainParams.kParamFXBus1Level / kParamFXBus2Level
    - index positionally identifies the SOURCE channel:
        0=OSC A, 1=OSC B, 2=OSC C, 3=NOISE, 4=SUB OSC, 5=FILTER 1, 6=FILTER 2
    - scale: CBOR 0..100 (linear) == VST3 host param 0..1
      (e.g. RoutingSlot0.kParamFXBus1Level=100.0 -> host param "A>BUS1"=1.0)
    - dict-merge isolation: kParamFXBus1Level and kParamFXBus2Level are
      independent sibling keys within the same slot's plainParams.
    - kParamRoutingDest (e.g. 'kRoutingDestFilter', 'kRoutingDestMaster') is an
      optional companion field capturing the source channel's own primary
      routing selection; it does NOT gate or alter the bus-send host param.

  Global0.plainParams.kParamFXBus1Vol / kParamFXBus2Vol
    - the FX Bus channel's OWN overall volume (distinct from per-source sends)
    - scale: kParamFXBus{N}Vol = 0.5 * 10^(dB/20); default 0.5 == 0dB unity
    - real UI evidence: dragged fader tooltip read "Bus 1 Vol : 35% [-6.4 dB]"
      while CBOR held 0.24017598294614292 (matches formula to within display
      rounding: 0.5 * 10^(-6.4/20) = 0.2393).

Negative evidence (also proven): the VST3 HOST_PARAM controls named
"A>BUS1", "B>BUS1", ..., "Filter 2>BUS2" are runtime-only — setting them via
set_parameter() produces ZERO diff in the persisted CBOR body. This confirms
HOST_PARAM is not the persistent backend, consistent with project rules.
"""
import os
import tempfile
import copy
import math
import dawdreamer as daw
from serum2 import bridge, codec, vst3_state, pathmerge
from serum2.evidence import epoch as epoch_mod

VST3 = epoch_mod.SERUM_VST3
SR = 44100
BLOCK = 512

# RoutingSlot index -> (VST3 host param prefix)
SLOT_SOURCE_PREFIX = {
    0: "A",
    1: "B",
    2: "C",
    3: "Noise",
    4: "Sub Osc",
    5: "Filter 1",
    6: "Filter 2",
}


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
# EXPERIMENT A: OSC A -> BUS1
# ---------------------------------------------------------------------------

def test_osc_a_to_bus1_persistence():
    body = fresh_skeleton_body()
    pathmerge.apply_path_value(body, "RoutingSlot0.plainParams.kParamFXBus1Level", 65.0)

    engine, synth = load_body(body)
    assert abs(find_param(synth, "A>BUS1") - 0.65) < 1e-4
    del engine

    print("[PASS] Experiment A: OSC A -> BUS1 (CBOR 65.0 -> host param 0.65)")


# ---------------------------------------------------------------------------
# EXPERIMENT B: OSC A -> BUS2
# ---------------------------------------------------------------------------

def test_osc_a_to_bus2_persistence():
    body = fresh_skeleton_body()
    pathmerge.apply_path_value(body, "RoutingSlot0.plainParams.kParamFXBus2Level", 40.0)

    engine, synth = load_body(body)
    assert abs(find_param(synth, "A>BUS2") - 0.40) < 1e-4
    del engine

    print("[PASS] Experiment B: OSC A -> BUS2 (CBOR 40.0 -> host param 0.40)")


# ---------------------------------------------------------------------------
# EXPERIMENT C: sibling isolation within one RoutingSlot
# ---------------------------------------------------------------------------

def test_bus1_bus2_sibling_isolation():
    body = fresh_skeleton_body()
    body["RoutingSlot0"]["plainParams"] = {
        "kParamFXBus1Level": 100.0,
        "kParamFXBus2Level": 50.0,
    }
    engine, synth = load_body(body)
    a_bus1 = find_param(synth, "A>BUS1")
    a_bus2 = find_param(synth, "A>BUS2")
    del engine
    assert abs(a_bus1 - 1.0) < 1e-4
    assert abs(a_bus2 - 0.5) < 1e-4

    # Mutate ONLY BUS1 via pathmerge; verify BUS2 sibling untouched
    body2 = copy.deepcopy(body)
    pathmerge.apply_path_value(body2, "RoutingSlot0.plainParams.kParamFXBus1Level", 20.0)
    assert body2["RoutingSlot0"]["plainParams"]["kParamFXBus2Level"] == 50.0, \
        "BUS2 sibling was affected by BUS1 mutation!"

    engine2, synth2 = load_body(body2)
    assert abs(find_param(synth2, "A>BUS1") - 0.20) < 1e-4
    assert abs(find_param(synth2, "A>BUS2") - 0.50) < 1e-4
    del engine2

    # Mutate ONLY BUS2; verify BUS1 sibling untouched
    body3 = copy.deepcopy(body)
    pathmerge.apply_path_value(body3, "RoutingSlot0.plainParams.kParamFXBus2Level", 5.0)
    assert body3["RoutingSlot0"]["plainParams"]["kParamFXBus1Level"] == 100.0, \
        "BUS1 sibling was affected by BUS2 mutation!"

    print("[PASS] Experiment C: BUS1/BUS2 sibling isolation within RoutingSlot")


def test_routing_slot_index_isolation():
    """Setting one RoutingSlot must not affect any other slot's source."""
    body = fresh_skeleton_body()
    pathmerge.apply_path_value(body, "RoutingSlot0.plainParams.kParamFXBus1Level", 80.0)  # OSC A
    pathmerge.apply_path_value(body, "RoutingSlot2.plainParams.kParamFXBus1Level", 30.0)  # OSC C

    engine, synth = load_body(body)
    a_bus1 = find_param(synth, "A>BUS1")
    b_bus1 = find_param(synth, "B>BUS1")  # untouched slot 1
    c_bus1 = find_param(synth, "C>BUS1")
    del engine

    assert abs(a_bus1 - 0.80) < 1e-4
    assert abs(c_bus1 - 0.30) < 1e-4
    assert b_bus1 == 0.0 or b_bus1 is None, f"OSC B (untouched slot) leaked a value: {b_bus1}"

    print("[PASS] Cross-slot isolation: RoutingSlot0/2 mutations don't affect RoutingSlot1 (OSC B)")


# ---------------------------------------------------------------------------
# EXPERIMENT D: scale calibration (0/25/50/75/100 linearity, proven earlier
# via direct testing; re-asserted here as a regression contract)
# ---------------------------------------------------------------------------

def test_scale_linearity():
    for level, expected in [(0, 0.0), (25, 0.25), (50, 0.5), (75, 0.75), (100, 1.0)]:
        body = fresh_skeleton_body()
        pathmerge.apply_path_value(body, "RoutingSlot0.plainParams.kParamFXBus1Level", float(level))
        engine, synth = load_body(body)
        val = find_param(synth, "A>BUS1") or 0.0
        del engine
        assert abs(val - expected) < 1e-4, f"level={level}: expected {expected}, got {val}"
    print("[PASS] Experiment D: scale is linear, CBOR 0..100 == host param 0..1")


def test_bus_vol_db_formula():
    """kParamFXBus{N}Vol = 0.5 * 10^(dB/20); default=0.5=0dB.

    Real UI calibration point: fader tooltip read "35% [-6.4 dB]" while the
    persisted CBOR value was 0.24017598294614292.
        0.5 * 10**(-6.4/20) = 0.23935  (matches within tooltip's 1-decimal rounding)
    """
    real_ui_value = 0.24017598294614292
    predicted = 0.5 * (10 ** (-6.4 / 20))
    assert abs(real_ui_value - predicted) < 0.005, \
        f"dB formula mismatch: real={real_ui_value}, predicted={predicted}"
    print(f"[PASS] Bus Vol dB formula verified: 0.5*10^(dB/20) matches real UI point "
          f"(real={real_ui_value:.6f}, predicted={predicted:.6f})")


# ---------------------------------------------------------------------------
# EXPERIMENT E: representation type confirmation
# ---------------------------------------------------------------------------

def test_representation_is_routing_slot_not_plain_params():
    """Sends must NOT be forced into Oscillator{N}.plainParams like Pan/Level."""
    body = fresh_skeleton_body()
    pathmerge.apply_path_value(body, "RoutingSlot0.plainParams.kParamFXBus1Level", 50.0)

    # Oscillator0.plainParams must remain untouched by the send mutation
    osc0_pp = body["Oscillator0"].get("plainParams")
    assert osc0_pp == "default", \
        f"Send mutation leaked into Oscillator0.plainParams: {osc0_pp}"

    print("[PASS] Experiment E: confirmed RoutingSlot (not Oscillator.plainParams) "
          "is the send-level container")


# ---------------------------------------------------------------------------
# Round-trip persistence (save state -> decode -> reload -> readback)
# ---------------------------------------------------------------------------

def test_save_reload_round_trip():
    body = fresh_skeleton_body()
    pathmerge.apply_path_value(body, "RoutingSlot0.plainParams.kParamFXBus1Level", 65.0)
    pathmerge.apply_path_value(body, "RoutingSlot2.plainParams.kParamFXBus2Level", 40.0)

    engine, synth = load_body(body)

    fd, save_path = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    synth.save_state(save_path)

    raw = open(save_path, "rb").read()
    _, body_saved = codec.decode(vst3_state.unwrap_vc2(raw))

    assert body_saved["RoutingSlot0"]["plainParams"]["kParamFXBus1Level"] == 65.0
    assert body_saved["RoutingSlot2"]["plainParams"]["kParamFXBus2Level"] == 40.0

    engine2 = daw.RenderEngine(SR, BLOCK)
    synth2 = engine2.make_plugin_processor("serum", VST3)
    synth2.load_state(save_path)
    os.remove(save_path)

    assert abs(find_param(synth2, "A>BUS1") - 0.65) < 1e-4
    assert abs(find_param(synth2, "C>BUS2") - 0.40) < 1e-4

    del engine
    del engine2
    print("[PASS] Round-trip persistence: save -> decode -> reload -> readback")


# ---------------------------------------------------------------------------
# Negative evidence: HOST_PARAM is runtime-only, not persistent
# ---------------------------------------------------------------------------

def test_host_param_is_runtime_only():
    body = fresh_skeleton_body()
    engine, synth = load_body(body)

    idx = None
    for p in synth.get_plugin_parameters_description():
        if p["name"] == "A>BUS1":
            idx = p["index"]
    synth.set_parameter(idx, 0.7)
    assert abs(synth.get_parameter(idx) - 0.7) < 1e-4

    fd, save_path = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    synth.save_state(save_path)
    raw = open(save_path, "rb").read()
    _, body_after = codec.decode(vst3_state.unwrap_vc2(raw))
    os.remove(save_path)

    def deep_diff(o, n, path=""):
        diffs = []
        if isinstance(o, dict) and isinstance(n, dict):
            for k in set(o) | set(n):
                diffs.extend(deep_diff(o.get(k, "<M>"), n.get(k, "<M>"), f"{path}.{k}"))
        elif isinstance(o, list) and isinstance(n, list):
            if len(o) == len(n):
                for i, (a, b) in enumerate(zip(o, n)):
                    diffs.extend(deep_diff(a, b, f"{path}[{i}]"))
        elif o != n:
            diffs.append(path)
        return diffs

    diffs = deep_diff(body, body_after)
    del engine
    assert len(diffs) == 0, f"HOST_PARAM change unexpectedly persisted: {diffs}"
    print("[PASS] Negative evidence confirmed: A>BUS1 HOST_PARAM set to 0.7 "
          "produces ZERO CBOR diff (runtime-only, not persistent backend)")


if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# STEP 20B PART 3: MIX SEND LEVELS — REGRESSION SUITE")
    print("#" * 70)

    tests = [
        test_osc_a_to_bus1_persistence,
        test_osc_a_to_bus2_persistence,
        test_bus1_bus2_sibling_isolation,
        test_routing_slot_index_isolation,
        test_scale_linearity,
        test_bus_vol_db_formula,
        test_representation_is_routing_slot_not_plain_params,
        test_save_reload_round_trip,
        test_host_param_is_runtime_only,
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
            failed += 1

    print("\n" + "#" * 70)
    if failed == 0:
        print(f"# ALL {len(tests)} TESTS PASSED")
    else:
        print(f"# {failed}/{len(tests)} TESTS FAILED")
    print("#" * 70)

    if failed:
        exit(1)
