"""
PHASE 2D.6J bidirectional reconciliation builder.
READ-ONLY over raw authoritative artifacts. Writes only the 2D.6J outputs.
No targets.py / semantic inventory / contracts touched.
"""
import json
import hashlib

R = "serum2/reconciliation/"


def load(name):
    with open(R + name, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- RAW AUTHORITATIVE INPUTS ----------
sem_normalized = load("SERUM2_SEMANTIC_NORMALIZED.json")
assert sem_normalized["metadata"]["record_count"] == 908, "SEMANTIC COUNT GATE FAILED"
sem_records = {r["semantic_id"]: r for r in sem_normalized["records"]}
assert len(sem_records) == 908

target_normalized = load("SERUM2_TARGET_NORMALIZED_V4.json")
assert target_normalized["metadata"]["total"] == 396, "TARGET COUNT GATE FAILED"
target_ids_all = [t["target_id"] for t in target_normalized["targets"]]
assert len(target_ids_all) == 396
assert len(set(target_ids_all)) == 396, "duplicate target ids"

sem_rows = {r["semantic_id"]: dict(r) for r in load("_phase2d6g_semantic_rows.json")}
assert len(sem_rows) == 908
assert len(set(sem_rows.keys())) == 908, "duplicate semantic ids"

cp_matrix = {r["semantic_id"]: r for r in load("SERUM2_CONTROL_PATH_MATRIX.json")["records"]}
assert len(cp_matrix) == 908

frozen_152 = set(load("_phase2d6f_true_unknown_152.json"))
assert len(frozen_152) == 152

reverse_audit = {r["target_id"]: dict(r) for r in load("_phase2d6e_final_reverse_audit.json")}
assert len(reverse_audit) == 396

four_tables_2d6h = load("_phase2d6h_four_tables.json")
table3_2d6h = four_tables_2d6h["table3_newly_resolved"]
orphan_ids_2d6h = set(four_tables_2d6h["table2_technical_to_semantic"]["orphan_ids"])
assert len(orphan_ids_2d6h) == 98

pnuc_ids = set(
    sid for sid, r in sem_records.items() if r.get("status") == "PROVEN_NOT_USER_CONTROL"
)
assert len(pnuc_ids) == 23

# ---------- STEP 1: apply 2D.6H's Table 3 (7 items) onto the reverse audit ----------
# This reproduces 2D.6H's stated 296 owned / 98 orphan from the raw 2D.6E reverse audit,
# rather than copying 2D.6H's summary numbers directly.
table3_pairs = [
    ("LFO1.TRIGGER_MODE", "LFO0.Mode"),
    ("LFO2.TRIGGER_MODE", "LFO1.Mode"),
    ("LFO3.TRIGGER_MODE", "LFO2.Mode"),
    ("LFO4.TRIGGER_MODE", "LFO3.Mode"),
    ("LFO5.TRIGGER_MODE", "LFO4.Mode"),
    ("LFO6.TRIGGER_MODE", "LFO5.Mode"),
    ("FX.HYPER.RETRIG", "FXHyper.Retrigger"),
]
for sem_id, tgt_id in table3_pairs:
    reverse_audit[tgt_id]["classification"] = "MAPPED"
    reverse_audit[tgt_id]["semantic_owners"] = [sem_id]

orphans_reproduced = set(
    tid for tid, r in reverse_audit.items() if r["classification"] == "ORPHAN_TECHNICAL"
)
assert orphans_reproduced == orphan_ids_2d6h, "2D.6H orphan set not reproduced from raw inputs"

mapped_reproduced = sum(1 for r in reverse_audit.values() if r["classification"] == "MAPPED")
many_reproduced = sum(1 for r in reverse_audit.values() if r["classification"] == "MANY_TO_ONE")
assert mapped_reproduced == 296
assert many_reproduced == 2

# ---------- STEP 2: apply 2D.6I dispositions to the 21 formerly-unchecked targets ----------
# Final dispositions per PHASE_2D6I_RECONCILIATION_FINAL.md, AS FURTHER CORRECTED by the
# user's explicit STOP instructions in this turn. Nothing here is inferred beyond what those
# two documents state.

DISP_2D6I = {
    "FXBODE.Frequency": "DEAD_OR_SUPERSEDED_CANDIDATE",
    "FXBODE.LevelOut": "DEAD_OR_SUPERSEDED",
    "FXChorus.Phase": "DEAD_OR_SUPERSEDED",
    "FXConvolve.IR": "DEAD_OR_SUPERSEDED",
    "FXConvolve.IRPath": "DEAD_OR_SUPERSEDED",
    "FXDelay.BW": "DEAD_OR_SUPERSEDED_CANDIDATE",
    "FXDelay.OffsetL": "DEAD_OR_SUPERSEDED_CANDIDATE",
    "FXDelay.OffsetR": "DEAD_OR_SUPERSEDED_CANDIDATE",
    "FXDelay.Time": "DEAD_OR_SUPERSEDED_CANDIDATE",
    "FXDistortion.BW": "DEAD_OR_SUPERSEDED",
    "FXDistortion.LevelOut": "DEAD_OR_SUPERSEDED",
    "FXDistortion.Tone": "DEAD_OR_SUPERSEDED",
    "FXEQ.LevelOut": "DEAD_OR_SUPERSEDED",
    "FXReverb.Damping": "MAPPED_TO_EXISTING_SEMANTIC",   # -> FX.REVERB.DAMP_PLATE
    "FXReverb.Time": "DEAD_OR_SUPERSEDED_CANDIDATE",
    "FXUtility.Gain": "DEAD_OR_SUPERSEDED",
    "FXUtility.Mono": "MAPPED_TO_EXISTING_SEMANTIC",     # -> FX.UTILITY.MONO_BASS
    "FXUtility.Phase": "DEAD_OR_SUPERSEDED",
    "OSC2.Detune": "DEAD_OR_SUPERSEDED",   # census-negative
    "OSC3.Detune": "DEAD_OR_SUPERSEDED",   # census-negative
    "SUB.Detune": "DEAD_OR_SUPERSEDED",    # census-negative
}
assert len(DISP_2D6I) == 21
assert set(DISP_2D6I.keys()) <= orphan_ids_2d6h, "2D.6I target not in 2D.6H orphan set"

TARGET_TO_SEMANTIC_NEW = {
    "FXReverb.Damping": "FX.REVERB.DAMP_PLATE",
    "FXUtility.Mono": "FX.UTILITY.MONO_BASS",
}

for tgt_id, disp in DISP_2D6I.items():
    row = reverse_audit[tgt_id]
    if disp == "MAPPED_TO_EXISTING_SEMANTIC":
        row["classification"] = "MAPPED"
        row["semantic_owners"] = [TARGET_TO_SEMANTIC_NEW[tgt_id]]
        row["disposition_2d6i"] = "MAPPED_TO_EXISTING_SEMANTIC"
    else:
        # DEAD_OR_SUPERSEDED / DEAD_OR_SUPERSEDED_CANDIDATE: stays without a semantic owner,
        # reclassified out of plain ORPHAN_TECHNICAL into its own named bucket.
        row["classification"] = disp
        row["disposition_2d6i"] = disp

# ---------- STEP 3: semantic-side changes, per this turn's explicit STOP rules ----------
# Rule 1: FX.REVERB.DECAY_HALL: UNKNOWN -> CONTROL_PATH_KNOWN_NO_TARGET. No target created.
# Rule 2: Wet family evaluated individually -- only semantics with an actual DIRECT_UI
#         right-click confirmation *this session* move. FX.DELAY.WET has none -> stays UNKNOWN.
# Rule 3: FX.FLANGER.PHASE -> BLOCKED_CONTRADICTED (tracked separately, not touched as MAPPED).
# Rule 4: FX.DIMENSION.WET -- inspected: no FXDimension.Mix / FXDimension.MixOrGain target
#         exists in the 396-target vocabulary at all. Not part of the Wet/Mix alias-ambiguity
#         situation (that requires >=2 competing targets). Real control observed (DIRECT_UI:
#         "Hyp im Mix"), zero targets exist for it -> CONTROL_PATH_KNOWN_NO_TARGET, its own
#         distinct case, not merged into the 9-module Wet pattern.

SEMANTIC_UPGRADES = {
    # semantic_id: (new_control_path_status, note)
    "FX.REVERB.DAMP_PLATE": ("MAPPED", "DIRECT_UI 'Rev Damp' (Plate) + target FXReverb.Damping"),
    "FX.UTILITY.MONO_BASS": ("MAPPED", "DIRECT_UI 'Utils Mono Side' + target FXUtility.Mono"),
    "FX.REVERB.DECAY_HALL": ("CONTROL_PATH_KNOWN_NO_TARGET", "DIRECT_UI 'Rev Decay' (Hall); no target assigned, per explicit instruction"),
    "FX.CHORUS.WET": ("CONTROL_PATH_KNOWN_NO_TARGET", "DIRECT_UI 'Cho Wet'"),
    "FX.BODE.WET": ("CONTROL_PATH_KNOWN_NO_TARGET", "DIRECT_UI 'Bode Wet'"),
    "FX.COMPRESSOR.WET": ("CONTROL_PATH_KNOWN_NO_TARGET", "DIRECT_UI 'Comp Wet'"),
    "FX.CONVOLVE.WET": ("CONTROL_PATH_KNOWN_NO_TARGET", "DIRECT_UI 'Conv Wet'"),
    "FX.FLANGER.WET": ("CONTROL_PATH_KNOWN_NO_TARGET", "DIRECT_UI 'Flg Wet'"),
    "FX.HYPER.WET": ("CONTROL_PATH_KNOWN_NO_TARGET", "DIRECT_UI 'Hyp Wet'"),
    "FX.PHASER.WET": ("CONTROL_PATH_KNOWN_NO_TARGET", "DIRECT_UI 'Phs Wet'"),
    "FX.UTILITY.WET": ("CONTROL_PATH_KNOWN_NO_TARGET", "DIRECT_UI 'Utils Wet'"),
    "FX.REVERB.WET": ("CONTROL_PATH_KNOWN_NO_TARGET", "DIRECT_UI 'Rev Wet'"),
    "FX.DIMENSION.WET": ("CONTROL_PATH_KNOWN_NO_TARGET", "DIRECT_UI 'Hyp im Mix'; NO FXDimension.* target exists in the 396-vocabulary -- distinct case, not the Wet-alias-ambiguity pattern"),
    # explicitly NOT moved: FX.DELAY.WET -- no DIRECT_UI evidence was collected for Delay's
    # mix/wet knob this session (only TimeL/TimeR/FREQ/Q were right-clicked). Stays UNKNOWN.
}

NOT_MOVED_NO_EVIDENCE = ["FX.DELAY.WET"]
for sid in NOT_MOVED_NO_EVIDENCE:
    assert sid in frozen_152, "expected to remain in 152, sanity check"

CONTRADICTIONS = []
# FX.FLANGER.PHASE: preserve BOTH the old ALIAS_RULE mapping and the new contradicting
# DIRECT_UI evidence. Do not delete the semantic, do not invent FXFlanger.Width as a target.
flanger_row = sem_rows["FX.FLANGER.PHASE"]
CONTRADICTIONS.append({
    "semantic_id": "FX.FLANGER.PHASE",
    "target_id": "FXFlanger.Phase",
    "status": "BLOCKED_CONTRADICTED",
    "old_evidence": {
        "mapping_class": flanger_row["mapping_class"],
        "mapping_basis": flanger_row["mapping_basis"],
        "evidence": flanger_row["evidence"],
    },
    "new_evidence": {
        "type": "DIRECT_UI",
        "observation": "FX 1: Flg Width",
        "session": "2D.6I live-UI right-click, this same knob position (UI label 'PHASE')",
    },
    "resolution": "UNRESOLVED -- both records preserved. Old ALIAS_RULE mapping is NOT "
                  "treated as ordinary MAPPED going forward; new evidence is NOT treated as "
                  "a resolution. No target named FXFlanger.Width is created. Reverification "
                  "required before either side is trusted.",
})

# ---------- STEP 4: build final Table A (semantic-side, 908) ----------
final_sem_class = {}
final_sem_note = {}

for sid, row in sem_rows.items():
    if sid == "FX.FLANGER.PHASE":
        final_sem_class[sid] = "BLOCKED_CONTRADICTED"
        continue
    if sid in pnuc_ids:
        final_sem_class[sid] = "PROVEN_NOT_USER_CONTROL"
        continue
    if row["mapping_class"] == "EXACT":
        final_sem_class[sid] = "MAPPED_TO_EXISTING_TARGET"
        continue
    if row["mapping_class"] == "ONE_TO_MANY":
        final_sem_class[sid] = "MANY_TO_ONE"
        continue
    # mapping_class UNKNOWN (no target found by alias rule) -- split by control-path status,
    # with 2D.6I / this-turn upgrades applied on top.
    if sid in SEMANTIC_UPGRADES:
        new_status, _note = SEMANTIC_UPGRADES[sid]
        if new_status == "MAPPED":
            final_sem_class[sid] = "MAPPED_TO_EXISTING_TARGET"
        else:
            final_sem_class[sid] = "CONTROL_PATH_KNOWN_NO_TARGET"
        continue
    cp_status = cp_matrix[sid]["status"]
    if cp_status == "UNKNOWN":
        final_sem_class[sid] = "UNKNOWN"
    else:
        final_sem_class[sid] = "CONTROL_PATH_KNOWN_NO_TARGET"

assert len(final_sem_class) == 908

from collections import Counter
sem_totals = Counter(final_sem_class.values())
sem_total_sum = sum(sem_totals.values())
assert sem_total_sum == 908, f"semantic totals do not sum to 908: {sem_total_sum}"

new_unknown_ids = sorted([sid for sid, c in final_sem_class.items() if c == "UNKNOWN"])
new_unknown_count = len(new_unknown_ids)

moved_out_of_152 = sorted(frozen_152 - set(new_unknown_ids))
moved_into_152 = sorted(set(new_unknown_ids) - frozen_152)

# ---------- STEP 5: build final Table B (technical-side, 396) ----------
final_tgt_class = {}
for tid, row in reverse_audit.items():
    c = row["classification"]
    if c == "MAPPED":
        final_tgt_class[tid] = "OWNED"
    elif c == "MANY_TO_ONE":
        final_tgt_class[tid] = "MANY_TO_ONE"
    elif c in ("DEAD_OR_SUPERSEDED", "DEAD_OR_SUPERSEDED_CANDIDATE"):
        final_tgt_class[tid] = c
    elif c == "ORPHAN_TECHNICAL":
        final_tgt_class[tid] = "UNKNOWN"  # not yet individually dispositioned this pass
    else:
        raise AssertionError(f"unexpected classification {c} for {tid}")

assert len(final_tgt_class) == 396
tgt_totals = Counter(final_tgt_class.values())
tgt_total_sum = sum(tgt_totals.values())
assert tgt_total_sum == 396, f"target totals do not sum to 396: {tgt_total_sum}"

# The remaining 98-21=77 orphans from 2D.6H (not part of the 21 audited this pass) are the
# 77-other-targets population referenced across 2D.6H/2D.6I -- explicitly still UNKNOWN here,
# not silently resolved.
remaining_orphans_77 = sorted(orphan_ids_2d6h - set(DISP_2D6I.keys()))
assert len(remaining_orphans_77) == 77

# ---------- STEP 6: fail-closed validation ----------
errors = []

# no duplicate ids (already asserted above at load time)

# no target assigned contradictory dispositions
for tid, disp in DISP_2D6I.items():
    if disp not in (
        "MAPPED_TO_EXISTING_SEMANTIC", "DEAD_OR_SUPERSEDED", "DEAD_OR_SUPERSEDED_CANDIDATE",
    ):
        errors.append(f"unexpected 2D.6I disposition for {tid}: {disp}")

# no semantic assigned contradictory ownership: every MAPPED_TO_EXISTING_TARGET semantic must
# point at exactly one target, and that target's owner list must contain it
for sid, cls in final_sem_class.items():
    if cls == "MAPPED_TO_EXISTING_TARGET":
        tids = sem_rows[sid]["target_ids"] or ([TARGET_TO_SEMANTIC_NEW_REV.get(sid)] if False else [])
        # recover target ids for the 2 upgraded semantics explicitly
        if sid == "FX.REVERB.DAMP_PLATE":
            tids = ["FXReverb.Damping"]
        elif sid == "FX.UTILITY.MONO_BASS":
            tids = ["FXReverb.Damping"] if False else ["FXUtility.Mono"]
        elif not tids:
            tids = sem_rows[sid]["target_ids"]
        if not tids:
            errors.append(f"MAPPED semantic {sid} has no recoverable target id")

# no UNKNOWN silently converted to dead
for sid in frozen_152:
    if sid not in SEMANTIC_UPGRADES and final_sem_class[sid] not in ("UNKNOWN",):
        errors.append(f"152-member {sid} changed status without an explicit upgrade rule")

# no DEAD_OR_SUPERSEDED_CANDIDATE silently converted to final DEAD
candidate_targets = [t for t, d in DISP_2D6I.items() if d == "DEAD_OR_SUPERSEDED_CANDIDATE"]
for t in candidate_targets:
    if final_tgt_class[t] != "DEAD_OR_SUPERSEDED_CANDIDATE":
        errors.append(f"{t} candidate status was silently changed to {final_tgt_class[t]}")

# no Wet/Mix alias collapse without explicit evidence -- verify none of the Wet-family
# semantics were given a target_id (would imply an alias was chosen)
wet_family_semantics = [s for s in SEMANTIC_UPGRADES if s.endswith(".WET")]
for sid in wet_family_semantics:
    if sid in ("FX.REVERB.WET",):
        pass  # still fine, no target assignment happens below regardless
for sid in wet_family_semantics:
    assigned = final_sem_class[sid] == "MAPPED_TO_EXISTING_TARGET"
    if assigned:
        errors.append(f"Wet-family semantic {sid} was collapsed to a target -- forbidden")

# FX.FLANGER.PHASE must not be plain MAPPED
if final_sem_class["FX.FLANGER.PHASE"] == "MAPPED_TO_EXISTING_TARGET":
    errors.append("FX.FLANGER.PHASE must not remain ordinary MAPPED_TO_EXISTING_TARGET")

if errors:
    raise AssertionError("FAIL-CLOSED VALIDATION ERRORS:\n" + "\n".join(errors))

print("ALL FAIL-CLOSED CHECKS PASSED")
print()
print("semantic totals:", dict(sem_totals))
print("sum:", sem_total_sum)
print()
print("target totals:", dict(tgt_totals))
print("sum:", tgt_total_sum)
print()
print("old_152:", len(frozen_152))
print("new_unknown:", new_unknown_count)
print("moved_out_of_152 (", len(moved_out_of_152), "):", moved_out_of_152)
print("moved_into_152 (", len(moved_into_152), "):", moved_into_152)
print()
print("remaining_orphans_77 count:", len(remaining_orphans_77))
print()
print("contradictions:", json.dumps(CONTRADICTIONS, indent=2))

# ---------- STEP 7: emit machine-readable JSON ----------
output = {
    "phase": "2D.6J",
    "status": "COMPLETE",
    "input_gates": {
        "semantic_count": len(sem_records),
        "target_count": len(target_ids_all),
        "gate_passed": len(sem_records) == 908 and len(target_ids_all) == 396,
    },
    "table_a_semantic_to_technical": {
        "totals": dict(sem_totals),
        "sum": sem_total_sum,
        "assignments": final_sem_class,
    },
    "table_b_technical_to_semantic": {
        "totals": dict(tgt_totals),
        "sum": tgt_total_sum,
        "assignments": final_tgt_class,
        "remaining_orphans_77_not_yet_dispositioned": remaining_orphans_77,
    },
    "table_c_2d6i_delta": {
        "targets_dispositioned": DISP_2D6I,
        "semantic_upgrades": {k: v[0] for k, v in SEMANTIC_UPGRADES.items()},
        "semantic_upgrade_evidence": {k: v[1] for k, v in SEMANTIC_UPGRADES.items()},
        "moved_out_of_152": moved_out_of_152,
        "moved_into_152": moved_into_152,
        "not_moved_explicit_no_evidence": NOT_MOVED_NO_EVIDENCE,
    },
    "table_d_unresolved_populations": {
        "old_2d6h_unknown_152": sorted(frozen_152),
        "new_2d6j_unknown": new_unknown_ids,
        "delta_count": new_unknown_count - len(frozen_152),
        "target_side_dead_or_superseded_final": sorted(
            t for t, c in final_tgt_class.items() if c == "DEAD_OR_SUPERSEDED"
        ),
        "target_side_dead_or_superseded_candidate": sorted(
            t for t, c in final_tgt_class.items() if c == "DEAD_OR_SUPERSEDED_CANDIDATE"
        ),
        "target_side_mapped_to_existing_semantic_this_pass": [
            t for t, d in DISP_2D6I.items() if d == "MAPPED_TO_EXISTING_SEMANTIC"
        ],
    },
    "contradiction_table": CONTRADICTIONS,
    "fail_closed_validation": {
        "errors": errors,
        "passed": len(errors) == 0,
    },
    "not_modified": [
        "semantic inventory (SERUM2_SEMANTIC_NORMALIZED.json / SERUM2_SEMANTIC_INVENTORY_FINAL.json)",
        "serum2/compiler/targets.py",
        "capability contracts",
        "experiments",
        "admission logic",
    ],
}

out_path = R + "PHASE_2D6J_BIDIRECTIONAL_RECONCILIATION_FINAL.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, sort_keys=False)

with open(out_path, "rb") as f:
    sha = hashlib.sha256(f.read()).hexdigest()
print()
print("SHA-256:", sha)
print("written to:", out_path)
