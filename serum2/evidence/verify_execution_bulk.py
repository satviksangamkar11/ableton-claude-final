#!/usr/bin/env python3
"""MACHINE-TIER bulk verification for every unique CapabilityBinding in
SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json.

Scope and what this is NOT:
  This verifies MUTATION_PASS (authority mutation is observed by a readback
  from the SAME loaded Serum instance) and PERSISTENCE_PASS (readback after
  a real Serum save_state()/load_state() round-trip) for every unique
  capability_id, batched into as few Serum load/save cycles as the
  execution family allows. It is fully scriptable -- no UI, no computer-use,
  no human per control.

  It is deliberately NOT the UI Truth Gate. A control can be
  MACHINE_VERIFIED (the CBOR/VST3-parameter byte genuinely round-trips)
  while still being UI_MISMATCH in the real Serum GUI -- that is exactly
  the FXPhaser.Phase defect this same session already caught: kParamPhase
  round-tripped fine at this machine tier and still never moved the real
  knob (the real control was kParamWidth). MACHINE_VERIFIED is a necessary
  but not sufficient condition for UI_VERIFIED; only real-Serum-in-Ableton
  visual inspection (manual, one control at a time, see the V3 Pass 2 UI
  Truth Gate report) can close that gap. This script exists to make sure
  the machine tier -- which IS bulk-automatable -- is not left unexercised
  for the ~80 bindings that have never been run through ANY real-Serum
  round-trip at all (the HOST_PARAMETER family currently only has
  existence evidence: the parameter name appears in
  synth.get_parameters_description(), nothing more).

Probe strategy: two off-default probes per control (a "low" and a "high"
quartile value), not one. A single default-valued probe cannot distinguish
a real round-trip from Serum's presence-preserving collapse-to-"default"
behavior (the exact trap that made an early version of the FXPhaser.Phase
regression test look broken this session: the range midpoint, 180.0, is
that control's actual default). Two distinct non-default probes that both
read back correctly is not fooled by that trap.
"""

import sys
import copy
import json
import tempfile
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import dawdreamer as daw

from serum2 import bridge, codec, vst3_state
from serum2.evidence import epoch as epoch_mod
from serum2.evidence.mutation_executor_extended import execute_mutation_request_with_authority
from serum2.evidence.mutation_request import MutationRequest, MutationType
from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding
from serum2.operations.fx_resolver import resolve_fx_parameter

VST3 = epoch_mod.SERUM_VST3
SR, BLOCK = 44100, 512
REGISTRY_PATH = Path(__file__).parent.parent.parent / "SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json"

# Same confirmed real (type_index -> FX-type-key) map used by the V3
# real-roundtrip tests -- authoritative, captured against real Serum
# preset output this session, not guessed.
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


def load_registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def dedupe_bindings(registry):
    """Same dedup the registry's own summary reports (93 for this run):
    collapse every RESOLVED semantic row's capability_binding down to
    unique capability_id, keeping one representative row per id."""
    seen = {}
    for row in registry["semantic_resolutions"]:
        cb = row.get("capability_binding")
        if not cb:
            continue
        seen.setdefault(cb["capability_id"], {"binding": cb, "semantic_ids": []})
        seen[cb["capability_id"]]["semantic_ids"].append(row["semantic_id"])
    return seen


def host_param_engine():
    engine = daw.RenderEngine(SR, BLOCK)
    return engine, engine.make_plugin_processor("serum", VST3)


def make_host_contract(param_name):
    binding = ExecutionBinding(mutation_type="HOST_PARAMETER", host_parameter_name=param_name,
                                binding_source="verify_execution_bulk", binding_version="1.0")
    return CapabilityContract(target="T", allowed_operation="mutate_numeric_value",
                               status="CAUSAL_VERIFIED", prerequisites=(), verified={},
                               measurement=None, scope={}, provenance={},
                               execution_binding=binding, limitations=())


def make_fx_contract():
    binding = ExecutionBinding(mutation_type="BODY_STATE", resolver_operation_id="fx_set_parameter",
                                binding_source="verify_execution_bulk", binding_version="1.0")
    return CapabilityContract(target="T", allowed_operation="mutate_numeric_value",
                               status="CAUSAL_VERIFIED", prerequisites=(), verified={},
                               measurement=None, scope={}, provenance={},
                               execution_binding=binding, limitations=())


def verify_host_parameters_bulk(bindings):
    """One Serum instance, all HOST_PARAMETER controls in one batch:
    mutate every param on the live synth, verify each readback in-process
    (MUTATION_PASS), then a single save_state()/fresh-instance load_state()
    cycle proves PERSISTENCE_PASS for all of them at once."""
    results = {}
    engine, synth = host_param_engine()
    params = synth.get_parameters_description()
    by_name = {p["name"]: p for p in params}

    probes = {}  # cap_id -> (idx, probe_a, probe_b)
    for cap_id, entry in bindings.items():
        b = entry["binding"]
        name = b["authoritative_binding"]["parameter_name"]
        meta = by_name.get(name)
        if meta is None:
            results[cap_id] = {"status": "BINDING_ERROR", "detail": f"host parameter not in live list: {name!r}"}
            continue
        default = meta["defaultValue"]
        probe_a = 0.75 if abs(default - 0.75) > 0.05 else 0.2
        probe_b = 0.25 if abs(default - 0.25) > 0.05 else 0.8
        probes[cap_id] = (meta["index"], probe_a, probe_b)

    contract_cache = {}

    def mutate_and_check(cap_id, value):
        b = bindings[cap_id]["binding"]
        name = b["authoritative_binding"]["parameter_name"]
        contract = contract_cache.setdefault(cap_id, make_host_contract(name))
        request = MutationRequest(target="T", mutation_type=MutationType.HOST_PARAMETER, value=value,
                                   host_parameter_name=name)
        proof = execute_mutation_request_with_authority(
            request=request, body={}, contracts={("T", ""): contract}, synth=synth,
        )
        return proof

    # Pass 1: mutate to probe_a, verify in-process
    for cap_id, (idx, probe_a, probe_b) in probes.items():
        proof = mutate_and_check(cap_id, probe_a)
        if not proof.executed:
            results[cap_id] = {"status": "MUTATION_FAILED", "detail": proof.detail}
            continue
        readback = synth.get_parameter(idx)
        if abs(readback - probe_a) > 1e-4:
            results[cap_id] = {"status": "MUTATION_MISMATCH",
                                "detail": f"requested {probe_a}, in-process readback {readback}"}
            continue
        results[cap_id] = {"status": "MUTATION_PASS", "probe_a": probe_a, "probe_b": probe_b}

    # Save the whole batch's state in one shot
    fd, tmp = tempfile.mkstemp(suffix=".bin"); os.close(fd)
    synth.save_state(tmp)

    # Fresh instance, load, confirm probe_a persisted -- this is the real
    # Serum save/load cycle, not an in-memory assumption.
    engine2, synth2 = host_param_engine()
    synth2.load_state(tmp)
    os.remove(tmp)
    for cap_id, (idx, probe_a, probe_b) in probes.items():
        if results.get(cap_id, {}).get("status") != "MUTATION_PASS":
            continue
        readback = synth2.get_parameter(idx)
        if abs(readback - probe_a) > 1e-4:
            results[cap_id] = {**results[cap_id], "status": "PERSISTENCE_MISMATCH",
                                "detail": f"requested {probe_a}, post-reload readback {readback}"}
            continue
        results[cap_id]["persistence_probe_a"] = "PASS"

    # Pass 2 (second, distinct probe -- defeats the default-collapse trap):
    # mutate synth2 to probe_b, verify in-process, save/reload again.
    for cap_id, (idx, probe_a, probe_b) in probes.items():
        if results.get(cap_id, {}).get("status") != "MUTATION_PASS":
            continue
        b = bindings[cap_id]["binding"]
        name = b["authoritative_binding"]["parameter_name"]
        contract = contract_cache[cap_id]
        request = MutationRequest(target="T", mutation_type=MutationType.HOST_PARAMETER, value=probe_b,
                                   host_parameter_name=name)
        proof = execute_mutation_request_with_authority(
            request=request, body={}, contracts={("T", ""): contract}, synth=synth2,
        )
        if not proof.executed:
            results[cap_id] = {**results[cap_id], "status": "MUTATION_FAILED_PROBE_B", "detail": proof.detail}
            continue
        readback = synth2.get_parameter(idx)
        if abs(readback - probe_b) > 1e-4:
            results[cap_id] = {**results[cap_id], "status": "MUTATION_MISMATCH_PROBE_B",
                                "detail": f"requested {probe_b}, in-process readback {readback}"}

    fd, tmp2 = tempfile.mkstemp(suffix=".bin"); os.close(fd)
    synth2.save_state(tmp2)
    engine3, synth3 = host_param_engine()
    synth3.load_state(tmp2)
    os.remove(tmp2)
    for cap_id, (idx, probe_a, probe_b) in probes.items():
        if results.get(cap_id, {}).get("status") != "MUTATION_PASS":
            continue
        readback = synth3.get_parameter(idx)
        if abs(readback - probe_b) > 1e-4:
            results[cap_id] = {**results[cap_id], "status": "PERSISTENCE_MISMATCH_PROBE_B",
                                "detail": f"requested {probe_b}, post-reload readback {readback}"}
            continue
        results[cap_id]["status"] = "MACHINE_VERIFIED"
        results[cap_id]["persistence_probe_b"] = "PASS"

    return results


def verify_fx_parameters_bulk(bindings):
    """All FX_PARAMETER/BODY_STATE_FIELD controls, batched into ONE FXRack0
    with one module per distinct effect (mirrors the real 6-effect chain
    already proven in the V3 Pass 2 UI Truth Gate session -- multiple FX
    modules coexist fine in one rack), one save, one reload."""
    results = {}
    by_effect = {}
    for cap_id, entry in bindings.items():
        b = entry["binding"]["authoritative_binding"]
        effect = b["effect"]
        by_effect.setdefault(effect, []).append((cap_id, b["parameter"]))

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, skel_body = skeleton
    body = copy.deepcopy(skel_body)
    fx_list = []
    slot_of = {}
    probes = {}  # cap_id -> (effect, parameter, probe_a, probe_b)
    for slot, (effect, params) in enumerate(by_effect.items()):
        type_key = EFFECT_TO_TYPE_KEY.get(effect)
        if type_key is None or type_key not in CONFIRMED_FX_TYPE_INDEX:
            for cap_id, param in params:
                results[cap_id] = {"status": "BINDING_ERROR", "detail": f"no confirmed FX-type-key for effect {effect!r}"}
            continue
        fx_list.append({"type": CONFIRMED_FX_TYPE_INDEX[type_key], type_key: {"plainParams": {}}})
        slot_of[effect] = slot
        for cap_id, param in params:
            resolved = resolve_fx_parameter(effect, param, 0, slot)
            if resolved is None:
                results[cap_id] = {"status": "BINDING_ERROR", "detail": f"fx_resolver has no catalog entry for {effect}/{param}"}
                continue
            span = resolved.max_value - resolved.min_value
            probe_a = resolved.min_value + 0.75 * span
            probe_b = resolved.min_value + 0.25 * span
            probes[cap_id] = (effect, param, slot, probe_a, probe_b)
    body["FXRack0"]["FX"] = fx_list

    def rt(meta_, body_):
        fd, tmp = tempfile.mkstemp(suffix=".bin"); os.close(fd)
        bridge.write_state_file(tmp, meta_, body_)
        engine = daw.RenderEngine(SR, BLOCK)
        synth = engine.make_plugin_processor("serum", VST3)
        synth.load_state(tmp)
        os.remove(tmp)
        fd, out = tempfile.mkstemp(suffix=".bin"); os.close(fd)
        synth.save_state(out)
        raw = open(out, "rb").read(); os.remove(out)
        return codec.decode(vst3_state.unwrap_vc2(raw))

    contract = make_fx_contract()
    for cap_id, (effect, param, slot, probe_a, probe_b) in probes.items():
        request = MutationRequest(target="T", mutation_type=MutationType.BODY_STATE, value=probe_a,
                                   resolver_parameters={"rack": 0, "slot": slot, "effect": effect, "parameter": param})
        proof = execute_mutation_request_with_authority(
            request=request, body=body, contracts={("T", ""): contract}, synth=None,
        )
        if not proof.executed:
            results[cap_id] = {"status": "MUTATION_FAILED", "detail": proof.detail}

    _, resaved = rt(meta, body)
    fx_by_slot = {i: fx for i, fx in enumerate(resaved["FXRack0"]["FX"])}
    param_key_by_state_path = {}
    for cap_id, (effect, param, slot, probe_a, probe_b) in probes.items():
        if cap_id in results:
            continue
        resolved = resolve_fx_parameter(effect, param, 0, slot)
        key_name = resolved.state_path.rsplit(".", 1)[-1]  # e.g. "kParamWidth"
        type_key = EFFECT_TO_TYPE_KEY[effect]
        fx = fx_by_slot.get(slot)
        plain_params = fx.get(type_key, {}).get("plainParams") if fx else None
        readback = plain_params.get(key_name) if isinstance(plain_params, dict) else None
        if readback is None or abs(readback - probe_a) > 1e-3:
            results[cap_id] = {"status": "PERSISTENCE_MISMATCH_PROBE_A",
                                "detail": f"requested {probe_a}, readback {readback}"}
        else:
            results[cap_id] = {"status": "PROBE_A_PASS", "probe_a": probe_a, "probe_b": probe_b}

    # Second pass with probe_b, fresh skeleton (same batching, different values)
    body2 = copy.deepcopy(skel_body)
    body2["FXRack0"]["FX"] = copy.deepcopy(fx_list)
    for cap_id, (effect, param, slot, probe_a, probe_b) in probes.items():
        if results.get(cap_id, {}).get("status") != "PROBE_A_PASS":
            continue
        request = MutationRequest(target="T", mutation_type=MutationType.BODY_STATE, value=probe_b,
                                   resolver_parameters={"rack": 0, "slot": slot, "effect": effect, "parameter": param})
        proof = execute_mutation_request_with_authority(
            request=request, body=body2, contracts={("T", ""): contract}, synth=None,
        )
        if not proof.executed:
            results[cap_id] = {**results[cap_id], "status": "MUTATION_FAILED_PROBE_B", "detail": proof.detail}

    _, resaved2 = rt(meta, body2)
    fx_by_slot2 = {i: fx for i, fx in enumerate(resaved2["FXRack0"]["FX"])}
    for cap_id, (effect, param, slot, probe_a, probe_b) in probes.items():
        if results.get(cap_id, {}).get("status") != "PROBE_A_PASS":
            continue
        resolved = resolve_fx_parameter(effect, param, 0, slot)
        key_name = resolved.state_path.rsplit(".", 1)[-1]
        type_key = EFFECT_TO_TYPE_KEY[effect]
        fx = fx_by_slot2.get(slot)
        plain_params = fx.get(type_key, {}).get("plainParams") if fx else None
        readback = plain_params.get(key_name) if isinstance(plain_params, dict) else None
        if readback is None or abs(readback - probe_b) > 1e-3:
            results[cap_id] = {**results[cap_id], "status": "PERSISTENCE_MISMATCH_PROBE_B",
                                "detail": f"requested {probe_b}, readback {readback}"}
        else:
            results[cap_id]["status"] = "MACHINE_VERIFIED"
            results[cap_id]["probe_b_persisted"] = "PASS"

    return results


def main():
    registry = load_registry()
    unique = dedupe_bindings(registry)
    print(f"Deduplicated {sum(len(v['semantic_ids']) for v in unique.values())} bound semantic rows "
          f"-> {len(unique)} unique capability_ids\n")

    by_family = {}
    for cap_id, entry in unique.items():
        fam = entry["binding"]["execution_family"]
        status = entry["binding"]["binding_status"]
        by_family.setdefault((fam, status), []).append(cap_id)

    for (fam, status), ids in sorted(by_family.items()):
        print(f"  {fam:24s} {status:16s} {len(ids):3d}")
    print()

    host_ids = by_family.get(("HOST_PARAMETER", "LIVE_VERIFIED"), [])
    fx_ids = by_family.get(("BODY_STATE_FIELD", "LIVE_VERIFIED"), [])
    other_ids = [cid for (fam, status), ids in by_family.items()
                 if fam not in ("HOST_PARAMETER", "BODY_STATE_FIELD") for cid in ids]

    all_results = {}

    if host_ids:
        print(f"=== HOST_PARAMETER machine-tier bulk verification ({len(host_ids)} unique) ===")
        host_bindings = {cid: unique[cid] for cid in host_ids}
        all_results.update(verify_host_parameters_bulk(host_bindings))

    if fx_ids:
        print(f"\n=== FX_PARAMETER (BODY_STATE_FIELD) machine-tier bulk verification ({len(fx_ids)} unique) ===")
        fx_bindings = {cid: unique[cid] for cid in fx_ids}
        all_results.update(verify_fx_parameters_bulk(fx_bindings))

    for cid in other_ids:
        all_results[cid] = {"status": "SKIPPED_NOT_YET_DERIVED",
                             "detail": "binding_status != LIVE_VERIFIED, nothing to verify yet"}

    # ---- Ledger ----
    status_counts = {}
    for cid, r in all_results.items():
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1

    print("\n" + "=" * 70)
    print("MACHINE-TIER BULK VERIFICATION LEDGER")
    print("=" * 70)
    for status, count in sorted(status_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {status:32s} {count:3d}")
    print()

    anomalies = {cid: r for cid, r in all_results.items()
                 if r["status"] not in ("MACHINE_VERIFIED", "SKIPPED_NOT_YET_DERIVED")}
    if anomalies:
        print(f"ANOMALIES ({len(anomalies)}) -- these need investigation, not the other "
              f"{len(all_results) - len(anomalies)}:")
        for cid, r in anomalies.items():
            b = unique[cid]["binding"]["authoritative_binding"]
            print(f"  [{r['status']}] {cid}")
            print(f"      binding: {json.dumps(b)}")
            print(f"      detail:  {r.get('detail', '')}")
    else:
        print("No anomalies.")

    ledger_path = Path(__file__).parent.parent.parent / "SERUM2_MACHINE_VERIFICATION_LEDGER.json"
    with open(ledger_path, "w", encoding="utf-8") as f:
        json.dump({
            "unique_capability_count": len(unique),
            "status_counts": status_counts,
            "results": {cid: {**r, "semantic_ids": unique[cid]["semantic_ids"],
                               "authoritative_binding": unique[cid]["binding"]["authoritative_binding"]}
                        for cid, r in all_results.items()},
        }, f, indent=2)
    print(f"\nWrote: {ledger_path}")

    return 0 if not anomalies else 1


if __name__ == "__main__":
    sys.exit(main())
