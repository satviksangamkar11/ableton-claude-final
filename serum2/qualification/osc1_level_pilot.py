"""OSC1.Level Behavioral Qualification Pilot

Complete behavioral qualification for OSC1.Level, following the Filter1.Cutoff
pilot pattern: use exercise_context to activate OSC1 for both baseline and treatment.

Chain:
  target (OSC1.Level)
  -> frozen exercise context (OSC1 On=1.0, or equivalent)
  -> ExperimentSpec (SINGLE_FIELD, mutation: Oscillator0.plainParams.kParamLevel=0.0)
  -> baseline render (OSC1 active)
  -> treatment render (OSC1 active, level=0.0 for silence)
  -> overall_rms_db + spectral_centroid_hz measurement
  -> ExerciseQualification binding
"""

import json
from serum2 import bridge
from serum2.evidence import epoch as epoch_mod
from serum2.evidence.spec import ExperimentSpec, Mutation, SINGLE_FIELD
from serum2.qualification.a3_behavior_harness import run_behavior_test
from serum2.evidence.exercise_qualification import make_exercise_qualification

print("=" * 70)
print("OSC1.LEVEL BEHAVIORAL QUALIFICATION PILOT")
print("=" * 70)
print()

# =========================================================================
# TARGET DEFINITION
# =========================================================================

TARGET_SEMANTIC_ID = "OSC1.Level"
TARGET_CBOR_PATH = "Oscillator0.plainParams.kParamLevel"
EXPERIMENT_ID = "osc1_level_pilot_001"

# Mutation value: 0.0 (silence) to create maximum contrast with baseline
MUTATION_VALUE = 0.0

# Exercise context: Activate OSC1 for both arms
# Following the Filter1.Cutoff pattern: "Filter 1 On" = 1.0
# For OSC1, from MCP discovery: "A Enable" (parameter 16) is the enable control

# Start with "A Enable" (MCP host parameter name):
CONTEXT_KEYS_TO_TRY = [
    "A Enable",
    "OSC1 On",
    "Oscillator 1 On",
    "OSC 1 On",
    "Osc1 Enable",
]

FROZEN_CONTEXT = {CONTEXT_KEYS_TO_TRY[0]: 1.0}

# Measurement: Use RMS (amplitude) since reducing level should reduce amplitude
METRIC = "overall_rms_db"
EXPECTED_DIRECTION = "decrease"  # level 0.0 (silence) should decrease RMS
EFFECT_THRESHOLD_DB = 1.0        # dB — conservative; ~3dB expected for silence

print("Target:           {}".format(TARGET_SEMANTIC_ID))
print("CBOR path:        {}".format(TARGET_CBOR_PATH))
print("Mutation value:   {}".format(MUTATION_VALUE))
print("Exercise context: {}".format(FROZEN_CONTEXT))
print("Metric:           {}".format(METRIC))
print("Expected dir:     {}".format(EXPECTED_DIRECTION))
print("Threshold:        {} dB".format(EFFECT_THRESHOLD_DB))
print()

# =========================================================================
# BUILD SPEC
# =========================================================================

spec = ExperimentSpec(
    experiment_id=EXPERIMENT_ID,
    mutations=[
        Mutation(
            target_path=TARGET_CBOR_PATH,
            value=MUTATION_VALUE,
            provenance="osc1_level_pilot",
        )
    ],
    prerequisites=[],
    isolation_level=SINGLE_FIELD,
    claim_subject=TARGET_SEMANTIC_ID,
    claim_predicate="causal_behavior",
)

print("ExperimentSpec built.")
print("  isolation_level: {}".format(spec.isolation_level))
print("  mutations: {}".format([(m.target_path, m.value) for m in spec.mutations]))
print()

# =========================================================================
# LOAD SKELETON
# =========================================================================

print("Step 1: Capturing VST3 skeleton...")
skeleton = bridge.capture_v8_skeleton(epoch_mod.SERUM_VST3)
print("  skeleton captured.")
print()

# =========================================================================
# RUN TWO-ARM RENDER
# =========================================================================

print("Step 2: Running two-arm render with exercise context...")
print("  exercise_context applied to BOTH arms: {}".format(
    list(FROZEN_CONTEXT.items())))
print()

behavior_result = run_behavior_test(
    experiment_id=EXPERIMENT_ID,
    target_path=TARGET_CBOR_PATH,
    mutation_value=MUTATION_VALUE,
    skeleton=skeleton,
    spec=spec,
    expected_direction=EXPECTED_DIRECTION,
    metric_name=METRIC,
    effect_threshold=EFFECT_THRESHOLD_DB,
    exercise_context=list(FROZEN_CONTEXT.items()),
)

# =========================================================================
# ANALYZE RESULT
# =========================================================================

print("Step 3: Analyzing result...")
print()

status = behavior_result.get("status", "UNKNOWN")
baseline_metric = behavior_result.get("baseline_metric")
mutated_metric = behavior_result.get("mutated_metric")
delta = behavior_result.get("delta")

print("Baseline render:  {}".format(behavior_result.get("baseline_rendered")))
print("Treatment render: {}".format(behavior_result.get("mutated_rendered")))
print()

print("Baseline RMS:     {:.2f} dB".format(baseline_metric or 0))
print("Treatment RMS:    {:.2f} dB".format(mutated_metric or 0))
print("Delta:            {:+.2f} dB".format(delta or 0))
print("Status:           {}".format(status))
print()

if status == "EFFECT_OBSERVED":
    print("[OK] EFFECT OBSERVED!")
    print()
    print("=" * 70)
    print("OSC1.LEVEL PILOT: SUCCESS")
    print("=" * 70)
    print()
    print("Acceptance criteria:")
    print("  [OK] Context recorded: {}".format(list(FROZEN_CONTEXT.items())))
    print("  [OK] Baseline rendered: True")
    print("  [OK] Treatment rendered: True")
    print("  [OK] Single-field isolation: kParamLevel only")
    print("  [OK] Effect observed: {} dB delta".format(delta))
    print()

    # =========================================================
    # CREATE EXERCISE QUALIFICATION
    # =========================================================

    print("Creating ExerciseQualification...")
    print()

    exq = make_exercise_qualification(
        target_semantic_id=TARGET_SEMANTIC_ID,
        target_cbor_path=TARGET_CBOR_PATH,
        frozen_context=FROZEN_CONTEXT,
        mutation_value=MUTATION_VALUE,
        causal_measurement={
            "metric": METRIC,
            "baseline": baseline_metric,
            "treatment": mutated_metric,
            "delta": delta,
            "expected_direction": EXPECTED_DIRECTION,
            "observed_direction": behavior_result.get("observed_direction"),
            "threshold": EFFECT_THRESHOLD_DB,
            "status": status,
        },
        isolation_level="single_field",
        scope="single_run_non_reusable",
        experiment_id=EXPERIMENT_ID,
    )

    print("ExerciseQualification created:")
    print("  target: {}".format(exq.target_semantic_id))
    print("  status: {}".format(exq.causal_measurement.get("status")))
    print("  is_valid: {}".format(exq.is_valid))
    print()

    if exq.is_valid:
        print("[OK] ExerciseQualification is VALID")
        print()
        print("EVIDENCE SUMMARY:")
        print("  OSC1.Level is behaviorally observable when:")
        print("    1. Exercise context: {} activated for BOTH arms".format(FROZEN_CONTEXT))
        print("    2. Mutation: Oscillator0.plainParams.kParamLevel = 0.0")
        print("    3. Measurement: {} delta = {:.2f} dB".format(METRIC, delta))
        print()
        print("Proof complete. OSC1.Level → ExerciseQualification → BehaviorClaim")
        print()
    else:
        print("[FAIL] ExerciseQualification is NOT valid")
        print("Reasons:")
        for reason in exq.validation_errors:
            print("  - {}".format(reason))

else:
    print("[FAIL] NO EFFECT OBSERVED")
    print()
    print("Result: {}".format(behavior_result.get("reason")))
    print()

    if baseline_metric is None or baseline_metric <= -20:
        print("DIAGNOSIS: Baseline is still silent (RMS <= -20 dB)")
        print("           Exercise context '{}' did not activate OSC1.".format(
            list(FROZEN_CONTEXT.keys())[0]))
        print()
        print("NEXT: Try alternative context keys:")
        for key in CONTEXT_KEYS_TO_TRY[1:]:
            print("      - {}".format(key))
    else:
        print("DIAGNOSIS: Baseline is audible but mutation had no effect")
        print("           CBOR path may be wrong, or context insufficient")

print()
