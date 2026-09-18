"""
PHASE 4A: EXECUTION CLOSURE - 4 additional FXEQ targets

Bulk-tests FXEQ.Freq2, FXEQ.Gain1, FXEQ.Reso1, FXEQ.Type2 using the EXACT
same established mechanism proven in Phase 3 (BODY_STATE + corpus fixture
bodies[4]). No new mechanism invented.
"""
import sys, json, pickle
from pathlib import Path
from datetime import datetime

sys.path.insert(0, r"D:\ableton claude")
from serum2.producer.contract_registry import ContractRegistry
from serum2.evidence import admission as admission_mod
from serum2 import pathmerge

TARGETS = [
    ("FXEQ.Freq2", "fx_field_eq_kParamFreq2", "FXRack0.FX.1.FXEQ.plainParams.kParamFreq2", 5000.0),
    ("FXEQ.Gain1", "fx_field_eq_kParamGain1", "FXRack0.FX.1.FXEQ.plainParams.kParamGain1", -10.0),
    ("FXEQ.Reso1", "fx_field_eq_kParamReso1", "FXRack0.FX.1.FXEQ.plainParams.kParamReso1", 75.0),
    ("FXEQ.Type2", "fx_field_eq_kParamType2", "FXRack0.FX.1.FXEQ.plainParams.kParamType2", 2.0),
]

def load_fixture():
    corpus_cache = pickle.load(open(r"D:\ableton claude\experiments\_corpus_cache.pkl", "rb"))
    return corpus_cache["bodies"][4]

def run():
    print("=" * 100)
    print("PHASE 4A: FXEQ EXECUTION CLOSURE (4 targets, established fixture)")
    print("=" * 100)

    fixture_body = load_fixture()
    registry = ContractRegistry()
    contracts_dict = registry.get_contracts_dict()

    results = []
    verified = 0

    for semantic, internal, body_path, mutation_val in TARGETS:
        print(f"\n{semantic}")
        print("-" * 100)
        result = {"target": semantic, "internal": internal, "body_path": body_path,
                   "execution_verified": False, "error": None}
        try:
            contract = registry.get(internal)
            if not contract or contract.status != "CAUSAL_VERIFIED":
                result["error"] = "contract_missing_or_not_verified"
                results.append(result); print("  FAIL: contract"); continue
            if not contract.execution_binding or contract.execution_binding.mutation_type != "BODY_STATE":
                result["error"] = "binding_missing"
                results.append(result); print("  FAIL: binding"); continue

            prereq = {}
            for p in (contract.prerequisites or []):
                fp = p.get("field_path")
                if fp: prereq[fp] = p.get("declared_value")
            adm = admission_mod.admit(contracts_dict, internal, proposed_prerequisites_verified=prereq or None)
            if not adm.admitted:
                result["error"] = f"admission_denied:{adm.reason}"
                results.append(result); print("  FAIL: admission"); continue
            print("  Admission: ADMITTED")

            body = dict(fixture_body)
            baseline = pathmerge.read_path_value(body, body_path)
            if baseline is None:
                result["error"] = "path_not_found"
                results.append(result); print("  FAIL: path not found"); continue
            result["baseline"] = float(baseline)
            print(f"  Baseline: {baseline}")

            pathmerge.apply_path_value(body, body_path, mutation_val)
            observed = pathmerge.read_path_value(body, body_path)
            result["requested"] = mutation_val
            result["observed"] = float(observed)
            ok = abs(float(observed) - mutation_val) < 1.0
            print(f"  Mutation {mutation_val} -> Observed {observed} ({'OK' if ok else 'FAIL'})")
            if not ok:
                result["error"] = "mutation_failed"
                results.append(result); continue

            pathmerge.apply_path_value(body, body_path, float(baseline))
            restored = pathmerge.read_path_value(body, body_path)
            result["restored"] = float(restored)
            rok = abs(float(restored) - float(baseline)) < 1.0
            print(f"  Restored: {restored} ({'OK' if rok else 'FAIL'})")
            if not rok:
                result["error"] = "restore_failed"
                results.append(result); continue

            result["execution_verified"] = True
            verified += 1
            print("  Status: EXECUTION_VERIFIED")
        except Exception as e:
            result["error"] = str(e)
            print(f"  ERROR: {e}")
        results.append(result)

    print(f"\n{verified}/4 VERIFIED")
    return verified == 4, results

if __name__ == "__main__":
    ok, results = run()
    out = Path("experiments/phase4a_fxeq_closure_execution.json")
    with open(out, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "verified": sum(1 for r in results if r["execution_verified"]),
                    "total": 4, "results": results}, f, indent=2)
    print(f"Saved: {out}")
    sys.exit(0 if ok else 1)
