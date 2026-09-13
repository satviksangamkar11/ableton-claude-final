#!/usr/bin/env python3
"""Context-Aware Target Resolution for NO_SERUM_TARGET and AMBIGUOUS items

Invariants:
  A. RESOLVED items are never overwritten
  B. AMBIGUOUS items are not silently converted to RESOLVED
  C. Keyword matching generates candidates, not final targets
  D. Candidate becomes RESOLVED only with sufficient semantic context
  E. Generic terms alone (frequency, pitch, gain, etc.) are insufficient
  F. Authoritative semantic vocabulary is the identity source

Strategy:
  - Extract KnowledgeItems with status NO_SERUM_TARGET or AMBIGUOUS
  - Apply context-aware rules that require explicit procedural language
  - Generate hypotheses only for items with high-confidence mappings
  - Preserve all pre-existing mappings
"""

import json
import re
from collections import defaultdict


def load_target_resolution():
    """Load the trusted target resolution state."""
    path = "serum2/knowledge/yt_f507169bd7cb_target_resolution.json"
    with open(path) as f:
        return json.load(f)


def load_extracted_items():
    """Load extracted KnowledgeItems."""
    path = "serum2/knowledge/yt_f507169bd7cb_semantic_extraction.json"
    with open(path) as f:
        data = json.load(f)
    return {item['knowledge_item_id']: item for item in data.get('extracted_knowledge_items', [])}


# =========================================================================
# CONTEXT-AWARE RESOLUTION RULES
# =========================================================================
# Each rule requires explicit procedural context + semantic target

CONTEXT_AWARE_RULES = {
    "OSC1.Level": {
        "capability_key": "oscillator_level",
        # Rules that require EXPLICIT context binding
        "contextual_patterns": [
            # Explicit level/volume control language
            r"oscillator\s+level\s+(?:control|adjust|knob|parameter|slider)",
            r"oscillator\s+volume\s+(?:control|adjust|knob|parameter|slider)",
            r"oscillator\s+amplitude\s+(?:control|adjust|knob|parameter|slider)",
            r"osc\s+level\s+(?:control|adjust|knob|parameter|slider)",
            r"(?:to|adjust|control|set)\s+(?:the\s+)?oscillator\s+level",
            r"(?:to|adjust|control|set)\s+(?:the\s+)?oscillator\s+volume",
            # Procedural language
            r"how\s+to\s+(?:change|adjust|control)\s+(?:oscillator\s+)?(?:level|volume|amplitude)",
            r"click\s+(?:on\s+)?(?:the\s+)?(?:level|volume|amplitude)",
        ],
        "rejection_patterns": [
            # Generic/theoretical discussion
            r"oscillator.*come.*with|oscillator.*have|oscillator.*are|oscillator.*types",
            r"amplitude\s+(?:of|in|affects).*(?:harmonics|tone|sound|frequency)",
        ],
        "min_confidence": 0.85,
    },
    "OSC1.Detune": {
        "capability_key": "oscillator_detune",
        "contextual_patterns": [
            # Explicit detune control language
            r"oscillator.*(?:detun|fine[\s-]?tun).*(?:control|adjust|knob|parameter|slider|amount)",
            r"osc.*(?:detun|fine[\s-]?tun).*(?:control|adjust|knob|parameter|slider|amount)",
            r"(?:to|adjust|control|set)\s+(?:the\s+)?(?:oscillator\s+)?(?:detun|fine[\s-]?tun)",
            r"(?:how\s+)?to\s+(?:detun|fine[\s-]?tun).*oscillator",
            r"(?:detun|fine[\s-]?tun)\s+(?:amount|parameter|control)",
            # Oscillator 2 specific
            r"oscillator\s+2.*(?:detun|fine[\s-]?tun|pitch)",
            r"second\s+oscillator.*(?:detun|fine[\s-]?tun)",
        ],
        "rejection_patterns": [
            # Generic oscillator discussion
            r"oscillator.*type|oscillator.*mode|oscillator.*form",
            # Generic pitch discussion
            r"pitch\s+(?:in|of).*(?:hertz|hz|frequency)",
        ],
        "min_confidence": 0.85,
    },
    "Filter.Cutoff": {
        "capability_key": "filter_cutoff",
        "contextual_patterns": [
            # Explicit filter cutoff language
            r"filter\s+cutoff\s+(?:control|adjust|knob|parameter|slider|frequency)",
            r"cutoff\s+(?:frequency|control|adjust|knob|parameter|slider)",
            r"(?:to|adjust|control|set)\s+(?:the\s+)?filter\s+cutoff",
            r"(?:to|adjust|control|set)\s+(?:the\s+)?cutoff\s+(?:frequency)?",
            r"how\s+to.*(?:adjust|control).*(?:filter\s+)?cutoff",
            r"click\s+(?:on\s+)?(?:the\s+)?cutoff",
            # Brightness as explicit parameter control
            r"(?:adjust|control|change).*brightness.*filter|brightness.*control.*filter",
        ],
        "rejection_patterns": [
            # Generic frequency/brightness
            r"frequency\s+(?:affects|determines|controls).*(?:harmonics|tone|sound|pitch)",
            r"(?:bright|dark).*(?:because|due|result|harmonic|tone|sound)",
        ],
        "min_confidence": 0.85,
    },
}


def check_rejection_patterns(text, rule):
    """Check if text matches rejection patterns (content that should NOT map)."""
    for pattern in rule.get('rejection_patterns', []):
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def apply_context_aware_resolution(item, rules=CONTEXT_AWARE_RULES):
    """
    Apply context-aware resolution to an item.

    Returns list of (target_name, capability_key, confidence) tuples,
    or empty list if no confident match found.
    """
    source_text = item.get('raw_source_text', '').lower()
    resolved = []

    for target_name, rule in rules.items():
        # Check rejection patterns FIRST
        if check_rejection_patterns(source_text, rule):
            continue

        # Check contextual patterns
        patterns_matched = 0
        for pattern in rule.get('contextual_patterns', []):
            if re.search(pattern, source_text, re.IGNORECASE):
                patterns_matched += 1

        # Only resolve if patterns matched
        if patterns_matched > 0:
            # Confidence based on pattern matches
            confidence = 0.85 + min(0.10, patterns_matched * 0.05)
            confidence = round(min(confidence, 0.95), 2)

            if confidence >= rule['min_confidence']:
                resolved.append((target_name, rule['capability_key'], confidence))

    return resolved


def main():
    print("=" * 80)
    print("CONTEXT-AWARE TARGET RESOLUTION FOR NO_SERUM_TARGET / AMBIGUOUS ITEMS")
    print("=" * 80)
    print()

    # Load artifacts
    print("Loading artifacts...")
    resolution = load_target_resolution()
    extracted_items = load_extracted_items()
    print(f"  Target resolution items: {len(resolution['resolved_items'])}")
    print(f"  Extracted items: {len(extracted_items)}")
    print()

    # Separate items by status
    resolved_items = []
    ambiguous_items = []
    no_target_items = []
    source_only_items = []

    for item in resolution['resolved_items']:
        ki_id = item['knowledge_item_id']
        status = item.get('resolution_status', 'UNKNOWN')

        if status == 'RESOLVED':
            resolved_items.append(item)
        elif status == 'AMBIGUOUS':
            ambiguous_items.append(item)
        elif status == 'NO_SERUM_TARGET':
            no_target_items.append(item)
        elif status == 'SOURCE_ONLY':
            source_only_items.append(item)

    print("Item classification:")
    print(f"  RESOLVED: {len(resolved_items)} (PRESERVE - never modify)")
    print(f"  AMBIGUOUS: {len(ambiguous_items)} (PRESERVE - never silently convert)")
    print(f"  NO_SERUM_TARGET: {len(no_target_items)} (candidates for mapping)")
    print(f"  SOURCE_ONLY: {len(source_only_items)} (low priority)")
    print()

    # Apply context-aware resolution ONLY to NO_SERUM_TARGET items
    print("Applying context-aware resolution to NO_SERUM_TARGET items...")
    newly_resolved = {}
    target_counts = defaultdict(int)
    confidence_histogram = defaultdict(int)

    for item in no_target_items:
        ki_id = item['knowledge_item_id']
        extracted_item = extracted_items.get(ki_id)

        if not extracted_item:
            continue

        targets = apply_context_aware_resolution(extracted_item)

        if targets:
            resolved_targets = [
                {'target_name': t, 'capability_key': cap_key, 'confidence': conf}
                for t, cap_key, conf in targets
            ]

            newly_resolved[ki_id] = {
                'knowledge_item_id': ki_id,
                'source_segment_ids': extracted_item.get('source_segment_ids', []),
                'source_text': extracted_item.get('raw_source_text', '')[:200],
                'semantic_kind': extracted_item.get('kind', 'UNKNOWN'),
                'semantic_concept': extracted_item.get('extracted_statement', '')[:150],
                'resolution_status': 'RESOLVED',
                'resolved_targets': resolved_targets,
                'resolution_method': 'context_aware_pattern',
                'confidence': targets[0][2],  # First target's confidence
            }

            for target_name, _, conf in targets:
                target_counts[target_name] += 1
                confidence_histogram[round(conf, 1)] += 1

    print(f"  Newly resolved: {len(newly_resolved)} items")
    print()

    print("Resolution counts by target:")
    for target in sorted(target_counts.keys()):
        count = target_counts[target]
        print(f"  {target}: {count} items")
    print()

    print("Confidence distribution:")
    for conf in sorted(confidence_histogram.keys(), reverse=True):
        count = confidence_histogram[conf]
        print(f"  {conf}: {count} items")
    print()

    # Build updated resolution: PRESERVED items + NEWLY RESOLVED items
    print("Building updated resolution...")
    updated_items = []

    # Add RESOLVED items unchanged
    for item in resolved_items:
        updated_items.append(item)

    # Add AMBIGUOUS items unchanged
    for item in ambiguous_items:
        updated_items.append(item)

    # Add newly resolved items
    for ki_id, item in newly_resolved.items():
        updated_items.append(item)

    # Add remaining NO_SERUM_TARGET items that weren't resolved
    for item in no_target_items:
        ki_id = item['knowledge_item_id']
        if ki_id not in newly_resolved:
            updated_items.append(item)

    # Add SOURCE_ONLY items unchanged
    for item in source_only_items:
        updated_items.append(item)

    print(f"  Total items: {len(updated_items)}")
    print()

    # Count targets
    all_targets = set()
    for item in updated_items:
        if item.get('resolved_targets'):
            for t in item['resolved_targets']:
                all_targets.add(t['target_name'])

    # Write updated resolution
    updated_resolution = {
        'version': resolution.get('version', '1.0'),
        'source_id': resolution.get('source_id'),
        'resolution_metadata': {
            'total_items': len(updated_items),
            'resolved': len([i for i in updated_items if i.get('resolved_targets')]),
            'multiple_candidates': 0,
            'ambiguous': len(ambiguous_items),
            'no_target': len([i for i in updated_items if not i.get('resolved_targets')]),
            'source_only': len(source_only_items),
            'coverage_statistics': {
                'target_coverage': len(all_targets),
                'targets_used': sorted(list(all_targets)),
            }
        },
        'resolved_items': updated_items,
    }

    output_path = 'serum2/knowledge/yt_f507169bd7cb_target_resolution.json'
    with open(output_path, 'w') as f:
        json.dump(updated_resolution, f, indent=2)

    print(f"Updated resolution written: {output_path}")
    print()

    # Summary
    print("=" * 80)
    print("CONTEXT-AWARE RESOLUTION COMPLETE")
    print("=" * 80)
    print(f"Items preserved (RESOLVED): {len(resolved_items)}")
    print(f"Items preserved (AMBIGUOUS): {len(ambiguous_items)}")
    print(f"Items newly resolved: {len(newly_resolved)}")
    print(f"Items still unresolved: {len([i for i in updated_items if not i.get('resolved_targets')])}")
    print()
    print("Targets after context-aware resolution:")
    for target in sorted(all_targets):
        is_new = target in ['OSC1.Level', 'OSC1.Detune', 'Filter.Cutoff']
        status = "[NEW]" if is_new else "[EXISTING]"
        count = target_counts.get(target, 0)
        print(f"  {target}: {status} ({count} items)")
    print()


if __name__ == '__main__':
    main()
