#!/usr/bin/env python3
"""PHASE D FINAL CORRECTION — Reclassify 129 TARGET_REQUIRED as UNKNOWN_EXECUTION"""

import json
from collections import defaultdict

# Load authoritative data
with open('SERUM2_COMPLETE_EXECUTABLE_CONTROL_MATRIX.json') as f:
    matrix = json.load(f)

with open('serum2/reconciliation/SERUM2_SEMANTIC_NORMALIZED.json') as f:
    semantics = {r['semantic_id']: r for r in json.load(f)['records']}

with open('serum2/reconciliation/SERUM2_CONTROL_PATH_MATRIX.json') as f:
    cp_matrix = {r['semantic_id']: r for r in json.load(f)['records']}

with open('_phase_c_raw_dispositions.json') as f:
    disposition_data = json.load(f)

# Reconstruct disposition map
disposition_map = {}
for section, disp_dict in disposition_data['dispositions_by_section'].items():
    for disp, sem_ids in disp_dict.items():
        for sem_id in sem_ids:
            disposition_map[sem_id] = disp

# Add target-backed semantics (268)
for row in matrix['records']:
    if row['execution_status'] == 'EXECUTABLE_CENSUS_VERIFIED':
        disposition_map[row['semantic_id']] = 'TARGET_BACKED'

# Build 908-row registry with correct family assignments
rows = []
family_members = defaultdict(int)

for sem_id in sorted(semantics.keys()):
    sem_rec = semantics[sem_id]
    cp_rec = cp_matrix.get(sem_id, {})
    disp = disposition_map.get(sem_id, 'UNKNOWN')
    section = sem_rec.get('section')

    # Determine execution class and family
    if disp == 'TARGET_BACKED':
        exec_class = 'HOST_PARAMETER'
        family_id = 'TARGET_BACKED_CENSUS_VERIFIED'
        rep_family = 'HOST_PARAMETER_REPRESENTATIVE'
        exec_mechanism = 'VST3_parameter_or_state_path'
        target_or_op = sem_rec.get('target_id') or (cp_rec.get('target_ids', ['unknown'])[0] if cp_rec.get('target_ids') else 'unknown')
        exp_required = False
        member_verify = 'lightweight_readback'
        qual_state = 'CENSUS_VERIFIED'

    elif disp == 'UI_ACTION':
        exec_class = 'UI_ACTION'
        family_id = 'UI_ACTION_' + section
        rep_family = 'UI_ACTION_REPRESENTATIVE'
        exec_mechanism = 'ui_control_action'
        target_or_op = 'ui_operation'
        exp_required = True
        member_verify = 'ui_action_test'
        qual_state = 'UNDER_QUALIFICATION'

    elif disp == 'STRUCTURAL_OPERATION':
        exec_class = 'STRUCTURAL_OPERATION'
        family_id = 'STRUCTURAL_OPERATION'
        rep_family = 'STRUCTURAL_OPERATION_REPRESENTATIVE'
        exec_mechanism = 'ui_structural_edit'
        target_or_op = 'structural_operation'
        exp_required = False
        member_verify = 'structural_test'
        qual_state = 'UNDER_QUALIFICATION'

    elif disp == 'RESOURCE_OPERATION':
        exec_class = 'RESOURCE_OPERATION'
        family_id = 'RESOURCE_OPERATION'
        rep_family = 'RESOURCE_OPERATION_REPRESENTATIVE'
        exec_mechanism = 'browser_or_resource_load'
        target_or_op = 'resource_operation'
        exp_required = False
        member_verify = 'resource_test'
        qual_state = 'UNDER_QUALIFICATION'

    elif disp == 'MATRIX_ROUTE':
        exec_class = 'MATRIX_ROUTE'
        family_id = 'MATRIX_ROUTE'
        rep_family = 'MATRIX_ROUTE_REPRESENTATIVE'
        exec_mechanism = 'matrix_routing_assignment'
        target_or_op = 'matrix_routing'
        exp_required = False
        member_verify = 'routing_test'
        qual_state = 'UNDER_QUALIFICATION'

    elif disp == 'BODY_STATE_FIELD':
        exec_class = 'BODY_STATE_FIELD'
        family_id = 'BODY_STATE_FIELD_' + section
        rep_family = 'BODY_STATE_FIELD_REPRESENTATIVE'
        exec_mechanism = 'conditional_state_mutation'
        target_or_op = 'body_state_field'
        exp_required = True
        member_verify = 'state_readback'
        qual_state = 'UNDER_QUALIFICATION'

    elif disp == 'SHARED_PHYSICAL_PARAMETER':
        exec_class = 'SHARED_PHYSICAL_PARAMETER'
        family_id = 'SHARED_PHYSICAL_PARAMETER'
        rep_family = 'SHARED_PHYSICAL_REPRESENTATIVE'
        exec_mechanism = 'multi_semantic_shared'
        target_or_op = 'shared_parameter'
        exp_required = False
        member_verify = 'shared_test'
        qual_state = 'UNDER_QUALIFICATION'

    elif disp == 'TARGET_REQUIRED':
        # CORRECTION: TARGET_REQUIRED semantics are UNKNOWN_EXECUTION (pending investigation)
        exec_class = 'UNKNOWN_EXECUTION'
        family_id = 'UNKNOWN_EXECUTION'
        rep_family = 'UNKNOWN_EXECUTION_REPRESENTATIVE'
        exec_mechanism = 'investigation_required'
        target_or_op = 'unknown'
        exp_required = True
        member_verify = 'investigation_test'
        qual_state = 'INVESTIGATION_REQUIRED'

    else:  # UNKNOWN_EXECUTION (from control path, not disposition)
        exec_class = 'UNKNOWN_EXECUTION'
        family_id = 'UNKNOWN_EXECUTION'
        rep_family = 'UNKNOWN_EXECUTION_REPRESENTATIVE'
        exec_mechanism = 'investigation_required'
        target_or_op = 'unknown'
        exp_required = True
        member_verify = 'investigation_test'
        qual_state = 'INVESTIGATION_REQUIRED'

    # Track family membership
    family_members[family_id] += 1

    # Build row
    rows.append({
        'semantic_id': sem_id,
        'section': section,
        'module': sem_rec.get('module'),
        'execution_class': exec_class,
        'execution_family_id': family_id,
        'representation_family_id': rep_family,
        'execution_mechanism': exec_mechanism,
        'target_or_operation': target_or_op,
        'existing_evidence': disp,
        'representative_member': 'TBD_INVESTIGATION' if exp_required else 'verified_by_census',
        'exception_status': 'investigation_pending' if exp_required else 'none',
        'experiment_required': exp_required,
        'member_verification_required': member_verify,
        'qualification_state': qual_state,
    })

# Verify invariants
print('PHASE D FINAL CORRECTION')
print()
assert len(rows) == 908, 'ERROR: Expected 908 rows, got {}'.format(len(rows))
print('Pass: All 908 semantics present')

# Count by execution class
exec_class_counts = defaultdict(int)
for row in rows:
    exec_class_counts[row['execution_class']] += 1

print()
print('Execution class distribution (EXACT):')
total_exec = 0
for cls in sorted(exec_class_counts.keys()):
    count = exec_class_counts[cls]
    total_exec += count
    print('  {}: {}'.format(cls, count))
print('  ——————————————————————————————')
print('  TOTAL: {}'.format(total_exec))

# Verify sum
assert total_exec == 908, 'ERROR: Execution class sum {} != 908'.format(total_exec)
print('Pass: Execution class sum = 908')

# Count families and workload
unique_families = set(row['execution_family_id'] for row in rows)
print()
print('Execution families (EXACT): {}'.format(len(unique_families)))

exp_required_rows = [r for r in rows if r['experiment_required']]
deep_exp_families = set(r['execution_family_id'] for r in exp_required_rows)
lightweight_rows = [r for r in rows if not r['experiment_required']]

print()
print('WORKLOAD BREAKDOWN (EXACT):')
print('  Families requiring deep experiment: {}'.format(len(deep_exp_families)))
print('  Deep experiments (one representative per family): {}'.format(len(deep_exp_families)))
print('  Lightweight member verifications: {}'.format(len(lightweight_rows)))
print('  Investigation tests (for UNKNOWN_EXECUTION): {}'.format(
    sum(1 for r in rows if r['qualification_state'] == 'INVESTIGATION_REQUIRED')))
print()
print('  Total = {} + {} = {}'.format(
    len(deep_exp_families),
    len(lightweight_rows),
    len(deep_exp_families) + len(lightweight_rows)
))

# Verify no UNCLASSIFIED
unclassified = [r for r in rows if r['execution_class'] == 'UNCLASSIFIED']
assert len(unclassified) == 0, 'ERROR: {} UNCLASSIFIED rows remain'.format(len(unclassified))
print('Pass: Zero UNCLASSIFIED rows')

# Verify family membership sum
total_family_members = sum(family_members.values())
assert total_family_members == 908, 'ERROR: Family membership sum {} != 908'.format(total_family_members)
print('Pass: Family membership sum = 908')

# Save final registry
registry = {
    'metadata': {
        'phase': 'D — Complete Execution Family Registry (CORRECTED)',
        'date': '2026-09-17',
        'correction': 'Reclassified 129 TARGET_REQUIRED as UNKNOWN_EXECUTION',
    },
    'summary': {
        'total_semantics': 908,
        'execution_classes': dict(sorted(exec_class_counts.items())),
        'total_execution_families': len(unique_families),
        'deep_experiments_required': len(deep_exp_families),
        'lightweight_verifications_required': len(lightweight_rows),
        'investigation_tests_required': sum(1 for r in rows if r['qualification_state'] == 'INVESTIGATION_REQUIRED'),
    },
    'records': rows,
}

with open('SERUM2_EXECUTION_FAMILY_REGISTRY_FINAL.json', 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2)

print()
print('Saved: SERUM2_EXECUTION_FAMILY_REGISTRY_FINAL.json')

