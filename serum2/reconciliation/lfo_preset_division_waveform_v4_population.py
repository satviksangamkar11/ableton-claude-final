#!/usr/bin/env python3
"""V4 population pass: LFO PRESET / DIVISION / WAVEFORM_GRAPH evidence gaps.

All 18 rows (6 LFOs × 3 fields) remain NOT_YET_DERIVED with documented
architectural blockers, not guesses.

LFO.DIVISION (6 rows): curveDisplayName mechanism confirmed via test suite.
Same default-collapse behavior as LFO.TEMPO_SYNC (BeatSync=1.0 sentinel).
Direct probe attempts have shown no field materializes. No evidence
contradicts their existence; simply unobservable in corpus or via direct
writes. Marked BLOCKED_BY_EVIDENCE_DESIGN: awaiting explicit mechanism
design for how to represent "defaults collapse to sentinel" semantics if
binding is ever intended. (This is orthogonal to whether binding IS
intended -- the semantic answer precedes the binding decision.)

LFO.PRESET (6 rows): curveDisplayName field confirmed to survive
serum2.codec's .SerumPreset file format round trip but NOT survive
DawDreamer/live-Serum round trip (collapses to None). Marked
BLOCKED_BY_EVIDENCE_TIER_MISMATCH: evidence tier is "file-format-only"
but BODY_STATE_FIELD family's standing standard is "DawDreamer-verified"
(proven to round-trip through live Serum). No contradiction; a clean
distinction between file-format persistence and VST3-processor-state
persistence. Binding would require an architectural decision on how the
registry classifies/represents file-format-only BODY fields (if at all).

LFO.WAVEFORM_GRAPH (6 rows): curveData confirmed structural
(curveVals/numPoints/xVals/yVals dict-of-lists, not a scalar/enum).
Marked NOT_BINDABLE_AS_SCALAR: genuine complex object, not a
field-mutation target. Mapping curveData onto the registry's scalar/enum/
boolean mutation types would require wrapper logic and a distinct binding
type (e.g., COMPOUND binding for curveData, or a dedicated structural
type). Deferred pending explicit decision on whether complex nested
structures get their own binding types.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

REPO_ROOT = Path(__file__).parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json"

EVIDENCE_GAPS = {
    # DIVISION: default collapse, same as TEMPO_SYNC
    **{f"LFO{n}.DIVISION": (
        "kParamDivision field never observed in corpus (745-file scan) or via direct BeatSync=1.0 probe. "
        "Default-collapse behavior matches LFO.TEMPO_SYNC: when enabled, materializes a default sentinel "
        "instead of a real value; cannot be probed bidirectionally. Same challenge as TEMPO_SYNC applies: "
        "architectural blocker is representing 'defaults collapse to sentinel' semantics if binding is ever "
        "intended. Not a data gap; a modeling gap. BLOCKED_BY_EVIDENCE_DESIGN."
    ) for n in range(1, 7)},

    # PRESET: file-format-only evidence tier
    **{f"LFO{n}.PRESET": (
        "curveDisplayName field confirmed to survive serum2.codec's .SerumPreset file-format round trip "
        "(tested in test_lfo_type_direction_real_roundtrip.py) but collapses to None through DawDreamer/ "
        "live-Serum round trip. BODY_STATE_FIELD family's standing evidence bar is DawDreamer-verified. "
        "This is not a contradiction; a clean distinction between file-format persistence and VST3-processor "
        "state persistence. BLOCKED_BY_EVIDENCE_TIER_MISMATCH: binding would require registry architectural "
        "decision on whether file-format-only BODY fields are represented (and how)."
    ) for n in range(1, 7)},

    # WAVEFORM_GRAPH: structural curveData, not scalar
    **{f"LFO{n}.WAVEFORM_GRAPH": (
        "curveData confirmed structural: dict with curveVals (list), numPoints (int), xVals (list), yVals (list). "
        "Not a scalar/enum/boolean field; a complex nested object. Mapping onto registry's mutation type system "
        "would require wrapper logic and decision on whether complex objects get their own binding types (e.g., "
        "COMPOUND for curveData mutation, or a new STRUCTURAL type). NOT_BINDABLE_AS_SCALAR: deferred pending "
        "explicit architectural decision."
    ) for n in range(1, 7)},
}

BLOCKED_STATUS = "NOT_YET_DERIVED"  # All 18 rows remain unbound with documented blockers


def main():
    registry = json.load(open(REGISTRY_PATH, encoding="utf-8"))
    rows_by_id = {r["semantic_id"]: r for r in registry["semantic_resolutions"]}

    noted = []
    skipped = []

    for sem_id, reason in EVIDENCE_GAPS.items():
        row = rows_by_id.get(sem_id)
        if row is None:
            skipped.append((sem_id, "not found in registry semantic_resolutions"))
            continue
        row["capability_binding"]["binding_provenance"] = reason
        row["resolution_provenance"] += f"; V4: evidence gap documented (see capability_binding.binding_provenance)"
        noted.append({"semantic_id": sem_id, "reason": reason[:100]})

    registry["metadata"]["v4_lfo_preset_division_waveform_population_pass"] = {
        "scope": "LFO{1-6}.PRESET/DIVISION/WAVEFORM_GRAPH (18 of 30 LFO rows): all remain NOT_YET_DERIVED with "
                 "documented architectural blockers (evidence tier mismatch, default collapse, structural type).",
        "rows_with_documented_gaps": len(noted),
        "skipped": len(skipped),
    }

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    lines = ["# LFO PRESET/DIVISION/WAVEFORM_GRAPH V4 Population Pass Report\n"]
    lines.append("## All 18 rows remain NOT_YET_DERIVED with documented architectural blockers\n")
    for n in noted:
        lines.append(f"- `{n['semantic_id']}`: {n['reason']}…")

    report_path = REPO_ROOT / "serum2" / "reconciliation" / "LFO_PRESET_DIVISION_WAVEFORM_V4_POPULATION_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Documented gaps: {len(noted)}  Skipped: {len(skipped)}")
    print(f"Wrote: {REGISTRY_PATH}")
    print(f"Wrote: {report_path}")


if __name__ == "__main__":
    main()
