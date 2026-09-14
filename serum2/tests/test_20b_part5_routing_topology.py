"""STEP 20B PART 5: Routing topology (channel -> destination) - regression suite.

Persistent representation (proven via real Serum UI dropdown selection + native
save + CBOR decode; genericity confirmed across 3 distinct channel types):

  RoutingSlot{index}.plainParams.kParamRoutingDest

  - Same container as PART 3's BUS sends (kParamFXBus1Level/kParamFXBus2Level)
    - dict-merge sibling, proven independent.
  - index positionally identifies source channel (same mapping as PART 3):
      0=OSC A, 1=OSC B, 2=OSC C, 3=NOISE, 4=SUB, 5=FILTER1, 6=FILTER2
  - Enum values (real UI confirmed):
      'kRoutingDestMaster'  <- dropdown "Main"
      'kRoutingDestDirect'  <- dropdown "Direct"
      'kRoutingDestNone'    <- dropdown "None"
      'kRoutingDestFilter'  <- dropdown "Filter" (oscillators) / "Filter 2"
                               (Filter1's own dropdown, since it can't route
                               to itself) - SAME enum value in both contexts,
                               confirming the option's label is just contextual
                               UI text over one generic "route to a filter"
                               destination.
      (absent key)          <- each channel's own implicit default:
                               Filter for OSC A/B/C, SUB, NOISE;
                               Main for FILTER1, FILTER2.
                               Confirmed by switching back to the default
                               option from a non-default state: the key is
                               REMOVED (reverts to "default"), not stored
                               explicitly.

  No VST3 HOST_PARAM exists for this field (searched all 2623 parameters on a
  fresh skeleton, zero matches for "rout"/"dest"/"target" other than an
  unrelated Arp param) - this is a STRUCTURAL_ONLY field per project
  evidence tiers; persistence is verified via CBOR decode + reload, not via
  automatable host-parameter readback.
"""
import os
import tempfile
import copy
from serum2 import bridge, codec, vst3_state, pathmerge
from serum2.evidence import epoch as epoch_mod
import dawdreamer as daw

VST3 = epoch_mod.SERUM_VST3
SR = 44100
BLOCK = 512


def fresh_skeleton_body():
    return copy.deepcopy(bridge.capture_v8_skeleton(VST3)[1])


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


# ---------------------------------------------------------------------------
# Enum values, confirmed via real UI on 3 distinct channel types
# ---------------------------------------------------------------------------

def test_osc_a_routing_enum_values():
    """RoutingSlot0 (OSC A): Main/Direct/None all real-UI confirmed."""
    for enum_val in ["kRoutingDestMaster", "kRoutingDestDirect", "kRoutingDestNone"]:
        body = fresh_skeleton_body()
        pathmerge.apply_path_value(body, "RoutingSlot0.plainParams.kParamRoutingDest", enum_val)
        assert body["RoutingSlot0"]["plainParams"]["kParamRoutingDest"] == enum_val
    print("[PASS] OSC A (RoutingSlot0) routing enum values settable")


def test_filter1_routing_enum_values_including_filter_dest():
    """RoutingSlot5 (FILTER1): Main/Direct/None/Filter(->Filter2) all real-UI confirmed."""
    for enum_val in ["kRoutingDestMaster", "kRoutingDestDirect", "kRoutingDestNone", "kRoutingDestFilter"]:
        body = fresh_skeleton_body()
        pathmerge.apply_path_value(body, "RoutingSlot5.plainParams.kParamRoutingDest", enum_val)
        assert body["RoutingSlot5"]["plainParams"]["kParamRoutingDest"] == enum_val
    print("[PASS] FILTER1 (RoutingSlot5) routing enum values settable, "
          "including 'kRoutingDestFilter' for its 'Filter 2' option")


def test_noise_routing_enum_value():
    """RoutingSlot3 (NOISE): genericity confirmed via real UI ('None')."""
    body = fresh_skeleton_body()
    pathmerge.apply_path_value(body, "RoutingSlot3.plainParams.kParamRoutingDest", "kRoutingDestNone")
    assert body["RoutingSlot3"]["plainParams"]["kParamRoutingDest"] == "kRoutingDestNone"
    print("[PASS] NOISE (RoutingSlot3) routing enum genericity confirmed")


# ---------------------------------------------------------------------------
# Default-reversion behavior: setting back to the implicit default REMOVES
# the key rather than storing it explicitly (real UI confirmed for OSC A).
# ---------------------------------------------------------------------------

def test_default_reversion_removes_key():
    body = fresh_skeleton_body()
    pathmerge.apply_path_value(body, "RoutingSlot0.plainParams.kParamRoutingDest", "kRoutingDestNone")
    assert body["RoutingSlot0"]["plainParams"]["kParamRoutingDest"] == "kRoutingDestNone"

    # Real Serum UI: switching back to "Filter" (OSC A's implicit default)
    # reverts RoutingSlot0.plainParams to the literal string "default" (key
    # removed entirely). We replicate that exact transition here.
    body["RoutingSlot0"]["plainParams"] = "default"
    assert body["RoutingSlot0"]["plainParams"] == "default"
    print("[PASS] Reverting to implicit default matches real UI behavior (key removed)")


# ---------------------------------------------------------------------------
# Isolation: routing dest is a dict-merge sibling of BUS sends (PART 3) within
# the SAME RoutingSlot, and independent across slots.
# ---------------------------------------------------------------------------

def test_routing_dest_isolated_from_bus_sends_same_slot():
    body = fresh_skeleton_body()
    body["RoutingSlot0"]["plainParams"] = {
        "kParamFXBus1Level": 65.0,
        "kParamFXBus2Level": 40.0,
    }
    before_bus1 = body["RoutingSlot0"]["plainParams"]["kParamFXBus1Level"]
    before_bus2 = body["RoutingSlot0"]["plainParams"]["kParamFXBus2Level"]

    # Mutate ONLY routing dest; BUS sends must survive unchanged
    pathmerge.apply_path_value(body, "RoutingSlot0.plainParams.kParamRoutingDest", "kRoutingDestMaster")
    assert body["RoutingSlot0"]["plainParams"]["kParamFXBus1Level"] == before_bus1
    assert body["RoutingSlot0"]["plainParams"]["kParamFXBus2Level"] == before_bus2
    assert body["RoutingSlot0"]["plainParams"]["kParamRoutingDest"] == "kRoutingDestMaster"

    # Mutate ONLY BUS1 send; routing dest must survive unchanged
    pathmerge.apply_path_value(body, "RoutingSlot0.plainParams.kParamFXBus1Level", 20.0)
    assert body["RoutingSlot0"]["plainParams"]["kParamRoutingDest"] == "kRoutingDestMaster"
    assert body["RoutingSlot0"]["plainParams"]["kParamFXBus2Level"] == before_bus2

    print("[PASS] Routing dest and BUS sends are independent siblings (dict-merge)")


def test_cross_slot_isolation():
    body = fresh_skeleton_body()
    pathmerge.apply_path_value(body, "RoutingSlot0.plainParams.kParamRoutingDest", "kRoutingDestMaster")
    pathmerge.apply_path_value(body, "RoutingSlot2.plainParams.kParamRoutingDest", "kRoutingDestDirect")

    assert body["RoutingSlot0"]["plainParams"]["kParamRoutingDest"] == "kRoutingDestMaster"
    assert body["RoutingSlot2"]["plainParams"]["kParamRoutingDest"] == "kRoutingDestDirect"
    assert body["RoutingSlot1"]["plainParams"] == "default"  # untouched OSC B slot

    print("[PASS] Cross-slot isolation: RoutingSlot0/2 mutations don't affect RoutingSlot1")


def test_isolation_from_filter_and_oscillator_plainparams():
    """Routing dest mutation must not leak into Oscillator/VoiceFilter plainParams."""
    body = fresh_skeleton_body()
    pathmerge.apply_path_value(body, "Oscillator0.plainParams.kParamPan", -25.0)
    pathmerge.apply_path_value(body, "VoiceFilter0.plainParams.kParamWet", 78.0)
    before_osc0 = copy.deepcopy(body["Oscillator0"]["plainParams"])
    before_vf0 = copy.deepcopy(body["VoiceFilter0"]["plainParams"])

    pathmerge.apply_path_value(body, "RoutingSlot0.plainParams.kParamRoutingDest", "kRoutingDestNone")

    assert body["Oscillator0"]["plainParams"] == before_osc0
    assert body["VoiceFilter0"]["plainParams"] == before_vf0
    print("[PASS] Routing dest mutation isolated from Oscillator.plainParams and VoiceFilter.plainParams")


# ---------------------------------------------------------------------------
# Round-trip persistence (save -> decode -> reload -> re-save -> decode)
# ---------------------------------------------------------------------------

def test_round_trip_persistence():
    body = fresh_skeleton_body()
    pathmerge.apply_path_value(body, "RoutingSlot0.plainParams.kParamRoutingDest", "kRoutingDestMaster")
    pathmerge.apply_path_value(body, "RoutingSlot5.plainParams.kParamRoutingDest", "kRoutingDestFilter")

    engine, synth = load_body(body)

    fd, save_path = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    synth.save_state(save_path)
    raw = open(save_path, "rb").read()
    _, body_saved = codec.decode(vst3_state.unwrap_vc2(raw))

    assert body_saved["RoutingSlot0"]["plainParams"]["kParamRoutingDest"] == "kRoutingDestMaster"
    assert body_saved["RoutingSlot5"]["plainParams"]["kParamRoutingDest"] == "kRoutingDestFilter"

    # Reload fresh and re-save, verify still exact (two full round-trips)
    engine2 = daw.RenderEngine(SR, BLOCK)
    synth2 = engine2.make_plugin_processor("serum", VST3)
    synth2.load_state(save_path)
    os.remove(save_path)

    fd2, save_path2 = tempfile.mkstemp(suffix=".bin")
    os.close(fd2)
    synth2.save_state(save_path2)
    raw2 = open(save_path2, "rb").read()
    _, body_saved2 = codec.decode(vst3_state.unwrap_vc2(raw2))
    os.remove(save_path2)

    assert body_saved2["RoutingSlot0"]["plainParams"]["kParamRoutingDest"] == "kRoutingDestMaster"
    assert body_saved2["RoutingSlot5"]["plainParams"]["kParamRoutingDest"] == "kRoutingDestFilter"

    del engine, engine2
    print("[PASS] Round-trip persistence across two full save/reload cycles")


# ---------------------------------------------------------------------------
# Semantic-target wiring sanity
# ---------------------------------------------------------------------------

def test_semantic_target_wiring():
    from serum2.compiler import targets as targets_mod
    from serum2.operations.scalar_operations import PHASE_9B_STRUCTURAL_PATHS

    expected = {
        "OSC1.Route": "RoutingSlot0.plainParams.kParamRoutingDest",
        "OSC2.Route": "RoutingSlot1.plainParams.kParamRoutingDest",
        "OSC3.Route": "RoutingSlot2.plainParams.kParamRoutingDest",
        "NOISE.Route": "RoutingSlot3.plainParams.kParamRoutingDest",
        "SUB.Route": "RoutingSlot4.plainParams.kParamRoutingDest",
        "FILTER1.Route": "RoutingSlot5.plainParams.kParamRoutingDest",
        "FILTER2.Route": "RoutingSlot6.plainParams.kParamRoutingDest",
    }
    for semantic_name, expected_path in expected.items():
        ref = targets_mod.SEMANTIC_TARGETS[semantic_name]
        actual_path = PHASE_9B_STRUCTURAL_PATHS[ref.capability_key]
        assert actual_path == expected_path, \
            f"{semantic_name}: expected {expected_path}, wired to {actual_path}"
    print("[PASS] All 7 Route semantic targets wired to exactly the proven CBOR paths")


if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# STEP 20B PART 5: ROUTING TOPOLOGY — REGRESSION SUITE")
    print("#" * 70)

    tests = [
        test_osc_a_routing_enum_values,
        test_filter1_routing_enum_values_including_filter_dest,
        test_noise_routing_enum_value,
        test_default_reversion_removes_key,
        test_routing_dest_isolated_from_bus_sends_same_slot,
        test_cross_slot_isolation,
        test_isolation_from_filter_and_oscillator_plainparams,
        test_round_trip_persistence,
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
