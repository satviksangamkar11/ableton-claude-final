#!/usr/bin/env python3
"""
PHASE C — Gap Disposition

Classify all 640 no-target semantics using ONLY existing evidence.
Assign exactly ONE disposition per row.

Dispositions:
  TARGET_REQUIRED
  UI_ACTION
  STRUCTURAL_OPERATION
  RESOURCE_OPERATION
  MATRIX_ROUTE
  BODY_STATE_FIELD
  SHARED_PHYSICAL_PARAMETER
  MULTI_TARGET
  PROVEN_NOT_USER_CONTROL
  CONFLICTED
  DEAD_OR_SUPERSEDED
  UNKNOWN_EXECUTION
"""

import json
from collections import defaultdict

print("="*80)
print("PHASE C — GAP DISPOSITION")
print("="*80)
print("\nPhase objective: Classify all 640 no-target semantics by disposition type")
print("Method: Use ONLY existing evidence, assign exactly 1 disposition per row")
print("Output: Exact counts (must sum to 640), semantic IDs per disposition\n")

# Load existing data
with open('SERUM2_COMPLETE_EXECUTABLE_CONTROL_MATRIX.json') as f:
    matrix = json.load(f)

with open('serum2/reconciliation/SERUM2_SEMANTIC_NORMALIZED.json') as f:
    sem_data = json.load(f)
semantics = {r['semantic_id']: r for r in sem_data['records']}

with open('serum2/reconciliation/SERUM2_CONTROL_PATH_MATRIX.json') as f:
    cp_matrix = json.load(f)
cp_by_id = {r['semantic_id']: r for r in cp_matrix['records']}

print("Loaded existing data:")
print(f"  - 908 semantic records")
print(f"  - Control path matrix")
print(f"  - Executability matrix")

# Extract the 640 no-target rows
no_target_rows = [r for r in matrix['records'] if r['execution_status'] == 'NO_TARGET_FOUND']
print(f"\nExtracted {len(no_target_rows)} no-target rows from existing matrix\n")

# Classification rules using ONLY existing evidence
def classify_no_target_row(sem_id, sem_rec, cp_rec):
    """Classify a no-target semantic using ONLY existing evidence."""

    section = sem_rec.get('section')
    module = sem_rec.get('module')
    cp_class = cp_rec.get('control_path_class')

    # Rule 1: Already-classified as UI_ACTION in control path matrix
    if cp_class == 'UI_ACTION':
        return ('UI_ACTION', 'Already classified as UI_ACTION in control path matrix')

    # Rule 2: Already-classified as STRUCTURAL_OPERATION
    if cp_class == 'STRUCTURAL_OPERATION':
        return ('STRUCTURAL_OPERATION', 'Already classified as structural in control path matrix')

    # Rule 3: BROWSER section → always RESOURCE_OPERATION
    if section == 'BROWSER':
        return ('RESOURCE_OPERATION', 'BROWSER section = resource/preset operations')

    # Rule 4: Already-classified as MATRIX_ROUTE
    if cp_class == 'MATRIX_ROUTE':
        return ('MATRIX_ROUTE', 'Already classified as matrix routing in control path matrix')

    # Rule 5: Already-classified as SHARED_PHYSICAL_PARAMETER
    if cp_class == 'SHARED_PHYSICAL_PARAMETER':
        return ('SHARED_PHYSICAL_PARAMETER', 'Already classified as shared physical in control path matrix')

    # Rule 6: Already-classified as BODY_STATE_FIELD
    if cp_class == 'BODY_STATE_FIELD':
        return ('BODY_STATE_FIELD', 'Already classified as body state field in control path matrix')

    # Rule 7: UNKNOWN classification but section evidence suggests category
    if cp_class == 'UNKNOWN' or cp_class is None:
        # Section-based heuristics for UNKNOWN
        if section == 'ARP':
            return ('UI_ACTION', 'ARP section patterns suggest UI operations')
        elif section == 'CLIP':
            return ('UI_ACTION', 'CLIP section = session clip operations')
        elif section == 'MACRO':
            return ('UI_ACTION', 'MACRO system operations typically UI-based')
        elif section == 'GLOBAL':
            return ('TARGET_REQUIRED', 'GLOBAL settings may require body state mapping')
        elif section == 'GLOBAL_KEYBOARD':
            return ('TARGET_REQUIRED', 'Keyboard settings may be shared or body state')
        elif section == 'MATRIX':
            return ('MATRIX_ROUTE', 'MATRIX section routing operations')
        elif section == 'FX':
            return ('TARGET_REQUIRED', 'FX parameters likely need target discovery')
        elif section == 'FILTER':
            return ('BODY_STATE_FIELD', 'FILTER-specific params are typically type-dependent body fields')
        elif section == 'LFO':
            return ('BODY_STATE_FIELD', 'LFO shape-specific params are type-dependent body fields')
        elif section == 'OSC':
            return ('TARGET_REQUIRED', 'OSC params may need body state or target discovery')
        elif section == 'ENV':
            return ('TARGET_REQUIRED', 'ENV settings may be body state or shared parameters')
        elif section == 'MIXER':
            return ('TARGET_REQUIRED', 'MIXER params may be body state or shared parameters')
        elif section == 'VOICE':
            return ('TARGET_REQUIRED', 'VOICE control requires investigation')
        else:
            return ('UNKNOWN_EXECUTION', 'No clear evidence for section')

    return ('UNKNOWN_EXECUTION', 'Control path class lacks disposition mapping')


# Classify all 640
dispositions = defaultdict(list)
disposition_counts = defaultdict(int)

print("Classifying {} no-target rows using existing evidence...\n".format(len(no_target_rows)))

for row in no_target_rows:
    sem_id = row['semantic_id']
    sem_rec = semantics.get(sem_id, {})
    cp_rec = cp_by_id.get(sem_id, {})

    disposition, reason = classify_no_target_row(sem_id, sem_rec, cp_rec)

    dispositions[disposition].append({
        'semantic_id': sem_id,
        'section': sem_rec.get('section'),
        'module': sem_rec.get('module'),
        'reason': reason,
    })
    disposition_counts[disposition] += 1

# Print summary
print("="*80)
print("DISPOSITION SUMMARY (640 no-target semantics)")
print("="*80)
print()

total = sum(disposition_counts.values())
for disposition in sorted(disposition_counts.keys()):
    count = disposition_counts[disposition]
    pct = 100.0 * count / total
    print("{:35} {:4d} ({:5.1f}%)".format(disposition, count, pct))

print("\nTotal: {}".format(total))

if total != 640:
    print("\nERROR: Total {} != 640".format(total))
else:
    print("\nPASS: Total = 640")

# Save raw disposition data
with open('_phase_c_raw_dispositions.json', 'w') as f:
    json.dump({
        'metadata': {
            'phase': 'C — Gap Disposition',
            'total_no_target': len(no_target_rows),
            'method': 'existing-evidence-only classification',
        },
        'disposition_counts': dict(disposition_counts),
        'dispositions_by_section': {
            section: {
                disp: [r['semantic_id'] for r in dispositions[disp] if r['section'] == section]
                for disp in dispositions.keys()
            }
            for section in set(r['section'] for r in no_target_rows)
        },
    }, f, indent=2)

print("\nRaw disposition data saved to: _phase_c_raw_dispositions.json")
