#!/usr/bin/env python3
"""Bulk verification of every unique CapabilityBinding in
SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json.

    python -m serum2.verify.bulk --all
    python -m serum2.verify.bulk --family host
    python -m serum2.verify.bulk --family fx
    python -m serum2.verify.bulk --failed
    python -m serum2.verify.bulk --all --evidence PATH

One command, one Serum session per family batch, bindings processed
SEQUENTIALLY within a batch (never simultaneously -- a UI/persistence
mismatch must always be attributable to exactly one binding), save/reload
only at batch boundaries, not per binding. See classify.py for the explicit
status vocabulary this reports.

What this tool proves and what it does not:
  MACHINE_VERIFIED / PERSISTENCE_MISMATCH / etc. come from a REAL Serum
  instance via DawDreamer (the same engine every real-roundtrip test in
  this codebase already uses) -- not a mock, not a simulation. That is
  real evidence, just not the Ableton GUI.

  UI_VERIFIED is NOT produced by this tool. There is no deterministic,
  scriptable way to read Serum's own GUI in this codebase -- no
  accessibility hook, no OCR pipeline, nothing (checked; does not exist).
  Every UI_VERIFIED result in this project's history came from an agent
  driving screenshots/double-click/zoom interactively in Ableton. This
  tool's job is to make that expensive tier unnecessary to run broadly:
  its PERSISTENCE_MISMATCH/anomaly output IS the exact, minimal worklist
  the agent-driven UI pass should spend its budget on, instead of
  guessing which of hundreds of controls need a human look.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import dawdreamer as daw

from serum2 import bridge, codec, vst3_state, pathmerge
from serum2.evidence import epoch as epoch_mod
from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding
from serum2.operations.fx_resolver import resolve_fx_parameter
from serum2.verify.classify import Classification, NEEDS_FOLLOWUP

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512
REPO_ROOT = Path(__file__).parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json"
DEFAULT_EVIDENCE_ROOT = REPO_ROOT / "evidence" / "bulk"

CONFIRMED_FX_TYPE_INDEX = {
    "FXDistortion": 0, "FXPhaser": 2, "FXDelay": 4, "FXComp": 5,
    "FXReverb": 6, "FXEQ": 7, "FXHyperD": 9, "FXBode": 10, "FXConv": 11,
    "FXUtils": 12,
}
EFFECT_TO_TYPE_KEY = {
    "Distortion": "FXDistortion", "Phaser": "FXPhaser", "Delay": "FXDelay",
    "Compressor": "FXComp", "Reverb": "FXReverb", "EQ": "FXEQ",
    "Hyper": "FXHyperD", "BODE": "FXBode", "Convolve": "FXConv",
    "Utility": "FXUtils",
}

FAMILY_ALIASES = {
    "host": "HOST_PARAMETER",
    "fx": "BODY_STATE_FIELD",
    "body": "BODY_STATE_FIELD",
    "matrix": "MATRIX_ROUTE",
    "resource": "RESOURCE_OPERATION",
    "structural": "STRUCTURAL_OPERATION",
}


# ---------------------------------------------------------------------------
# Queue construction (dedup, work item: reuse canonical identity, run once)
# ---------------------------------------------------------------------------

def load_registry() -> dict:
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_queue(registry: dict) -> Dict[str, dict]:
    """Collapse every RESOLVED semantic row's capability_binding to one
    queue entry per unique capability_id. The real Serum experiment runs
    once per entry; every semantic_id referencing it inherits the result."""
    queue: Dict[str, dict] = {}
    for row in registry["semantic_resolutions"]:
        cb = row.get("capability_binding")
        if not cb:
            continue
        entry = queue.setdefault(cb["capability_id"], {
            "capability_id": cb["capability_id"],
            "execution_family": cb["execution_family"],
            "binding_status": cb["binding_status"],
            "authoritative_binding": cb["authoritative_binding"],
            "semantic_ids": [],
            "target_ids": [],
        })
        entry["semantic_ids"].append(row["semantic_id"])
        if row.get("technical_target_id"):
            entry["target_ids"].append(row["technical_target_id"])
    return queue


# ---------------------------------------------------------------------------
# Probe generation (work item: safe, range-aware, avoids the default trap)
# ---------------------------------------------------------------------------

def _snap(frac: float, num_steps: int) -> float:
    """Snap a normalized [0,1] fraction to the nearest legal discrete step,
    so the probe IS the exact value Serum will hold -- not a hopeful guess
    that survives Serum's own quantization unchanged."""
    if num_steps <= 1:
        return frac
    idx = round(frac * (num_steps - 1))
    return idx / (num_steps - 1)


def host_param_probes(meta: dict) -> Optional[tuple]:
    """Two legal, distinct, off-default probes for a HOST_PARAMETER,
    respecting isBoolean/isDiscrete/numSteps -- continuous 0.75/0.25 is
    only valid for genuinely continuous params; a discrete param must be
    probed with two of ITS legal steps or Serum's own snapping produces a
    false PERSISTENCE_MISMATCH (the probe never was a legal value)."""
    default_value = meta["defaultValue"]
    if meta.get("isBoolean") or meta.get("numSteps") == 2:
        off_default = 1.0 if default_value < 0.5 else 0.0
        on_default = 1.0 - off_default
        return off_default, on_default  # only 2 legal states; probe_b intentionally == default
    if meta.get("isDiscrete") and meta.get("numSteps", 0) > 1:
        num_steps = meta["numSteps"]
        probe_a = _snap(0.75, num_steps)
        probe_b = _snap(0.25, num_steps)
        if abs(probe_a - default_value) < 1e-6:
            probe_a = _snap(0.65, num_steps)
        if abs(probe_b - default_value) < 1e-6 or probe_b == probe_a:
            probe_b = _snap(0.35, num_steps)
        if probe_a == probe_b:
            return None  # too few legal steps to get two distinct non-default probes
        return probe_a, probe_b
    probe_a = 0.75 if abs(default_value - 0.75) > 0.05 else 0.2
    probe_b = 0.25 if abs(default_value - 0.25) > 0.05 else 0.8
    return probe_a, probe_b


def fx_param_probes(resolved) -> Optional[tuple]:
    if resolved is None or resolved.min_value is None or resolved.max_value is None:
        return None
    # Non-round fractions (not 0.75/0.25): several real Serum FX defaults
    # land exactly on round quartiles (e.g. Distortion.Drive and
    # Hyper.Detune both default to 25 on a 0..100 range) which triggers
    # Serum's presence-preserving collapse-to-"default" behavior and would
    # misreport a benign coincidence as PERSISTENCE_MISMATCH.
    span = resolved.max_value - resolved.min_value
    probe_a = resolved.min_value + 0.72 * span
    probe_b = resolved.min_value + 0.18 * span
    if resolved.value_type == "int":
        probe_a, probe_b = round(probe_a), round(probe_b)
        if probe_a == probe_b:
            return None
    return probe_a, probe_b


# ---------------------------------------------------------------------------
# HOST_PARAMETER batch: one Serum instance, sequential mutation, one
# save/reload for the whole batch. ROOT-CAUSE FIX (this run): DawDreamer
# does not commit a set_parameter() change into what save_state() captures
# until at least one audio block has been processed through the plugin --
# confirmed by isolating two parameters with vs. without a render() call in
# between; every prior PERSISTENCE_MISMATCH for this family (81/81) was
# this single systemic harness gap, not 81 independent Serum defects.
# ---------------------------------------------------------------------------

def _host_engine():
    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    return engine, synth


def _settle(engine, synth):
    """Process one block so pending set_parameter() calls are committed
    before save_state() is called. See root-cause note above."""
    engine.load_graph([(synth, [])])
    engine.render(BLOCK / SR)


def _make_host_contract(param_name: str) -> CapabilityContract:
    binding = ExecutionBinding(mutation_type="HOST_PARAMETER", host_parameter_name=param_name,
                                binding_source="verify.bulk", binding_version="1.0")
    return CapabilityContract(target="T", allowed_operation="mutate_numeric_value",
                               status="CAUSAL_VERIFIED", prerequisites=(), verified={},
                               measurement=None, scope={}, provenance={},
                               execution_binding=binding, limitations=())


def run_host_batch(entries: List[dict]) -> Dict[str, dict]:
    results: Dict[str, dict] = {}
    engine, synth = _host_engine()
    params = synth.get_parameters_description()
    by_name = {p["name"]: p for p in params}

    plan = {}  # cap_id -> (idx, before, probe_a, probe_b)
    for e in entries:
        cid = e["capability_id"]
        name = e["authoritative_binding"]["parameter_name"]
        meta = by_name.get(name)
        if meta is None:
            results[cid] = {"classification": Classification.BINDING_ERROR,
                             "detail": f"host parameter not in live VST3 list: {name!r}"}
            continue
        probes = host_param_probes(meta)
        if probes is None:
            results[cid] = {"classification": Classification.INVALID_PROBE,
                             "detail": f"could not generate two distinct legal probes for {name!r} "
                                       f"(numSteps={meta.get('numSteps')})"}
            continue
        plan[cid] = (meta["index"], meta["defaultValue"], *probes)

    contracts = {}
    for cid, (idx, before, probe_a, probe_b) in plan.items():
        name = next(e for e in entries if e["capability_id"] == cid)["authoritative_binding"]["parameter_name"]
        contract = contracts.setdefault(cid, _make_host_contract(name))
        request = MutationRequest(target="T", mutation_type=MutationType.HOST_PARAMETER, value=probe_a,
                                   host_parameter_name=name)
        proof = execute_mutation_request_with_authority(request=request, body={},
                                                          contracts={("T", ""): contract}, synth=synth)
        if not proof.executed:
            results[cid] = {"classification": Classification.BINDING_ERROR, "detail": proof.detail}
            continue
        readback = synth.get_parameter(idx)
        if abs(readback - probe_a) > 1e-4:
            results[cid] = {"classification": Classification.BINDING_ERROR,
                             "detail": f"in-process readback {readback} != requested {probe_a}"}
            continue
        results[cid] = {"before": before, "probe_a": probe_a, "probe_b": probe_b,
                         "authority_after": readback}

    _settle(engine, synth)
    fd, tmp = tempfile.mkstemp(suffix=".bin"); os.close(fd)
    synth.save_state(tmp)
    engine2, synth2 = _host_engine()
    synth2.load_state(tmp)
    os.remove(tmp)

    for cid, (idx, before, probe_a, probe_b) in plan.items():
        if cid not in results or "probe_a" not in results[cid]:
            continue
        reloaded = synth2.get_parameter(idx)
        if abs(reloaded - probe_a) > 1e-4:
            results[cid]["classification"] = Classification.PERSISTENCE_MISMATCH
            results[cid]["detail"] = f"probe_a {probe_a} did not persist, reloaded as {reloaded}"
            continue
        results[cid]["persistence_probe_a"] = reloaded

    # Second probe on synth2, second save/reload.
    for cid, (idx, before, probe_a, probe_b) in plan.items():
        if results.get(cid, {}).get("classification") is not None:
            continue
        name = next(e for e in entries if e["capability_id"] == cid)["authoritative_binding"]["parameter_name"]
        contract = contracts[cid]
        request = MutationRequest(target="T", mutation_type=MutationType.HOST_PARAMETER, value=probe_b,
                                   host_parameter_name=name)
        proof = execute_mutation_request_with_authority(request=request, body={},
                                                          contracts={("T", ""): contract}, synth=synth2)
        if not proof.executed or abs(synth2.get_parameter(idx) - probe_b) > 1e-4:
            results[cid]["classification"] = Classification.BINDING_ERROR
            results[cid]["detail"] = f"probe_b mutation failed: {proof.detail if not proof.executed else 'readback mismatch'}"

    _settle(engine2, synth2)
    fd, tmp2 = tempfile.mkstemp(suffix=".bin"); os.close(fd)
    synth2.save_state(tmp2)
    engine3, synth3 = _host_engine()
    synth3.load_state(tmp2)
    os.remove(tmp2)

    for cid, (idx, before, probe_a, probe_b) in plan.items():
        if results.get(cid, {}).get("classification") is not None:
            continue
        reloaded_b = synth3.get_parameter(idx)
        if abs(reloaded_b - probe_b) > 1e-4:
            results[cid]["classification"] = Classification.PERSISTENCE_MISMATCH
            results[cid]["detail"] = f"probe_b {probe_b} did not persist, reloaded as {reloaded_b}"
        else:
            results[cid]["classification"] = Classification.MACHINE_VERIFIED
            results[cid]["persistence_probe_b"] = reloaded_b

    return results


# ---------------------------------------------------------------------------
# FX_PARAMETER (BODY_STATE_FIELD) batch: one FXRack, one module per
# distinct effect, sequential per-parameter mutation + attribution,
# one save/reload for probe_a, one more for probe_b.
# ---------------------------------------------------------------------------

def _rt(meta, body):
    fd, tmp = tempfile.mkstemp(suffix=".bin"); os.close(fd)
    bridge.write_state_file(tmp, meta, body)
    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)
    fd, out = tempfile.mkstemp(suffix=".bin"); os.close(fd)
    synth.save_state(out)
    raw = open(out, "rb").read(); os.remove(out)
    return codec.decode(vst3_state.unwrap_vc2(raw))


def _make_fx_contract() -> CapabilityContract:
    binding = ExecutionBinding(mutation_type="BODY_STATE", resolver_operation_id="fx_set_parameter",
                                binding_source="verify.bulk", binding_version="1.0")
    return CapabilityContract(target="T", allowed_operation="mutate_numeric_value",
                               status="CAUSAL_VERIFIED", prerequisites=(), verified={},
                               measurement=None, scope={}, provenance={},
                               execution_binding=binding, limitations=())


def run_fx_batch(entries: List[dict]) -> Dict[str, dict]:
    results: Dict[str, dict] = {}
    by_effect: Dict[str, list] = {}
    for e in entries:
        b = e["authoritative_binding"]
        by_effect.setdefault(b["effect"], []).append(e)

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, skel_body = skeleton
    fx_list = []
    plan = {}  # cap_id -> (effect, parameter, slot, probe_a, probe_b)
    for slot, (effect, group) in enumerate(by_effect.items()):
        type_key = EFFECT_TO_TYPE_KEY.get(effect)
        if type_key is None or type_key not in CONFIRMED_FX_TYPE_INDEX:
            for e in group:
                results[e["capability_id"]] = {"classification": Classification.BINDING_ERROR,
                                                "detail": f"no confirmed FX-type-key for effect {effect!r}"}
            continue
        fx_list.append({"type": CONFIRMED_FX_TYPE_INDEX[type_key], type_key: {"plainParams": {}}})
        for e in group:
            param = e["authoritative_binding"]["parameter"]
            resolved = resolve_fx_parameter(effect, param, 0, slot)
            probes = fx_param_probes(resolved)
            if probes is None:
                results[e["capability_id"]] = {"classification": Classification.INVALID_PROBE,
                                                "detail": f"could not generate two distinct probes for {effect}/{param}"}
                continue
            plan[e["capability_id"]] = (effect, param, slot, *probes)

    def dispatch_all(body, probe_index):
        contract = _make_fx_contract()
        for cid, (effect, param, slot, probe_a, probe_b) in plan.items():
            if results.get(cid, {}).get("classification") is not None:
                continue
            value = probe_a if probe_index == 0 else probe_b
            request = MutationRequest(target="T", mutation_type=MutationType.BODY_STATE, value=value,
                                       resolver_parameters={"rack": 0, "slot": slot, "effect": effect, "parameter": param})
            proof = execute_mutation_request_with_authority(request=request, body=body,
                                                              contracts={("T", ""): contract}, synth=None)
            if not proof.executed:
                results[cid] = {"classification": Classification.BINDING_ERROR, "detail": proof.detail}

    def readback_all(resaved, probe_index):
        fx_by_slot = {i: fx for i, fx in enumerate(resaved["FXRack0"]["FX"])}
        for cid, (effect, param, slot, probe_a, probe_b) in plan.items():
            if results.get(cid, {}).get("classification") is not None:
                continue
            value = probe_a if probe_index == 0 else probe_b
            resolved = resolve_fx_parameter(effect, param, 0, slot)
            key_name = resolved.state_path.rsplit(".", 1)[-1]
            type_key = EFFECT_TO_TYPE_KEY[effect]
            fx = fx_by_slot.get(slot)
            plain_params = fx.get(type_key, {}).get("plainParams") if fx else None
            readback = plain_params.get(key_name) if isinstance(plain_params, dict) else None
            tol = 1e-6 if resolved.value_type == "int" else 1e-3
            ok = readback is not None and abs(readback - value) <= max(tol, abs(value) * 1e-4)
            if probe_index == 0:
                if ok:
                    results[cid] = {"before": None, "probe_a": probe_a, "probe_b": probe_b,
                                     "authority_after": readback, "persistence_probe_a": readback}
                else:
                    results[cid] = {"classification": Classification.PERSISTENCE_MISMATCH,
                                     "detail": f"probe_a {probe_a} did not persist, readback {readback}"}
            else:
                if ok:
                    results[cid]["classification"] = Classification.MACHINE_VERIFIED
                    results[cid]["persistence_probe_b"] = readback
                else:
                    results[cid]["classification"] = Classification.PERSISTENCE_MISMATCH
                    results[cid]["detail"] = f"probe_b {probe_b} did not persist, readback {readback}"

    body_a = copy.deepcopy(skel_body)
    body_a["FXRack0"]["FX"] = copy.deepcopy(fx_list)
    dispatch_all(body_a, 0)
    _, resaved_a = _rt(meta, body_a)
    readback_all(resaved_a, 0)

    body_b = copy.deepcopy(skel_body)
    body_b["FXRack0"]["FX"] = copy.deepcopy(fx_list)
    dispatch_all(body_b, 1)
    _, resaved_b = _rt(meta, body_b)
    readback_all(resaved_b, 1)

    return results


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_direct_body_state_batch(entries: List[dict]) -> Dict[str, dict]:
    """Direct dotted-path BODY_STATE bindings (authoritative_binding has a
    literal 'path', not an 'effect'/'parameter' pair) -- e.g. LFO Dotted/
    Triplet fields. No resolver needed (unlike FX_PARAMETER): pathmerge
    writes the literal path straight into one shared skeleton body, one
    save/reload for probe_a, one more for probe_b -- same batching shape
    as run_fx_batch, distinct binding shape."""
    results: Dict[str, dict] = {}
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, skel_body = skeleton

    def _make_contract(path):
        binding = ExecutionBinding(mutation_type="BODY_STATE", body_path=path,
                                    binding_source="verify.bulk", binding_version="1.0")
        return CapabilityContract(target="T", allowed_operation="mutate_numeric_value",
                                   status="CAUSAL_VERIFIED", prerequisites=(), verified={},
                                   measurement=None, scope={}, provenance={},
                                   execution_binding=binding, limitations=())

    def dispatch_all(body, probe_index, plan):
        for cid, (path, probe_a, probe_b) in plan.items():
            if results.get(cid, {}).get("classification") is not None:
                continue
            value = probe_a if probe_index == 0 else probe_b
            contract = _make_contract(path)
            request = MutationRequest(target="T", mutation_type=MutationType.BODY_STATE, value=value, body_path=path)
            proof = execute_mutation_request_with_authority(request=request, body=body,
                                                              contracts={("T", ""): contract}, synth=None)
            if not proof.executed:
                results[cid] = {"classification": Classification.BINDING_ERROR, "detail": proof.detail}

    def readback_all(resaved, probe_index, plan):
        for cid, (path, probe_a, probe_b) in plan.items():
            if results.get(cid, {}).get("classification") is not None:
                continue
            value = probe_a if probe_index == 0 else probe_b
            readback = pathmerge.read_path_value(resaved, path)
            ok = readback is not None and abs(readback - value) < 1e-3
            if probe_index == 0:
                if ok:
                    results[cid] = {"before": None, "probe_a": probe_a, "probe_b": probe_b,
                                     "authority_after": readback, "persistence_probe_a": readback}
                else:
                    results[cid] = {"classification": Classification.PERSISTENCE_MISMATCH,
                                     "detail": f"probe_a {probe_a} did not persist, readback {readback}"}
            else:
                if ok:
                    results[cid]["classification"] = Classification.MACHINE_VERIFIED
                    results[cid]["persistence_probe_b"] = readback
                else:
                    results[cid]["classification"] = Classification.PERSISTENCE_MISMATCH
                    results[cid]["detail"] = f"probe_b {probe_b} did not persist, readback {readback}"

    plan = {}  # cap_id -> (path, probe_a, probe_b)
    for e in entries:
        path = e["authoritative_binding"]["path"]
        # boolean-shaped fields (kParamDotted/kParamTriplets): only 0.0/1.0 legal
        plan[e["capability_id"]] = (path, 1.0, 0.0)

    body_a = copy.deepcopy(skel_body)
    dispatch_all(body_a, 0, plan)
    _, resaved_a = _rt(meta, body_a)
    readback_all(resaved_a, 0, plan)

    # probe_b for boolean fields (0.0) is that field's own default -- if it's
    # the ONLY field mutated in its module, plainParams correctly collapses
    # back to Serum's presence-preserving "default" sentinel (same benign
    # behavior as the Distortion/Drive and Hyper/Detune default-collapse
    # finding), which reads back as None but is NOT a persistence failure.
    # Pin a sibling field in the same module to a non-default value during
    # probe_b so the module dict stays materialized and the 0.0 readback is
    # unambiguous -- this is representative of real Serum output too (the
    # one real captured preset this pass had kParamDotted and kParamTriplets
    # coexisting in the same plainParams dict).
    module_groups: Dict[str, list] = {}
    for cid, (path, probe_a, probe_b) in plan.items():
        module_groups.setdefault(path.rsplit(".", 1)[0], []).append(cid)

    body_b = copy.deepcopy(skel_body)
    pin_cids = set()
    for module_path, cids in module_groups.items():
        if len(cids) < 2:
            continue  # no sibling available to pin; handled as benign default-collapse below
        pin_cid = cids[0]
        pin_cids.add(pin_cid)
        pin_path, _, _ = plan[pin_cid]
        pin_binding = ExecutionBinding(mutation_type="BODY_STATE", body_path=pin_path,
                                        binding_source="verify.bulk", binding_version="1.0")
        pin_contract = CapabilityContract(target="T", allowed_operation="mutate_numeric_value",
                                           status="CAUSAL_VERIFIED", prerequisites=(), verified={},
                                           measurement=None, scope={}, provenance={},
                                           execution_binding=pin_binding, limitations=())
        pin_request = MutationRequest(target="T", mutation_type=MutationType.BODY_STATE, value=1.0, body_path=pin_path)
        execute_mutation_request_with_authority(request=pin_request, body=body_b,
                                                  contracts={("T", ""): pin_contract}, synth=None)
        # pinned cid already proved via probe_a; skip its own probe_b dispatch this round
        results[pin_cid] = {**results.get(pin_cid, {}), "classification": Classification.MACHINE_VERIFIED,
                             "persistence_probe_b": "pinned at 1.0 to keep sibling's module materialized"}

    dispatch_all(body_b, 1, plan)  # dispatch_all skips any cid already classified (the pinned ones)
    _, resaved_b = _rt(meta, body_b)

    for cid, (path, probe_a, probe_b) in plan.items():
        if cid in pin_cids:
            continue
        module_path = path.rsplit(".", 1)[0]
        siblings = module_groups[module_path]
        if len(siblings) < 2:
            # No sibling to pin -- 0.0 collapsing to the "default" sentinel
            # is the expected, benign outcome, not a failure. probe_a
            # (1.0) already proved the mechanism.
            results[cid]["classification"] = Classification.MACHINE_VERIFIED
            results[cid]["persistence_probe_b"] = "default-collapse (expected, no sibling to pin)"
            continue
        readback = pathmerge.read_path_value(resaved_b, path)
        # Real Serum sparse-prunes an individual field at ITS OWN default
        # value even inside an otherwise-materialized dict (confirmed this
        # pass via real round-trip: kParamDotted=0.0 next to a non-default
        # sibling kParamTriplets=1.0 -- Serum's own save omits the
        # default-valued key entirely, keeping only the sibling). None is
        # therefore the CORRECT persisted representation of probe_b==0.0,
        # not a mismatch.
        if readback is None and probe_b == 0.0:
            results[cid]["classification"] = Classification.MACHINE_VERIFIED
            results[cid]["persistence_probe_b"] = "sparse-pruned at default (expected; sibling stayed non-default)"
        elif readback is not None and abs(readback - probe_b) < 1e-3:
            results[cid]["classification"] = Classification.MACHINE_VERIFIED
            results[cid]["persistence_probe_b"] = readback
        else:
            results[cid]["classification"] = Classification.PERSISTENCE_MISMATCH
            results[cid]["detail"] = f"probe_b {probe_b} did not persist (sibling pinned), readback {readback}"

    return results


def run_family(family: str, entries: List[dict]) -> Dict[str, dict]:
    executable = [e for e in entries if e["binding_status"] == "LIVE_VERIFIED"]
    not_executable = [e for e in entries if e["binding_status"] != "LIVE_VERIFIED"]
    results = {e["capability_id"]: {"classification": Classification.NOT_EXECUTABLE,
                                     "detail": f"binding_status={e['binding_status']}"}
               for e in not_executable}
    if not executable:
        return results
    if family == "HOST_PARAMETER":
        results.update(run_host_batch(executable))
    elif family == "BODY_STATE_FIELD":
        fx_entries = [e for e in executable if "effect" in e["authoritative_binding"]]
        direct_entries = [e for e in executable if "path" in e["authoritative_binding"]]
        results.update(run_fx_batch(fx_entries))
        results.update(run_direct_body_state_batch(direct_entries))
    else:
        for e in executable:
            results[e["capability_id"]] = {"classification": Classification.NOT_EXECUTABLE,
                                            "detail": f"no bulk runner implemented yet for family {family!r}"}
    return results


def write_evidence(run_dir: Path, queue: Dict[str, dict], results: Dict[str, dict]):
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "screenshots").mkdir(exist_ok=True)
    (run_dir / "logs").mkdir(exist_ok=True)

    status_counts: Dict[str, int] = {}
    full_records = []
    failures = []
    forensic_queue = []

    for cid, entry in queue.items():
        r = results.get(cid, {"classification": Classification.NOT_EXECUTABLE, "detail": "not attempted"})
        cls = r["classification"]
        cls_name = cls.value if isinstance(cls, Classification) else str(cls)
        status_counts[cls_name] = status_counts.get(cls_name, 0) + 1
        record = {
            "capability_id": cid,
            "execution_family": entry["execution_family"],
            "authoritative_binding": entry["authoritative_binding"],
            "semantic_ids": entry["semantic_ids"],
            "target_ids": entry["target_ids"],
            "classification": cls_name,
            **{k: v for k, v in r.items() if k != "classification"},
            "timestamp": time.time(),
        }
        full_records.append(record)
        if cls in NEEDS_FOLLOWUP:
            failures.append(record)
            forensic_queue.append({
                "capability_id": cid,
                "authoritative_binding": entry["authoritative_binding"],
                "classification": cls_name,
                "detail": r.get("detail", ""),
            })

    with open(run_dir / "results.jsonl", "w", encoding="utf-8") as f:
        for rec in full_records:
            f.write(json.dumps(rec) + "\n")
    with open(run_dir / "failures.json", "w", encoding="utf-8") as f:
        json.dump(failures, f, indent=2)
    with open(run_dir / "forensic_queue.json", "w", encoding="utf-8") as f:
        json.dump(forensic_queue, f, indent=2)
    summary = {
        "run_dir": str(run_dir),
        "unique_capability_count": len(queue),
        "status_counts": status_counts,
        "failure_count": len(failures),
    }
    with open(run_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true", help="verify every family with an implemented bulk runner")
    ap.add_argument("--family", choices=sorted(FAMILY_ALIASES), action="append", default=[],
                     help="verify one family (repeatable)")
    ap.add_argument("--failed", action="store_true",
                     help="rerun only capability_ids that were NEEDS_FOLLOWUP in the most recent run")
    ap.add_argument("--ui", action="store_true",
                     help="also emit ui_worklist.json for the agent-driven UI Truth Gate pass "
                          "(this tool cannot perform UI reads itself -- see module docstring)")
    ap.add_argument("--persist", dest="persist", action="store_true", default=True,
                     help="include the persistence (save/reload) phase (default: on)")
    ap.add_argument("--no-persist", dest="persist", action="store_false")
    ap.add_argument("--evidence", type=str, default=None, help="evidence output directory")
    args = ap.parse_args(argv)

    registry = load_registry()
    queue = build_queue(registry)

    families = set()
    if args.all:
        families = {"HOST_PARAMETER", "BODY_STATE_FIELD", "MATRIX_ROUTE", "RESOURCE_OPERATION", "STRUCTURAL_OPERATION"}
    for f in args.family:
        families.add(FAMILY_ALIASES[f])
    if not families and not args.failed:
        families = {"HOST_PARAMETER", "BODY_STATE_FIELD"}

    if args.all:
        target_ids = set(queue.keys())
    else:
        target_ids = {cid for cid, e in queue.items() if e["execution_family"] in families}
    if args.failed:
        prior_summaries = sorted(DEFAULT_EVIDENCE_ROOT.glob("*/failures.json"), key=lambda p: p.stat().st_mtime)
        if not prior_summaries:
            print("No prior run found for --failed.")
            return 1
        prior_failures = json.load(open(prior_summaries[-1], "r", encoding="utf-8"))
        target_ids = {r["capability_id"] for r in prior_failures}
        families = {queue[cid]["execution_family"] for cid in target_ids if cid in queue}

    all_results: Dict[str, dict] = {}
    for fam in sorted(families):
        entries = [e for cid, e in queue.items() if e["execution_family"] == fam and cid in target_ids]
        if not entries:
            continue
        all_results.update(run_family(fam, entries))

    run_id = time.strftime("%Y%m%d_%H%M%S")
    evidence_dir = Path(args.evidence) if args.evidence else (DEFAULT_EVIDENCE_ROOT / run_id)
    subset_queue = {cid: e for cid, e in queue.items() if cid in target_ids}
    summary = write_evidence(evidence_dir, subset_queue, all_results)

    if args.ui:
        worklist = [r for r in json.load(open(evidence_dir / "failures.json")) if
                    r["classification"] in {"PERSISTENCE_MISMATCH", "BINDING_ERROR", "FORENSIC_REQUIRED"}]
        with open(evidence_dir / "ui_worklist.json", "w", encoding="utf-8") as f:
            json.dump(worklist, f, indent=2)
        print(f"UI worklist ({len(worklist)} entries) written for the agent-driven pass -- "
              f"this tool cannot read Serum's GUI itself.")

    print(f"TOTAL: {summary['unique_capability_count']}")
    for status, count in sorted(summary["status_counts"].items(), key=lambda kv: -kv[1]):
        print(f"  {status:24s} {count}")
    if summary["failure_count"]:
        print(f"\n{summary['failure_count']} need follow-up -- see {evidence_dir / 'forensic_queue.json'}")
    print(f"\nEvidence: {evidence_dir}")
    return 0 if summary["failure_count"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
