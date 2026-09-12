"""4.Q.4 step 4: Fresh Attack qualification for 4.2 target-independence proof.

This is FRESH and INDEPENDENT, not a reuse of the archived _env_attack_record.pkl
(experiment_id ENV-ATTACK, condition_signature_hash 12dc2f522836863e). Uses the
same harness infrastructure that produced that record, with the same nominal
stimulus, but the causal outcome here is NOT assumed.

Attack has no baseline_overrides context (unlike Release), so this qualification
is simpler on the context side. The test remains target-independent: no code
path should know or care that this is Attack rather than any other capability.

EFFECT_OBSERVED     -> contract may become CAUSAL_VERIFIED, continue 4.2
NO_OBSERVED_EFFECT  -> contract becomes NEGATIVE_EVIDENCE, 4.2 STOPS
"""
import sys, pickle
sys.path.insert(0, r"D:\ableton claude")
from serum2.evidence import harness
from serum2.evidence.spec import (ExperimentSpec, Mutation, Stimulus,
                                  MeasurementPlan, TargetSpec, SINGLE_FIELD)

spec = ExperimentSpec(
    experiment_id="attack_qualified_complete_001",
    mutations=[Mutation("Env0.plainParams.kParamAttack", 0.8,
                        "4.Q.4 fresh qualification for 4.2 target-independence: "
                        "absolute parameter value")],
    prerequisites=[],
    baseline_overrides=[],  # Attack has no shared context (unlike Release/Decay)
    isolation_level=SINGLE_FIELD,
    claim_subject="Env1.Attack",
    claim_predicate="reduces",
    measurement_plans=[MeasurementPlan(
        metric="attack_onset_rms_db",
        target=TargetSpec("Env0.plainParams.kParamAttack", "Env", "kParamAttack"),
        expected_direction="decrease",  # shorter attack -> faster onset -> less pre-attack energy
        threshold=0.5,  # same threshold as archived evidence
        stimulus=Stimulus(note=60, velocity=110, note_len=0.4, render_seconds=2.0, tail_start=0.6),
        kernel_artifact="attack_onset_rms_db.py",
    )],
    notes="4.Q.4 FRESH qualification for 4.2 target-independence proof. Stimulus "
          "and mutation value chosen to match archived ENV-ATTACK "
          "(condition_signature_hash=12dc2f522836863e) for measurement comparability, "
          "but this is an independent experiment run: the causal outcome is not assumed.",
)

print("=" * 70)
print("4.Q.4 FRESH ATTACK QUALIFICATION -- experiment_id: %s" % spec.experiment_id)
print("=" * 70)

rec = harness.run(spec)

print("\ngate_completeness:", rec.gate_completeness())
m = rec.causal_measurements[0]
print("\nmeasurement_definition_id:", m.measurement_definition_id)
print("causal: baseline=%.4f treatment=%.4f delta=%+.4f threshold=%.2f" %
      (m.baseline, m.treatment, m.delta, m.threshold))
print("direction: expected=%s observed=%s" % (m.expected_direction, m.observed_direction))
print("STATUS:", m.status)
print("\npersistence:", rec.persistence_observation["status"],
      rec.persistence_observation.get("detail"))
print("\nexperiment_condition_signature:", rec.experiment["experiment_condition_signature"])

pickle.dump(rec, open(r"D:\ableton claude\experiments\_env_attack_qualified_complete_001.pkl", "wb"))
print("\nSaved: experiments/_env_attack_qualified_complete_001.pkl")

print("\n" + "=" * 70)
if m.status == "EFFECT_OBSERVED":
    print("OUTCOME: EFFECT_OBSERVED -- fresh qualification SUCCEEDS. Proceed to contract build.")
else:
    print("OUTCOME: %s -- fresh qualification FAILS. 4.2 STOPS HERE." % m.status)
    print("Do not build a CAUSAL_VERIFIED contract. Do not reuse the archived contract.")
print("=" * 70)
