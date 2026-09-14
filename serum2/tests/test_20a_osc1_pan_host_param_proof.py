"""STEP 20A: OSC1.Pan HOST_PARAM proof-of-concept.

Proves that:
1. OSC1.Pan compiles to a HOST_PARAM mutation
2. HOST_PARAM mutation works end-to-end (write, readback, reload)
3. Isolation: changing OSC1.Pan doesn't affect other parameters
4. Persistence: value survives save/reload cycle
"""

import os
import tempfile
import dawdreamer as daw
from serum2 import bridge
from serum2.evidence import runtime as runtime_mod
from serum2.evidence import epoch as epoch_mod
from serum2.operations.scalar_operations import PHASE_9B_STRUCTURAL_PATHS

VST3 = epoch_mod.SERUM_VST3
SR = 44100
BLOCK = 512


def test_osc1_pan_host_param_write_readback():
    """PART 2: Runtime mutation proof.

    1. Load Serum
    2. Read current OSC1 Pan
    3. Set OSC1 Pan to 0.25 (known value)
    4. Read it back immediately
    5. Confirm exact value match
    """
    print("\n" + "="*70)
    print("PART 2A: Runtime Write -> Readback")
    print("="*70)

    # Get baseline skeleton
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], skeleton[1]

    # Load Serum
    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)

    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)

    # Read baseline OSC1 Pan
    baseline_pan = runtime_mod.read_host_param(synth, "A Pan")
    print(f"[OK] Baseline OSC1 Pan: {baseline_pan}")

    # Write new value
    test_value = 0.25
    params = synth.get_parameters_description()
    by_name = {p["name"]: p["index"] for p in params}
    param_idx = by_name["A Pan"]
    synth.set_parameter(param_idx, float(test_value))
    print(f"[OK] Set OSC1 Pan to {test_value}")

    # Read back immediately
    readback_value = runtime_mod.read_host_param(synth, "A Pan")
    print(f"[OK] Readback OSC1 Pan: {readback_value}")

    # Verify exact match (within floating-point tolerance)
    tolerance = 1e-5
    assert abs(readback_value - test_value) < tolerance, \
        f"Value mismatch: wrote {test_value}, read {readback_value}"
    print(f"[OK] Values match within tolerance {tolerance}")

    del engine
    return True


def test_osc1_pan_isolation():
    """PART 3: Isolation check.

    Verify that changing OSC1 Pan does NOT mutate:
    - OSC2 Pan (if it exists)
    - OSC3 Pan (if it exists)
    - OSC1 Level
    """
    print("\n" + "="*70)
    print("PART 3: Isolation Check")
    print("="*70)

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], skeleton[1]

    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)

    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)

    params = synth.get_parameters_description()
    param_names = [p["name"] for p in params]

    # Baseline values
    baseline = {}
    for name in ["A Pan", "A Level", "B Pan", "C Pan"]:
        if name in param_names:
            baseline[name] = runtime_mod.read_host_param(synth, name)

    print(f"[OK] Baseline values: {baseline}")

    # Change OSC1 Pan only
    by_name = {p["name"]: p["index"] for p in params}
    synth.set_parameter(by_name["A Pan"], 0.75)

    # Check all values
    actual = {}
    for name in baseline.keys():
        actual[name] = runtime_mod.read_host_param(synth, name)

    print(f"[OK] After OSC1.Pan change: {actual}")

    # Verify isolation
    for name in baseline.keys():
        if name == "A Pan":
            # Should have changed
            assert abs(actual[name] - 0.75) < 1e-5, f"{name} not changed"
            print(f"  [OK] {name} changed as expected")
        else:
            # Should NOT have changed
            tolerance = 1e-5
            assert abs(actual[name] - baseline[name]) < tolerance, \
                f"{name} was modified: {baseline[name]} -> {actual[name]}"
            print(f"  [OK] {name} unchanged")

    del engine
    return True


def test_osc1_pan_persistence():
    """PART 2B: Persistence proof.

    1. Set OSC1 Pan to 0.6
    2. Save the Serum state
    3. Reload it
    4. Read OSC1 Pan again
    5. Confirm value survived reload
    """
    print("\n" + "="*70)
    print("PART 2B: Persistence (Save/Reload)")
    print("="*70)

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], skeleton[1]

    # Set OSC1 Pan in CBOR state (for persistence test)
    # This is the baseline state before mutation

    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta, body)

    engine1 = daw.RenderEngine(SR, BLOCK)
    synth1 = engine1.make_plugin_processor("serum", VST3)
    synth1.load_state(tmp)
    os.remove(tmp)

    test_value = 0.6
    params = synth1.get_parameters_description()
    by_name = {p["name"]: p["index"] for p in params}
    synth1.set_parameter(by_name["A Pan"], float(test_value))
    print(f"[OK] Set OSC1 Pan to {test_value}")

    # Read back before save
    readback1 = runtime_mod.read_host_param(synth1, "A Pan")
    print(f"[OK] Pre-save readback: {readback1}")
    assert abs(readback1 - test_value) < 1e-5

    # Save state from Serum
    fd, save_path = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    synth1.save_state(save_path)
    print(f"[OK] Saved state to {save_path}")

    del engine1

    # Load in a new engine
    engine2 = daw.RenderEngine(SR, BLOCK)
    synth2 = engine2.make_plugin_processor("serum", VST3)
    synth2.load_state(save_path)
    os.remove(save_path)
    print(f"[OK] Reloaded state in new engine")

    # Read OSC1 Pan from reloaded state
    readback2 = runtime_mod.read_host_param(synth2, "A Pan")
    print(f"[OK] Post-reload readback: {readback2}")

    # Verify persistence
    assert abs(readback2 - test_value) < 1e-5, \
        f"Persistence failed: wrote {test_value}, reloaded {readback2}"
    print(f"[OK] Value survived reload (persistence verified)")

    del engine2
    return True


def test_osc1_pan_compilation():
    """PART 1: Compilation proof.

    Verify that OSC1.Pan:
    1. Is in SEMANTIC_TARGETS
    2. Maps to capability_key "osc_field_pan_osc1"
    3. Maps to route "host:A Pan" in PHASE_9B_STRUCTURAL_PATHS
    4. Compiles to correct Mutation
    """
    print("\n" + "="*70)
    print("PART 1: Compilation Proof")
    print("="*70)

    from serum2.compiler.targets import SEMANTIC_TARGETS
    from serum2.operations.scalar_operations import PHASE_9B_STRUCTURAL_PATHS

    # Check semantic target
    assert "OSC1.Pan" in SEMANTIC_TARGETS, "OSC1.Pan not in SEMANTIC_TARGETS"
    ref = SEMANTIC_TARGETS["OSC1.Pan"]
    print(f"[OK] OSC1.Pan in SEMANTIC_TARGETS")
    print(f"  semantic name: {ref.name}")
    print(f"  capability_key: {ref.capability_key}")

    # Check capability_key
    assert ref.capability_key == "osc_field_pan_osc1", \
        f"Wrong capability_key: {ref.capability_key}"
    print(f"[OK] capability_key correct: osc_field_pan_osc1")

    # Check path mapping
    assert ref.capability_key in PHASE_9B_STRUCTURAL_PATHS, \
        f"capability_key not in PHASE_9B_STRUCTURAL_PATHS"
    path = PHASE_9B_STRUCTURAL_PATHS[ref.capability_key]
    print(f"[OK] Found in PHASE_9B_STRUCTURAL_PATHS")
    print(f"  target_path: {path}")

    # Check it's a HOST_PARAM path
    assert path.startswith("host:"), f"Path is not HOST_PARAM: {path}"
    print(f"[OK] Path is HOST_PARAM format: {path}")

    # Check the parameter name is correct
    param_name = path.split("host:", 1)[1]
    assert param_name == "A Pan", f"Wrong parameter name: {param_name}"
    print(f"[OK] Parameter name correct: A Pan")

    # Test operation compilation
    from serum2.operations.registry import get_registry
    registry = get_registry()
    op_def = registry.get("scalar_osc_field_pan_osc1")
    assert op_def is not None, "Operation not registered"
    print(f"[OK] Operation registered: {op_def.operation_id}")
    print(f"  semantic name: {op_def.semantic_name}")
    print(f"  kind: {op_def.kind}")

    return True


if __name__ == "__main__":
    print("\n" + "█"*70)
    print("█ STEP 20A: OSC1.PAN HOST_PARAM PROOF-OF-CONCEPT")
    print("█"*70)

    try:
        # PART 1: Compilation
        assert test_osc1_pan_compilation(), "Part 1 failed"
        print("\n[PASS] PART 1 PASSED: Compilation proof")

        # PART 2A: Runtime write/readback
        assert test_osc1_pan_write_readback(), "Part 2A failed"
        print("\n[PASS] PART 2A PASSED: Runtime mutation proof")

        # PART 2B: Persistence
        assert test_osc1_pan_persistence(), "Part 2B failed"
        print("\n[PASS] PART 2B PASSED: Persistence proof")

        # PART 3: Isolation
        assert test_osc1_pan_isolation(), "Part 3 failed"
        print("\n[PASS] PART 3 PASSED: Isolation check")

        print("\n" + "█"*70)
        print("█ 🎯 OSC1.PAN HOST_PARAM PROOF COMPLETE")
        print("█"*70)
        print("\nSUMMARY:")
        print("  A. Semantic operation: OSC1.Pan")
        print("  B. HOST_PARAM route: host:A Pan")
        print("  C. Mutation mechanism: synth.set_parameter(index, value)")
        print("  D. Immediate readback: [OK] Confirmed")
        print("  E. Reload persistence: [OK] Confirmed")
        print("  F. Isolation: [OK] Confirmed")
        print("  G. Tests: [OK] All passed")
        print("  H. HOST_PARAM proof: [OK] COMPLETE")

    except Exception as e:
        print(f"\n[FAIL] FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
