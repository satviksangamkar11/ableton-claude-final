"""
STEP 5.5 — KNOWLEDGE NORMALIZATION IMPLEMENTATION

Transform 36 propositions from 5.4-Q repaired extraction into canonical KnowledgeItems.
Follows frozen STEP_5_5_PROPOSAL.md design (Revision 1 Final).

Input: yt_74ab96e1f377_proposition_extraction_5_4_q_repaired.json (36 propositions)
Output:
  - yt_74ab96e1f377_knowledge_normalized_5_5.json (36 KnowledgeItems)
  - yt_74ab96e1f377_normalization_ledger_5_5.json (36 ledger entries)
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import hashlib

print("=" * 80)
print("STEP 5.5 — KNOWLEDGE NORMALIZATION")
print("=" * 80)
print()

# =========================================================================
# STEP 1: LOAD INPUT ARTIFACT
# =========================================================================

print("-" * 80)
print("STEP 1: LOAD INPUT ARTIFACT (5.4-Q repaired extraction)")
print("-" * 80)
print()

input_path = Path("yt_74ab96e1f377_proposition_extraction_5_4_q_repaired.json")

if not input_path.exists():
    print("[FAIL] Input artifact not found: {}".format(input_path))
    exit(1)

with open(input_path, 'r', encoding='utf-8') as f:
    extraction_artifact = json.load(f)

propositions = extraction_artifact["propositions"]
source_record = {
    "source_id": extraction_artifact["source_id"],
    "source_title": extraction_artifact["source_title"],
}

print("[OK] Loaded {} propositions".format(len(propositions)))
print("[OK] Source: {} ({})".format(source_record["source_id"], source_record["source_title"]))
print()

# Verify cardinality
classified_count = sum(1 for p in propositions if p["kind"] != "UNKNOWN")
unknown_count = sum(1 for p in propositions if p["kind"] == "UNKNOWN")
print("Distribution check:")
print("  Classified: {}".format(classified_count))
print("  UNKNOWN: {}".format(unknown_count))
print("  Total: {}".format(len(propositions)))
print()

if len(propositions) != 36:
    print("[FAIL] Expected 36 propositions, got {}".format(len(propositions)))
    exit(1)

# =========================================================================
# STEP 2: DEFINE NORMALIZATION RULES & HELPERS
# =========================================================================

print("-" * 80)
print("STEP 2: DEFINE NORMALIZATION RULES")
print("-" * 80)
print()

def generate_knowledge_id(source_id: str, proposition_id: str) -> str:
    """Generate deterministic knowledge_item_id."""
    key = "{}:{}".format(source_id, proposition_id)
    hash_val = hashlib.md5(key.encode()).hexdigest()[:16]
    return "ki_{}".format(hash_val)

def get_best_guess_type(candidate_classes: List[str]) -> str:
    """
    Pick best-guess KnowledgeType for UNKNOWN items.
    Priority: OBSERVATION > PRINCIPLE > PROCEDURE (lowest risk first)
    """
    priority = ["OBSERVATION", "PRINCIPLE", "PROCEDURE"]
    for preferred in priority:
        if preferred in candidate_classes:
            return preferred
    # Fallback (should not happen if classifier works)
    return candidate_classes[0] if candidate_classes else "OBSERVATION"

def normalize_proposition_text(original_text: str, kind: str) -> Optional[str]:
    """
    Apply light normalization: remove transcript artifacts, collapse whitespace.
    Return None if no changes needed (keep original).
    """
    normalized = original_text.strip()

    # Remove [Music], [Pause], etc.
    while "[Music]" in normalized or "[Pause]" in normalized:
        normalized = normalized.replace("[Music]", "").replace("[Pause]", "")

    # Collapse multiple spaces
    while "  " in normalized:
        normalized = normalized.replace("  ", " ")

    normalized = normalized.strip()

    # Return None if unchanged
    if normalized == original_text.strip():
        return None

    return normalized

print("[OK] Normalization rules loaded")
print()

# =========================================================================
# STEP 3: NORMALIZE PROPOSITIONS TO KNOWLEDGEITEMS
# =========================================================================

print("-" * 80)
print("STEP 3: NORMALIZE PROPOSITIONS -> KNOWLEDGEITEMS")
print("-" * 80)
print()

knowledge_items = []
ledger_entries = []
transformation_stats = {
    "NORMALIZED": 0,
    "UNCHANGED": 0,
    "REJECTED": 0,
    "UNRESOLVED": 0,
}

for idx, prop in enumerate(propositions):
    if idx % 10 == 0:
        print("  Processing {} / {}...".format(idx, len(propositions)))

    prop_id = prop["proposition_id"]
    kind = prop["kind"]
    original_text = prop["original_text"]
    source_segment_ids = prop["source_segment_ids"]
    epistemic_status_source = prop["epistemic_status"]

    # Generate stable ID
    knowledge_id = generate_knowledge_id(source_record["source_id"], prop_id)

    # Determine KnowledgeType and epistemic_status
    if kind == "UNKNOWN":
        # For UNKNOWN: pick best-guess type, set epistemic_status to UNKNOWN
        knowledge_type = get_best_guess_type(prop.get("candidate_classes", ["OBSERVATION"]))
        epistemic_status = "UNKNOWN"
        extraction_confidence = 0.5  # LOW for UNKNOWN
        ambiguity = prop.get("ambiguity", "semantic function unclear")
        status = "UNRESOLVED"
        transformation_stats["UNRESOLVED"] += 1
    else:
        # For classified: use the classification
        knowledge_type = kind
        epistemic_status = epistemic_status_source
        extraction_confidence = prop.get("extraction_confidence", 0.85)
        ambiguity = None
        status = "NORMALIZED" if normalize_proposition_text(original_text, kind) else "UNCHANGED"
        transformation_stats[status] += 1

    # Light normalization
    normalized_text = normalize_proposition_text(original_text, knowledge_type)
    transformations = []
    if normalized_text:
        transformations.append("artifact_removal")
        transformations.append("whitespace_collapsing")

    # Create KnowledgeItem
    knowledge_item = {
        "knowledge_item_id": knowledge_id,
        "source_reference": {
            "source_id": source_record["source_id"],
            "source_type": "YOUTUBE_VIDEO",
            "source_title": source_record["source_title"],
            "segment_ids": source_segment_ids,
            "start_time_sec": prop.get("start_time_sec"),
            "end_time_sec": prop.get("end_time_sec"),
        },
        "original_proposition": original_text,
        "knowledge_type": knowledge_type,
        "epistemic_status": epistemic_status,
        "normalized_proposition": normalized_text,
        "semantic_bindings": [],  # To be populated in future phases
        "extraction_confidence": extraction_confidence,
        "ambiguity": ambiguity,
        "conditions": [],
        "limitations": [],
        "extraction_metadata": {
            "extraction_timestamp": datetime.now().isoformat() + "Z",
            "extraction_method": "semantic_classification_5_4_q",
            "extraction_confidence": extraction_confidence,
            "raw_extraction_status": "EXTRACTED",
        },
        "notes": None,
    }

    # For UNKNOWN items, preserve candidate information
    if kind == "UNKNOWN":
        knowledge_item["notes"] = "Candidates: {}. Classifier could not determine semantic function.".format(
            prop.get("candidate_classes", [])
        )

    # Create ledger entry
    ledger_entry = {
        "proposition_id": prop_id,
        "knowledge_id": knowledge_id,
        "classification_from_5_4": kind,
        "status": status,
        "rejection_reason": None,
        "transformations_applied": transformations,
        "extraction_confidence": extraction_confidence,
        "notes": "Normalized from 5.4 proposition",
    }

    knowledge_items.append(knowledge_item)
    ledger_entries.append(ledger_entry)

print("[OK] Processed {} propositions".format(len(propositions)))
print()
print("Transformation summary:")
for status, count in transformation_stats.items():
    print("  {}: {}".format(status, count))
print()

# =========================================================================
# STEP 4: VALIDATION
# =========================================================================

print("-" * 80)
print("STEP 4: VALIDATION")
print("-" * 80)
print()

validation_pass = True

# 13.1 Per-item validation
print("Per-item validation:")
for item, ledger in zip(knowledge_items, ledger_entries):
    # Check original_text preserved
    if not item["original_proposition"]:
        print("[FAIL] Missing original_proposition in {}".format(item["knowledge_item_id"]))
        validation_pass = False

    # Check knowledge_type is one of 9 types
    valid_types = ["CONCEPT", "PROCEDURE", "PRINCIPLE", "OBSERVATION",
                   "RECOMMENDATION", "CONDITION", "EXAMPLE", "CONTEXT", "LIMITATION"]
    if item["knowledge_type"] not in valid_types:
        print("[FAIL] Invalid knowledge_type {} in {}".format(
            item["knowledge_type"], item["knowledge_item_id"]))
        validation_pass = False

    # Check epistemic_status
    valid_statuses = ["SOURCE_REPORTED", "SOURCE_RECOMMENDED", "SOURCE_OBSERVED", "UNKNOWN"]
    if item["epistemic_status"] not in valid_statuses:
        print("[FAIL] Invalid epistemic_status {} in {}".format(
            item["epistemic_status"], item["knowledge_item_id"]))
        validation_pass = False

    # Check UNKNOWN items have required fields
    if item["epistemic_status"] == "UNKNOWN":
        if item["extraction_confidence"] >= 0.7:
            print("[FAIL] UNKNOWN item {} has HIGH confidence {}".format(
                item["knowledge_item_id"], item["extraction_confidence"]))
            validation_pass = False
        if not item["ambiguity"]:
            print("[FAIL] UNKNOWN item {} missing ambiguity field".format(
                item["knowledge_item_id"]))
            validation_pass = False
        if not item["notes"]:
            print("[FAIL] UNKNOWN item {} missing candidate_classes in notes".format(
                item["knowledge_item_id"]))
            validation_pass = False

print("[OK] Per-item validation complete")
print()

# 13.2 Artifact-level validation
print("Artifact-level validation:")
if len(knowledge_items) != 36:
    print("[FAIL] Expected 36 KnowledgeItems, got {}".format(len(knowledge_items)))
    validation_pass = False
else:
    print("[OK] All 36 propositions present")

if len(ledger_entries) != 36:
    print("[FAIL] Expected 36 ledger entries, got {}".format(len(ledger_entries)))
    validation_pass = False
else:
    print("[OK] Ledger has 36 entries (1:1 with input)")

# Check no duplicate IDs
knowledge_ids = [item["knowledge_item_id"] for item in knowledge_items]
if len(knowledge_ids) != len(set(knowledge_ids)):
    print("[FAIL] Duplicate knowledge_item_ids detected")
    validation_pass = False
else:
    print("[OK] All knowledge_item_ids unique")

# Check all 9 KnowledgeTypes used from frozen enum
unknown_items = sum(1 for item in knowledge_items if item["epistemic_status"] == "UNKNOWN")
if unknown_items != 5:
    print("[FAIL] Expected 5 UNKNOWN items, got {}".format(unknown_items))
    validation_pass = False
else:
    print("[OK] 5 UNKNOWN items with epistemic_status=UNKNOWN")

print()

# =========================================================================
# STEP 5: PERSIST ARTIFACTS
# =========================================================================

print("-" * 80)
print("STEP 5: PERSIST ARTIFACTS")
print("-" * 80)
print()

# Output KnowledgeItems
output_artifact = {
    "version": "1.0",
    "phase": "5.5",
    "source_id": source_record["source_id"],
    "source_title": source_record["source_title"],
    "normalization_metadata": {
        "total_items": len(knowledge_items),
        "classified": sum(1 for item in knowledge_items if item["epistemic_status"] != "UNKNOWN"),
        "unknown": sum(1 for item in knowledge_items if item["epistemic_status"] == "UNKNOWN"),
        "timestamp": datetime.now().isoformat() + "Z",
    },
    "knowledge_items": knowledge_items,
}

output_path = Path("yt_74ab96e1f377_knowledge_normalized_5_5.json")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_artifact, f, indent=2, ensure_ascii=False)

print("[OK] Wrote {} KnowledgeItems to {}".format(len(knowledge_items), output_path))

# Output ledger
ledger_artifact = {
    "version": "1.0",
    "phase": "5.5",
    "source_id": source_record["source_id"],
    "timestamp": datetime.now().isoformat() + "Z",
    "total_items": len(ledger_entries),
    "ledger": ledger_entries,
}

ledger_path = Path("yt_74ab96e1f377_normalization_ledger_5_5.json")
with open(ledger_path, 'w', encoding='utf-8') as f:
    json.dump(ledger_artifact, f, indent=2, ensure_ascii=False)

print("[OK] Wrote {} ledger entries to {}".format(len(ledger_entries), ledger_path))
print()

# =========================================================================
# STEP 6: FINAL REPORT
# =========================================================================

print("=" * 80)
print("STEP 5.5 NORMALIZATION REPORT")
print("=" * 80)
print()

print("INPUT:")
print("  File: {}".format(input_path))
print("  Propositions: {}".format(len(propositions)))
print("  Distribution: {} classified + {} UNKNOWN".format(classified_count, unknown_count))
print()

print("OUTPUT:")
print("  KnowledgeItems: {}".format(output_path))
print("  Ledger: {}".format(ledger_path))
print()

print("STATISTICS:")
print("  NORMALIZED: {}".format(transformation_stats["NORMALIZED"]))
print("  UNCHANGED: {}".format(transformation_stats["UNCHANGED"]))
print("  UNRESOLVED: {}".format(transformation_stats["UNRESOLVED"]))
print()

print("VALIDATION:")
if validation_pass:
    print("  Status: PASS")
    print("  All 36 items validated")
    print("  All UNKNOWN items have epistemic_status=UNKNOWN")
    print("  All required fields present")
else:
    print("  Status: FAIL")
    print("  See errors above")
print()

print("=" * 80)
print("STEP 5.5 NORMALIZATION {}".format("COMPLETE" if validation_pass else "FAILED"))
print("=" * 80)

if not validation_pass:
    exit(1)
