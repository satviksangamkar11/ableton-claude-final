#!/usr/bin/env python3
"""Deterministic UI-text bulk verifier for HOST_PARAMETER bindings.

    python -m serum2.verify.ui_bulk --all

One Serum session, one fixture load, every LIVE_VERIFIED HOST_PARAMETER
binding processed sequentially (never simultaneously -- a UI mismatch must
stay attributable to exactly one binding): mutate -> read Serum's own
displayed text -> [after all bindings] save once -> load a fresh/different
instance -> reload -> re-read text for every binding -> write local
evidence, print only the compact ledger and failures.

WHAT THIS PROVES, PRECISELY (read before treating this as equivalent to a
screenshot-based read):

  Every VST3 plugin, Serum included, must implement getParamStringByValue
  so the text a host displays for a parameter matches what the plugin's
  own GUI draws for that same parameter -- that is the whole point of the
  VST3 parameter-text API, and it is exactly what DawDreamer's
  get_parameters_description()[i]["currentValText"] returns. Confirmed
  live this session: "Filter 1 Var" at 0.66 -> "66", "Env 1 Attack" at 0.5
  -> "1.00 s", "Mono Toggle" at 1.0 -> "On", "LFO 1 Rate" at 0.3 ->
  "2 bar" -- these are exactly the strings the real Serum GUI shows next
  to those controls. This is real, deterministic, scriptable UI evidence,
  not a machine/CBOR-only round-trip and not a vision-model guess.

  It is still NOT a literal on-screen pixel read (that requires the
  agent-driven Ableton protocol used for the FX family's 11 UI_VERIFIED
  rows) and it does NOT cover BODY_STATE_FIELD bindings (FX_PARAMETER /
  direct CBOR paths like LFO's kParamDotted): those aren't real VST3
  parameters at all, so Serum never generates host-visible text for them,
  and there is no deterministic proxy for them in this codebase. Per
  CLAUDE.md's evidence-tier discipline, this result is reported as its
  OWN classification (UI_TEXT_VERIFIED), never collapsed into or
  reported as the agent-screenshot UI_VERIFIED tier.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import dawdreamer as daw

from serum2.evidence import epoch as epoch_mod
from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding
from serum2.verify import bulk as machine_bulk
from serum2.verify.classify import Classification, NEEDS_FOLLOWUP

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512
REPO_ROOT = Path(__file__).parent.parent.parent
DEFAULT_EVIDENCE_ROOT = REPO_ROOT / "evidence" / "ui_bulk"


class UIClassification:
    """UI-tier statuses -- kept a distinct vocabulary from classify.py's
    Classification (machine tier) so the two are never conflated in
    output or in the registry. UI_TEXT_VERIFIED is intentionally not
    named UI_VERIFIED -- see module docstring."""
    UI_TEXT_VERIFIED = "UI_TEXT_VERIFIED"
    UI_TEXT_MISMATCH = "UI_TEXT_MISMATCH"
    UI_TEXT_UNREADABLE = "UI_TEXT_UNREADABLE"
    NO_DETERMINISTIC_UI_PROXY = "NO_DETERMINISTIC_UI_PROXY"
    FORENSIC_REQUIRED = "FORENSIC_REQUIRED"


def _engine():
    engine = daw.RenderEngine(SR, BLOCK)
    return engine, engine.make_plugin_processor("serum", VST3)


def _settle(engine, synth):
    engine.load_graph([(synth, [])])
    engine.render(BLOCK / SR)


def _make_contract(param_name: str) -> CapabilityContract:
    binding = ExecutionBinding(mutation_type="HOST_PARAMETER", host_parameter_name=param_name,
                                binding_source="verify.ui_bulk", binding_version="1.0")
    return CapabilityContract(target="T", allowed_operation="mutate_numeric_value",
                               status="CAUSAL_VERIFIED", prerequisites=(), verified={},
                               measurement=None, scope={}, provenance={},
                               execution_binding=binding, limitations=())


def run_host_parameter_ui_batch(entries: List[dict]) -> Dict[str, dict]:
    """Per CLAUDE.md's single-field-isolation epistemic rule: each binding
    gets its OWN fresh engine/synth for its mutate -> UI_AFTER -> save ->
    fresh-instance-reload -> UI_RELOADED cycle. An earlier attempt shared
    one synth instance across all 168 bindings before a single save/reload
    and produced 7 apparent anomalies; isolating 4 of them individually
    showed 2 were pure cross-parameter display confounds (a batch-testing
    artifact, not a real defect) -- exactly the uncontrolled-experiment
    trap this rule exists to catch. Slower (one engine per binding) but
    the only way to keep every result attributable to exactly one
    binding, and still fully scripted -- no agent/UI involvement."""
    results: Dict[str, dict] = {}
    probe_engine, probe_synth = _engine()
    probe_params = {p["name"]: p for p in probe_synth.get_parameters_description()}

    for e in entries:
        cid = e["capability_id"]
        name = e["authoritative_binding"]["parameter_name"]
        meta = probe_params.get(name)
        if meta is None:
            results[cid] = {"classification": UIClassification.UI_TEXT_UNREADABLE,
                             "detail": f"host parameter not in live VST3 list: {name!r}"}
            continue
        probes = machine_bulk.host_param_probes(meta)
        if probes is None:
            results[cid] = {"classification": UIClassification.UI_TEXT_UNREADABLE,
                             "detail": "could not generate a legal probe"}
            continue
        probe = probes[0]

        engine, synth = _engine()
        idx = meta["index"]
        before_text = synth.get_parameters_description()[idx]["text"]
        contract = _make_contract(name)
        request = MutationRequest(target="T", mutation_type=MutationType.HOST_PARAMETER, value=probe,
                                   host_parameter_name=name)
        proof = execute_mutation_request_with_authority(request=request, body={},
                                                          contracts={("T", ""): contract}, synth=synth)
        if not proof.executed:
            results[cid] = {"classification": UIClassification.UI_TEXT_UNREADABLE, "detail": proof.detail}
            continue
        _settle(engine, synth)
        after_text = synth.get_parameters_description()[idx]["currentValText"]

        fd, tmp = tempfile.mkstemp(suffix=".bin"); os.close(fd)
        synth.save_state(tmp)
        engine2, synth2 = _engine()
        synth2.load_state(tmp)
        os.remove(tmp)
        reloaded_text = synth2.get_parameters_description()[idx]["currentValText"]

        record = {"before_text": before_text, "ui_after_text": after_text,
                  "ui_reloaded_text": reloaded_text, "probe": probe}
        if after_text != before_text and after_text == reloaded_text:
            record["classification"] = UIClassification.UI_TEXT_VERIFIED
        elif after_text == before_text:
            record["classification"] = UIClassification.FORENSIC_REQUIRED
            record["detail"] = (f"displayed text did not change: before={before_text!r}, after={after_text!r} "
                                 f"-- may require a prerequisite context (e.g. a linked mode/type parameter) "
                                 f"not set in this bare-skeleton fixture")
        else:
            record["classification"] = UIClassification.FORENSIC_REQUIRED
            record["detail"] = (f"displayed text changed but did not survive reload: "
                                 f"after={after_text!r}, reloaded={reloaded_text!r}")
        results[cid] = record

    return results



def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true", help="run every LIVE_VERIFIED binding")
    ap.add_argument("--evidence", type=str, default=None)
    args = ap.parse_args(argv)

    registry = machine_bulk.load_registry()
    queue = machine_bulk.build_queue(registry)

    results: Dict[str, dict] = {}
    host_entries = [e for e in queue.values()
                    if e["execution_family"] == "HOST_PARAMETER" and e["binding_status"] == "LIVE_VERIFIED"]
    non_host_live = [e for e in queue.values()
                      if e["execution_family"] != "HOST_PARAMETER" and e["binding_status"] == "LIVE_VERIFIED"]
    not_live = [e for e in queue.values() if e["binding_status"] != "LIVE_VERIFIED"]

    print(f"HOST_PARAMETER (deterministic UI-text tier available): {len(host_entries)}")
    results.update(run_host_parameter_ui_batch(host_entries))

    for e in non_host_live:
        results[e["capability_id"]] = {
            "classification": UIClassification.NO_DETERMINISTIC_UI_PROXY,
            "detail": (f"binding_type={e['authoritative_binding'].get('binding_type')}: not a real VST3 "
                       f"parameter, so Serum generates no host-visible display text for it; requires the "
                       f"agent-driven Ableton visual-read protocol (as already done for the 11 FX rows), "
                       f"not this deterministic tool."),
        }
    for e in not_live:
        results[e["capability_id"]] = {"classification": Classification.NOT_EXECUTABLE,
                                        "detail": f"binding_status={e['binding_status']}"}

    run_id = time.strftime("%Y%m%d_%H%M%S")
    evidence_dir = Path(args.evidence) if args.evidence else (DEFAULT_EVIDENCE_ROOT / run_id)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    status_counts: Dict[str, int] = {}
    records = []
    forensic_queue = []
    for cid, entry in queue.items():
        r = results.get(cid, {"classification": Classification.NOT_EXECUTABLE, "detail": "not attempted"})
        cls = r["classification"]
        status_counts[cls] = status_counts.get(cls, 0) + 1
        record = {"capability_id": cid, "execution_family": entry["execution_family"],
                   "authoritative_binding": entry["authoritative_binding"],
                   "semantic_ids": entry["semantic_ids"], **{k: v for k, v in r.items() if k != "classification"},
                   "classification": cls, "timestamp": time.time()}
        records.append(record)
        if cls in (UIClassification.UI_TEXT_MISMATCH, UIClassification.UI_TEXT_UNREADABLE,
                   UIClassification.FORENSIC_REQUIRED):
            forensic_queue.append(record)

    with open(evidence_dir / "results.jsonl", "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    with open(evidence_dir / "forensic_queue.json", "w", encoding="utf-8") as f:
        json.dump(forensic_queue, f, indent=2)
    summary = {"unique_capability_count": len(queue), "status_counts": status_counts,
               "forensic_count": len(forensic_queue)}
    with open(evidence_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nTOTAL: {summary['unique_capability_count']}")
    for status, count in sorted(status_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {status:32s} {count}")
    if forensic_queue:
        print(f"\n{len(forensic_queue)} need follow-up -- see {evidence_dir / 'forensic_queue.json'}")
        for r in forensic_queue[:10]:
            print(f"  [{r['classification']}] {r['capability_id']}  {r['authoritative_binding']}  {r.get('detail','')}")
    print(f"\nEvidence: {evidence_dir}")
    return 0 if not forensic_queue else 1


if __name__ == "__main__":
    sys.exit(main())
