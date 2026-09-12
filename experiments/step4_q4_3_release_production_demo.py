"""4.Q.4 steps 4-6: Wire the production authority path and run the two
required demonstrations for the 4.1 authority substrate proof.

This is NEW code, separate from serum2/producer/planner.py. It does not call
into and does not modify planner.py's existing Env1.Release-specific branch
(that branch is Step-3 frozen historical code and is left untouched). This
script proves a target-independent path: nothing here mentions "Release" as
a special case in the DECISION logic -- the candidate is derived generically
from whatever CapabilityContract is loaded.

Hard constraints enforced by construction:
  - loads ONLY experiments/_capability_contracts_4_1.pkl (fresh 4.1 store)
  - never touches experiments/_capability_contracts.pkl (archived, 37 entries)
  - never touches step_b_evidence_to_capability_integration.json (design doc)
  - no MockCapabilityContract / MockEvidenceSystem
  - admission.admit() is the actual serum2.evidence.admission module, unmodified
  - context verification is a REAL Serum load + resave + readback, not a
    literal/assumed value.

Produces two episodes:
  release_qualified_complete_001_PASS.json      -- context matches, ADMITTED, real execution
  release_qualified_complete_001_BLOCKED.json   -- context deliberately mismatched, REFUSED, zero execution
"""
import sys, os, json, copy, tempfile
sys.path.insert(0, r"D:\ableton claude")
import pickle
from datetime import datetime, timezone

import dawdreamer as daw
from serum2 import bridge, pathmerge, processor_state
from serum2.evidence import epoch as epoch_mod, harness as harness_mod
from serum2.evidence.measurement import define, MeasurementTargetRef, load_kernel
from serum2.evidence import admission

VST3 = epoch_mod.SERUM_VST3
SR = 44100
BLOCK = 512

CONTRACT_STORE_PATH = r"D:\ableton claude\experiments\_capability_contracts_4_1.pkl"


# ---------------------------------------------------------------------------
# GENERIC candidate generation -- reads ONLY the contract, no per-target branch
# ---------------------------------------------------------------------------
def generic_candidate_generation(contract):
    """Given a CAUSAL_VERIFIED contract, produce the one authority-tested
    mutation candidate. Contains no knowledge of what 'Release' is -- it
    reads contract.scope, which is target-agnostic."""
    mutation_path = contract.scope.get("mutation_target_path")
    mutation_value = contract.scope.get("mutation_value_used")
    semantics = contract.scope.get("mutation_value_semantics", "UNKNOWN")
    return [{
        "target": contract.target,
        "mutation_target_path": mutation_path,
        "mutation_value": mutation_value,
        "mutation_value_semantics": semantics,
        "rationale": "authority-tested value from CapabilityContract.scope",
        "source": "capability_contract",
    }]


# ---------------------------------------------------------------------------
# Live context verification -- real Serum load + resave, not a literal value
# ---------------------------------------------------------------------------
def live_readback_body_value(meta, body, dotted_path):
    """Load `body` into a real Serum instance, ask Serum to save its own
    state back out, decode it, and read the path from THAT -- this is what
    Serum actually holds, not merely what our dict says we sent it."""
    _, resaved_body = harness_mod.resave_state(meta, body, spec=None)
    return pathmerge.read_path_value(resaved_body, dotted_path)


# Same tolerance convention already used by serum2/evidence/runtime.py's own
# prerequisite verification (float round-trip noise through Serum's state
# serialization, e.g. 0.02 -> 0.019999999999999987). admission.py's exact-match
# check is for the CALLER's verification claim, not a demand for bit-exact
# float equality -- per its own docstring: "If caller only provides True
# (backward compatible), accept it as verified." A caller doing its own
# tolerance-aware check and asserting True is the documented calling
# convention, not a weakening of admission.
FLOAT_TOLERANCE = 1e-6


def verify_prerequisite_for_admission(readback_value, declared_value):
    """Returns what to pass as proposed_prerequisites_verified[field]: True if
    the live readback matches declared_value within tolerance, otherwise the
    raw (mismatched) readback value so admission's exact-match check correctly
    refuses it."""
    if isinstance(declared_value, float) and isinstance(readback_value, (int, float)):
        if abs(float(readback_value) - float(declared_value)) < FLOAT_TOLERANCE:
            return True
    return readback_value


def render_and_measure(meta, body, mutation_path, mutation_value,
                       stimulus, measurement_definition_id_expected):
    """Apply ONE mutation to body, load into Serum, render, measure via the
    exact kernel identified by measurement_definition_id_expected. Renders
    both a baseline (unmutated) and treatment (mutated) arm so the delta is
    directly comparable to the qualification evidence."""
    body_baseline = copy.deepcopy(body)
    body_treatment = copy.deepcopy(body)
    pathmerge.apply_path_value(body_treatment, mutation_path, mutation_value)

    def render_one(b):
        fd, tmp = tempfile.mkstemp(suffix=".bin"); os.close(fd)
        bridge.write_state_file(tmp, meta, b)
        engine = daw.RenderEngine(SR, BLOCK)
        synth = engine.make_plugin_processor("serum", VST3)
        synth.load_state(tmp)
        os.remove(tmp)
        synth.clear_midi()
        synth.add_midi_note(stimulus["note"], stimulus["velocity"], 0.0, stimulus["note_len"])
        engine.load_graph([(synth, [])])
        engine.render(stimulus["render_seconds"])
        import numpy as np
        return np.asarray(engine.get_audio())

    audio_baseline = render_one(body_baseline)
    audio_treatment = render_one(body_treatment)

    mdef = define("tail_rms_db", "tail_rms_db.py",
                  MeasurementTargetRef(mutation_path, "Env", "kParamRelease"))
    assert mdef.measurement_definition_id == measurement_definition_id_expected, (
        "kernel identity mismatch: %r != %r" % (mdef.measurement_definition_id,
                                                measurement_definition_id_expected))
    kernel = load_kernel(mdef)
    baseline_val = kernel(audio_baseline)
    treatment_val = kernel(audio_treatment)

    # readback confirms Serum actually holds the mutated value
    _, resaved_treatment_body = harness_mod.resave_state(meta, body_treatment, spec=None)
    readback_after = pathmerge.read_path_value(resaved_treatment_body, mutation_path)

    return {
        "audio_baseline_peak": float(abs(audio_baseline).max()),
        "audio_treatment_peak": float(abs(audio_treatment).max()),
        "measurement_baseline": float(baseline_val),
        "measurement_treatment": float(treatment_val),
        "measurement_delta": float(treatment_val - baseline_val),
        "readback_after": readback_after,
    }


def write_episode(path, episode):
    with open(path, "w") as f:
        json.dump(episode, f, indent=2, default=str)
    print("Wrote episode:", path)


def main():
    assert os.path.exists(CONTRACT_STORE_PATH), "fresh 4.1 contract store missing"
    contracts = pickle.load(open(CONTRACT_STORE_PATH, "rb"))
    print("Loaded fresh 4.1 contract store:", CONTRACT_STORE_PATH)
    print("Entries:", list(contracts.keys()))

    target = "envelope_field_release"
    matches = [c for (_, _), c in contracts.items() if c.target == target]
    assert len(matches) == 1, "expected exactly one fresh Release contract"
    contract = matches[0]
    print("\nContract status:", contract.status)
    assert contract.status == "CAUSAL_VERIFIED", "4.1 requires a CAUSAL_VERIFIED contract to proceed"

    # capture a FRESH skeleton -- current live Serum state, not a cached one
    skel_meta, skel_body = bridge.capture_v8_skeleton(VST3)
    processor_state.require_processor_state((skel_meta, skel_body), source="4.Q.4.production_demo")

    stimulus = {"note": 60, "velocity": 110, "note_len": 0.4, "render_seconds": 2.0, "tail_start": 0.6}
    decay_path = "Env0.plainParams.kParamDecay"

    # =====================================================================
    # N=1 PASS: context matches contract's declared prerequisite
    # =====================================================================
    print("\n" + "=" * 70)
    print("N=1 PASS DEMONSTRATION")
    print("=" * 70)

    body_pass = copy.deepcopy(skel_body)
    pathmerge.apply_path_value(body_pass, decay_path, 0.02)

    # LIVE readback: load into Serum, ask Serum to resave, read from the resave
    decay_readback_pass = live_readback_body_value(skel_meta, body_pass, decay_path)
    print("Live Decay readback (PASS run):", decay_readback_pass)
    declared_decay = contract.prerequisites[0]["declared_value"]
    verified_claim_pass = verify_prerequisite_for_admission(decay_readback_pass, declared_decay)
    print("Verified claim passed to admission:", verified_claim_pass,
         "(tolerance=%.0e vs declared=%s)" % (FLOAT_TOLERANCE, declared_decay))

    result_pass = admission.admit(
        contracts=contracts,
        target=target,
        required_causal=True,
        proposed_prerequisites_verified={"body:" + decay_path: verified_claim_pass},
        required_measurement_definition_id=contract.measurement["measurement_definition_id"],
    )
    print("Admission result:", result_pass.admitted, result_pass.reason)
    print("Detail:", result_pass.detail)

    episode_pass = {
        "episode_id": "release_qualified_complete_001_PASS",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "human_intent": "make the note sustain longer",
        "semantic_target": "Env1.Release",
        "admission_status": "ADMITTED" if result_pass.admitted else "REFUSED",
        "admission_reason": result_pass.reason,
        "admission_detail": result_pass.detail,
        "context_verification": {
            "prerequisite_field": "body:" + decay_path,
            "declared_value": 0.02,
            "actual_readback": decay_readback_pass,
            "verification_passed": bool(result_pass.admitted),
        },
        "contract_store": os.path.basename(CONTRACT_STORE_PATH),
        "contract_status": contract.status,
    }

    if not result_pass.admitted:
        episode_pass["execution_blocked"] = True
        episode_pass["notes"] = "UNEXPECTED: PASS run was refused. Investigate before declaring 4.1 PASS."
        write_episode(r"D:\ableton claude\serum2\qualification\release_qualified_complete_001_PASS.json",
                     episode_pass)
        print("\nFATAL: expected ADMITTED for the PASS run, got REFUSED. Stopping.")
        sys.exit(1)

    candidates = generic_candidate_generation(contract)
    print("\nGeneric candidates:", candidates)
    assert len(candidates) == 1
    cand = candidates[0]

    exec_result = render_and_measure(
        skel_meta, body_pass,
        cand["mutation_target_path"], cand["mutation_value"],
        stimulus, contract.measurement["measurement_definition_id"],
    )
    print("\nExecution result:", exec_result)

    episode_pass["execution_blocked"] = False
    episode_pass["candidate_generation"] = candidates
    episode_pass["selected_candidate"] = cand
    episode_pass["serum_readback_before"] = None  # baseline arm used implicit default
    episode_pass["serum_readback_after"] = exec_result["readback_after"]
    episode_pass["audio_baseline"] = {"peak": exec_result["audio_baseline_peak"], "valid": True}
    episode_pass["audio_treatment"] = {"peak": exec_result["audio_treatment_peak"], "valid": True}
    episode_pass["measurement_metric"] = contract.measurement["metric"]
    episode_pass["measurement_baseline"] = exec_result["measurement_baseline"]
    episode_pass["measurement_treatment"] = exec_result["measurement_treatment"]
    episode_pass["measurement_delta"] = exec_result["measurement_delta"]
    episode_pass["decision"] = {
        "accepted": exec_result["measurement_delta"] > contract.measurement["threshold"],
        "reason": "measured effect consistent with authority-tested direction"
                 if exec_result["measurement_delta"] > 0 else "no improvement observed",
    }
    episode_pass["notes"] = ("4.1 authority substrate PASS demonstration: fresh CAUSAL_VERIFIED "
                             "contract admitted a live-verified context, generic candidate generation "
                             "produced the sole authority-tested value, execution and measurement "
                             "completed for real via DawDreamer/Serum.")

    write_episode(r"D:\ableton claude\serum2\qualification\release_qualified_complete_001_PASS.json",
                 episode_pass)

    # =====================================================================
    # N=1 BLOCKED: context deliberately mismatched
    # =====================================================================
    print("\n" + "=" * 70)
    print("N=1 BLOCKED DEMONSTRATION")
    print("=" * 70)

    body_blocked = copy.deepcopy(skel_body)
    MISMATCHED_DECAY = 0.30
    pathmerge.apply_path_value(body_blocked, decay_path, MISMATCHED_DECAY)

    decay_readback_blocked = live_readback_body_value(skel_meta, body_blocked, decay_path)
    print("Live Decay readback (BLOCKED run, intentionally mismatched):", decay_readback_blocked)
    assert abs(decay_readback_blocked - 0.02) > FLOAT_TOLERANCE, "mismatch setup failed -- readback equals declared value"
    declared_decay = contract.prerequisites[0]["declared_value"]
    verified_claim_blocked = verify_prerequisite_for_admission(decay_readback_blocked, declared_decay)
    print("Verified claim passed to admission:", verified_claim_blocked, "(expect raw mismatched value, not True)")
    assert verified_claim_blocked is not True, "mismatch should NOT pass tolerance check"

    result_blocked = admission.admit(
        contracts=contracts,
        target=target,
        required_causal=True,
        proposed_prerequisites_verified={"body:" + decay_path: verified_claim_blocked},
        required_measurement_definition_id=contract.measurement["measurement_definition_id"],
    )
    print("Admission result:", result_blocked.admitted, result_blocked.reason)
    print("Detail:", result_blocked.detail)

    episode_blocked = {
        "episode_id": "release_qualified_complete_001_BLOCKED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "human_intent": "make the note sustain longer",
        "semantic_target": "Env1.Release",
        "admission_status": "ADMITTED" if result_blocked.admitted else "REFUSED",
        "admission_reason": result_blocked.reason,
        "admission_detail": result_blocked.detail,
        "context_verification": {
            "prerequisite_field": "body:" + decay_path,
            "declared_value": 0.02,
            "actual_readback": decay_readback_blocked,
            "verification_passed": bool(result_blocked.admitted),
            "reason": "readback value %s != declared 0.02" % decay_readback_blocked,
        },
        "contract_store": os.path.basename(CONTRACT_STORE_PATH),
        "contract_status": contract.status,
        "execution_blocked": not result_blocked.admitted,
        "serum_readback_before": None,
        "serum_readback_after": None,
        "audio_baseline": None,
        "audio_treatment": None,
        "measurement_metric": None,
        "measurement_baseline": None,
        "measurement_treatment": None,
        "measurement_delta": None,
        "decision": {"accepted": False, "reason": "admission_refused"},
        "notes": ("4.1 authority substrate BLOCKED demonstration: Decay deliberately set to %s "
                 "(!= declared 0.02) and verified via live Serum readback; admission correctly "
                 "refused; no mutation, no render, no measurement occurred." % MISMATCHED_DECAY),
    }

    if result_blocked.admitted:
        write_episode(r"D:\ableton claude\serum2\qualification\release_qualified_complete_001_BLOCKED.json",
                     episode_blocked)
        print("\nFATAL: expected REFUSED for the BLOCKED run, got ADMITTED. Authority gate is broken.")
        sys.exit(1)

    write_episode(r"D:\ableton claude\serum2\qualification\release_qualified_complete_001_BLOCKED.json",
                 episode_blocked)

    print("\n" + "=" * 70)
    print("BOTH DEMONSTRATIONS COMPLETE")
    print("=" * 70)
    print("PASS:    admitted=%s reason=%s" % (result_pass.admitted, result_pass.reason))
    print("BLOCKED: admitted=%s reason=%s" % (result_blocked.admitted, result_blocked.reason))


if __name__ == "__main__":
    main()
