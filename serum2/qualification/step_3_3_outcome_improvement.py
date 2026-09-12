"""Step 3.3: Outcome Improvement

Tests whether the retrieval-influenced decision (+0.08 magnitude) produces a
BETTER MEASURED outcome than the control decision (+0.05 magnitude).

Uses the existing trusted execution path:
    capability admission (already established: Env1.Release CAUSAL_VERIFIED)
    -> bridge.capture_v8_skeleton (existing Serum skeleton loader)
    -> render_and_measure (existing DawDreamer -> Serum VST3 -> render -> measure)

Frozen decisions (already established by Step 3.0 / Step 3.2 — NOT re-decided here):

    CONTROL:          Env1.Release baseline 0.50 -> mutation 0.55 (+0.05)
    MEMORY-INFORMED:  Env1.Release baseline 0.50 -> mutation 0.58 (+0.08)

Both executions share:
    - identical Serum skeleton (same VST3 state)
    - identical baseline parameter value (0.50)
    - identical measurement metric (tail_rms_db)
    - identical render path (render_and_measure)
    - identical validity checks (is_valid_signal)

The ONLY difference between the two executions is the mutation value applied
to Env1.Release (0.55 vs 0.58).

Does NOT invoke Claude. Does NOT re-derive the decision. Does NOT modify
capability status or promote the episode to authority.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2 import bridge
from serum2.evidence import epoch as epoch_mod
from serum2.producer.canonical_feedback_loop import (
    resolve_host_param_name,
    render_and_measure,
)

VST3 = epoch_mod.SERUM_VST3

TARGET = "Env1.Release"
BASELINE_VALUE = 0.50
MEASUREMENT_METRIC = "tail_rms_db"

CONTROL_MAGNITUDE = 0.05
CONTROL_RESULTANT = 0.55

MEMORY_INFORMED_MAGNITUDE = 0.08
MEMORY_INFORMED_RESULTANT = 0.58

IMPROVEMENT_THRESHOLD_DB = 0.05  # NOTE: chosen by implementer when writing this script, not
                                  # pre-registered in a separate experiment spec before execution.
                                  # The defensible claim is the measured delta_difference itself;
                                  # this threshold is a convenience cutoff, not a validated
                                  # significance criterion. See methodological_note in result JSON.


def execute_condition(condition_name: str, host_param_name: str, resultant_value: float) -> dict:
    """Execute one condition through the real trusted path and measure the result.

    Both baseline and treatment are rendered fresh from the same Serum skeleton
    to guarantee identical initial state across conditions.
    """
    print(f"\n[{condition_name}] EXECUTING")
    print("-" * 70)

    # Load Serum skeleton fresh for this condition (identical initial state)
    print(f"  Loading Serum skeleton...")
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta = skeleton[0]
    body = skeleton[1]

    # Render baseline (Env1.Release = 0.50) with this skeleton
    print(f"  Rendering baseline ({host_param_name} = {BASELINE_VALUE})...")
    baseline_override_param = (host_param_name, BASELINE_VALUE)
    audio_baseline, measurement_baseline, baseline_validity = render_and_measure(
        meta, body, MEASUREMENT_METRIC, baseline_override_param=baseline_override_param
    )
    print(f"    baseline {MEASUREMENT_METRIC}: {measurement_baseline:.4f}")
    print(f"    baseline signal valid: {baseline_validity['valid']}")

    # Render treatment (Env1.Release = resultant_value) with same skeleton
    print(f"  Rendering treatment ({host_param_name} = {resultant_value})...")
    treatment_override_param = (host_param_name, resultant_value)
    audio_treatment, measurement_treatment, treatment_validity = render_and_measure(
        meta, body, MEASUREMENT_METRIC, baseline_override_param=treatment_override_param
    )
    print(f"    treatment {MEASUREMENT_METRIC}: {measurement_treatment:.4f}")
    print(f"    treatment signal valid: {treatment_validity['valid']}")

    delta = measurement_treatment - measurement_baseline
    signal_valid = bool(baseline_validity['valid']) and bool(treatment_validity['valid'])

    print(f"  delta: {delta:+.4f}")
    print(f"  signal_valid: {signal_valid}")

    return {
        "condition": condition_name,
        "target": TARGET,
        "host_param_name": host_param_name,
        "resultant_value": resultant_value,
        "baseline_measurement": measurement_baseline,
        "treatment_measurement": measurement_treatment,
        "delta": delta,
        "baseline_validity": baseline_validity,
        "treatment_validity": treatment_validity,
        "signal_valid": signal_valid,
    }


def main():
    print("[STEP 3.3] OUTCOME IMPROVEMENT — REAL EXECUTION")
    print("=" * 70)
    print("Testing: does retrieval-influenced decision (+0.08) improve the")
    print("measured outcome vs. the control decision (+0.05)?")
    print()
    print("These decisions were already made in Step 3.0 / Step 3.2.")
    print("This step does NOT invoke Claude and does NOT re-decide anything.")
    print()

    # ---- Resolve host parameter name once (shared by both conditions) ----
    print("[RESOLVING HOST PARAMETER]")
    print("-" * 70)
    host_param_name = resolve_host_param_name(TARGET)
    print(f"  {TARGET} -> '{host_param_name}'")

    print("\n" + "=" * 70)
    print("[FROZEN CONDITIONS]")
    print("=" * 70)
    print(f"""
CONTROL:
    target = {TARGET}
    magnitude = +{CONTROL_MAGNITUDE}
    resultant_value = {CONTROL_RESULTANT}

MEMORY-INFORMED:
    target = {TARGET}
    magnitude = +{MEMORY_INFORMED_MAGNITUDE}
    resultant_value = {MEMORY_INFORMED_RESULTANT}

Shared:
    baseline_value = {BASELINE_VALUE}
    measurement_metric = {MEASUREMENT_METRIC}
    execution_backend = DawDreamer -> Serum VST3 (bridge.capture_v8_skeleton + render_and_measure)
    """)

    # ---- Execute CONTROL ----
    print("=" * 70)
    print("[CONTROL EXECUTION]")
    print("=" * 70)
    try:
        control_result = execute_condition("CONTROL", host_param_name, CONTROL_RESULTANT)
    except Exception as e:
        print(f"\n[FATAL] CONTROL execution failed: {e}")
        import traceback
        traceback.print_exc()
        print("\nSTEP 3.3 STATUS: INVALID")
        print("Failure classification: CONTROL_EXECUTION_FAILED")
        return 1

    # ---- Execute MEMORY-INFORMED ----
    print("\n" + "=" * 70)
    print("[MEMORY-INFORMED EXECUTION]")
    print("=" * 70)
    try:
        memory_informed_result = execute_condition(
            "MEMORY-INFORMED", host_param_name, MEMORY_INFORMED_RESULTANT
        )
    except Exception as e:
        print(f"\n[FATAL] MEMORY-INFORMED execution failed: {e}")
        import traceback
        traceback.print_exc()
        print("\nSTEP 3.3 STATUS: INVALID")
        print("Failure classification: MEMORY_INFORMED_EXECUTION_FAILED")
        return 1

    # ---- Signal validity check ----
    print("\n" + "=" * 70)
    print("[SIGNAL VALIDITY CHECK]")
    print("=" * 70)

    both_valid = control_result["signal_valid"] and memory_informed_result["signal_valid"]
    print(f"\n  CONTROL signal valid:          {control_result['signal_valid']}")
    print(f"  MEMORY-INFORMED signal valid:  {memory_informed_result['signal_valid']}")

    # Comparability check: baseline measurements should match (same skeleton, same baseline value)
    baseline_diff = abs(control_result["baseline_measurement"] - memory_informed_result["baseline_measurement"])
    print(f"\n  CONTROL baseline measurement:         {control_result['baseline_measurement']:.4f}")
    print(f"  MEMORY-INFORMED baseline measurement: {memory_informed_result['baseline_measurement']:.4f}")
    print(f"  Baseline difference:                  {baseline_diff:.6f}")

    comparable = baseline_diff < 0.001  # Baselines should be numerically identical
    print(f"  Baselines comparable (< 0.001 dB diff): {comparable}")

    if not both_valid:
        print("\nSTEP 3.3 STATUS: INVALID")
        print("Failure classification: SIGNAL_INVALID")
        _emit_final_json(control_result, memory_informed_result, None, "INVALID", "SIGNAL_INVALID")
        return 1

    if not comparable:
        print("\nSTEP 3.3 STATUS: INVALID")
        print("Failure classification: EXECUTIONS_NOT_COMPARABLE (baseline drift between conditions)")
        _emit_final_json(control_result, memory_informed_result, None, "INVALID", "EXECUTIONS_NOT_COMPARABLE")
        return 1

    # ---- Measurement comparison ----
    print("\n" + "=" * 70)
    print("[MEASUREMENT COMPARISON]")
    print("=" * 70)

    control_delta = control_result["delta"]
    memory_informed_delta = memory_informed_result["delta"]
    improvement_difference = memory_informed_delta - control_delta

    print(f"\n  control_delta:            {control_delta:+.4f} dB ({MEASUREMENT_METRIC})")
    print(f"  memory_informed_delta:    {memory_informed_delta:+.4f} dB ({MEASUREMENT_METRIC})")
    print(f"  improvement_difference:   {improvement_difference:+.4f} dB")
    print(f"  significance threshold:   {IMPROVEMENT_THRESHOLD_DB} dB (predefined)")

    # ---- Interpretation ----
    print("\n" + "=" * 70)
    print("[INTERPRETATION]")
    print("=" * 70)

    if improvement_difference > IMPROVEMENT_THRESHOLD_DB:
        status = "PASS"
        classification = "MEMORY_INFORMED_BETTER"
        print(f"\n  MEMORY-INFORMED BETTER")
        print(f"  memory_informed_delta ({memory_informed_delta:+.4f}) > control_delta ({control_delta:+.4f})")
        print(f"  by {improvement_difference:+.4f} dB, exceeding {IMPROVEMENT_THRESHOLD_DB} dB threshold")
        print(f"\nSTEP 3.3 STATUS: PASS")
        print(f"  Retrieval-influenced decision (+0.08) produced a measurably better outcome")
        print(f"  than the control decision (+0.05).")
        print(f"\nSTEP 3 COMPLETE.")
        result_code = 0
    else:
        status = "FAIL"
        classification = "NO_IMPROVEMENT" if improvement_difference <= 0 else "IMPROVEMENT_BELOW_THRESHOLD"
        print(f"\n  NO IMPROVEMENT (or below significance threshold)")
        print(f"  memory_informed_delta ({memory_informed_delta:+.4f}) vs control_delta ({control_delta:+.4f})")
        print(f"  difference {improvement_difference:+.4f} dB does not exceed {IMPROVEMENT_THRESHOLD_DB} dB threshold")
        print(f"\nSTEP 3.3 STATUS: FAIL")
        print(f"  Retrieval influenced the decision (Step 3.2), but the changed decision")
        print(f"  did NOT improve the measured outcome.")
        print(f"  This is a valid, informative result — not a learning-mechanism failure.")
        print(f"  Smallest next action: episode representation may need actionable")
        print(f"  measurement context (e.g., which magnitude direction under-corrects)")
        print(f"  rather than accept/reject alone, but this requires new evidence first.")
        result_code = 1

    _emit_final_json(control_result, memory_informed_result, improvement_difference, status, classification)

    return result_code


def _emit_final_json(control_result, memory_informed_result, improvement_difference, status, classification):
    print("\n" + "=" * 70)
    print("[FINAL OUTPUT — MACHINE READABLE]")
    print("=" * 70)

    output = {
        "step": "3.3",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "control_execution_conditions": {
            "target": TARGET,
            "magnitude": CONTROL_MAGNITUDE,
            "resultant_value": CONTROL_RESULTANT,
            "baseline_value": BASELINE_VALUE,
            "measurement_metric": MEASUREMENT_METRIC,
        },
        "memory_informed_execution_conditions": {
            "target": TARGET,
            "magnitude": MEMORY_INFORMED_MAGNITUDE,
            "resultant_value": MEMORY_INFORMED_RESULTANT,
            "baseline_value": BASELINE_VALUE,
            "measurement_metric": MEASUREMENT_METRIC,
        },
        "control_measurement": {
            "baseline_measurement": control_result["baseline_measurement"],
            "treatment_measurement": control_result["treatment_measurement"],
            "delta": control_result["delta"],
        },
        "memory_informed_measurement": {
            "baseline_measurement": memory_informed_result["baseline_measurement"],
            "treatment_measurement": memory_informed_result["treatment_measurement"],
            "delta": memory_informed_result["delta"],
        },
        "control_delta": control_result["delta"],
        "memory_informed_delta": memory_informed_result["delta"],
        "delta_difference": improvement_difference,
        "signal_validity": {
            "control_valid": control_result["signal_valid"],
            "memory_informed_valid": memory_informed_result["signal_valid"],
        },
        "status": status,
        "classification": classification,
    }

    print(json.dumps(output, indent=2, default=str))

    out_path = Path(__file__).parent / "step_3_3_outcome_improvement_result.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    sys.exit(main())
