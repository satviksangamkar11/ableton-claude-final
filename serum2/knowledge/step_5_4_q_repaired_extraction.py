"""
STEP 5.4-Q REPAIRED EXTRACTION

Re-run extraction on the ORIGINAL 5.3 source using the repaired semantic classifier.
This is the critical proof that the classifier itself produces correct results,
not that manual auditing can fix bad output.

Input: yt_74ab96e1f377_source_ingestion_5_3.json (390 segments, unchanged)
Output: step_5_4_q_repaired_extraction artifact
"""

import json
import re
from typing import List, Dict, Optional
from collections import defaultdict
from pathlib import Path
from step_5_4_q_semantic_contract import classify_semantic

print("=" * 80)
print("STEP 5.4-Q REPAIRED EXTRACTION")
print("=" * 80)
print()

# =========================================================================
# STEP 1: Load 5.3 source artifact (UNCHANGED)
# =========================================================================

print("-" * 80)
print("STEP 1: LOAD 5.3 SOURCE ARTIFACT")
print("-" * 80)
print()

artifact_path = Path("yt_74ab96e1f377_source_ingestion_5_3.json")

if not artifact_path.exists():
    print("[FAIL] Source artifact not found: {}".format(artifact_path))
    exit(1)

print("Loading: {}".format(artifact_path))

with open(artifact_path, 'r', encoding='utf-8') as f:
    source_artifact = json.load(f)

segments = source_artifact['transcript_segments']
source_record = source_artifact['source']

print("[OK] Loaded {} segments from source: {}".format(
    len(segments), source_record['source_id']))
print()

# =========================================================================
# STEP 2: Group segments into semantic units (SAME as original)
# =========================================================================

print("-" * 80)
print("STEP 2: GROUP SEGMENTS INTO SEMANTIC UNITS")
print("-" * 80)
print()

def should_start_new_unit(prev_seg, curr_seg):
    """Determine if current segment starts a new semantic unit."""
    time_gap = curr_seg['start_time_sec'] - prev_seg['end_time_sec']
    if time_gap > 2.0:
        return True

    text = curr_seg['text'].lower()

    if any(text.startswith(phrase) for phrase in [
        "hello", "hi", "welcome", "so", "now", "next", "finally",
        "in this", "let's", "we're", "i'm"
    ]):
        return True

    return False

semantic_units = []
current_unit = [segments[0]]

for i in range(1, len(segments)):
    prev_seg = segments[i-1]
    curr_seg = segments[i]

    if should_start_new_unit(prev_seg, curr_seg):
        semantic_units.append(current_unit)
        current_unit = [curr_seg]
    else:
        current_unit.append(curr_seg)

semantic_units.append(current_unit)

print("[OK] Grouped {} segments into {} semantic units".format(
    len(segments), len(semantic_units)))
print()

# =========================================================================
# STEP 3: Extract propositions using REPAIRED SEMANTIC CLASSIFIER
# =========================================================================

print("-" * 80)
print("STEP 3: EXTRACT PROPOSITIONS WITH REPAIRED CLASSIFIER")
print("-" * 80)
print()

extracted_propositions = []
filler_count = 0
item_counter = 0

for unit_idx, unit in enumerate(semantic_units):
    if unit_idx % 100 == 0:
        print("  Processing unit {}/{}...".format(unit_idx, len(semantic_units)))

    combined_text = " ".join([seg['text'] for seg in unit])

    # Skip very short units
    if len(combined_text) < 10:
        filler_count += 1
        continue

    # REPAIRED: Use semantic classifier, not keyword patterns
    segment_ids = [seg['segment_id'] for seg in unit]
    result = classify_semantic(combined_text, segment_ids)

    kind = result["classification"]
    confidence = result.get("confidence", 0.7)
    ambiguity = result.get("ambiguity")
    rationale = result.get("rationale", "")
    candidate_classes = result.get("candidate_classes")

    # Infer epistemic status from language (same as original)
    epistemic_status = "SOURCE_REPORTED"
    if re.search(r"(?:I recommend|I suggest|you should|try)", combined_text, re.IGNORECASE):
        epistemic_status = "SOURCE_RECOMMENDED"
    elif re.search(r"(?:I notice|I see|I found|as you can see)", combined_text, re.IGNORECASE):
        epistemic_status = "SOURCE_OBSERVED"

    # If classifier says FILLER, skip this proposition
    if kind == "FILLER":
        filler_count += 1
        continue

    # Create proposition record
    proposition = {
        "proposition_id": "prop_{:06d}".format(item_counter),
        "source_id": source_record['source_id'],
        "source_segment_ids": segment_ids,
        "segment_count": len(unit),
        "start_time_sec": unit[0]['start_time_sec'],
        "end_time_sec": unit[-1]['end_time_sec'],
        "original_text": combined_text,
        "kind": kind,
        "epistemic_status": epistemic_status,
        "extraction_confidence": confidence,
        "semantic_classifier_rationale": rationale,
        "ambiguity": ambiguity,
    }

    # For UNKNOWN items, preserve candidate classes to document ambiguity explicitly
    if kind == "UNKNOWN" and candidate_classes:
        proposition["candidate_classes"] = candidate_classes

    extracted_propositions.append(proposition)
    item_counter += 1

print("[OK] Extracted {} propositions".format(len(extracted_propositions)))
print("[OK] Filtered {} filler units".format(filler_count))
print()

# =========================================================================
# STEP 4: Analysis and statistics
# =========================================================================

print("-" * 80)
print("STEP 4: STATISTICS")
print("-" * 80)
print()

kind_counts = defaultdict(int)
epistemic_counts = defaultdict(int)
ambiguous_count = 0

for prop in extracted_propositions:
    kind_counts[prop["kind"]] += 1
    epistemic_counts[prop["epistemic_status"]] += 1
    if prop["ambiguity"]:
        ambiguous_count += 1

print("Classification Distribution:")
for kind in sorted(kind_counts.keys()):
    pct = 100.0 * kind_counts[kind] / len(extracted_propositions)
    print("  {}: {} ({:.1f}%)".format(kind, kind_counts[kind], pct))
print()

print("Epistemic Status Distribution:")
for status in sorted(epistemic_counts.keys()):
    pct = 100.0 * epistemic_counts[status] / len(extracted_propositions)
    print("  {}: {} ({:.1f}%)".format(status, epistemic_counts[status], pct))
print()

print("Ambiguity:")
print("  Ambiguous propositions: {}".format(ambiguous_count))
print("  Unambiguous propositions: {}".format(len(extracted_propositions) - ambiguous_count))
print()

print("Overall:")
print("  Total segments: {}".format(len(segments)))
print("  Semantic units: {}".format(len(semantic_units)))
print("  Retained propositions: {}".format(len(extracted_propositions)))
print("  Filtered filler: {}".format(filler_count))
print("  Retention rate: {:.1f}%".format(
    100.0 * len(extracted_propositions) / len(semantic_units)))
print()

# =========================================================================
# STEP 5: Persist extraction artifact
# =========================================================================

print("-" * 80)
print("STEP 5: PERSIST REPAIRED EXTRACTION ARTIFACT")
print("-" * 80)
print()

extraction_artifact = {
    "version": "2.0",
    "phase": "5.4-Q",
    "repair_status": "REPAIRED_WITH_SEMANTIC_CLASSIFIER",
    "source_id": source_record['source_id'],
    "source_title": source_record['title'],
    "extraction_metadata": {
        "total_segments": len(segments),
        "semantic_units": len(semantic_units),
        "retained_propositions": len(extracted_propositions),
        "filler_filtered": filler_count,
        "retention_rate": len(extracted_propositions) / len(semantic_units) if semantic_units else 0,
        "classification_distribution": dict(kind_counts),
        "epistemic_distribution": dict(epistemic_counts),
        "ambiguous_count": ambiguous_count,
    },
    "propositions": extracted_propositions,
}

output_path = Path("yt_74ab96e1f377_proposition_extraction_5_4_q_repaired.json")

print("Writing repaired extraction artifact to: {}".format(output_path))

try:
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extraction_artifact, f, indent=2, ensure_ascii=False)

    print("[OK] Artifact written successfully")
    print("  File: {}".format(output_path))

except Exception as e:
    print("[FAIL] Could not write artifact: {}".format(e))

print()

# =========================================================================
# FINAL REPORT
# =========================================================================

print("=" * 80)
print("STEP 5.4-Q REPAIRED EXTRACTION REPORT")
print("=" * 80)
print()

print("INPUT ARTIFACT:")
print("  Source: {}".format(source_record['source_id']))
print("  Title: {}".format(source_record['title']))
print("  Segments: {}".format(len(segments)))
print()

print("EXTRACTION RESULT:")
print("  Propositions extracted: {}".format(len(extracted_propositions)))
print("  Filler filtered: {}".format(filler_count))
print("  Retention rate: {:.1f}%".format(
    100.0 * len(extracted_propositions) / len(semantic_units)))
print()

print("CLASSIFICATION DISTRIBUTION:")
for kind in sorted(kind_counts.keys()):
    print("  {}: {}".format(kind, kind_counts[kind]))
print()

print("OUTPUT ARTIFACT:")
print("  File: {}".format(output_path))
print("  Status: {}".format("OK" if output_path.exists() else "MISSING"))
print()

print("=" * 80)
print("STEP 5.4-Q REPAIRED EXTRACTION COMPLETE")
print("=" * 80)
