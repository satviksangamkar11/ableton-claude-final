#!/usr/bin/env python3
"""Registry synchronization test: prevents the attack_onset_rms_db class of
bug from silently recurring.

There are two independent measurement registries:
  1. serum2/evidence/kernels/*.py       -- qualification-time kernel files,
                                            loaded via evidence/measurement.py::load_kernel()
  2. serum2.evidence.measure.METRICS    -- producer runtime metric dict

A CapabilityContract's measurement_definition_id names a metric that MUST be
resolvable in BOTH registries, or the producer can admit a mutation whose
measurement step then fails with no path to ever succeed. This test checks
all three layers agree for every contract currently loaded by the producer's
ContractRegistry, and would fail immediately if a kernel file existed with no
corresponding METRICS entry (or vice versa) for any contract actually in use.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2.evidence.measure import METRICS
from serum2.producer.contract_registry import ContractRegistry


def metric_name_from_measurement_definition_id(measurement_definition_id: str) -> str:
    """Same parsing rule as canonical_feedback_loop.get_measurement_metric_from_contract."""
    return measurement_definition_id.split(":")[0] if ":" in measurement_definition_id else measurement_definition_id


def test_all_loaded_contracts_have_resolvable_metrics():
    """Every contract the producer can actually admit must have its
    measurement_definition_id's metric present in METRICS, and (if a kernel
    artifact exists) the kernel file must exist too."""
    registry = ContractRegistry()

    assert registry.contracts, "No contracts loaded -- cannot verify sync (check experiments/*.pkl paths)"

    kernel_dir = Path(__file__).parent / "kernels"

    failures = []
    for target, contract in registry.contracts.items():
        if not contract.measurement:
            continue

        measurement_definition_id = contract.measurement.get("measurement_definition_id")
        if not measurement_definition_id:
            continue

        metric_name = metric_name_from_measurement_definition_id(measurement_definition_id)

        # Layer 2: measure.METRICS
        if metric_name not in METRICS:
            failures.append(
                f"{target}: metric {metric_name!r} (from {measurement_definition_id!r}) "
                f"missing from serum2.evidence.measure.METRICS"
            )
            continue

        # Layer 1: kernel artifact file (best-effort -- not every METRICS
        # entry is kernel-file-backed, e.g. tail_rms_db/rms_db are inline)
        kernel_file = kernel_dir / f"{metric_name}.py"
        if kernel_file.exists():
            # If a kernel file exists for this metric, the METRICS entry
            # must actually reuse it (not silently diverge / reimplement).
            import importlib
            mod = importlib.import_module(f"serum2.evidence.kernels.{metric_name}")
            kernel_fn = mod.kernel

            import numpy as np
            # 2s buffer: long enough for tail-window metrics (tail_start=0.6s
            # default) to have a non-empty slice; a too-short buffer produces
            # NaN on both sides, and NaN != NaN would falsely fail this check.
            test_audio = np.random.RandomState(42).randn(2, 44100 * 2) * 0.1
            kernel_value = float(kernel_fn(test_audio, sample_rate=44100))
            metrics_value = float(METRICS[metric_name](test_audio))

            if kernel_value != metrics_value:
                failures.append(
                    f"{target}: METRICS[{metric_name!r}] diverges from "
                    f"kernels/{metric_name}.py (kernel={kernel_value}, METRICS={metrics_value})"
                )

    if failures:
        print("[FAIL] Registry synchronization failures:")
        for f in failures:
            print(f"  - {f}")
        return False

    print(f"[PASS] All {len(registry.contracts)} loaded contract(s) have resolvable, "
          f"kernel-consistent measurement metrics")
    return True


def test_attack_onset_rms_db_specifically():
    """Explicit regression guard for the exact bug this test suite exists to prevent."""
    if "attack_onset_rms_db" not in METRICS:
        print("[FAIL] attack_onset_rms_db missing from METRICS")
        return False

    kernel_file = Path(__file__).parent / "kernels" / "attack_onset_rms_db.py"
    if not kernel_file.exists():
        print("[FAIL] kernels/attack_onset_rms_db.py not found")
        return False

    import importlib
    import numpy as np
    mod = importlib.import_module("serum2.evidence.kernels.attack_onset_rms_db")
    test_audio = np.random.RandomState(7).randn(2, 4410) * 0.2

    kernel_value = float(mod.kernel(test_audio, sample_rate=44100))
    metrics_value = float(METRICS["attack_onset_rms_db"](test_audio))

    if kernel_value != metrics_value:
        print(f"[FAIL] attack_onset_rms_db: kernel={kernel_value} != METRICS={metrics_value}")
        return False

    print(f"[PASS] attack_onset_rms_db: METRICS and kernel agree ({kernel_value})")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MEASUREMENT REGISTRY SYNCHRONIZATION TEST")
    print("=" * 80 + "\n")

    results = [
        ("All loaded contracts resolvable", test_all_loaded_contracts_have_resolvable_metrics()),
        ("attack_onset_rms_db specific guard", test_attack_onset_rms_db_specifically()),
    ]

    print("\n" + "=" * 80)
    passed = sum(1 for _, r in results if r)
    for name, result in results:
        print(f"  [{'PASS' if result else 'FAIL'}] {name}")
    print(f"\n{passed}/{len(results)} passed")

    if passed != len(results):
        sys.exit(1)
