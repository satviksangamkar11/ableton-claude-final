"""
Step 16 — Complete field-by-field inspection of FXDelay.
Dump EVERY value in FXDelay for states A, B, C.
Compare recursively to find what changes during bypass.
"""
import gzip
import struct
import json
import zstandard as zstd
import cbor2
from pathlib import Path
from xml.etree import ElementTree as ET

ALS_FILES = {
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


def dump_value(v, indent=0):
    """Recursively dump a value showing type and content."""
    prefix = "  " * indent
    if v is None:
        return f"{prefix}None"
    elif isinstance(v, bool):
        return f"{prefix}bool: {v}"
    elif isinstance(v, int):
        return f"{prefix}int: {v}"
    elif isinstance(v, float):
        return f"{prefix}float: {v}"
    elif isinstance(v, str):
        if len(v) > 100:
            return f"{prefix}str[{len(v)}]: {v[:50]}...{v[-50:]}"
        return f"{prefix}str: {repr(v)}"
    elif isinstance(v, bytes):
        return f"{prefix}bytes[{len(v)}]: {v[:20]}..."
    elif isinstance(v, dict):
        result = [f"{prefix}dict[{len(v)} keys]:"]
        for k in sorted(v.keys()):
            result.append(f"{prefix}  {k}: {dump_value(v[k], indent+2).strip()}")
        return "\n".join(result)
    elif isinstance(v, list):
        result = [f"{prefix}list[{len(v)}]:"]
        for i, item in enumerate(v[:10]):  # Show first 10
            result.append(f"{prefix}  [{i}]: {dump_value(item, indent+2).strip()}")
        if len(v) > 10:
            result.append(f"{prefix}  ... and {len(v)-10} more items")
        return "\n".join(result)
    else:
        return f"{prefix}{type(v).__name__}: {repr(v)[:100]}"


def main():
    print("="*80)
    print("STEP 16: COMPLETE FXDELAY FIELD INSPECTION")
    print("="*80)

    states = {}
    for label, als_path in ALS_FILES.items():
        print(f"\n[{label}] Loading...")
        if not Path(als_path).exists():
            print(f"  NOT FOUND")
            continue
        hex_text = find_serum_processor_state(als_path)
        if not hex_text:
            print(f"  ERROR: No ProcessorState")
            continue
        try:
            body = decode_hex_state(hex_text)
            states[label] = body
            print(f"  ✓ Decoded")
        except Exception as e:
            print(f"  ERROR: {e}")

    if len(states) < 3:
        print(f"\nERROR: Need 3 states.")
        return

    # Dump FXDelay for each state
    print("\n" + "="*80)
    print("FXDelay STRUCTURE FOR EACH STATE")
    print("="*80)

    for label, body in states.items():
        fx_rack = body.get("FXRack0", {})
        fx_list = fx_rack.get("FX", [])

        print(f"\n--- {label} ---")

        if not fx_list:
            print("(FX array empty)")
            continue

        slot = fx_list[0]

        if "FXDelay" not in slot:
            print("(No FXDelay in slot)")
            continue

        fx_delay = slot["FXDelay"]

        print(f"\nFXDelay object:")
        print(f"  type: {type(fx_delay)}")

        if isinstance(fx_delay, dict):
            print(f"  keys: {sorted(fx_delay.keys())}")
            for key in sorted(fx_delay.keys()):
                val = fx_delay[key]
                print(f"\n  Key: {key}")
                print(f"  Value type: {type(val).__name__}")
                if isinstance(val, str):
                    print(f"  Value: {repr(val)}")
                elif isinstance(val, dict):
                    print(f"  Dict keys: {sorted(val.keys())}")
                    for k2 in sorted(val.keys()):
                        v2 = val[k2]
                        print(f"    {k2}: {repr(v2)}")
                elif isinstance(val, list):
                    print(f"  List length: {len(val)}")
                    for i, item in enumerate(val[:5]):
                        print(f"    [{i}]: {repr(item)[:100]}")
                    if len(val) > 5:
                        print(f"    ... and {len(val)-5} more")
                else:
                    print(f"  Value: {repr(val)}")

    # Compare A->B at every level
    print("\n" + "="*80)
    print("COMPARISON: A->B  (ACTIVE -> BYPASSED)")
    print("="*80)

    a_fx_delay = states["A_ACTIVE"].get("FXRack0", {}).get("FX", [{}])[0].get("FXDelay", {})
    b_fx_delay = states["B_BYPASSED"].get("FXRack0", {}).get("FX", [{}])[0].get("FXDelay", {})

    if a_fx_delay and b_fx_delay:
        print("\nA_ACTIVE FXDelay:")
        print(dump_value(a_fx_delay))

        print("\n\nB_BYPASSED FXDelay:")
        print(dump_value(b_fx_delay))

        print("\n\nDifferences (A vs B):")
        if a_fx_delay == b_fx_delay:
            print("  ⚠️  NO DIFFERENCES")
        else:
            print("  Changes found:")
            all_keys = set(list((a_fx_delay if isinstance(a_fx_delay, dict) else {}).keys()) +
                          list((b_fx_delay if isinstance(b_fx_delay, dict) else {}).keys()))
            for key in sorted(all_keys):
                a_val = a_fx_delay.get(key) if isinstance(a_fx_delay, dict) else None
                b_val = b_fx_delay.get(key) if isinstance(b_fx_delay, dict) else None
                if a_val != b_val:
                    print(f"\n  {key}:")
                    print(f"    A: {repr(a_val)[:150]}")
                    print(f"    B: {repr(b_val)[:150]}")

    # Look at whole FX slot
    print("\n" + "="*80)
    print("FULL FX[0] SLOT COMPARISON")
    print("="*80)

    a_slot = states["A_ACTIVE"].get("FXRack0", {}).get("FX", [{}])[0]
    b_slot = states["B_BYPASSED"].get("FXRack0", {}).get("FX", [{}])[0]

    print(f"\nA_ACTIVE FX[0] keys: {sorted(a_slot.keys())}")
    print(f"B_BYPASSED FX[0] keys: {sorted(b_slot.keys())}")

    all_keys_slot = set(list(a_slot.keys()) + list(b_slot.keys()))
    for key in sorted(all_keys_slot):
        a_val = a_slot.get(key)
        b_val = b_slot.get(key)
        if a_val != b_val:
            print(f"\n{key} differs:")
            print(f"  A: {repr(a_val)[:120]}")
            print(f"  B: {repr(b_val)[:120]}")


if __name__ == "__main__":
    main()
