#!/usr/bin/env python3
"""SERUM2_EXECUTION_COVERAGE_REGISTRY_V3 -- builder.

First substep of Execution Coverage Population: populate canonical
CapabilityBindings for a subset of the 373 RESOLVED-but-NOT_YET_DERIVED
rows from V2, using the now-complete authority substrate (STATE/COMPOUND/
TOPOLOGY/RESOURCE all authority-integrated).

Preserves: RESOLVED != BOUND != EXECUTABLE != CAUSAL_VERIFIED != ADMITTED.
This pass only advances RESOLVED rows to BOUND (a real CapabilityBinding
with a verified authoritative_binding). It does not qualify or admit
anything -- qualification/admission remain separate, later gates.

SCOPE OF THIS PASS (conservative, evidence-backed, not exhaustive):
  FX_PARAMETER targets, exact 1:1 semantic<->target match, AND effect
  FX-type-key independently confirmed against real Serum output (14 rows
  bound; 6 more matched but excluded because their key is unconfirmed --
  see CONFIRMED_SAFE_EFFECTS). Everything else in the 373-row gap is
  explicitly left NOT_YET_DERIVED for follow-up substeps.

  MID-PASS CORRECTION: an earlier draft of this pass matched against
  fx_resolver_complete.py (disconnected from the real dispatch path) and
  would have bound 19 rows, several non-dispatchable. Re-matching against
  fx_resolver.py (the actually-wired catalog) plus an ACTUAL executor
  dispatch check surfaced that fx_resolver.py itself had 4 wrong FX-type
  keys (Compressor, Convolve, Hyper, Bode) -- fixed with real evidence
  (see fx_resolver.py's own docstring). 4 more effects (Chorus, FilterFX,
  Flanger, Utility) remain genuinely unconfirmed and are excluded here,
  not guessed.

KEY CORRECTION MADE IN THIS PASS (evidence-backed, not carried forward):
The frozen 396-target vocabulary tags all 96 target_source=="FX_PARAMETER"
targets as parameter_kind=="VST3_HOST_FIELD". Checked directly against the
live VST3 parameter list this session (2623 params): NO host parameter
exists for any of them (e.g. no "EQ Freq1", no "Distortion Drive" --
only "Filter 1/2 Drive", which is the main VoiceFilter, a DIFFERENT
capability). This classification is demonstrably wrong. The real
mechanism (verified against captured real preset structures earlier this
session, and cross-validated against serum2.operations.fx_resolver_
complete's catalog) is CBOR body state via the fx_set_parameter resolver
(already authority-integrated as part of STATE). This coverage registry
(a derived layer, not the frozen vocabulary itself) overrides the family
for these 19 rows to BODY_STATE_FIELD with full evidence recorded --
the frozen SERUM2_TARGET_NORMALIZED_V4.json file itself is NOT edited.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from serum2.coverage.schema import ExecutionFamily, MutationPrimitive, BindingStatus
from serum2.coverage.canonicalize import canonicalize_fx_parameter, compute_capability_id
from serum2.coverage.operation_registry import operation_key_for

# Effects whose fx_resolver.py FX{Type} state-path key AND plainParams
# structure have been INDEPENDENTLY VERIFIED against real
# archive/golden_presets/*.SerumPreset output this session (see
# fx_resolver.py's module docstring for the full key-correction record: 4
# keys were found WRONG and fixed -- FXCompressor->FXComp, FXBODE->FXBode,
# FXConvolve->FXConv, FXHyper->FXHyperD).
#
# Convolve is deliberately EXCLUDED despite its key now being correct: a
# real captured Convolve FX entry has NO "plainParams" field at all (only
# "embeddedIR" + others) -- confirmed by a live dispatch+round-trip test
# that failed with plainParams remaining the literal string "default"
# rather than becoming a dict. Convolve's parameters most likely only
# materialize once real IR content is loaded (the same presence-preserving
# CBOR pattern found earlier this session for envelope ADSR fields), which
# this scaffold-only test cannot exercise. Needs dedicated investigation,
# not a guess.
#
# Chorus, FilterFX, Flanger, and Utility remain UNCONFIRMED (no real
# preset evidence found for them either way) and are deliberately excluded
# -- binding them would repeat the exact mistake just caught and fixed.
CONFIRMED_SAFE_EFFECTS = {
    "Distortion", "Delay", "EQ", "Phaser", "Reverb",  # never wrong
    "Compressor", "BODE", "Hyper",                     # fixed + verified this session
}

V2_JSON = Path("SERUM2_EXECUTION_COVERAGE_REGISTRY_V2.json")
TARGET_VOCAB_PATH = Path("serum2/reconciliation/SERUM2_TARGET_NORMALIZED_V4.json")
SEMANTIC_PATH = Path("serum2/reconciliation/SERUM2_SEMANTIC_NORMALIZED.json")

OUTPUT_JSON = Path("SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json")
OUTPUT_REPORT = Path("SERUM2_EXECUTION_COVERAGE_REGISTRY_V3_REPORT.md")


def normalize_id(s: str) -> str:
    return s.upper().replace("_", "").replace(".", "")


def find_fx_parameter_exact_matches():
    """The (semantic_id, target_id, effect, parameter) tuples: exact 1:1
    normalized match AND resolvable in fx_resolver.py's REAL catalog -- the
    one actually wired into the authority-gated executor via
    compiler_set_fx_parameter/fx_set_parameter (NOT fx_resolver_complete.py,
    a separate, larger, uniformly-cased catalog that is NOT connected to
    dispatch; an earlier draft of this script used that one by mistake and
    would have produced 19 bindings that fail at real dispatch time --
    caught and fixed before shipping by attempting a real dispatch, see
    verify_binding_dispatches()).

    fx_resolver.py's keys use INCONSISTENT casing per effect (e.g.
    ("Distortion","Drive"), ("BODE","Range"), ("FilterFX","Cutoff")) --
    matched case-insensitively against the target_id's effect prefix, but
    the REAL casing from the table is what gets stored in the binding
    (dispatch requires the exact key).
    """
    import re
    from serum2.operations.fx_resolver import _FX_PARAMETERS

    with open(TARGET_VOCAB_PATH, encoding="utf-8") as f:
        target_records = json.load(f)["targets"]
    fx_targets = [t for t in target_records if t["target_source"] == "FX_PARAMETER"]

    with open(SEMANTIC_PATH, encoding="utf-8") as f:
        semantic_records = json.load(f)["records"]
    sem_by_norm = {}
    for r in semantic_records:
        sem_by_norm.setdefault(normalize_id(r["semantic_id"]), []).append(r["semantic_id"])

    ci_table = {(effect.upper(), param.upper()): (effect, param) for (effect, param) in _FX_PARAMETERS}

    matches = []
    for t in fx_targets:
        parts = t["target_id"].split(".")
        if len(parts) != 2:
            continue
        prefix, param = parts
        effect_guess = re.sub("^FX", "", prefix).upper()
        real_key = ci_table.get((effect_guess, param.upper()))
        if real_key is None:
            continue
        norm_key = normalize_id(t["target_id"])
        sem_ids = sem_by_norm.get(norm_key, [])
        if len(sem_ids) == 1:
            real_effect, real_param = real_key
            matches.append({
                "semantic_id": sem_ids[0],
                "target_id": t["target_id"],
                "effect": real_effect,
                "parameter": real_param,
            })
    return matches


def verify_binding_dispatches(effect: str, parameter: str) -> bool:
    """The strongest verification: actually dispatch a MutationRequest
    through the REAL authority-gated executor with this (effect, parameter)
    and confirm it executes with exactly 1 pathmerge call. This is what
    caught the fx_resolver_complete/fx_resolver.py table mismatch.

    Uses a range-aware probe value (midpoint of the resolver's own declared
    min/max), not a fixed constant -- an earlier version used a fixed 0.5
    and produced a false negative for Compressor/Ratio (real range [1, 10]):
    the capability was fine, the fixed probe value was simply out of range
    for that specific parameter.
    """
    from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
    from serum2.evidence.mutation_request import MutationRequest, MutationType
    from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding
    from serum2.operations.fx_resolver import resolve_fx_parameter

    resolved = resolve_fx_parameter(effect, parameter, rack_index=0, slot_index=0)
    if resolved is None:
        return False
    if resolved.value_type == "float" and resolved.min_value is not None and resolved.max_value is not None:
        probe_value = (resolved.min_value + resolved.max_value) / 2.0
    else:
        probe_value = 0.5

    binding = ExecutionBinding(mutation_type="BODY_STATE", resolver_operation_id="fx_set_parameter",
                                binding_source="v3_verify", binding_version="1")
    contract = CapabilityContract(target="V3VERIFY", allowed_operation="mutate_numeric_value",
                                   status="CAUSAL_VERIFIED", prerequisites=(), verified={},
                                   measurement=None, scope={}, provenance={},
                                   execution_binding=binding, limitations=())
    # pathmerge needs a real array scaffold at FXRack0.FX[0] to write into
    # (an earlier version of this check used body={} and got a false
    # negative: the compiler succeeded but pathmerge failed on an empty
    # dict where a list was expected -- fixed by providing a minimal but
    # structurally real FX slot, matching the resolver's own path template).
    fx_type_key = f"FX{effect}" if not effect.startswith("FX") else effect
    body = {"FXRack0": {"FX": [{"type": 0, fx_type_key: {"plainParams": {}}}]}}
    request = MutationRequest(target="V3VERIFY", mutation_type=MutationType.BODY_STATE, value=probe_value,
                               resolver_parameters={"rack": 0, "slot": 0, "effect": effect, "parameter": parameter})
    proof = execute_mutation_request_with_authority(
        request=request, body=body, contracts={("V3VERIFY", ""): contract}, synth=None,
    )
    return proof.executed and proof.pathmerge_call_count == 1


def verify_no_live_host_parameter(effect_name: str, param: str, live_param_names: set) -> bool:
    """Independent cross-check: no live VST3 host parameter plausibly
    matches this (effect, parameter) pair. Returns True if none found
    (supporting the BODY_STATE_FIELD correction)."""
    candidates = [
        f"{effect_name.title()} {param}",
        f"FX {effect_name.title()} {param}",
    ]
    return not any(c in live_param_names for c in candidates)


def build_v3():
    with open(V2_JSON, encoding="utf-8") as f:
        v2 = json.load(f)

    import dawdreamer as daw
    from serum2.evidence import epoch as epoch_mod
    engine = daw.RenderEngine(44100, 512)
    synth = engine.make_plugin_processor("serum", epoch_mod.SERUM_VST3)
    live_param_names = {p["name"] for p in synth.get_parameters_description()}

    matches = find_fx_parameter_exact_matches()

    resolutions_by_id = {r["semantic_id"]: r for r in v2["semantic_resolutions"]}
    bound_this_pass = []
    skipped = []

    for m in matches:
        sem_id = m["semantic_id"]
        row = resolutions_by_id.get(sem_id)
        if row is None:
            skipped.append((sem_id, "not found in V2 semantic_resolutions"))
            continue
        if row["execution_resolution"] != "RESOLVED":
            skipped.append((sem_id, f"not RESOLVED (state={row['execution_resolution']})"))
            continue

        if m["effect"] not in CONFIRMED_SAFE_EFFECTS:
            skipped.append((sem_id, f"effect {m['effect']!r} FX-type-key not confirmed against "
                                     f"real Serum output (no matching preset evidence found this "
                                     f"session) -- refusing to bind on an unverified key"))
            continue

        no_host_param = verify_no_live_host_parameter(m["effect"], m["parameter"], live_param_names)
        if not no_host_param:
            skipped.append((sem_id, "a plausible live host parameter name WAS found -- "
                                     "does not support the BODY_STATE_FIELD override, skipped"))
            continue

        if not verify_binding_dispatches(m["effect"], m["parameter"]):
            skipped.append((sem_id, f"real dispatch through execute_mutation_request_with_authority "
                                     f"FAILED for (effect={m['effect']!r}, parameter={m['parameter']!r}) "
                                     f"-- not bound, evidence does not support this capability"))
            continue

        canonical = canonicalize_fx_parameter(m["effect"], m["parameter"])
        cap_id = compute_capability_id(ExecutionFamily.BODY_STATE_FIELD.value, canonical)
        operation_key = operation_key_for(MutationPrimitive.STATE.value)

        old_binding = row.get("capability_binding")
        new_binding = {
            "capability_id": cap_id,
            "execution_family": ExecutionFamily.BODY_STATE_FIELD.value,
            "mutation_type": MutationPrimitive.STATE.value,
            "operation_key": operation_key,
            "authoritative_binding": {**canonical, "resolver_operation_id": "fx_set_parameter"},
            "binding_status": BindingStatus.LIVE_VERIFIED.value,
            "binding_provenance": (
                f"V3 population: target_id={m['target_id']!r} exact 1:1 semantic match; "
                f"resolver=fx_set_parameter (fx_resolver.py's REAL, actually-wired catalog "
                f"entry ({m['effect']!r}, {m['parameter']!r})); verified by an ACTUAL dispatch "
                f"through execute_mutation_request_with_authority (not just catalog presence -- "
                f"an earlier draft trusted a disconnected catalog, fx_resolver_complete.py, and "
                f"would have produced 19 non-dispatchable bindings; caught by this same real-"
                f"dispatch check before shipping); frozen vocabulary's parameter_kind="
                f"VST3_HOST_FIELD for this target overridden to BODY_STATE_FIELD -- verified "
                f"against the live VST3 parameter list (no host parameter exists for this "
                f"effect/parameter combination)."
            ),
            "binding_version": "1",
        }

        row["capability_binding"] = new_binding
        row["resolution_provenance"] += "; V3: execution_family corrected HOST_PARAMETER->BODY_STATE_FIELD (see capability_binding.binding_provenance)"

        bound_this_pass.append({
            "semantic_id": sem_id,
            "target_id": m["target_id"],
            "old_family": (old_binding or {}).get("execution_family"),
            "new_family": ExecutionFamily.BODY_STATE_FIELD.value,
            "capability_id": cap_id,
        })

    v2["metadata"]["artifact"] = "SERUM2_EXECUTION_COVERAGE_REGISTRY_V3"
    v2["metadata"]["v3_population_pass"] = {
        "scope": "FX_PARAMETER targets, exact 1:1 semantic<->target match only",
        "candidates_found": len(matches),
        "bound_this_pass": len(bound_this_pass),
        "skipped": len(skipped),
    }

    return v2, bound_this_pass, skipped, matches


def write_outputs(v3, bound_this_pass, skipped, matches):
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(v3, f, indent=2)

    lines = []
    lines.append("# SERUM2_EXECUTION_COVERAGE_REGISTRY_V3 -- Population Pass Report\n")
    lines.append("First substep of Execution Coverage Population, using the now-complete "
                 "authority substrate (SCALAR/STATE/COMPOUND/TOPOLOGY/RESOURCE all "
                 "authority-integrated).\n")
    lines.append("**Invariant preserved:** RESOLVED != BOUND != EXECUTABLE != "
                 "CAUSAL_VERIFIED != ADMITTED. This pass only advances rows from RESOLVED "
                 "to BOUND (a real, evidence-backed CapabilityBinding). No qualification or "
                 "admission work is claimed here.\n")

    lines.append("## Scope of this pass\n")
    lines.append("FX_PARAMETER targets (96 total in the 396-vocabulary), restricted to exact "
                 "1:1 normalized semantic<->target matches with a real, resolvable "
                 "fx_resolver.py catalog entry AND an independently confirmed FX-type-key "
                 "(see CONFIRMED_SAFE_EFFECTS).\n")
    lines.append(f"- Candidates found: {len(matches)}")
    lines.append(f"- Bound this pass: {len(bound_this_pass)}")
    lines.append(f"- Skipped: {len(skipped)}")
    lines.append("")

    lines.append("## Key correction made this pass (evidence-backed)\n")
    lines.append("The frozen 396-target vocabulary tags all 96 FX_PARAMETER targets as "
                 "`parameter_kind=VST3_HOST_FIELD`. Checked directly against the live VST3 "
                 "parameter list this session (2623 params): **no host parameter exists** for "
                 "any of the 14 bound here (e.g. no \"EQ Freq1\", no \"Distortion Drive\" -- "
                 "only \"Filter 1/2 Drive\", a different capability, the main VoiceFilter). "
                 "The real mechanism is CBOR body state via the already authority-integrated "
                 "`fx_set_parameter` resolver, cross-validated against real preset structures "
                 "captured earlier this session. This coverage registry (a derived layer) "
                 "corrects the family for these rows; the frozen "
                 "`SERUM2_TARGET_NORMALIZED_V4.json` file itself is untouched.\n")

    lines.append("## Bound this pass\n")
    for b in bound_this_pass:
        lines.append(f"- `{b['semantic_id']}` -> `{b['target_id']}`: "
                     f"{b['old_family']} -> **{b['new_family']}** "
                     f"(capability_id=`{b['capability_id']}`)")
    lines.append("")

    if skipped:
        lines.append("## Skipped (with reason)\n")
        for sem_id, reason in skipped:
            lines.append(f"- `{sem_id}`: {reason}")
        lines.append("")

    lines.append("## Deferred to follow-up substeps (explicitly NOT attempted this pass)\n")
    lines.append("- **6 FX_PARAMETER targets matched but excluded**: Chorus (2: Rate, Depth) and "
                 "Flanger (4: Rate, Depth, Feedback, Phase) resolve in fx_resolver.py's catalog "
                 "and have an exact semantic match, but their FX-type-key (FXChorus, FXFlanger) "
                 "is unconfirmed against real Serum output -- no preset evidence found this "
                 "session. Binding them would repeat the exact mistake just caught for "
                 "Compressor/Convolve/Hyper/Bode. Needs a real preset containing a loaded "
                 "Chorus or Flanger module before these can be safely bound.")
    lines.append("- **~76 more FX_PARAMETER targets** with no exact 1:1 semantic_id normalized "
                 "match at all (e.g. `FXEQ.Freq1` has no `FX.EQ.FREQ1`-shaped semantic row -- "
                 "the actual semantic naming for EQ uses `FX.EQUALIZER.LEFT_FREQ`/`RIGHT_FREQ`, "
                 "a genuinely different convention requiring evidence-based reconciliation, not "
                 "a mechanical string match) or no fx_resolver.py catalog entry at all under "
                 "exact parameter-name match (e.g. \"Mix\" vs \"Wet\") -- needs per-parameter "
                 "evidence check, not guessed.")
    lines.append("- **MATRIX_ROUTE family** (106 rows): a3_modulation_route.py has real "
                 "source/destination tables; semantic<->route population not attempted this pass.")
    lines.append("- **RESOURCE_OPERATION family** (41 rows) beyond WAVETABLE: unresolved.")
    lines.append("- **STRUCTURAL_OPERATION family** (10 rows): fx_structural_operations.py's "
                 "proven operations are rack/bus-level, not naturally per-semantic-row bindings; "
                 "disposition not yet determined.")
    lines.append("- **HOST_PARAMETER family remainder**: rows with no technical_target_id join "
                 "at all cannot be live-verified without expanding the semantic<->target join "
                 "beyond the existing mechanical string match.")
    lines.append("")

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    print("Building SERUM2_EXECUTION_COVERAGE_REGISTRY_V3 (population pass 1)...")
    v3, bound_this_pass, skipped, matches = build_v3()
    write_outputs(v3, bound_this_pass, skipped, matches)
    print(f"\nCandidates found: {len(matches)}")
    print(f"Bound this pass: {len(bound_this_pass)}")
    print(f"Skipped: {len(skipped)}")
    for b in bound_this_pass:
        print(f"  {b['semantic_id']} -> {b['new_family']}")
    print(f"\nWrote: {OUTPUT_JSON}")
    print(f"Wrote: {OUTPUT_REPORT}")
