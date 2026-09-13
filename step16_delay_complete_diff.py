"""
Step 16 — Complete recursive structural comparison of Delay bypass.

Goal: Find EVERY change from A->B and B->C. Do not filter or summarize.
Dump the complete FXRack0.FX[0] structure for each state.
"""
import gzip
import struct
import json
import zstandard as zstd
import cbor2
import sys
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
        raise ValueError(f'not XferJson')
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


def recursive_diff(obj_a, obj_b, path="", diffs=None):
    """
    Recursively compare two objects and record EVERY difference.
    Return list of (path, change_type, a_value, b_value).
    """
    if diffs is None:
        diffs = []

    # Type mismatch
    if type(obj_a) != type(obj_b):
        diffs.append((path or "ROOT", "TYPE_MISMATCH",
                      type(obj_a).__name__, type(obj_b).__name__,
                      repr(obj_a)[:200], repr(obj_b)[:200]))
        return diffs

    # Dict
    if isinstance(obj_a, dict):
        all_keys = sorted(set(list(obj_a.keys()) + list(obj_b.keys())))
        for key in all_keys:
            p = f"{path}.{key}" if path else key
            if key not in obj_a:
                diffs.append((p, "KEY_ADDED_IN_B", None, key, None, repr(obj_b[key])[:200]))
            elif key not in obj_b:
                diffs.append((p, "KEY_REMOVED_IN_B", key, None, repr(obj_a[key])[:200], None))
            else:
                recursive_diff(obj_a[key], obj_b[key], p, diffs)

    # List
    elif isinstance(obj_a, list):
        if len(obj_a) != len(obj_b):
            diffs.append((path, "ARRAY_LENGTH", len(obj_a), len(obj_b),
                          f"len={len(obj_a)}", f"len={len(obj_b)}"))
        for i in range(min(len(obj_a), len(obj_b))):
            recursive_diff(obj_a[i], obj_b[i], f"{path}[{i}]", diffs)

    # Scalar
    elif obj_a != obj_b:
        diffs.append((path, "VALUE", type(obj_a).__name__, type(obj_b).__name__,
                      repr(obj_a)[:200], repr(obj_b)[:200]))

    return diffs


def main():
    print("="*80)
    print("STEP 16: COMPLETE STRUCTURAL COMPARISON — DELAY BYPASS")
    print("="*80)

    states = {}
    for label, als_path in ALS_FILES.items():
        print(f"\n[{label}] Loading {Path(als_path).name}...")
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
            print(f"  ✓ Decoded {len(hex_text)} hex chars")
        except Exception as e:
            print(f"  ERROR: {e}")

    if len(states) < 2:
        print(f"\nERROR: Need at least 2 states.")
        return

    # Dump full FXRack0.FX[0] for each state
    print("\n" + "="*80)
    print("FULL FXRack0.FX[0] CONTENT FOR EACH STATE")
    print("="*80)

    for label, body in states.items():
        fx_rack = body.get("FXRack0", {})
        fx_list = fx_rack.get("FX", [])
        print(f"\n--- {label}: FXRack0 ---")
        print(f"FX array length: {len(fx_list)}")
        if fx_list:
            slot = fx_list[0]
            print(f"FXRack0.FX[0] keys: {sorted(slot.keys())}")
            print(f"\nFull FXRack0.FX[0] structure:")
            pprint(slot, width=120, depth=10)
        else:
            print("(FX array is empty)")

    # Recursive diff A -> B (ACTIVE -> BYPASSED)
    print("\n" + "="*80)
    print("COMPLETE DIFF: A->B  (ACTIVE -> BYPASSED)")
    print("="*80)

    if "A_ACTIVE" in states and "B_BYPASSED" in states:
        diffs_ab = recursive_diff(states["A_ACTIVE"], states["B_BYPASSED"])

        if diffs_ab:
            print(f"\nFound {len(diffs_ab)} differences:\n")
            for path, change_type, v1, v2, desc_a, desc_b in sorted(diffs_ab, key=lambda x: x[0]):
                print(f"PATH: {path}")
                print(f"CHANGE: {change_type}")
                if change_type == "TYPE_MISMATCH":
                    print(f"  A type: {v1}")
                    print(f"  B type: {v2}")
                elif change_type in ("KEY_ADDED_IN_B", "KEY_REMOVED_IN_B"):
                    if change_type == "KEY_ADDED_IN_B":
                        print(f"  Added in B: {desc_b}")
                    else:
                        print(f"  Removed in B: {desc_a}")
                elif change_type == "ARRAY_LENGTH":
                    print(f"  A: {desc_a}")
                    print(f"  B: {desc_b}")
                elif change_type == "VALUE":
                    print(f"  A ({v1}): {desc_a}")
                    print(f"  B ({v2}): {desc_b}")
                print()
        else:
            print("\nNO DIFFERENCES FOUND between A and B")

    # Recursive diff B -> C (BYPASSED -> REMOVED)
    print("\n" + "="*80)
    print("COMPLETE DIFF: B->C  (BYPASSED -> REMOVED)")
    print("="*80)

    if "B_BYPASSED" in states and "C_REMOVED" in states:
        diffs_bc = recursive_diff(states["B_BYPASSED"], states["C_REMOVED"])

        if diffs_bc:
            print(f"\nFound {len(diffs_bc)} differences:\n")
            for path, change_type, v1, v2, desc_a, desc_b in sorted(diffs_bc, key=lambda x: x[0]):
                print(f"PATH: {path}")
                print(f"CHANGE: {change_type}")
                if change_type == "TYPE_MISMATCH":
                    print(f"  A type: {v1}")
                    print(f"  B type: {v2}")
                elif change_type in ("KEY_ADDED_IN_B", "KEY_REMOVED_IN_B"):
                    if change_type == "KEY_ADDED_IN_B":
                        print(f"  Added in C: {desc_b}")
                    else:
                        print(f"  Removed from C: {desc_a}")
                elif change_type == "ARRAY_LENGTH":
                    print(f"  B: {desc_a}")
                    print(f"  C: {desc_b}")
                elif change_type == "VALUE":
                    print(f"  B ({v1}): {desc_a}")
                    print(f"  C ({v2}): {desc_b}")
                print()
        else:
            print("\nNO DIFFERENCES FOUND between B and C (should only be FX array removal)")

    # Analysis
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)

    if "A_ACTIVE" in states and "B_BYPASSED" in states:
        diffs_ab = recursive_diff(states["A_ACTIVE"], states["B_BYPASSED"])

        if not diffs_ab:
            print("\n⚠️  NO CHANGES from A->B (ACTIVE->BYPASSED)")
            print("    Hypothesis: Bypass state may not be stored in the main Serum state.")
            print("    Alternative: Bypass may be stored in ControllerState (not ProcessorState).")
            print("    Or: The bypass flag is encoded in a way not yet visible in the CBOR decode.")
        else:
            print(f"\n✓ Found {len(diffs_ab)} changes from A->B:")
            fx_related = [d for d in diffs_ab if "FX" in d[0]]
            if fx_related:
                print("\n  FX-related changes:")
                for d in fx_related:
                    print(f"    {d[0]}: {d[1]} — {d[4]} → {d[5]}")
            else:
                print("\n  (No FX-specific changes found)")


if __name__ == "__main__":
    main()
