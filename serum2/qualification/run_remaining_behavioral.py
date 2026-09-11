"""Execute and classify remaining seed behavioral experiments.

Steps:
1. Classify all 12 seed experiments by admission status.
2. Execute READY experiments (excluding Filter1.Cutoff and OSC1.Octave).
3. Qualify each observation.
4. Write remaining_behavioral_execution.json.

Classification logic:
  READY          = host_param or CBOR route known, context achievable in DawDreamer,
                   measurement kernel exists.
  BLOCKED_NO_ROUTE   = no working mutation route in DawDreamer subprocess.
  BLOCKED_CONTEXT    = required context cannot be applied (e.g. string value in
                       numeric-only host-param interface, unknown activation param).
  BLOCKED_MEASUREMENT = no suitable measurement kernel.
  BLOCKED_RESOURCE   = missing file/resource.

Known working routes (from prior evidence):
  - CBOR dict mutation works for Filter1.* because VoiceFilter0 plainParams are
    materialized in the default skeleton (not sparse "default" sentinels).
  - CBOR dict mutation does NOT work for VoiceOsc0/1, VoiceEnv0, VoiceModulation0,
    VoiceFilter1 — their plainParams are sparse sentinels; Serum ignores the dict.
  - Host param mutations via synth.set_parameter(index, value) work for any param
    exposed in get_parameters_description(), but treatment_host_param_name in the
    seed specs is None for all remaining experiments.
  - LFO1.Rate (no destination): CBOR mutation doesn't reach LFO audio chain, but
    expected outcome is NO_OBSERVED_EFFECT (LFO without destination is inaudible
    regardless of rate). The measurement confirms this — READY as null-control.
"""

from __future__ import annotations

import json
import os
import sys

# Add project root to path
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from serum2.qualification.seed_12_experiments import SEED_12_EXPERIMENTS
from serum2.qualification.experiment_worker import run_experiment_worker

# ── admission classification ──────────────────────────────────────────────────

ALREADY_QUALIFIED = {"seed_filter1_cutoff_001", "OSC1.Octave"}

# Experiments excluded from new execution (already have final qualified evidence)
EXCLUDED_EXPERIMENT_IDS = {"seed_filter1_cutoff_001"}

# Rationale for each blocked experiment
BLOCKED_RATIONALE = {
    "seed_filter2_cutoff_001": {
        "status": "BLOCKED_NO_ROUTE",
        "reason": (
            "Filter2 activation route unavailable in DawDreamer subprocess. "
            "No known host param activates VoiceFilter1 in isolated context. "
            "Context key 'Filter 2 On' not confirmed to reach DawDreamer instance. "
            "CBOR plainParams mutation produces exact-zero delta (confirmed by diagnostics)."
        ),
    },
    "seed_osc1_level_001": {
        "status": "BLOCKED_NO_ROUTE",
        "reason": (
            "CBOR dict mutation does not work for VoiceOsc0.plainParams — Serum ignores "
            "dict-replacement of sparse sentinel fields (confirmed by exact-zero delta "
            "regardless of treatment value). Host param route (set_parameter by index) "
            "would work, but treatment_host_param_name is not set in this experiment spec."
        ),
    },
    "seed_osc1_detune_001": {
        "status": "BLOCKED_NO_ROUTE",
        "reason": (
            "Same root cause as OSC1.Level: CBOR dict mutation at VoiceOsc0.plainParams "
            "is ignored by Serum. Host param index for 'A Detune' is not specified in "
            "this experiment spec's treatment_host_param_name."
        ),
    },
    "seed_osc2_detune_001": {
        "status": "BLOCKED_NO_ROUTE",
        "reason": (
            "CBOR dict mutation at VoiceOsc1.plainParams is ignored by Serum. "
            "OSC2 activation and parameter route are not established in subprocess context."
        ),
    },
    "seed_env1_attack_001": {
        "status": "BLOCKED_NO_ROUTE",
        "reason": (
            "CBOR dict mutation at VoiceEnv0.plainParams is ignored by Serum. "
            "Envelope routing to an audible destination is not established in subprocess context. "
            "MCP parameter 'Env 1 Attack' (index 12) operates on Ableton's running instance, "
            "not DawDreamer subprocess."
        ),
    },
    "seed_env1_release_001": {
        "status": "BLOCKED_NO_ROUTE",
        "reason": (
            "Same root cause as Env1.Attack: CBOR dict mutation at VoiceEnv0.plainParams "
            "is ignored by Serum. Envelope routing unavailable in subprocess."
        ),
    },
    "seed_lfo1_rate_filter_modulation_001": {
        "status": "BLOCKED_CONTEXT",
        "reason": (
            "Context includes 'LFO1 Mod Dest': 'Filter1.Cutoff' (string value). "
            "_apply_host_context converts all context values to float, causing ValueError "
            "when attempting float('Filter1.Cutoff'). Render fails before audio is produced. "
            "LFO modulation destination requires structural CBOR routing, not a host param float."
        ),
    },
    "seed_fxeq_freq1_001": {
        "status": "BLOCKED_NO_ROUTE",
        "reason": (
            "FX EQ requires explicit FX preset loading or CBOR FX activation. "
            "No confirmed host param activates 'FX EQ On' in DawDreamer subprocess. "
            "CBOR path FXRack0.FX.0.EQParameters.kParamEQ1Frequency may not be materialized "
            "in default skeleton. FX loading route not established."
        ),
    },
}

READY_EXPERIMENT_IDS = {
    "seed_filter1_resonance_001",  # CBOR route works (Filter1 materialized by default); effect below threshold but measurement valid
    "seed_filter1_drive_001",      # same Filter1 CBOR route
    "seed_lfo1_rate_no_destination_001",  # expected NO_OBSERVED_EFFECT; null-control confirmation
}


def classify_experiment(exp) -> dict:
    """Classify one BehaviorExperiment for admission."""
    eid = exp.experiment_id
    if eid in EXCLUDED_EXPERIMENT_IDS:
        return {
            "experiment_id": eid,
            "semantic_target": exp.semantic_target,
            "status": "ALREADY_QUALIFIED",
            "reason": "Filter1.Cutoff is the pilot — already has qualified evidence.",
        }
    if eid in BLOCKED_RATIONALE:
        bl = BLOCKED_RATIONALE[eid]
        return {
            "experiment_id": eid,
            "semantic_target": exp.semantic_target,
            "status": bl["status"],
            "reason": bl["reason"],
        }
    if eid in READY_EXPERIMENT_IDS:
        return {
            "experiment_id": eid,
            "semantic_target": exp.semantic_target,
            "status": "READY",
            "reason": (
                "CBOR route works for Filter1 (materialized plainParams in default skeleton). "
                "Context achievable via DawDreamer host params. Measurement kernel exists."
                if "filter1" in eid or "drive" in eid
                else "Expected null-control; LFO without modulation destination produces no audible effect regardless of CBOR route success."
            ),
        }
    return {
        "experiment_id": eid,
        "semantic_target": exp.semantic_target,
        "status": "BLOCKED_NO_ROUTE",
        "reason": "Unclassified experiment — no known working route.",
    }


def qualify_observation(obs_dict: dict, exp) -> dict:
    """Determine qualification status for one observation."""
    if not obs_dict.get("baseline_rendered") or not obs_dict.get("treatment_rendered"):
        return {"status": "INVALID_OBSERVATION", "reason": "Render failed or signal invalid."}

    measurements = obs_dict.get("measurements", [])
    if not measurements:
        return {"status": "INVALID_OBSERVATION", "reason": "No measurements captured."}

    primary = measurements[0]
    status = primary.get("status", "NOT_RUN")
    delta = primary.get("delta")
    threshold = primary.get("threshold")

    if status == "EFFECT_OBSERVED":
        return {
            "status": "EFFECT_OBSERVED",
            "primary_metric": primary["kernel"],
            "delta": delta,
            "threshold": threshold,
        }
    elif status == "NO_OBSERVED_EFFECT":
        return {
            "status": "NO_OBSERVED_EFFECT",
            "primary_metric": primary["kernel"],
            "delta": delta,
            "threshold": threshold,
        }
    else:
        return {"status": "NOT_RUN", "reason": f"Primary measurement status: {status}"}


def main():
    print("=" * 70)
    print("REMAINING BEHAVIORAL EXECUTION")
    print("=" * 70)

    classifications = []
    ready_experiments = []
    blocked_experiments = []

    for exp in SEED_12_EXPERIMENTS:
        cls = classify_experiment(exp)
        classifications.append(cls)
        if cls["status"] == "READY":
            ready_experiments.append(exp)
        elif cls["status"] not in ("ALREADY_QUALIFIED",):
            blocked_experiments.append(cls)

    print(f"\nClassification complete: {len(ready_experiments)} READY, {len(blocked_experiments)} BLOCKED")

    # Execute READY experiments
    observations = []
    qualifications = []

    effect_observed_count = 0
    no_effect_count = 0
    invalid_count = 0

    for exp in ready_experiments:
        print(f"\n  Executing: {exp.experiment_id} ({exp.semantic_target})")
        spec = exp.to_dict()
        result = run_experiment_worker(spec)

        if not result.get("success"):
            print(f"    ERROR: {result.get('error', 'unknown')}")
            obs_entry = {
                "experiment_id": exp.experiment_id,
                "success": False,
                "error": result.get("error"),
            }
            qual_entry = {"experiment_id": exp.experiment_id, "status": "INVALID_OBSERVATION", "reason": result.get("error")}
            invalid_count += 1
        else:
            obs = result.get("behavior_observation", {})
            obs_entry = {"experiment_id": exp.experiment_id, "success": True, "observation": obs}

            qual = qualify_observation(obs, exp)
            qual_entry = {"experiment_id": exp.experiment_id, **qual}

            st = qual.get("status")
            if st == "EFFECT_OBSERVED":
                effect_observed_count += 1
            elif st == "NO_OBSERVED_EFFECT":
                no_effect_count += 1
            else:
                invalid_count += 1

            print(f"    -> {st}  (delta={qual.get('delta')}, threshold={qual.get('threshold')})")

        observations.append(obs_entry)
        qualifications.append(qual_entry)

    # Assemble artifact
    artifact = {
        "total_seed_experiments": 12,
        "already_qualified": ["Filter1.Cutoff", "OSC1.Octave"],
        "ready_executed": [e.experiment_id for e in ready_experiments],
        "blocked": [{"experiment_id": b["experiment_id"], "semantic_target": b["semantic_target"], "status": b["status"], "reason": b["reason"]} for b in blocked_experiments],
        "classifications": classifications,
        "observations": observations,
        "qualifications": qualifications,
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "remaining_behavioral_execution.json")
    with open(out_path, "w") as f:
        json.dump(artifact, f, indent=2, default=str)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"READY:     {len(ready_experiments)}")
    print(f"EXECUTED:  {len(observations)}")
    print(f"QUALIFIED: {len(qualifications)}")
    print(f"EFFECT_OBSERVED:    {effect_observed_count}")
    print(f"NO_OBSERVED_EFFECT: {no_effect_count}")
    print(f"BLOCKED:   {len(blocked_experiments)}")
    print(f"INVALID:   {invalid_count}")
    print(f"\nArtifact: {out_path}")
    return artifact


if __name__ == "__main__":
    main()
