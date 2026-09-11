"""Corrected seed experiments based on measured baselines.

Use actual measurement results to guide treatment value selection.
Where experiments showed zero or tiny deltas, the treatment value
was likely close to or identical to the baseline. Invert the strategy.
"""

from serum2.qualification.behavior_experiment import (
    BehaviorExperiment,
    MeasurementPlan,
)


# Based on measured baselines from existing experiments:
# Filter1.Resonance: baseline centroid 463.09 Hz, delta +13.78 Hz
#   → resonance effect is small; try higher resonance value
#
# Filter2.Cutoff: baseline centroid 4378.13 Hz (VERY HIGH), delta +0.00 Hz
#   → Filter2 already high-pass; try LOW cutoff (0.1 or 0.2)
#
# OSC1.Level: baseline RMS -23.65 dB, delta +0.00 dB
#   → Level already at max (1.0); try LOW level (0.0 or 0.1)
#
# OSC1.Detune: baseline centroid 463.09 Hz, delta +0.00 Hz
#   → No detune at baseline; try HIGHER detune (but measured same)
#   → Try aggressive detune (0.8 or 0.9)
#
# Env1.Attack: baseline RMS -23.65 dB, delta +0.00 dB
#   → Attack already fast; try SLOW attack (0.8 or 0.9)
#
# Env1.Release: baseline RMS -23.65 dB, delta +0.00 dB
#   → Release already fast; try SLOW release (0.8 or 0.9)
#
# Filter1.Drive: baseline RMS -23.65 dB, delta +0.34 dB
#   → Drive effect measured; try HIGHER drive (was 1.0, try 0.8? or keep exploring)


FILTER1_RESONANCE_CORRECTED = BehaviorExperiment(
    experiment_id="diag_filter1_resonance_corrected_001",
    semantic_target="Filter1.Resonance",
    operation="SET_PARAMETER",
    context={"Filter 1 On": 1.0},
    context_provenance="filter must be active to exercise resonance",
    treatment_cbor_path="VoiceFilter0.plainParams.kParamReso",
    treatment_cbor_value=0.1,  # Try LOW resonance (was 0.9)
    measurement_plan=(
        MeasurementPlan(
            name="spectral_centroid_hz",
            kernel="spectral_centroid_hz",
            threshold=50.0,  # Lower threshold for small effects
        ),
        MeasurementPlan(
            name="overall_rms_db",
            kernel="rms_db",
            threshold=0.5,
        ),
    ),
    expected_outcome="EFFECT_OBSERVED",
    expected_direction="decrease",
    notes="Resonance with low peak (inverse of prior attempt). "
          "Baseline: kParamReso at default. Treatment: 0.1 (low resonance).",
)

FILTER2_CUTOFF_CORRECTED = BehaviorExperiment(
    experiment_id="diag_filter2_cutoff_corrected_001",
    semantic_target="Filter2.Cutoff",
    operation="SET_PARAMETER",
    context={"Filter 2 On": 1.0},
    context_provenance="filter must be active; baseline shows Filter2 already high-pass",
    treatment_cbor_path="VoiceFilter1.plainParams.kParamFreq",
    treatment_cbor_value=0.1,  # Try LOW cutoff (was 0.9, which produced zero change)
    measurement_plan=(
        MeasurementPlan(
            name="spectral_centroid_hz",
            kernel="spectral_centroid_hz",
            threshold=200.0,
        ),
        MeasurementPlan(
            name="overall_rms_db",
            kernel="rms_db",
            threshold=0.5,
        ),
    ),
    expected_outcome="EFFECT_OBSERVED",
    expected_direction="decrease",
    notes="Filter2 baseline shows 4378 Hz centroid (very high-pass). "
          "Mutation to 0.9 was no-op. Try 0.1 (low-pass) for contrast.",
)

OSC1_LEVEL_CORRECTED = BehaviorExperiment(
    experiment_id="diag_osc1_level_corrected_001",
    semantic_target="OSC1.Level",
    operation="SET_PARAMETER",
    context={},
    context_provenance="level is independent",
    treatment_cbor_path="VoiceOsc0.plainParams.kParamLevel",
    treatment_cbor_value=0.0,  # Try ZERO level (was 1.0, which produced zero change)
    measurement_plan=(
        MeasurementPlan(
            name="overall_rms_db",
            kernel="rms_db",
            threshold=2.0,
        ),
        MeasurementPlan(
            name="tail_rms_db",
            kernel="tail_rms_db",
            threshold=1.0,
        ),
    ),
    expected_outcome="EFFECT_OBSERVED",
    expected_direction="decrease",
    notes="Baseline RMS -23.65 dB with Level=1.0 (already max). "
          "Treatment: Level=0.0 (silence) for strong contrast.",
)

OSC1_DETUNE_CORRECTED = BehaviorExperiment(
    experiment_id="diag_osc1_detune_corrected_001",
    semantic_target="OSC1.Detune",
    operation="SET_PARAMETER",
    context={},
    context_provenance="detune works independently",
    treatment_cbor_path="VoiceOsc0.plainParams.kParamDetune",
    treatment_cbor_value=0.0,  # Try ZERO detune (inverse of 0.5)
    measurement_plan=(
        MeasurementPlan(
            name="spectral_centroid_hz",
            kernel="spectral_centroid_hz",
            threshold=50.0,
        ),
        MeasurementPlan(
            name="overall_rms_db",
            kernel="rms_db",
            threshold=1.0,
        ),
    ),
    expected_outcome="EFFECT_OBSERVED",
    expected_direction="change",
    notes="Prior attempt (0.5) showed zero change. Try 0.0 (exact unison). "
          "This may reveal if baseline has intrinsic detune.",
)

ENV1_ATTACK_CORRECTED = BehaviorExperiment(
    experiment_id="diag_env1_attack_corrected_001",
    semantic_target="Env1.Attack",
    operation="SET_PARAMETER",
    context={},
    context_provenance="envelope attack is independent",
    treatment_cbor_path="VoiceEnv0.plainParams.kParamAttackTime",
    treatment_cbor_value=0.9,  # Try SLOW attack (was 0.1, which produced zero change)
    measurement_plan=(
        MeasurementPlan(
            name="overall_rms_db",
            kernel="rms_db",
            threshold=1.0,
        ),
        MeasurementPlan(
            name="spectral_centroid_hz",
            kernel="spectral_centroid_hz",
            threshold=100.0,
        ),
    ),
    expected_outcome="CONDITIONAL",
    expected_direction="change",
    notes="Fast attack (0.1) showed no effect. Try 0.9 (very slow). "
          "Effect depends on whether envelope routes to filter/level.",
)

ENV1_RELEASE_CORRECTED = BehaviorExperiment(
    experiment_id="diag_env1_release_corrected_001",
    semantic_target="Env1.Release",
    operation="SET_PARAMETER",
    context={},
    context_provenance="envelope release is independent",
    treatment_cbor_path="VoiceEnv0.plainParams.kParamReleaseTime",
    treatment_cbor_value=0.9,  # Try SLOW release (was 0.1, which produced zero change)
    measurement_plan=(
        MeasurementPlan(
            name="overall_rms_db",
            kernel="rms_db",
            threshold=0.5,
        ),
        MeasurementPlan(
            name="spectral_centroid_hz",
            kernel="spectral_centroid_hz",
            threshold=100.0,
        ),
    ),
    expected_outcome="CONDITIONAL",
    expected_direction="change",
    notes="Fast release (0.1) showed no effect. Try 0.9 (very slow). "
          "Render window may not capture tail if release extends beyond 2.0s.",
)

FILTER1_DRIVE_CORRECTED = BehaviorExperiment(
    experiment_id="diag_filter1_drive_corrected_001",
    semantic_target="Filter1.Drive",
    operation="SET_PARAMETER",
    context={"Filter 1 On": 1.0},
    context_provenance="filter must be active to apply drive",
    treatment_cbor_path="VoiceFilter0.plainParams.kParamDrive",
    treatment_cbor_value=0.0,  # Try ZERO drive (inverse of 1.0)
    measurement_plan=(
        MeasurementPlan(
            name="overall_rms_db",
            kernel="rms_db",
            threshold=1.0,
        ),
        MeasurementPlan(
            name="spectral_centroid_hz",
            kernel="spectral_centroid_hz",
            threshold=200.0,
        ),
    ),
    expected_outcome="EFFECT_OBSERVED",
    expected_direction="decrease",
    notes="Prior drive=1.0 showed +0.34 dB (small effect). "
          "Try drive=0.0 for inverse contrast.",
)


DIAGNOSTIC_EXPERIMENTS = (
    FILTER1_RESONANCE_CORRECTED,
    FILTER2_CUTOFF_CORRECTED,
    OSC1_LEVEL_CORRECTED,
    OSC1_DETUNE_CORRECTED,
    ENV1_ATTACK_CORRECTED,
    ENV1_RELEASE_CORRECTED,
    FILTER1_DRIVE_CORRECTED,
)


if __name__ == "__main__":
    print("DIAGNOSTIC SEED EXPERIMENTS (CORRECTED)")
    print("=" * 70)
    print()
    print("Based on measured baselines from prior seed batch:")
    print()

    for i, exp in enumerate(DIAGNOSTIC_EXPERIMENTS, 1):
        exp.validate()
        print("[{:2d}] {}".format(i, exp.semantic_target))
        print("     CBOR: {} = {}".format(exp.treatment_cbor_path, exp.treatment_cbor_value))
        print("     Notes: {}".format(exp.notes))
        print()

    import json
    print("All experiments validated OK")
    print()
    print("Ready for execution: run_seed_diagnostics_corrected.py")
