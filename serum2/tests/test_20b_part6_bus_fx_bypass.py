"""STEP 20B PART 6: Bus FX bypass - discovery and regression suite.

FINDING (rigorous negative evidence): Serum 2.0.21 has NO distinct
"bus-level FX bypass" persistent representation, separate from bypassing
each FX module individually.

Evidence gathered:
  1. Real Serum UI search found no dedicated bus-bypass control:
     - FX page tab right-click menu: Cut/Copy/Paste/Clear FX Bus, Lock FX
       Bus, Lock All Busses, Load/Save FX Bus, Add FX Module - no bypass.
     - MIX page BUS1/BUS2/MAIN headers have no checkbox or mute button
       (unlike oscillator channels, which do).
     - No context-menu bypass option on tabs, FX module names, or the
       Bus N Vol fader (right-click there: only Reset/MIDI Learn/Lock).
     - Top MENU (About/Init/Load/Save/etc.) has no bypass entry.
     - Alt-click on one module's bypass icon only toggles that module
       (BODE alone went gray; CHORUS stayed active) - no bus-wide action.
  2. No VST3 HOST_PARAM exists for it: searched all 2623 parameters for
     "bus"+"enable"/"bypass"/"active", zero matches. The only "Bus 1"-
     named params are "Bus 1 Vol" and 16 generic "FX Bus 1 Param N"
     placeholders.
  3. CBOR structure: FXRack{N}.plainParams.kParamEnable is NOT a genuine
     recognized field. Setting it via pathmerge and round-tripping through
     a REAL DawDreamer save/reload silently discards it back to "default"
     - confirmed on FXRack0 (MAIN), FXRack1 (BUS1), FXRack2 (BUS2) alike.
     A sanity check on the SAME round-trip mechanism applied to an
     INDIVIDUAL FX module's plainParams.kParamEnable preserves it exactly,
     ruling out a bridge/skeleton artifact as the explanation.

CONCLUSION: "bus bypass" != a distinct persistent flag. It is implemented
as a COMPOUND operation: the proven individual-FX bypass mutation
(plainParams -> {"kParamEnable": 0.0}) applied to every FX module currently
present in the bus's rack, in one operation (bypass_bus/unbypass_bus in
fx_structural_operations.py). This is explicitly NOT the same as REMOVE
(which changes rack topology/array length) and NOT the same as bypassing
only one of several modules (individual bypass remains independently
addressable via the pre-existing per-slot mechanism).

NOTE: bypass_bus/unbypass_bus resolve the FX-type key directly from state
rather than using the "*" wildcard in the older bypass_effect()/
unbypass_effect() - pathmerge.apply_path_value has no wildcard resolution,
so that "*" would write a literal garbage key if ever executed. See the
spawned follow-up task for auditing/fixing bypass_effect/unbypass_effect.
"""
import copy
from serum2.operations.fx_structural_operations import (
    FXStructuralCompiler,
    Bus,
    _resolve_fx_type_key,
)
from serum2.operations.model import (
    SerumOperation,
    OperationKind,
    OperationContext,
)
from serum2 import pathmerge


def make_two_fx_body(rack_key="FXRack1"):
    """A minimal body with two real FX modules (Bode type=10, Chorus
    type=3) in one rack, matching the real preset structure decoded from
    BUSBYPASSSTATEA.SerumPreset."""
    return {
        rack_key: {
            "FX": [
                {"type": 10, "FXBode": {"plainParams": "default"}},
                {"type": 3, "FXChorus": {"lfophasor": 0.0, "plainParams": "default"}},
            ],
            "plainParams": "default",
        }
    }


def make_operation(op_id):
    return SerumOperation(operation_id=op_id, semantic_name=op_id, kind=OperationKind.TOPOLOGY, parameters=[])


# ---------------------------------------------------------------------------
# Negative evidence regression: FXRack.plainParams.kParamEnable is NOT
# preserved (this is the finding that rules out a distinct bus-level flag).
# ---------------------------------------------------------------------------

def test_rack_level_kparam_enable_is_not_a_real_field():
    """Directly documents the discriminating evidence: pathmerge accepts
    the mutation (no crash), but this is a synthetic-body check, not proof
    of Serum's own behavior - the REAL proof is the DawDreamer round-trip
    performed during discovery (see module docstring). This test guards
    that our own compound implementation never accidentally routes through
    FXRack.plainParams.kParamEnable instead of per-module mutations."""
    compiler = FXStructuralCompiler()
    body = make_two_fx_body()
    ctx = OperationContext(body=body)
    op = make_operation("fx_struct_bypass_bus_BUS1")

    result = compiler.bypass_bus(op, ctx, Bus.BUS1)

    for m in result.compiled_mutations:
        assert "plainParams.kParamEnable" not in m.target_path or ".FX." in m.target_path, \
            f"Mutation should target a per-slot plainParams, not the rack-level field: {m.target_path}"
        assert m.target_path != "FXRack1.plainParams", \
            "bypass_bus must not mutate FXRack.plainParams directly (proven non-functional)"
    print("[PASS] bypass_bus never targets the non-functional FXRack.plainParams.kParamEnable")


# ---------------------------------------------------------------------------
# BUS1 bypass: compiles correct per-slot mutations, preserving topology
# ---------------------------------------------------------------------------

def test_bus1_bypass_compiles_per_slot_mutations():
    compiler = FXStructuralCompiler()
    body = make_two_fx_body("FXRack1")
    ctx = OperationContext(body=body)
    op = make_operation("fx_struct_bypass_bus_BUS1")

    result = compiler.bypass_bus(op, ctx, Bus.BUS1)

    assert result.success
    assert len(result.compiled_mutations) == 2
    paths = {m.target_path for m in result.compiled_mutations}
    assert "FXRack1.FX.0.FXBode.plainParams" in paths
    assert "FXRack1.FX.1.FXChorus.plainParams" in paths
    for m in result.compiled_mutations:
        assert m.value == {"kParamEnable": 0.0}
    print("[PASS] BUS1 bypass compiles exactly 2 correct per-slot mutations")


def test_bus1_bypass_applies_and_preserves_array():
    """Bus bypass preserves FX array: both modules remain in the rack,
    correct order, correct types, only plainParams changed."""
    compiler = FXStructuralCompiler()
    body = make_two_fx_body("FXRack1")
    original_fx = copy.deepcopy(body["FXRack1"]["FX"])
    ctx = OperationContext(body=body)
    op = make_operation("fx_struct_bypass_bus_BUS1")

    result = compiler.bypass_bus(op, ctx, Bus.BUS1)
    for m in result.compiled_mutations:
        pathmerge.apply_path_value(body, m.target_path, m.value)

    fx = body["FXRack1"]["FX"]
    assert len(fx) == len(original_fx), "bus bypass must not remove modules (array length unchanged)"
    assert fx[0]["type"] == original_fx[0]["type"] == 10, "module order/type preserved (slot 0 = Bode)"
    assert fx[1]["type"] == original_fx[1]["type"] == 3, "module order/type preserved (slot 1 = Chorus)"
    assert fx[0]["FXBode"]["plainParams"] == {"kParamEnable": 0.0}
    assert fx[1]["FXChorus"]["plainParams"] == {"kParamEnable": 0.0}
    assert fx[1]["FXChorus"]["lfophasor"] == 0.0, "unrelated FX-internal state preserved"
    print("[PASS] BUS1 bypass preserves rack topology/order/types; only plainParams changed")


# ---------------------------------------------------------------------------
# BUS2: genericity proven independently, not assumed identical to BUS1
# ---------------------------------------------------------------------------

def test_bus2_bypass_uses_correct_rack():
    compiler = FXStructuralCompiler()
    body = make_two_fx_body("FXRack2")
    ctx = OperationContext(body=body)
    op = make_operation("fx_struct_bypass_bus_BUS2")

    result = compiler.bypass_bus(op, ctx, Bus.BUS2)

    paths = {m.target_path for m in result.compiled_mutations}
    assert "FXRack2.FX.0.FXBode.plainParams" in paths
    assert "FXRack2.FX.1.FXChorus.plainParams" in paths
    assert not any(p.startswith("FXRack1") for p in paths), "BUS2 bypass must not touch FXRack1"
    print("[PASS] BUS2 bypass targets FXRack2 correctly, independent of BUS1")


def test_main_bypass_uses_correct_rack():
    """MAIN's rack (FXRack0) must not be assumed identical without evidence
    - verified same compound mechanism applies (no bus-specific special
    case was found for MAIN in the negative-evidence sweep)."""
    compiler = FXStructuralCompiler()
    body = make_two_fx_body("FXRack0")
    ctx = OperationContext(body=body)
    op = make_operation("fx_struct_bypass_bus_MAIN")

    result = compiler.bypass_bus(op, ctx, Bus.MAIN)

    paths = {m.target_path for m in result.compiled_mutations}
    assert "FXRack0.FX.0.FXBode.plainParams" in paths
    assert "FXRack0.FX.1.FXChorus.plainParams" in paths
    print("[PASS] MAIN bypass targets FXRack0 correctly")


# ---------------------------------------------------------------------------
# Sibling isolation: bypassing one bus does not touch another bus's rack,
# and does not silently change individual module bypass state beyond the
# intended compound effect.
# ---------------------------------------------------------------------------

def test_unrelated_bus_remains_unchanged():
    compiler = FXStructuralCompiler()
    body = make_two_fx_body("FXRack1")
    body.update(make_two_fx_body("FXRack2"))
    before_rack2 = copy.deepcopy(body["FXRack2"])

    ctx = OperationContext(body=body)
    op = make_operation("fx_struct_bypass_bus_BUS1")
    result = compiler.bypass_bus(op, ctx, Bus.BUS1)
    for m in result.compiled_mutations:
        pathmerge.apply_path_value(body, m.target_path, m.value)

    assert body["FXRack2"] == before_rack2, "BUS1 bypass leaked into BUS2's rack!"
    print("[PASS] Bypassing BUS1 leaves BUS2's rack completely unchanged")


# ---------------------------------------------------------------------------
# States A/B/C/D distinction (PART 3 of the task)
# ---------------------------------------------------------------------------

def test_state_a_vs_b_bus_bypass_vs_active():
    """A: FX1 active, FX2 active. B: bus bypassed (both individually
    bypassed via the compound operation) - both modules remain present."""
    compiler = FXStructuralCompiler()

    # State A
    body_a = make_two_fx_body("FXRack1")

    # State B: apply bus bypass
    body_b = copy.deepcopy(body_a)
    ctx_b = OperationContext(body=body_b)
    op = make_operation("fx_struct_bypass_bus_BUS1")
    result = compiler.bypass_bus(op, ctx_b, Bus.BUS1)
    for m in result.compiled_mutations:
        pathmerge.apply_path_value(body_b, m.target_path, m.value)

    assert body_a["FXRack1"]["FX"][0]["FXBode"]["plainParams"] == "default"
    assert body_a["FXRack1"]["FX"][1]["FXChorus"]["plainParams"] == "default"
    assert body_b["FXRack1"]["FX"][0]["FXBode"]["plainParams"] == {"kParamEnable": 0.0}
    assert body_b["FXRack1"]["FX"][1]["FXChorus"]["plainParams"] == {"kParamEnable": 0.0}
    assert len(body_a["FXRack1"]["FX"]) == len(body_b["FXRack1"]["FX"]) == 2, \
        "State B keeps both FX modules in the rack (bus bypass != remove)"
    print("[PASS] State A (active) vs State B (bus bypassed): both modules present, "
          "only plainParams differ")


def test_state_c_individual_bypass_differs_from_state_b():
    """C: FX1 bypassed only, FX2 active, bus 'active' (no bus-wide action
    taken). Distinguishes individual bypass from the bus-bypass compound."""
    compiler = FXStructuralCompiler()
    body_c = make_two_fx_body("FXRack1")

    # Individually bypass ONLY slot 0 (FX1), leaving FX2 untouched -
    # using the same proven mutation shape, applied to one slot.
    pathmerge.apply_path_value(body_c, "FXRack1.FX.0.FXBode.plainParams", {"kParamEnable": 0.0})

    assert body_c["FXRack1"]["FX"][0]["FXBode"]["plainParams"] == {"kParamEnable": 0.0}
    assert body_c["FXRack1"]["FX"][1]["FXChorus"]["plainParams"] == "default", \
        "State C: FX2 must remain fully active while only FX1 is bypassed"
    print("[PASS] State C (individual bypass of FX1 only) leaves FX2 active - "
          "proves individual bypass is independently addressable from bus bypass")


def test_state_d_remove_differs_from_bypass():
    """D: FX1 removed (topology change - array shrinks), FX2 active, bus
    active. Distinguishes REMOVE from both bypass forms."""
    body_d = make_two_fx_body("FXRack1")

    # Remove FX1 (slot 0) entirely - array shrinks, unlike bypass which
    # preserves array length.
    del body_d["FXRack1"]["FX"][0]

    assert len(body_d["FXRack1"]["FX"]) == 1, "State D: array must shrink (topology change)"
    assert body_d["FXRack1"]["FX"][0]["type"] == 3, "remaining module is Chorus (was slot 1)"

    # Contrast: bypass (State B) NEVER shrinks the array.
    body_b = make_two_fx_body("FXRack1")
    compiler = FXStructuralCompiler()
    ctx_b = OperationContext(body=body_b)
    op = make_operation("fx_struct_bypass_bus_BUS1")
    result = compiler.bypass_bus(op, ctx_b, Bus.BUS1)
    for m in result.compiled_mutations:
        pathmerge.apply_path_value(body_b, m.target_path, m.value)

    assert len(body_b["FXRack1"]["FX"]) == 2, "bypass (State B) must NOT shrink the array"
    print("[PASS] State D (remove, array shrinks) is structurally distinct from "
          "State B (bypass, array length preserved)")


# ---------------------------------------------------------------------------
# Toggle back: unbypass restores active state
# ---------------------------------------------------------------------------

def test_unbypass_bus_restores_active_state():
    compiler = FXStructuralCompiler()
    body = make_two_fx_body("FXRack1")

    ctx = OperationContext(body=body)
    bypass_op = make_operation("fx_struct_bypass_bus_BUS1")
    result = compiler.bypass_bus(bypass_op, ctx, Bus.BUS1)
    for m in result.compiled_mutations:
        pathmerge.apply_path_value(body, m.target_path, m.value)

    assert body["FXRack1"]["FX"][0]["FXBode"]["plainParams"] == {"kParamEnable": 0.0}

    ctx2 = OperationContext(body=body)
    unbypass_op = make_operation("fx_struct_unbypass_bus_BUS1")
    result2 = compiler.unbypass_bus(unbypass_op, ctx2, Bus.BUS1)
    for m in result2.compiled_mutations:
        pathmerge.apply_path_value(body, m.target_path, m.value)

    assert body["FXRack1"]["FX"][0]["FXBode"]["plainParams"] == "default"
    assert body["FXRack1"]["FX"][1]["FXChorus"]["plainParams"] == "default"
    print("[PASS] unbypass_bus restores both modules to active ('default') state")


# ---------------------------------------------------------------------------
# Empty rack / malformed slot handling
# ---------------------------------------------------------------------------

def test_bypass_bus_on_empty_rack_is_a_no_op():
    compiler = FXStructuralCompiler()
    body = {"FXRack1": {"FX": [], "plainParams": "default"}}
    ctx = OperationContext(body=body)
    op = make_operation("fx_struct_bypass_bus_BUS1")

    result = compiler.bypass_bus(op, ctx, Bus.BUS1)
    assert result.success
    assert result.compiled_mutations == []
    print("[PASS] Bypassing an empty bus rack is a safe no-op")


def test_resolve_fx_type_key_helper():
    assert _resolve_fx_type_key({"type": 10, "FXBode": {}}) == "FXBode"
    assert _resolve_fx_type_key({"type": 3, "FXChorus": {}}) == "FXChorus"
    assert _resolve_fx_type_key({"type": -1}) is None
    print("[PASS] _resolve_fx_type_key correctly identifies the FX-type sibling key")


if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# STEP 20B PART 6: BUS FX BYPASS — REGRESSION SUITE")
    print("#" * 70)

    tests = [
        test_rack_level_kparam_enable_is_not_a_real_field,
        test_bus1_bypass_compiles_per_slot_mutations,
        test_bus1_bypass_applies_and_preserves_array,
        test_bus2_bypass_uses_correct_rack,
        test_main_bypass_uses_correct_rack,
        test_unrelated_bus_remains_unchanged,
        test_state_a_vs_b_bus_bypass_vs_active,
        test_state_c_individual_bypass_differs_from_state_b,
        test_state_d_remove_differs_from_bypass,
        test_unbypass_bus_restores_active_state,
        test_bypass_bus_on_empty_rack_is_a_no_op,
        test_resolve_fx_type_key_helper,
    ]

    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"[FAILED] {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {t.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "#" * 70)
    if failed == 0:
        print(f"# ALL {len(tests)} TESTS PASSED")
    else:
        print(f"# {failed}/{len(tests)} TESTS FAILED")
    print("#" * 70)

    if failed:
        exit(1)
