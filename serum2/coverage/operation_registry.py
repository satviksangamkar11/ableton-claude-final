"""Generic, primitive-level operation_key registry + validation.

Work item 8 of the Execution Coverage V2 milestone.

Invariant V2-3: operation_key must be one of a fixed set of GENERIC
dispatchers, never a target-specific function name (e.g. never
"ENV1_RELEASE_handler"). This module is the single source of truth for
that fixed set, and mechanically verifies each entry is actually
importable -- a plausible-looking dotted path is not evidence it exists.

STATUS (updated as each primitive is authority-integrated, per the agreed
milestone order STATE -> COMPOUND -> TOPOLOGY -> RESOURCE):

Originally there were TWO separate, disconnected execution-dispatch
systems in this codebase: the AUTHORITY-GATED path
(execute_mutation_request_with_authority, D.1.1/D.1.2) and an OLDER,
separately-built serum2.operations.registry.OperationRegistry
(get_registry()) whose compilers were reachable from nowhere in
producer/evidence/compiler -- a disconnected, admission-bypassing parallel
architecture, verified by grep, not assumed.

The integration work wires each OperationRegistry compiler in as a
backend, invoked ONLY from inside the authority-gated executor via
ExecutionBinding.resolver_operation_id (contract-derived, never
caller-chosen) -- never called directly. get_registry() itself is called
from exactly one place in producer/evidence/compiler: inside
mutation_executor_extended.py's shared _dispatch_resolver_operation().
This is re-verified mechanically by
test_compound_resolver_integration.py::test_no_direct_operation_registry_bypass
on every run, not just asserted once.

  SCALAR:   integrated (D.1.2 -- inline, HOST_PARAMETER)
  STATE:    integrated (resolver-backed, e.g. fx_set_parameter fixes the
            rack/slot/effect/parameter -> CBOR path + range validation
            that raw pathmerge never did)
  COMPOUND: integrated (resolver-backed, e.g. compound_create_modulation_
            route -- ALSO fixed the pre-existing hard-coded-to-
            VoiceFilter/kParamFreq destination defect as part of
            integration, per explicit instruction not to carry a known
            defect forward behind the new authority boundary; now uses
            the empirically-derived a3_modulation_route tables)
  TOPOLOGY: integrated, PROVEN OPERATIONS ONLY -- not the whole
            FXStructuralOperation enum. An explicit allowlist
            (PROVEN_TOPOLOGY_OPERATION_IDS) permits ADD/REMOVE/REPLACE/
            CLEAR_RACK/BYPASS/UNBYPASS (+ bus-level bypass/unbypass); it
            deliberately excludes REORDER and MOVE_BETWEEN_BUSES, which
            have no compiler at all. ALSO fixed as part of integration: the
            bypass_effect()/unbypass_effect() "*" wildcard path segment
            (pathmerge has no resolver for it -- would have written a
            literal "*" key) now resolves the concrete FX-type key from
            live state, mirroring the already-correct bypass_bus() pattern.
            ADD/REPLACE compiler methods existed but were never registered
            in the OperationRegistry at all -- registered as part of this
            integration. Every mechanism class (ADD, REMOVE, REPLACE,
            CLEAR_RACK, BYPASS) proven against real Serum/DawDreamer, not
            just unit-level compilation; BYPASS additionally proven to
            produce a genuine audible difference (RMS delta), not just a
            state-field change.
  RESOURCE: integrated, WAVETABLE ONLY -- an explicit allowlist
            (oscillator_operations.PROVEN_RESOURCE_OPERATION_IDS) permits
            only osc_load_wavetable. osc_load_sample and osc_load_
            multisample are deliberately excluded: their claimed state
            fields were checked against real presets this session and
            found wrong/inapplicable (SAMPLE's claimed
            SampleOsc{N}.relativePathToSample is contradicted by a real
            granular-oscillator preset, whose actual field is
            GranularOsc{N}.samplePathRelative; MULTISAMPLE uses embedded
            SFZ text, not a path field). ALSO fixed as part of this
            integration audit, found by direct evidence, not assumed:
            (1) ResourceResolver's search roots and its "standard library"
            shortcut (STANDARD_WAVETABLES/STANDARD_SAMPLES) were entirely
            fabricated -- checked against the real installed content
            directory, none of "operator"/"brass"/"pad"/"drum_kick"
            correspond to any real file. Removed the shortcut; resolution
            now ALWAYS verifies against real files (hash + size computed),
            never a cached guess. (2) search roots were wrong
            (<install_dir>/S2 Tables vs the real Documents-based content
            root already used elsewhere in this codebase, e.g.
            serum2/statemodel.py). (3) filename matching silently failed
            for any multi-word name ("Default Shapes" never matched
            "Default Shapes.wav") due to inconsistent space/underscore
            normalization between query and candidate. (4) no upper-bound
            oscillator-index validation existed at all. Full chain proven
            against real Serum, not just filesystem resolution: resource
            identity -> validated content-root resolution (real hash/size)
            -> authority-gated mutation -> real Serum load -> real Serum
            save/readback, with two DIFFERENT wavetables shown to produce
            two DIFFERENT Serum-confirmed readback states.
"""

from __future__ import annotations
import importlib
from typing import Dict, Optional

from .schema import MutationPrimitive, InvariantViolation

AUTHORITY_GATED_EXECUTOR = (
    "serum2.evidence.mutation_executor_extended.execute_mutation_request_with_authority"
)

# mutation_type -> dotted "module.function" path. Values here are the ONLY
# valid operation_key values (V2-3). All five primitives now share the same
# entry point deliberately: it is one generic executor that dispatches
# internally on MutationRequest.mutation_type, not a per-primitive function.
# NOTE: RESOURCE being VERIFIED_IMPORTABLE here means the primitive-level
# dispatch exists and is real; it does NOT mean every resource kind is
# usable -- see oscillator_operations.PROVEN_RESOURCE_OPERATION_IDS
# (WAVETABLE only; SAMPLE/MULTISAMPLE explicitly excluded).
GENERIC_EXECUTORS: Dict[str, Optional[str]] = {
    MutationPrimitive.SCALAR.value: AUTHORITY_GATED_EXECUTOR,
    MutationPrimitive.STATE.value: AUTHORITY_GATED_EXECUTOR,
    MutationPrimitive.COMPOUND.value: AUTHORITY_GATED_EXECUTOR,
    MutationPrimitive.TOPOLOGY.value: AUTHORITY_GATED_EXECUTOR,
    MutationPrimitive.RESOURCE.value: AUTHORITY_GATED_EXECUTOR,
}

NOT_IMPLEMENTED_REASON: Dict[str, str] = {}


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
