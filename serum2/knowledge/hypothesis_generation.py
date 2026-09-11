#!/usr/bin/env python3
"""Generate hypotheses from fixed target resolution.

Creates hypotheses from resolved KnowledgeItems for OSC1.Level, OSC1.Detune,
and Filter.Cutoff using the updated target_resolution.json.
"""

import json
from collections import defaultdict


def load_target_resolution():
    """Load the updated target resolution."""
    path = "serum2/knowledge/yt_f507169bd7cb_target_resolution.json"
    with open(path) as f:
        return json.load(f)


def load_current_hypotheses():
    """Load existing hypotheses to preserve them."""
    path = "serum2/knowledge/yt_f507169bd7cb_hypotheses.json"
    with open(path) as f:
        return json.load(f)


def generate_hypothesis_id(ki_id, target_index):
    """Generate a hypothesis ID from knowledge item ID."""
    # Extract the index from ki_id (e.g., ki_ext_000001 → 000001)
    ki_num = ki_id.split('_')[-1]
    # Use format: hyp_target_ki_index (e.g., hyp_osc1level_000001_01)
    return f"hyp_{ki_num}_{target_index:02d}"


def create_hypothesis(ki_id, knowledge_item, target_name, target_index):
    """Create a hypothesis from a knowledge item and target."""
    source_text = knowledge_item.get('source_text', '')[:100]

    return {
        "hypothesis_id": generate_hypothesis_id(ki_id, target_index),
        "knowledge_item_id": ki_id,
        "target": target_name,
        "semantic_concept": knowledge_item.get('semantic_concept', '')[:100],
        "source_description": source_text,
        "confidence": 0.85,
        "source_type": "YOUTUBE_TRANSCRIPT",
    }


def main():
    print("=" * 80)
    print("HYPOTHESIS GENERATION FROM FIXED TARGET RESOLUTION")
    print("=" * 80)
    print()

    # Load artifacts
    print("Loading artifacts...")
    resolution = load_target_resolution()
    hypotheses_data = load_current_hypotheses()
    print(f"  Loaded {len(resolution['resolved_items'])} resolved items")
    print(f"  Existing hypotheses: {len(hypotheses_data.get('hypotheses', []))}")
    print()

    # Preserve existing hypotheses by ID
    existing_by_id = {h['hypothesis_id']: h for h in hypotheses_data.get('hypotheses', [])}
    print(f"  Preserved IDs: {len(existing_by_id)}")
    print()

    # Generate new hypotheses from resolved items
    print("Generating new hypotheses...")
    new_hypotheses_by_target = defaultdict(list)
    generated_count = 0

    for item in resolution['resolved_items']:
        ki_id = item['knowledge_item_id']

        if not item.get('resolved_targets'):
            continue

        for target_index, target_info in enumerate(item['resolved_targets']):
            target_name = target_info['target_name']

            # Check if this is one of the newly resolved targets
            if target_name in ['OSC1.Level', 'OSC1.Detune', 'Filter.Cutoff']:
                hyp = create_hypothesis(ki_id, item, target_name, target_index)

                # Only add if not already existing (avoid duplicates)
                if hyp['hypothesis_id'] not in existing_by_id:
                    new_hypotheses_by_target[target_name].append(hyp)
                    generated_count += 1

    print(f"  Generated {generated_count} new hypotheses:")
    for target in sorted(new_hypotheses_by_target.keys()):
        count = len(new_hypotheses_by_target[target])
        print(f"    {target}: {count}")
    print()

    # Combine all hypotheses: existing + newly generated
    print("Combining with existing hypotheses...")
    all_hypotheses = list(existing_by_id.values())

    for target in new_hypotheses_by_target:
        all_hypotheses.extend(new_hypotheses_by_target[target])

    print(f"  Total hypotheses after merge: {len(all_hypotheses)}")
    print()

    # Count by target
    target_counts = defaultdict(int)
    for hyp in all_hypotheses:
        target = hyp.get('target')
        target_counts[target] += 1

    print("Hypothesis counts by target:")
    for target in sorted(target_counts.keys()):
        count = target_counts[target]
        is_new = "[NEW]" if target in new_hypotheses_by_target else "[EXISTING]"
        print(f"  {target}: {count} {is_new}")
    print()

    # Write updated hypotheses
    updated_hypotheses = {
        "version": hypotheses_data.get('version', '1.0'),
        "source_id": hypotheses_data.get('source_id'),
        "metadata": {
            "total_hypotheses": len(all_hypotheses),
            "sources": {
                "youtube_transcript": len([h for h in all_hypotheses if h.get('source_type') == 'YOUTUBE_TRANSCRIPT'])
            },
            "targets_covered": sorted(list(set(h.get('target') for h in all_hypotheses if h.get('target')))),
        },
        "hypotheses": all_hypotheses,
    }

    output_path = "serum2/knowledge/yt_f507169bd7cb_hypotheses.json"
    with open(output_path, 'w') as f:
        json.dump(updated_hypotheses, f, indent=2)

    print(f"Updated hypotheses written to: {output_path}")
    print()

    # Summary
    print("=" * 80)
    print("HYPOTHESIS GENERATION COMPLETE")
    print("=" * 80)
    print(f"Total hypotheses: {len(all_hypotheses)}")
    print(f"Newly generated: {generated_count}")
    print(f"Preserved from existing: {len(existing_by_id)}")
    print()
    print("New target coverage:")
    for target in ['OSC1.Level', 'OSC1.Detune', 'Filter.Cutoff']:
        count = target_counts.get(target, 0)
        print(f"  {target}: {count} hypotheses")
    print()


if __name__ == '__main__':
    main()
