"""STEP 20A PART 3 & 4: Persistent OSC1.Pan and Level implementation + round-trip tests."""
import os
import tempfile
import copy
import math
import dawdreamer as daw
from serum2 import bridge, codec, vst3_state, pathmerge
from serum2.evidence import epoch as epoch_mod
from serum2.evidence import runtime as runtime_mod

VST3 = epoch_mod.SERUM_VST3
SR = 44100
BLOCK = 512


def semantic_pan_to_cbor(semantic_pan):
    """Convert semantic Pan (0..1, where 0.5=center) to CBOR kParamPan (-50..+50).

    Semantic 0.0 = -50 (fully left)
    Semantic 0.5 = 0 (center)
    Semantic 1.0 = +50 (fully right)
    """
    return (semantic_pan - 0.5) * 100.0


def semantic_level_to_cbor(semantic_level):
    """Convert semantic Level (0..1, linear) to CBOR kParamVolume.

    CBOR uses a square function for natural loudness feel.
    Semantic is linear 0..1, CBOR is 0..1 but squared.
    """
    return semantic_level ** 2


def cbor_to_vst3_pan(cbor_pan):
    """Convert CBOR kParamPan to VST3 A Pan readback.

    VST3 = 0.5 + kParamPan / 100
    """
    return 0.5 + cbor_pan / 100.0


def cbor_to_vst3_level(cbor_level):
    """Convert CBOR kParamVolume to VST3 A Level readback.

    VST3 = sqrt(kParamVolume)
    """
    return math.sqrt(cbor_level)


def test_pan_persistent_mutation():
    """Semantic Pan → CBOR → save → reload → verify VST3 readback."""
    print("\n" + "="*70)
    print("TEST 3A: OSC1.Pan Persistent Mutation (semantic 0.25 = left)")
    print("="*70)

    semantic_pan = 0.25  # 25% from center, toward left
    cbor_pan = semantic_pan_to_cbor(semantic_pan)
    expected_vst3_pan = cbor_to_vst3_pan(cbor_pan)

    print(f"Semantic Pan: {semantic_pan} (25% left of center)")
    print(f"CBOR kParamPan: {cbor_pan} (should be -25)")
    print(f"Expected VST3 A Pan: {expected_vst3_pan} (should be 0.25)")

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], copy.deepcopy(skeleton[1])

    # Apply mutation via pathmerge
    pathmerge.apply_path_value(body, "Oscillator0.plainParams.kParamPan", cbor_pan)

    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)

    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)

    vst3_pan_initial = runtime_mod.read_host_param(synth, "A Pan")
    print(f"\nInitial VST3 A Pan readback: {vst3_pan_initial:.10f}")
    assert abs(vst3_pan_initial - expected_vst3_pan) < 1e-4, \
        f"Pan mutation failed: expected {expected_vst3_pan}, got {vst3_pan_initial}"
    print("✓ Pan mutation applied correctly")

    # Save via DawDreamer and reload
    fd, save_path = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    synth.save_state(save_path)

    raw = open(save_path, "rb").read()
    meta_saved, body_saved = codec.decode(vst3_state.unwrap_vc2(raw))

    print(f"\nAfter save: Oscillator0.plainParams = {body_saved['Oscillator0']['plainParams']}")
    assert body_saved['Oscillator0']['plainParams'].get('kParamPan') == cbor_pan, \
        "Pan value NOT persisted in CBOR!"
    print("✓ Pan value persisted in CBOR")

    # Reload in new engine
    engine2 = daw.RenderEngine(SR, BLOCK)
    synth2 = engine2.make_plugin_processor("serum", VST3)
    synth2.load_state(save_path)
    os.remove(save_path)

    vst3_pan_reloaded = runtime_mod.read_host_param(synth2, "A Pan")
    print(f"\nAfter reload: VST3 A Pan = {vst3_pan_reloaded:.10f}")
    assert abs(vst3_pan_reloaded - expected_vst3_pan) < 1e-4, \
        f"Pan did NOT persist: expected {expected_vst3_pan}, got {vst3_pan_reloaded}"
    print("✓ Pan value persisted through save/reload cycle")

    del engine
    del engine2
    print("\n[PASS] OSC1.Pan persistent mutation")


def test_level_persistent_mutation():
    """Semantic Level → CBOR (squared) → save → reload → verify VST3 readback."""
    print("\n" + "="*70)
    print("TEST 3B: OSC1.Level Persistent Mutation (semantic 0.8 = 80% volume)")
    print("="*70)

    semantic_level = 0.8  # 80% volume
    cbor_level = semantic_level_to_cbor(semantic_level)
    expected_vst3_level = cbor_to_vst3_level(cbor_level)

    print(f"Semantic Level: {semantic_level} (80% volume, linear)")
    print(f"CBOR kParamVolume: {cbor_level} (should be 0.64 = 0.8^2)")
    print(f"Expected VST3 A Level: {expected_vst3_level} (should be ~0.8)")

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], copy.deepcopy(skeleton[1])

    # Apply mutation via pathmerge
    pathmerge.apply_path_value(body, "Oscillator0.plainParams.kParamVolume", cbor_level)

    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)

    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)

    vst3_level_initial = runtime_mod.read_host_param(synth, "A Level")
    print(f"\nInitial VST3 A Level readback: {vst3_level_initial:.10f}")
    assert abs(vst3_level_initial - expected_vst3_level) < 1e-4, \
        f"Level mutation failed: expected {expected_vst3_level}, got {vst3_level_initial}"
    print("✓ Level mutation applied correctly")

    # Save via DawDreamer and reload
    fd, save_path = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    synth.save_state(save_path)

    raw = open(save_path, "rb").read()
    meta_saved, body_saved = codec.decode(vst3_state.unwrap_vc2(raw))

    print(f"\nAfter save: Oscillator0.plainParams = {body_saved['Oscillator0']['plainParams']}")
    assert abs(body_saved['Oscillator0']['plainParams'].get('kParamVolume') - cbor_level) < 1e-6, \
        "Level value NOT persisted in CBOR!"
    print("✓ Level value persisted in CBOR")

    # Reload in new engine
    engine2 = daw.RenderEngine(SR, BLOCK)
    synth2 = engine2.make_plugin_processor("serum", VST3)
    synth2.load_state(save_path)
    os.remove(save_path)

    vst3_level_reloaded = runtime_mod.read_host_param(synth2, "A Level")
    print(f"\nAfter reload: VST3 A Level = {vst3_level_reloaded:.10f}")
    assert abs(vst3_level_reloaded - expected_vst3_level) < 1e-4, \
        f"Level did NOT persist: expected {expected_vst3_level}, got {vst3_level_reloaded}"
    print("✓ Level value persisted through save/reload cycle")

    del engine
    del engine2
    print("\n[PASS] OSC1.Level persistent mutation")


def test_isolation_pan_does_not_affect_level():
    """Changing Pan should NOT affect Level."""
    print("\n" + "="*70)
    print("TEST 4A: Isolation - Pan mutation does not affect Level")
    print("="*70)

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], copy.deepcopy(skeleton[1])

    # Set both to non-default values
    cbor_pan = semantic_pan_to_cbor(0.75)  # 75% right
    cbor_level = semantic_level_to_cbor(0.6)  # 60% volume

    body["Oscillator0"]["plainParams"] = {
        "kParamPan": cbor_pan,
        "kParamVolume": cbor_level,
    }

    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)

    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)

    pan_before = runtime_mod.read_host_param(synth, "A Pan")
    level_before = runtime_mod.read_host_param(synth, "A Level")

    print(f"Before Pan mutation: Pan={pan_before:.4f}, Level={level_before:.4f}")

    # Mutate ONLY Pan
    new_pan = semantic_pan_to_cbor(0.25)  # 25% left
    pathmerge.apply_path_value(body, "Oscillator0.plainParams.kParamPan", new_pan)

    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)

    engine2 = daw.RenderEngine(SR, BLOCK)
    synth2 = engine2.make_plugin_processor("serum", VST3)
    synth2.load_state(tmp)
    os.remove(tmp)

    pan_after = runtime_mod.read_host_param(synth2, "A Pan")
    level_after = runtime_mod.read_host_param(synth2, "A Level")

    print(f"After Pan mutation: Pan={pan_after:.4f}, Level={level_after:.4f}")

    pan_changed = abs(pan_after - pan_before) > 1e-4
    level_unchanged = abs(level_after - level_before) < 1e-4

    print(f"Pan changed: {pan_changed} (should be True)")
    print(f"Level unchanged: {level_unchanged} (should be True)")

    assert pan_changed, "Pan did not change!"
    assert level_unchanged, "Level was affected by Pan mutation!"
    print("\n[PASS] Isolation: Pan and Level are independent")

    del engine
    del engine2


if __name__ == "__main__":
    print("\n" + "#"*70)
    print("# STEP 20A PART 3 & 4: ROUNDTRIP PERSISTENCE TESTS")
    print("#"*70)

    try:
        test_pan_persistent_mutation()
        test_level_persistent_mutation()
        test_isolation_pan_does_not_affect_level()

        print("\n" + "#"*70)
        print("# ALL PART 3 & 4 TESTS PASSED")
        print("#"*70)

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
