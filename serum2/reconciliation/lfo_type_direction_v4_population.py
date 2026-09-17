#!/usr/bin/env python3
"""V4 population pass: LFO TYPE / DIRECTION.

Binds LFO{1-6}.TYPE and LFO{1-6}.DIRECTION (12 of the 30 previously
NOT_YET_DERIVED LFO rows: TYPE/DIVISION/DIRECTION/PRESET/WAVEFORM_GRAPH x6),
using the already-established LFOx.plainParams.kParam<Name> pattern
(LFOx = LFO{n}'s CBOR body module, 0-indexed).

Real evidence:
  - Scanned all 745 real .SerumPreset files in the local Serum 2 Presets
    library: `kParamType` (values seen: Lorenz, Path, RandomSH, Rossler)
    and `kParamDirection` (values seen: 1.0, 2.0) both appear inside real
    LFO plainParams dicts, alongside the already-bound kParamMode/kParamRate/
    kParamBeatSync/kParamTriplets/kParamDotted fields.
  - serum2/reconciliation/test_lfo_type_direction_real_roundtrip.py proves,
    via a REAL DawDreamer/Serum round trip (same standard as every other
    BODY_STATE_FIELD binding in this registry -- not just our own codec),
    that both fields dispatch through the authority-gated executor and
    persist exactly, from both an already-active LFO slot (LFO0, real
    curveData) and a cold/unused slot (LFO5, 'default' sentinel) -- proving
    the mechanism generalizes across all 6 LFOs, not just one instance.

Explicitly NOT bound this pass (left NOT_YET_DERIVED, not guessed):
  - LFO.DIVISION: no real preset in the 745-file library has a non-default
    kParamBeatSync, so no division-related field has ever been observed
    materializing. A live-Serum-in-Ableton BeatSync=1.0 write also collapses
    to the presence-preserving default sentinel (matching LFO.TEMPO_SYNC's
    own documented finding), so it cannot be probed this way either.
  - LFO.PRESET: curveDisplayName is proven (same test file) to survive
    serum2.codec's OWN .SerumPreset file round trip but NOT the DawDreamer
    live-Serum round trip (collapses to None even with zero mutation
    applied). Binding it as an ordinary BODY_STATE_FIELD would silently
    misrepresent its evidence tier against this registry's DawDreamer
    standard -- left open pending an explicit decision on how to represent
    file-format-only body fields (a distinct case from META_STRING, which
    covers the top-level meta dict, not the CBOR body).
  - LFO.WAVEFORM_GRAPH: confirmed structural curveData (curveVals/numPoints/
    xVals/yVals), a complex nested object, not a scalar/enum -- deferred per
    explicit instruction, not attempted this pass.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2.coverage.schema import ExecutionFamily, MutationPrimitive, BindingStatus
from serum2.coverage.canonicalize import canonicalize_body_state, compute_capability_id
from serum2.coverage.operation_registry import operation_key_for

REPO_ROOT = Path(__file__).parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json"
REPORT_PATH = REPO_ROOT / "serum2" / "reconciliation" / "LFO_TYPE_DIRECTION_V4_POPULATION_REPORT.md"

ROUNDTRIP_EVIDENCE = (
    "serum2/reconciliation/test_lfo_type_direction_real_roundtrip.py: mutated through "
    "execute_mutation_request_with_authority (BODY_STATE dispatch), loaded into a REAL "
    "Serum instance via DawDreamer, Serum's own save_state() re-read and decoded, exact "
    "value match confirmed for both an already-active LFO slot and a cold/unused slot -- "
    "the same DawDreamer live-Serum evidence standard used for every other BODY_STATE_FIELD "
    "binding in this registry (e.g. LFO.TEMPO_SYNC/TRIPLET/DOTTED)."
)

# semantic_id -> real CBOR body path, generalized from the already-bound
# LFO1.TEMPO_SYNC/TRIPLET/DOTTED pattern (LFOx.plainParams.kParam<Name>).
BOUND = {}
for n in range(1, 7):
    idx = n - 1
    BOUND[f"LFO{n}.TYPE"] = f"LFO{idx}.plainParams.kParamType"
    BOUND[f"LFO{n}.DIRECTION"] = f"LFO{idx}.plainParams.kParamDirection"

UNSUPPORTED = {}
for n in range(1, 7):
    UNSUPPORTED[f"LFO{n}.DIVISION"] = (
        "no real preset in the 745-file local library has a non-default kParamBeatSync, and a "
        "direct real-Serum write of kParamBeatSync=1.0 collapses to the presence-preserving "
        "default sentinel (same finding already documented on LFO.TEMPO_SYNC) -- no division "
        "field has ever been observed materializing; requires live UI toggle+observe, out of "
        "scope for this automated pass"
    )
    UNSUPPORTED[f"LFO{n}.PRESET"] = (
        "curveDisplayName confirmed via real round-trip test to survive serum2.codec's OWN "
        ".SerumPreset file format round trip but NOT the DawDreamer live-Serum round trip "
        "(collapses to None even with zero mutation) -- binding it as ordinary BODY_STATE_FIELD "
        "would misrepresent its evidence tier against this registry's DawDreamer standard; needs "
        "an explicit architecture decision on file-format-only body fields before binding"
    )
    UNSUPPORTED[f"LFO{n}.WAVEFORM_GRAPH"] = (
        "confirmed structural curveData (curveVals/numPoints/xVals/yVals) -- a complex nested "
        "object, not a scalar/enum field; deferred per explicit instruction, not attempted"
    )


def main():
    registry = json.load(open(REGISTRY_PATH, encoding="utf-8"))
    rows_by_id = {r["semantic_id"]: r for r in registry["semantic_resolutions"]}

    bound, noted_unsupported, skipped = [], [], []

    for sem_id, body_path in BOUND.items():
        row = rows_by_id.get(sem_id)
        if row is None:
            skipped.append((sem_id, "not found in registry semantic_resolutions"))
            continue
        canonical = canonicalize_body_state(body_path)
        cap_id = compute_capability_id(ExecutionFamily.BODY_STATE_FIELD.value, canonical)
        old_status = (row.get("capability_binding") or {}).get("binding_status")
        row["capability_binding"] = {
            "capability_id": cap_id,
            "execution_family": ExecutionFamily.BODY_STATE_FIELD.value,
            "mutation_type": MutationPrimitive.STATE.value,
            "operation_key": operation_key_for(MutationPrimitive.STATE.value),
            "authoritative_binding": canonical,
            "binding_status": BindingStatus.LIVE_VERIFIED.value,
            "binding_provenance": (
                f"LFO V4 population: body_path={body_path!r} confirmed present in real "
                f".SerumPreset evidence (745-file library scan). {ROUNDTRIP_EVIDENCE}"
            ),
            "binding_version": "1",
        }
        row["resolution_provenance"] += (
            f"; V4: binding derived {old_status}->LIVE_VERIFIED (see capability_binding.binding_provenance)"
        )
        bound.append({"semantic_id": sem_id, "body_path": body_path, "capability_id": cap_id})

    for sem_id, reason in UNSUPPORTED.items():
        row = rows_by_id.get(sem_id)
        if row is None:
            skipped.append((sem_id, "not found in registry semantic_resolutions"))
            continue
        row["capability_binding"]["binding_provenance"] = reason
        row["resolution_provenance"] += f"; V4: binding attempt recorded, remains NOT_YET_DERIVED -- {reason}"
        noted_unsupported.append({"semantic_id": sem_id, "reason": reason})

    registry["metadata"]["v4_lfo_type_direction_population_pass"] = {
        "scope": "LFO{1-6}.TYPE and LFO{1-6}.DIRECTION (12 of 30 LFO rows): bind with real "
                 "DawDreamer round-trip evidence. DIVISION/PRESET/WAVEFORM_GRAPH (18 rows) left "
                 "honestly unresolved with documented reasoning.",
        "bound_this_pass": len(bound),
        "noted_unsupported_this_pass": len(noted_unsupported),
        "skipped": len(skipped),
    }

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    lines = ["# LFO TYPE/DIRECTION V4 Population Pass Report\n"]
    lines.append("## Bound (real DawDreamer/Serum round-trip evidence)\n")
    for b in bound:
        lines.append(f"- `{b['semantic_id']}` -> `{b['body_path']}` (capability_id=`{b['capability_id']}`)")
    lines.append("\n## Left unresolved, with documented evidence gap\n")
    for u in noted_unsupported:
        lines.append(f"- `{u['semantic_id']}`: {u['reason']}")
    if skipped:
        lines.append("\n## Skipped\n")
        for sem_id, reason in skipped:
            lines.append(f"- `{sem_id}`: {reason}")
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Bound: {len(bound)}  Unresolved(noted): {len(noted_unsupported)}  Skipped: {len(skipped)}")
    print(f"Wrote: {REGISTRY_PATH}")
    print(f"Wrote: {REPORT_PATH}")


if __name__ == "__main__":
    main()
