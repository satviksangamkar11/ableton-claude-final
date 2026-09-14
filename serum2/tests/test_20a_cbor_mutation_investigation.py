"""STEP 20A: Investigate plainParams format and CBOR mutation strategy."""

import os
import tempfile
import json
import copy
import dawdreamer as daw
from serum2 import bridge, codec, vst3_state, pathmerge
from serum2.evidence import epoch as epoch_mod
from serum2.evidence import runtime as runtime_mod

VST3 = epoch_mod.SERUM_VST3
SR = 44100
BLOCK = 512


def test_plainparams_mutation():
    """Try different ways to mutate oscillator parameters via CBOR."""
    print("\n" + "="*70)
    print("EXPERIMENT: CBOR plainParams mutation strategies")
    print("="*70)

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], skeleton[1].copy()

    print(f"\nBaseline Oscillator0.plainParams: {body['Oscillator0']['plainParams']}")
    print(f"Baseline VoicePanel0.plainParams: {body['VoicePanel0']['plainParams']}")

    # Strategy A: Try mutating plainParams to a dict with kParamPan
    print(f"\n[Strategy A] Convert plainParams to dict with kParamPan field")
    body_a = copy.deepcopy(body)
    body_a['Oscillator0']['plainParams'] = {'kParamPan': 0.75}

    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body_a)

    try:
        engine = daw.RenderEngine(SR, BLOCK)
        synth = engine.make_plugin_processor("serum", VST3)
        synth.load_state(tmp)
        pan_a = runtime_mod.read_host_param(synth, "A Pan")
        print(f"  Load succeeded. A Pan readback: {pan_a}")
        del engine
    except Exception as e:
        print(f"  Load failed: {e}")
    os.remove(tmp)

    # Strategy B: Try mutating VoicePanel0
    print(f"\n[Strategy B] Convert VoicePanel0.plainParams to dict with pan field")
    body_b = copy.deepcopy(body)
    body_b['VoicePanel0']['plainParams'] = {'kParamEnableOsc1': 1.0, 'kParamPanOsc1': 0.75}

    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body_b)

    try:
        engine = daw.RenderEngine(SR, BLOCK)
        synth = engine.make_plugin_processor("serum", VST3)
        synth.load_state(tmp)
        pan_b = runtime_mod.read_host_param(synth, "A Pan")
        print(f"  Load succeeded. A Pan readback: {pan_b}")
        del engine
    except Exception as e:
        print(f"  Load failed: {e}")
    os.remove(tmp)

    # Strategy C: Look for how existing non-default params are stored
    print(f"\n[Strategy C] Examine what existing non-default parameters look like")
    # Check if any oscill ator currently has non-default params
    for i in range(5):
        osc_key = f"Oscillator{i}"
        if osc_key in body:
            pp = body[osc_key].get('plainParams')
            print(f"  {osc_key}.plainParams = {pp} (type: {type(pp).__name__})")


def test_host_param_to_cbor_sync():
    """Test whether Serum syncs HOST_PARAM changes into CBOR on save."""
    print("\n" + "="*70)
    print("EXPERIMENT: HOST_PARAM to CBOR synchronization")
    print("="*70)

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], skeleton[1].copy()

    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)

    # Load and mutate via HOST_PARAM
    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)

    params = synth.get_parameters_description()
    by_name = {p["name"]: p["index"] for p in params}
    synth.set_parameter(by_name["A Pan"], 0.75)

    print(f"\n[A] Set A Pan via HOST_PARAM to 0.75")
    readback = runtime_mod.read_host_param(synth, "A Pan")
    print(f"    Readback: {readback}")

    # Save immediately after HOST_PARAM write (while engine still loaded)
    fd, path_save1 = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    synth.save_state(path_save1)
    print(f"    Saved (engine still alive)")

    # Decode the saved state
    raw = open(path_save1, "rb").read()
    meta_saved, body_saved = codec.decode(vst3_state.unwrap_vc2(raw))

    print(f"    Oscillator0.plainParams after save: {body_saved['Oscillator0']['plainParams']}")
    print(f"    VoicePanel0.plainParams after save: {body_saved['VoicePanel0']['plainParams']}")

    # Check if Oscillator0 got any new fields
    osc_keys_before = set(body['Oscillator0'].keys())
    osc_keys_after = set(body_saved['Oscillator0'].keys())
    if osc_keys_after != osc_keys_before:
        print(f"    Oscillator0 keys changed: {osc_keys_after - osc_keys_before}")

    # Reload in a new engine
    engine2 = daw.RenderEngine(SR, BLOCK)
    synth2 = engine2.make_plugin_processor("serum", VST3)
    synth2.load_state(path_save1)

    readback2 = runtime_mod.read_host_param(synth2, "A Pan")
    print(f"\n[B] After reload in new engine")
    print(f"    A Pan readback: {readback2}")

    if abs(readback2 - 0.75) < 1e-5:
        print(f"    [SUCCESS] Value persisted!")
    else:
        print(f"    [FAIL] Value did NOT persist (reverted to {readback2})")

    del engine
    del engine2
    os.remove(path_save1)


if __name__ == "__main__":
    print("\n" + "█"*70)
    print("█ STEP 20A: CBOR MUTATION INVESTIGATION")
    print("█"*70)

    try:
        test_plainparams_mutation()
        test_host_param_to_cbor_sync()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
