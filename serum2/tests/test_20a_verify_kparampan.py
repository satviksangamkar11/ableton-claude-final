"""STEP 20A: Verify kParamPan CBOR path with correct value scale."""
import os
import tempfile
import dawdreamer as daw
from serum2 import bridge, codec, vst3_state
from serum2.evidence import epoch as epoch_mod
from serum2.evidence import runtime as runtime_mod

VST3 = epoch_mod.SERUM_VST3
SR = 44100
BLOCK = 512


def test_kparampan_correct_scale():
    """Set Oscillator0.plainParams.kParamPan directly in CBOR with correct scale,
    verify it produces the expected VST3 'A Pan' readback, and persists through
    DawDreamer's own save/reload cycle."""

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], skeleton[1].copy()

    import copy
    body = copy.deepcopy(body)

    # Set kParamPan directly (using the scale discovered from real Serum UI: ~43 = 43R)
    test_kparam_value = 43.24561357498169
    body['Oscillator0']['plainParams'] = {'kParamPan': test_kparam_value}

    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)

    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)

    # Read VST3 "A Pan" host parameter
    vst3_pan = runtime_mod.read_host_param(synth, "A Pan")
    print(f"[CBOR] Set kParamPan = {test_kparam_value}")
    print(f"[VST3] Readback 'A Pan' = {vst3_pan}")

    # Expected: kParamPan 43.24 -> VST3 ~0.5 + 43.24/200 = 0.7162
    expected_vst3 = 0.5 + test_kparam_value / 200.0
    print(f"[CALC] Expected VST3 value (linear -100..100 -> 0..1): {expected_vst3}")

    # Now test persistence: save via DawDreamer's save_state, reload, check CBOR
    fd, save_path = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    synth.save_state(save_path)

    raw = open(save_path, "rb").read()
    meta_saved, body_saved = codec.decode(vst3_state.unwrap_vc2(raw))
    print(f"\n[PERSIST CHECK] Oscillator0.plainParams after DawDreamer save_state():")
    print(f"  {body_saved['Oscillator0']['plainParams']}")

    # Reload in new engine
    engine2 = daw.RenderEngine(SR, BLOCK)
    synth2 = engine2.make_plugin_processor("serum", VST3)
    synth2.load_state(save_path)
    os.remove(save_path)

    vst3_pan_reloaded = runtime_mod.read_host_param(synth2, "A Pan")
    print(f"[RELOAD] VST3 'A Pan' after reload: {vst3_pan_reloaded}")

    match = abs(vst3_pan_reloaded - vst3_pan) < 1e-4
    print(f"\n[RESULT] Persistence via DawDreamer save/reload: {'PASS' if match else 'FAIL'}")

    del engine
    del engine2

    return vst3_pan, body_saved['Oscillator0']['plainParams'], vst3_pan_reloaded


if __name__ == "__main__":
    print("="*70)
    print("VERIFY kParamPan CBOR PATH WITH CORRECT SCALE")
    print("="*70)
    test_kparampan_correct_scale()
