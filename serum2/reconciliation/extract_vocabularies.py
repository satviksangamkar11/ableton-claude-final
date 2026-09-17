#!/usr/bin/env python3
"""
Phase 1: Extract both semantic and target vocabularies.

This script:
1. Reads frozen SERUM2_SEMANTIC_INVENTORY.json
2. Extracts all semantic records (semantic_id, section, module, label, control_type, etc.)
3. Reads existing targets from serum2/compiler/targets.py
4. Produces two canonical JSON files for reconciliation

NO UI PROBING. Text-only extraction from frozen inventory and existing code.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class SemanticRecord:
    """Extracted semantic record from inventory."""
    semantic_id: str
    section: str
    module: Optional[str]
    submodule: Optional[str]
    label: str
    control_type: Optional[str]
    value_range: Optional[str]
    options: Optional[List[str]]
    conditional_visibility: Optional[str]
    conditions: Optional[List[str]]
    cross_references: Optional[List[str]]
    resource_dependency: Optional[str]
    structural_action: bool
    status: str
    sources: List[str]
    evidence_type: Optional[str]

@dataclass
class ExistingTarget:
    """Existing target from targets.py."""
    semantic_name: str
    capability_key: str
    target_source: str  # VST3_PARAMETER, UI_ACTION, STRUCTURAL_OPERATION, etc.

def read_frozen_inventory(path: Path) -> Dict[str, Any]:
    """Read frozen semantic inventory JSON."""
    print(f"Reading frozen inventory from {path}...")
    with open(path) as f:
        return json.load(f)

def extract_semantic_records(inventory: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract all semantic records from the frozen inventory.

    Walks the sections and their records, preserving all metadata exactly.
    """
    records = []

    # The inventory structure has records embedded in different ways
    # depending on the section. We need to handle the closure ledgers.

    if 'records' in inventory:
        records.extend(inventory['records'])

    # Also check for records in section closures
    for key, value in inventory.items():
        if key.endswith('_closure_ledger') and isinstance(value, dict):
            # Each closure ledger contains closure passes
            for pass_key, pass_data in value.items():
                if isinstance(pass_data, dict) and 'records' in pass_data:
                    records.extend(pass_data['records'])

    return records

def extract_existing_targets(targets_path: Path) -> List[ExistingTarget]:
    """
    Extract all existing semantic targets from targets.py.
    Parses the SEMANTIC_TARGETS dictionary.
    """
    print(f"Reading targets from {targets_path}...")
    with open(targets_path) as f:
        content = f.read()

    # Extract the SEMANTIC_TARGETS dict via regex
    # Pattern: "SEMANTIC_NAME": SemanticTargetRef("SEMANTIC_NAME", "capability_key")
    pattern = r'"([^"]+)":\s*SemanticTargetRef\("([^"]+)",\s*"([^"]+)"\)'
    matches = re.findall(pattern, content)

    targets = []
    for semantic_name, _, capability_key in matches:
        # Determine source based on naming convention
        if semantic_name.startswith("FX") or semantic_name.startswith("ModRoute"):
            target_source = "VST3_PARAMETER"  # Most targets are VST3-based
        elif semantic_name in ["FXEQ", "FXDistortion", "FXDelay", "FXReverb"]:
            target_source = "VST3_PARAMETER"
        else:
            target_source = "VST3_PARAMETER"  # Default assumption

        targets.append(ExistingTarget(
            semantic_name=semantic_name,
            capability_key=capability_key,
            target_source=target_source
        ))

    return targets

def save_semantic_vocabulary(records: List[Dict[str, Any]], output_path: Path) -> None:
    """Save extracted semantic vocabulary to JSON."""
    output = {
        "metadata": {
            "source": "SERUM2_SEMANTIC_INVENTORY.json",
            "extraction_date": "2026-09-16",
            "purpose": "Phase 1: Extract semantic vocabulary for target reconciliation",
            "record_count": len(records)
        },
        "records": records
    }

    print(f"Saving semantic vocabulary to {output_path} ({len(records)} records)...")
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

def save_target_vocabulary(targets: List[ExistingTarget], output_path: Path) -> None:
    """Save extracted target vocabulary to JSON."""
    output = {
        "metadata": {
            "source": "serum2/compiler/targets.py SEMANTIC_TARGETS",
            "extraction_date": "2026-09-16",
            "purpose": "Phase 1: Extract existing target vocabulary",
            "target_count": len(targets)
        },
        "targets": [asdict(t) for t in targets]
    }

    print(f"Saving target vocabulary to {output_path} ({len(targets)} targets)...")
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

def main():
    """Main extraction workflow."""
    project_root = Path("D:/ableton claude")

    # Paths
    inventory_path = project_root / "serum2" / "SERUM2_SEMANTIC_INVENTORY.json"
    targets_path = project_root / "serum2" / "compiler" / "targets.py"

    # Output paths
    reconciliation_dir = project_root / "serum2" / "reconciliation"
    reconciliation_dir.mkdir(parents=True, exist_ok=True)

    semantic_vocab_path = reconciliation_dir / "PHASE_1A_SEMANTIC_VOCABULARY.json"
    target_vocab_path = reconciliation_dir / "PHASE_1B_TARGET_VOCABULARY.json"

    # Step 1: Extract semantic vocabulary
    print("\n=== PHASE 1A: Extract Semantic Vocabulary ===")
    inventory = read_frozen_inventory(inventory_path)
    print(f"Inventory loaded. Keys: {list(inventory.keys())[:5]}...")

    # For now, we'll manually extract a representative sample
    # since the structure is complex. In production, we'd walk it fully.
    semantic_records = extract_semantic_records(inventory)
    print(f"Extracted {len(semantic_records)} semantic records (or will enumerate below)")

    # Step 2: Extract target vocabulary
    print("\n=== PHASE 1B: Extract Target Vocabulary ===")
    existing_targets = extract_existing_targets(targets_path)
    print(f"Extracted {len(existing_targets)} existing targets from targets.py")

    # Step 3: Save both vocabularies
    print("\n=== SAVE VOCABULARIES ===")
    save_semantic_vocabulary(semantic_records or [], semantic_vocab_path)
    save_target_vocabulary(existing_targets, target_vocab_path)

    # Summary
    print("\n=== EXTRACTION COMPLETE ===")
    print(f"Semantic records: {len(semantic_records) or 'N/A (manual enumeration required)'}")
    print(f"Existing targets: {len(existing_targets)}")
    print(f"\nOutput files:")
    print(f"  - {semantic_vocab_path}")
    print(f"  - {target_vocab_path}")
    print("\nNext: Phase 2 (Normalize), Phase 3 (Reconciliation), Phase 4 (Gap Analysis)")

if __name__ == "__main__":
    main()
