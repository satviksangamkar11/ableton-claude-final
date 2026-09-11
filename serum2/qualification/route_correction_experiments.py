"""Route correction experiments for OSC1.Level and Env1.Attack.

Correct the CBOR paths, verify they exist, execute fresh experiments.
"""

from serum2.evidence.spec import ExperimentSpec, Mutation, SINGLE_FIELD
from serum2.qualification.a3_behavior_harness import run_behavior_test
from serum2 import bridge
from serum2.evidence import epoch as epoch_mod

print("=" * 70)
print("ROUTE CORRECTION: OSC1.Level + Env1.Attack")
print("=" * 70)
print()

skeleton = bridge.capture_v8_skeleton(epoch_mod.SERUM_VST3)
meta, body = skeleton

# =========================================================================
# VERIFY CORRECTED PATHS EXIST
# =========================================================================

print("-" * 70)
print("PATH VERIFICATION")
print("-" * 70)
print()

osc0_exists = "Oscillator0" in body
env0_exists = "Env0" in body

print("Oscillator0 exists: {}".format(osc0_exists))
print("Env0 exists: {}".format(env0_exists))
print()

if not osc0_exists or not env0_exists:
    print("[FATAL] Required paths do not exist in skeleton")
    exit(1)

print("[OK] Both corrected paths exist")
print()

# =========================================================================
# 1. OSC1.Level with corrected path
# =========================================================================

print("=" * 70)
print("1. OSC1.Level (CORRECTED PATH)")
print("=" * 70)
print()

spec_osc = ExperimentSpec(
    experiment_id="osc1_level_corrected_route",
    mutations=[
        Mutation(
            target_path="Oscillator0.plainParams.kParamLevel",
            value=0.0,
            provenance="route_correction",
        )
    ],
    prerequisites=[],
    isolation_level=SINGLE_FIELD,
    claim_subject="OSC1.Level",
    claim_predicate="causal_behavior",
)

print("Semantic target: OSC1.Level")
print("Old path: VoiceOsc0.plainParams.kParamLevel")
print("Corrected path: Oscillator0.plainParams.kParamLevel")
print("Treatment: 0.0 (SILENCE / minimum level)")
print()

result_osc = run_behavior_test(
    experiment_id="osc1_level_corrected_route",
    target_path="Oscillator0.plainParams.kParamLevel",
    mutation_value=0.0,
    skeleton=skeleton,
    spec=spec_osc,
    expected_direction="decrease",
    metric_name="overall_rms_db",
    effect_threshold=1.0,
    exercise_context=[],
)

print("RESULT:")
if result_osc.get("success"):
    print("  Status: {}".format(result_osc.get("status")))
    print("  Baseline RMS: {:.2f} dB".format(result_osc.get("baseline_metric", 0)))
    print("  Treatment RMS: {:.2f} dB".format(result_osc.get("mutated_metric", 0)))
    print("  Delta: {:+.2f} dB".format(result_osc.get("delta", 0)))
    print()

    if result_osc.get("delta", 0) < -1.0:
        print("  ROUTE CLASSIFICATION: ROUTE_VERIFIED")
        print("  Corrected path produced measurable effect!")
    else:
        print("  ROUTE CLASSIFICATION: ROUTE_EXISTS_BUT_CONTEXT_INACTIVE")
        print("  Path exists but mutation has no effect")
else:
    print("  [FAIL] {}".format(result_osc.get("error")))
    print("  ROUTE CLASSIFICATION: ROUTE_WRONG OR INACCESSIBLE")

print()

# =========================================================================
# 2. Env1.Attack with corrected path
# =========================================================================

print("=" * 70)
print("2. Env1.Attack (CORRECTED PATH)")
print("=" * 70)
print()

spec_env = ExperimentSpec(
    experiment_id="env1_attack_corrected_route",
    mutations=[
        Mutation(
            target_path="Env0.plainParams.kParamAttackTime",
            value=0.9,
            provenance="route_correction",
        )
    ],
    prerequisites=[],
    isolation_level=SINGLE_FIELD,
    claim_subject="Env1.Attack",
    claim_predicate="causal_behavior",
)

print("Semantic target: Env1.Attack")
print("Old path: VoiceEnv0.plainParams.kParamAttackTime")
print("Corrected path: Env0.plainParams.kParamAttackTime")
print("Treatment: 0.9 (SLOW attack / maximum attack time)")
print()

result_env = run_behavior_test(
    experiment_id="env1_attack_corrected_route",
    target_path="Env0.plainParams.kParamAttackTime",
    mutation_value=0.9,
    skeleton=skeleton,
    spec=spec_env,
    expected_direction="change",
    metric_name="overall_rms_db",
    effect_threshold=1.0,
    exercise_context=[],
)

print("RESULT:")
if result_env.get("success"):
    print("  Status: {}".format(result_env.get("status")))
    print("  Baseline RMS: {:.2f} dB".format(result_env.get("baseline_metric", 0)))
    print("  Treatment RMS: {:.2f} dB".format(result_env.get("mutated_metric", 0)))
    print("  Delta: {:+.2f} dB".format(result_env.get("delta", 0)))
    print()

    if abs(result_env.get("delta", 0)) > 1.0:
        print("  ROUTE CLASSIFICATION: ROUTE_VERIFIED")
        print("  Corrected path produced measurable effect!")
    else:
        print("  ROUTE CLASSIFICATION: ROUTE_EXISTS_BUT_CONTEXT_INACTIVE")
        print("  Path exists but mutation has no effect")
else:
    print("  [FAIL] {}".format(result_env.get("error")))
    print("  ROUTE CLASSIFICATION: ROUTE_WRONG OR INACCESSIBLE")

print()

# =========================================================================
# FINAL SUMMARY
# =========================================================================

print("=" * 70)
print("SUMMARY: DOES ROUTE CORRECTION ENABLE BEHAVIOR?")
print("=" * 70)
print()

osc_effect = result_osc.get("delta", 0)
env_effect = result_env.get("delta", 0)

print("OSC1.Level:")
print("  Corrected path: Oscillator0.plainParams.kParamLevel")
print("  Delta: {:+.2f} dB".format(osc_effect))
print("  Classification: {}".format(
    "ROUTE_VERIFIED" if osc_effect < -1.0 else "ROUTE_EXISTS_BUT_CONTEXT_INACTIVE"
))
print()

print("Env1.Attack:")
print("  Corrected path: Env0.plainParams.kParamAttackTime")
print("  Delta: {:+.2f} dB".format(env_effect))
print("  Classification: {}".format(
    "ROUTE_VERIFIED" if abs(env_effect) > 1.0 else "ROUTE_EXISTS_BUT_CONTEXT_INACTIVE"
))
print()

if osc_effect < -1.0 or abs(env_effect) > 1.0:
    print("[KEY FINDING] Correcting physical routes enabled real Serum behavior!")
else:
    print("[KEY FINDING] Even corrected paths produce zero/tiny effects.")
    print("              This suggests the controls may be structural-only or")
    print("              require different activation mechanisms.")
