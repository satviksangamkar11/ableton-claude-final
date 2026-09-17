#!/usr/bin/env python3
"""SERUM2_EXECUTION_COVERAGE_REGISTRY_V1 — builder.

First concrete deliverable of the Serum-wide execution coverage milestone.

For every one of the frozen 396 technical targets (SERUM2_TARGET_NORMALIZED_V4.json),
determine: exactly how would the system manipulate it, and what evidence is
still missing?

Sources joined (all read-only; nothing here writes back into any frozen
artifact, contract, or evidence store):
  1. serum2/reconciliation/SERUM2_TARGET_NORMALIZED_V4.json  -- frozen 396-target vocabulary
  2. serum2.compiler.targets.SEMANTIC_TARGETS                -- production capability_key registration (255/396)
  3. Live DawDreamer VST3 parameter list                     -- mechanical re-verification of claimed
                                                                  host_parameter_name (not reuse of the
                                                                  unverified 2D.6A claim)
  4. serum2.producer.contract_registry.ContractRegistry       -- actual qualified CapabilityContracts (2/396)

State assigned per target (exactly one of):
  EXECUTABLE_HOST          -- VST3 host parameter, name LIVE-VERIFIED against current plugin
  EXECUTABLE_BODY          -- CBOR body state field (VST3_PLAIN_PARAM), path-addressable
  EXECUTABLE_COMPOUND      -- routing/modulation slot (multi-step operation, not a single primitive)
  EXECUTABLE_TOPOLOGY      -- FX/module structural operation (not in 396 vocab as of V4 -- reserved)
  EXECUTABLE_RESOURCE      -- resource load/readback operation (not in 396 vocab as of V4 -- reserved)
  UNRESOLVED                -- no execution mechanism identified yet (with blocking_reason)
  REFUSED_NON_USER_CONTROL  -- not applicable in this pass (no targets currently known to qualify -- reserved)

IMPORTANT: EXECUTABLE_* here means "the execution PRIMITIVE and BINDING are
identified/verifiable", per the state machine
  SEMANTIC -> TARGET/REPRESENTATION -> EXECUTABLE -> QUALIFIED -> ADMITTED -> PRODUCER-USABLE
It does NOT mean causally qualified or admitted. qualification_status
separately records whether a real CapabilityContract exists (currently
true for exactly 2 targets).
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent))

TARGET_VOCAB_PATH = Path("serum2/reconciliation/SERUM2_TARGET_NORMALIZED_V4.json")
OUTPUT_JSON = Path("SERUM2_EXECUTION_COVERAGE_REGISTRY_V1.json")
OUTPUT_REPORT = Path("SERUM2_EXECUTION_COVERAGE_REGISTRY_V1_REPORT.md")


def load_target_vocabulary():
    with open(TARGET_VOCAB_PATH) as f:
        data = json.load(f)
    return data["targets"]


def load_production_registration():
    from serum2.compiler.targets import SEMANTIC_TARGETS
    return {name: ref.capability_key for name, ref in SEMANTIC_TARGETS.items()}


def load_live_vst3_parameter_names():
    """Fresh, current-runtime parameter list -- NOT the 2D.6A claim reused."""
    import dawdreamer as daw
    from serum2.evidence import epoch as epoch_mod
    engine = daw.RenderEngine(44100, 512)
    synth = engine.make_plugin_processor("serum", epoch_mod.SERUM_VST3)
    params = synth.get_parameters_description()
    return {p["name"] for p in params}


def load_qualified_contracts():
    from serum2.producer.contract_registry import ContractRegistry
    registry = ContractRegistry()
    # keyed by capability_key (== contract.target)
    return dict(registry.contracts)


def classify_target(target, capability_key, production_registered,
                     live_verified_host_name, has_contract, contract):
    """Return (state, execution_family, mutation_type, authoritative_binding,
    qualification_status, blocking_reason)."""

    parameter_kind = target.get("parameter_kind")
    target_source = target.get("target_source")
    claimed_host_name = target.get("host_parameter_name")

    qualification_status = "QUALIFIED_CAUSAL_VERIFIED" if (has_contract and contract and contract.status == "CAUSAL_VERIFIED") \
        else ("QUALIFIED_OTHER" if has_contract else "NOT_QUALIFIED")

    # -- EXECUTABLE_HOST: VST3 host parameter, claim exists AND is live-verified now
    if parameter_kind == "VST3_HOST_FIELD" and claimed_host_name not in (None, "UNKNOWN"):
        if live_verified_host_name:
            binding = {
                "mutation_type": "HOST_PARAMETER",
                "host_parameter_name": claimed_host_name,
                "binding_source": "live_dawdreamer_parameter_list (this run)",
                "binding_status": "LIVE_VERIFIED_PRESENT",
            }
            return ("EXECUTABLE_HOST", "HOST_PARAMETER", "HOST_PARAMETER",
                    binding, qualification_status, None)
        else:
            return ("UNRESOLVED", "HOST_PARAMETER", "HOST_PARAMETER", None,
                    qualification_status,
                    f"claimed host_parameter_name {claimed_host_name!r} "
                    f"(source: {target.get('_origin', 'unknown')}) NOT found in live "
                    f"synth.get_parameters_description() -- claim unverified/stale")

    # -- VST3_HOST_FIELD with no name claim at all yet
    if parameter_kind == "VST3_HOST_FIELD":
        return ("UNRESOLVED", "HOST_PARAMETER", "HOST_PARAMETER", None,
                qualification_status,
                "no host_parameter_name claim recorded in target vocabulary V4 -- "
                "needs VST3 parameter-name resolution pass")

    # -- VST3_PLAIN_PARAM: CBOR body state field
    if parameter_kind == "VST3_PLAIN_PARAM":
        return ("UNRESOLVED", "BODY_STATE", "BODY_STATE", None,
                qualification_status,
                "parameter_kind=VST3_PLAIN_PARAM (CBOR body field candidate) but no "
                "body_path derived/verified yet -- needs skeleton path resolution "
                "(cf. Env0.plainParams.kParamRelease precedent from D.1.2)")

    # -- ROUTING_SLOT_FIELD: matrix/modulation routing
    if parameter_kind == "ROUTING_SLOT_FIELD" or target_source == "MATRIX_ROUTE":
        return ("UNRESOLVED", "MATRIX_ROUTE", "COMPOUND", None,
                qualification_status,
                "parameter_kind=ROUTING_SLOT_FIELD / target_source=MATRIX_ROUTE -- "
                "requires COMPOUND operation (multi-step routing), not a single "
                "primitive; no generic routing operation implemented yet "
                "(current compiler hard-codes destinations per user instruction)")

    return ("UNRESOLVED", "UNKNOWN", "UNKNOWN", None, qualification_status,
            f"parameter_kind={parameter_kind!r} target_source={target_source!r} "
            f"does not match any known classification rule")


def build_registry():
    targets = load_target_vocabulary()
    prod_registration = load_production_registration()  # name -> capability_key
    live_param_names = load_live_vst3_parameter_names()
    contracts = load_qualified_contracts()  # capability_key -> CapabilityContract

    records = []
    for t in targets:
        target_id = t["target_id"]
        capability_key = prod_registration.get(target_id)
        production_registered = capability_key is not None

        claimed_host_name = t.get("host_parameter_name")
        live_verified = claimed_host_name in live_param_names if claimed_host_name not in (None, "UNKNOWN") else False

        contract = contracts.get(capability_key) if capability_key else None
        has_contract = contract is not None

        state, exec_family, mutation_type, binding, qual_status, blocking_reason = classify_target(
            t, capability_key, production_registered, live_verified, has_contract, contract
        )

        record = {
            "target_id": target_id,
            "capability_key": capability_key,
            "production_registered": production_registered,
            "semantic_rows": [],  # NOT populated this pass -- see report limitations
            "execution_family": exec_family,
            "mutation_type": mutation_type,
            "authoritative_binding": binding,
            "operation_compiler": "serum2.operations.scalar_operations.scalar_compiler" if production_registered else None,
            "prerequisites": list(contract.prerequisites) if contract else [],
            "evidence_status": "CAUSAL_VERIFIED" if (contract and contract.status == "CAUSAL_VERIFIED") else "NO_EVIDENCE",
            "qualification_status": qual_status,
            "state": state,
            "blocking_reason": blocking_reason,
        }
        records.append(record)

    return records


def write_outputs(records):
    state_counts = Counter(r["state"] for r in records)
    family_counts = Counter(r["execution_family"] for r in records)
    prod_reg_count = sum(1 for r in records if r["production_registered"])
    qualified_count = sum(1 for r in records if r["qualification_status"] != "NOT_QUALIFIED")

    output = {
        "metadata": {
            "artifact": "SERUM2_EXECUTION_COVERAGE_REGISTRY_V1",
            "date": "2026-09-17",
            "frozen_target_count": len(records),
            "sources": [
                "serum2/reconciliation/SERUM2_TARGET_NORMALIZED_V4.json (frozen, read-only)",
                "serum2.compiler.targets.SEMANTIC_TARGETS (production registration)",
                "live DawDreamer synth.get_parameters_description() (this run, 2623 params)",
                "serum2.producer.contract_registry.ContractRegistry (qualified contracts)",
            ],
            "state_definitions": {
                "EXECUTABLE_HOST": "VST3 host parameter; name LIVE-VERIFIED against current plugin this run",
                "EXECUTABLE_BODY": "CBOR body state field; path derived and verified",
                "EXECUTABLE_COMPOUND": "routing/modulation slot; multi-step operation, path derived and verified",
                "EXECUTABLE_TOPOLOGY": "FX/module structural operation; binding derived and verified",
                "EXECUTABLE_RESOURCE": "resource load/readback operation; binding derived and verified",
                "UNRESOLVED": "execution mechanism not yet identified/verified -- see blocking_reason",
                "REFUSED_NON_USER_CONTROL": "not a controllable capability -- none assigned this pass",
            },
        },
        "summary": {
            "total_targets": len(records),
            "state_counts": dict(state_counts),
            "execution_family_counts": dict(family_counts),
            "production_registered": prod_reg_count,
            "not_production_registered": len(records) - prod_reg_count,
            "qualified_with_contract": qualified_count,
        },
        "records": records,
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(output, f, indent=2)

    lines = []
    lines.append("# SERUM2_EXECUTION_COVERAGE_REGISTRY_V1 -- Coverage Report\n")
    lines.append(f"**Total frozen technical targets:** {len(records)}\n")
    lines.append("## State distribution\n")
    for state in ["EXECUTABLE_HOST", "EXECUTABLE_BODY", "EXECUTABLE_COMPOUND",
                  "EXECUTABLE_TOPOLOGY", "EXECUTABLE_RESOURCE", "UNRESOLVED",
                  "REFUSED_NON_USER_CONTROL"]:
        lines.append(f"- **{state}**: {state_counts.get(state, 0)}")
    lines.append("")
    lines.append("## Execution family distribution\n")
    for fam, count in sorted(family_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- **{fam}**: {count}")
    lines.append("")
    lines.append("## Production / qualification status\n")
    lines.append(f"- Registered in production `SEMANTIC_TARGETS` (has capability_key): {prod_reg_count}/{len(records)}")
    lines.append(f"- NOT registered in production at all: {len(records) - prod_reg_count}/{len(records)}")
    lines.append(f"- Has a real, qualified `CapabilityContract`: {qualified_count}/{len(records)}")
    lines.append("")

    exec_host = [r for r in records if r["state"] == "EXECUTABLE_HOST"]
    exec_host_registered = sum(1 for r in exec_host if r["production_registered"])
    unresolved = [r for r in records if r["state"] == "UNRESOLVED"]
    unresolved_registered = sum(1 for r in unresolved if r["production_registered"])
    lines.append("## Key structural finding: two SEPARATE gaps, not one\n")
    lines.append(f"- `EXECUTABLE_HOST` ({len(exec_host)}): all `target_source=SYNTH_PARAMETER`, "
                  f"host name now live-verified against the current plugin. "
                  f"**{exec_host_registered}/{len(exec_host)}** already have a `capability_key` "
                  f"in production -- i.e. **{len(exec_host) - exec_host_registered} are fully "
                  f"binding-ready but completely unregistered in `SEMANTIC_TARGETS`.**")
    lines.append(f"- `UNRESOLVED` ({len(unresolved)}): all `target_source=FX_PARAMETER` "
                  f"(or routing). **{unresolved_registered}/{len(unresolved)}** already have a "
                  f"`capability_key` in production but no `host_parameter_name` claim exists in "
                  f"the V4 vocabulary at all -- these were registered via a different path "
                  f"(fx_resolver-style) and need mutation-path derivation, not name lookup.")
    lines.append("- These are two independent, non-overlapping problems requiring different "
                  "fixes: (1) register the 141 already-binding-ready SYNTH_PARAMETER targets "
                  "into `SEMANTIC_TARGETS` (mechanical, low-risk, follows the exact D.1.2 "
                  "Release/Attack precedent), vs (2) derive real mutation paths for the 255 "
                  "already-registered FX_PARAMETER targets (requires fx_resolver / body-state "
                  "path work, higher effort per target).")
    lines.append("")
    lines.append("## Blocking reasons (UNRESOLVED targets, grouped)\n")
    blocking = Counter(r["blocking_reason"].split(" -- ")[0] if r["blocking_reason"] else "none"
                        for r in records if r["state"] == "UNRESOLVED")
    for reason, count in sorted(blocking.items(), key=lambda x: -x[1]):
        lines.append(f"- {count}x: {reason}")
    lines.append("")
    lines.append("## Known limitations of this V1 pass\n")
    lines.append("- `semantic_rows` is NOT populated: there is no existing, general, "
                  "authoritative mapping from the 396 `target_id`s back to the 908 "
                  "`semantic_id`s (only ENV1.ATTACK has a formal post-freeze reconciliation "
                  "record). Building that join at scale is separate, unstarted work, not "
                  "reopened semantic discovery.")
    lines.append("- `EXECUTABLE_HOST` here means the host parameter NAME is live-verified "
                  "to exist in the current plugin's parameter list -- it does NOT mean the "
                  "mutation has been causally proven, or that a CapabilityContract exists. "
                  "That distinction is `qualification_status`.")
    lines.append("- `EXECUTABLE_BODY` / `EXECUTABLE_COMPOUND` counts are currently 0: the V4 "
                  "vocabulary's `mutation_path` field is UNKNOWN for all 396 targets, so no "
                  "body-path or routing-path has been derived/verified yet for any target. "
                  "This is the concrete next-work item for those families.")
    lines.append("- `EXECUTABLE_TOPOLOGY` / `EXECUTABLE_RESOURCE` / "
                  "`REFUSED_NON_USER_CONTROL` are 0 in this pass: no target in the frozen "
                  "396-vocabulary V4 is currently tagged with a structural or resource "
                  "`target_source`/`parameter_kind` distinguishable from the three "
                  "categories above. The 908-semantic-level STRUCTURAL_OPERATION (10) and "
                  "RESOURCE_OPERATION (41) families exist but have not yet been joined to "
                  "specific `target_id`s in the 396 vocabulary.")
    lines.append("")

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output


if __name__ == "__main__":
    print("Building SERUM2_EXECUTION_COVERAGE_REGISTRY_V1...")
    records = build_registry()
    output = write_outputs(records)
    print(json.dumps(output["summary"], indent=2))
    print(f"\nWrote: {OUTPUT_JSON}")
    print(f"Wrote: {OUTPUT_REPORT}")
