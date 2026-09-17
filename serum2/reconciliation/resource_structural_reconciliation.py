#!/usr/bin/env python3
"""RESOURCE_OPERATION (41) + STRUCTURAL_OPERATION (10) reconciliation.

Classifies every row using only its frozen semantic definition's
control_type -- no invented bindings, no forced parameter verification.
Confirms the instruction's premise directly: these rows are file-system/
OS-dialog actions, one-shot UI actions (buttons, menus, context menus),
non-interactive displays/structural constants, or free-text metadata
fields -- none of them are numeric SCALAR/STATE parameters, so none of
them belong in the existing (numeric) bulk verifier. They need their own
action-execution architecture (simulated click/menu-select/file-dialog
handling), which does not exist in this codebase yet and is out of scope
to invent here.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json"
SEMANTIC_PATH = REPO_ROOT / "serum2" / "reconciliation" / "SERUM2_SEMANTIC_NORMALIZED.json"
OUT_PATH = REPO_ROOT / "serum2" / "reconciliation" / "RESOURCE_STRUCTURAL_RECONCILIATION.json"

# control_type -> disposition, from the frozen semantic definition alone.
NON_INTERACTIVE_TYPES = {"display", "structural_fact"}
METADATA_FIELD_TYPES = {"text_field", "text_area", "tag_editor"}
ACTION_TYPES = {
    "button", "menu_action", "action", "tab_toggle", "dropdown", "context_menu",
    "cascading_menu", "star_rating", "multi_select_list", "tree", "table",
    "button_pair", "menu", "launch_button", "midi_trigger", "submenu_select", "toggle",
}


def classify(sem):
    ctype = sem.get("control_type")
    if ctype in NON_INTERACTIVE_TYPES:
        return ("PROVEN_NOT_USER_CONTROL",
                f"control_type={ctype!r}: non-interactive display or structural constant, not a mutable value.")
    if ctype in METADATA_FIELD_TYPES:
        return ("NEEDS_STRING_METADATA_MECHANISM",
                f"control_type={ctype!r}: real, editable free-text metadata -- a genuine user action, but a "
                f"STRING-value edit, not a numeric SCALAR/STATE parameter. No string-mutation mechanism "
                f"exists in this codebase (execute_mutation_request_with_authority's MutationType variants "
                f"are all numeric); needs its own resolver/mechanism, not the existing bulk verifier.")
    if ctype in ACTION_TYPES:
        return ("NEEDS_ACTION_EXECUTION_MECHANISM",
                f"control_type={ctype!r}: a genuine one-shot user action (button/menu/context-menu/file "
                f"dialog/OS-level operation), not a value to mutate at all. No action-execution architecture "
                f"exists in this codebase (osc_load_wavetable/osc_load_sample are the only RESOURCE compilers, "
                f"scoped to oscillator resources, not preset/browser/file-system actions). Needs its own "
                f"mechanism (e.g. driven UI clicks or a file-system/host API), not the numeric bulk verifier.")
    return ("UNSUPPORTED_NO_EVIDENCE", f"control_type={ctype!r}: unrecognized pattern, not classified.")


def main():
    registry = json.load(open(REGISTRY_PATH, "r", encoding="utf-8"))
    semantic_defs = {r["semantic_id"]: r for r in json.load(open(SEMANTIC_PATH, "r", encoding="utf-8"))["records"]}

    rows = [r for r in registry["semantic_resolutions"]
            if r.get("capability_binding") and r["capability_binding"]["execution_family"] in
            ("RESOURCE_OPERATION", "STRUCTURAL_OPERATION")
            and r["capability_binding"]["binding_status"] == "NOT_YET_DERIVED"]

    results = []
    for row in rows:
        sid = row["semantic_id"]
        sem = semantic_defs.get(sid)
        if sem is None:
            results.append({"semantic_id": sid, "disposition": "UNSUPPORTED_NO_EVIDENCE",
                             "evidence": "no frozen semantic definition found"})
            continue
        disposition, evidence = classify(sem)
        results.append({"semantic_id": sid, "family": row["capability_binding"]["execution_family"],
                         "label": sem.get("canonical_label"), "control_type": sem.get("control_type"),
                         "disposition": disposition, "evidence": evidence})

    counts = {}
    for r in results:
        counts[r["disposition"]] = counts.get(r["disposition"], 0) + 1

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"total": len(results), "counts": counts, "rows": results}, f, indent=2)

    print(f"RESOURCE_OPERATION + STRUCTURAL_OPERATION reconciliation: {len(results)} rows")
    for disposition, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {disposition:36s} {count}")
    print(f"\nWrote: {OUT_PATH}")


if __name__ == "__main__":
    main()
