"""Diagnostic: verify CBOR mutations actually propagated.

For each control, inspect:
1. The baseline serialized state
2. The treatment serialized state
3. What CBOR field changed
4. Whether other fields changed (unexpected mutations)
5. Whether the changed field affects the signal path
"""

import json
import subprocess
import sys
from pathlib import Path

from serum2 import bridge, pathmerge
from serum2.evidence import epoch
from serum2.qualification.seed_12_experiments import SEED_12_EXPERIMENTS


def load_evidence_file(exp_num):
    """Load one evidence file by experiment number."""
    pattern = f"serum2/qualification/A_SEED_EXPERIMENT_{exp_num:02d}_*.json"
    files = list(Path(".").glob(pattern))
    if not files:
        return None
    with open(files[0]) as f:
        return json.load(f)


def compare_cbor_states(baseline_cbor, treatment_cbor, target_path, treatment_value):
    """Find what changed between baseline and treatment CBOR states.

    Returns:
        (changed, other_diffs) where:
        - changed: (path, old_val, new_val) or None if not found
        - other_diffs: list of (path, old_val, new_val) for unexpected changes
    """

    def flatten_dict(d, prefix=""):
        """Recursively flatten nested dict to dot-notation paths."""
        result = {}
        for key, val in d.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(val, dict):
                result.update(flatten_dict(val, path))
            elif isinstance(val, list):
                for i, item in enumerate(val):
                    list_path = f"{path}.{i}"
                    if isinstance(item, dict):
                        result.update(flatten_dict(item, list_path))
                    else:
                        result[list_path] = item
            else:
                result[path] = val
        return result

    baseline_flat = flatten_dict(baseline_cbor)
    treatment_flat = flatten_dict(treatment_cbor)

    # Find all changes
    changed = None
    other_diffs = []

    for path in set(baseline_flat.keys()) | set(treatment_flat.keys()):
        baseline_val = baseline_flat.get(path, "KEY_MISSING")
        treatment_val = treatment_flat.get(path, "KEY_MISSING")

        if baseline_val != treatment_val:
            # This is a change
            if path == target_path or path.endswith(target_path.split(".")[-1]):
                # This might be our intended change
                if changed is None:
                    changed = (path, baseline_val, treatment_val)
            else:
                # Unexpected change
                other_diffs.append((path, baseline_val, treatment_val))

    return changed, other_diffs


def diagnose_mutation(exp_num, exp_spec):
    """Diagnose one experiment's CBOR mutation."""

    print("=" * 70)
    print(f"DIAGNOSTIC: Experiment {exp_num}: {exp_spec.semantic_target}")
    print("=" * 70)
    print()

    # Load evidence
    evidence = load_evidence_file(exp_num)
    if not evidence or not evidence.get("success"):
        print(f"[FAIL] Could not load evidence for experiment {exp_num}")
        print()
        return

    # Get the CBOR path and treatment value
    cbor_path = exp_spec.treatment_cbor_path
    treatment_value = exp_spec.treatment_cbor_value

    print(f"Intended mutation:")
    print(f"  CBOR path: {cbor_path}")
    print(f"  Treatment value: {treatment_value}")
    print()

    # We don't have the serialized CBOR states in the evidence file,
    # so we'll need to reconstruct them from scratch.
    # Load the skeleton and apply the same mutations.

    print("Reconstructing baseline state...")
    try:
        skeleton = bridge.capture_v8_skeleton(epoch.SERUM_VST3)
        meta_baseline, body_baseline = skeleton

        # Read baseline value at path
        try:
            baseline_val = pathmerge.read_path_value(body_baseline, cbor_path)
            print(f"  Baseline value at {cbor_path}: {baseline_val}")
        except Exception as e:
            print(f"  [ERROR] Could not read baseline: {e}")
            baseline_val = None
    except Exception as e:
        print(f"[FAIL] Could not load skeleton: {e}")
        print()
        return

    print()
    print("Reconstructing treatment state...")
    try:
        skeleton = bridge.capture_v8_skeleton(epoch.SERUM_VST3)
        meta_treatment, body_treatment = skeleton

        # Apply the treatment mutation
        pathmerge.apply_path_value(body_treatment, cbor_path, treatment_value)

        # Read treatment value at path
        try:
            treatment_read = pathmerge.read_path_value(body_treatment, cbor_path)
            print(f"  Treatment value at {cbor_path}: {treatment_read}")
        except Exception as e:
            print(f"  [ERROR] Could not read treatment: {e}")
            treatment_read = None
    except Exception as e:
        print(f"[FAIL] Could not apply mutation: {e}")
        print()
        return

    print()
    print("Mutation propagation:")
    if baseline_val is not None and treatment_read is not None:
        if baseline_val == treatment_read:
            print(f"  [NO CHANGE] Baseline and treatment values are identical")
            print(f"  Classification: MUTATION_NOT_APPLIED")
        else:
            print(f"  [CHANGED] {baseline_val} → {treatment_read}")
            print(f"  Delta: {treatment_read - baseline_val if isinstance(treatment_read, (int, float)) else 'N/A'}")
            print(f"  Classification: MUTATION_APPLIED")
    else:
        print(f"  [ERROR] Could not read values for comparison")
        print(f"  Classification: UNKNOWN")

    print()

    # Get observed measurements from evidence
    obs = evidence.get("behavior_observation", {})
    if obs.get("measurements"):
        m = obs["measurements"][0]  # primary measurement
        print(f"Observed effect in audio:")
        print(f"  Measurement: {m['name']}")
        print(f"  Baseline: {m['baseline']:.2f}")
        print(f"  Treatment: {m['treatment']:.2f}")
        print(f"  Delta: {m['delta']:+.2f}")
        print(f"  Threshold: {m['threshold']}")
        print(f"  Status: {m['status']}")

    print()
    print("-" * 70)
    print()


def main():
    print("MUTATION PROPAGATION DIAGNOSTICS")
    print("=" * 70)
    print()

    # Start with Filter1.Resonance (exp 2) and Filter2.Cutoff (exp 3)
    experiments_to_diagnose = [
        (2, SEED_12_EXPERIMENTS[1]),  # Filter1.Resonance
        (3, SEED_12_EXPERIMENTS[2]),  # Filter2.Cutoff
    ]

    for exp_num, exp_spec in experiments_to_diagnose:
        diagnose_mutation(exp_num, exp_spec)

    print("=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
