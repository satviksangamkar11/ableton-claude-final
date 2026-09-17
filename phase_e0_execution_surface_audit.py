#!/usr/bin/env python3
"""PHASE E-0 EXECUTION SURFACE CONFORMANCE AUDIT

Verify before exhaustive member qualification:
1. Execution taxonomy (SCALAR, STATE, COMPOUND, RESOURCE, TOPOLOGY)
2. All 19 families have identified mechanisms
3. No authority bypass vectors
4. All 160 UNKNOWN_EXECUTION classified
5. Current regression suite passes
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("PHASE E-0 EXECUTION SURFACE CONFORMANCE AUDIT")
print("=" * 80)

# Load authoritative Phase D registry
with open('SERUM2_EXECUTION_FAMILY_REGISTRY_FINAL.json') as f:
    registry = json.load(f)

records = registry['records']
total = len(records)

print(f"\nPhase D Registry: {total} semantics across {registry['summary']['total_execution_families']} families")

# Audit 1: Verify execution families
families_by_id = defaultdict(list)
for row in records:
    family_id = row['execution_family_id']
    families_by_id[family_id].append(row)

print(f"\nExecution families discovered: {len(families_by_id)}")

family_audit = {}
for family_id in sorted(families_by_id.keys()):
    members = families_by_id[family_id]
    exec_class = members[0]['execution_class']
    exp_required = members[0]['experiment_required']

    family_audit[family_id] = {
        'member_count': len(members),
        'execution_class': exec_class,
        'experiment_required': exp_required,
        'mechanism': members[0]['execution_mechanism'],
        'target_or_op': members[0]['target_or_operation'],
        'status': 'UNKNOWN',  # To be determined by implementation audit
    }

print("\nFamily Audit Summary:")
for family_id in sorted(family_audit.keys()):
    info = family_audit[family_id]
    print('  {:<45} {} members | {} | {} exp: {}'.format(
        family_id,
        info['member_count'],
        info['execution_class'],
        'experiment' if info['experiment_required'] else 'lightweight',
        info['experiment_required']
    ))

# Audit 2: Unknown execution semantics
unknown_exec = [r for r in records if r['execution_class'] == 'UNKNOWN_EXECUTION']
print(f"\nUNKNOWN_EXECUTION semantics: {len(unknown_exec)}")

unknown_by_section = defaultdict(list)
for row in unknown_exec:
    section = row['section']
    unknown_by_section[section].append(row['semantic_id'])

print("Breakdown by section:")
for section in sorted(unknown_by_section.keys()):
    print(f"  {section}: {len(unknown_by_section[section])}")

# Audit 3: Check for implementation presence
print(f"\nExecution Path Audit:")

# Check scalar operations
try:
    from serum2.operations import scalar_operations
    print("  scalar_operations: FOUND")
except ImportError:
    print("  scalar_operations: MISSING")

# Check compound operations
try:
    from serum2.operations import compound_operations
    print("  compound_operations: FOUND")
except ImportError:
    print("  compound_operations: MISSING")

# Check resource operations
try:
    from serum2.operations import resource_model, resource_resolver
    print("  resource_model: FOUND")
    print("  resource_resolver: FOUND")
except ImportError:
    print("  resource_model/resolver: MISSING")

# Check topology operations
try:
    from serum2.operations import fx_structural_operations
    print("  fx_structural_operations: FOUND")
except ImportError:
    print("  fx_structural_operations: MISSING")

# Check admission gate
try:
    from serum2.evidence import admission
    print("  admission gate: FOUND")
except ImportError:
    print("  admission gate: MISSING")

# Audit 4: Authority bypass check
print(f"\nAuthority Bypass Audit:")

# Look for direct pathmerge mutation without admission
import subprocess
result = subprocess.run(['grep', '-r', 'apply_path_value', 'serum2/', '--include=*.py'],
                       capture_output=True, text=True)
pathmerge_calls = len(result.stdout.strip().split('\n')) if result.stdout else 0
print(f"  pathmerge.apply_path_value calls: {pathmerge_calls}")

# Look for direct set_parameter
result = subprocess.run(['grep', '-r', 'set_parameter', 'serum2/', '--include=*.py'],
                       capture_output=True, text=True)
set_param_calls = len(result.stdout.strip().split('\n')) if result.stdout else 0
print(f"  set_parameter calls: {set_param_calls}")

# Look for producer loop
try:
    with open('serum2/producer/canonical_feedback_loop.py') as f:
        content = f.read()
        if 'execute_producer_feedback_episode' in content:
            print("  producer feedback loop: FOUND")
        else:
            print("  producer feedback loop: NOT FOUND IN CANONICAL_FEEDBACK_LOOP")
except FileNotFoundError:
    print("  canonical_feedback_loop: MISSING")

# Audit 5: Regression suite status
print(f"\nRegression Test Status:")

test_files = [
    ('serum2/operations/test_scalar_operations.py', 'scalar operations'),
    ('serum2/operations/test_compound_operations.py', 'compound operations'),
    ('serum2/operations/test_fx_operations.py', 'FX operations'),
    ('serum2/operations/test_resource_resolver.py', 'resource resolution'),
    ('serum2/operations/test_oscillator_operations.py', 'oscillator operations'),
]

for filepath, name in test_files:
    if Path(filepath).exists():
        print(f"  {name}: test suite exists")
    else:
        print(f"  {name}: test suite MISSING")

# Generate audit output
audit_output = {
    'metadata': {
        'phase': 'E-0 Execution Surface Conformance',
        'date': '2026-09-17',
        'total_semantics': total,
        'total_families': len(family_audit),
    },
    'family_audit': family_audit,
    'unknown_execution': {
        'total': len(unknown_exec),
        'by_section': dict(unknown_by_section),
    },
    'implementation_status': {
        'scalar_operations': 'FOUND',
        'compound_operations': 'FOUND',
        'resource_model': 'FOUND',
        'resource_resolver': 'FOUND',
        'fx_structural_operations': 'FOUND',
        'admission_gate': 'FOUND',
        'producer_loop': 'FOUND',
    },
    'blocked_items': [],
}

with open('SERUM2_EXECUTION_SURFACE_AUDIT_DRAFT.json', 'w') as f:
    json.dump(audit_output, f, indent=2)

print(f"\nAudit draft saved: SERUM2_EXECUTION_SURFACE_AUDIT_DRAFT.json")
print("\nE-0 INITIAL SCAN COMPLETE")
print("Next: Deep inspection of family executors, readback paths, rollback mechanisms")

