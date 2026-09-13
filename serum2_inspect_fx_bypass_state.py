"""
One minimal DawDreamer state inspection:
Compare FX state in two conditions:
1. Empty rack (no FX)
2. Rack with FXDistortion

Goal: Identify actual bypass/enable mechanism
"""

import json
import sys

try:
    import cbor2
    print("CBOR2 available")
except ImportError:
    print("CBOR2 not available - cannot decode state")
    sys.exit(1)

try:
    import dawdreamer as dw
    from serum2.evidence.codec import load_xferjson_preset
    print("DawDreamer available\n")
except ImportError as e:
    print(f"DawDreamer/codec not available: {e}")
    sys.exit(1)

print("="*70)
print("STATE INSPECTION: Empty Rack vs FX Distortion")
print("="*70)

try:
    engine = dw.AudioEngine()
    engine.set_sample_rate(44100)
    engine.set_buffer_size(512)

    synth = engine.add_synth("serum", "/Program Files/VstPlugins/Serum_x64.vst3")
    print("\n1. Synth loaded")

    # Capture empty state
    print("\n2. Capturing empty FX rack state...")
    empty_state = synth.plugin.get_state()
    print(f"   State size: {len(empty_state)} bytes")

    # Try to decode
    try:
        empty_decoded = cbor2.loads(empty_state)
        print("   Decoded successfully")

        # Look for FXRack0
        if "FXRack0" in empty_decoded:
            rack0 = empty_decoded["FXRack0"]
            print(f"   FXRack0 keys: {list(rack0.keys())}")
            if "FX" in rack0:
                fx_array = rack0["FX"]
                print(f"   FX array type: {type(fx_array)}")
                print(f"   FX array length: {len(fx_array) if isinstance(fx_array, (list, tuple)) else 'N/A'}")
                print(f"   FX array contents: {fx_array}")
    except Exception as e:
        print(f"   CBOR decode error: {e}")

    print("\n3. Attempting to add FXDistortion via UI/parameter...")
    print("   (Skipped - would require UI automation)")
    print("   DawDreamer has limited UI control")

    print("\n" + "="*70)
    print("FINDING")
    print("="*70)
    print("""
The actual FX bypass mechanism requires either:

1. UI-level automation (not available in DawDreamer scripting)
2. Direct parameter discovery via effect enumeration
3. Preset corpus inspection (binary format)

EVIDENCE SO FAR:
- No kParamBypass field found in code
- ModSlot routes use ModSlot{N}.bypass field
- FX may use different representation

NEXT STEP:
Inspect actual Serum reference documentation or use
Serum's parameter enumeration to discover FX enable field.

CONCLUSION: Cannot determine FX bypass mechanism from code alone.
Must rely on:
1. Serum UI behavior (bypass button → state change)
2. Serum reference or documentation
3. Preset corpus forensics (if decodable)
    """)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
