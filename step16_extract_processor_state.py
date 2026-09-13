"""
Step 16 - Extract ProcessorState from Ableton .als files and diff them.

Ableton Live 12 stores VST3 plugin state in:
  PluginDevice > PluginDesc > Vst3PluginInfo > Preset > Vst3Preset > ProcessorState (text = hex or base64)
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
    decompressed = zstd.ZstdDecompressor().stream_reader(tail[8:]).read()
    body = cbor2.loads(decompressed)
    return meta, body


def try_decode(raw: bytes):
    """Try to decode raw bytes as XferJson, then raw CBOR."""
    if raw[:8] == MAGIC:
        return decode_xferjson(raw)
    # Try raw CBOR
    body = cbor2.loads(raw)
    return None, body


def find_serum_processor_state(als_path: str):
    """Extract Serum VST3 ProcessorState from .als file."""
    with gzip.open(als_path, 'rb') as f:
        xml_data = f.read()

    root = ET.fromstring(xml_data)

    # Find all Vst3Preset elements that are inside a Serum PluginDevice
    # Path: PluginDevice > PluginDesc > Vst3PluginInfo[@Name='Serum 2'] > Preset > Vst3Preset > ProcessorState

    results = []
    for vst3_info in root.iter('Vst3PluginInfo'):
        name_elem = vst3_info.find('Name')
        name = name_elem.get('Value', '') if name_elem is not None else ''
        if 'Serum' not in name and 'serum' not in name.lower():
            continue

        print(f"  Found Vst3PluginInfo Name={name!r}")

        # Look for Preset > Vst3Preset > ProcessorState
        for preset in vst3_info.iter('Preset'):
            for vst3preset in preset.iter('Vst3Preset'):
                proc_state = vst3preset.find('ProcessorState')
                ctrl_state = vst3preset.find('ControllerState')

                if proc_state is not None:
                    text = (proc_state.text or '').strip()
                    print(f"  ProcessorState: {len(text)} chars, first 40: {text[:40]!r}")
                    results.append(('ProcessorState', text))

                if ctrl_state is not None:
                    text = (ctrl_state.text or '').strip()
                    print(f"  ControllerState: {len(text)} chars, first 40: {text[:40]!r}")

    return results


def decode_processor_state(hex_text: str):
    """Decode ProcessorState hex string -> raw bytes, then try XferJson/CBOR."""
    # It might be hex-encoded
    raw = bytes.fromhex(hex_text)
    print(f"  Decoded hex -> {len(raw)} bytes, magic: {raw[:8]!r}")
    return raw


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
    else:
        print(f"  (FX slot {slot_idx} not present)")


def main():
    print("="*70)
    print("STEP 16: SERUM FX BYPASS DISCOVERY")
    print("Extracting plugin states via ProcessorState from Ableton .als files")
    print("="*70)

    states = {}
    for label, als_path in ALS_FILES.items():
        print(f"\n[{label}] Loading: {Path(als_path).name}")
        if not Path(als_path).exists():
            print(f"  ERROR: File not found: {als_path}")
            continue

        results = find_serum_processor_state(als_path)
        if not results:
            print(f"  ERROR: No Serum ProcessorState found")
            continue

        # Use first ProcessorState result
        kind, hex_text = results[0]
        if not hex_text:
            print(f"  ERROR: ProcessorState is empty")
            continue

        try:
            raw = decode_processor_state(hex_text)
        except ValueError as e:
            # Maybe it's base64?
            import base64
            try:
                raw = base64.b64decode(hex_text)
                print(f"  Decoded base64 -> {len(raw)} bytes, magic: {raw[:8]!r}")
            except Exception as e2:
                print(f"  ERROR: Could not decode: hex={e}, b64={e2}")
                continue

        try:
            meta, body = try_decode(raw)
            if meta:
                print(f"  XferJson decoded OK. Top-level keys: {sorted(body.keys())[:10]}")
            else:
                print(f"  Raw CBOR decoded OK. Top-level keys: {sorted(body.keys())[:10]}")
            states[label] = body
        except Exception as e:
            print(f"  ERROR decoding: {e}")
            print(f"  Raw bytes (first 40): {raw[:40]!r}")

    if len(states) < 2:
        print(f"\nERROR: Need at least 2 states for comparison. Got {len(states)}. Aborting.")
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
