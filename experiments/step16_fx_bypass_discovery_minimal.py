"""
DISCOVERY EXPERIMENT: FX Bypass Mechanism

Objective: Determine exact serialized representation of FX bypass in Serum v8 state.

Protocol:
1. Capture three authoritative Serum v8 states for ONE effect (Distortion):
   A = effect active (normal processing)
   B = effect bypassed via UI (disabled but present)
   C = effect removed (deleted from rack)

2. Perform recursive structural diff on all three states
3. Identify every changed field/path between A↔B and B↔C
4. Repeat for second FX type (Delay) to verify shared representation
5. Report all findings WITHOUT implementing operations

Output: Structured diff showing exact representation of bypass.
"""

import json
import sys
import cbor2
from pathlib import Path

try:
    import dawdreamer as dw
    print("✓ DawDreamer available")
except ImportError:
    print("✗ DawDreamer not available")
    sys.exit(1)


def deep_diff(obj_a, obj_b, path="", diff_list=None):
    """Recursively diff two objects, tracking all changes."""
    if diff_list is None:
        diff_list = []

    # Type check
    if type(obj_a) != type(obj_b):
        diff_list.append({
            "path": path or "root",
            "change": "type_change",
            "a_type": type(obj_a).__name__,
            "b_type": type(obj_b).__name__,
            "a_value": str(obj_a)[:100],
            "b_value": str(obj_b)[:100],
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
                    "change": "key_added_in_b",
                    "b_value": str(obj_b[key])[:100],
                })
            elif key not in obj_b:
                diff_list.append({
                    "path": new_path,
                    "change": "key_removed_in_b",
                    "a_value": str(obj_a[key])[:100],
                })
            else:
                deep_diff(obj_a[key], obj_b[key], new_path, diff_list)
        return diff_list

    # List comparison
    if isinstance(obj_a, list):
        if len(obj_a) != len(obj_b):
            diff_list.append({
                "path": path,
                "change": "length_change",
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
            "change": "value_change",
            "a_value": obj_a,
            "b_value": obj_b,
        })

    return diff_list


def capture_and_decode(synth, label, effect_type=""):
    """Capture Serum v8 state and decode CBOR."""
    print(f"\nCapturing {label}...")
    try:
        state_bytes = synth.plugin.get_state()
        state = cbor2.loads(state_bytes)
        print(f"  ✓ State decoded ({len(state_bytes)} bytes)")
        return state
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def print_fx_rack_summary(state, label):
    """Print summary of FXRack0 structure."""
    if "FXRack0" not in state:
        print(f"\n{label}: No FXRack0 found")
        return

    rack = state["FXRack0"]
    print(f"\n{label}:")
    print(f"  FXRack0.FX length: {len(rack.get('FX', []))}")

    if rack.get("FX") and len(rack["FX"]) > 0:
        fx0 = rack["FX"][0]
        print(f"  FXRack0.FX[0] keys: {sorted(fx0.keys())}")

        # Print plainParams keys if present
        for key in ["type", "plainParams", "flex"]:
            if key in fx0:
                val = fx0[key]
                if key == "type":
                    print(f"    type: {val}")
                elif key == "plainParams":
                    if isinstance(val, dict):
                        print(f"    plainParams keys: {sorted(val.keys())[:10]}...")
                    else:
                        print(f"    plainParams: {type(val).__name__}")
                elif key == "flex":
                    if isinstance(val, list):
                        print(f"    flex: list of {len(val)} elements")
                    else:
                        print(f"    flex: {type(val).__name__}")


def main():
    """Run FX bypass discovery experiment."""
    print("="*70)
    print("FX BYPASS DISCOVERY EXPERIMENT")
    print("="*70)

    try:
        # Initialize DawDreamer
        print("\n1. Initializing DawDreamer...")
        engine = dw.AudioEngine()
        engine.set_sample_rate(44100)
        engine.set_buffer_size(512)

        synth = engine.add_synth("serum", "/Program Files/VstPlugins/Serum_x64.vst3")
        print("   ✓ Serum loaded")

        # Test 1: DISTORTION FX
        print("\n" + "="*70)
        print("TEST 1: DISTORTION FX")
        print("="*70)

        print("\nStep 1: ADD FX DISTORTION to slot 0")
        print("  (Note: DawDreamer UI automation limited; this may fail)")
        print("  Manual step: Open Serum, add Distortion to MAIN rack slot 0")

        print("\nStep 2A: Capturing state A (ACTIVE - manual setup required)")
        print("  → Prerequisite: Distortion loaded and ACTIVE in slot 0")
        state_a_dist = capture_and_decode(synth, "A: DISTORTION ACTIVE")
        if state_a_dist:
            print_fx_rack_summary(state_a_dist, "A: DISTORTION ACTIVE")

        print("\nStep 2B: BYPASS the distortion via Serum UI")
        print("  Manual step: Click the bypass/disable button on Distortion in Serum")
        print("  Then run the readback below...")

        print("\nStep 2C: Capturing state B (BYPASSED)")
        state_b_dist = capture_and_decode(synth, "B: DISTORTION BYPASSED")
        if state_b_dist:
            print_fx_rack_summary(state_b_dist, "B: DISTORTION BYPASSED")

        print("\nStep 2D: REMOVE the distortion from the rack")
        print("  Manual step: Delete/remove Distortion from MAIN rack")

        print("\nStep 2E: Capturing state C (REMOVED)")
        state_c_dist = capture_and_decode(synth, "C: DISTORTION REMOVED")
        if state_c_dist:
            print_fx_rack_summary(state_c_dist, "C: DISTORTION REMOVED")

        # Perform diffs
        if state_a_dist and state_b_dist and state_c_dist:
            print("\n" + "="*70)
            print("STRUCTURAL DIFF: DISTORTION")
            print("="*70)

            diff_ab = deep_diff(state_a_dist, state_b_dist)
            diff_bc = deep_diff(state_b_dist, state_c_dist)
            diff_ac = deep_diff(state_a_dist, state_c_dist)

            print("\nA→B (ACTIVE → BYPASSED):")
            if diff_ab:
                for change in diff_ab:
                    print(f"  {change['path']}: {change['change']}")
                    if 'a_value' in change:
                        print(f"    A: {change.get('a_value', 'N/A')}")
                    if 'b_value' in change:
                        print(f"    B: {change.get('b_value', 'N/A')}")
            else:
                print("  (no changes)")

            print("\nB→C (BYPASSED → REMOVED):")
            if diff_bc:
                for change in diff_bc:
                    print(f"  {change['path']}: {change['change']}")
            else:
                print("  (no changes)")

            print("\nA→C (ACTIVE → REMOVED):")
            if diff_ac:
                for change in diff_ac:
                    print(f"  {change['path']}: {change['change']}")
            else:
                print("  (no changes)")

            # Focus on FX[0]
            print("\n" + "-"*70)
            print("FOCUS: FXRack0.FX[0] comparison")
            print("-"*70)

            if "FXRack0" in state_a_dist and state_a_dist["FXRack0"].get("FX"):
                fx0_a = state_a_dist["FXRack0"]["FX"][0]

                if "FXRack0" in state_b_dist and state_b_dist["FXRack0"].get("FX"):
                    fx0_b = state_b_dist["FXRack0"]["FX"][0]

                    fx_diff = deep_diff(fx0_a, fx0_b)
                    print("\nFXRack0.FX[0] A→B (detailed):")
                    for change in fx_diff:
                        print(f"\n  {change['path']}")
                        print(f"    Type: {change['change']}")
                        if 'a_value' in change and change['a_value'] is not None:
                            av = str(change['a_value'])
                            print(f"    A value: {av[:200]}")
                        if 'b_value' in change and change['b_value'] is not None:
                            bv = str(change['b_value'])
                            print(f"    B value: {bv[:200]}")

        print("\n" + "="*70)
        print("EXPERIMENT COMPLETE")
        print("="*70)
        print("""
NEXT STEPS:
1. Review the diffs above
2. Identify which field(s) change between A↔B
3. Verify that B↔C shows topology changes (array removal)
4. Repeat with DELAY to confirm representation is shared
5. Deliver findings
""")

    except Exception as e:
        print(f"\n✗ Error during experiment: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
