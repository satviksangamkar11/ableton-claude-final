"""MODULATION_ROUTE fixture.

STRUCTURAL fixture only -- proves a modulation route (e.g. LFO1 -> a
destination) is created and persists through a real Serum round-trip
(ModSlot destModuleTypeString/destModuleID/destModuleParamID match).

This does NOT constitute a causal audio proof by itself. It is the
required PREREQUISITE fixture for any LFO causal-audio test (e.g.
LFO1.Rate), which currently has no render/measurement step defined yet
(see EXERCISE_CONTEXT_REGISTRY_V1.json: LFO1.Rate is BLOCKED pending this).

Reuses the exact resolver already proven in
serum2/reconciliation/test_matrix_lfo_bus_destination_real_roundtrip.py.
"""

from serum2 import bridge
from serum2.evidence import epoch as epoch_mod
from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding

VST3 = epoch_mod.SERUM_VST3

EXERCISE_CONTEXT = []


def _make_contract():
    binding = ExecutionBinding(
        mutation_type="COMPOUND",
        resolver_operation_id="compound_create_modulation_route",
        binding_source="fixture", binding_version="1.0",
    )
    return CapabilityContract(
        target="T", allowed_operation="mutate_structured_value",
        status="STRUCTURAL_ONLY", prerequisites=(), verified={},
        measurement=None, scope={}, provenance={},
        execution_binding=binding, limitations=(),
    )


def create_lfo_route(body, source: str, destination: str, amount: float = 0.5):
    """Create a modulation route in-place on `body`. Returns the executor proof."""
    contract = _make_contract()
    request = MutationRequest(
        target="T", mutation_type=MutationType.COMPOUND, value=None,
        resolver_parameters={"source": source, "destination": destination, "amount": amount},
    )
    return execute_mutation_request_with_authority(
        request=request, body=body, contracts={("T", ""): contract}, synth=None,
    )


def MODULATION_ROUTE(source: str = "LFO1", destination: str = "LFO3.Rate", amount: float = 0.6):
    """Returns (skeleton, exercise_context) with the route already applied to body.

    Caller must render this skeleton and compare against a baseline skeleton
    WITHOUT the route to isolate the causal effect of the route itself, or
    use it as shared context while mutating the source LFO's own parameters.
    """
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton
    proof = create_lfo_route(body, source, destination, amount)
    return (meta, body), list(EXERCISE_CONTEXT), proof
