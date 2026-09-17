#!/usr/bin/env python3
"""META_STRING -- real .SerumPreset file round-trip proof.

Unlike every other mutation family (BODY_STATE/HOST_PARAMETER/TOPOLOGY/
RESOURCE/COMPOUND), META_STRING cannot be verified via the DawDreamer
live-Serum round trip: a real captured v8 VST3 processor-state meta dict
(bridge.capture_v8_skeleton) was checked directly this session and
contains ONLY {fileType/component, hash, product, productVersion, url,
vendor, version} -- none of presetName/presetAuthor/presetDescription/tags
exist in VST3 processor state at all. Those fields live ONLY in the
.SerumPreset (v5) file's own meta dict, a file-level/Browser concept, not
something the VST3 host round-trips.

This file therefore proves persistence the only way that is actually
possible: through serum2.codec's own real encode/decode of the
XferJson container format -- mutate through the authority-gated executor,
write a real .SerumPreset file, read it back, and compare. This is real
file I/O (real zstd/cbor/struct encoding), not a simulation, but it is
NOT a live-Serum-UI or DawDreamer proof -- MACHINE_VERIFIED only, never
reported as ACTUAL UI_VERIFIED.
"""

import copy
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2 import codec
from serum2.evidence import admission
from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding, STRUCTURAL_ONLY

GOLDEN_PRESET = str(Path(__file__).parent.parent.parent / "archive" / "golden_presets" / "arp.SerumPreset")


def make_contract(meta_key: str) -> CapabilityContract:
    binding = ExecutionBinding(mutation_type="META_STRING", meta_path=meta_key,
                                binding_source="test", binding_version="1.0")
    return CapabilityContract(target=f"META.{meta_key}", allowed_operation="mutate_enum_value",
                               status=STRUCTURAL_ONLY, prerequisites=(), verified={},
                               measurement=None, scope={}, provenance={},
                               execution_binding=binding, limitations=())


def dispatch(meta: dict, meta_key: str, value):
    contract = make_contract(meta_key)
    request = MutationRequest(target=f"META.{meta_key}", mutation_type=MutationType.META_STRING, value=value)
    return execute_mutation_request_with_authority(
        request=request, body={}, contracts={(f"META.{meta_key}", ""): contract}, synth=None, meta=meta,
    )


def real_codec_roundtrip(meta: dict, body: dict):
    """Real serum2.codec encode -> write -> read -> decode. No simulation."""
    fd, tmp = tempfile.mkstemp(suffix=".SerumPreset")
    os.close(fd)
    try:
        codec.dump_preset_file(tmp, meta, body)
        return codec.load_preset_file(tmp)
    finally:
        os.remove(tmp)


def _load_base():
    meta, body = codec.load_preset_file(GOLDEN_PRESET)
    return copy.deepcopy(meta), copy.deepcopy(body)


def test_preset_name_roundtrip():
    meta, body = _load_base()
    proof = dispatch(meta, "presetName", "TEST - Renamed Preset")
    assert proof.executed and proof.mutation_succeeded
    assert meta["presetName"] == "TEST - Renamed Preset"

    reloaded_meta, reloaded_body = real_codec_roundtrip(meta, body)
    assert reloaded_meta["presetName"] == "TEST - Renamed Preset", \
        f"real codec round-trip did not persist presetName: {reloaded_meta}"
    print("[PASS] presetName: mutate -> real .SerumPreset round-trip -> persisted")


def test_preset_author_roundtrip():
    meta, body = _load_base()
    proof = dispatch(meta, "presetAuthor", "Test Author")
    assert proof.executed and proof.mutation_succeeded

    reloaded_meta, _ = real_codec_roundtrip(meta, body)
    assert reloaded_meta["presetAuthor"] == "Test Author", \
        f"real codec round-trip did not persist presetAuthor: {reloaded_meta}"
    print("[PASS] presetAuthor: mutate -> real .SerumPreset round-trip -> persisted")


def test_preset_description_roundtrip():
    meta, body = _load_base()
    proof = dispatch(meta, "presetDescription", "Test description text")
    assert proof.executed and proof.mutation_succeeded

    reloaded_meta, _ = real_codec_roundtrip(meta, body)
    assert reloaded_meta["presetDescription"] == "Test description text", \
        f"real codec round-trip did not persist presetDescription: {reloaded_meta}"
    print("[PASS] presetDescription: mutate -> real .SerumPreset round-trip -> persisted")


def test_tags_roundtrip_is_a_list():
    """Real evidence (BA - 303 Punchier.SerumPreset, arp.SerumPreset) shows
    `tags` is a LIST of strings, not a scalar string or structured object.
    The mutation VALUE must be the whole replacement list -- there is no
    proven per-tag add/remove primitive, only whole-field replacement,
    matching every other META_STRING field's semantics."""
    meta, body = _load_base()
    assert isinstance(meta["tags"], list) and all(isinstance(t, str) for t in meta["tags"]), \
        f"tags is not a list-of-strings in real evidence: {meta['tags']!r}"

    new_tags = ["Bass", "Acid", "TestTag"]
    proof = dispatch(meta, "tags", new_tags)
    assert proof.executed and proof.mutation_succeeded
    assert meta["tags"] == new_tags

    reloaded_meta, _ = real_codec_roundtrip(meta, body)
    assert reloaded_meta["tags"] == new_tags, \
        f"real codec round-trip did not persist tags list: {reloaded_meta}"
    print("[PASS] tags: confirmed list-of-strings representation, mutate -> real round-trip -> persisted")


def test_category_and_notes_are_refused_unknown():
    """No real .SerumPreset meta dict evidence (BA - 303 Punchier, arp.SerumPreset,
    v8 VST3 processor state) contains a `category` or `notes` key. No contract
    exists for these targets -- admission must refuse REFUSED_UNKNOWN, not
    silently synthesize a binding from the semantic label alone."""
    for target in ("BROWSER.METADATA.CATEGORY", "BROWSER.METADATA.NOTES"):
        result = admission.admit({}, target)
        assert not result.admitted
        assert result.reason == admission.REFUSED_UNKNOWN
        print(f"[PASS] {target}: correctly REFUSED_UNKNOWN (no serialized field evidence exists)")


def test_refused_mutation_produces_zero_change():
    """Authority invariant: an executor call using a contract with NO
    META_STRING execution_binding must refuse and leave meta untouched."""
    meta, _ = _load_base()
    baseline = copy.deepcopy(meta)
    binding = ExecutionBinding(mutation_type="BODY_STATE", body_path="Irrelevant")
    contract = CapabilityContract(target="X", allowed_operation="mutate_enum_value",
                                   status=STRUCTURAL_ONLY, prerequisites=(), verified={},
                                   measurement=None, scope={}, provenance={},
                                   execution_binding=binding, limitations=())
    request = MutationRequest(target="X", mutation_type=MutationType.META_STRING, value="hacked")
    proof = execute_mutation_request_with_authority(
        request=request, body={}, contracts={("X", ""): contract}, synth=None, meta=meta,
    )
    assert not proof.executed
    assert meta == baseline, "AUTHORITY VIOLATION: meta dict changed despite refused binding"
    print("[PASS] mismatched execution_binding -> refused, zero mutation")


if __name__ == "__main__":
    test_preset_name_roundtrip()
    test_preset_author_roundtrip()
    test_preset_description_roundtrip()
    test_tags_roundtrip_is_a_list()
    test_category_and_notes_are_refused_unknown()
    test_refused_mutation_produces_zero_change()
    print("\nALL META_STRING REAL ROUND-TRIP TESTS PASSED")
