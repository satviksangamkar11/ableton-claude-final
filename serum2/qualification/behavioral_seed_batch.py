"""12-control behavioral seed set qualification batch.

Runs ExerciseQualification protocol on 11 remaining high-value timbral controls
(Filter.Cutoff was the pilot, already done). Together they form the 12-control
behavioral seed set.

Each target uses the same chain:
  frozen exercise context
  -> ExperimentSpec (SINGLE_FIELD)
  -> baseline render
  -> treatment render
  -> objective measurement
  -> ExerciseQualification binding
  -> CAUSAL_VERIFIED / NO_OBSERVED_EFFECT / WRONG_DIRECTION / UNKNOWN

Two mutation adapters:
  cbor_body  - mutation applied via pathmerge to CBOR body (build_arm)
  host_param - mutation applied via baseline_host_context / mutated_host_context

For FX parameters (FXEQ, FXDistortion): the skeleton is pre-modified with a
real preset body's FXRack0 so both arms share the same FX context. Only the
specific FX parameter differs between arms.
"""

from __future__ import annotations

import copy
import json
import datetime
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from serum2 import bridge
from serum2.evidence import epoch as epoch_mod
from serum2.evidence.spec import ExperimentSpec, Mutation, SINGLE_FIELD
from serum2.evidence.exercise_qualification import make_exercise_qualification, ExerciseQualification

# Lazy-load heavy dependencies
def _get_run_behavior_test():
    from serum2.qualification.a3_behavior_harness import run_behavior_test
    return run_behavior_test

# ---------------------------------------------------------------------------
# Target definitions
# ---------------------------------------------------------------------------

@dataclass
class TargetDef:
    semantic_id: str
    experiment_id: str
    cbor_path: Optional[str]           # None = host_param adapter
    host_param_name: Optional[str]     # None = cbor_body adapter
    mutation_value: Any                # treatment value for CBOR path
    baseline_host_val: Optional[float] # for host_param adapter
    mutated_host_val: Optional[float]  # for host_param adapter
    exercise_context: List[Tuple[str, float]]  # shared both arms
    metric: str
    expected_direction: str
    effect_threshold: Optional[float]
    notes: str = ""
    fx_preset_path: Optional[str] = None  # if set, load this preset's FXRack0 into skeleton
    fx_shared_overrides: Optional[List[Tuple[str, Any]]] = None  # cbor_path overrides applied
        # to BOTH arms after FX injection, via pathmerge -- for FX effects with a body-level
        # (not host-param) wet/gate field, e.g. FXDistortion.kParamWet defaults 0.0


ALTAR_PRESET = r"C:\Users\Satvik\Documents\Xfer\Serum 2 Presets\Presets\Factory\Arp\ARP - Altar.SerumPreset"

TARGETS: List[TargetDef] = [

    # 1. Filter1.Resonance
    # Low cutoff + filter on → resonance peak at the cutoff frequency is audible
    # High resonance raises RMS significantly (self-oscillation effect)
    TargetDef(
        semantic_id="Filter1.Resonance",
        experiment_id="filter1_reso_pilot_001",
        cbor_path="VoiceFilter0.plainParams.kParamReso",
        host_param_name=None,
        mutation_value=0.9,
        baseline_host_val=None,
        mutated_host_val=None,
        exercise_context=[("Filter 1 On", 1.0), ("Filter 1 Freq", 0.15)],
        metric="overall_rms_db",
        expected_direction="increase",
        effect_threshold=0.5,
        notes="Low cutoff (0.15) makes resonance peak audible. High reso -> self-osc peak adds energy.",
    ),

    # 2. Filter2.Cutoff
    # Same principle as Filter1.Cutoff: higher cutoff passes more highs -> centroid up
    TargetDef(
        semantic_id="Filter2.Cutoff",
        experiment_id="filter2_cutoff_pilot_001",
        cbor_path="VoiceFilter1.plainParams.kParamFreq",
        host_param_name=None,
        mutation_value=0.9,
        baseline_host_val=None,
        mutated_host_val=None,
        exercise_context=[("Filter 2 On", 1.0)],
        metric="spectral_centroid_hz",
        expected_direction="increase",
        effect_threshold=200.0,
        notes="Filter 2 must be active. Treatment=0.9 passes much more high-frequency content.",
    ),

    # NOTE: OSC1.Level, Env1.Attack, OSC2.Level, OSC3.Level, FXEQ.Freq1 are
    # PROVEN (CAUSAL_VERIFIED) and are now sourced from
    # EXERCISE_CONTEXT_REGISTRY_V1.json via load_targets_from_registry()
    # below, instead of being duplicated here. See TARGETS composition at
    # the bottom of this section.

    # 4. OSC1.Fine (OSC1 pitch detune via fine tune)
    # Fine pitch shift of OSC A. Raising fine tune to 1.0 = +100 cents = +1 semitone.
    # All harmonics shift up -> spectral centroid increases.
    # Default: VoiceOsc0.plainParams.kParamFine absent (0 cents offset)
    # Treatment: kParamFine = 1.0 (+100 cents)
    TargetDef(
        semantic_id="OSC1.Detune",
        experiment_id="osc1_fine_pilot_001",
        cbor_path="VoiceOsc0.plainParams.kParamFine",
        host_param_name=None,
        mutation_value=1.0,
        baseline_host_val=None,
        mutated_host_val=None,
        exercise_context=[],
        metric="spectral_centroid_hz",
        expected_direction="increase",
        effect_threshold=50.0,
        notes="A Fine (index 25). Treatment=1.0 shifts OSC A up 100 cents. All harmonics shift up.",
    ),

    # 5. OSC2.Fine (OSC2 pitch detune via fine tune)
    TargetDef(
        semantic_id="OSC2.Detune",
        experiment_id="osc2_fine_pilot_001",
        cbor_path="VoiceOsc1.plainParams.kParamFine",
        host_param_name=None,
        mutation_value=1.0,
        baseline_host_val=None,
        mutated_host_val=None,
        exercise_context=[("B Enable", 1.0)],
        metric="spectral_centroid_hz",
        expected_direction="increase",
        effect_threshold=50.0,
        notes="B Fine (index 80). OSC B must be enabled. Treatment=1.0 shifts up 100 cents.",
    ),

    # 7. Env1.Release
    # Long release (0.9) means sound persists after note-off.
    # Note: 0.5s, render: 2.0s. Last 1.5s: baseline silent, treatment has tail.
    # Metric: overall_rms_db. Treatment has more total energy.
    TargetDef(
        semantic_id="Env1.Release",
        experiment_id="env1_release_pilot_001",
        cbor_path="Env0.plainParams.kParamRelease",
        host_param_name=None,
        mutation_value=0.9,
        baseline_host_val=None,
        mutated_host_val=None,
        exercise_context=[],
        metric="overall_rms_db",
        expected_direction="increase",
        effect_threshold=0.5,
        notes="Long release makes sound persist 1.5s after note-off in 2s render.",
    ),

    # 8. LFO1.Rate
    # LFO1 rate without a modulation target -> expected NO_OBSERVED_EFFECT.
    # This is a valid result: it tells us LFO.Rate requires an active modulation to be exercisable.
    # The ExerciseQualification will be is_valid=False (NO_OBSERVED_EFFECT, not EFFECT_OBSERVED).
    # Documenting this finding is useful for the behavioral vocabulary.
    TargetDef(
        semantic_id="LFO1.Rate",
        experiment_id="lfo1_rate_pilot_001",
        cbor_path="LFO0.plainParams.kParamRate",
        host_param_name=None,
        mutation_value=0.9,
        baseline_host_val=None,
        mutated_host_val=None,
        exercise_context=[],
        metric="overall_rms_db",
        expected_direction="change",
        effect_threshold=0.5,
        notes="Without a modulation target, LFO rate has no audible effect. "
              "Expected NO_OBSERVED_EFFECT — valid finding: needs modulation assignment context.",
    ),

    # 9. Filter1.Drive
    # Drive adds saturation/harmonics. More drive -> more energy, brighter.
    # Exercise context: filter must be on so drive is in the signal path.
    TargetDef(
        semantic_id="Filter1.Drive",
        experiment_id="filter1_drive_pilot_001",
        cbor_path="VoiceFilter0.plainParams.kParamDrive",
        host_param_name=None,
        mutation_value=0.9,
        baseline_host_val=None,
        mutated_host_val=None,
        exercise_context=[("Filter 1 On", 1.0)],
        metric="overall_rms_db",
        expected_direction="increase",
        effect_threshold=0.5,
        notes="Filter drive adds saturation. Filter must be on. High drive adds energy/harmonics.",
    ),

    # 13. Env2.Attack (mirrors Env1.Attack pattern: Env1 body index = Env2 in UI, 0-indexed)
    TargetDef(
        semantic_id="Env2.Attack",
        experiment_id="env2_attack_pilot_001",
        cbor_path="Env1.plainParams.kParamAttack",
        host_param_name=None,
        mutation_value=0.9,
        baseline_host_val=None,
        mutated_host_val=None,
        exercise_context=[],
        metric="overall_rms_db",
        expected_direction="decrease",
        effect_threshold=0.5,
        notes="Env1 = Env2 in UI (0-indexed), mirrors Env0/Env1.Attack. Slow attack=0.9 reduces energy in 2s render window.",
    ),

]


# ---------------------------------------------------------------------------
# Registry-driven targets (PROVEN entries -- single source of truth)
# ---------------------------------------------------------------------------

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "EXERCISE_CONTEXT_REGISTRY_V1.json")


def load_targets_from_registry(status: str = "PROVEN") -> List[TargetDef]:
    """Build TargetDef list from EXERCISE_CONTEXT_REGISTRY_V1.json entries
    matching the given status. This is the authoritative source for
    already-proven capabilities -- do not hard-code them a second time here.
    """
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    targets: List[TargetDef] = []
    for entry in registry["entries"]:
        if entry.get("status") != status:
            continue
        mut = entry.get("target_mutation")
        if mut is None:
            continue  # structural-only entries (e.g. MODULATION_ROUTE) have no render-based TargetDef

        adapter = mut["adapter"]
        if adapter == "compound":
            continue  # structural-only; not a render-based TargetDef

        exercise_context = [tuple(pair) for pair in entry.get("exercise_context", [])]
        fx_preset_path = None
        if entry.get("fx_preset_injection"):
            fx_preset_path = entry["fx_preset_injection"]["preset_path"]

        if adapter == "host_param":
            targets.append(TargetDef(
                semantic_id=entry["capability_id"],
                experiment_id=entry["capability_id"].lower().replace(".", "_") + "_registry",
                cbor_path=None,
                host_param_name=mut["path_or_param"],
                mutation_value=None,
                baseline_host_val=mut["baseline_value"],
                mutated_host_val=mut["treatment_value"],
                exercise_context=exercise_context,
                metric=entry["measurement_template"]["metric"],
                expected_direction=entry["measurement_template"]["expected_direction"],
                effect_threshold=entry["measurement_template"]["threshold"],
                notes="[registry:{}] {}".format(entry["status"], entry.get("notes", "")),
                fx_preset_path=fx_preset_path,
            ))
        else:  # cbor_body
            targets.append(TargetDef(
                semantic_id=entry["capability_id"],
                experiment_id=entry["capability_id"].lower().replace(".", "_") + "_registry",
                cbor_path=mut["path_or_param"],
                host_param_name=None,
                mutation_value=mut["treatment_value"],
                baseline_host_val=None,
                mutated_host_val=None,
                exercise_context=exercise_context,
                metric=entry["measurement_template"]["metric"],
                expected_direction=entry["measurement_template"]["expected_direction"],
                effect_threshold=entry["measurement_template"]["threshold"],
                notes="[registry:{}] {}".format(entry["status"], entry.get("notes", "")),
                fx_preset_path=fx_preset_path,
            ))
    return targets


# Final TARGETS = registry-sourced PROVEN targets + still-exploratory/BLOCKED
# hard-coded targets above (kept hard-coded because they are not yet
# promoted to PROVEN and must not be silently treated as reusable truth).
TARGETS: List[TargetDef] = load_targets_from_registry("PROVEN") + TARGETS


def run_golden_regression(verbose: bool = True) -> Tuple[bool, List[dict]]:
    """Run every registry PROVEN target and confirm it remains CAUSAL_VERIFIED.

    Returns (all_passed, results). Must be run -- and must pass -- before any
    new capability is scaled from the registry-driven pattern.
    """
    import gc

    golden_targets = load_targets_from_registry("PROVEN")
    if verbose:
        print("\n" + "=" * 70)
        print("GOLDEN REGRESSION -- {} registry PROVEN targets".format(len(golden_targets)))
        print("=" * 70)

    results = []
    all_passed = True
    for i, t in enumerate(golden_targets):
        gc.collect()
        if verbose:
            print("\n[{}/{}] {}".format(i + 1, len(golden_targets), t.semantic_id))
        skeleton = bridge.capture_v8_skeleton(epoch_mod.SERUM_VST3)
        r = run_one(t, skeleton, verbose=verbose)
        results.append(r)
        status = r["behavior_result"].get("status")
        if status != "CAUSAL_VERIFIED":
            all_passed = False
            if verbose:
                print("  *** GOLDEN REGRESSION FAILURE: {} status={} (expected CAUSAL_VERIFIED)".format(
                    t.semantic_id, status))
        del skeleton
        gc.collect()

    if verbose:
        print("\n" + "-" * 70)
        print("Golden regression: {}/{} PASSED".format(
            sum(1 for r in results if r["behavior_result"].get("status") == "CAUSAL_VERIFIED"),
            len(golden_targets)))
        print("=" * 70)

    return all_passed, results


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def _build_spec(t: TargetDef) -> ExperimentSpec:
    """Build ExperimentSpec. Empty mutations for host_param adapter."""
    if t.cbor_path is not None:
        mutations = [
            Mutation(
                target_path=t.cbor_path,
                value=t.mutation_value,
                provenance="behavioral_seed_batch",
            )
        ]
    else:
        mutations = []

    return ExperimentSpec(
        experiment_id=t.experiment_id,
        mutations=mutations,
        prerequisites=[],
        isolation_level=SINGLE_FIELD,
        claim_subject=t.semantic_id,
        claim_predicate="causal_behavior",
    )


def _load_fx_skeleton(base_skeleton: tuple, preset_path: str,
                       shared_overrides: Optional[List[Tuple[str, Any]]] = None) -> tuple:
    """Inject FXRack0 from a preset into the base skeleton. Returns modified skeleton.

    shared_overrides: optional list of (cbor_path, value) applied via pathmerge
    AFTER injection, to BOTH arms identically (e.g. forcing an FX slot's
    kParamWet gate on, mirroring the host-param exercise_context mechanism
    for FX fields that have no host parameter).
    """
    from serum2 import codec, pathmerge
    _, preset_body = codec.load_preset_file(preset_path)
    meta = copy.deepcopy(base_skeleton[0])
    body = copy.deepcopy(base_skeleton[1])
    body["FXRack0"] = copy.deepcopy(preset_body["FXRack0"])
    for path, value in (shared_overrides or []):
        pathmerge.apply_path_value(body, path, value)
    return (meta, body)


def run_one(t: TargetDef, skeleton: tuple, verbose: bool = True) -> dict:
    """Run one ExerciseQualification pilot. Returns result dict."""
    if verbose:
        print("\n  [{}]  {}".format(t.experiment_id, t.semantic_id))
        print("  adapter: {}".format("host_param" if t.cbor_path is None else "cbor_body"))
        print("  metric:  {}".format(t.metric))
        print("  expected: {}".format(t.expected_direction))
        if t.exercise_context:
            print("  exercise_context: {}".format(t.exercise_context))

    # Possibly inject FX preset body
    active_skeleton = skeleton
    if t.fx_preset_path:
        active_skeleton = _load_fx_skeleton(skeleton, t.fx_preset_path, t.fx_shared_overrides)
        if verbose:
            print("  fx_preset: {}".format(os.path.basename(t.fx_preset_path)))
            if t.fx_shared_overrides:
                print("  fx_shared_overrides: {}".format(t.fx_shared_overrides))

    spec = _build_spec(t)

    # For host_param adapter, arm-specific contexts carry the mutation
    baseline_host_ctx = list(t.exercise_context)
    mutated_host_ctx = list(t.exercise_context)

    if t.cbor_path is None:
        # host_param adapter: differ only in the one param value
        baseline_host_ctx = list(t.exercise_context) + [(t.host_param_name, t.baseline_host_val)]
        mutated_host_ctx = list(t.exercise_context) + [(t.host_param_name, t.mutated_host_val)]
        exercise_ctx = []
    else:
        # cbor_body adapter: exercise_context shared, arm contexts identical
        exercise_ctx = list(t.exercise_context)
        baseline_host_ctx = []
        mutated_host_ctx = []

    run_behavior_test = _get_run_behavior_test()

    behavior_result = run_behavior_test(
        experiment_id=t.experiment_id,
        target_path=t.cbor_path or t.host_param_name,
        mutation_value=t.mutation_value if t.cbor_path else t.mutated_host_val,
        skeleton=active_skeleton,
        spec=spec,
        expected_direction=t.expected_direction,
        metric_name=t.metric,
        effect_threshold=t.effect_threshold,
        exercise_context=exercise_ctx,
        baseline_host_context=baseline_host_ctx,
        mutated_host_context=mutated_host_ctx,
    )

    if verbose:
        status = behavior_result.get("status", "UNKNOWN")
        baseline = behavior_result.get("baseline_metric")
        mutated = behavior_result.get("mutated_metric")
        unit = "Hz" if "centroid" in t.metric else "dB"
        print("  status: {}".format(status))
        if baseline is not None and mutated is not None:
            delta = mutated - baseline
            print("  baseline: {:.1f} {}".format(baseline, unit))
            print("  mutated:  {:.1f} {}".format(mutated, unit))
            print("  delta:    {:+.1f} {}".format(delta, unit))
        if behavior_result.get("error_traceback"):
            print("  ERROR:", behavior_result.get("reason"))

    # Build ExerciseQualification
    frozen_ctx = dict(t.exercise_context)
    if t.cbor_path is None:
        # Record the contrast for host_param case
        frozen_ctx["_baseline_{}".format(t.host_param_name)] = t.baseline_host_val
        frozen_ctx["_mutated_{}".format(t.host_param_name)] = t.mutated_host_val

    eq = make_exercise_qualification(
        target_semantic_id=t.semantic_id,
        target_cbor_path=t.cbor_path or "host_param:{}".format(t.host_param_name),
        frozen_context=frozen_ctx,
        mutation_value=t.mutation_value if t.cbor_path else t.mutated_host_val,
        experiment_id=t.experiment_id,
        behavior_result=behavior_result,
    )

    if verbose:
        print("  is_valid: {}".format(eq.is_valid))

    acceptance = {
        "baseline_rendered": bool(behavior_result.get("baseline_rendered")),
        "mutated_rendered": bool(behavior_result.get("mutated_rendered")),
        "single_field_isolation": eq.isolation_level == SINGLE_FIELD,
        "effect_observed": eq.causal_measurement.status == "EFFECT_OBSERVED",
        "exercise_qualification_valid": eq.is_valid,
    }
    chain_valid = all(acceptance.values())

    return {
        "semantic_id": t.semantic_id,
        "experiment_id": t.experiment_id,
        "exercise_qualification": eq,
        "behavior_result": behavior_result,
        "acceptance": acceptance,
        "chain_valid": chain_valid,
        "notes": t.notes,
    }


def run_batch(verbose: bool = True) -> List[dict]:
    """Run all 11 remaining pilots. Returns list of result dicts.

    Captures skeleton fresh for each target to avoid resource accumulation.
    """
    import gc

    if verbose:
        print("\n" + "=" * 70)
        print("BEHAVIORAL SEED BATCH — 11 REMAINING TARGETS")
        print("=" * 70)

    results = []
    for i, t in enumerate(TARGETS):
        gc.collect()
        if verbose:
            print("\n[{}/{}] Capturing skeleton and running {}".format(
                i + 1, len(TARGETS), t.semantic_id))

        skeleton = bridge.capture_v8_skeleton(epoch_mod.SERUM_VST3)
        r = run_one(t, skeleton, verbose=verbose)
        results.append(r)

        # Cleanup
        del skeleton
        gc.collect()

    return results


def save_batch_evidence(results: List[dict], out_path: str = None) -> str:
    if out_path is None:
        out_path = os.path.join(
            os.path.dirname(__file__),
            "A_BEHAVIORAL_SEED_BATCH_EVIDENCE.json",
        )

    summary = []
    for r in results:
        eq = r["exercise_qualification"]
        br = r["behavior_result"]
        unit = "Hz" if "centroid" in (br.get("metric_name") or "") else "dB"
        summary.append({
            "semantic_id": r["semantic_id"],
            "experiment_id": r["experiment_id"],
            "chain_valid": r["chain_valid"],
            "status": br.get("status"),
            "baseline_metric": br.get("baseline_metric"),
            "mutated_metric": br.get("mutated_metric"),
            "delta": br.get("delta"),
            "metric": br.get("metric_name"),
            "unit": unit,
            "observed_direction": br.get("observed_direction"),
            "exercise_qualification_valid": eq.is_valid,
            "scope": eq.scope,
            "notes": r.get("notes", ""),
        })

    payload = {
        "batch": "12-Control Behavioral Seed Set",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "filter_cutoff_pilot": "serum2/qualification/A_FILTER_CUTOFF_PILOT_EVIDENCE.json",
        "targets_attempted": len(results),
        "chain_valid_count": sum(1 for r in results if r["chain_valid"]),
        "summary": summary,
        "full_results": [
            {
                "semantic_id": r["semantic_id"],
                "exercise_qualification": r["exercise_qualification"].to_dict(),
                "behavior_result_raw": {
                    k: v for k, v in r["behavior_result"].items()
                    if k not in ("error_traceback",)
                },
                "acceptance": r["acceptance"],
            }
            for r in results
        ],
    }

    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    return out_path


def print_matrix(results: List[dict]) -> None:
    print("\n" + "=" * 70)
    print("BEHAVIORAL SEED MATRIX (11 targets)")
    print("=" * 70)
    print("{:<20} {:<20} {:>8} {:<8} {:<10}".format(
        "target", "status", "delta", "unit", "valid"))
    print("-" * 70)

    # Include the pilot result for display
    print("{:<20} {:<20} {:>8} {:<8} {:<10}".format(
        "Filter.Cutoff", "CAUSAL_VERIFIED", "+2684", "Hz", "True"))

    for r in results:
        br = r["behavior_result"]
        eq = r["exercise_qualification"]
        metric = br.get("metric_name", "")
        unit = "Hz" if "centroid" in metric else "dB"
        delta_raw = br.get("delta")
        delta_str = "{:+.0f}".format(delta_raw) if delta_raw is not None else "N/A"
        print("{:<20} {:<20} {:>8} {:<8} {:<10}".format(
            r["semantic_id"],
            br.get("status", "UNKNOWN"),
            delta_str,
            unit,
            str(eq.is_valid),
        ))

    valid_count = sum(1 for r in results if r["exercise_qualification"].is_valid)
    print("-" * 70)
    print("Chain valid (including pilot): {}/12".format(valid_count + 1))


if __name__ == "__main__":
    results = run_batch(verbose=True)
    print_matrix(results)
    path = save_batch_evidence(results)
    print("\nEvidence saved to: {}".format(path))
