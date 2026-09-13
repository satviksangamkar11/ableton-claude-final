"""Step 5.4 — Proposition Extraction from real 5.3 transcript.

Extract knowledge-bearing propositions from the real acquired transcript.
Preserve provenance, ambiguity, and epistemic clarity.

Input: yt_74ab96e1f377_source_ingestion_5_3.json (390 segments)
Output: step_5_4_extraction artifact
"""

import json
import re
from typing import List, Dict, Optional
from collections import defaultdict
from pathlib import Path

print("=" * 70)
print("STEP 5.4 — PROPOSITION EXTRACTION")
print("=" * 70)
print()

# =========================================================================
# STEP 1: Load 5.3 source artifact
# =========================================================================

print("-" * 70)
print("STEP 1: LOAD 5.3 SOURCE ARTIFACT")
print("-" * 70)
print()

artifact_path = Path("serum2/knowledge/yt_74ab96e1f377_source_ingestion_5_3.json")

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
print("  Title: {}".format(source_record['title']))
print("  Time coverage: {:.1f}s - {:.1f}s".format(
    segments[0]['start_time_sec'] if segments else 0,
    segments[-1]['end_time_sec'] if segments else 0
))
print()

# =========================================================================
# STEP 2: Define extraction patterns and rules
# =========================================================================

print("-" * 70)
print("STEP 2: DEFINE EXTRACTION PATTERNS")
print("-" * 70)
print()

EXTRACTION_PATTERNS = {
    'PROCEDURE': [
        r"(?:to |how to |steps? to |need to |try to )([\w\s]+)",
        r"(?:click|drag|select|open|load|save|press|hold|turn)",
        r"(?:go to|navigate to|access)",
    ],
    'CONCEPT': [
        r"(?:this is|that is|it's|the .* is)",
        r"(?:oscillator|filter|envelope|LFO|modulation|routing|synthesis|parameter|control|setting)",
        r"(?:Serum|waveform|frequency|resonance|decay|attack|release|sustain)",
    ],
    'PRINCIPLE': [
        r"(?:when you|if you|whenever you)",
        r"(?:this .* affects?|controls?|determines?)",
        r"(?:the .* .* the|affects?|influences?)",
    ],
    'OBSERVATION': [
        r"(?:I notice|I see|I found|I discovered|you can hear|you'll notice)",
        r"(?:as you|when you|if you .* you)",
    ],
    'RECOMMENDATION': [
        r"(?:I recommend|I suggest|try|use|consider|experiment with|play with)",
        r"(?:should|might want to|good idea|better)",
        r"(?:for .* use|for .* try)",
    ],
    'CONDITION': [
        r"(?:depends on|based on|when|if|in .* case)",
        r"(?:unless|except|but)",
    ],
    'LIMITATION': [
        r"(?:don't|avoid|never|be careful|warning|caution|limited|can't|won't)",
        r"(?:might cause|could cause|can cause|results in)",
    ],
    'CONTEXT': [
        r"(?:genre|style|type of music|for .* music|bass|lead|pad|synth)",
        r"(?:ambient|house|techno|trap|hip-hop|EDM)",
    ],
    'EXAMPLE': [
        r"(?:for example|like|such as|instance|let's say|imagine|suppose)",
        r"(?:here's|here is|try this)",
    ],
}

FILLER_PATTERNS = [
    r"^(?:hi|hello|hey|what's up|welcome|thanks|thank you)",
    r"(?:subscribe|like|comment|channel|video|link|description|comment section)",
    r"(?:check out|click the link|social media|Twitter|Instagram|Discord)",
    r"(?:support|patreon|become a member|donate|buy)",
    r"(?:bye|see you|until next|take care|see you later)",
    r"(?:\[.*\]|music|sound effect)",  # Bracketed annotations and music notation
    r"^(?:the|and|or|but|you|me|we|i)\s*$",  # Extremely common filler
]

print("Extraction patterns defined for:")
for kind in sorted(EXTRACTION_PATTERNS.keys()):
    print("  - {}".format(kind))
print()
print("Filler patterns: {} patterns".format(len(FILLER_PATTERNS)))
print()

# =========================================================================
# STEP 3: Group segments into semantic units
# =========================================================================

print("-" * 70)
print("STEP 3: GROUP SEGMENTS INTO SEMANTIC UNITS")
print("-" * 70)
print()

def should_start_new_unit(prev_seg, curr_seg):
    """Determine if current segment starts a new semantic unit."""
    # Large time gap = new topic
    time_gap = curr_seg['start_time_sec'] - prev_seg['end_time_sec']
    if time_gap > 2.0:
        return True

    text = curr_seg['text'].lower()

    # Topic starters
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
# STEP 4: Extract propositions
# =========================================================================

print("-" * 70)
print("STEP 4: EXTRACT PROPOSITIONS")
print("-" * 70)
print()

extracted_propositions = []
filler_count = 0
item_counter = 0

for unit_idx, unit in enumerate(semantic_units):
    if unit_idx % 100 == 0:
        print("  Processing unit {}/{}...".format(unit_idx, len(semantic_units)))

    combined_text = " ".join([seg['text'] for seg in unit])

    # Skip very short units (likely filler)
    if len(combined_text) < 10:
        filler_count += 1
        continue

    # Check if unit is filler
    is_filler = False
    for filler_pattern in FILLER_PATTERNS:
        if re.search(filler_pattern, combined_text, re.IGNORECASE):
            # Check if it's a short, obvious filler
            if len(combined_text) < 30 or combined_text.count(' ') < 5:
                is_filler = True
                break

    if is_filler:
        filler_count += 1
        continue

    # Classify based on patterns
    kind = "OBSERVATION"  # Default to observation if patterns unclear
    confidence = 0.7
    matches = {}

    for test_kind, patterns in EXTRACTION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                matches[test_kind] = True

    # Priority classification (prefer more specific types)
    priority = ["PROCEDURE", "RECOMMENDATION", "LIMITATION", "PRINCIPLE",
                "CONCEPT", "CONDITION", "CONTEXT", "EXAMPLE", "OBSERVATION"]
    for kind_candidate in priority:
        if kind_candidate in matches:
            kind = kind_candidate
            break

    # Infer epistemic status from language
    epistemic_status = "SOURCE_REPORTED"
    if re.search(r"(?:I recommend|I suggest|you should|try)", combined_text, re.IGNORECASE):
        epistemic_status = "SOURCE_RECOMMENDED"
    elif re.search(r"(?:I notice|I see|I found|as you can see)", combined_text, re.IGNORECASE):
        epistemic_status = "SOURCE_OBSERVED"

    # Create proposition record
    proposition = {
        "proposition_id": "prop_{:06d}".format(item_counter),
        "source_id": source_record['source_id'],
        "source_segment_ids": [seg['segment_id'] for seg in unit],
        "segment_count": len(unit),
        "start_time_sec": unit[0]['start_time_sec'],
        "end_time_sec": unit[-1]['end_time_sec'],
        "original_text": combined_text,
        "kind": kind,
        "epistemic_status": epistemic_status,
        "extraction_confidence": confidence,
        "semantic_patterns_matched": list(matches.keys()),
        "ambiguity": None,  # Will be set if we detect ambiguity
    }

    # Detect common ambiguities
    if re.search(r"\b(?:it|this|that|the .+)\b", combined_text):
        # Reference without clear antecedent
        if len(combined_text) < 50:
            proposition["ambiguity"] = "Unclear referent; missing context"

    if re.search(r"make it (?:longer|shorter|bigger|smaller|louder|quieter)", combined_text, re.IGNORECASE):
        if not re.search(r"release|decay|attack|sustain|volume|level", combined_text, re.IGNORECASE):
            proposition["ambiguity"] = "Parameter unclear (could be release, decay, duration, etc.)"

    extracted_propositions.append(proposition)
    item_counter += 1

print("[OK] Extracted {} propositions".format(len(extracted_propositions)))
print("[OK] Filtered {} filler units".format(filler_count))
print()

# =========================================================================
# STEP 5: Analysis and statistics
# =========================================================================

print("-" * 70)
print("STEP 5: STATISTICS")
print("-" * 70)
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
# STEP 6: Persist extraction artifact
# =========================================================================

print("-" * 70)
print("STEP 6: PERSIST EXTRACTION ARTIFACT")
print("-" * 70)
print()

extraction_artifact = {
    "version": "1.0",
    "phase": "5.4",
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

output_path = Path("serum2/knowledge/yt_74ab96e1f377_proposition_extraction_5_4.json")

print("Writing extraction artifact to: {}".format(output_path))

try:
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extraction_artifact, f, indent=2, ensure_ascii=False)

    print("[OK] Artifact written successfully")
    print("  File: {}".format(output_path))
    print("  Size: {} bytes".format(len(json.dumps(extraction_artifact))))

except Exception as e:
    print("[FAIL] Could not write artifact: {}".format(e))

print()

# =========================================================================
# STEP 7: Sample inspection
# =========================================================================

print("-" * 70)
print("STEP 7: SAMPLE PROPOSITION INSPECTION")
print("-" * 70)
print()

if len(extracted_propositions) > 0:
    print("Representative Propositions (first 5):")
    print()
    for i, prop in enumerate(extracted_propositions[:5]):
        print("Proposition {}: {}".format(i+1, prop["proposition_id"]))
        print("  Type: {}".format(prop["kind"]))
        print("  Epistemic: {}".format(prop["epistemic_status"]))
        print("  Confidence: {:.1f}".format(prop["extraction_confidence"]))
        print("  Segments: {}".format(len(prop["source_segment_ids"])))
        print("  Text: {}...".format(prop["original_text"][:100]))
        if prop["ambiguity"]:
            print("  Ambiguity: {}".format(prop["ambiguity"]))
        print()

# =========================================================================
# FINAL REPORT
# =========================================================================

print("=" * 70)
print("STEP 5.4 EXTRACTION REPORT")
print("=" * 70)
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

print("CLASSIFICATION:")
for kind in sorted(kind_counts.keys()):
    print("  {}: {}".format(kind, kind_counts[kind]))
print()

print("EPISTEMIC STATUS:")
for status in sorted(epistemic_counts.keys()):
    print("  {}: {}".format(status, epistemic_counts[status]))
print()

print("AMBIGUITY:")
print("  Ambiguous: {}".format(ambiguous_count))
print("  Unambiguous: {}".format(len(extracted_propositions) - ambiguous_count))
print()

print("OUTPUT ARTIFACT:")
print("  File: {}".format(output_path))
print("  Status: {}".format("OK" if output_path.exists() else "MISSING"))
print()

print("=" * 70)
if len(extracted_propositions) > 0 and output_path.exists():
    print("STEP 5.4 VERDICT: PASS")
else:
    print("STEP 5.4 VERDICT: FAIL")
print("=" * 70)
