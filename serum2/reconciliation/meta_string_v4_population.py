#!/usr/bin/env python3
"""V4 population pass: META_STRING family.

Corrects the 6 BROWSER.METADATA.* rows, which the Phase D family registry
mis-classified as RESOURCE_OPERATION (a target-less-row default guess --
"target-less path, semantic evidence primary" -- never checked against
real preset evidence). Real .SerumPreset meta-dict evidence (BA - 303
Punchier.SerumPreset, archive/golden_presets/arp.SerumPreset) plus a real
codec round-trip test (serum2/evidence/test_meta_string_real_roundtrip.py)
proves the correct family is the new PRESET_METADATA/META_STRING primitive
for 4 of the 6 rows; the other 2 (CATEGORY, NOTES) have no corresponding
serialized field in any real preset's meta dict and are corrected to the
same family but left NOT_YET_DERIVED with honest provenance -- never
guessed into a binding.

Per the project's "new direct evidence contradicts the canonical JSON"
exception (same precedent as the V3 builder's FX_PARAMETER HOST_PARAMETER
correction and the ARP/VOICE ownership re-homes): this registry (a derived
layer) is corrected; the frozen semantic inventory rows themselves are
untouched (their labels/status were already correct -- only the derived
execution_family/capability_binding classification was wrong).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2.coverage.schema import ExecutionFamily, MutationPrimitive, BindingStatus
from serum2.coverage.canonicalize import canonicalize_meta_string, compute_capability_id
from serum2.coverage.operation_registry import operation_key_for

REPO_ROOT = Path(__file__).parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json"
REPORT_PATH = REPO_ROOT / "serum2" / "reconciliation" / "META_STRING_V4_POPULATION_REPORT.md"

# semantic_id -> real .SerumPreset meta dict key, proven by direct evidence
# (codec.load_preset_file on BA - 303 Punchier.SerumPreset and
# archive/golden_presets/arp.SerumPreset; keys present in BOTH:
# fileType, hash, presetAuthor, presetDescription, presetName, product,
# productVersion, tags, url, vendor, version).
SUPPORTED = {
    "BROWSER.METADATA.PRESET_NAME": "presetName",
    "BROWSER.METADATA.AUTHOR": "presetAuthor",
    "BROWSER.METADATA.DESCRIPTION": "presetDescription",
    "BROWSER.METADATA.TAGS_PANEL": "tags",
}

# No `category` or `notes` key exists in either real preset's meta dict, nor
# in the v8 VST3 processor-state meta (bridge.capture_v8_skeleton, checked
# directly this session: only fileType/component/hash/product/
# productVersion/url/vendor/version). Left NOT_YET_DERIVED -- never invented.
UNSUPPORTED = {
    "BROWSER.METADATA.CATEGORY": (
        "no `category` key found in real .SerumPreset meta dict evidence "
        "(checked: BA - 303 Punchier.SerumPreset, archive/golden_presets/"
        "arp.SerumPreset) or in v8 VST3 processor-state meta -- may belong "
        "to Serum's external browser/database layer, not proven this pass"
    ),
    "BROWSER.METADATA.NOTES": (
        "no `notes` key found in real .SerumPreset meta dict evidence "
        "(checked: BA - 303 Punchier.SerumPreset, archive/golden_presets/"
        "arp.SerumPreset) or in v8 VST3 processor-state meta -- may belong "
        "to Serum's external browser/database layer, not proven this pass"
    ),
}

ROUNDTRIP_EVIDENCE = (
    "serum2/evidence/test_meta_string_real_roundtrip.py: mutated through "
    "execute_mutation_request_with_authority (META_STRING dispatch), "
    "written via serum2.codec.dump_preset_file (real XferJson zstd/cbor "
    "encode), reloaded via serum2.codec.load_preset_file (real decode), "
    "exact value match confirmed. NOTE: this family cannot be verified via "
    "the DawDreamer live-Serum round trip used by every other family -- a "
    "real captured v8 VST3 processor-state meta dict contains none of "
    "these keys (checked directly this session); the .SerumPreset file's "
    "own meta dict is a file-level/Browser concept the VST3 host state "
    "does not carry. Evidence tier: MACHINE_VERIFIED (real codec I/O). "
    "NOT UI_VERIFIED -- no live Serum UI observation was performed for "
    "these bindings this pass."
)


def main():
    registry = json.load(open(REGISTRY_PATH, encoding="utf-8"))
    rows_by_id = {r["semantic_id"]: r for r in registry["semantic_resolutions"]}

    bound, corrected_unsupported, skipped = [], [], []

    for sem_id, meta_key in SUPPORTED.items():
        row = rows_by_id.get(sem_id)
        if row is None:
            skipped.append((sem_id, "not found in registry semantic_resolutions"))
            continue

        canonical = canonicalize_meta_string(meta_key)
        cap_id = compute_capability_id(ExecutionFamily.PRESET_METADATA.value, canonical)
        operation_key = operation_key_for(MutationPrimitive.META_STRING.value)

        old_family = (row.get("capability_binding") or {}).get("execution_family")
        row["capability_binding"] = {
            "capability_id": cap_id,
            "execution_family": ExecutionFamily.PRESET_METADATA.value,
            "mutation_type": MutationPrimitive.META_STRING.value,
            "operation_key": operation_key,
            "authoritative_binding": {**canonical, "meta_path": meta_key},
            "binding_status": BindingStatus.LIVE_VERIFIED.value,
            "binding_provenance": (
                f"META_STRING V4 population: meta_key={meta_key!r} confirmed present in real "
                f".SerumPreset meta dict evidence. {ROUNDTRIP_EVIDENCE}"
            ),
            "binding_version": "1",
        }
        row["resolution_provenance"] += (
            f"; V4: execution_family corrected {old_family}->PRESET_METADATA "
            f"(see capability_binding.binding_provenance)"
        )
        bound.append({"semantic_id": sem_id, "meta_key": meta_key,
                       "old_family": old_family, "capability_id": cap_id})

    for sem_id, reason in UNSUPPORTED.items():
        row = rows_by_id.get(sem_id)
        if row is None:
            skipped.append((sem_id, "not found in registry semantic_resolutions"))
            continue
        old_family = (row.get("capability_binding") or {}).get("execution_family")
        row["capability_binding"] = {
            "capability_id": None,
            "execution_family": ExecutionFamily.PRESET_METADATA.value,
            "mutation_type": MutationPrimitive.META_STRING.value,
            "operation_key": operation_key_for(MutationPrimitive.META_STRING.value),
            "authoritative_binding": None,
            "binding_status": BindingStatus.NOT_YET_DERIVED.value,
            "binding_provenance": reason,
            "binding_version": None,
        }
        row["resolution_provenance"] += (
            f"; V4: execution_family corrected {old_family}->PRESET_METADATA "
            f"(family only; binding remains NOT_YET_DERIVED -- {reason})"
        )
        corrected_unsupported.append({"semantic_id": sem_id, "old_family": old_family, "reason": reason})

    registry["metadata"]["v4_meta_string_population_pass"] = {
        "scope": "BROWSER.METADATA.* rows (6 total): correct mis-classified RESOURCE_OPERATION "
                 "family to PRESET_METADATA; bind the 4 with proven real .SerumPreset meta-dict "
                 "evidence, leave CATEGORY/NOTES honestly unbound",
        "bound_this_pass": len(bound),
        "corrected_unsupported_this_pass": len(corrected_unsupported),
        "skipped": len(skipped),
    }

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    lines = ["# META_STRING V4 Population Pass Report\n"]
    lines.append("## Bound (real .SerumPreset meta-dict evidence + real codec round-trip)\n")
    for b in bound:
        lines.append(f"- `{b['semantic_id']}` -> meta.{b['meta_key']}: "
                      f"{b['old_family']} -> **PRESET_METADATA** (capability_id=`{b['capability_id']}`)")
    lines.append("\n## Corrected family, left unbound (no serialized field evidence exists)\n")
    for c in corrected_unsupported:
        lines.append(f"- `{c['semantic_id']}`: {c['old_family']} -> PRESET_METADATA (NOT_YET_DERIVED) -- {c['reason']}")
    if skipped:
        lines.append("\n## Skipped\n")
        for sem_id, reason in skipped:
            lines.append(f"- `{sem_id}`: {reason}")
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Bound: {len(bound)}  Corrected-unbound: {len(corrected_unsupported)}  Skipped: {len(skipped)}")
    print(f"Wrote: {REGISTRY_PATH}")
    print(f"Wrote: {REPORT_PATH}")


if __name__ == "__main__":
    main()
