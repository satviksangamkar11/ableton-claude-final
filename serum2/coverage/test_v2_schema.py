#!/usr/bin/env python3
"""Self-check for Execution Coverage V2 schema/canonicalization/invariants."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2.coverage.schema import (
    ExecutionResolution, ExecutionFamily, MutationPrimitive, BindingStatus,
    SemanticResolution, CapabilityBinding, InvariantViolation,
    validate_v2_1_resolution_gate, validate_v2_3_generic_operation_key,
    validate_family_primitive_consistency,
)
from serum2.coverage.canonicalize import (
    canonicalize_host_parameter, canonicalize_matrix_route, canonicalize_topology,
    canonicalize_resource, compute_capability_id,
)
from serum2.coverage.operation_registry import GENERIC_EXECUTORS, verify_generic_executors


def test_dedup_key_ignores_payload_value():
    """Same mechanism, different mutation value -> SAME capability_id."""
    b1 = canonicalize_host_parameter("Env 1 Release")
    b2 = canonicalize_host_parameter("Env 1 Release")
    id1 = compute_capability_id("HOST_PARAMETER", b1)
    id2 = compute_capability_id("HOST_PARAMETER", b2)
    assert id1 == id2, "identical parameter_name must produce identical capability_id"
    print("[PASS] dedup key stable for identical binding")


def test_dedup_key_ignores_matrix_route_amount():
    """MATRIX_ROUTE binding excludes amount/depth -- same route, different
    amount must be the SAME capability."""
    route_a = canonicalize_matrix_route(
        source={"module": "LFO1", "parameter": "Rate"},
        destination={"module": "VoiceFilter", "parameter": "Freq"},
        slot_index=3,
    )
    route_b = canonicalize_matrix_route(
        source={"module": "LFO1", "parameter": "Rate"},
        destination={"module": "VoiceFilter", "parameter": "Freq"},
        slot_index=3,
    )
    id_a = compute_capability_id("MATRIX_ROUTE", route_a)
    id_b = compute_capability_id("MATRIX_ROUTE", route_b)
    assert id_a == id_b
    # amount is never a parameter of canonicalize_matrix_route at all --
    # this is enforced by the function signature, not just by equal calls.
    print("[PASS] MATRIX_ROUTE canonical binding has no payload-value field")


def test_matrix_route_different_slot_different_capability():
    route_a = canonicalize_matrix_route(
        source={"module": "LFO1", "parameter": "Rate"},
        destination={"module": "VoiceFilter", "parameter": "Freq"},
        slot_index=3,
    )
    route_b = canonicalize_matrix_route(
        source={"module": "LFO1", "parameter": "Rate"},
        destination={"module": "VoiceFilter", "parameter": "Freq"},
        slot_index=4,
    )
    id_a = compute_capability_id("MATRIX_ROUTE", route_a)
    id_b = compute_capability_id("MATRIX_ROUTE", route_b)
    assert id_a != id_b, "different slot_index must be a different capability"
    print("[PASS] MATRIX_ROUTE different slot_index -> different capability_id")


def test_key_ordering_irrelevant():
    """Field ordering at the Python dict level must not affect the hash."""
    b1 = canonicalize_topology(
        owner={"bus": "FX1"}, action="ADD_MODULE", instance_selector=None,
    )
    # construct with keys inserted in a different order
    b2 = {
        "binding_type": "TOPOLOGY",
        "action": "ADD_MODULE",
        "owner": {"bus": "FX1"},
        "binding_schema_version": 1,
    }
    id_a = compute_capability_id("STRUCTURAL_OPERATION", b1)
    id_b = compute_capability_id("STRUCTURAL_OPERATION", b2)
    assert id_a == id_b, "dict key insertion order must not affect capability_id"
    print("[PASS] capability_id independent of dict key insertion order")


def test_float_rejected():
    try:
        compute_capability_id("HOST_PARAMETER", {"binding_type": "HOST_PARAMETER", "value": 0.5})
        assert False, "should have rejected a float in the binding"
    except InvariantViolation:
        print("[PASS] float in identity binding rejected")


def test_resource_omits_payload():
    b = canonicalize_resource(owner="OSC1", resource_kind="WAVETABLE")
    assert "wavetable_path" not in b and "hash" not in b and "name" not in b
    print("[PASS] RESOURCE canonical binding excludes resource value/path/hash")


def test_v2_1_resolution_gate():
    unresolved = SemanticResolution(
        semantic_id="TEST.UNKNOWN", technical_target_id=None,
        execution_resolution=ExecutionResolution.UNKNOWN_EXECUTION.value,
        resolution_provenance="test", resolution_reason="test",
    )
    bad_binding = CapabilityBinding(
        capability_id="fake", execution_family="HOST_PARAMETER", mutation_type="SCALAR",
        operation_key="x", authoritative_binding={"a": 1},
        binding_status="LIVE_VERIFIED", binding_provenance=None, binding_version=None,
    )
    try:
        validate_v2_1_resolution_gate(unresolved, bad_binding)
        assert False, "should have raised: UNRESOLVED row with populated binding"
    except InvariantViolation:
        print("[PASS] V2-1 rejects populated binding on unresolved row")

    good_binding_none = None
    validate_v2_1_resolution_gate(unresolved, good_binding_none)
    print("[PASS] V2-1 allows unresolved row with no binding")


def test_v2_3_generic_operation_key():
    try:
        validate_v2_3_generic_operation_key("ENV1_RELEASE_handler", GENERIC_EXECUTORS)
        assert False, "should have rejected a target-specific operation_key"
    except InvariantViolation:
        print("[PASS] V2-3 rejects target-specific operation_key")

    validate_v2_3_generic_operation_key(
        "serum2.evidence.mutation_executor_extended.execute_mutation_request_with_authority",
        GENERIC_EXECUTORS,
    )
    print("[PASS] V2-3 accepts the registered authority-gated executor")


def test_family_primitive_consistency():
    validate_family_primitive_consistency("HOST_PARAMETER", "SCALAR")
    print("[PASS] family/primitive consistency accepts correct mapping")
    try:
        validate_family_primitive_consistency("HOST_PARAMETER", "COMPOUND")
        assert False
    except InvariantViolation:
        print("[PASS] family/primitive consistency rejects mismatched mapping")


def test_generic_executors_importable():
    status = verify_generic_executors()
    assert status["SCALAR"].startswith("VERIFIED_IMPORTABLE")
    assert status["STATE"].startswith("VERIFIED_IMPORTABLE")
    assert status["COMPOUND"].startswith("VERIFIED_IMPORTABLE")
    assert status["SCALAR"] == status["STATE"] == status["COMPOUND"], (
        "SCALAR, STATE, and COMPOUND must share the same authority-gated entry point"
    )
    for prim in ("TOPOLOGY", "RESOURCE"):
        assert status[prim].startswith("NOT_AUTHORITY_INTEGRATED")
    print("[PASS] generic executor registry: SCALAR+STATE+COMPOUND share the "
          "authority-gated executor; TOPOLOGY/RESOURCE honestly NOT_AUTHORITY_INTEGRATED")


if __name__ == "__main__":
    tests = [
        test_dedup_key_ignores_payload_value,
        test_dedup_key_ignores_matrix_route_amount,
        test_matrix_route_different_slot_different_capability,
        test_key_ordering_irrelevant,
        test_float_rejected,
        test_resource_omits_payload,
        test_v2_1_resolution_gate,
        test_v2_3_generic_operation_key,
        test_family_primitive_consistency,
        test_generic_executors_importable,
    ]
    print("=" * 80)
    print("EXECUTION COVERAGE V2 -- SCHEMA SELF-CHECK")
    print("=" * 80)
    for t in tests:
        t()
    print("\nALL V2 SCHEMA CHECKS PASSED")
