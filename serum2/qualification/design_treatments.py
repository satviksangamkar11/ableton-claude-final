"""Design meaningful treatments based on baseline analysis.

Using the proven a3_behavior_harness mechanism, establish baselines
then design treatments that create real contrast.
"""

from serum2.evidence.spec import ExperimentSpec, Mutation, SINGLE_FIELD
from serum2.qualification.a3_behavior_harness import run_behavior_test
from serum2 import bridge
from serum2.evidence import epoch as epoch_mod

print("=" * 70)
print("TREATMENT DESIGN: BASELINE-AWARE BEHAVIORAL EXPERIMENTS")
print("=" * 70)
print()

# Load skeleton once
skeleton = bridge.capture_v8_skeleton(epoch_mod.SERUM_VST3)

# =========================================================================
# 1. OSC1.Level
# =========================================================================

print("-" * 70)
print("1. OSC1.Level")
print("-" * 70)
print()

spec = ExperimentSpec(
    experiment_id="osc1_level_design",
    mutations=[Mutation(target_path="VoiceOsc0.plainParams.kParamLevel", value=1.0, provenance="design")],
    prerequisites=[],
    isolation_level=SINGLE_FIELD,
    claim_subject="OSC1.Level",
    claim_predicate="causal_behavior",
)

print("Test 1A: Baseline (Level at default)")
result_base = run_behavior_test(
    experiment_id="osc1_level_baseline",
    target_path="VoiceOsc0.plainParams.kParamLevel",
    mutation_value=1.0,  # baseline (will be ignored since apply_mutations=False in build_arm)
    skeleton=skeleton,
    spec=spec,
    expected_direction="change",
    metric_name="overall_rms_db",
    effect_threshold=1.0,
    exercise_context=[],
)

baseline_rms = result_base.get("baseline_metric")
print(f"  Baseline RMS: {baseline_rms:.2f} dB")
print()

print("Test 1B: Treatment (Level = 0.0 for SILENCE)")
result_treat = run_behavior_test(
    experiment_id="osc1_level_silence",
    target_path="VoiceOsc0.plainParams.kParamLevel",
    mutation_value=0.0,  # MINIMUM to create strong contrast
    skeleton=skeleton,
    spec=spec,
    expected_direction="decrease",
    metric_name="overall_rms_db",
    effect_threshold=1.0,
    exercise_context=[],
)

treatment_rms = result_treat.get("mutated_metric")
delta_rms = result_treat.get("delta")
print(f"  Treatment RMS (Level=0.0): {treatment_rms:.2f} dB")
print(f"  Delta: {delta_rms:+.2f} dB")
print(f"  Status: {result_treat.get('status')}")
print()

# =========================================================================
# 2. Filter2.Cutoff
# =========================================================================

print("-" * 70)
print("2. Filter2.Cutoff")
print("-" * 70)
print()

spec2 = ExperimentSpec(
    experiment_id="filter2_cutoff_design",
    mutations=[Mutation(target_path="VoiceFilter1.plainParams.kParamFreq", value=0.1, provenance="design")],
    prerequisites=[],
    isolation_level=SINGLE_FIELD,
    claim_subject="Filter2.Cutoff",
    claim_predicate="causal_behavior",
)

print("Test 2A: Baseline (Filter2 at default, active)")
result2_base = run_behavior_test(
    experiment_id="filter2_baseline",
    target_path="VoiceFilter1.plainParams.kParamFreq",
    mutation_value=0.1,  # will be ignored
    skeleton=skeleton,
    spec=spec2,
    expected_direction="change",
    metric_name="spectral_centroid_hz",
    effect_threshold=200.0,
    exercise_context=[("Filter 2 On", 1.0)],
)

baseline_centroid = result2_base.get("baseline_metric")
print(f"  Baseline centroid: {baseline_centroid:.2f} Hz")
print(f"  (> 4000 Hz indicates Filter2 is already high-pass)")
print()

print("Test 2B: Treatment (Cutoff = 0.0 for LOW-PASS)")
result2_treat = run_behavior_test(
    experiment_id="filter2_lowpass",
    target_path="VoiceFilter1.plainParams.kParamFreq",
    mutation_value=0.0,  # MINIMUM (opposite direction from 0.9)
    skeleton=skeleton,
    spec=spec2,
    expected_direction="decrease",
    metric_name="spectral_centroid_hz",
    effect_threshold=200.0,
    exercise_context=[("Filter 2 On", 1.0)],
)

treatment_centroid = result2_treat.get("mutated_metric")
delta_centroid = result2_treat.get("delta")
print(f"  Treatment centroid (Cutoff=0.0): {treatment_centroid:.2f} Hz")
print(f"  Delta: {delta_centroid:+.2f} Hz")
print(f"  Status: {result2_treat.get('status')}")
print()

# =========================================================================
# 3. Env1.Attack
# =========================================================================

print("-" * 70)
print("3. Env1.Attack")
print("-" * 70)
print()

spec3 = ExperimentSpec(
    experiment_id="env1_attack_design",
    mutations=[Mutation(target_path="VoiceEnv0.plainParams.kParamAttackTime", value=0.9, provenance="design")],
    prerequisites=[],
    isolation_level=SINGLE_FIELD,
    claim_subject="Env1.Attack",
    claim_predicate="causal_behavior",
)

print("Test 3A: Baseline (Attack at default - likely FAST)")
result3_base = run_behavior_test(
    experiment_id="env1_attack_baseline",
    target_path="VoiceEnv0.plainParams.kParamAttackTime",
    mutation_value=0.9,  # will be ignored
    skeleton=skeleton,
    spec=spec3,
    expected_direction="change",
    metric_name="overall_rms_db",
    effect_threshold=1.0,
    exercise_context=[],
)

baseline_attack_rms = result3_base.get("baseline_metric")
print(f"  Baseline RMS: {baseline_attack_rms:.2f} dB")
print()

print("Test 3B: Treatment (Attack = 0.9 for SLOW attack)")
result3_treat = run_behavior_test(
    experiment_id="env1_slow_attack",
    target_path="VoiceEnv0.plainParams.kParamAttackTime",
    mutation_value=0.9,  # SLOW
    skeleton=skeleton,
    spec=spec3,
    expected_direction="change",
    metric_name="overall_rms_db",
    effect_threshold=1.0,
    exercise_context=[],
)

treatment_attack_rms = result3_treat.get("mutated_metric")
delta_attack = result3_treat.get("delta")
print(f"  Treatment RMS (Attack=0.9): {treatment_attack_rms:.2f} dB")
print(f"  Delta: {delta_attack:+.2f} dB")
print(f"  Status: {result3_treat.get('status')}")
print()

print("=" * 70)
print("SUMMARY: TREATMENT DESIGN RESULTS")
print("=" * 70)
print()
print("OSC1.Level (silence) delta: {:.2f} dB".format(delta_rms or 0))
print("Filter2.Cutoff (low-pass) delta: {:.2f} Hz".format(delta_centroid or 0))
print("Env1.Attack (slow) delta: {:.2f} dB".format(delta_attack or 0))

