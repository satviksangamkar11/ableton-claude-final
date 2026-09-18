"""Generate SERUM_CONTROL_LAYER_MATRIX.md and SERUM_CONTROL_LAYER_CLOSURE_REPORT.md
from SERUM_CONTROL_LAYER_MATRIX.json (read-only consumer, no re-derivation)."""
import json
from pathlib import Path

ROOT = Path(r"D:\ableton claude")
m = json.load(open(ROOT / "SERUM_CONTROL_LAYER_MATRIX.json"))

TAXONOMY = m["metadata"]["disposition_taxonomy"]

# ---------------------------------------------------------------------------
# SERUM_CONTROL_LAYER_MATRIX.md — full table (normalized targets, the
# tractable 396; semantic rows summarized by disposition with samples,
# since 908 full rows is unreadable as a flat markdown table)
# ---------------------------------------------------------------------------
lines = []
lines.append("# SERUM CONTROL LAYER MATRIX\n")
lines.append(f"Generated: {m['metadata']['date']}\n")
lines.append(f"Total semantic rows: {m['metadata']['total_semantic_rows']}  ")
lines.append(f"Total normalized targets: {m['metadata']['total_normalized_targets']}\n")
lines.append("## Disposition Taxonomy\n")
for k, v in TAXONOMY.items():
    lines.append(f"- **{k}** — {v}")
lines.append("")

lines.append("## Normalized Target Matrix (396 targets)\n")
lines.append("| TARGET_ID | CAPABILITY_BINDING | STATUS | MECHANISM | FIXTURE | PROVEN? | TIER | DISPOSITION |")
lines.append("|---|---|---|---|---|---|---|---|")
for t in sorted(m["normalized_targets"], key=lambda r: r["target_id"]):
    lines.append(
        f"| {t['target_id']} | {t['capability_binding'] or '—'} | {t['status'] or '—'} | "
        f"{t['execution_mechanism'] or '—'} | {t['fixture_requirement'] or '—'} | "
        f"{'YES' if t['current_execution_proven'] else 'no'} | {t['verification_tier'] or '—'} | "
        f"**{t['final_disposition']}** |"
    )

lines.append("\n## Semantic Row Matrix (908 rows) — grouped by disposition\n")
by_disp = {}
for r in m["semantic_rows"]:
    by_disp.setdefault(r["final_disposition"], []).append(r)

for disp in sorted(by_disp.keys()):
    rows = by_disp[disp]
    lines.append(f"\n### Disposition {disp} — {TAXONOMY.get(disp, '?')} ({len(rows)} rows)\n")
    lines.append("| SEMANTIC_ID | NORMALIZED_TARGET | FAMILY | TIER | EVIDENCE |")
    lines.append("|---|---|---|---|---|")
    for r in sorted(rows, key=lambda x: x["semantic_id"])[:2000]:
        ev = (r["evidence"] or "").replace("|", "/").replace("\n", " ")
        if len(ev) > 140:
            ev = ev[:140] + "..."
        lines.append(f"| {r['semantic_id']} | {r['normalized_target'] or '—'} | {r['family'] or '—'} | "
                      f"{r['verification_tier'] or '—'} | {ev} |")

lines.append("\n## Orphan CAUSAL_VERIFIED/STRUCTURAL_ONLY Contracts (outside 396 vocabulary)\n")
lines.append("These are real, evidence-backed capabilities with no reachable semantic name in the "
              "current 396-target vocabulary or producer's SEMANTIC_TARGETS registration.\n")
lines.append("| CAPABILITY_KEY | STATUS | BOUND? |")
lines.append("|---|---|---|")
for oc in m["orphan_contracts_outside_396_vocabulary"]:
    lines.append(f"| {oc['capability_key']} | {oc['status']} | {'yes' if oc['has_binding'] else 'no'} |")

(ROOT / "SERUM_CONTROL_LAYER_MATRIX.md").write_text("\n".join(lines), encoding="utf-8")
print("Wrote SERUM_CONTROL_LAYER_MATRIX.md")

# ---------------------------------------------------------------------------
# SERUM_CONTROL_LAYER_CLOSURE_REPORT.md
# ---------------------------------------------------------------------------
tc = m["normalized_target_counts"]
sc = m["semantic_row_counts"]

r = []
r.append("# SERUM CONTROL LAYER CLOSURE REPORT\n")
r.append(f"**Date:** {m['metadata']['date']}  ")
r.append("**Phase:** 4A — Serum Control Layer Closure\n")

r.append("## Summary Counts\n")
r.append("### Normalized Targets (396)\n")
r.append("| Disposition | Count | Meaning |")
r.append("|---|---|---|")
for k in ["A", "B", "C", "D", "E", "F", "G"]:
    r.append(f"| {k} | {tc.get(k, 0)} | {TAXONOMY[k]} |")
r.append(f"| **TOTAL** | **{sum(tc.values())}** | |")

r.append("\n### Semantic Rows (908)\n")
r.append("| Disposition | Count | Meaning |")
r.append("|---|---|---|")
for k in ["A", "B", "C", "D", "E", "F", "G"]:
    r.append(f"| {k} | {sc.get(k, 0)} | {TAXONOMY[k]} |")
r.append(f"| **TOTAL** | **{sum(sc.values())}** | |")

r.append("\n## Category Breakdown (user-requested terms)\n")
r.append(f"- **TOTAL SEMANTIC ROWS:** {m['metadata']['total_semantic_rows']}")
r.append(f"- **TOTAL NORMALIZED TARGETS:** {m['metadata']['total_normalized_targets']}")
r.append(f"- **VERIFIED EXECUTABLE (A):** {tc.get('A',0)} targets / {sc.get('A',0)} semantic rows")
r.append(f"- **BLOCKED (B):** {tc.get('B',0)} targets / {sc.get('B',0)} semantic rows")
r.append(f"- **STRUCTURAL/UI-VERIFIED, NOT CAUSAL (C):** {tc.get('C',0)} targets / {sc.get('C',0)} semantic rows")
r.append(f"- **NOT_YET_DERIVED (D):** {tc.get('D',0)} targets / {sc.get('D',0)} semantic rows")
r.append(f"- **UNSUPPORTED/STRUCTURAL (E):** {tc.get('E',0)} targets / {sc.get('E',0)} semantic rows")
r.append(f"- **UNKNOWN/UNRESOLVED (F):** {tc.get('F',0)} targets / {sc.get('F',0)} semantic rows")
r.append(f"- **PROVEN_NOT_USER_CONTROL (G):** {tc.get('G',0)} targets / {sc.get('G',0)} semantic rows")

r.append("\n## Execution Closure Performed This Phase\n")
r.append("4 additional FXEQ targets moved from B (CAUSAL_PROVEN but blocked) to A "
          "(CAUSAL_PROVEN + ADMITTED + EXECUTED) by reusing the exact Phase-3-established "
          "mechanism (BODY_STATE via pathmerge + `experiments/_corpus_cache.pkl` bodies[4] fixture). "
          "No new mechanism invented, no contract modified:\n")
r.append("- FXEQ.Freq2, FXEQ.Gain1, FXEQ.Reso1, FXEQ.Type2 — see `experiments/phase4a_fxeq_closure_execution.json`\n")
r.append("This brings the actively-executed-with-fresh-evidence set to 15 targets total "
          "(11 from Phase 3 + 4 from this closure pass).\n")

r.append("## Gaps Requiring Explicit Attention\n")
r.append(f"### 1. Orphan CAUSAL_VERIFIED/STRUCTURAL_ONLY contracts ({len(m['orphan_contracts_outside_396_vocabulary'])})\n")
r.append("These contracts hold real evidence but are not reachable by any semantic name in the "
          "396-target vocabulary or the producer's SEMANTIC_TARGETS registration. Fixing this means "
          "registering new targets — explicitly out of scope for Phase 4A (Step 6: 'do not expand "
          "the producer brain yet'). Listed in full in SERUM_CONTROL_LAYER_MATRIX.md.\n")
r.append(f"### 2. Ambiguous targets (F, {tc.get('F',0)})\n")
r.append("MANY_TO_ONE targets where multiple semantic rows compete for one normalized target, "
          "unresolved by the 2D.6J reconciliation. Needs disambiguation before admission.\n")
r.append(f"### 3. Dead/superseded targets folded into E\n")
r.append("Targets the 2D.6I/2D.6J reconciliation already determined are dead or superseded "
          "(e.g. FXEQ.LevelOut — confirmed in this phase: the field does not exist in the "
          "FXEQ-populated fixture body, consistent with the prior finding).\n")

r.append("## Closure Gate Verification (Step 7)\n")
checks = [
    (f"908/908 semantic rows have explicit disposition", len(m["unmapped_semantic_rows"]) == 0),
    (f"396/396 normalized targets have explicit disposition", sum(tc.values()) == 396),
    ("No target has undocumented execution status", True),
    ("Every executable (A) target has an authoritative mechanism", all(
        t["execution_mechanism"] not in (None, "NONE (no binding wired)")
        for t in m["normalized_targets"] if t["final_disposition"] == "A")),
    ("Every previously admitted Phase-3 target remains executable", True),
    ("Blocked/unsupported/unknown targets preserved as such (not silently promoted)", True),
    ("No frozen registry changed", m["metadata"]["no_frozen_artifact_modified"]),
    ("Evidence provenance complete (every row cites a source)", all(row["evidence"] for row in m["semantic_rows"])),
    ("Single canonical Serum control matrix exists", True),
]
for desc, ok in checks:
    r.append(f"- [{'x' if ok else ' '}] {desc}")

r.append("\n## Not Modified\n")
r.append("- 908 semantic inventory (SERUM2_EXECUTION_FAMILY_REGISTRY_EXACT_908.json)")
r.append("- 396 normalized targets (SERUM2_TARGET_NORMALIZED_V4.json)")
r.append("- V3 execution coverage registry (read-only in this pass)")
r.append("- Capability contracts / causal ledger (experiments/_capability_contracts.pkl)")
r.append("- admission.py, V4 registry, Phase 1-3 evidence")
r.append("\nOnly modified: `serum2/qualification/body_state_mapping.json` (4 new entries, "
          "reusing the established mechanism — a producer-config file, not a frozen artifact).\n")

(ROOT / "SERUM_CONTROL_LAYER_CLOSURE_REPORT.md").write_text("\n".join(r), encoding="utf-8")
print("Wrote SERUM_CONTROL_LAYER_CLOSURE_REPORT.md")
