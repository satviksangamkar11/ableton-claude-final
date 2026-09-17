#!/usr/bin/env python3
"""SERUM2_EXECUTION_COVERAGE_REGISTRY_V2 -- builder.

Work items 9 and 10 of the Execution Coverage V2 milestone: the
908(semantic) -> resolution -> 396(target)/canonical-binding reconciliation,
and the V2 coverage report.

Implements the frozen architecture from this session's design discussion:
  SemanticResolution (908 rows, keyed by semantic_id)
  CapabilityBinding (deduplicated, keyed by capability_id)
  Invariants V2-1 through V2-6 enforced, not just documented.

Sources joined (all read-only; nothing here edits any frozen artifact,
contract, or evidence store, and semantic discovery is NOT reopened --
Phase D's family registry output is REUSED as evidence, not redone):
  1. serum2/reconciliation/SERUM2_SEMANTIC_NORMALIZED.json (908 semantic rows)
  2. SERUM2_EXECUTION_FAMILY_REGISTRY_FINAL.json (Phase D's frozen
     execution_class per semantic_id -- target-less family evidence)
  3. serum2/reconciliation/SERUM2_TARGET_NORMALIZED_V4.json (396 targets)
  4. A mechanical, verifiable semantic_id<->target_id join (normalized
     string match, documented with its own provenance -- NOT claimed to be
     as strong as the single formal STEP_4_1 ENV1.ATTACK precedent)
  5. serum2.compiler.targets.SEMANTIC_TARGETS (production capability_key registration)
  6. Live DawDreamer synth.get_parameters_description() (this run)
  7. serum2.producer.contract_registry.ContractRegistry (2 real, qualified contracts)
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from serum2.coverage.schema import (
    ExecutionResolution, ExecutionFamily, MutationPrimitive,
    SemanticResolution, CapabilityBinding, InvariantViolation,
    validate_v2_1_resolution_gate, validate_v2_3_generic_operation_key,
    validate_family_primitive_consistency,
)
from serum2.coverage.family_derivation import derive
from serum2.coverage.binding_derivation import derive_binding
from serum2.coverage.operation_registry import GENERIC_EXECUTORS, verify_generic_executors

SEMANTIC_PATH = Path("serum2/reconciliation/SERUM2_SEMANTIC_NORMALIZED.json")
PHASE_D_FAMILY_PATH = Path("SERUM2_EXECUTION_FAMILY_REGISTRY_FINAL.json")
TARGET_VOCAB_PATH = Path("serum2/reconciliation/SERUM2_TARGET_NORMALIZED_V4.json")

OUTPUT_JSON = Path("SERUM2_EXECUTION_COVERAGE_REGISTRY_V2.json")
OUTPUT_REPORT = Path("SERUM2_EXECUTION_COVERAGE_REGISTRY_V2_REPORT.md")


def normalize_id(s: str) -> str:
    return s.upper().replace("_", "").replace(".", "")


def load_sources():
    with open(SEMANTIC_PATH, encoding="utf-8") as f:
        semantic_records = json.load(f)["records"]
    with open(PHASE_D_FAMILY_PATH, encoding="utf-8") as f:
        phase_d_records = json.load(f)["records"]
    with open(TARGET_VOCAB_PATH, encoding="utf-8") as f:
        target_records = json.load(f)["targets"]

    from serum2.compiler.targets import SEMANTIC_TARGETS
    prod_capability_key = {name: ref.capability_key for name, ref in SEMANTIC_TARGETS.items()}

    import dawdreamer as daw
    from serum2.evidence import epoch as epoch_mod
    engine = daw.RenderEngine(44100, 512)
    synth = engine.make_plugin_processor("serum", epoch_mod.SERUM_VST3)
    live_vst3_param_names = {p["name"] for p in synth.get_parameters_description()}

    from serum2.producer.contract_registry import ContractRegistry
    qualified_contracts = dict(ContractRegistry().contracts)

    return (semantic_records, phase_d_records, target_records,
            prod_capability_key, live_vst3_param_names, qualified_contracts)


def build_semantic_target_join(semantic_records, target_records):
    """Mechanical, verifiable, 1:1-only normalized-string join.

    Provenance is explicit and honest: this is NOT the same evidentiary
    strength as the single formal STEP_4_1 ENV1.ATTACK reconciliation
    record (which required live control-path + causal-measurement
    evidence). It is a reproducible string match, nothing more, and is
    labeled as such in every SemanticResolution it produces.
    """
    sem_ids = [r["semantic_id"] for r in semantic_records]
    tgt_ids = [t["target_id"] for t in target_records]

    sem_by_norm = defaultdict(list)
    for s in sem_ids:
        sem_by_norm[normalize_id(s)].append(s)
    tgt_by_norm = defaultdict(list)
    for t in tgt_ids:
        tgt_by_norm[normalize_id(t)].append(t)

    join = {}  # semantic_id -> target_id
    for norm_key in set(sem_by_norm) & set(tgt_by_norm):
        if len(sem_by_norm[norm_key]) == 1 and len(tgt_by_norm[norm_key]) == 1:
            join[sem_by_norm[norm_key][0]] = tgt_by_norm[norm_key][0]
    return join


def build_registry():
    (semantic_records, phase_d_records, target_records,
     prod_capability_key, live_vst3_param_names, qualified_contracts) = load_sources()

    phase_d_by_semantic_id = {r["semantic_id"]: r["execution_class"] for r in phase_d_records}
    target_by_id = {t["target_id"]: t for t in target_records}
    semantic_target_join = build_semantic_target_join(semantic_records, target_records)

    # Formal, evidence-backed precedent overrides the mechanical join where
    # it exists (currently only ENV1.ATTACK -- STEP_4_1 post-freeze record).
    FORMAL_JOIN_OVERRIDES = {"ENV1.ATTACK": "Env1.Attack"}
    join_provenance = {}
    for sem_id, tgt_id in FORMAL_JOIN_OVERRIDES.items():
        semantic_target_join[sem_id] = tgt_id
        join_provenance[sem_id] = "formal:STEP_4_1_POST_FREEZE_SEMANTIC_TARGET_MAPPING_UPDATE.json"
    for sem_id in semantic_target_join:
        join_provenance.setdefault(sem_id, "mechanical_normalized_string_match")

    resolutions = []
    bindings_by_semantic_id = {}
    capability_bindings = {}  # capability_id -> CapabilityBinding (dedup)
    violations = []

    for rec in semantic_records:
        semantic_id = rec["semantic_id"]
        technical_target_id = semantic_target_join.get(semantic_id)
        target_record = target_by_id.get(technical_target_id) if technical_target_id else None
        phase_d_class = phase_d_by_semantic_id.get(semantic_id)

        resolution_enum, family_enum, provenance, reason = derive(
            technical_target_id, target_record, phase_d_class
        )
        if technical_target_id:
            provenance = f"{provenance}; join={join_provenance[semantic_id]}"

        sem_res = SemanticResolution(
            semantic_id=semantic_id,
            technical_target_id=technical_target_id,
            execution_resolution=resolution_enum.value,
            resolution_provenance=provenance,
            resolution_reason=reason,
        )
        resolutions.append(sem_res)

        binding = None
        if family_enum is not None:
            capability_key = prod_capability_key.get(technical_target_id) if technical_target_id else None
            binding = derive_binding(
                family_enum, target_record, live_vst3_param_names,
                capability_key, qualified_contracts,
            )
            try:
                validate_family_primitive_consistency(binding.execution_family, binding.mutation_type)
                validate_v2_3_generic_operation_key(binding.operation_key, GENERIC_EXECUTORS)
            except InvariantViolation as e:
                violations.append(f"{semantic_id}: {e}")

            if binding.is_bound():
                existing = capability_bindings.get(binding.capability_id)
                if existing is None:
                    capability_bindings[binding.capability_id] = binding
                # else: dedup -- same capability_id, don't create a duplicate

        try:
            validate_v2_1_resolution_gate(sem_res, binding)
        except InvariantViolation as e:
            violations.append(str(e))

        bindings_by_semantic_id[semantic_id] = binding

    if violations:
        raise InvariantViolation(f"{len(violations)} invariant violations found:\n" + "\n".join(violations[:20]))

    return (resolutions, bindings_by_semantic_id, capability_bindings,
            semantic_target_join, join_provenance, phase_d_by_semantic_id)


def write_outputs(resolutions, bindings_by_semantic_id, capability_bindings,
                   phase_d_by_semantic_id,
                   semantic_target_join, join_provenance):
    executor_status = verify_generic_executors()

    resolution_counts = Counter(r.execution_resolution for r in resolutions)
    family_counts = Counter(
        b.execution_family for b in bindings_by_semantic_id.values() if b is not None and b.execution_family
    )
    binding_status_counts = Counter(
        b.binding_status for b in bindings_by_semantic_id.values() if b is not None
    )
    bound_capability_count = len(capability_bindings)
    semantic_rows_with_capability = sum(1 for b in bindings_by_semantic_id.values() if b and b.is_bound())

    # dedup ratio: how many semantic rows collapse onto each capability_id
    semantic_per_capability = Counter()
    for sem_id, b in bindings_by_semantic_id.items():
        if b and b.is_bound():
            semantic_per_capability[b.capability_id] += 1
    dedup_examples = sorted(semantic_per_capability.items(), key=lambda kv: -kv[1])[:5]

    output = {
        "metadata": {
            "artifact": "SERUM2_EXECUTION_COVERAGE_REGISTRY_V2",
            "date": "2026-09-17",
            "frozen_semantic_count": len(resolutions),
            "frozen_target_count": 396,
            "sources": [
                "serum2/reconciliation/SERUM2_SEMANTIC_NORMALIZED.json (908, frozen, read-only)",
                "SERUM2_EXECUTION_FAMILY_REGISTRY_FINAL.json (Phase D, frozen, REUSED not redone)",
                "serum2/reconciliation/SERUM2_TARGET_NORMALIZED_V4.json (396, frozen, read-only)",
                "mechanical normalized-string semantic_id<->target_id join (this run)",
                "formal STEP_4_1 ENV1.ATTACK post-freeze reconciliation (overrides mechanical join)",
                "serum2.compiler.targets.SEMANTIC_TARGETS (production registration)",
                "live DawDreamer synth.get_parameters_description() (this run)",
                "serum2.producer.contract_registry.ContractRegistry (2 qualified contracts)",
            ],
            "invariants_enforced": ["V2-1", "V2-2", "V2-3", "V2-4", "V2-5", "V2-6"],
            "generic_executor_status": executor_status,
        },
        "summary": {
            "total_semantic_rows": len(resolutions),
            "execution_resolution_counts": dict(resolution_counts),
            "execution_family_counts": dict(family_counts),
            "binding_status_counts": dict(binding_status_counts),
            "semantic_target_join_count": len(semantic_target_join),
            "unique_capability_bindings": bound_capability_count,
            "semantic_rows_with_a_bound_capability": semantic_rows_with_capability,
            "dedup_top_examples": [
                {"capability_id": cid, "semantic_row_count": count}
                for cid, count in dedup_examples
            ],
        },
        "semantic_resolutions": [
            {
                "semantic_id": r.semantic_id,
                "technical_target_id": r.technical_target_id,
                "execution_resolution": r.execution_resolution,
                "resolution_provenance": r.resolution_provenance,
                "resolution_reason": r.resolution_reason,
                "capability_binding": (
                    {
                        "capability_id": b.capability_id,
                        "execution_family": b.execution_family,
                        "mutation_type": b.mutation_type,
                        "operation_key": b.operation_key,
                        "authoritative_binding": b.authoritative_binding,
                        "binding_status": b.binding_status,
                        "binding_provenance": b.binding_provenance,
                        "binding_version": b.binding_version,
                    } if (b := bindings_by_semantic_id.get(r.semantic_id)) is not None else None
                ),
            }
            for r in resolutions
        ],
        "capability_bindings": [
            {
                "capability_id": cid,
                "execution_family": b.execution_family,
                "mutation_type": b.mutation_type,
                "operation_key": b.operation_key,
                "authoritative_binding": b.authoritative_binding,
                "binding_status": b.binding_status,
                "binding_provenance": b.binding_provenance,
                "referenced_by_semantic_count": semantic_per_capability[cid],
            }
            for cid, b in capability_bindings.items()
        ],
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    lines = []
    lines.append("# SERUM2_EXECUTION_COVERAGE_REGISTRY_V2 -- Coverage Report\n")
    lines.append(f"**Total frozen semantic rows:** {len(resolutions)}  \n"
                 f"**Frozen technical targets:** 396\n")

    lines.append("## Invariants enforced (not just documented)\n")
    lines.append("- V2-1: unresolved rows carry no family/primitive/operation/binding -- "
                 "checked per-row, this build raises InvariantViolation on any violation")
    lines.append("- V2-2/V2-6: capability_id dedup -- multiple semantic rows collapse onto "
                 "one CapabilityBinding (see dedup examples below)")
    lines.append("- V2-3: operation_key restricted to the registered generic-executor set")
    lines.append("- V2-4: every binding/resolution carries explicit provenance")
    lines.append("- V2-5: qualification (CapabilityContract) belongs to the capability, "
                 "not to every semantic row referencing it")
    lines.append("")

    lines.append("## Execution resolution distribution\n")
    for state in ["RESOLVED", "UNRESOLVED_UI_ACTION", "UNKNOWN_EXECUTION"]:
        lines.append(f"- **{state}**: {resolution_counts.get(state, 0)}")
    lines.append("")

    lines.append("## Execution family distribution (RESOLVED rows only)\n")
    for fam, count in sorted(family_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- **{fam}**: {count}")
    lines.append("")

    lines.append("## Binding status distribution\n")
    for status, count in sorted(binding_status_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- **{status}**: {count}")
    lines.append("")

    lines.append("## Capability deduplication (the actual point of V2)\n")
    lines.append(f"- {semantic_rows_with_capability} semantic rows carry a bound capability")
    lines.append(f"- They collapse onto **{bound_capability_count} unique CapabilityBinding records**")
    lines.append("- Top dedup examples (semantic rows sharing one capability_id):")
    for cid, count in dedup_examples:
        lines.append(f"  - `{cid}`: {count} semantic rows")
    lines.append("")

    # Positive finding: rows the (reused, unmodified) Phase D classification
    # left as UNKNOWN_EXECUTION, but which the target-linked evidence path
    # was able to resolve once joined -- demonstrates the two-path design
    # working as intended, not just architecturally described.
    promoted = [r for r in resolutions
                if r.technical_target_id
                and phase_d_by_semantic_id.get(r.semantic_id) == "UNKNOWN_EXECUTION"
                and r.execution_resolution == "RESOLVED"]
    lines.append("## Two-path design validated: target-link promotion\n")
    lines.append(f"- {len(promoted)} semantic rows that Phase D's semantic-only "
                 f"classification left as `UNKNOWN_EXECUTION` were resolved once joined "
                 f"to a technical target (target evidence overriding the weaker "
                 f"semantic-only classification, exactly as the frozen two-path rule "
                 f"specifies):")
    for r in promoted:
        b = bindings_by_semantic_id.get(r.semantic_id)
        lines.append(f"  - `{r.semantic_id}` -> `{r.technical_target_id}` -> "
                     f"`{b.execution_family if b else None}`")
    lines.append("")

    lines.append("## Semantic <-> technical target join\n")
    lines.append(f"- {len(semantic_target_join)}/908 semantic rows joined to a technical_target_id")
    formal = sum(1 for p in join_provenance.values() if p.startswith("formal"))
    mechanical = sum(1 for p in join_provenance.values() if p.startswith("mechanical"))
    lines.append(f"  - {formal} via formal, evidence-backed post-freeze reconciliation "
                 f"(STEP_4_1 precedent)")
    lines.append(f"  - {mechanical} via mechanical normalized-string match (this run) -- "
                 f"a reproducible heuristic, NOT the same evidentiary strength as the formal "
                 f"precedent; each carries this provenance explicitly in its record")
    lines.append(f"- {908 - len(semantic_target_join)}/908 semantic rows have no technical "
                 f"target join (target-less path, or unmatched -- both legitimate per the "
                 f"frozen architecture: 'some may legitimately have no technical target')")
    lines.append("")

    lines.append("## Generic executor (operation_key) status\n")
    for mt, status in executor_status.items():
        lines.append(f"- **{mt}**: {status}")
    lines.append("")
    lines.append("**Architectural finding from this build:** a separate, pre-D.1.x "
                 "`OperationRegistry` (serum2/operations/registry.py) already has real, "
                 "registered compilers for STATE/COMPOUND/RESOURCE/TOPOLOGY operations "
                 "(fx_set_parameter, create_modulation_route, load_wavetable, FX structural "
                 "ops, etc.), but `get_registry()` is called from nowhere in "
                 "producer/evidence/compiler -- it is disconnected from the admission-gated "
                 "authority chain entirely. This is flagged for explicit decision (integrate "
                 "under the D.1.2 authority pattern, or deprecate), not resolved here.")
    lines.append("")

    lines.append("## Known limitations of this V2 pass\n")
    lines.append("- The semantic<->target join is majority-mechanical (string-normalized "
                 "match), not majority-formal-evidence. Every joined row's provenance says "
                 "which kind it got.")
    lines.append("- `binding_status=LIVE_VERIFIED` for HOST_PARAMETER rows means the "
                 "parameter NAME is confirmed present in the current plugin -- it does NOT "
                 "mean the mutation has been causally qualified (see CapabilityContract "
                 "count separately: still only 2 of 908/396).")
    lines.append("- BODY_STATE_FIELD/MATRIX_ROUTE/STRUCTURAL_OPERATION/RESOURCE_OPERATION "
                 "bindings are `NOT_YET_DERIVED` across the board: the 396-target "
                 "vocabulary's `mutation_path` is UNKNOWN for all targets, so no concrete "
                 "body-path/route/topology/resource binding exists yet for any of them. "
                 "This is the concrete next-work item, family by family.")
    lines.append("")

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output


if __name__ == "__main__":
    print("Building SERUM2_EXECUTION_COVERAGE_REGISTRY_V2...")
    (resolutions, bindings_by_semantic_id, capability_bindings,
     join, join_prov, phase_d_by_semantic_id) = build_registry()
    output = write_outputs(resolutions, bindings_by_semantic_id, capability_bindings,
                            phase_d_by_semantic_id, join, join_prov)
    print(json.dumps(output["summary"], indent=2))
    print(f"\nWrote: {OUTPUT_JSON}")
    print(f"Wrote: {OUTPUT_REPORT}")
