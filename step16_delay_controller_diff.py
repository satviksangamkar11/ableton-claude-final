"""
Step 16 — Check ControllerState for Delay bypass.
ProcessorState shows NO changes A->B, so bypass may be in ControllerState.
"""
import gzip
import struct
import json
import zstandard as zstd
import cbor2
from pathlib import Path
from xml.etree import ElementTree as ET
from pprint import pprint

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


def find_serum_controller_state(als_path: str):
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
                ctrl = vst3preset.find('ControllerState')
                if ctrl is not None and ctrl.text:
                    return ctrl.text.strip()
    return None


def decode_hex_state(hex_text: str):
    raw = bytes.fromhex(hex_text)
    _, body = decode_xferjson(raw)
    return body


def recursive_diff(obj_a, obj_b, path="", diffs=None):
    if diffs is None:
        diffs = []
    if type(obj_a) != type(obj_b):
        diffs.append((path or "ROOT", "TYPE_MISMATCH", type(obj_a).__name__, type(obj_b).__name__,
                      repr(obj_a)[:150], repr(obj_b)[:150]))
        return diffs
    if isinstance(obj_a, dict):
        all_keys = sorted(set(list(obj_a.keys()) + list(obj_b.keys())))
        for key in all_keys:
            p = f"{path}.{key}" if path else key
            if key not in obj_a:
                diffs.append((p, "KEY_ADDED_IN_B", None, key, None, repr(obj_b[key])[:150]))
            elif key not in obj_b:
                diffs.append((p, "KEY_REMOVED_IN_B", key, None, repr(obj_a[key])[:150], None))
            else:
                recursive_diff(obj_a[key], obj_b[key], p, diffs)
    elif isinstance(obj_a, list):
        if len(obj_a) != len(obj_b):
            diffs.append((path, "ARRAY_LENGTH", len(obj_a), len(obj_b),
                          f"len={len(obj_a)}", f"len={len(obj_b)}"))
        for i in range(min(len(obj_a), len(obj_b))):
            recursive_diff(obj_a[i], obj_b[i], f"{path}[{i}]", diffs)
    elif obj_a != obj_b:
        diffs.append((path, "VALUE", type(obj_a).__name__, type(obj_b).__name__,
                      repr(obj_a)[:150], repr(obj_b)[:150]))
    return diffs


def main():
    print("="*80)
    print("STEP 16: CONTROLLER STATE ANALYSIS — DELAY BYPASS")
    print("="*80)

    states = {}
    for label, als_path in ALS_FILES.items():
        print(f"\n[{label}] Loading ControllerState...")
        if not Path(als_path).exists():
            print(f"  NOT FOUND")
            continue
        hex_text = find_serum_controller_state(als_path)
        if not hex_text:
            print(f"  ERROR: No ControllerState")
            continue
        try:
            body = decode_hex_state(hex_text)
            states[label] = body
            print(f"  ✓ Decoded {len(hex_text)} hex chars")
            print(f"  Top-level keys: {sorted(body.keys())[:10]}")
        except Exception as e:
            print(f"  ERROR: {e}")

    if len(states) < 2:
        print(f"\nERROR: Need at least 2 states.")
        return

    # Show FXRack structures
    print("\n" + "="*80)
    print("CONTROLLER STATE: FXRack0 CONTENT")
    print("="*80)

    for label, body in states.items():
        print(f"\n--- {label} ---")
        if "FXRack0" in body:
            rack = body["FXRack0"]
            print(f"FXRack0 type: {type(rack)}")
            if isinstance(rack, dict):
                print(f"FXRack0 keys: {sorted(rack.keys())}")
                if "FX" in rack:
                    fx = rack["FX"]
                    print(f"FXRack0.FX type: {type(fx)}")
                    print(f"FXRack0.FX length: {len(fx) if isinstance(fx, list) else 'N/A'}")
                    if isinstance(fx, list) and fx:
                        print(f"\nFXRack0.FX[0]:")
                        pprint(fx[0], width=120, depth=15)
        else:
            print("(No FXRack0 in ControllerState)")

    # Diff A->B
    print("\n" + "="*80)
    print("DIFF: A->B  (ControllerState)")
    print("="*80)

    if "A_ACTIVE" in states and "B_BYPASSED" in states:
        diffs_ab = recursive_diff(states["A_ACTIVE"], states["B_BYPASSED"])
        if diffs_ab:
            print(f"\nFound {len(diffs_ab)} differences:\n")
            for path, ctype, v1, v2, d_a, d_b in sorted(diffs_ab, key=lambda x: x[0])[:50]:
                print(f"PATH: {path}")
                print(f"CHANGE: {ctype}")
                if ctype == "VALUE":
                    print(f"  A: {d_a}")
                    print(f"  B: {d_b}")
                elif ctype == "ARRAY_LENGTH":
                    print(f"  A: {d_a}, B: {d_b}")
                elif "KEY" in ctype:
                    print(f"  {d_a or d_b}")
                print()
            if len(diffs_ab) > 50:
                print(f"\n... and {len(diffs_ab) - 50} more differences")
        else:
            print("\nNO DIFFERENCES")


if __name__ == "__main__":
    main()
