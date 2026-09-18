"""
PHASE 4A: SERUM CONTROL LAYER MATRIX BUILDER

Consolidates ALL existing reconciliation work (no re-derivation, no new
experiments) into one canonical disposition per semantic row (908) and
per normalized target (396).

Frozen inputs (read-only):
  - SERUM2_EXECUTION_FAMILY_REGISTRY_EXACT_908.json (908 semantic rows)
  - serum2/reconciliation/SERUM2_TARGET_NORMALIZED_V4.json (396 targets)
  - SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json (living per-row registry,
    already has 908 rows populated by prior V3/V4 reconciliation passes)
  - serum2/reconciliation/PHASE_2D6J_BIDIRECTIONAL_RECONCILIATION_FINAL.json
    (final bidirectional 908<->396 reconciliation)
  - serum2/reconciliation/MATRIX_ROUTE_RECONCILIATION.json (105 MATRIX_ROUTE
    semantic rows, not yet folded into V3)
  - experiments/_capability_contracts.pkl (43 contracts: 32 CAUSAL_VERIFIED,
    8 STRUCTURAL_ONLY, 3 NEGATIVE_EVIDENCE)
  - serum2/compiler/targets.py SEMANTIC_TARGETS (target_id -> capability_key,
    producer registration)
  - serum2/qualification/semantic_vst3_mapping.json (HOST_PARAMETER bindings)
  - serum2/qualification/body_state_mapping.json (BODY_STATE bindings)

Disposition taxonomy (exactly one per row/target):
  A. CAUSAL_PROVEN + ADMITTED         - contract CAUSAL_VERIFIED + binding exists
  B. CAUSAL_PROVEN but blocked        - contract CAUSAL_VERIFIED, no binding wired
  C. machine/UI verified, not causal  - contract STRUCTURAL_ONLY
  D. not-yet-derived                  - no contract, mechanism/family known
  E. unsupported/structural           - RESOURCE/STRUCTURAL UNSUPPORTED_NO_EVIDENCE,
                                         DEAD_OR_SUPERSEDED targets, NEGATIVE_EVIDENCE contracts
  F. unresolved/unknown               - MANY_TO_ONE, BLOCKED_CONTRADICTED, true UNKNOWN
  G. proven-not-user-control          - structural facts / automatic consequences, not actions

No frozen registry, contract, or evidence file is modified by this script.
It only READS existing artifacts and WRITES the three new deliverable files.
"""
import sys, json, pickle
from pathlib import Path
from datetime import datetime

sys.path.insert(0, r"D:\ableton claude")
from serum2.compiler.targets import SEMANTIC_TARGETS

ROOT = Path(r"D:\ableton claude")

# ---------------------------------------------------------------------------
# Load all frozen/authoritative sources (read-only)
# ---------------------------------------------------------------------------

REG_908 = json.load(open(ROOT / "SERUM2_EXECUTION_FAMILY_REGISTRY_EXACT_908.json"))["records"]
TARGETS_396 = json.load(open(ROOT / "serum2/reconciliation/SERUM2_TARGET_NORMALIZED_V4.json"))["targets"]
V3_REGISTRY = json.load(open(ROOT / "SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json"))
V3_ROWS = {r["semantic_id"]: r for r in V3_REGISTRY["semantic_resolutions"]}
RECON_2D6J = json.load(open(ROOT / "serum2/reconciliation/PHASE_2D6J_BIDIRECTIONAL_RECONCILIATION_FINAL.json"))
TABLE_A = RECON_2D6J["table_a_semantic_to_technical"]["assignments"]          # semantic_id -> category
TABLE_B = RECON_2D6J["table_b_technical_to_semantic"]["assignments"]          # target_id -> category
TABLE_C = RECON_2D6J["table_c_2d6i_delta"]["targets_dispositioned"]           # target_id -> delta category
CONTRADICTIONS = {c["semantic_id"]: c for c in RECON_2D6J["contradiction_table"]}
MATRIX_ROUTE = json.load(open(ROOT / "serum2/reconciliation/MATRIX_ROUTE_RECONCILIATION.json"))["rows"]
MATRIX_ROUTE_BY_ID = {r["semantic_id"]: r for r in MATRIX_ROUTE}

CONTRACTS_RAW = pickle.load(open(ROOT / "experiments/_capability_contracts.pkl", "rb"))
CONTRACTS_BY_KEY = {}
for _, contract in CONTRACTS_RAW.items():
    # multiple entries can share target; keep the one with a status (all do)
    CONTRACTS_BY_KEY[contract.target] = contract

HOST_MAPPING = json.load(open(ROOT / "serum2/qualification/semantic_vst3_mapping.json"))["mappings"]
BODY_STATE_MAPPING = json.load(open(ROOT / "serum2/qualification/body_state_mapping.json"))["bindings"]

# The 15 targets with actual fresh Phase-3/4A execution evidence (bulk-tested,
# not merely bound). Everything else that is bound is "admitted, binding
# ready" but not yet bulk-executed with fresh evidence in this project.
EXECUTED_WITH_FRESH_EVIDENCE = {
    "envelope_field_attack", "filter_field_cutoff", "filter_field_reso",
    "oscillator_field_OSC1-DETUNE", "oscillator_field_OSC2-DETUNE",
    "osc1_plain_param_level", "osc2_plain_param_level", "osc3_plain_param_level",
    "fx_field_eq_freq1", "fx_field_eq_kParamGain2", "fx_field_eq_kParamReso2",
    "fx_field_eq_kParamFreq2", "fx_field_eq_kParamGain1", "fx_field_eq_kParamReso1",
    "fx_field_eq_kParamType2",
}

DEAD_TARGET_IDS = {tid for tid, cat in TABLE_B.items() if cat.startswith("DEAD_OR_SUPERSEDED")}
DEAD_TARGET_IDS |= {tid for tid, cat in TABLE_C.items() if cat.startswith("DEAD_OR_SUPERSEDED")}

# ---------------------------------------------------------------------------
# Build target_id -> capability_key map (union of SEMANTIC_TARGETS + 396 file's
# own host_parameter_id, since not all 396 targets are yet registered in the
# producer's SEMANTIC_TARGETS dict)
# ---------------------------------------------------------------------------
TARGET_ID_TO_CAP_KEY = dict(SEMANTIC_TARGETS)  # SemanticTargetRef objects
TARGET_ID_TO_CAP_KEY = {k: v.capability_key for k, v in TARGET_ID_TO_CAP_KEY.items()}


def capability_key_for(target_id, record_396):
    if target_id in TARGET_ID_TO_CAP_KEY:
        return TARGET_ID_TO_CAP_KEY[target_id]
    hp_id = record_396.get("host_parameter_id")
    return hp_id if hp_id else None


# ---------------------------------------------------------------------------
# STEP A: disposition every one of the 396 normalized targets
# ---------------------------------------------------------------------------

def disposition_target(record):
    target_id = record["target_id"]
    cap_key = capability_key_for(target_id, record)
    contract = CONTRACTS_BY_KEY.get(cap_key) if cap_key else None

    row = {
        "target_id": target_id,
        "capability_binding": cap_key,
        "contract": None,
        "status": None,
        "execution_mechanism": None,
        "fixture_requirement": None,
        "current_execution_proven": False,
        "verification_tier": None,
        "final_disposition": None,
        "evidence": None,
    }

    # Dead/superseded targets take priority regardless of contract state
    if target_id in DEAD_TARGET_IDS:
        row.update(final_disposition="E", status="DEAD_OR_SUPERSEDED",
                   verification_tier="NONE",
                   evidence="2D.6J/2D.6I reconciliation: target superseded/dead, no longer a live control")
        return row

    if contract is not None:
        row["contract"] = f"{contract.status} ({cap_key})"
        row["status"] = contract.status

        if contract.status == "CAUSAL_VERIFIED":
            has_body_state = cap_key in BODY_STATE_MAPPING
            has_host_param = cap_key in HOST_MAPPING
            if has_body_state:
                row["execution_mechanism"] = "BODY_STATE (pathmerge)"
                row["fixture_requirement"] = "experiments/_corpus_cache.pkl bodies[4] (FXEQ-populated fixture)"
            elif has_host_param:
                row["execution_mechanism"] = f"HOST_PARAMETER (DawDreamer: '{HOST_MAPPING[cap_key]}')"
                row["fixture_requirement"] = "none (default Serum skeleton)"

            if has_body_state or has_host_param:
                proven = cap_key in EXECUTED_WITH_FRESH_EVIDENCE
                row["current_execution_proven"] = proven
                row["verification_tier"] = "EXECUTED_WITH_FRESH_EVIDENCE" if proven else "ADMITTED_BINDING_READY_UNTESTED"
                row["final_disposition"] = "A"
                row["evidence"] = ("Phase 3/4A bulk execution (baseline->mutation->observed->restored)"
                                    if proven else "CAUSAL_VERIFIED contract + execution_binding attached, no bulk-execution run yet")
            else:
                row["execution_mechanism"] = "NONE (no binding wired)"
                row["verification_tier"] = "CAUSAL_PROVEN_NO_BINDING"
                row["final_disposition"] = "B"
                row["evidence"] = "CAUSAL_VERIFIED contract exists but no HOST_PARAMETER/BODY_STATE binding configured"

        elif contract.status == "STRUCTURAL_ONLY":
            row["execution_mechanism"] = "mutate+persist verified, no causal claim"
            row["verification_tier"] = "STRUCTURAL_ONLY"
            row["final_disposition"] = "C"
            row["evidence"] = "Contract STRUCTURAL_ONLY: construct/mutate/persist gates passed, causal gate NOT_RUN or negative"

        elif contract.status == "NEGATIVE_EVIDENCE":
            row["execution_mechanism"] = "none (gates failed)"
            row["verification_tier"] = "NEGATIVE_EVIDENCE"
            row["final_disposition"] = "E"
            row["evidence"] = "Contract NEGATIVE_EVIDENCE: causal/other gates demonstrably failed in original experiment"
        return row

    # No contract at all -- use 2D.6J table_b / table_c disposition
    cat = TABLE_C.get(target_id) or TABLE_B.get(target_id, "UNKNOWN")
    if cat == "OWNED":
        row["final_disposition"] = "D"
        row["verification_tier"] = "NOT_YET_DERIVED"
        row["evidence"] = "2D.6J table_b: OWNED (a real, named target) but no CapabilityContract / causal evidence yet"
    elif cat in ("UNKNOWN",):
        row["final_disposition"] = "D"
        row["verification_tier"] = "NOT_YET_DERIVED"
        row["evidence"] = "2D.6J table_b: UNKNOWN disposition, no contract"
    elif cat.startswith("MANY_TO_ONE"):
        row["final_disposition"] = "F"
        row["verification_tier"] = "AMBIGUOUS"
        row["evidence"] = "2D.6J table_b: MANY_TO_ONE, multiple semantic rows compete for this target, unresolved"
    elif cat == "MAPPED_TO_EXISTING_SEMANTIC":
        row["final_disposition"] = "D"
        row["verification_tier"] = "NOT_YET_DERIVED"
        row["evidence"] = "2D.6J table_c: mapped to existing semantic row, no independent contract yet"
    else:
        row["final_disposition"] = "F"
        row["verification_tier"] = "UNRESOLVED"
        row["evidence"] = f"2D.6J disposition category: {cat}"
    return row


TARGET_ROWS = [disposition_target(r) for r in TARGETS_396]
TARGET_ROWS_BY_ID = {r["target_id"]: r for r in TARGET_ROWS}

# ---------------------------------------------------------------------------
# STEP B: disposition every one of the 908 semantic rows
# ---------------------------------------------------------------------------

def disposition_semantic(record):
    sem_id = record["semantic_id"]
    v3row = V3_ROWS.get(sem_id, {})
    tech_target = v3row.get("technical_target_id")

    row = {
        "semantic_id": sem_id,
        "normalized_target": tech_target,
        "family": record.get("execution_family_id"),
        "capability_binding": None,
        "contract": None,
        "status": None,
        "execution_mechanism": None,
        "fixture_requirement": None,
        "current_execution_proven": False,
        "verification_tier": None,
        "final_disposition": None,
        "evidence": None,
    }

    # 1) If joined to a normalized target, inherit that target's disposition
    if tech_target and tech_target in TARGET_ROWS_BY_ID:
        t = TARGET_ROWS_BY_ID[tech_target]
        row.update(
            capability_binding=t["capability_binding"], contract=t["contract"], status=t["status"],
            execution_mechanism=t["execution_mechanism"], fixture_requirement=t["fixture_requirement"],
            current_execution_proven=t["current_execution_proven"], verification_tier=t["verification_tier"],
            final_disposition=t["final_disposition"],
            evidence=f"Joined to normalized target {tech_target}: {t['evidence']}",
        )
        return row

    # 2) MATRIX_ROUTE family: use the dedicated reconciliation (finer grain
    #    than the 2D.6J bulk category, not yet folded into V3)
    if sem_id in MATRIX_ROUTE_BY_ID:
        mr = MATRIX_ROUTE_BY_ID[sem_id]
        bucket = mr["bucket"]
        if bucket == "PROVEN_NOT_USER_CONTROL":
            row.update(final_disposition="G", verification_tier="PROVEN_NOT_USER_CONTROL", evidence=mr["evidence"])
        elif bucket == "UNSUPPORTED_NO_EVIDENCE":
            row.update(final_disposition="E", verification_tier="UNSUPPORTED_NO_EVIDENCE", evidence=mr["evidence"])
        elif bucket == "EXISTING_EXECUTABLE_DIFFERENT_MECHANISM":
            row.update(final_disposition="D", verification_tier="MECHANISM_KNOWN_PREREQ_UNMET", evidence=mr["evidence"])
        else:
            row.update(final_disposition="F", verification_tier="UNRESOLVED", evidence=mr["evidence"])
        return row

    # 3) Contradiction table entries
    if sem_id in CONTRADICTIONS:
        c = CONTRADICTIONS[sem_id]
        row.update(final_disposition="F", verification_tier="BLOCKED_CONTRADICTED",
                   evidence=f"{c['resolution']} (old={c['old_evidence']}, new={c['new_evidence']})")
        return row

    # 4) Fall back to V3 registry's own capability_binding if present
    cb = v3row.get("capability_binding")
    if cb and cb.get("binding_status") == "LIVE_VERIFIED":
        row.update(final_disposition="D",
                    verification_tier="LIVE_VERIFIED_NO_TARGET_JOIN",
                    execution_mechanism=cb.get("mutation_type"),
                    evidence=f"V3 registry: LIVE_VERIFIED binding ({cb.get('binding_provenance')}) but no normalized-target join")
        return row

    # 5) Fall back to 2D.6J table_a category (908-level bulk disposition)
    cat = TABLE_A.get(sem_id, "UNKNOWN")
    mapping = {
        "UNKNOWN": ("D", "NOT_YET_DERIVED"),
        "CONTROL_PATH_KNOWN_NO_TARGET": ("D", "MECHANISM_KNOWN_NO_TARGET"),
        "PROVEN_NOT_USER_CONTROL": ("G", "PROVEN_NOT_USER_CONTROL"),
        "MANY_TO_ONE": ("F", "AMBIGUOUS"),
        "BLOCKED_CONTRADICTED": ("F", "BLOCKED_CONTRADICTED"),
        "MAPPED_TO_EXISTING_TARGET": ("D", "MAPPED_LINK_NOT_MACHINE_JOINED"),
    }
    disp, tier = mapping.get(cat, ("F", "UNRESOLVED"))
    row.update(final_disposition=disp, verification_tier=tier,
                evidence=f"2D.6J table_a bulk category: {cat}"
                         + (" (mapped to a target but this pass has no machine-readable link)"
                            if cat == "MAPPED_TO_EXISTING_TARGET" else ""))
    return row


SEMANTIC_ROWS = [disposition_semantic(r) for r in REG_908]

# ---------------------------------------------------------------------------
# STEP C: 908 -> 396 reconciliation check (every semantic row must map to a
# target, an explicit structural/semantic disposition, or a documented
# non-executable classification -- i.e. every row must have final_disposition set)
# ---------------------------------------------------------------------------
unmapped_semantic = [r["semantic_id"] for r in SEMANTIC_ROWS if r["final_disposition"] is None]

# Orphan check: CAUSAL_VERIFIED/STRUCTURAL_ONLY contracts whose capability_key
# is not reachable from ANY of the 396 normalized targets or SEMANTIC_TARGETS
# registration. These are real, proven capabilities sitting outside the
# current semantic vocabulary -- a genuine gap, not something this pass fixes
# (fixing it means registering new targets, which is producer/vocabulary
# expansion, explicitly out of scope for Phase 4A per Step 6).
_reachable_cap_keys = {t["capability_binding"] for t in TARGET_ROWS if t["capability_binding"]}
orphan_contracts = []
for cap_key, contract in CONTRACTS_BY_KEY.items():
    if cap_key not in _reachable_cap_keys:
        orphan_contracts.append({
            "capability_key": cap_key,
            "status": contract.status,
            "has_binding": cap_key in HOST_MAPPING or cap_key in BODY_STATE_MAPPING,
            "note": "CAUSAL_VERIFIED/STRUCTURAL_ONLY contract exists but capability_key is not "
                    "registered in SEMANTIC_TARGETS and not reachable from any of the 396 "
                    "normalized targets -- no semantic name currently reaches this capability.",
        })

# ---------------------------------------------------------------------------
# Assemble outputs
# ---------------------------------------------------------------------------
def counts(rows):
    c = {}
    for r in rows:
        d = r["final_disposition"]
        c[d] = c.get(d, 0) + 1
    return c

target_counts = counts(TARGET_ROWS)
semantic_counts = counts(SEMANTIC_ROWS)

matrix = {
    "metadata": {
        "artifact": "SERUM_CONTROL_LAYER_MATRIX",
        "date": datetime.now().isoformat(),
        "phase": "4A",
        "total_semantic_rows": len(SEMANTIC_ROWS),
        "total_normalized_targets": len(TARGET_ROWS),
        "disposition_taxonomy": {
            "A": "CAUSAL_PROVEN + ADMITTED",
            "B": "CAUSAL_PROVEN but blocked (no execution binding wired)",
            "C": "machine/UI verified but not causally qualified (STRUCTURAL_ONLY)",
            "D": "not-yet-derived",
            "E": "unsupported/structural (incl. DEAD_OR_SUPERSEDED, NEGATIVE_EVIDENCE)",
            "F": "unresolved/unknown (ambiguous, contradicted)",
            "G": "proven-not-user-control",
        },
        "sources_consulted": [
            "SERUM2_EXECUTION_FAMILY_REGISTRY_EXACT_908.json",
            "serum2/reconciliation/SERUM2_TARGET_NORMALIZED_V4.json",
            "SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json",
            "serum2/reconciliation/PHASE_2D6J_BIDIRECTIONAL_RECONCILIATION_FINAL.json",
            "serum2/reconciliation/MATRIX_ROUTE_RECONCILIATION.json",
            "experiments/_capability_contracts.pkl",
            "serum2/compiler/targets.py (SEMANTIC_TARGETS)",
            "serum2/qualification/semantic_vst3_mapping.json",
            "serum2/qualification/body_state_mapping.json",
        ],
        "no_frozen_artifact_modified": True,
    },
    "normalized_target_counts": target_counts,
    "semantic_row_counts": semantic_counts,
    "unmapped_semantic_rows": unmapped_semantic,
    "orphan_contracts_outside_396_vocabulary": orphan_contracts,
    "normalized_targets": TARGET_ROWS,
    "semantic_rows": SEMANTIC_ROWS,
}

out_json = ROOT / "SERUM_CONTROL_LAYER_MATRIX.json"
with open(out_json, "w") as f:
    json.dump(matrix, f, indent=2)

print(f"Wrote {out_json}")
print(f"Normalized target counts: {target_counts}  (sum={sum(target_counts.values())})")
print(f"Semantic row counts:      {semantic_counts}  (sum={sum(semantic_counts.values())})")
print(f"Unmapped semantic rows:   {len(unmapped_semantic)}")
print(f"Orphan contracts (outside 396 vocab): {len(orphan_contracts)}")
for oc in orphan_contracts:
    print(f"  - {oc['capability_key']}: {oc['status']}, bound={oc['has_binding']}")
