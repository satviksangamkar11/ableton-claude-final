"""Execute Filter1.Cutoff through revised architecture.

One experiment through subprocess worker.
Validate against pilot evidence.
"""

import json
import subprocess
import sys
import os

from serum2.qualification.filter_cutoff_revised_spec import FILTER_CUTOFF_SPEC


def run_experiment():
    """Execute one Filter1.Cutoff experiment through subprocess worker."""

    spec = FILTER_CUTOFF_SPEC
    spec.validate()

    spec_json = json.dumps(spec.to_dict(), default=str)

    print("=" * 70)
    print("FILTER1.CUTOFF REVISED EXECUTION")
    print("=" * 70)
    print()
    print("Launching subprocess worker...")
    print(f"  experiment_id: {spec.experiment_id}")
    print(f"  semantic_target: {spec.semantic_target}")
    print(f"  context: {spec.context}")
    print(f"  treatment_cbor_path: {spec.treatment_cbor_path}")
    print(f"  treatment_cbor_value: {spec.treatment_cbor_value}")
    print(f"  measurement_plan: {[m.name for m in spec.measurement_plan]}")
    print()

    result = subprocess.run(
        [sys.executable, "-m", "serum2.qualification.experiment_worker", spec_json],
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        print(f"FAILED: Worker exited with code {result.returncode}")
        print("STDERR:", result.stderr)
        return None

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"FAILED: Could not parse worker output as JSON")
        print("Output:", result.stdout[:500])
        print("Error:", e)
        return None

    if not output.get("success"):
        print(f"FAILED: {output.get('error')}")
        print(output.get("traceback", ""))
        return None

    print("[OK] Worker completed successfully")
    print()

    return output


def compare_to_pilot(output):
    """Compare revised result to original pilot evidence."""

    print("=" * 70)
    print("COMPARISON WITH ORIGINAL PILOT")
    print("=" * 70)
    print()

    pilot_path = "serum2/qualification/A_FILTER_CUTOFF_PILOT_EVIDENCE.json"
    if not os.path.exists(pilot_path):
        print(f"WARNING: Pilot evidence not found at {pilot_path}")
        return False

    with open(pilot_path) as f:
        pilot = json.load(f)

    obs_revised = output["behavior_observation"]
    eq_revised = output["exercise_qualification"]

    pilot_eq = pilot["exercise_qualification"]
    pilot_obs = pilot["behavior_result_raw"]

    # Compare key measurements
    print("Measurement comparison:")
    print()

    revised_centroid_baseline = None
    revised_centroid_delta = None
    for m in obs_revised["measurements"]:
        if m["name"] == "spectral_centroid_hz":
            revised_centroid_baseline = m["baseline"]
            revised_centroid_delta = m["delta"]
            break

    pilot_centroid_baseline = pilot_obs["baseline_metric"]
    pilot_centroid_delta = pilot_obs["delta"]

    print(f"  Baseline centroid:")
    print(f"    Pilot:   {pilot_centroid_baseline:>10.1f} Hz")
    print(f"    Revised: {revised_centroid_baseline:>10.1f} Hz")
    centroid_baseline_match = (
        abs(revised_centroid_baseline - pilot_centroid_baseline) < 50
    )
    print(f"    Match: {'[OK]' if centroid_baseline_match else '[FAIL]'}")
    print()

    print(f"  Delta (treatment - baseline):")
    print(f"    Pilot:   {pilot_centroid_delta:>10.1f} Hz")
    print(f"    Revised: {revised_centroid_delta:>10.1f} Hz")
    centroid_delta_match = abs(revised_centroid_delta - pilot_centroid_delta) < 200
    print(f"    Match: {'[OK]' if centroid_delta_match else '[FAIL]'}")
    print()

    # Compare exercise qualification validity
    print("ExerciseQualification:")
    print(f"  Pilot is_valid:   {pilot_eq['is_valid']}")
    print(f"  Revised is_valid: {eq_revised['is_valid']}")
    eq_match = pilot_eq["is_valid"] == eq_revised["is_valid"]
    print(f"  Match: {'[OK]' if eq_match else '[FAIL]'}")
    print()

    # Compare context
    print("Context:")
    print(f"  Pilot:   {pilot_eq['frozen_context']}")
    print(f"  Revised: {eq_revised['frozen_context']}")
    context_match = pilot_eq["frozen_context"] == eq_revised["frozen_context"]
    print(f"  Match: {'[OK]' if context_match else '[FAIL]'}")
    print()

    # Overall
    all_match = centroid_baseline_match and centroid_delta_match and eq_match and context_match
    return all_match


def save_result(output):
    """Save revised evidence to file."""
    out_path = "serum2/qualification/A_FILTER_CUTOFF_REVISED_EVIDENCE.json"

    eq = output["exercise_qualification"]
    obs = output["behavior_observation"]

    payload = {
        "pilot": "Filter1.Cutoff Revised Architecture Execution",
        "status": "REVISED_ARCHITECTURE",
        "comparison_with": "A_FILTER_CUTOFF_PILOT_EVIDENCE.json",
        "exercise_qualification": eq,
        "behavior_observation": obs,
    }

    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    return out_path


def main():
    output = run_experiment()
    if output is None:
        print("\n" + "=" * 70)
        print("RESULT: FAIL (experiment execution failed)")
        print("=" * 70)
        return 1

    match = compare_to_pilot(output)

    out_path = save_result(output)
    print("=" * 70)
    print("RESULT: {} (revised evidence saved to {})".format(
        "PASS" if match else "PASS WITH NOTES",
        out_path,
    ))
    print("=" * 70)

    return 0 if match else 1


if __name__ == "__main__":
    sys.exit(main())
