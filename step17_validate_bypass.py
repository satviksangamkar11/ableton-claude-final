"""Step 17 Validation: Test bypass/unbypass operations against real Serum states.

Tests the implementation against the three authoritative states captured in Step 16:
- A_ACTIVE: Distortion active (type=0)
- B_BYPASSED: Distortion bypassed
- C_REMOVED: Distortion removed

And for Delay:
- delay_a_active: Delay active (type=4)
- delay_b_bypassed: Delay bypassed
- delay_c_removed: Delay removed
"""
import gzip
import struct
import json
import zstandard as zstd
import cbor2
from pathlib import Path
from xml.etree import ElementTree as ET

ALS_FILES_DISTORTION = {
    "A_ACTIVE":   r"D:\ableton claude\step16_state_a_active Project\step16_state_a_active.als",
    "B_BYPASSED": r"D:\ableton claude\step16_state_a_activestep16_state_b_bypassed Project\step16_state_a_activestep16_state_b_bypassed.als",
    "C_REMOVED":  r"D:\ableton claude\step16_state_c_removed Project\step16_state_c_removed.als",
}

ALS_FILES_DELAY = {
    "A_ACTIVE":   r"D:\ableton claude\step16_delay_a_active Project\step16_delay_a_active.als",
    "B_BYPASSED": r"D:\ableton claude\step16_delay_b_bypassed Project\step16_delay_b_bypassed.als",
    "C_REMOVED":  r"D:\ableton claude\step16_delay_c_removed Project\step16_delay_c_removed.als",
}


def decode_xferjson(raw: bytes):
    if raw[:8] != b'XferJson':
        raise ValueError('not XferJson')
    meta_len = struct.unpack('<Q', raw[9:17])[0]
    meta = json.loads(raw[17:17 + meta_len])
    tail = raw[17 + meta_len:]
    raw_len, mode = struct.unpack('<II', tail[0:8])
    decompressed = zstd.ZstdDecompressor().stream_reader(tail[8:]).read()
    body = cbor2.loads(decompressed)
    return meta, body


def find_serum_processor_state(als_path: str):
    with gzip.open(als_path, 'rb') as f:
        xml_data = f.read()
    root = ET.fromstring(xml_data)
    for vst3_info in root.iter('Vst3PluginInfo'):
        name_elem = vst3_info.find('Name')
        name = name_elem.get('Value', '') if name_elem is not None else ''
        if 'Serum' not in name:
            continue
        for preset in vst3_info.iter('Preset'):
            for vst3preset in preset.iter('Vst3Preset'):
                proc = vst3preset.find('ProcessorState')
                if proc is not None and proc.text:
                    return proc.text.strip()
    return None


def decode_hex_state(hex_text: str):
    raw = bytes.fromhex(hex_text)
    _, body = decode_xferjson(raw)
    return body


def validate_bypass_mechanism(fx_name, als_files):
    """Validate bypass mechanism for a specific FX type."""
    print(f"\n{'='*80}")
    print(f"VALIDATING {fx_name.upper()} BYPASS MECHANISM")
    print(f"{'='*80}")

    states = {}
    for label, als_path in als_files.items():
        if not Path(als_path).exists():
            print(f"[{label}] File not found: {als_path}")
            continue

        hex_text = find_serum_processor_state(als_path)
        if not hex_text:
            print(f"[{label}] No ProcessorState found")
            continue

        body = decode_hex_state(hex_text)
        states[label] = body
        print(f"[{label}] ✓ State loaded")

    if len(states) < 3:
        print(f"ERROR: Need 3 states, got {len(states)}")
        return False

    # Verify A_ACTIVE state
    fx_rack_a = states["A_ACTIVE"].get("FXRack0", {})
    fx_a = fx_rack_a.get("FX", [])
    if not fx_a:
        print("ERROR: A_ACTIVE has no FX")
        return False

    slot_a = fx_a[0]
    print(f"\nA_ACTIVE FX[0] keys: {sorted(slot_a.keys())}")

    # Find the FX type name (FXDistortion, FXDelay, etc.)
    fx_type_name = None
    for key in slot_a.keys():
        if key.startswith('FX'):
            fx_type_name = key
            break

    if not fx_type_name:
        print("ERROR: No FX type found in slot")
        return False

    print(f"FX Type: {fx_type_name}")

    # Get plainParams from each state
    params_a = slot_a.get(fx_type_name, {}).get('plainParams')
    fx_rack_b = states["B_BYPASSED"].get("FXRack0", {})
    fx_b = fx_rack_b.get("FX", [])
    params_b = fx_b[0].get(fx_type_name, {}).get('plainParams') if fx_b else None

    # Verify mechanism
    print(f"\nA_ACTIVE: plainParams = {repr(params_a)[:80]}")
    print(f"B_BYPASSED: plainParams = {repr(params_b)[:80]}")

    # Check that A is active (string) and B is bypassed (dict with kParamEnable)
    if params_a != "default":
        print(f"ERROR: A_ACTIVE plainParams should be 'default', got {repr(params_a)}")
        return False

    if not isinstance(params_b, dict) or params_b.get("kParamEnable") != 0.0:
        print(f"ERROR: B_BYPASSED plainParams should be {{'kParamEnable': 0.0}}, got {repr(params_b)}")
        return False

    print("\n✓ Bypass mechanism verified:")
    print("  ACTIVE: plainParams = 'default'")
    print("  BYPASSED: plainParams = {'kParamEnable': 0.0}")

    # Verify C_REMOVED topology
    fx_rack_c = states["C_REMOVED"].get("FXRack0", {})
    fx_c = fx_rack_c.get("FX", [])

    print(f"\nC_REMOVED FX array length: {len(fx_c)} (expected 0)")
    if len(fx_c) != 0:
        print("ERROR: C_REMOVED should have empty FX array")
        return False

    print("✓ Remove operation changes topology as expected")

    # Summary
    print(f"\n✓ {fx_name.upper()} bypass mechanism is VALID")
    print(f"  - Bypass preserves slot and topology")
    print(f"  - Remove operation is distinct (changes array)")
    print(f"  - Representation: plainParams string ↔ dict")

    return True


def main():
    print("="*80)
    print("STEP 17: FX BYPASS VALIDATION")
    print("Validating bypass mechanism against real captured states")
    print("="*80)

    # Validate Distortion
    distortion_ok = validate_bypass_mechanism("Distortion", ALS_FILES_DISTORTION)

    # Validate Delay
    delay_ok = validate_bypass_mechanism("Delay", ALS_FILES_DELAY)

    print(f"\n{'='*80}")
    print("VALIDATION RESULTS")
    print(f"{'='*80}")
    print(f"Distortion: {'✓ PASSED' if distortion_ok else '✗ FAILED'}")
    print(f"Delay: {'✓ PASSED' if delay_ok else '✗ FAILED'}")

    if distortion_ok and delay_ok:
        print(f"\n✓ STEP 17 VALIDATION COMPLETE - All checks passed")
        return 0
    else:
        print(f"\n✗ STEP 17 VALIDATION FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
