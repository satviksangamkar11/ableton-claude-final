"""
STEP 16 EXECUTION: FX Bypass Authoritative Discovery

Capture three real Serum v8 states and perform recursive structural diff
to identify exact serialized changes for FX bypass.

No hypotheses. Only captured evidence.
"""

import json
import sys
from pathlib import Path

try:
    import cbor2
    print("[OK] cbor2 available")
except ImportError:
    print("[FAIL] cbor2 not available")
    sys.exit(1)

try:
    import dawdreamer as dw
    print("[OK] DawDreamer available")
except ImportError:
    print("[FAIL] DawDreamer not available")
    sys.exit(1)


def deep_diff(obj_a, obj_b, path="", diff_list=None):
    """Recursively diff two objects, reporting ALL changes."""
    if diff_list is None:
        diff_list = []

    # Type mismatch
    if type(obj_a) != type(obj_b):
        diff_list.append({
            "path": path or "ROOT",
            "change": "TYPE_MISMATCH",
            "a_type": type(obj_a).__name__,
            "b_type": type(obj_b).__name__,
        })
        return diff_list

    # Dict comparison
    if isinstance(obj_a, dict):
        all_keys = set(obj_a.keys()) | set(obj_b.keys())
        for key in sorted(all_keys):
            new_path = f"{path}.{key}" if path else key
            if key not in obj_a:
                diff_list.append({
                    "path": new_path,
                    "change": "KEY_ADDED_IN_B",
                })
            elif key not in obj_b:
                diff_list.append({
                    "path": new_path,
                    "change": "KEY_REMOVED_IN_B",
                })
            else:
                deep_diff(obj_a[key], obj_b[key], new_path, diff_list)
        return diff_list

    # List comparison
    if isinstance(obj_a, list):
        if len(obj_a) != len(obj_b):
            diff_list.append({
                "path": path,
                "change": "ARRAY_LENGTH",
                "a_length": len(obj_a),
                "b_length": len(obj_b),
            })
        for i in range(min(len(obj_a), len(obj_b))):
            new_path = f"{path}[{i}]"
            deep_diff(obj_a[i], obj_b[i], new_path, diff_list)
        return diff_list

    # Scalar comparison
    if obj_a != obj_b:
        diff_list.append({
            "path": path,
            "change": "VALUE_CHANGE",
            "a_value": obj_a,
            "b_value": obj_b,
            "a_type": type(obj_a).__name__,
            "b_type": type(obj_b).__name__,
        })

    return diff_list


def print_fx_summary(state, label):
    """Print summary of FXRack0 for verification."""
    if "FXRack0" not in state:
        print(f"{label}: NO FXRack0")
        return False

    rack = state["FXRack0"]
    fx_array = rack.get("FX", [])
    print(f"{label}:")
    print(f"  FXRack0.FX length: {len(fx_array)}")

    if fx_array:
        for i, fx in enumerate(fx_array):
            print(f"  FXRack0.FX[{i}]:")
            print(f"    keys: {list(fx.keys())}")
            if "type" in fx:
                print(f"    type: {fx['type']}")
            if "plainParams" in fx and isinstance(fx["plainParams"], dict):
                param_keys = sorted(fx["plainParams"].keys())
                print(f"    plainParams keys ({len(param_keys)}): {param_keys[:5]}...")
            if "flex" in fx:
                if isinstance(fx["flex"], list):
                    print(f"    flex: list of {len(fx['flex'])} elements")
                    if fx["flex"]:
                        print(f"      flex[0] keys: {list(fx['flex'][0].keys()) if isinstance(fx['flex'][0], dict) else type(fx['flex'][0])}")
                else:
                    print(f"    flex: {type(fx['flex']).__name__}")
    return True


def main():
    print("="*80)
    print("STEP 16: FX BYPASS DISCOVERY EXECUTION")
    print("="*80)

    # Initialize DawDreamer
    try:
        engine = dw.RenderEngine(44100, 512)

        # Try multiple possible paths
        serum_paths = [
            "C:/Program Files/Common Files/VST3/Serum2.vst3/Contents/x86_64-win/Serum2.vst3",
            "/Program Files/Common Files/VST3/Serum2.vst3/Contents/x86_64-win/Serum2.vst3",
            "/c/Program Files/Common Files/VST3/Serum2.vst3/Contents/x86_64-win/Serum2.vst3",
        ]

        synth = None
        for path in serum_paths:
            try:
                synth = engine.make_plugin_processor("serum", path)
                print(f"\n[OK] Serum VST3 loaded from: {path}")
                break
            except:
                continue

        if not synth:
            print("[FAIL] Could not find Serum VST3 at any known path")
            sys.exit(1)

    except Exception as e:
        print(f"\n[FAIL] Error loading Serum: {e}")
        sys.exit(1)

    # PART 1: DISTORTION
    print("\n" + "="*80)
    print("PART 1: DISTORTION FX")
    print("="*80)

    print("\nMANUAL STEP: Add FXDistortion to MAIN rack (slot 0), leave ACTIVE")
    print("Press ENTER when done...")
    input()

    print("\nCapturing STATE A (DISTORTION ACTIVE)...")
    try:
        state_a_bytes = synth.get_state()
        state_a = cbor2.loads(state_a_bytes)
        print(f"[OK] Captured ({len(state_a_bytes)} bytes)")
        if not print_fx_summary(state_a, "A: DISTORTION ACTIVE"):
            print("ERROR: FXRack0 not found or no FX")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Failed to capture state A: {e}")
        sys.exit(1)

    print("\nMANUAL STEP: Bypass the Distortion via Serum UI (click bypass button)")
    print("Verify it shows as bypassed/disabled in the UI")
    print("Press ENTER when done...")
    input()

    print("\nCapturing STATE B (DISTORTION BYPASSED)...")
    try:
        state_b_bytes = synth.get_state()
        state_b = cbor2.loads(state_b_bytes)
        print(f"[OK] Captured ({len(state_b_bytes)} bytes)")
        if not print_fx_summary(state_b, "B: DISTORTION BYPASSED"):
            print("ERROR: FXRack0 not found or FX was removed")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Failed to capture state B: {e}")
        sys.exit(1)

    print("\nMANUAL STEP: Remove the Distortion from MAIN rack")
    print("Press ENTER when done...")
    input()

    print("\nCapturing STATE C (DISTORTION REMOVED)...")
    try:
        state_c_bytes = synth.get_state()
        state_c = cbor2.loads(state_c_bytes)
        print(f"[OK] Captured ({len(state_c_bytes)} bytes)")
        print_fx_summary(state_c, "C: DISTORTION REMOVED")
    except Exception as e:
        print(f"[FAIL] Failed to capture state C: {e}")
        sys.exit(1)

    # Diff Part 1
    print("\n" + "-"*80)
    print("DISTORTION DIFFS")
    print("-"*80)

    diff_ab = deep_diff(state_a, state_b)
    print(f"\nA -> B (ACTIVE -> BYPASSED): {len(diff_ab)} changes")
    for change in sorted(diff_ab, key=lambda x: x["path"]):
        print(f"  {change['path']}")
        print(f"    {change['change']}")
        if "a_value" in change:
            print(f"    A: {change['a_value']}")
        if "b_value" in change:
            print(f"    B: {change['b_value']}")

    diff_bc = deep_diff(state_b, state_c)
    print(f"\nB -> C (BYPASSED -> REMOVED): {len(diff_bc)} changes")
    for change in sorted(diff_bc, key=lambda x: x["path"]):
        if "ARRAY" in change.get("change", ""):
            print(f"  {change['path']}: {change['change']} ({change.get('a_length')} -> {change.get('b_length')})")
        else:
            print(f"  {change['path']}: {change['change']}")

    # Focus on FXRack0.FX[0]
    print("\n" + "-"*80)
    print("FOCUSED: FXRack0.FX[0] ONLY (A vs B)")
    print("-"*80)

    if ("FXRack0" in state_a and state_a["FXRack0"].get("FX") and
        "FXRack0" in state_b and state_b["FXRack0"].get("FX")):

        fx0_a = state_a["FXRack0"]["FX"][0]
        fx0_b = state_b["FXRack0"]["FX"][0]

        fx_diff = deep_diff(fx0_a, fx0_b)
        print(f"\n{len(fx_diff)} changed fields:")
        for change in sorted(fx_diff, key=lambda x: x["path"]):
            print(f"\n  {change['path']}")
            if change.get("change") == "VALUE_CHANGE":
                print(f"    TYPE: {change.get('a_type')} -> {change.get('b_type')}")
                print(f"    A: {repr(change.get('a_value'))}")
                print(f"    B: {repr(change.get('b_value'))}")
            else:
                print(f"    {change['change']}")

    # PART 2: DELAY (Validation)
    print("\n" + "="*80)
    print("PART 2: DELAY FX (Validation)")
    print("="*80)

    print("\nMANUAL STEP: Remove Distortion if present, add FXDelay to MAIN rack (slot 0), leave ACTIVE")
    print("Press ENTER when done...")
    input()

    print("\nCapturing STATE A2 (DELAY ACTIVE)...")
    try:
        state_a2_bytes = synth.get_state()
        state_a2 = cbor2.loads(state_a2_bytes)
        print(f"[OK] Captured ({len(state_a2_bytes)} bytes)")
        if not print_fx_summary(state_a2, "A2: DELAY ACTIVE"):
            print("ERROR: FXRack0 not found or no FX")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Failed to capture state A2: {e}")
        sys.exit(1)

    print("\nMANUAL STEP: Bypass the Delay via Serum UI")
    print("Press ENTER when done...")
    input()

    print("\nCapturing STATE B2 (DELAY BYPASSED)...")
    try:
        state_b2_bytes = synth.get_state()
        state_b2 = cbor2.loads(state_b2_bytes)
        print(f"[OK] Captured ({len(state_b2_bytes)} bytes)")
        if not print_fx_summary(state_b2, "B2: DELAY BYPASSED"):
            print("ERROR: FXRack0 not found or FX was removed")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Failed to capture state B2: {e}")
        sys.exit(1)

    # Diff Part 2
    print("\n" + "-"*80)
    print("DELAY DIFFS")
    print("-"*80)

    diff_a2b2 = deep_diff(state_a2, state_b2)
    print(f"\nA2 -> B2 (ACTIVE -> BYPASSED): {len(diff_a2b2)} changes")
    for change in sorted(diff_a2b2, key=lambda x: x["path"]):
        print(f"  {change['path']}")
        print(f"    {change['change']}")
        if "a_value" in change:
            print(f"    A: {change['a_value']}")
        if "b_value" in change:
            print(f"    B: {change['b_value']}")

    # Focused Delay comparison
    print("\n" + "-"*80)
    print("FOCUSED: FXRack0.FX[0] ONLY (A2 vs B2)")
    print("-"*80)

    if ("FXRack0" in state_a2 and state_a2["FXRack0"].get("FX") and
        "FXRack0" in state_b2 and state_b2["FXRack0"].get("FX")):

        fx0_a2 = state_a2["FXRack0"]["FX"][0]
        fx0_b2 = state_b2["FXRack0"]["FX"][0]

        fx_diff_2 = deep_diff(fx0_a2, fx0_b2)
        print(f"\n{len(fx_diff_2)} changed fields:")
        for change in sorted(fx_diff_2, key=lambda x: x["path"]):
            print(f"\n  {change['path']}")
            if change.get("change") == "VALUE_CHANGE":
                print(f"    TYPE: {change.get('a_type')} -> {change.get('b_type')}")
                print(f"    A: {repr(change.get('a_value'))}")
                print(f"    B: {repr(change.get('b_value'))}")
            else:
                print(f"    {change['change']}")

        # CONSISTENCY CHECK
        print("\n" + "="*80)
        print("CONSISTENCY CHECK: Distortion vs Delay")
        print("="*80)

        # Extract changed field paths from both
        dist_changed_paths = {c["path"] for c in fx_diff if c.get("change") == "VALUE_CHANGE"}
        delay_changed_paths = {c["path"] for c in fx_diff_2 if c.get("change") == "VALUE_CHANGE"}

        print(f"\nDistortion A->B changed fields: {dist_changed_paths}")
        print(f"Delay A2->B2 changed fields: {delay_changed_paths}")

        if dist_changed_paths == delay_changed_paths:
            print("[OK] SAME FIELDS CHANGED: Bypass mechanism is shared across FX types")
        else:
            common = dist_changed_paths & delay_changed_paths
            only_dist = dist_changed_paths - delay_changed_paths
            only_delay = delay_changed_paths - dist_changed_paths
            if common:
                print(f"[WARN] PARTIAL MATCH: Common changed fields: {common}")
                if only_dist:
                    print(f"   Only in Distortion: {only_dist}")
                if only_delay:
                    print(f"   Only in Delay: {only_delay}")
            else:
                print("[FAIL] NO COMMON FIELDS: Mechanisms differ (unexpected)")

    print("\n" + "="*80)
    print("DISCOVERY EXECUTION COMPLETE")
    print("="*80)
    print("\nStep 16 findings captured. Ready for analysis.")


if __name__ == "__main__":
    main()
