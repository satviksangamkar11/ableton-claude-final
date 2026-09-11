#!/usr/bin/env python3
"""Target Resolution Repair: Semantic KnowledgeItems → Semantic Targets

Fix the semantic target resolution pipeline to properly map extracted
KnowledgeItems to semantic targets: OSC1.Level, OSC1.Detune, Filter.Cutoff

This script implements the target resolution rules that should have
been applied during semantic extraction.
"""

import json
import re
from collections import defaultdict
from pathlib import Path


def load_extracted_items():
    """Load extracted KnowledgeItems from semantic_extraction.json"""
    path = "serum2/knowledge/yt_f507169bd7cb_semantic_extraction.json"
    with open(path) as f:
        data = json.load(f)
    return data.get('extracted_knowledge_items', [])


def load_current_resolution():
    """Load current target_resolution.json to preserve existing mappings"""
    path = "serum2/knowledge/yt_f507169bd7cb_target_resolution.json"
    with open(path) as f:
        return json.load(f)


# =========================================================================
# TARGET RESOLUTION RULES
# =========================================================================

TARGET_RESOLUTION_RULES = {
    "OSC1.Level": {
        "capability_key": "oscillator_level",
        "keywords": [
            "oscillator level", "osc level", "osc1 level",
            "oscillator volume", "osc volume",
            "amplitude", "loud", "quieter", "louder",
            "output level", "output volume",
            "gain", "boost",
            "level control", "volume control",
        ],
        "patterns": [
            r"oscillator\s+(?:level|volume|amplitude)",
            r"osc\s+(?:level|volume|amplitude)",
            r"(?:make|increase|decrease|adjust)\s+(?:volume|level|amplitude|loud)",
            r"(?:sound|output)\s+(?:quieter|louder|louder|level)",
        ],
        "min_confidence": 0.7,
    },
    "OSC1.Detune": {
        "capability_key": "oscillator_detune",
        "keywords": [
            "detune", "detuning", "detuned",
            "fine tune", "fine tuning", "fine-tune",
            "pitch offset", "offset",
            "oscillator two", "osc two", "osc 2",
            "oscillator b", "osc b",
            "second oscillator",
            "slightly", "pitch adjustment",
        ],
        "patterns": [
            r"detun(?:e|ing)",
            r"fine\s+tun(?:e|ing)",
            r"pitch\s+offset",
            r"oscillator\s+two\s+(?:pitch|frequency|detune)",
        ],
        "min_confidence": 0.7,
    },
    "Filter.Cutoff": {
        "capability_key": "filter_cutoff",
        "keywords": [
            "filter cutoff", "cutoff frequency", "cutoff",
            "filter frequency", "filter freq",
            "filter brightness", "brightness",
            "brighter", "darker",
            "high pass", "low pass",
            "cutoff knob", "frequency knob",
            "filter sweep",
        ],
        "patterns": [
            r"(?:filter|cutoff)\s+(?:frequency|freq|cutoff)",
            r"cutoff(?:\s+frequency)?",
            r"(?:bright|dark)er",
            r"filter\s+(?:brightness|color|shape)",
        ],
        "min_confidence": 0.7,
    },
}


def resolve_item_to_targets(item, rules=TARGET_RESOLUTION_RULES):
    """
    Resolve a single KnowledgeItem to zero or more semantic targets.

    Returns list of (target_name, capability_key, confidence, method) tuples.
    One item can resolve to multiple targets (e.g., both OSC1.Level and OSC1.Detune).
    """
    resolved = []
    source_text = item.get('raw_source_text', '').lower()

    for target_name, rule in rules.items():
        confidence = 0.0
        method = None

        # Try keyword matching first
        keywords_found = [kw for kw in rule['keywords'] if kw.lower() in source_text]
        if keywords_found:
            confidence = 0.7 + min(0.2, len(keywords_found) * 0.05)
            method = 'keyword_match'

        # Try pattern matching if no keywords matched
        if not keywords_found:
            for pattern in rule['patterns']:
                if re.search(pattern, source_text, re.IGNORECASE):
                    confidence = 0.8
                    method = 'pattern_match'
                    break

        # Add if confident enough
        if confidence >= rule['min_confidence']:
            resolved.append((
                target_name,
                rule['capability_key'],
                round(confidence, 2),
                method
            ))

    return resolved


def main():
    print("=" * 80)
    print("TARGET RESOLUTION REPAIR")
    print("=" * 80)
    print()

    # Load artifacts
    print("Loading artifacts...")
    items = load_extracted_items()
    current_resolution = load_current_resolution()
    print(f"  Extracted items: {len(items)}")
    print(f"  Currently resolved: {current_resolution['resolution_metadata']['resolved']}")
    print()

    # Build new resolution mapping: ki_id → list of targets
    print("Applying target resolution rules...")
    new_resolved_by_ki = {}  # ki_id → [(target_name, cap_key, confidence, method)]
    target_counts = defaultdict(int)

    for item in items:
        ki_id = item['knowledge_item_id']
        targets = resolve_item_to_targets(item)

        if targets:
            new_resolved_by_ki[ki_id] = targets
            for target_name, _, _, _ in targets:
                target_counts[target_name] += 1

    print(f"  Newly resolved: {len(new_resolved_by_ki)} items")
    print()

    print("Target resolution counts (new):")
    for target in sorted(TARGET_RESOLUTION_RULES.keys()):
        count = target_counts.get(target, 0)
        print(f"  {target}: {count} items")
    print()

    # Build merged resolution
    print("Merging with existing resolution...")
    all_resolved = {}

    # Start with existing items
    for item in current_resolution.get('resolved_items', []):
        ki_id = item['knowledge_item_id']
        all_resolved[ki_id] = item

    # Override with newly resolved items (complete replacement, not merge)
    for ki_id, targets in new_resolved_by_ki.items():
        # Create entry with ALL resolved targets
        resolved_targets_list = [
            {
                "target_name": target_name,
                "capability_key": cap_key,
                "confidence": confidence,
            }
            for target_name, cap_key, confidence, _ in targets
        ]

        # Find the item in the extracted items
        item = next((i for i in items if i['knowledge_item_id'] == ki_id), None)
        if not item:
            continue

        all_resolved[ki_id] = {
            "knowledge_item_id": ki_id,
            "source_segment_ids": item.get('source_segment_ids', []),
            "source_text": item.get('raw_source_text', '')[:200],
            "semantic_kind": item.get('kind', 'UNKNOWN'),
            "semantic_concept": item.get('extracted_statement', '')[:150],
            "resolution_status": "RESOLVED",
            "resolved_targets": resolved_targets_list,
            "resolution_method": targets[0][3] if targets else "unknown",  # Use first target's method
            "confidence": targets[0][2] if targets else 0.0,  # Use first target's confidence
        }

    print(f"  Total items after merge: {len(all_resolved)}")
    print()

    # Compute target coverage
    all_targets_used = set()
    for entry in all_resolved.values():
        if entry.get('resolved_targets'):
            for target in entry['resolved_targets']:
                all_targets_used.add(target['target_name'])

    # Update resolution metadata
    updated_resolution = {
        "version": current_resolution.get('version', '1.0'),
        "source_id": current_resolution.get('source_id'),
        "resolution_metadata": {
            "total_items": len(items),
            "resolved": len(all_resolved),
            "multiple_candidates": 0,
            "ambiguous": 0,
            "no_target": len(items) - len(all_resolved),
            "source_only": 0,
            "coverage_statistics": {
                "target_coverage": len(all_targets_used),
                "targets_used": sorted(list(all_targets_used)),
            }
        },
        "resolved_items": list(all_resolved.values()),
    }

    # Write updated resolution
    output_path = "serum2/knowledge/yt_f507169bd7cb_target_resolution.json"
    with open(output_path, 'w') as f:
        json.dump(updated_resolution, f, indent=2)

    print(f"Updated resolution written to: {output_path}")
    print()

    # Summary
    print("=" * 80)
    print("REPAIR COMPLETE")
    print("=" * 80)
    print(f"Total items: {len(items)}")
    print(f"Newly resolved items: {len(new_resolved_by_ki)}")
    print(f"Total resolved after merge: {len(all_resolved)}")
    print()
    print("Target coverage after repair:")
    for target in sorted(all_targets_used):
        count = target_counts.get(target, 0)
        status = "[NEW]" if count > 0 else "[EXISTING]"
        print(f"  {target}: {status}")
    print()


if __name__ == '__main__':
    main()
