"""Canonical binding construction + capability_id dedup key.

Work item 4 of the Execution Coverage V2 milestone.

Frozen rule (session architecture decision): authoritative_binding is a
typed, semantically normalized identity object containing only information
that identifies the executable MECHANISM, never the value being applied.

  capability_id = hash(execution_family, canonical_authoritative_binding)

Canonical serialization pipeline:
  typed normalized object -> UTF-8 canonical JSON (sorted keys, compact
  separators) -> deterministic byte sequence -> sha256 hash

Hard rules (enforced by _reject_non_canonical, not just documented):
  - no floats in identity bindings
  - no mutable/payload values (amount, current value, wavetable path/hash)
  - no target-specific executor names
  - no semantic wording
  - no arbitrary dict ordering (json.dumps(..., sort_keys=True) handles this)
"""

from __future__ import annotations
import hashlib
import json
import unicodedata
from typing import Any, Dict, Optional

from .schema import BindingType, InvariantViolation

BINDING_SCHEMA_VERSION = 1


def _reject_non_canonical(obj: Any, path: str = "$") -> None:
    """Recursively reject float and non-JSON-primitive values -- identity
    bindings must be exact, discrete, and value-free."""
    if isinstance(obj, float):
        raise InvariantViolation(
            f"canonical binding at {path} contains a float ({obj!r}); "
            f"identity bindings must contain only exact discrete values "
            f"(str/int/bool/None/dict/list), never mutation payload floats"
        )
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str):
                raise InvariantViolation(f"canonical binding at {path} has non-string key {k!r}")
            _reject_non_canonical(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _reject_non_canonical(v, f"{path}[{i}]")


def _omit_none(d: Dict[str, Any]) -> Dict[str, Any]:
    """Absent optional fields are omitted entirely, never present-as-null,
    so two bindings that differ only in an omitted-vs-null field canonicalize identically."""
    return {k: v for k, v in d.items() if v is not None}


def canonicalize_host_parameter(parameter_name: str) -> Dict[str, Any]:
    """Unicode NFC, exact case preserved, no whitespace folding."""
    normalized_name = unicodedata.normalize("NFC", parameter_name)
    binding = {
        "binding_schema_version": BINDING_SCHEMA_VERSION,
        "binding_type": BindingType.HOST_PARAMETER.value,
        "parameter_name": normalized_name,
    }
    _reject_non_canonical(binding)
    return binding


def canonicalize_body_state(path: str) -> Dict[str, Any]:
    """Path normalized to the project's canonical path grammar: strip a
    leading 'body:' prefix (matching the convention already used in
    contract.prerequisites field_path / canonical_feedback_loop.py), dotted
    segments preserved exactly (pathmerge.apply_path_value's own grammar)."""
    normalized_path = path[len("body:"):] if path.startswith("body:") else path
    binding = {
        "binding_schema_version": BINDING_SCHEMA_VERSION,
        "binding_type": BindingType.BODY_STATE.value,
        "path": normalized_path,
    }
    _reject_non_canonical(binding)
    return binding


def canonicalize_fx_parameter(effect: str, parameter: str) -> Dict[str, Any]:
    """FX-parameter identity: (effect, parameter) only. rack_index and
    slot_index are deliberately EXCLUDED -- they are where the user has
    currently placed the effect (runtime payload, supplied at request time
    via resolver_parameters to the fx_set_parameter resolver, exactly like
    STATE's other resolver-backed bindings), not part of what capability
    this is. "FXEQ.Freq1" is one capability regardless of which rack/slot
    the EQ instance currently occupies.
    """
    binding = {
        "binding_schema_version": BINDING_SCHEMA_VERSION,
        "binding_type": BindingType.FX_PARAMETER.value,
        "effect": effect,
        "parameter": parameter,
    }
    _reject_non_canonical(binding)
    return binding


def canonicalize_matrix_route(source: Dict[str, str], destination: Dict[str, str],
                                slot_index: Optional[int] = None) -> Dict[str, Any]:
    """source/destination endpoint fields explicitly named; slot_index
    always integer or omitted; amount/depth/curve are mutation payload, not
    identity, and must never be passed to this function."""
    if slot_index is not None and not isinstance(slot_index, int):
        raise InvariantViolation(f"slot_index must be int or None, got {type(slot_index)}")
    binding = _omit_none({
        "binding_schema_version": BINDING_SCHEMA_VERSION,
        "binding_type": BindingType.MATRIX_ROUTE.value,
        "source": _omit_none(dict(source)),
        "destination": _omit_none(dict(destination)),
        "slot_index": slot_index,
    })
    _reject_non_canonical(binding)
    return binding


def canonicalize_topology(owner: Dict[str, str], action: str,
                            instance_selector: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """The module configuration being inserted/removed is mutation data
    unless it changes the identity of the operation itself -- callers must
    only pass fields that distinguish one structural operation from another."""
    binding = _omit_none({
        "binding_schema_version": BINDING_SCHEMA_VERSION,
        "binding_type": BindingType.TOPOLOGY.value,
        "owner": _omit_none(dict(owner)),
        "action": action,
        "instance_selector": _omit_none(dict(instance_selector)) if instance_selector else None,
    })
    _reject_non_canonical(binding)
    return binding


def canonicalize_meta_string(meta_key: str) -> Dict[str, Any]:
    """.SerumPreset meta-dict field identity: the key itself
    (e.g. "presetName"). No rack/slot/effect placement concept applies --
    a meta field is a single top-level key in the preset file's JSON meta
    dict, not a CBOR body path."""
    binding = {
        "binding_schema_version": BINDING_SCHEMA_VERSION,
        "binding_type": BindingType.META_STRING.value,
        "meta_key": meta_key,
    }
    _reject_non_canonical(binding)
    return binding


def canonicalize_resource(owner: str, resource_kind: str) -> Dict[str, Any]:
    """The actual resource path/hash/name is mutation payload, never identity
    -- that is exactly what prevents every wavetable from becoming a
    separate capability."""
    binding = {
        "binding_schema_version": BINDING_SCHEMA_VERSION,
        "binding_type": BindingType.RESOURCE.value,
        "owner": owner,
        "resource_kind": resource_kind,
    }
    _reject_non_canonical(binding)
    return binding


def canonical_json_bytes(canonical_binding: Dict[str, Any]) -> bytes:
    """Deterministic byte sequence: sorted keys, compact separators, UTF-8."""
    return json.dumps(canonical_binding, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False).encode("utf-8")


def compute_capability_id(execution_family: str, canonical_binding: Dict[str, Any]) -> str:
    """capability_id = hash(execution_family, canonical_authoritative_binding).

    execution_family is included in the hashed payload (not just prefixed)
    so two families can never collide even with pathologically similar
    binding shapes.
    """
    _reject_non_canonical(canonical_binding)
    payload = {"execution_family": execution_family, "binding": canonical_binding}
    digest = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    return f"{execution_family}:{digest[:16]}"
