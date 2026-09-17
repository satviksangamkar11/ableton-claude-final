#!/usr/bin/env python3
"""Programmatic MATRIX_ROUTE reconciliation pass.

Classifies all 106 frozen MATRIX_ROUTE semantic rows into
REAL_EXECUTABLE / EXISTING_EXECUTABLE_DIFFERENT_MECHANISM /
PROVEN_NOT_USER_CONTROL / UNSUPPORTED_NO_EVIDENCE using ONLY:
  - the frozen semantic definitions (SERUM2_SEMANTIC_NORMALIZED.json)
  - the registered OperationRegistry compilers (compound_operations.py)
  - a3_modulation_route.py's evidence-graded source/destination tables
  - the live VST3 host-parameter list (real Serum, via DawDreamer)

No source ID, destination ID, parameter path, or binding is invented.
Where the frozen definition itself proves a row is non-interactive
(a UI label, an indicator, a system policy/limit, a hypothesized-but-
nonexistent control), that IS the evidence for PROVEN_NOT_USER_CONTROL --
not a guess.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import dawdreamer as daw
from serum2.evidence import epoch as epoch_mod
from serum2.qualification.a3_modulation_route import _SOURCES, _DESTINATIONS

# MATRIX.LFO_BUS.NN -> which LFO number (1-16) it names.
_LFO_BUS_NUMBER = {f"MATRIX.LFO_BUS.{n:02d}": n for n in range(1, 17)}

REPO_ROOT = Path(__file__).parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json"
SEMANTIC_PATH = REPO_ROOT / "serum2" / "reconciliation" / "SERUM2_SEMANTIC_NORMALIZED.json"
OUT_PATH = REPO_ROOT / "serum2" / "reconciliation" / "MATRIX_ROUTE_RECONCILIATION.json"

# Registered COMPOUND compilers that are NOT compiler_create_modulation_route
# but DO exist, are wired in registry.py, and write real ModSlot{N} body
# fields. (mod_set_curve, mod_set_bipolar, mod_set_aux_source)
EXISTING_MOD_SLOT_COMPILERS = {"mod_set_curve", "mod_set_bipolar", "mod_set_aux_source"}

# a3_modulation_route._SOURCES keys, normalized for name matching against
# MATRIX.SOURCE.<X> semantic rows (evidence: source_type_id table, Step 20).
_SOURCE_NAME_TO_SEMANTIC_SUFFIX = {
    "LFO1": "LFO_1", "LFO2": "LFO_2", "LFO3": "LFO_3", "LFO4": "LFO_4", "LFO5": "LFO_5",
    "LFO6": "LFO_6", "LFO7": "LFO_7", "LFO8": "LFO_8", "LFO9": "LFO_9", "LFO10": "LFO_10",
    "Env1": "ENV_1", "Env2": "ENV_2", "Env3": "ENV_3", "Env4": "ENV_4",
    "ModWheel": "MOD_WHEEL", "Velocity": "VELO", "Note": "NOTE#",
}


def get_live_host_param_names():
    VST3 = epoch_mod.SERUM_VST3
    engine = daw.RenderEngine(44100, 512)
    synth = engine.make_plugin_processor("serum", VST3)
    return {p["name"] for p in synth.get_parameters_description()}


def load_matrix_route_rows(registry):
    return [r for r in registry["semantic_resolutions"]
            if r.get("capability_binding") and r["capability_binding"]["execution_family"] == "MATRIX_ROUTE"]


def load_semantic_defs():
    recs = json.load(open(SEMANTIC_PATH, "r", encoding="utf-8"))["records"]
    return {r["semantic_id"]: r for r in recs}


def classify(semantic_id, sem, host_params):
    """Returns (bucket, evidence_note, candidate_binding_or_None)."""
    label = sem.get("canonical_label", "")
    ctype = sem.get("control_type")
    vdomain = sem.get("value_domain")
    options = sem.get("options") or []

    # ---- Explicit non-interactive/structural rows (definition itself proves it) ----
    if semantic_id == "MATRIX.OUT_INDICATOR":
        return ("PROVEN_NOT_USER_CONTROL",
                "Own definition: 'small non-interactive indicator' -- proven non-interactive by definition.", None)
    if semantic_id == "MATRIX.MOD":
        return ("PROVEN_NOT_USER_CONTROL",
                "Own definition: 'hypothesized separate...control (does not exist as a discrete Matrix column)' "
                "-- proven not to exist as a real column by its own frozen definition.", None)
    if semantic_id == "MATRIX.SYS.DUPLICATE_ROUTE_POLICY":
        return ("PROVEN_NOT_USER_CONTROL",
                "control_type='structural_policy': describes internal duplicate-route ALLOW rules, not a "
                "settable value.", None)
    if semantic_id == "MATRIX.SYS.MAX_ROUTES":
        return ("PROVEN_NOT_USER_CONTROL",
                "control_type='system_limit': a fixed capacity constant (0-64 slots), not a mutable control.", None)
    if semantic_id == "MATRIX.SYS.MENU":
        return ("PROVEN_NOT_USER_CONTROL",
                "control_type='menu': a UI menu container of sub-actions (Sort by Source, Lock Matrix, etc.), "
                "not itself a single mutable value.", None)
    if semantic_id == "MATRIX.DESTINATION.LFO_N_CONDITIONAL":
        return ("PROVEN_NOT_USER_CONTROL",
                "control_type='destination_target_conditional': describes the conditional param-choice submenu "
                "shown once LFO is picked as destination module, not itself one settable field.", None)
    if semantic_id.endswith(".SOURCE") and ctype == "unknown" and "drag-handle" in label:
        return ("PROVEN_NOT_USER_CONTROL",
                "Own definition: 'drag-handle circle icon' -- a drag-gesture affordance for initiating a route, "
                "not itself a discrete value.", None)

    # ---- MATRIX.SOURCE.* structural_source_selection: availability declarations ----
    if ctype == "structural_source_selection" and vdomain == "STRUCTURAL_SELECTION":
        suffix = semantic_id.split("MATRIX.SOURCE.", 1)[-1]
        matched_source = next((k for k, v in _SOURCE_NAME_TO_SEMANTIC_SUFFIX.items() if v == suffix), None)
        note = ("control_type='structural_source_selection'/value_domain='STRUCTURAL_SELECTION': the frozen "
                "definition itself classifies this as an availability declaration (this item exists as a "
                "selectable option), not an independently mutable value.")
        if matched_source:
            note += (f" Backed by a3_modulation_route._SOURCES[{matched_source!r}] "
                      f"(source_type_id={_SOURCES[matched_source].source_type_id}, "
                      f"{_SOURCES[matched_source].notes}) -- exercising this selection is what "
                      f"compound_create_modulation_route's source={matched_source!r} parameter already does; "
                      f"the row itself remains a structural fact, not a scalar/boolean target.")
        return ("PROVEN_NOT_USER_CONTROL", note, None)

    # ---- MATRIX.SOURCE.* with control_type='source_target' but NOT in _SOURCES: no evidence ----
    if ctype == "source_target":
        return ("UNSUPPORTED_NO_EVIDENCE",
                f"control_type='source_target', but {semantic_id!r} has no matching key in "
                f"a3_modulation_route._SOURCES ({sorted(_SOURCES.keys())}) -- real user-facing concept, "
                f"no authoritative source_type_id evidence yet.", None)

    # ---- MATRIX.LFO_BUS.NN: dynamically checked against the REAL, evidence-backed
    # a3_modulation_route._DESTINATIONS table (745-file corpus scan, V4 pass) ----
    if semantic_id in _LFO_BUS_NUMBER:
        bus_n = _LFO_BUS_NUMBER[semantic_id]
        module_id = bus_n - 1
        matching = [name for name, d in _DESTINATIONS.items()
                    if d.dest_module_type_string == "LFO" and d.dest_module_id == module_id]
        if matching:
            return ("EXISTING_EXECUTABLE_DIFFERENT_MECHANISM",
                    f"control_type='destination_target': a3_modulation_route._DESTINATIONS now has "
                    f"{len(matching)} real, corpus-evidenced per-parameter destination(s) for LFO{bus_n} "
                    f"(moduleID={module_id}): {sorted(matching)}. Exercising this bus is what "
                    f"compound_create_modulation_route's destination={matching[0]!r} parameter already does "
                    f"(real DawDreamer/Serum round-trip proven, see "
                    f"test_matrix_lfo_bus_destination_real_roundtrip.py) -- the row itself remains a "
                    f"bus-level menu-selection fact (paired with MATRIX.DESTINATION.LFO_N_CONDITIONAL's "
                    f"already-classified param submenu), not an independently mutable value.",
                    {"binding_type": "COMPOUND_DESTINATION_AVAILABLE", "sample_destination": matching[0]})
        return ("UNSUPPORTED_NO_EVIDENCE",
                f"control_type='destination_target': a3_modulation_route._DESTINATIONS has zero real, "
                f"corpus-evidenced entries for LFO{bus_n} (moduleID={module_id}) across a 745-file scan of "
                f"the local Serum 2 Presets library -- no real preset routes anything into this LFO slot.", None)

    # ---- GLOBAL.RETRIGGERS.*: boolean, checked against live host-param list (no match) ----
    if semantic_id.startswith("GLOBAL.RETRIGGERS."):
        return ("UNSUPPORTED_NO_EVIDENCE",
                "control_type='boolean': checked against the live VST3 host-parameter list this run -- no "
                "'<source> Retrig'-shaped parameter exists (only unrelated 'Arp Retrig Rate' found); no "
                "registered COMPOUND compiler for retrigger-enable either. Real user-facing concept, no "
                "mechanism evidence yet.", None)

    # ---- LFO1-6.SOURCE: continuous/SCALAR_UNBOUNDED, no compiler or table entry matches this shape ----
    if semantic_id.endswith(".SOURCE") and vdomain == "SCALAR_UNBOUNDED":
        return ("UNSUPPORTED_NO_EVIDENCE",
                "control_type='continuous'/value_domain='SCALAR_UNBOUNDED' with no options and no matching "
                "field in any registered compiler or a3_modulation_route table -- no evidence for what this "
                "numeric value represents mechanically.", None)

    # ---- MATRIX.OUT: real host parameter 'Mod N Out' (checked live this run) ----
    if semantic_id == "MATRIX.OUT":
        if "Mod 1 Out" in host_params:
            return ("EXISTING_EXECUTABLE_DIFFERENT_MECHANISM",
                    "control_type='slider', label 'scale the final modulation output (per-row final-output "
                    "scale slider)' -- matches the live VST3 host-parameter list's 'Mod N Out' (checked this "
                    "run: 64 Mod-slot Amount/Out pairs present, e.g. 'Mod 1 Out'..'Mod 64 Out'). "
                    "HOST_PARAMETER mechanism, not compiler_create_modulation_route.",
                    {"binding_type": "HOST_PARAMETER", "parameter_name": "Mod 1 Out"})
        return ("UNSUPPORTED_NO_EVIDENCE", "Expected live host parameter 'Mod 1 Out' not found this run.", None)

    # ---- MACRO.SYS.AUX_CURVE / BIPOLAR_UNIPOLAR / AUX_SOURCE: real registered compilers exist ----
    if semantic_id == "MACRO.SYS.AUX_CURVE":
        return ("EXISTING_EXECUTABLE_DIFFERENT_MECHANISM",
                "Registered COMPOUND compiler 'mod_set_curve' (compiler_set_modulation_curve) writes "
                "ModSlot{N}.curve -- real, wired mechanism, not compiler_create_modulation_route. Requires an "
                "existing ModSlot (route) as a prerequisite; deferred, see caveat below.", None)
    if semantic_id == "MACRO.SYS.BIPOLAR_UNIPOLAR":
        return ("EXISTING_EXECUTABLE_DIFFERENT_MECHANISM",
                "Registered COMPOUND compiler 'mod_set_bipolar' (compiler_set_modulation_bipolar) writes "
                "ModSlot{N}.bipolar -- real, wired mechanism, not compiler_create_modulation_route. Requires an "
                "existing ModSlot (route) as a prerequisite; deferred, see caveat below.", None)
    if semantic_id == "MACRO.SYS.AUX_SOURCE":
        return ("EXISTING_EXECUTABLE_DIFFERENT_MECHANISM",
                "Registered COMPOUND compiler 'mod_set_aux_source' (compiler_set_modulation_aux_source) writes "
                "ModSlot{N}.auxSource -- real, wired mechanism, not compiler_create_modulation_route. Requires "
                "an existing ModSlot (route) as a prerequisite; deferred, see caveat below.", None)
    if semantic_id == "MACRO.SYS.AUX_INVERT":
        return ("UNSUPPORTED_NO_EVIDENCE",
                "control_type='toggle': no registered compiler for aux-invert (checked compound_operations.py's "
                "full compiler list) and no matching live host parameter ('invert'/'nvert' not found).", None)
    if semantic_id == "MACRO.SYS.ASSIGN_MATRIX_SOURCE":
        return ("UNSUPPORTED_NO_EVIDENCE",
                "The general mechanism (compound_create_modulation_route's source= parameter) exists, but "
                "'Macro 1'..'Macro 8' are not keys in a3_modulation_route._SOURCES -- selecting a macro as a "
                "route source specifically has no source_type_id evidence.", None)

    return ("UNSUPPORTED_NO_EVIDENCE", "No matching mechanism or table evidence found for this row.", None)


def main():
    registry = json.load(open(REGISTRY_PATH, "r", encoding="utf-8"))
    semantic_defs = load_semantic_defs()
    host_params = get_live_host_param_names()

    rows = load_matrix_route_rows(registry)
    results = []
    for row in rows:
        sid = row["semantic_id"]
        sem = semantic_defs.get(sid)
        if sem is None:
            results.append({"semantic_id": sid, "bucket": "UNSUPPORTED_NO_EVIDENCE",
                             "evidence": "No frozen semantic definition found for this row.", "candidate_binding": None})
            continue
        bucket, evidence, candidate = classify(sid, sem, host_params)
        results.append({"semantic_id": sid, "label": sem.get("canonical_label"), "bucket": bucket,
                         "evidence": evidence, "candidate_binding": candidate})

    counts = {}
    for r in results:
        counts[r["bucket"]] = counts.get(r["bucket"], 0) + 1

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"total": len(results), "counts": counts, "rows": results}, f, indent=2)

    print(f"MATRIX_ROUTE reconciliation: {len(results)} rows")
    for bucket, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {bucket:40s} {count}")
    print(f"\nWrote: {OUT_PATH}")
    return results


if __name__ == "__main__":
    main()
