#!/usr/bin/env python
"""External knowledge extraction from transcript.

Reads transcript JSON from disk and extracts compact KnowledgeItems.
Does NOT load raw transcript into Claude Code context.

Usage:
    python source/extract_knowledge.py data/transcripts/yt_QqYlEc_6E6A.json

Output:
    data/knowledge/yt_QqYlEc_6E6A.json (structured KnowledgeItems)
"""
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


def extract_knowledge_items(transcript_file: Path) -> List[Dict[str, Any]]:
    """Extract structured KnowledgeItems from transcript."""
    with open(transcript_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    source_id = data.get("source_id")
    source_url = data.get("source_url")
    segments = data.get("segments", [])

    if not segments:
        print("[WARN] No segments found in transcript", file=sys.stderr)
        return []

    knowledge_items = []

    # Simple heuristic-based extraction
    # Group consecutive segments that form semantic units
    current_unit = []
    current_start_time = 0

    for i, segment in enumerate(segments):
        current_unit.append(segment)

        # Start new unit every ~15-20 seconds or at silence
        should_split = False
        if len(current_unit) >= 3:
            end_time = current_unit[-1].get("start_time_sec", 0)
            if end_time - current_start_time > 15:
                should_split = True

        if should_split or i == len(segments) - 1:
            # Convert unit to KnowledgeItem
            unit_text = " ".join(s.get("text", "") for s in current_unit).strip()

            if len(unit_text) > 5:  # Skip very short segments
                segment_ids = [s.get("segment_id") for s in current_unit]
                start_sec = current_unit[0].get("start_time_sec", 0)
                end_sec = current_unit[-1].get("start_time_sec", 0)

                # Determine knowledge type based on heuristics
                knowledge_type = classify_knowledge_type(unit_text)

                # Generate item ID
                item_id = f"ki_{hashlib.md5(unit_text.encode()).hexdigest()[:16]}"

                ki = {
                    "knowledge_item_id": item_id,
                    "source_id": source_id,
                    "source_url": source_url,
                    "source_segment_ids": segment_ids,
                    "timestamp_start": start_sec,
                    "timestamp_end": end_sec,
                    "original_proposition": unit_text,
                    "knowledge_type": knowledge_type,
                    "epistemic_status": "SOURCE_DERIVED",
                    "concepts": extract_concepts(unit_text),
                    "candidate_semantic_targets": extract_semantic_candidates(unit_text),
                    "producer_actions": extract_producer_actions(unit_text),
                    "extraction_timestamp": datetime.utcnow().isoformat(),
                }

                knowledge_items.append(ki)

            current_unit = []
            current_start_time = segments[i].get("start_time_sec", 0) if i < len(segments) - 1 else 0

    return knowledge_items


def classify_knowledge_type(text: str) -> str:
    """Classify the type of knowledge based on text content."""
    text_lower = text.lower()

    # Heuristics for classification
    if any(w in text_lower for w in ["how to", "steps to", "process", "method"]):
        return "PROCEDURE"

    if any(w in text_lower for w in ["increase", "decrease", "raise", "lower", "adjust", "turn", "change"]):
        return "TECHNIQUE"

    if any(w in text_lower for w in ["creates", "produces", "makes", "gives", "results in", "adds"]):
        return "OBSERVATION"

    if any(w in text_lower for w in ["sounds like", "sounds", "ear", "listen", "hear"]):
        return "OBSERVATION"

    return "FACT"


def extract_concepts(text: str) -> List[str]:
    """Extract candidate concepts from text."""
    concepts = []
    text_lower = text.lower()

    # Musical/synthesis concepts
    synthesis_terms = {
        "release": ["release", "tail", "sustain"],
        "attack": ["attack", "onset", "start"],
        "filter": ["filter", "cutoff", "resonance", "low-pass", "high-pass"],
        "oscillator": ["oscillator", "osc", "wave", "wavetable"],
        "envelope": ["envelope", "adsr", "decay"],
        "modulation": ["modulation", "lfo", "mod", "depth"],
        "volume": ["volume", "amplitude", "level", "gain"],
        "pitch": ["pitch", "note", "frequency", "octave", "semitone"],
        "effects": ["effect", "reverb", "delay", "chorus", "distortion"],
    }

    for concept, keywords in synthesis_terms.items():
        if any(kw in text_lower for kw in keywords):
            concepts.append(concept)

    return list(set(concepts))  # Remove duplicates


def extract_semantic_candidates(text: str) -> List[str]:
    """Extract candidate semantic targets from text."""
    # These are NOT authoritative - just candidates for resolution
    candidates = []
    text_lower = text.lower()

    # Map text hints to potential Serum semantic targets
    if "release" in text_lower:
        candidates.extend(["Env1.Release", "Env2.Release"])

    if "attack" in text_lower:
        candidates.extend(["Env1.Attack", "Env2.Attack"])

    if ("filter" in text_lower or "cutoff" in text_lower):
        candidates.extend(["Filter.Cutoff", "Filter.Resonance"])

    if ("osc" in text_lower or "oscillator" in text_lower or "wave" in text_lower):
        candidates.extend(["OSC1.Volume", "OSC2.Volume", "OSC1.Octave", "OSC1.Detune"])

    if "volume" in text_lower or "level" in text_lower or "gain" in text_lower:
        candidates.extend(["OSC1.Volume", "OSC2.Volume", "Master.Volume"])

    return list(set(candidates))  # Remove duplicates


def extract_producer_actions(text: str) -> List[str]:
    """Extract candidate producer actions from text."""
    actions = []
    text_lower = text.lower()

    if any(w in text_lower for w in ["increase", "raise", "turn up", "higher"]):
        actions.append("increase")

    if any(w in text_lower for w in ["decrease", "lower", "turn down", "reduce"]):
        actions.append("decrease")

    if any(w in text_lower for w in ["enable", "activate", "turn on"]):
        actions.append("enable")

    if any(w in text_lower for w in ["disable", "deactivate", "turn off"]):
        actions.append("disable")

    if any(w in text_lower for w in ["select", "choose", "pick", "load"]):
        actions.append("select")

    return list(set(actions))  # Remove duplicates


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_knowledge.py <TRANSCRIPT_JSON_PATH>", file=sys.stderr)
        sys.exit(1)

    transcript_path = Path(sys.argv[1])

    if not transcript_path.exists():
        print(f"[ERROR] Transcript file not found: {transcript_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Reading transcript from: {transcript_path}", file=sys.stderr)

    # Extract knowledge items
    knowledge_items = extract_knowledge_items(transcript_path)

    if not knowledge_items:
        print("[WARN] No knowledge items extracted", file=sys.stderr)

    # Build output
    output = {
        "source_id": None,
        "extraction_timestamp": datetime.utcnow().isoformat(),
        "item_count": len(knowledge_items),
        "knowledge_items": knowledge_items,
    }

    if knowledge_items:
        output["source_id"] = knowledge_items[0]["source_id"]

    # Save to disk
    output_dir = Path("data/knowledge")
    output_dir.mkdir(parents=True, exist_ok=True)

    source_id = output["source_id"] or "unknown"
    output_path = output_dir / f"{source_id}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    # Print summary
    print(f"[OK] source_id: {source_id}")
    print(f"[OK] knowledge_items: {len(knowledge_items)}")
    print(f"[OK] saved: {output_path}")
    print("\n[COMPLETE] Knowledge extraction finished.")
    print("[NOTE] Raw transcript NOT included in output (stays external to reasoning).")


if __name__ == "__main__":
    main()
