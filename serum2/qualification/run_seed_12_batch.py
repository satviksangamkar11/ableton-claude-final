"""Execute the 12-experiment behavioral seed set.

Orchestrator for experiments 2-12 (experiment 1/Filter1.Cutoff already complete).
One subprocess per experiment. Independent processes, fresh DawDreamer instances.
Records all evidence; no claims/contracts yet.
"""

import json
import subprocess
import sys
import os
import datetime
from pathlib import Path

from serum2.qualification.seed_12_experiments import SEED_12_EXPERIMENTS


def run_single_experiment(exp, exp_num):
    """Execute one BehaviorExperiment through subprocess worker.

    Returns:
        dict with success, experiment_id, behavior_observation, exercise_qualification, or error
    """

    spec = exp
    spec.validate()

    spec_json = json.dumps(spec.to_dict(), default=str)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "serum2.qualification.experiment_worker", spec_json],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            return {
                "success": False,
                "experiment_id": exp.experiment_id,
                "error": f"Worker exited with code {result.returncode}",
                "stderr": result.stderr[:500],
            }

        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "experiment_id": exp.experiment_id,
                "error": f"Could not parse worker output as JSON: {str(e)}",
                "output_sample": result.stdout[:500],
            }

        if not output.get("success"):
            return {
                "success": False,
                "experiment_id": exp.experiment_id,
                "error": output.get("error", "unknown error"),
                "traceback": output.get("traceback", ""),
            }

        return output

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "experiment_id": exp.experiment_id,
            "error": "Worker timed out (300s)",
        }
    except Exception as e:
        return {
            "success": False,
            "experiment_id": exp.experiment_id,
            "error": f"Execution exception: {str(e)}",
        }


def save_individual_result(exp_num, output):
    """Save individual experiment result to file."""
    exp_id = output.get("experiment_id", "unknown")
    out_path = f"serum2/qualification/A_SEED_EXPERIMENT_{exp_num:02d}_{exp_id}_EVIDENCE.json"

    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    return out_path


def main():
    print("=" * 70)
    print("SEED SET BATCH EXECUTION: Experiments 2-12")
    print("=" * 70)
    print()
    print("Filter1.Cutoff (experiment 1) skipped (already completed)")
    print("Executing experiments 2-12 (11 new experiments)")
    print()

    results = []
    completed = 0
    failed = 0

    for i, exp in enumerate(SEED_12_EXPERIMENTS[1:], start=2):  # Skip experiment 1 (Filter1.Cutoff)
        print("-" * 70)
        print(f"[{i:2d}] {exp.semantic_target:30s} {exp.experiment_id}")
        print(f"     Context: {exp.context}")
        print(f"     Expected: {exp.expected_outcome}")
        print()

        print("     Executing...")
        output = run_single_experiment(exp, i)

        if output.get("success"):
            print("     [OK] Worker completed successfully")

            # Save individual result
            out_path = save_individual_result(i, output)
            print(f"     Evidence saved: {out_path}")

            # Extract key measurements
            if output.get("behavior_observation"):
                obs = output["behavior_observation"]
                if obs.get("measurements"):
                    for m in obs["measurements"]:
                        status = m.get("status", "?")
                        delta = m.get("delta")
                        if delta is not None:
                            print("       - {:30s} delta={:+8.2f} [{}]".format(m['name'], delta, status))
                        else:
                            print("       - {:30s} delta=     N/A [{}]".format(m['name'], status))

            completed += 1
            results.append({
                "experiment_id": exp.experiment_id,
                "semantic_target": exp.semantic_target,
                "expected_outcome": exp.expected_outcome,
                "success": True,
                "evidence_file": out_path,
                "behavior_observation": output.get("behavior_observation"),
                "exercise_qualification": output.get("exercise_qualification"),
            })
        else:
            print(f"     [FAIL] {output.get('error', 'unknown error')}")
            if output.get("stderr"):
                print(f"     STDERR: {output['stderr']}")

            failed += 1
            results.append({
                "experiment_id": exp.experiment_id,
                "semantic_target": exp.semantic_target,
                "expected_outcome": exp.expected_outcome,
                "success": False,
                "error": output.get("error"),
            })

        print()

    # Aggregate results
    print("=" * 70)
    print("AGGREGATING RESULTS")
    print("=" * 70)
    print()

    aggregate = {
        "seed_batch_execution": {
            "execution_date": datetime.datetime.now(datetime.UTC).isoformat(),
            "total_experiments": 11,
            "completed": completed,
            "failed": failed,
            "experiments": results,
        }
    }

    aggregate_path = "serum2/qualification/A_BEHAVIORAL_SEED_EVIDENCE_v2.json"
    with open(aggregate_path, "w") as f:
        json.dump(aggregate, f, indent=2, default=str)

    print(f"Aggregate evidence saved to: {aggregate_path}")
    print()

    # Summary
    print("=" * 70)
    print("EXECUTION SUMMARY")
    print("=" * 70)
    print()
    print(f"Completed:  {completed}/11 experiments")
    print(f"Failed:     {failed}/11 experiments")
    print()

    if completed > 0:
        print("SUCCESSFUL EXPERIMENTS:")
        for r in results:
            if r["success"]:
                obs_status = "?"
                if r.get("behavior_observation") and r["behavior_observation"].get("measurements"):
                    obs_status = r["behavior_observation"]["measurements"][0].get("status", "?")

                eq_valid = r.get("exercise_qualification", {}).get("is_valid", "?")
                print(f"  - {r['semantic_target']:30s} [{obs_status:20s}] is_valid={eq_valid}")

    if failed > 0:
        print()
        print("FAILED EXPERIMENTS:")
        for r in results:
            if not r["success"]:
                print(f"  - {r['semantic_target']:30s} {r.get('error', 'unknown')}")

    print()
    print("=" * 70)
    if failed == 0:
        print("RESULT: ALL EXPERIMENTS COMPLETED SUCCESSFULLY")
    else:
        print(f"RESULT: {completed} successful, {failed} failed")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
