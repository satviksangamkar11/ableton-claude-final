"""Generic, primitive-level operation_key registry + validation.

Work item 8 of the Execution Coverage V2 milestone.

Invariant V2-3: operation_key must be one of a fixed set of GENERIC
dispatchers, never a target-specific function name (e.g. never
"ENV1_RELEASE_handler"). This module is the single source of truth for
that fixed set, and mechanically verifies each entry is actually
importable -- a plausible-looking dotted path is not evidence it exists.

IMPORTANT DISCOVERED FINDING (verified this session, not assumed):
There are TWO separate, disconnected execution-dispatch systems in this
codebase:

  1. serum2.evidence.mutation_executor_extended
     .execute_mutation_request_with_authority()
     -- the AUTHORITY-GATED path (D.1.1/D.1.2). Admission-checked,
     ExecutionBinding-resolved, zero-mutation-on-refusal, proven end-to-end
     against real Serum for HOST_PARAMETER (Release/Attack). Internally
     dispatches SCALAR (HOST_PARAMETER) and STATE (BODY_STATE) inline
     (_execute_host_parameter_mutation / _execute_body_state_mutation).
     COMPOUND and TOPOLOGY are explicitly refused there today
     ("not yet implemented"); RESOURCE has no case at all yet.

  2. serum2.operations.registry.OperationRegistry (get_registry())
     -- an OLDER, separately-built compiler/operation catalog with real,
     already-registered compiler functions for STATE (fx_set_parameter,
     osc_set_parameter), COMPOUND (create_modulation_route,
     set_macro_value, mod_set_curve, ...), RESOURCE (load_wavetable,
     load_sample), and TOPOLOGY (register_fx_structural_operations).
     Mechanically confirmed this session: get_registry() is called from
     NOWHERE in serum2/producer/, serum2/evidence/, or serum2/compiler/ --
     it is not reachable from any admission-gated or producer-facing path.
     It predates the D.1.1/D.1.2 authority architecture and appears to be
     the kind of parallel/duplicate execution architecture CLAUDE.md warns
     against ("Do not create duplicate architectures... one admission
     gate"). It is real, substantial, importable code -- but using it
     directly would bypass admission entirely. Flagged here for explicit
     human decision (integrate vs. deprecate), not silently chosen either way.

Because of this, GENERIC_EXECUTORS below intentionally points ONLY at the
authority-gated entry point for the primitives it already handles, and
records the (2) OperationRegistry compilers as a separate, NOT
authority-integrated fact -- never as a usable operation_key.
"""

from __future__ import annotations
import importlib
from typing import Dict, Optional

from .schema import MutationPrimitive, InvariantViolation

AUTHORITY_GATED_EXECUTOR = (
    "serum2.evidence.mutation_executor_extended.execute_mutation_request_with_authority"
)

# mutation_type -> dotted "module.function" path, or None if no
# AUTHORITY-GATED generic dispatcher exists yet. Values here are the ONLY
# valid operation_key values (V2-3). SCALAR and STATE share the same entry
# point deliberately: it is one generic executor that dispatches internally
# on MutationRequest.mutation_type, not a per-primitive function.
GENERIC_EXECUTORS: Dict[str, Optional[str]] = {
    MutationPrimitive.SCALAR.value: AUTHORITY_GATED_EXECUTOR,
    MutationPrimitive.STATE.value: AUTHORITY_GATED_EXECUTOR,
    MutationPrimitive.COMPOUND.value: None,
    MutationPrimitive.TOPOLOGY.value: None,
    MutationPrimitive.RESOURCE.value: None,
}

NOT_IMPLEMENTED_REASON: Dict[str, str] = {
    MutationPrimitive.COMPOUND.value:
        "execute_mutation_request_with_authority() explicitly refuses "
        "COMPOUND today ('not yet implemented'). A separate, "
        "NOT-authority-integrated OperationRegistry compiler catalog exists "
        "(compound_operations.py: create_modulation_route, set_macro_value, "
        "mod_set_curve, ...) but is unreachable from get_registry() call "
        "sites in producer/evidence/compiler -- using it would bypass "
        "admission. Wiring it into the authority gate (mirroring D.1.2's "
        "BODY_STATE/HOST_PARAMETER pattern) is future work, not done here.",
    MutationPrimitive.TOPOLOGY.value:
        "execute_mutation_request_with_authority() explicitly refuses "
        "TOPOLOGY today ('not yet implemented'). A separate, "
        "NOT-authority-integrated FXStructuralCompiler exists "
        "(fx_structural_operations.py) registered into the same "
        "disconnected OperationRegistry -- same bypass risk as COMPOUND.",
    MutationPrimitive.RESOURCE.value:
        "execute_mutation_request_with_authority() has no RESOURCE case at "
        "all yet. osc_load_wavetable/osc_load_sample compilers exist in the "
        "disconnected OperationRegistry (same bypass risk as COMPOUND); "
        "ResourceResolver (resource_resolver.py) validates resource "
        "identity but is not itself a mutation executor.",
}


def _resolve_dotted_path(dotted_path: str):
    module_path, _, func_name = dotted_path.rpartition(".")
    mod = importlib.import_module(module_path)
    return getattr(mod, func_name)


def verify_generic_executors() -> Dict[str, str]:
    """Mechanically verify every non-None entry in GENERIC_EXECUTORS is
    actually importable. Returns {mutation_type: status} for reporting.
    Raises InvariantViolation if a registered entry does NOT import --
    a broken reference is worse than an honest None."""
    status = {}
    for mutation_type, operation_key in GENERIC_EXECUTORS.items():
        if operation_key is None:
            status[mutation_type] = f"NOT_AUTHORITY_INTEGRATED: {NOT_IMPLEMENTED_REASON[mutation_type]}"
            continue
        try:
            _resolve_dotted_path(operation_key)
            status[mutation_type] = f"VERIFIED_IMPORTABLE: {operation_key}"
        except (ImportError, AttributeError) as e:
            raise InvariantViolation(
                f"GENERIC_EXECUTORS[{mutation_type!r}] = {operation_key!r} "
                f"does not import: {type(e).__name__}: {e}"
            )
    return status


def operation_key_for(mutation_type: str) -> Optional[str]:
    if mutation_type not in GENERIC_EXECUTORS:
        raise InvariantViolation(f"unknown mutation_type: {mutation_type!r}")
    return GENERIC_EXECUTORS[mutation_type]
