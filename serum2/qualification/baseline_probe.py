"""Baseline-aware behavioral treatment design.

For each target, establish the actual baseline behavior first,
then deliberately choose a treatment that contrasts with it.
"""

from serum2.qualification.behavior_experiment import BehaviorExperiment, MeasurementPlan
from serum2.qualification.experiment_worker import run_experiment_worker
import json


def probe_baseline(target_name, semantic_target, context, measurement_kernels):
    """Run baseline (no mutation) to establish actual behavior."""

    spec = BehaviorExperiment(
        experiment_id=f"baseline_probe_{target_name}",
        semantic_target=semantic_target,
        operation="SET_PARAMETER",
        context=context,
        context_provenance="baseline probe: no treatment",
        treatment_cbor_path=None,  # No mutation
        treatment_cbor_value=None,
        measurement_plan=tuple(
            MeasurementPlan(name=k, kernel=k, threshold=None)
            for k in measurement_kernels
        ),
        expected_outcome="CONDITIONAL",
        notes=f"Baseline probe for {target_name}. No treatment applied.",
    )

    spec_dict = spec.to_dict()
    result = run_experiment_worker(spec_dict)

    return result


def report_baseline(target_name, result):
    """Print baseline measurements."""
    if not result.get("success"):
        print(f"[FAIL] {target_name}: {result.get('error')}")
        return

    obs = result.get("behavior_observation", {})
    print(f"[OK] {target_name} baseline:")
    print(f"     context: {obs.get('context')}")

    for m in obs.get("measurements", []):
        print(f"     {m['name']:30s}: {m['baseline']:+10.2f}")

    return obs


# Targets to probe
TARGETS_TO_PROBE = [
    {
        "name": "OSC1.Level",
        "semantic_target": "OSC1.Level",
        "context": {},
        "kernels": ["overall_rms_db", "tail_rms_db"],
        "strategy": "Baseline RMS shows amplitude; choose treatment as MIN (0.0) vs MAX (1.0)",
    },
    {
        "name": "Filter2.Cutoff",
        "semantic_target": "Filter2.Cutoff",
        "context": {"Filter 2 On": 1.0},
        "kernels": ["spectral_centroid_hz", "overall_rms_db"],
        "strategy": "Baseline centroid > 4000 Hz (already high-pass); choose treatment as LOW (0.1) vs baseline",
    },
    {
        "name": "Env1.Attack",
        "semantic_target": "Env1.Attack",
        "context": {},
        "kernels": ["overall_rms_db", "spectral_centroid_hz"],
        "strategy": "Baseline RMS shows current envelope setup; choose EXTREME SLOW (0.9) to contrast",
    },
]


def main():
    print("=" * 70)
    print("BASELINE PROBING FOR BEHAVIORAL TARGETS")
    print("=" * 70)
    print()

    for target_spec in TARGETS_TO_PROBE:
        print("-" * 70)
        print(f"Target: {target_spec['name']}")
        print(f"Strategy: {target_spec['strategy']}")
        print()

        result = probe_baseline(
            target_spec["name"],
            target_spec["semantic_target"],
            target_spec["context"],
            target_spec["kernels"],
        )

        obs = report_baseline(target_spec["name"], result)
        print()


if __name__ == "__main__":
    main()
