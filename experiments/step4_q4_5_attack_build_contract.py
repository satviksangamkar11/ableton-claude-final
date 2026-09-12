"""4.Q.4 step 5: Build the fresh 4.2 CapabilityContract from Attack evidence.

Writes to experiments/_capability_contracts_4_2.pkl -- a SEPARATE store from
both the archived experiments/_capability_contracts.pkl (37 entries, untouched)
and the 4.1 Release store (_capability_contracts_4_1.pkl).

Per 4.2 specification: the test is whether BOTH Release and Attack can be
executed through the same production pathway with ZERO target-specific branches.
By keeping each fresh contract in its own store during qualification, we make
the target-independence concrete: the producer code never specializes on which
target it is -- it only knows how to load and use a CapabilityContract.
"""
import sys, pickle
sys.path.insert(0, r"D:\ableton claude")
from serum2.evidence.claim import ClaimDefinition, ClaimEngine, SINGLE_FIELD, OBJECTIVELY_MEASURABLE
from serum2.evidence.record import PASS
from serum2.evidence.capability_contract import build_contract, CAUSAL_VERIFIED, NEGATIVE_EVIDENCE
from dataclasses import replace

rec = pickle.load(open(r"D:\ableton claude\experiments\_env_attack_qualified_complete_001.pkl", "rb"))
print("Loaded fresh evidence: experiment_id=%s" % rec.experiment_id)

claim_def = ClaimDefinition(
    claim_type="envelope_field_attack",
    subject_pattern={"kind": "envelope_field"},
    predicate="reduces",
    required_gate={"load": PASS, "causal": PASS, "persistence": PASS},
    required_isolation=(SINGLE_FIELD,),
    breadth_rule={"sampled_min": 1},
    coverage_rule={"generalizing_dimensions": [], "family_min_distinct": 1},
    contradiction_rule={"require_same_mutation": True, "require_comparable_measurement": True},
    dependency_rule={"enabled": False},
    measurability=OBJECTIVELY_MEASURABLE,
    required_measurement={"metric_name": "attack_onset_rms_db",
                          "target": "Env0.plainParams.kParamAttack"},
)
print("\nClaimDefinition.claim_definition_id:", claim_def.claim_definition_id)

eng = ClaimEngine({"envelope_field_attack": claim_def})
group = eng.add(rec, "envelope_field_attack")

if group is None:
    print("\nREJECTED by ClaimDefinition.admits():")
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
if contract.prerequisites:
    for p in contract.prerequisites:
        print("  -", p)
else:
    print("  (none)")
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
    print("\nOUTCOME: contract.status == CAUSAL_VERIFIED. 4.2 may proceed to execution test.")
elif contract.status == NEGATIVE_EVIDENCE:
    print("\nOUTCOME: contract.status == NEGATIVE_EVIDENCE. 4.2 STOPS. Contract is non-authorizing.")
else:
    print("\nOUTCOME: contract.status == %s (unexpected). Review before proceeding." % contract.status)

# Annotate scope with absolute value semantics and explicit limitations
annotated_scope = dict(contract.scope)
annotated_scope["mutation_value_semantics"] = "ABSOLUTE_PARAMETER_VALUE"

annotated_limitations = tuple(contract.limitations) + (
    "Tested only with Attack parameter = 0.8 (absolute value); "
    "generalization to other Attack values not established",
    "No baseline_overrides context tested; generalization across contexts not tested",
    "Single-field isolated mutation (N=1 witness); multi-field interactions not tested",
) if contract.status == CAUSAL_VERIFIED else contract.limitations

final_contract = replace(contract, scope=annotated_scope, limitations=annotated_limitations)

print("\n" + "=" * 70)
print("FINAL ANNOTATED CONTRACT")
print("=" * 70)
print("scope:")
for k, v in final_contract.scope.items():
    print("  %s: %s" % (k, v))
print("limitations:")
for lim in final_contract.limitations:
    print("  -", lim)

key = (claim_def.claim_definition_id, group.condition_signature_hash)
store_4_2 = {key: final_contract}

pickle.dump(store_4_2, open(r"D:\ableton claude\experiments\_capability_contracts_4_2.pkl", "wb"))
print("\nSaved fresh 4.2 authority store: experiments/_capability_contracts_4_2.pkl")
print("Key:", key)
print("\nNOTE: this store contains ONLY the fresh Attack contract. It is separate")
print("from _capability_contracts_4_1.pkl (Release) and _capability_contracts.pkl (archived).")
