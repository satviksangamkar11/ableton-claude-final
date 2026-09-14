"""STEP 20B: Parametric OSC2/3 Pan/Level round-trip tests."""
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
    return (semantic_pan - 0.5) * 100.0


def semantic_level_to_cbor(semantic_level):
    return semantic_level ** 2


def cbor_to_vst3_pan(cbor_pan):
    return 0.5 + cbor_pan / 100.0


def cbor_to_vst3_level(cbor_level):
    return math.sqrt(cbor_level)


def test_osc2_parametric(test_name, osc2_index, osc2_pan_semantic, osc2_level_semantic):
    """Test OSC2 with parametric path."""
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], copy.deepcopy(skeleton[1])

    osc2_pan_cbor = semantic_pan_to_cbor(osc2_pan_semantic)
    osc2_level_cbor = semantic_level_to_cbor(osc2_level_semantic)

    osc2_pan_vst3_expected = cbor_to_vst3_pan(osc2_pan_cbor)
    osc2_level_vst3_expected = cbor_to_vst3_level(osc2_level_cbor)

    # Apply mutations
    pathmerge.apply_path_value(body, f"Oscillator{osc2_index}.plainParams.kParamPan", osc2_pan_cbor)
    pathmerge.apply_path_value(body, f"Oscillator{osc2_index}.plainParams.kParamVolume", osc2_level_cbor)

    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)

    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)

    vst3_pan_initial = runtime_mod.read_host_param(synth, f"B Pan" if osc2_index == 1 else "C Pan")
    vst3_level_initial = runtime_mod.read_host_param(synth, f"B Level" if osc2_index == 1 else "C Level")

    print(f"\n{test_name}")
    print(f"  Pan: {osc2_pan_semantic:.2f} → {osc2_pan_cbor:.1f} → {vst3_pan_initial:.4f} (expected {osc2_pan_vst3_expected:.4f})")
    print(f"  Level: {osc2_level_semantic:.2f} → {osc2_level_cbor:.4f} → {vst3_level_initial:.4f} (expected {osc2_level_vst3_expected:.4f})")

    assert abs(vst3_pan_initial - osc2_pan_vst3_expected) < 1e-4
    assert abs(vst3_level_initial - osc2_level_vst3_expected) < 1e-4

    # Test persistence
    fd, save_path = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    synth.save_state(save_path)

    raw = open(save_path, "rb").read()
    meta_saved, body_saved = codec.decode(vst3_state.unwrap_vc2(raw))

    persisted_pan = body_saved[f"Oscillator{osc2_index}"]["plainParams"].get("kParamPan")
    persisted_level = body_saved[f"Oscillator{osc2_index}"]["plainParams"].get("kParamVolume")

    assert abs(persisted_pan - osc2_pan_cbor) < 1e-6, f"Pan not persisted: {persisted_pan} vs {osc2_pan_cbor}"
    assert abs(persisted_level - osc2_level_cbor) < 1e-6, f"Level not persisted: {persisted_level} vs {osc2_level_cbor}"

    # Reload
    engine2 = daw.RenderEngine(SR, BLOCK)
    synth2 = engine2.make_plugin_processor("serum", VST3)
    synth2.load_state(save_path)
    os.remove(save_path)

    vst3_pan_reloaded = runtime_mod.read_host_param(synth2, f"B Pan" if osc2_index == 1 else "C Pan")
    vst3_level_reloaded = runtime_mod.read_host_param(synth2, f"B Level" if osc2_index == 1 else "C Level")

    assert abs(vst3_pan_reloaded - osc2_pan_vst3_expected) < 1e-4
    assert abs(vst3_level_reloaded - osc2_level_vst3_expected) < 1e-4

    print(f"  ✓ Persisted and reloaded correctly")

    del engine
    del engine2


if __name__ == "__main__":
    print("\n" + "="*70)
    print("STEP 20B: PARAMETRIC OSC2/3 PAN/LEVEL ROUND-TRIP TESTS")
    print("="*70)

    try:
        # OSC2 (Oscillator1) tests
        test_osc2_parametric("OSC2: Pan 75% right, Level 60%", 1, 0.75, 0.6)
        test_osc2_parametric("OSC2: Pan 25% left, Level 85%", 1, 0.25, 0.85)

        # OSC3 (Oscillator2) tests
        test_osc2_parametric("OSC3: Pan 40% right, Level 70%", 2, 0.4, 0.7)
        test_osc2_parametric("OSC3: Pan 60% left, Level 50%", 2, 0.0, 0.5)

        print("\n" + "="*70)
        print("✓ ALL PARAMETRIC TESTS PASSED")
        print("="*70)

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
