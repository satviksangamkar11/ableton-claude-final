"""
Step 16 - Delay FX bypass confirmation.
Extract ProcessorState from three Delay .als files and diff to confirm bypass mechanism.
"""
import gzip
import struct
import json
import zstandard as zstd
import cbor2
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ALS_FILES = {
    "A_ACTIVE":   r"D:\ableton claude\step16_delay_a_active Project\step16_delay_a_active.als",
    "B_BYPASSED": r"D:\ableton claude\step16_delay_b_bypassed Project\step16_delay_b_bypassed.als",
    "C_REMOVED":  r"D:\ableton claude\step16_delay_c_removed Project\step16_delay_c_removed.als",
}

MAGIC = b'XferJson'


def decode_xferjson(raw: bytes):
    if raw[:8] != MAGIC:
        raise ValueError(f'not XferJson (got {raw[:8]!r})')
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


def deep_diff(obj_a, obj_b, path="", diff_list=None):
    if diff_list is None:
        diff_list = []
    if type(obj_a) != type(obj_b):
        diff_list.append({"path": path or "ROOT", "change": "TYPE_MISMATCH",
                          "a": repr(obj_a)[:300], "b": repr(obj_b)[:300]})
        return diff_list
    if isinstance(obj_a, dict):
        for key in sorted(set(list(obj_a.keys()) + list(obj_b.keys()))):
            p = f"{path}.{key}" if path else key
            if key not in obj_a:
                diff_list.append({"path": p, "change": "KEY_ADDED", "b": repr(obj_b[key])[:200]})
            elif key not in obj_b:
                diff_list.append({"path": p, "change": "KEY_REMOVED", "a": repr(obj_a[key])[:200]})
            else:
                deep_diff(obj_a[key], obj_b[key], p, diff_list)
    elif isinstance(obj_a, list):
        if len(obj_a) != len(obj_b):
            diff_list.append({"path": path, "change": "ARRAY_LENGTH",
                              "a_len": len(obj_a), "b_len": len(obj_b)})
        for i in range(min(len(obj_a), len(obj_b))):
            deep_diff(obj_a[i], obj_b[i], f"{path}[{i}]", diff_list)
    elif obj_a != obj_b:
        diff_list.append({"path": path, "change": "VALUE",
                          "a": obj_a, "b": obj_b,
                          "a_type": type(obj_a).__name__, "b_type": type(obj_b).__name__})
    return diff_list


def print_diff(diffs, label):
    print(f"\n{'='*70}")
    print(f"{label}  [{len(diffs)} changes]")
    print(f"{'='*70}")
    for d in sorted(diffs, key=lambda x: x["path"]):
        print(f"  PATH: {d['path']}")
        print(f"  CHANGE: {d['change']}")
        if d["change"] == "TYPE_MISMATCH":
            print(f"  A: {d['a']}")
            print(f"  B: {d['b']}")
        elif d["change"] == "VALUE":
            print(f"  A ({d['a_type']}): {repr(d['a'])}")
            print(f"  B ({d['b_type']}): {repr(d['b'])}")
        elif d["change"] == "ARRAY_LENGTH":
            print(f"  A length: {d['a_len']}  B length: {d['b_len']}")
        elif "a" in d:
            print(f"  A: {d['a']}")
        elif "b" in d:
            print(f"  B: {d['b']}")
        print()


def inspect_fx(body, label):
    print(f"\n--- {label}: FXRack0 ---")
    rack = body.get("FXRack0", {})
    fx = rack.get("FX", [])
    print(f"  FX count: {len(fx)}")
    for i, slot in enumerate(fx):
        print(f"  FX[{i}]:")
        for k, v in sorted(slot.items()):
            print(f"    {k}: {repr(v)[:150]}")


def main():
    print("="*70)
    print("STEP 16: DELAY FX BYPASS CONFIRMATION")
    print("="*70)

    states = {}
    for label, als_path in ALS_FILES.items():
        print(f"\n[{label}] {Path(als_path).name}")
        if not Path(als_path).exists():
            print(f"  NOT FOUND: {als_path}")
            continue
        hex_text = find_serum_processor_state(als_path)
        if not hex_text:
            print(f"  ERROR: No ProcessorState found")
            continue
        print(f"  ProcessorState: {len(hex_text)} hex chars")
        try:
            body = decode_hex_state(hex_text)
            states[label] = body
            print(f"  Decoded OK. Keys: {sorted(body.keys())[:5]}...")
        except Exception as e:
            print(f"  ERROR: {e}")

    if len(states) < 2:
        print(f"\nERROR: Need at least 2 states. Got {len(states)}.")
        sys.exit(1)

    for label, body in states.items():
        inspect_fx(body, label)

    if "A_ACTIVE" in states and "B_BYPASSED" in states:
        diff_ab = deep_diff(states["A_ACTIVE"], states["B_BYPASSED"])
        print_diff(diff_ab, "A->B  DELAY ACTIVE->BYPASSED")

        ra = states["A_ACTIVE"].get("FXRack0", {}).get("FX", [])
        rb = states["B_BYPASSED"].get("FXRack0", {}).get("FX", [])
        if ra and rb:
            fd = deep_diff(ra[0], rb[0])
            print_diff(fd, "FOCUSED: FXRack0.FX[0]  A->B")

    if "B_BYPASSED" in states and "C_REMOVED" in states:
        diff_bc = deep_diff(states["B_BYPASSED"], states["C_REMOVED"])
        print_diff(diff_bc, "B->C  DELAY BYPASSED->REMOVED")

    if "A_ACTIVE" in states and "C_REMOVED" in states:
        diff_ac = deep_diff(states["A_ACTIVE"], states["C_REMOVED"])
        print_diff(diff_ac, "A->C  DELAY ACTIVE->REMOVED")

    print("\n" + "="*70)
    print("CONFIRMATION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
