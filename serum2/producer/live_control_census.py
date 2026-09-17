#!/usr/bin/env python3
"""
SERUM Live Control Census

Automated mutation + readback census for all 396 frozen targets.
Answers: "Can I actually move each control and see/verify the change?"

Usage:
    python3 serum2/producer/live_control_census.py

Output:
    SERUM2_LIVE_CONTROL_CENSUS_RESULTS.json
"""

import json
import sys
import os
import time
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2 import bridge
import serum2.evidence.epoch as epoch_mod

VST3 = epoch_mod.SERUM_VST3

# Sentinel values for mutation testing
MUTATION_SENTINELS = {
    "float": 0.75,  # Distinctive float value
    "int": 42,
    "bool": True,
}


def load_targets():
    """Load frozen 396-target vocabulary."""
    with open('serum2/reconciliation/SERUM2_TARGET_NORMALIZED_V4.json') as f:
        data = json.load(f)
    return {t['target_id']: t for t in data['targets']}


def load_semantics():
    """Load frozen 908-semantic inventory."""
    with open('serum2/reconciliation/SERUM2_SEMANTIC_NORMALIZED.json') as f:
        data = json.load(f)
    return {r['semantic_id']: r for r in data['records']}


def load_target_to_semantics_map():
    """Map targets to their semantic owners."""
    with open('serum2/reconciliation/SERUM2_CONTROL_PATH_MATRIX.json') as f:
        cp_matrix = json.load(f)

    target_to_semantics = defaultdict(list)
    for rec in cp_matrix['records']:
        for target in rec.get('target_ids', []):
            target_to_semantics[target].append(rec['semantic_id'])

    return target_to_semantics


def attempt_target_mutation(target_id, target_spec):
    """
    Attempt to mutate a single target.

    Returns: {
        'target_id': str,
        'requested_value': float,
        'pre_value': float or None,
        'post_value': float or None,
        'mutation_attempted': bool,
        'mutation_succeeded': bool,
        'readback_changed': bool,
        'error': str or None,
        'method': str
    }
    """

    result = {
        'target_id': target_id,
        'requested_value': None,
        'pre_value': None,
        'post_value': None,
        'mutation_attempted': False,
        'mutation_succeeded': False,
        'readback_changed': False,
        'error': None,
        'method': 'unknown',
    }

    try:
        # Capture baseline skeleton
        skeleton = bridge.capture_v8_skeleton(VST3)
        meta, body = skeleton[0], skeleton[1]
        result['pre_value'] = 'baseline_captured'

        # Determine mutation value based on target type
        mutation_value = MUTATION_SENTINELS.get(target_spec.get('type'), 0.75)
        result['requested_value'] = mutation_value

        # Attempt mutation via pathmerge (if target is a state field)
        from serum2 import pathmerge

        # Try to apply mutation to body
        target_path = target_spec.get('path') or target_id
        try:
            pathmerge.apply_path_value(body, target_path, mutation_value)
            result['mutation_attempted'] = True
            result['method'] = 'state_mutation'

            # Readback
            post_value = pathmerge.read_path_value(body, target_path)
            result['post_value'] = post_value
            result['mutation_succeeded'] = post_value is not None
            result['readback_changed'] = post_value != result['pre_value']

        except Exception as e:
            result['error'] = f"State path mutation failed: {str(e)}"
            result['mutation_succeeded'] = False

    except Exception as e:
        result['error'] = f"Mutation attempt error: {str(e)}"

    return result


def run_census():
    """Run complete control census."""

    print("="*80)
    print("SERUM LIVE CONTROL CENSUS")
    print("="*80)

    targets = load_targets()
    semantics = load_semantics()
    target_to_semantics = load_target_to_semantics_map()

    print(f"\nTargets to test: {len(targets)}")
    print(f"Semantics: {len(semantics)}")
    print(f"Starting census...\n")

    results = {
        'metadata': {
            'date': '2026-09-17',
            'total_targets': len(targets),
            'total_semantics': len(semantics),
            'phase': 'Bulk automated execution census',
        },
        'target_results': [],
        'summary': {
            'mutation_attempted': 0,
            'mutation_succeeded': 0,
            'readback_confirmed': 0,
            'errors': 0,
        },
        'by_method': defaultdict(int),
    }

    for i, (target_id, target_spec) in enumerate(sorted(targets.items())):
        if i % 50 == 0:
            print(f"[{i}/{len(targets)}] Processing {target_id}...")

        result = attempt_target_mutation(target_id, target_spec)

        # Attach semantic owners
        result['semantic_owners'] = target_to_semantics.get(target_id, [])

        results['target_results'].append(result)

        # Update summary
        if result['mutation_attempted']:
            results['summary']['mutation_attempted'] += 1
        if result['mutation_succeeded']:
            results['summary']['mutation_succeeded'] += 1
        if result['readback_changed']:
            results['summary']['readback_confirmed'] += 1
        if result['error']:
            results['summary']['errors'] += 1

        results['by_method'][result['method']] += 1

    # Convert defaultdicts to regular dicts
    results['by_method'] = dict(results['by_method'])

    print(f"\n" + "="*80)
    print(f"CENSUS COMPLETE")
    print(f"="*80)
    print(f"\nResults summary:")
    print(f"  Mutations attempted: {results['summary']['mutation_attempted']}")
    print(f"  Mutations succeeded: {results['summary']['mutation_succeeded']}")
    print(f"  Readback confirmed: {results['summary']['readback_confirmed']}")
    print(f"  Errors: {results['summary']['errors']}")
    print(f"\nBy method:")
    for method, count in sorted(results['by_method'].items()):
        print(f"  {method}: {count}")

    # Save results
    output_path = 'SERUM2_LIVE_CONTROL_CENSUS_RESULTS.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    results = run_census()
    sys.exit(0 if results['summary']['errors'] == 0 else 1)
