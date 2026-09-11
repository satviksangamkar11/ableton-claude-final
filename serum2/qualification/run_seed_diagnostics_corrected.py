"""Execute corrected diagnostic experiments.

Based on measured baselines from the prior seed batch, run 7 targeted
experiments with corrected treatment values designed to produce meaningful
contrast against the actual Serum state.
"""

import json
import subprocess
import sys
from datetime import datetime

from serum2.qualification.seed_diagnostic_corrected import DIAGNOSTIC_EXPERIMENTS


def run_diagnostic(exp, exp_num):
    """Execute one diagnostic experiment through subprocess worker."""

    spec = exp
    spec.validate()

    spec_json = json.dumps(spec.to_dict(), default=str)

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
            "error": f"Worker exit code {result.returncode}",
            "stderr": result.stderr[:300],
        }

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "success": False,
            "experiment_id": exp.experiment_id,
            "error": "JSON parse failed",
            "output": result.stdout[:200],
        }

    if not output.get("success"):
        return {
            "success": False,
            "experiment_id": exp.experiment_id,
            "error": output.get("error", "unknown"),
        }

    return output


def save_diagnostic_result(exp_num, output):
    """Save diagnostic result."""
    exp_id = output.get("experiment_id", "unknown")
    path = f"serum2/qualification/DIAG_{exp_num:02d}_{exp_id}.json"

    with open(path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    return path


def main():
    print("=" * 70)
    print("TARGETED DIAGNOSTIC EXPERIMENTS (CORRECTED TREATMENT VALUES)")
    print("=" * 70)
    print()

    results = []

    for i, exp in enumerate(DIAGNOSTIC_EXPERIMENTS, 1):
        print("-" * 70)
        print("[{:2d}] {}".format(i, exp.semantic_target))
        print("     Treatment path: {}".format(exp.treatment_cbor_path))
        print("     Treatment value: {}".format(exp.treatment_cbor_value))
        print("     Context: {}".format(exp.context))
        print()

        print("     Executing...")
        output = run_diagnostic(exp, i)

        if output.get("success"):
            print("     [OK] Completed")

            # Save
            path = save_diagnostic_result(i, output)
            print("     Saved: {}".format(path))

            # Extract measurements
            obs = output.get("behavior_observation", {})
            if obs.get("measurements"):
                m = obs["measurements"][0]
                print("     Baseline: {:.2f}".format(m.get("baseline")))
                print("     Treatment: {:.2f}".format(m.get("treatment")))
                print("     Delta: {:+.2f}".format(m.get("delta")))
                print("     Status: {}".format(m.get("status")))

            results.append({
                "experiment_id": exp.experiment_id,
                "semantic_target": exp.semantic_target,
                "success": True,
                "file": path,
            })
        else:
            print("     [FAIL] {}".format(output.get("error")))
            results.append({
                "experiment_id": exp.experiment_id,
                "semantic_target": exp.semantic_target,
                "success": False,
                "error": output.get("error"),
            })

        print()

    # Summary
    print("=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)
    print()

    successful = sum(1 for r in results if r.get("success"))
    failed = sum(1 for r in results if not r.get("success"))

    print("Completed: {}/{}".format(successful, len(DIAGNOSTIC_EXPERIMENTS)))
    print("Failed:    {}/{}".format(failed, len(DIAGNOSTIC_EXPERIMENTS)))
    print()

    if successful > 0:
        print("SUCCESSFUL DIAGNOSTICS:")
        for r in results:
            if r.get("success"):
                print("  - {}".format(r["semantic_target"]))

    if failed > 0:
        print()
        print("FAILED DIAGNOSTICS:")
        for r in results:
            if not r.get("success"):
                print("  - {} ({})".format(r["semantic_target"], r.get("error")))

    print()
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
