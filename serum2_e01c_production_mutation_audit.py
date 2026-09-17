#!/usr/bin/env python3
"""PHASE E-0.1C — PRODUCTION MUTATION AUTHORITY INVENTORY

Audit EVERY production Serum mutation path.
Classify each as:
- ROUTED_TO_GATE: goes through execute_mutation_with_authority()
- PRE_AUTHORITY_SETUP: legitimate pre-admission (baseline context, etc)
- BYPASS: direct mutation without authority check (BLOCKER)
- NON_MUTATING: read-only (not a mutation)

Target: all production mutations -> authority gate
"""

import subprocess
import re
from collections import defaultdict
from pathlib import Path

def audit_production_mutations():
    """Search for all production mutation calls."""

    repo_root = Path(".")

    # Mutation entry points to audit
    mutation_patterns = [
        ("pathmerge.apply_path_value", "Direct state mutation via pathmerge"),
        ("set_parameter", "Direct VST3 parameter set"),
        ("Mutation\\(", "Direct Mutation object construction"),
        ("compiled_mutations.execute", "Mutation list execution"),
        ("pathmerge.apply_path_value", "State path mutation"),
    ]

    results = defaultdict(list)

    for pattern, description in mutation_patterns:
        # Search production code (exclude tests, exclude comments-only)
        cmd = f"grep -r '{pattern}' serum2/ --include='*.py' | grep -v 'test_' | grep -v '#'"

        try:
            output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if output.stdout:
                lines = output.stdout.strip().split('\n')
                for line in lines:
                    if line:
                        results[pattern].append(line)
        except Exception as e:
            print(f"[ERROR] {pattern}: {e}")

    return results

def classify_mutation_path(filepath, code_context):
    """Classify a mutation path based on file and context."""

    # E-0.1B: The official choke point
    if "execute_mutation_with_authority" in code_context:
        return "ROUTED_TO_GATE"

    # Legitimate pre-admission setup (not yet through gate)
    if "canonical_feedback_loop.py" in filepath and "prerequisite_overrides" in code_context:
        return "PRE_AUTHORITY_SETUP"  # baseline context before admission

    # Test files (excluded from audit)
    if "test_" in filepath:
        return "TEST_ONLY"

    # Producer loop (should route through gate)
    if "canonical_feedback_loop.py" in filepath:
        return "AUDIT_REQUIRED"  # producer loop needs wiring

    # Qualification/evidence code (experimental, not production)
    if "qualification/" in filepath:
        return "QUALIFICATION_ONLY"

    # Everything else in production paths needs audit
    return "AUDIT_REQUIRED"

def main():
    print("="*80)
    print("PHASE E-0.1C — PRODUCTION MUTATION AUTHORITY INVENTORY")
    print("="*80 + "\n")

    mutations = audit_production_mutations()

    inventory = {
        "ROUTED_TO_GATE": [],
        "PRE_AUTHORITY_SETUP": [],
        "AUDIT_REQUIRED": [],
        "TEST_ONLY": [],
        "QUALIFICATION_ONLY": [],
        "BYPASS": [],
    }

    print("Mutation entry points found:\n")

    total_calls = 0
    for pattern, calls in sorted(mutations.items()):
        print(f"{pattern}: {len(calls)} calls")
        total_calls += len(calls)

        for call_line in calls[:3]:  # Show first 3
            print(f"  {call_line[:100]}")
        if len(calls) > 3:
            print(f"  ... and {len(calls) - 3} more")

    print(f"\nTotal mutation calls found: {total_calls}\n")

    # Parse results to classify
    classified = defaultdict(int)

    for pattern, calls in mutations.items():
        for call_line in calls:
            # Extract filepath
            parts = call_line.split(":")
            if len(parts) >= 2:
                filepath = parts[0]
                context = ":".join(parts[2:])

                classification = classify_mutation_path(filepath, context)
                classified[classification] += 1

    print("CLASSIFICATION SUMMARY:\n")
    for status in ["ROUTED_TO_GATE", "PRE_AUTHORITY_SETUP", "AUDIT_REQUIRED", "TEST_ONLY", "QUALIFICATION_ONLY", "BYPASS"]:
        count = classified[status]
        print(f"  {status:30} {count:3d}")

    audit_required = classified["AUDIT_REQUIRED"]
    routed = classified["ROUTED_TO_GATE"]

    print(f"\n{'='*80}")
    print(f"E-0.1C VERDICT:")
    print(f"{'='*80}")
    print(f"Production mutations needing authority gate: {audit_required}")
    print(f"Already routed through gate: {routed}")
    print(f"Gateway coverage: {routed}/{routed + audit_required} = {100*routed/(routed + audit_required) if (routed + audit_required) > 0 else 0:.1f}%\n")

    if audit_required > 0:
        print("BLOCKERS:")
        print(f"  - {audit_required} production mutation paths require routing to execute_mutation_with_authority()")
        print(f"  - Primary: canonical_feedback_loop.py needs wiring")
        print(f"  - Secondary: qualification/* paths (check if production or test)")
        print(f"\nE-0.1C STATUS: BLOCKED")
        print("Next: Wire producer loop and other production paths through choke point")
    else:
        print("E-0.1C STATUS: PASS")
        print("All production mutations routed through authority gate")

    print(f"\nTo proceed to E-0.1D (regression tests):")
    print(f"  1. Inspect canonical_feedback_loop.py usage of mutations")
    print(f"  2. Wire through execute_mutation_with_authority()")
    print(f"  3. Re-audit to verify 100% coverage")
    print(f"  4. Run regression suite")
    print(f"  5. Then E-0.1 PASS and E-1 unblocked")

if __name__ == "__main__":
    main()

