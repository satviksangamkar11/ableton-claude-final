"""4.Q.4 step 2: Build the fresh 4.1 CapabilityContract from the fresh
release_qualified_complete_001 EvidenceRecord.

Uses the existing, unmodified evidence/claim/capability_contract machinery.
Writes to a SEPARATE store (experiments/_capability_contracts_4_1.pkl) --
never touches or reads from the archived experiments/_capability_contracts.pkl.
Per 4.Q.3 section 7.3: archived store is historical; this store is the sole
authoritative source for the 4.1 runtime proof.
"""
import sys, pickle
sys.path.insert(0, r"D:\ableton claude")
from serum2.evidence.claim import ClaimDefinition, ClaimEngine, SINGLE_FIELD, OBJECTIVELY_MEASURABLE
from serum2.evidence.record import PASS
from serum2.evidence.capability_contract import build_contract, CAUSAL_VERIFIED, NEGATIVE_EVIDENCE

rec = pickle.load(open(r"D:\ableton claude\experiments\_env_release_qualified_complete_001.pkl", "rb"))
print("Loaded fresh evidence: experiment_id=%s" % rec.experiment_id)

claim_def = ClaimDefinition(
    claim_type="envelope_field_release",
    subject_pattern={"kind": "envelope_field"},
    predicate="extends",
    required_gate={"load": PASS, "causal": PASS, "persistence": PASS},
    required_isolation=(SINGLE_FIELD,),
    breadth_rule={"sampled_min": 1},
    coverage_rule={"generalizing_dimensions": [], "family_min_distinct": 1},
    contradiction_rule={"require_same_mutation": True, "require_comparable_measurement": True},
    dependency_rule={"enabled": False},
    measurability=OBJECTIVELY_MEASURABLE,
    required_measurement={"metric_name": "tail_rms_db",
                          "target": "Env0.plainParams.kParamRelease"},
)
print("\nClaimDefinition.claim_definition_id:", claim_def.claim_definition_id)

eng = ClaimEngine({"envelope_field_release": claim_def})
group = eng.add(rec, "envelope_field_release")

if group is None:
    print("\nREJECTED by ClaimDefinition.admits() -- see eng.rejected:")
    print(eng.rejected)
    sys.exit(1)

print("\nClaimGroup formed:")
print("  condition_signature_hash:", group.condition_signature_hash)
print("  supporting_evidence:", group.supporting_evidence)
print("  gate_completeness:", group.derived_gate_completeness())
print("  contradiction_state:", group.derived_contradiction_state())

contract = build_contract(group)

print("\n" + "=" * 70)
print("BUILT CONTRACT")
print("=" * 70)
print("target:            ", contract.target)
print("allowed_operation: ", contract.allowed_operation)
print("status:             %s" % contract.status)
print("verified:          ", contract.verified)
print("prerequisites:")
for p in contract.prerequisites:
    print("  -", p)
print("measurement:")
for k, v in contract.measurement.items():
    print("  %s: %s" % (k, v))
print("scope:")
for k, v in contract.scope.items():
    print("  %s: %s" % (k, v))
print("limitations:")
for lim in contract.limitations:
    print("  -", lim)

if contract.status == CAUSAL_VERIFIED:
    print("\nOUTCOME: contract.status == CAUSAL_VERIFIED. 4.1 may proceed to execution test.")
elif contract.status == NEGATIVE_EVIDENCE:
    print("\nOUTCOME: contract.status == NEGATIVE_EVIDENCE. 4.1 STOPS. Contract is non-authorizing.")
else:
    print("\nOUTCOME: contract.status == %s (unexpected for this design). Review before proceeding." % contract.status)

# 4.Q.3 section 6.2: explicit mutation_value_semantics and non-empty limitations
# are NOT produced by the generic build_contract() -- it is target-agnostic and
# has no notion of "absolute vs delta" or of contract-specific scope narration.
# Per the frozen design, we annotate the built contract's scope/limitations
# ourselves rather than special-casing build_contract() for Release.
from dataclasses import replace

annotated_scope = dict(contract.scope)
annotated_scope["mutation_value_semantics"] = "ABSOLUTE_PARAMETER_VALUE"

annotated_limitations = tuple(contract.limitations) + (
    "Tested only with Release parameter = 1.0 (absolute value); "
    "generalization to other Release values not established",
    "Tested only with Decay parameter = 0.02 (baseline_overrides context); "
    "generalization to other Decay contexts not established",
    "Single-field isolated mutation (N=1 witness); multi-field interactions not tested",
) if contract.status == CAUSAL_VERIFIED else contract.limitations

final_contract = replace(contract, scope=annotated_scope, limitations=annotated_limitations)

print("\n" + "=" * 70)
print("FINAL ANNOTATED CONTRACT (scope.mutation_value_semantics + explicit limitations)")
print("=" * 70)
print("scope:")
for k, v in final_contract.scope.items():
    print("  %s: %s" % (k, v))
print("limitations:")
for lim in final_contract.limitations:
    print("  -", lim)

key = (claim_def.claim_definition_id, group.condition_signature_hash)
store_4_1 = {key: final_contract}

pickle.dump(store_4_1, open(r"D:\ableton claude\experiments\_capability_contracts_4_1.pkl", "wb"))
print("\nSaved fresh 4.1 authority store: experiments/_capability_contracts_4_1.pkl")
print("Key:", key)
print("\nNOTE: this store contains ONLY the fresh Release contract. It is separate")
print("from experiments/_capability_contracts.pkl (archived, 37 entries, untouched).")
