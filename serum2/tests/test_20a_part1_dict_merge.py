"""STEP 20A PART 1: Prove plainParams dict-merge semantics."""
import os
import tempfile
import copy
import dawdreamer as daw
from serum2 import bridge, codec, vst3_state
from serum2.evidence import epoch as epoch_mod
from serum2.evidence import runtime as runtime_mod

VST3 = epoch_mod.SERUM_VST3
SR = 44100
BLOCK = 512


def load_and_read(meta, body, params_to_read):
    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)
    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)
    result = {name: runtime_mod.read_host_param(synth, name) for name in params_to_read}
    del engine
    return result


def save_and_decode(meta, body):
    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)
    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)
    fd, out = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    synth.save_state(out)
    raw = open(out, "rb").read()
    os.remove(out)
    del engine
    return codec.decode(vst3_state.unwrap_vc2(raw))


def test_1a_mutate_pan_only_preserves_volume():
    """Start with BOTH keys set, mutate only Pan, verify Volume unchanged."""
    print("\n" + "="*70)
    print("TEST 1A: Mutate ONLY kParamPan, verify kParamVolume preserved")
    print("="*70)

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], copy.deepcopy(skeleton[1])

    body["Oscillator0"]["plainParams"] = {
        "kParamPan": 20.0,
        "kParamVolume": 0.65,
    }

    readback_before = load_and_read(meta, body, ["A Pan", "A Level"])
    print(f"Before mutation: {readback_before}")

    # Now mutate ONLY kParamPan via dict merge (read-modify-write pattern)
    body2 = copy.deepcopy(body)
    body2["Oscillator0"]["plainParams"] = dict(body2["Oscillator0"]["plainParams"])
    body2["Oscillator0"]["plainParams"]["kParamPan"] = -30.0

    readback_after = load_and_read(meta, body2, ["A Pan", "A Level"])
    print(f"After Pan-only mutation: {readback_after}")
    print(f"Full plainParams after: {body2['Oscillator0']['plainParams']}")

    assert body2["Oscillator0"]["plainParams"]["kParamVolume"] == 0.65, \
        "kParamVolume was NOT preserved during Pan-only mutation!"
    assert body2["Oscillator0"]["plainParams"]["kParamPan"] == -30.0

    pan_changed = abs(readback_after["A Pan"] - readback_before["A Pan"]) > 1e-4
    level_unchanged = abs(readback_after["A Level"] - readback_before["A Level"]) < 1e-4

    print(f"Pan changed: {pan_changed}")
    print(f"Level unchanged (isolated): {level_unchanged}")
    assert pan_changed, "Pan did not actually change in VST3 readback"
    assert level_unchanged, "Level was NOT isolated -- changed when only Pan was mutated!"
    print("[PASS] Pan-only mutation preserves Volume")
    return True


def test_1b_mutate_volume_only_preserves_pan():
    """Start with BOTH keys set, mutate only Volume, verify Pan unchanged."""
    print("\n" + "="*70)
    print("TEST 1B: Mutate ONLY kParamVolume, verify kParamPan preserved")
    print("="*70)

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], copy.deepcopy(skeleton[1])

    body["Oscillator0"]["plainParams"] = {
        "kParamPan": 15.0,
        "kParamVolume": 0.5,
    }

    readback_before = load_and_read(meta, body, ["A Pan", "A Level"])
    print(f"Before mutation: {readback_before}")

    body2 = copy.deepcopy(body)
    body2["Oscillator0"]["plainParams"] = dict(body2["Oscillator0"]["plainParams"])
    body2["Oscillator0"]["plainParams"]["kParamVolume"] = 0.9

    readback_after = load_and_read(meta, body2, ["A Pan", "A Level"])
    print(f"After Volume-only mutation: {readback_after}")
    print(f"Full plainParams after: {body2['Oscillator0']['plainParams']}")

    assert body2["Oscillator0"]["plainParams"]["kParamPan"] == 15.0, \
        "kParamPan was NOT preserved during Volume-only mutation!"

    level_changed = abs(readback_after["A Level"] - readback_before["A Level"]) > 1e-4
    pan_unchanged = abs(readback_after["A Pan"] - readback_before["A Pan"]) < 1e-4

    print(f"Level changed: {level_changed}")
    print(f"Pan unchanged (isolated): {pan_unchanged}")
    assert level_changed, "Level did not actually change in VST3 readback"
    assert pan_unchanged, "Pan was NOT isolated -- changed when only Volume was mutated!"
    print("[PASS] Volume-only mutation preserves Pan")
    return True


def test_1c_default_to_dict_transition():
    """plainParams='default' -> set first non-default key -> dict with ONLY that key."""
    print("\n" + "="*70)
    print("TEST 1C: 'default' string -> dict transition (first key)")
    print("="*70)

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], copy.deepcopy(skeleton[1])

    baseline_pp = body["Oscillator0"]["plainParams"]
    print(f"Baseline plainParams: {baseline_pp!r} (type: {type(baseline_pp).__name__})")
    assert baseline_pp == "default"

    body2 = copy.deepcopy(body)
    body2["Oscillator0"]["plainParams"] = {"kParamPan": 25.0}

    readback = load_and_read(meta, body2, ["A Pan", "A Level"])
    print(f"After setting first key (Pan=25.0): {readback}")

    # Save and re-decode to see what Serum itself considers valid/normalizes to
    meta_s, body_s = save_and_decode(meta, body2)
    print(f"Serum-saved plainParams: {body_s['Oscillator0']['plainParams']}")

    pan_took_effect = abs(readback["A Pan"] - 0.5) > 0.01
    print(f"Pan took effect (non-default): {pan_took_effect}")
    assert pan_took_effect, "Single-key dict did not take effect"
    print("[PASS] 'default' -> single-key dict transition works")
    return True


def test_1d_dict_to_default_transition():
    """dict with one key -> restore to default -> what representation does Serum use?"""
    print("\n" + "="*70)
    print("TEST 1D: dict -> restore-to-default transition")
    print("="*70)

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], copy.deepcopy(skeleton[1])

    # Start with a non-default Pan
    body["Oscillator0"]["plainParams"] = {"kParamPan": 25.0}

    # Try Option A: empty dict
    body_a = copy.deepcopy(body)
    body_a["Oscillator0"]["plainParams"] = {}
    try:
        readback_a = load_and_read(meta, body_a, ["A Pan"])
        print(f"[Option A: empty dict {{}}] Load succeeded. A Pan = {readback_a['A Pan']}")
        option_a_ok = abs(readback_a["A Pan"] - 0.5) < 0.01
        print(f"  Reads as default (0.5)? {option_a_ok}")
    except Exception as e:
        print(f"[Option A: empty dict {{}}] Load FAILED: {e}")
        option_a_ok = False

    # Try Option B: "default" string
    body_b = copy.deepcopy(body)
    body_b["Oscillator0"]["plainParams"] = "default"
    try:
        readback_b = load_and_read(meta, body_b, ["A Pan"])
        print(f"[Option B: 'default' string] Load succeeded. A Pan = {readback_b['A Pan']}")
        option_b_ok = abs(readback_b["A Pan"] - 0.5) < 0.01
        print(f"  Reads as default (0.5)? {option_b_ok}")
    except Exception as e:
        print(f"[Option B: 'default' string] Load FAILED: {e}")
        option_b_ok = False

    # Try Option C: explicit default value (kParamPan: 0.0)
    body_c = copy.deepcopy(body)
    body_c["Oscillator0"]["plainParams"] = {"kParamPan": 0.0}
    try:
        readback_c = load_and_read(meta, body_c, ["A Pan"])
        print(f"[Option C: explicit kParamPan=0.0] Load succeeded. A Pan = {readback_c['A Pan']}")
        option_c_ok = abs(readback_c["A Pan"] - 0.5) < 0.01
        print(f"  Reads as default (0.5)? {option_c_ok}")
    except Exception as e:
        print(f"[Option C: explicit kParamPan=0.0] Load FAILED: {e}")
        option_c_ok = False

    print(f"\nSummary: Option A (empty dict)={option_a_ok}, Option B ('default')={option_b_ok}, Option C (explicit 0.0)={option_c_ok}")
    return option_a_ok, option_b_ok, option_c_ok


if __name__ == "__main__":
    print("\n" + "#"*70)
    print("# STEP 20A PART 1: DICT-MERGE SEMANTICS")
    print("#"*70)

    results = {}
    try:
        results['1a'] = test_1a_mutate_pan_only_preserves_volume()
        results['1b'] = test_1b_mutate_volume_only_preserves_pan()
        results['1c'] = test_1c_default_to_dict_transition()
        results['1d'] = test_1d_dict_to_default_transition()

        print("\n" + "#"*70)
        print("# ALL PART 1 TESTS COMPLETE")
        print("#"*70)
        for k, v in results.items():
            print(f"  {k}: {v}")

    except AssertionError as e:
        print(f"\n[FAILED] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
