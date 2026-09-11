"""12-control behavioral seed set for Serum 2.0.21 qualification.

Proof-of-concept expansion from Filter1.Cutoff pilot.
These are EXPERIMENT SPECIFICATIONS ONLY—no execution, no claims, no evidence.

Seed design:
- EXPECTED POSITIVE: controls that measurably affect audio (most controls)
- EXPECTED CONDITIONAL: controls whose effect depends on context (LFO rate, envelopes)
- EXPECTED NULL: controls expected to produce no effect in isolation (LFO with no destination)

Each experiment must be independent and self-contained.
Context, measurement plan, intervention, and expected outcome are explicit.
"""

from serum2.qualification.behavior_experiment import (
    BehaviorExperiment,
    MeasurementPlan,
)


# =============================================================================
# EXPECTED POSITIVE — Direct audio effect observable
# =============================================================================

FILTER1_CUTOFF = BehaviorExperiment(
    experiment_id="seed_filter1_cutoff_001",
    semantic_target="Filter1.Cutoff",
    operation="SET_PARAMETER",
    context={"Filter 1 On": 1.0},
    context_provenance="filter must be active to exercise cutoff parameter",
    treatment_cbor_path="VoiceFilter0.plainParams.kParamFreq",
    treatment_cbor_value=0.9,
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
    expected_direction="increase",
    notes="Baseline: default Serum state with Filter1 On. "
          "Treatment: kParamFreq=0.9 (high-pass tuning, more high-frequency content). "
          "Expect: centroid + RMS increase.",
)

FILTER1_RESONANCE = BehaviorExperiment(
    experiment_id="seed_filter1_resonance_001",
    semantic_target="Filter1.Resonance",
    operation="SET_PARAMETER",
    context={"Filter 1 On": 1.0},
    context_provenance="filter must be active; resonance affects tone only when filter is processing",
    treatment_cbor_path="VoiceFilter0.plainParams.kParamReso",
    treatment_cbor_value=0.9,
    measurement_plan=(
        MeasurementPlan(
            name="spectral_centroid_hz",
            kernel="spectral_centroid_hz",
            threshold=100.0,
        ),
        MeasurementPlan(
            name="overall_rms_db",
            kernel="rms_db",
            threshold=1.0,
        ),
    ),
    expected_outcome="EFFECT_OBSERVED",
    expected_direction="increase",
    notes="Resonance (Q) emphasis at cutoff frequency. "
          "Treatment: kParamReso=0.9 (high resonance peak). "
          "Expect: RMS increase from resonance peak, centroid may shift slightly.",
)

FILTER2_CUTOFF = BehaviorExperiment(
    experiment_id="seed_filter2_cutoff_001",
    semantic_target="Filter2.Cutoff",
    operation="SET_PARAMETER",
    context={"Filter 2 On": 1.0},
    context_provenance="filter must be active to exercise cutoff parameter",
    treatment_cbor_path="VoiceFilter1.plainParams.kParamFreq",
    treatment_cbor_value=0.9,
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
    expected_direction="increase",
    notes="Filter2 operates independently. Same high-pass effect as Filter1. "
          "Treatment: kParamFreq=0.9.",
)

OSC1_LEVEL = BehaviorExperiment(
    experiment_id="seed_osc1_level_001",
    semantic_target="OSC1.Level",
    operation="SET_PARAMETER",
    context={},
    context_provenance="level is independent (no prerequisites)",
    treatment_cbor_path="VoiceOsc0.plainParams.kParamLevel",
    treatment_cbor_value=1.0,  # max level
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
    expected_direction="increase",
    notes="OSC1 amplitude control. Baseline: default level. "
          "Treatment: kParamLevel=1.0 (maximum). "
          "Expect: RMS increase from higher amplitude.",
)

OSC1_DETUNE = BehaviorExperiment(
    experiment_id="seed_osc1_detune_001",
    semantic_target="OSC1.Detune",
    operation="SET_PARAMETER",
    context={},
    context_provenance="detune works independently",
    treatment_cbor_path="VoiceOsc0.plainParams.kParamDetune",
    treatment_cbor_value=0.5,  # medium detune
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
    notes="Detune creates spectral width. Baseline: zero detune. "
          "Treatment: kParamDetune=0.5 (medium spread). "
          "Expect: spectral centroid shift from wider spectrum.",
)

OSC2_DETUNE = BehaviorExperiment(
    experiment_id="seed_osc2_detune_001",
    semantic_target="OSC2.Detune",
    operation="SET_PARAMETER",
    context={},
    context_provenance="detune works independently",
    treatment_cbor_path="VoiceOsc1.plainParams.kParamDetune",
    treatment_cbor_value=0.5,
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
    notes="OSC2 detune independent of OSC1. Detune creates spectral width.",
)

FILTER1_DRIVE = BehaviorExperiment(
    experiment_id="seed_filter1_drive_001",
    semantic_target="Filter1.Drive",
    operation="SET_PARAMETER",
    context={"Filter 1 On": 1.0},
    context_provenance="filter must be active to apply drive",
    treatment_cbor_path="VoiceFilter0.plainParams.kParamDrive",
    treatment_cbor_value=1.0,  # max drive
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
    expected_direction="increase",
    notes="Drive adds harmonic content and compression. Baseline: zero drive. "
          "Treatment: kParamDrive=1.0 (maximum). "
          "Expect: RMS increase and spectral centroid shift from harmonics.",
)

FXEQ_FREQ1 = BehaviorExperiment(
    experiment_id="seed_fxeq_freq1_001",
    semantic_target="FXEQ.Freq1",
    operation="SET_PARAMETER",
    context={"FX EQ On": 1.0},
    context_provenance="EQ must be active to affect audio",
    treatment_cbor_path="FXRack0.FX.0.EQParameters.kParamEQ1Frequency",
    treatment_cbor_value=0.8,  # boosted high-mid
    measurement_plan=(
        MeasurementPlan(
            name="spectral_centroid_hz",
            kernel="spectral_centroid_hz",
            threshold=200.0,
        ),
        MeasurementPlan(
            name="overall_rms_db",
            kernel="rms_db",
            threshold=1.0,
        ),
    ),
    expected_outcome="EFFECT_OBSERVED",
    expected_direction="increase",
    notes="EQ band 1 frequency shift. Baseline: default EQ frequency. "
          "Treatment: kParamEQ1Frequency=0.8. "
          "Expect: centroid shift depending on gain (may be neutral if only frequency changes).",
)


# =============================================================================
# EXPECTED CONDITIONAL — Effect depends on runtime context
# =============================================================================

ENV1_ATTACK = BehaviorExperiment(
    experiment_id="seed_env1_attack_001",
    semantic_target="Env1.Attack",
    operation="SET_PARAMETER",
    context={},
    context_provenance="envelope attack is independent; onset affects rendered audio only if note duration covers attack phase",
    treatment_cbor_path="VoiceEnv0.plainParams.kParamAttackTime",
    treatment_cbor_value=0.1,  # faster attack
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
    notes="Attack time affects envelope onset. Baseline: default attack. "
          "Treatment: kParamAttackTime=0.1 (fast). "
          "Conditional: effect depends on note duration and envelope routing. "
          "Expect: possible RMS/centroid shift if envelope routes to filter or level.",
)

ENV1_RELEASE = BehaviorExperiment(
    experiment_id="seed_env1_release_001",
    semantic_target="Env1.Release",
    operation="SET_PARAMETER",
    context={},
    context_provenance="envelope release is independent; tail occurs after note ends, may not affect the rendered window",
    treatment_cbor_path="VoiceEnv0.plainParams.kParamReleaseTime",
    treatment_cbor_value=0.1,  # fast release
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
    notes="Release time affects envelope tail. Rendered window: 2.0s from note start (1.5s sustain + tail). "
          "Baseline: default release. Treatment: kParamReleaseTime=0.1 (fast). "
          "Conditional: effect visible only if rendered window captures release phase.",
)


# =============================================================================
# EXPECTED NULL — No effect in isolation (important negative evidence)
# =============================================================================

LFO1_RATE_NO_DESTINATION = BehaviorExperiment(
    experiment_id="seed_lfo1_rate_no_destination_001",
    semantic_target="LFO1.Rate",
    operation="SET_PARAMETER",
    context={},  # empty: LFO running but not modulating anything
    context_provenance="LFO1 with no modulation destination produces no audible effect; confirms control isolation",
    treatment_cbor_path="VoiceModulation0.plainParams.kParamRate",
    treatment_cbor_value=0.5,  # medium LFO rate
    measurement_plan=(
        MeasurementPlan(
            name="overall_rms_db",
            kernel="rms_db",
            threshold=0.5,
        ),
        MeasurementPlan(
            name="spectral_centroid_hz",
            kernel="spectral_centroid_hz",
            threshold=50.0,
        ),
    ),
    expected_outcome="NO_OBSERVED_EFFECT",
    expected_direction="change",
    notes="LFO rate without modulation target. Baseline: default LFO rate. "
          "Treatment: kParamRate=0.5 (different rate). "
          "Expect: NO_OBSERVED_EFFECT. LFO oscillates internally but has no audio output. "
          "This is important: proves rate changes alone produce no evidence.",
)


# =============================================================================
# EXPECTED POSITIVE (CONDITIONAL) — Effect only with modulation destination
# =============================================================================

LFO1_RATE_WITH_FILTER_MODULATION = BehaviorExperiment(
    experiment_id="seed_lfo1_rate_filter_modulation_001",
    semantic_target="LFO1.Rate",
    operation="SET_PARAMETER",
    context={"LFO1 Mod Dest": "Filter1.Cutoff", "Filter 1 On": 1.0},
    context_provenance="LFO1 modulating Filter1.Cutoff; rate change affects how fast cutoff is swept",
    treatment_cbor_path="VoiceModulation0.plainParams.kParamRate",
    treatment_cbor_value=0.5,  # medium LFO rate
    measurement_plan=(
        MeasurementPlan(
            name="spectral_centroid_hz",
            kernel="spectral_centroid_hz",
            threshold=200.0,
        ),
        MeasurementPlan(
            name="overall_rms_db",
            kernel="rms_db",
            threshold=1.0,
        ),
    ),
    expected_outcome="EFFECT_OBSERVED",
    expected_direction="change",
    notes="LFO1 rate with modulation destination set to Filter1.Cutoff. "
          "Baseline: default LFO rate (slow). Treatment: kParamRate=0.5 (medium speed). "
          "With modulation active, faster LFO sweeps cutoff more frequently. "
          "Expect: spectral changes from rapid filter sweeping.",
)


# =============================================================================
# Seed collection for validation
# =============================================================================

SEED_12_EXPERIMENTS = (
    FILTER1_CUTOFF,
    FILTER1_RESONANCE,
    FILTER2_CUTOFF,
    OSC1_LEVEL,
    OSC1_DETUNE,
    OSC2_DETUNE,
    ENV1_ATTACK,
    ENV1_RELEASE,
    LFO1_RATE_NO_DESTINATION,
    LFO1_RATE_WITH_FILTER_MODULATION,
    FILTER1_DRIVE,
    FXEQ_FREQ1,
)


def validate_seed():
    """Validate all 12 experiments structurally."""
    print("=" * 70)
    print("VALIDATING SEED SET")
    print("=" * 70)
    print()

    for i, exp in enumerate(SEED_12_EXPERIMENTS, 1):
        try:
            exp.validate()
            print(f"[{i:2d}] {exp.experiment_id:40s} [OK]")
        except Exception as e:
            print(f"[{i:2d}] {exp.experiment_id:40s} [FAIL]")
            print(f"     Error: {e}")

    print()
    print("=" * 70)
    print(f"RESULT: Validated {len(SEED_12_EXPERIMENTS)} experiments")
    print("=" * 70)


if __name__ == "__main__":
    validate_seed()

    # Print one example
    import json
    print()
    print("Example: Filter1.Cutoff spec")
    print("-" * 70)
    print(json.dumps(FILTER1_CUTOFF.to_dict(), indent=2, default=str))
