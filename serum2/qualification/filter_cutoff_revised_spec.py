"""Filter1.Cutoff BehaviorExperiment specification.

Refactored pilot: same parameters, new structured format.
"""

from serum2.qualification.behavior_experiment import (
    BehaviorExperiment,
    MeasurementPlan,
)

FILTER_CUTOFF_SPEC = BehaviorExperiment(
    experiment_id="filter_cutoff_revised_001",
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

    notes="Baseline: default Serum CBOR state with Filter1 On. "
          "Treatment: kParamFreq=0.9 (near-max, passes all frequencies). "
          "Expected: centroid increases due to more high-frequency content.",
)


if __name__ == "__main__":
    FILTER_CUTOFF_SPEC.validate()
    print("Spec validated OK")
    import json
    print(json.dumps(FILTER_CUTOFF_SPEC.to_dict(), indent=2, default=str))
