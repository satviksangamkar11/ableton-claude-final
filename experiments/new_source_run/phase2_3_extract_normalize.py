"""PHASE 2+3 - Semantic extraction + normalization for the NEW source.

Uses the CANONICAL frozen Step 5 logic:
  - step_5_4_q_repaired_extraction.should_start_new_unit   (verbatim, via AST)
  - step_5_4_q_semantic_contract.classify_semantic         (imported module)
  - step_5_5_knowledge_normalization.*                     (verbatim, via AST)
  - knowledge_item.KnowledgeItem                           (imported)
  - step_5_6_knowledge_store.KnowledgeStore                (imported)

No frozen Step 5 file is modified. Function bodies are loaded verbatim from
the frozen sources so there is zero logic drift.
"""
import json, os, re, sys, ast, hashlib, datetime

ROOT = r"D:\ableton claude"
KDIR = os.path.join(ROOT, "serum2", "knowledge")
sys.path.insert(0, KDIR)

SOURCE_ID = "yt_f507169bd7cb"

from step_5_4_q_semantic_contract import classify_semantic
from knowledge_item import (KnowledgeItem, KnowledgeType, EpistemicStatus,
                            SourceReference, ExtractionMetadata, SemanticBinding)
from step_5_6_knowledge_store import KnowledgeStore


def load_funcs(path, names):
    """Load named function defs verbatim from a frozen script without running it."""
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    ns = {"re": re, "hashlib": hashlib, "Optional": object, "List": list}
    out = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            mod = ast.Module(body=[node], type_ignores=[])
            exec(compile(mod, path, "exec"), ns)
            out[node.name] = ns[node.name]
    return out


f1 = load_funcs(os.path.join(KDIR, "step_5_4_q_repaired_extraction.py"),
                {"should_start_new_unit"})
f2 = load_funcs(os.path.join(KDIR, "step_5_5_knowledge_normalization.py"),
                {"generate_knowledge_id", "get_best_guess_type", "normalize_proposition_text"})
should_start_new_unit = f1["should_start_new_unit"]
generate_knowledge_id = f2["generate_knowledge_id"]
get_best_guess_type = f2["get_best_guess_type"]
normalize_proposition_text = f2["normalize_proposition_text"]
print("[OK] canonical functions loaded verbatim from frozen Step 5 sources")

rec = json.load(open(os.path.join(KDIR, "%s_source_ingestion_5_3.json" % SOURCE_ID), encoding="utf-8"))
segments = rec["transcript_segments"]
src = rec["source"]
print("[OK] segments:", len(segments))

# ---------- PHASE 2a: group into semantic units (canonical) ----------
units, cur = [], [segments[0]]
for i in range(1, len(segments)):
    if should_start_new_unit(segments[i-1], segments[i]):
        units.append(cur); cur = [segments[i]]
    else:
        cur.append(segments[i])
units.append(cur)
print("[OK] semantic units:", len(units))

# ---------- PHASE 2b: classify (canonical) ----------
props, filler, n = [], 0, 0
for unit in units:
    text = " ".join(s["text"] for s in unit)
    if len(text) < 10:
        filler += 1; continue
    seg_ids = [s["segment_id"] for s in unit]
    r = classify_semantic(text, seg_ids)
    kind = r["classification"]
    if kind == "FILLER":
        filler += 1; continue
    est = "SOURCE_REPORTED"
    if re.search(r"(?:I recommend|I suggest|you should|try)", text, re.I):
        est = "SOURCE_RECOMMENDED"
    elif re.search(r"(?:I notice|I see|I found|as you can see)", text, re.I):
        est = "SOURCE_OBSERVED"
    p = {
        "proposition_id": "prop_%06d" % n,
        "source_id": SOURCE_ID,
        "source_segment_ids": seg_ids,
        "segment_count": len(unit),
        "start_time_sec": unit[0]["start_time_sec"],
        "end_time_sec": unit[-1]["end_time_sec"],
        "original_text": text,
        "kind": kind,
        "epistemic_status": est,
        "extraction_confidence": r.get("confidence", 0.7),
        "semantic_classifier_rationale": r.get("rationale", ""),
        "ambiguity": r.get("ambiguity"),
    }
    if kind == "UNKNOWN" and r.get("candidate_classes"):
        p["candidate_classes"] = r["candidate_classes"]
    props.append(p); n += 1

print("[OK] propositions:", len(props), "| filler filtered:", filler)
from collections import Counter
print("[OK] kind distribution:", dict(Counter(p["kind"] for p in props)))
print("[OK] epistemic distribution:", dict(Counter(p["epistemic_status"] for p in props)))
print("[OK] ambiguous:", sum(1 for p in props if p["ambiguity"]))

ext_path = os.path.join(KDIR, "%s_extraction_5_4.json" % SOURCE_ID)
json.dump({"source_id": SOURCE_ID, "phase": "5.4", "propositions": props},
          open(ext_path, "w", encoding="utf-8"), indent=1)
print("[WROTE]", ext_path)

# ---------- PHASE 3: normalize -> KnowledgeItems (canonical) ----------
items, stats = [], Counter()
for p in props:
    kind = p["kind"]
    if kind == "UNKNOWN":
        kt = get_best_guess_type(p.get("candidate_classes", []))
        amb = p["ambiguity"] or "classifier returned UNKNOWN; candidates=%s" % p.get("candidate_classes")
    else:
        kt, amb = kind, p["ambiguity"]
    try:
        ktype = KnowledgeType[kt]
    except KeyError:
        stats["REJECTED"] += 1; continue
    try:
        estatus = EpistemicStatus[p["epistemic_status"]]
    except KeyError:
        stats["REJECTED"] += 1; continue

    norm = normalize_proposition_text(p["original_text"], kind)
    stats["NORMALIZED" if norm else "UNCHANGED"] += 1

    ki = KnowledgeItem(
        knowledge_item_id=generate_knowledge_id(SOURCE_ID, p["proposition_id"]),
        source_reference=SourceReference(
            source_id=SOURCE_ID,
            source_type="YOUTUBE_VIDEO",
            source_url=src["url"],
            source_title=src["title"],
            segment_ids=p["source_segment_ids"],
            start_time_sec=p["start_time_sec"],
            end_time_sec=p["end_time_sec"],
        ),
        original_proposition=p["original_text"],
        knowledge_type=ktype,
        epistemic_status=estatus,
        normalized_proposition=norm,
        extraction_confidence=p["extraction_confidence"],
        ambiguity=amb,
        extraction_metadata=ExtractionMetadata(
            extraction_method="step_5_4_q_semantic_contract.classify_semantic",
            extraction_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            classifier_rationale=p["semantic_classifier_rationale"],
        ) if "classifier_rationale" in ExtractionMetadata.__dataclass_fields__ else None,
    )
    items.append(ki)

print("[OK] KnowledgeItems:", len(items), "| stats:", dict(stats))

store_path = os.path.join(KDIR, "%s_canonical_knowledge_store_5_6.json" % SOURCE_ID)
store = KnowledgeStore(store_path)
ins = dup = 0
for ki in items:
    try:
        if store.exists(ki.knowledge_item_id):
            dup += 1
        else:
            store.insert(ki); ins += 1
    except Exception as e:
        print("  [conflict]", ki.knowledge_item_id, e); dup += 1
print("[OK] inserted:", ins, "| already present:", dup, "| store count:", store.count())
print("[WROTE]", store_path)
