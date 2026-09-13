"""Step 16 - Diff all three states.
Loads states A, B, C and performs complete recursive structural diff.
Reports ALL changed paths with values and types.
"""
import pickle, cbor2

def deep_diff(obj_a, obj_b, path="", diff_list=None):
    if diff_list is None:
        diff_list = []
    if type(obj_a) != type(obj_b):
        diff_list.append({"path": path or "ROOT", "change": "TYPE_MISMATCH",
                          "a_type": type(obj_a).__name__, "b_type": type(obj_b).__name__,
                          "a_value": repr(obj_a)[:120], "b_value": repr(obj_b)[:120]})
        return diff_list
    if isinstance(obj_a, dict):
        for key in sorted(set(obj_a.keys()) | set(obj_b.keys())):
            p = f"{path}.{key}" if path else key
            if key not in obj_a:
                diff_list.append({"path": p, "change": "KEY_ADDED_IN_B", "b_value": repr(obj_b[key])[:120]})
            elif key not in obj_b:
                diff_list.append({"path": p, "change": "KEY_REMOVED_IN_B", "a_value": repr(obj_a[key])[:120]})
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
        print(f"\n  {d['path']}")
        print(f"    CHANGE: {d['change']}")
        if "a_type" in d and d["change"] == "TYPE_MISMATCH":
            print(f"    A type: {d['a_type']}  B type: {d['b_type']}")
        if "a_length" in d:
            print(f"    A length: {d['a_length']}  B length: {d['b_length']}")
        if "a_value" in d and d["change"] == "VALUE_CHANGE":
            print(f"    A value ({d.get('a_type','?')}): {repr(d['a_value'])}")
            print(f"    B value ({d.get('b_type','?')}): {repr(d['b_value'])}")
        elif "a_value" in d:
            print(f"    A: {d['a_value']}")
        elif "b_value" in d:
            print(f"    B: {d['b_value']}")

def inspect_fx_slot(state, label):
    print(f"\n--- {label} FXRack0.FX[0] full dump ---")
    rack = state.get("FXRack0", {})
    fx = rack.get("FX", [])
    print(f"  FX array length: {len(fx)}")
    if fx:
        slot = fx[0]
        for k, v in slot.items():
            if isinstance(v, dict):
                print(f"  {k}: dict with keys {sorted(v.keys())}")
                for kk, vv in v.items():
                    print(f"    {kk}: {repr(vv)[:80]}")
            elif isinstance(v, list):
                print(f"  {k}: list len={len(v)}")
                for i, item in enumerate(v):
                    print(f"    [{i}]: {repr(item)[:120]}")
            else:
                print(f"  {k}: {repr(v)[:80]}")

a = pickle.load(open("D:/ableton claude/s16_state_a.pkl", "rb"))["decoded"]
b = pickle.load(open("D:/ableton claude/s16_state_b.pkl", "rb"))["decoded"]
c = pickle.load(open("D:/ableton claude/s16_state_c.pkl", "rb"))["decoded"]

inspect_fx_slot(a, "STATE A (ACTIVE)")
inspect_fx_slot(b, "STATE B (BYPASSED)")
inspect_fx_slot(c, "STATE C (REMOVED)")

diff_ab = deep_diff(a, b)
diff_bc = deep_diff(b, c)
diff_ac = deep_diff(a, c)

print_diff(diff_ab, "A->B  ACTIVE->BYPASSED")
print_diff(diff_bc, "B->C  BYPASSED->REMOVED")
print_diff(diff_ac, "A->C  ACTIVE->REMOVED")

# Focused diff: just FXRack0.FX[0]
ra = a.get("FXRack0", {}).get("FX", [])
rb = b.get("FXRack0", {}).get("FX", [])
if ra and rb:
    print("\n" + "="*70)
    print("FOCUSED: FXRack0.FX[0] only  A->B")
    print("="*70)
    fd = deep_diff(ra[0], rb[0])
    print_diff(fd, "FXRack0.FX[0]  A->B")
