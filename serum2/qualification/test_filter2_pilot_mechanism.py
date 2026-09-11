"""Test Filter2.Cutoff using the exact pilot mechanism that works for Filter1.Cutoff.

This isolates whether the problem is:
A) The mechanism itself (both should fail)
B) The specific parameter/control (Filter2 has different behavior)
C) The architecture (pilot mechanism works, new worker doesn't)
"""

from serum2.evidence.spec import ExperimentSpec, Mutation, SINGLE_FIELD
from serum2.qualification.a3_behavior_harness import run_behavior_test
from serum2 import bridge
from serum2.evidence import epoch as epoch_mod

print("=" * 70)
print("TESTING FILTER2.CUTOFF WITH PILOT MECHANISM")
print("=" * 70)
print()

# Load skeleton (same as pilot)
skeleton = bridge.capture_v8_skeleton(epoch_mod.SERUM_VST3)

# Build ExperimentSpec (same structure as pilot)
spec = ExperimentSpec(
    experiment_id="filter2_cutoff_pilot_test",
    mutations=[
        Mutation(
            target_path="VoiceFilter1.plainParams.kParamFreq",  # Filter2
            value=0.9,  # high cutoff (original seed value)
            provenance="pilot_mechanism_test",
        )
    ],
    prerequisites=[],
    isolation_level=SINGLE_FIELD,
    claim_subject="Filter2.Cutoff",
    claim_predicate="causal_behavior",
)

# Run using pilot mechanism
print("Using a3_behavior_harness.run_behavior_test (pilot mechanism)...")
print("  target_path: VoiceFilter1.plainParams.kParamFreq")
print("  mutation_value: 0.9")
print("  exercise_context: [('Filter 2 On', 1.0)]")
print()

result = run_behavior_test(
    experiment_id="filter2_cutoff_pilot_test",
    target_path="VoiceFilter1.plainParams.kParamFreq",
    mutation_value=0.9,
    skeleton=skeleton,
    spec=spec,
    expected_direction="increase",
    metric_name="spectral_centroid_hz",
    effect_threshold=200.0,
    exercise_context=[("Filter 2 On", 1.0)],
)

print("RESULT:")
print("  status:", result.get("status"))
print("  baseline_centroid: {:.2f} Hz".format(result.get("baseline_metric")))
print("  mutated_centroid:  {:.2f} Hz".format(result.get("mutated_metric")))
print("  delta: {:+.2f} Hz".format(result.get("delta")))
print()

if result.get("delta", 0) > 50:
    print("[SUCCESS] Pilot mechanism produces measurable effect for Filter2.Cutoff")
else:
    print("[FAIL] Pilot mechanism produces zero/tiny effect for Filter2.Cutoff")
    print("       This suggests the parameter itself (Filter2.Cutoff) doesn't work,")
    print("       NOT the mechanism.")

EOF
