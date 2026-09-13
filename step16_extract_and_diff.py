"""
Step 16 - Extract Serum state from saved Ableton .als files and diff them.

Ableton .als files are gzip-compressed XML. Inside, plugin states are stored
as base64-encoded binary data in <Buffer> elements inside plugin device nodes.
The Serum 2 state is in XferJson format, decoded by serum2/codec.py.
"""
import gzip
import base64
import struct
import json
import zstandard as zstd
import cbor2
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ALS_FILES = {
    "A_ACTIVE":   r"D:\ableton claude\step16_state_a_active Project\step16_state_a_active.als",
    "B_BYPASSED":  r"D:\ableton claude\step16_state_a_activestep16_state_b_bypassed Project\step16_state_a_activestep16_state_b_bypassed.als",
    "C_REMOVED":  r"D:\ableton claude\step16_state_c_removed Project\step16_state_c_removed.als",
}

MAGIC = b'XferJson'


def decode_xferjson(raw: bytes):
    """Decode XferJson container -> (meta: dict, body: dict)."""
    if raw[:8] != MAGIC:
        raise ValueError(f'not XferJson (got {raw[:8]!r})')
    meta_len = struct.unpack('<Q', raw[9:17])[0]
    meta = json.loads(raw[17:17 + meta_len])
    tail = raw[17 + meta_len:]
    raw_len, mode = struct.unpack('<II', tail[0:8])
    body = cbor2.loads(
        zstd.ZstdDecompressor().decompress(tail[8:], max_length=max(raw_len * 4, 1 << 22))
    )
    return meta, body


def find_serum_buffer(als_path: str):
    """Extract Serum 2 plugin state buffer from .als file."""
    with gzip.open(als_path, 'rb') as f:
        xml_data = f.read()

    root = ET.fromstring(xml_data)

    # Find all PluginDevice elements that reference Serum
    serum_nodes = []
    for elem in root.iter():
        if elem.tag == 'PluginDesc':
            # Look for Serum in Vst3PluginInfo or VstPluginInfo
            for child in elem.iter():
                if child.tag in ('Vst3PluginInfo', 'VstPluginInfo'):
                    name = child.get('Name', '') or child.get('PlugName', '')
                    if 'Serum' in name or 'serum' in name.lower():
                        serum_nodes.append(elem)
                        break
                # Also check Name attribute directly
                if child.tag == 'Name' and 'Serum' in child.get('Value', ''):
                    serum_nodes.append(elem)
                    break

    print(f"  Found {len(serum_nodes)} Serum plugin nodes in {Path(als_path).name}")

    if not serum_nodes:
        # Try broader search: look for Buffer elements near plugin data
        # Search for PluginDevice that has a Buffer child
        for elem in root.iter('PluginDevice'):
            for buf_elem in elem.iter('Buffer'):
                data = buf_elem.text
                if data and len(data) > 100:
                    # Decode and check if it's XferJson
                    try:
                        raw = base64.b64decode(data.strip())
                        if raw[:8] == MAGIC:
                            print(f"  Found XferJson buffer in PluginDevice (unnamed)")
                            return raw
                    except Exception:
                        pass

        print(f"  ERROR: No Serum plugin state found")
        return None

    # Get the Buffer element from the PluginDevice containing this PluginDesc
    for serum_elem in serum_nodes:
        # Walk up/around to find the PluginDevice parent
        parent_device = None
        for elem in root.iter('PluginDevice'):
            for child in elem.iter():
                if child is serum_elem:
                    parent_device = elem
                    break
            if parent_device:
                break

        if parent_device is None:
            # The serum_elem might BE inside an InstrumentBranchPreset or similar
            # Try searching directly from the root for Buffer near Serum info
            continue

        # Find Buffer in PluginDevice
        for buf_elem in parent_device.iter('Buffer'):
            data = buf_elem.text
            if data and len(data) > 100:
                try:
                    raw = base64.b64decode(data.strip())
                    if raw[:8] == MAGIC:
                        return raw
                    else:
                        print(f"  Buffer found but not XferJson (starts: {raw[:8]!r})")
                except Exception as e:
                    print(f"  Buffer decode error: {e}")

    return None


def deep_diff(obj_a, obj_b, path="", diff_list=None):
    if diff_list is None:
        diff_list = []
    if type(obj_a) != type(obj_b):
        diff_list.append({"path": path or "ROOT", "change": "TYPE_MISMATCH",
                          "a_type": type(obj_a).__name__, "b_type": type(obj_b).__name__,
                          "a_value": repr(obj_a)[:200], "b_value": repr(obj_b)[:200]})
        return diff_list
    if isinstance(obj_a, dict):
        for key in sorted(set(list(obj_a.keys()) + list(obj_b.keys()))):
            p = f"{path}.{key}" if path else key
            if key not in obj_a:
                diff_list.append({"path": p, "change": "KEY_ADDED_IN_B", "b_value": repr(obj_b[key])[:200]})
            elif key not in obj_b:
                diff_list.append({"path": p, "change": "KEY_REMOVED_IN_B", "a_value": repr(obj_a[key])[:200]})
            else:
                deep_diff(obj_a[key], obj_b[key], p, diff_list)
        return diff_list
    if isinstance(obj_a, list):
        if len(obj_a) != len(obj_b):
            diff_list.append({"path": path, "change": "ARRAY_LENGTH",
                              "a_length": len(obj_a), "b_length": len(obj_b)})
        for i in range(min(len(obj_a), len(obj_b))):
            deep_diff(obj_a[i], obj_b[i], f"{path}[{i}]", diff_list)
        return diff_list
    if obj_a != obj_b:
        diff_list.append({"path": path, "change": "VALUE_CHANGE",
                          "a_value": obj_a, "b_value": obj_b,
                          "a_type": type(obj_a).__name__, "b_type": type(obj_b).__name__})
    return diff_list


def print_diff(diffs, label):
    print(f"\n{'='*70}")
    print(f"{label}: {len(diffs)} changes")
    print(f"{'='*70}")
    for d in sorted(diffs, key=lambda x: x["path"]):
        print(f"\n  PATH: {d['path']}")
        print(f"  CHANGE: {d['change']}")
        if d["change"] == "VALUE_CHANGE":
            print(f"  A ({d.get('a_type','?')}): {repr(d.get('a_value'))}")
            print(f"  B ({d.get('b_type','?')}): {repr(d.get('b_value'))}")
        elif d["change"] == "ARRAY_LENGTH":
            print(f"  A length: {d['a_length']}  B length: {d['b_length']}")
        elif "a_value" in d:
            print(f"  A: {d['a_value']}")
        elif "b_value" in d:
            print(f"  B: {d['b_value']}")


def inspect_fx_slot(body, label, slot_idx=0):
    print(f"\n--- {label}: FXRack0.FX[{slot_idx}] ---")
    rack = body.get("FXRack0", {})
    fx = rack.get("FX", [])
    print(f"  FX array length: {len(fx)}")
    if len(fx) > slot_idx:
        slot = fx[slot_idx]
        for k, v in sorted(slot.items()):
            if isinstance(v, dict):
                print(f"  {k}: dict keys={sorted(v.keys())}")
                for kk, vv in sorted(v.items()):
                    print(f"    {kk}: {repr(vv)[:100]}")
            elif isinstance(v, list):
                print(f"  {k}: list len={len(v)}")
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        print(f"    [{i}]: dict keys={sorted(item.keys())}")
                        for kk, vv in sorted(item.items()):
                            print(f"       {kk}: {repr(vv)[:100]}")
                    else:
                        print(f"    [{i}]: {repr(item)[:120]}")
            else:
                print(f"  {k}: {repr(v)[:100]}")


def main():
    print("="*70)
    print("STEP 16: SERUM FX BYPASS DISCOVERY")
    print("Extracting plugin states from Ableton .als files")
    print("="*70)

    states = {}
    for label, als_path in ALS_FILES.items():
        print(f"\n[{label}] Loading: {Path(als_path).name}")
        if not Path(als_path).exists():
            print(f"  ERROR: File not found: {als_path}")
            continue
        raw = find_serum_buffer(als_path)
        if raw is None:
            print(f"  ERROR: Could not extract Serum state")
            continue
        print(f"  Raw bytes: {len(raw)}")
        try:
            meta, body = decode_xferjson(raw)
            print(f"  XferJson decoded OK. Top-level keys: {sorted(body.keys())[:10]}")
            states[label] = body
        except Exception as e:
            print(f"  ERROR decoding XferJson: {e}")
            # Try decoding as raw CBOR
            try:
                body = cbor2.loads(raw)
                print(f"  Decoded as raw CBOR. Keys: {sorted(body.keys())[:10]}")
                states[label] = body
            except Exception as e2:
                print(f"  ERROR decoding CBOR: {e2}")

    if len(states) < 2:
        print("\nERROR: Need at least 2 states for comparison. Aborting.")
        sys.exit(1)

    # Inspect FX slots
    for label, body in states.items():
        inspect_fx_slot(body, label)

    # Diffs
    if "A_ACTIVE" in states and "B_BYPASSED" in states:
        diff_ab = deep_diff(states["A_ACTIVE"], states["B_BYPASSED"])
        print_diff(diff_ab, "A->B  ACTIVE->BYPASSED")

        # Focused diff: FXRack0.FX[0]
        ra = states["A_ACTIVE"].get("FXRack0", {}).get("FX", [])
        rb = states["B_BYPASSED"].get("FXRack0", {}).get("FX", [])
        if ra and rb:
            print("\n" + "="*70)
            print("FOCUSED: FXRack0.FX[0] only  A->B")
            print("="*70)
            fd = deep_diff(ra[0], rb[0])
            print_diff(fd, "FXRack0.FX[0]  A->B")

    if "B_BYPASSED" in states and "C_REMOVED" in states:
        diff_bc = deep_diff(states["B_BYPASSED"], states["C_REMOVED"])
        print_diff(diff_bc, "B->C  BYPASSED->REMOVED")

    if "A_ACTIVE" in states and "C_REMOVED" in states:
        diff_ac = deep_diff(states["A_ACTIVE"], states["C_REMOVED"])
        print_diff(diff_ac, "A->C  ACTIVE->REMOVED")

    print("\n" + "="*70)
    print("EXTRACTION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
