"""STEP 20A: Discover persistent OSC1.Pan representation.

Experiment to find the authoritative CBOR path for pan persistence.
"""

import os
import tempfile
import json
import dawdreamer as daw
from serum2 import bridge, codec, vst3_state, pathmerge
from serum2.evidence import epoch as epoch_mod
from serum2.evidence import runtime as runtime_mod

VST3 = epoch_mod.SERUM_VST3
SR = 44100
BLOCK = 512


def inspect_skeleton_structure():
    """Examine the baseline skeleton to understand oscillator structure."""
    print("\n" + "="*70)
    print("INSPECT: Baseline Skeleton Structure")
    print("="*70)

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], skeleton[1]

    print(f"\nTop-level keys in body:")
    for key in sorted(body.keys()):
        value = body[key]
        if isinstance(value, dict):
            print(f"  {key}: dict with keys {list(value.keys())[:5]}")
        elif isinstance(value, list):
            print(f"  {key}: list with {len(value)} items")
        else:
            print(f"  {key}: {type(value).__name__}")

    # Look for oscillator-related keys
    print(f"\nSearching for oscillator structures...")
    for key in body.keys():
        if "osc" in key.lower() or "voice" in key.lower():
            value = body[key]
            if isinstance(value, dict):
                print(f"  {key}: dict keys = {list(value.keys())}")

    # Examine VoicePanel0 if it exists
    if "VoicePanel0" in body:
        print(f"\nVoicePanel0 structure:")
        vp = body["VoicePanel0"]
        if isinstance(vp, dict):
            for k, v in vp.items():
                if isinstance(v, dict):
                    print(f"  {k}: dict with keys {list(v.keys())[:10]}")
                else:
                    print(f"  {k}: {type(v).__name__} = {v}")

    # Examine Oscillator0 if it exists
    if "Oscillator0" in body:
        print(f"\nOscillator0 structure:")
        osc = body["Oscillator0"]
        if isinstance(osc, dict):
            for k, v in osc.items():
                if isinstance(v, dict):
                    print(f"  {k}: dict with keys {list(v.keys())[:10]}")
                elif isinstance(v, (list, tuple)):
                    print(f"  {k}: {type(v).__name__} with {len(v)} items")
                else:
                    print(f"  {k}: {type(v).__name__}")


def compare_baseline_and_mutated():
    """Create two states and compare what changed when modifying pan via HOST_PARAM."""
    print("\n" + "="*70)
    print("EXPERIMENT: Compare baseline vs HOST_PARAM pan mutation")
    print("="*70)

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta_base, body_base = skeleton[0], skeleton[1].copy()

    # State A: baseline (no mutation)
    print(f"\n[A] Baseline state...")
    fd, path_a = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(path_a, meta_base, body_base)

    engine_a = daw.RenderEngine(SR, BLOCK)
    synth_a = engine_a.make_plugin_processor("serum", VST3)
    synth_a.load_state(path_a)
    baseline_pan = runtime_mod.read_host_param(synth_a, "A Pan")
    print(f"  A Pan baseline: {baseline_pan}")
    del engine_a

    # State B: mutated via HOST_PARAM
    print(f"\n[B] HOST_PARAM mutation...")
    engine_b = daw.RenderEngine(SR, BLOCK)
    synth_b = engine_b.make_plugin_processor("serum", VST3)
    synth_b.load_state(path_a)

    # Change pan
    params = synth_b.get_parameters_description()
    by_name = {p["name"]: p["index"] for p in params}
    test_value = 0.75
    synth_b.set_parameter(by_name["A Pan"], float(test_value))
    readback = runtime_mod.read_host_param(synth_b, "A Pan")
    print(f"  Set A Pan to: {test_value}")
    print(f"  Readback: {readback}")

    # Save the mutated state (with HOST_PARAM changes)
    fd, path_b = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    synth_b.save_state(path_b)
    print(f"  Saved to: {path_b}")
    del engine_b

    # Decode both states to compare CBOR bodies
    print(f"\n[COMPARE] Decoding saved states...")
    raw_a = open(path_a, "rb").read()
    raw_b = open(path_b, "rb").read()

    meta_a_saved, body_a = codec.decode(vst3_state.unwrap_vc2(raw_a))
    meta_b_saved, body_b = codec.decode(vst3_state.unwrap_vc2(raw_b))

    # Find what changed
    print(f"\nTop-level keys changed:")
    changed_keys = []
    for key in body_b.keys():
        if key not in body_a:
            print(f"  NEW: {key}")
            changed_keys.append(key)
        elif body_a[key] != body_b[key]:
            print(f"  MODIFIED: {key}")
            changed_keys.append(key)

    if not changed_keys:
        print(f"  NO TOP-LEVEL CHANGES DETECTED")

    # Deep dive into changed keys
    for key in changed_keys[:3]:  # Limit inspection
        print(f"\nDeep inspection of changed key: {key}")
        v_a = body_a.get(key)
        v_b = body_b.get(key)

        if isinstance(v_a, dict) and isinstance(v_b, dict):
            for k in v_b.keys():
                if k not in v_a or v_a[k] != v_b[k]:
                    print(f"  {k}: {v_a.get(k)} -> {v_b[k]}")
        else:
            print(f"  Type A: {type(v_a)}")
            print(f"  Type B: {type(v_b)}")

    # Check if oscillator pan field changed
    print(f"\nSearching for pan-related fields in oscillator structures...")
    for key in ["Oscillator0", "VoicePanel0"]:
        if key in body_a and key in body_b:
            print(f"\n{key}:")
            obj_a = body_a[key]
            obj_b = body_b[key]
            if isinstance(obj_a, dict) and isinstance(obj_b, dict):
                for k in obj_b.keys():
                    if obj_a.get(k) != obj_b[k]:
                        print(f"  {k}: {obj_a.get(k)} -> {obj_b[k]}")

    os.remove(path_a)
    os.remove(path_b)


def search_for_pan_field_cbor():
    """Systematically search for a field that looks like it could be pan."""
    print("\n" + "="*70)
    print("SEARCH: Looking for pan-related fields in CBOR")
    print("="*70)

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], skeleton[1]

    pan_candidates = []

    def search_value(obj, path=""):
        """Recursively search for numeric values that look like pan (0-1)."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_path = f"{path}.{k}" if path else k
                search_value(v, new_path)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                new_path = f"{path}[{i}]"
                search_value(v, new_path)
        elif isinstance(obj, (int, float)):
            # Pan values are typically 0-1, centered at 0.5
            if 0 <= obj <= 1:
                if "pan" in path.lower() or "stereo" in path.lower():
                    pan_candidates.append((path, obj))

    search_value(body)

    if pan_candidates:
        print(f"Found {len(pan_candidates)} pan-related candidates:")
        for path, value in pan_candidates[:20]:
            print(f"  {path} = {value}")
    else:
        print(f"No obvious pan fields found")

    # Also check what fields exist in Oscillator0.plainParams
    if "Oscillator0" in body and "plainParams" in body["Oscillator0"]:
        pp = body["Oscillator0"]["plainParams"]
        print(f"\nOscillator0.plainParams keys:")
        if isinstance(pp, dict):
            for k in sorted(pp.keys()):
                print(f"  {k}")


if __name__ == "__main__":
    print("\n" + "█"*70)
    print("█ STEP 20A: DISCOVER PERSISTENT OSC1.PAN REPRESENTATION")
    print("█"*70)

    try:
        inspect_skeleton_structure()
        search_for_pan_field_cbor()
        compare_baseline_and_mutated()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
