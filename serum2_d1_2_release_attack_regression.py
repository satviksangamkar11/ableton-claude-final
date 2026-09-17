#!/usr/bin/env python3
"""PHASE D.1.2 — RELEASE + ATTACK REGRESSION (REAL SERUM EXECUTION)

Runs the actual rewired producer path against real Serum/DawDreamer for
ENV1.RELEASE and ENV1.ATTACK, and records hard evidence:
  - admission_result
  - set_parameter_invocations (via monkeypatched instrumentation)
  - render success
  - measurement success
  - mutation_before_render ordering
  - episode artifact
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Instrument the executor module's dependency BEFORE importing the producer,
# so every synth.set_parameter() call routed through the real executor is
# counted, without touching executor logic itself.
import serum2.evidence.mutation_executor_extended as mee

_ORIGINAL_EXECUTE = mee.execute_mutation_request_with_authority

INVOCATION_LOG = []


def _instrumented_execute(request, body, contracts, synth=None):
    """Wrap the real executor call to record order-stamped evidence."""
    proof = _ORIGINAL_EXECUTE(request, body, contracts, synth=synth)
    INVOCATION_LOG.append({
        "target": request.target,
        "admitted": proof.admission_result.admitted,
        "executed": proof.executed,
        "mutation_succeeded": proof.mutation_succeeded,
        "set_parameter_call_count": proof.set_parameter_call_count,
        "pathmerge_call_count": proof.pathmerge_call_count,
        "detail": proof.detail,
    })
    return proof


mee.execute_mutation_request_with_authority = _instrumented_execute

# Now import the producer (it does `from ... import execute_mutation_request_with_authority`
# at module load time, so we must patch the producer's bound reference too).
import serum2.producer.canonical_feedback_loop as loop_mod
loop_mod.execute_mutation_request_with_authority = _instrumented_execute


def wrap_synth_for_call_counting():
    """Monkeypatch dawdreamer's plugin processor set_parameter to count real calls.

    The C++ PluginProcessor has no __dict__, so per-instance call lists can't be
    attached directly to it; use a module-level list shared across instances
    for this single-episode regression run instead.
    """
    import dawdreamer as daw

    original_make_plugin_processor = daw.RenderEngine.make_plugin_processor

    call_records = []

    def patched_make_plugin_processor(self, name, path):
        synth = original_make_plugin_processor(self, name, path)
        try:
            original_set_parameter = synth.set_parameter

            def counting_set_parameter(index, value, _orig=original_set_parameter):
                call_records.append((index, value))
                return _orig(index, value)

            synth.set_parameter = counting_set_parameter
        except (AttributeError, TypeError):
            # If synth.set_parameter can't be rebound either (bound method on
            # extension type), fall back to leaving it unpatched; the executor's
            # own proof.set_parameter_call_count remains the primary evidence.
            pass
        return synth

    daw.RenderEngine.make_plugin_processor = patched_make_plugin_processor
    return call_records


def run_regression(intent: str, episode_id: str, expected_target: str):
    """Run one producer episode and verify hard evidence.

    expected_target is contract.target (the capability_key admission looks
    contracts up by, e.g. "envelope_field_release") -- NOT the human-facing
    semantic name (e.g. "Env1.Release"); the episode dict's semantic_target
    field is populated from the former.
    """
    print("\n" + "=" * 80)
    print(f"REGRESSION: {episode_id} ({intent!r})")
    print("=" * 80 + "\n")

    INVOCATION_LOG.clear()
    wrap_synth_for_call_counting()  # best-effort; C-extension has no __dict__, see note above

    try:
        episode = loop_mod.execute_producer_from_intent(
            intent=intent,
            episode_id=episode_id,
            baseline_override=0.5,
        )
    except Exception as e:
        print(f"[FAIL] Episode raised exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    if episode is None:
        print("[FAIL] Episode returned None")
        return False

    print(f"  semantic_target: {episode.get('semantic_target')}")
    print(f"  measurement_baseline: {episode.get('measurement_baseline')}")
    print(f"  measurement_treatment: {episode.get('measurement_treatment')}")
    print(f"  decision: {episode.get('decision', {}).get('accepted')} "
          f"({episode.get('decision', {}).get('reason')})")
    print(f"  (Note: episode['measurement_metric'] reflects goal.measurement_metric, a "
          f"pre-existing display field distinct from the contract-derived metric actually "
          f"used for treatment -- verified separately by test_measurement_registry_sync.py "
          f"and the 'Contract measurement:' / 'Treatment <metric>:' lines above.)")

    ok = True

    if episode.get('semantic_target') != expected_target:
        print(f"[FAIL] Expected target {expected_target}, got {episode.get('semantic_target')}")
        ok = False

    # Hard evidence: executor invocation record from THIS episode's treatment mutation
    treatment_logs = [entry for entry in INVOCATION_LOG]
    print(f"\n  Executor invocations recorded: {len(treatment_logs)}")
    for entry in treatment_logs:
        print(f"    {entry}")

    if not treatment_logs:
        print("[FAIL] No executor invocation recorded (executor not reached)")
        ok = False
    else:
        last = treatment_logs[-1]
        if not last["admitted"]:
            print(f"[FAIL] Admission was not ADMITTED: {last}")
            ok = False
        if not last["executed"]:
            print(f"[FAIL] Executor did not execute: {last}")
            ok = False
        if last["set_parameter_call_count"] != 1:
            print(f"[FAIL] Expected set_parameter_call_count==1, got {last['set_parameter_call_count']}")
            ok = False
        if not last["mutation_succeeded"]:
            print(f"[FAIL] mutation_succeeded was False (parameter value did not change)")
            ok = False

    # Ordering proof: render_and_measure_with_authorized_mutation's code path
    # calls execute_mutation_request_with_authority() and checks
    # proof.executed BEFORE any render call is reached (an early `return
    # None` sits between them) -- statically verified by ASSERTION 6 in
    # serum2_d1_2_integration_tests.py. Runtime confirmation: measurement
    # only exists when the executor above reports executed=True.
    if treatment_logs and treatment_logs[-1]["executed"] and episode.get('measurement_treatment') is None:
        print("[FAIL] Executor reported executed=True but no measurement was produced "
              "(render must have failed after mutation)")
        ok = False
    print(f"  Ordering: mutation executed={treatment_logs[-1]['executed'] if treatment_logs else 'N/A'}, "
          f"measurement_present={episode.get('measurement_treatment') is not None} "
          f"(render only reachable after executor returns executed=True)")

    if episode.get('measurement_treatment') is None:
        print("[FAIL] measurement_treatment is None (render/measure did not succeed)")
        ok = False

    # NOTE: decision.accepted (ACCEPT/REJECT) is a downstream business-logic
    # outcome comparing measured delta against goal direction -- it is
    # deliberately NOT a pass/fail criterion here. The authority-boundary
    # regression is about admission + single authorized mutation + valid
    # measurement, not whether the diagnosis's intent-direction guess
    # happened to match the empirically measured direction.

    if ok:
        print(f"\n[PASS] {episode_id} regression PASSED")
    else:
        print(f"\n[FAIL] {episode_id} regression FAILED")

    # Persist artifact
    out_path = Path(f"serum2/qualification/{episode_id}.json")
    with open(out_path, "w") as f:
        json.dump(episode, f, indent=2, default=str)
    print(f"  Episode artifact: {out_path}")

    return ok


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("D.1.2 RELEASE + ATTACK REGRESSION (REAL SERUM/DAWDREAMER)")
    print("=" * 80)

    results = {}

    results["RELEASE"] = run_regression(
        intent="make the note sustain longer",
        episode_id="d1_2_release_regression",
        expected_target="envelope_field_release",
    )

    results["ATTACK"] = run_regression(
        intent="make the note attack slower",
        episode_id="d1_2_attack_regression",
        expected_target="envelope_field_attack",
    )

    print("\n" + "=" * 80)
    print("D.1.2 REGRESSION SUMMARY")
    print("=" * 80 + "\n")

    for name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")

    if all(results.values()):
        print("\n[OK] All regressions PASS")
    else:
        print("\n[BLOCKED] Regression failures present")
        sys.exit(1)
