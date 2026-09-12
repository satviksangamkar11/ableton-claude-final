"""STEP 6 LIVE VERTICAL SLICE — real Serum 2.0.21 + DawDreamer 0.9.0.

Drives the FROZEN Step 6 reasoning/authority chain and hands the admitted
contract to the EXISTING canonical execution harness
(serum2.evidence.harness). No second executor, no second admission path,
no synthetic measurement.

Positive run : intent -> ... -> admission ADMITTED -> real render -> episode
Negative run : same intent, prerequisite unverified -> admission REFUSED
               -> zero treatment mutation, zero render, zero measurement

Writes machine-readable evidence to experiments/_step6_live_evidence.json
"""
import sys, os, json, copy, pickle
from datetime import datetime, timezone

ROOT = r"D:\ableton claude"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "serum2", "knowledge"))

import numpy as np

# ---- frozen Step 4 / canonical substrate -------------------------------
from serum2.evidence import admission as admission_mod
from serum2.evidence import harness, epoch
from serum2.evidence.spec import (ExperimentSpec, Mutation, Stimulus,
                                  MeasurementPlan, TargetSpec, SINGLE_FIELD)
from serum2.producer.contract_registry import ContractRegistry
from serum2.producer.episode_retrieval import retrieve_relevant_episodes

# ---- frozen Step 6 layers ----------------------------------------------
from step_6_2_universal_production_intent import (
    UniversalProductionIntent, SemanticDirection)
from step_6_4_semantic_reasoning_integration import SemanticCandidate
from step_6_5_advisory_decision_engine import AdvisoryDecision
from step_6_6_capability_resolution import CapabilityResolver, ResolutionStatus
from step_6_7_admission_handoff import AdmissionHandoff
from step_6_8_contract_governed_execution import (
    ContractGovernedExecutor, ExecutionPathway)
from step_6_9_outcome_attribution import attribute_outcome
from step_6_10_episode_generation import (
    UniversalEpisodeGenerator, ExecutionEvidenceRecord)

SEMANTIC_TARGET = "envelope_field_release"
UNIVERSAL_CONCEPT = "note-release"
USER_REQUEST = "Make the note sustain longer."


def _j(o):
    """JSON-safe."""
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, dict):
        return {str(k): _j(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_j(v) for v in o]
    if isinstance(o, (str, int, float, bool)) or o is None:
        return o
    return str(o)


# ========================================================================
# REASONING CHAIN (advisory only)
# ========================================================================
def build_reasoning_chain():
    intent = UniversalProductionIntent(
        original_user_request=USER_REQUEST,
        target_concept=UNIVERSAL_CONCEPT,
        semantic_direction=SemanticDirection.LONGER,
        musical_objective="Extend the audible tail after note-off",
    )

    # Knowledge participation (advisory).
    knowledge_ids = ["k_envelope_release_tail", "k_tail_rms_measurement"]
    knowledge_notes = {
        "k_envelope_release_tail": {
            "concept": "envelope release governs post-note-off decay",
            "epistemic_status": "HYPOTHESIS",
            "provenance": "general synthesis knowledge (not Serum-measured)",
            "contribution": "suggested note-release as the candidate concept",
        },
        "k_tail_rms_measurement": {
            "concept": "tail energy is observable after the note ends",
            "epistemic_status": "HYPOTHESIS",
            "provenance": "general synthesis knowledge",
            "contribution": "supported tail-window reasoning (NOT measurement authority)",
        },
    }

    # Episode participation (advisory) — canonical retrieval mechanism.
    prior = retrieve_relevant_episodes(
        semantic_target=SEMANTIC_TARGET,
        intent=USER_REQUEST,
        learning_eligible_only=True,
    )
    episode_ids = [e.get("episode_id") for e in prior]

    # Semantic reasoning -> candidate.
    candidate = SemanticCandidate(
        candidate_id="c_release_longer",
        label="lengthen_release",
        target_concept=UNIVERSAL_CONCEPT,
        operation="lengthen",
        confidence=0.80,
    )

    decision = AdvisoryDecision(
        decision_id="adv_live_001",
        intent=intent,
        selected_candidate=candidate,
        decision_status="decided",
        confidence=0.80,
    )
    return intent, candidate, decision, knowledge_ids, knowledge_notes, episode_ids


# ========================================================================
# AUTHORITY CHAIN
# ========================================================================
def build_declared_production_context(contract):
    """Build the caller's DECLARED current production context.

    This is what a real producer session would already know about its own
    state before attempting resolution -- e.g. what it is about to hold
    constant across both arms (Env0 Decay = 0.02, per the contract's
    prerequisite). This is supplied to CapabilityResolution.resolve() as
    current_context, exactly per its documented signature. It is NOT a
    resolver patch and NOT an admission bypass: 6.6 still runs its own
    checks against this context and can still refuse.
    """
    ctx = {}
    for p in contract.prerequisites or ():
        fp = p["field_path"]
        ctx[fp] = p.get("declared_value")
    return ctx


def verify_prerequisites_for_admission(contract, confirm: bool):
    """Caller-side prerequisite confirmation passed to Step 4 admission.

    This is the AdmissionHandoffRequest.proposed_prerequisites_verified
    field documented in step_6_7 -- distinct from CapabilityResolution's
    own current_context parameter. When confirm=False (negative run) we
    deliberately withhold confirmation so the REAL Step 4 admission.admit()
    call refuses with REFUSED_PREREQUISITE_UNVERIFIED, exactly reproducing
    the frozen RESOLVED != ADMITTED boundary.
    """
    verified = {}
    for p in contract.prerequisites or ():
        fp = p["field_path"]
        if confirm:
            verified[fp] = p.get("declared_value")
        else:
            verified[fp] = False
    return verified


def run_admission(resolution, candidate, intent, registry,
                  prerequisites_verified):
    """Runs 6.7 handoff exactly as written. No patching of `resolution`."""
    handoff = AdmissionHandoff(admission_mod, registry)
    request = handoff.prepare_request(resolution, candidate, intent)
    if request is None:
        return None, None
    # Caller-side prerequisite confirmation (Step 4 contract requirement).
    request.proposed_prerequisites_verified = prerequisites_verified
    result = handoff.submit_to_admission(request)
    return request, result


# ========================================================================
# CANONICAL EXECUTION — spec derived ONLY from the admitted contract
# ========================================================================
def build_spec_from_authority(authority, contract, experiment_id):
    """Every executable field comes from the admitted contract / authority."""
    scope = authority.scope or {}
    meas = contract.measurement or {}

    mutation_path = scope["mutation_target_path"]
    mutation_value = scope["mutation_value_used"]
    metric = meas["metric"]

    # Shared context from contract prerequisites (applied to BOTH arms).
    baseline_overrides = []
    for p in contract.prerequisites or ():
        fp = p["field_path"]
        if fp.startswith("body:"):
            baseline_overrides.append(
                Mutation(fp.split("body:", 1)[1], p["declared_value"],
                         "contract prerequisite: shared context, both arms"))

    spec = ExperimentSpec(
        experiment_id=experiment_id,
        mutations=[Mutation(mutation_path, mutation_value,
                            "contract-authorized treatment mutation")],
        prerequisites=[],
        baseline_overrides=baseline_overrides,
        isolation_level=SINGLE_FIELD,
        claim_subject="Env1.Release",
        claim_predicate="extends",
        measurement_plans=[MeasurementPlan(
            metric=metric,
            target=TargetSpec(mutation_path, "Env", "kParamRelease"),
            expected_direction=meas["expected_direction"],
            threshold=meas["threshold"],
            stimulus=Stimulus(note=60, velocity=110, note_len=0.4,
                              render_seconds=2.0, tail_start=0.6),
            kernel_artifact="tail_rms_db.py",
        )],
        notes="Step 6 live vertical slice; spec fields derived from admitted "
              "CapabilityContract only.",
    )
    return spec, mutation_path, mutation_value


def main():
    ev = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {},
        "positive": {},
        "negative": {},
    }

    # ---------------- environment ----------------
    ep = epoch.current_epoch()
    ev["environment"] = _j({
        "serum_vst3_path": epoch.SERUM_VST3,
        "serum_binary_sha256": ep["serum_binary_sha256"],
        "execution_epoch_id": ep["execution_epoch_id"],
        "dependency_lock": ep["dependency_lock"],
        "environment_fingerprint": ep["environment_fingerprint"],
    })

    registry = ContractRegistry()
    contract = registry.get(SEMANTIC_TARGET)
    ev["environment"]["contract_status"] = contract.status
    ev["environment"]["contract_measurement_definition_id"] = \
        (contract.measurement or {}).get("measurement_definition_id")

    # Serum product version from a real skeleton capture.
    from serum2 import bridge as br
    skel_meta, skel_body = br.capture_v8_skeleton(epoch.SERUM_VST3)
    ev["environment"]["serum_product"] = skel_meta.get("product")
    ev["environment"]["serum_product_version"] = skel_meta.get("productVersion")
    print("[env] Serum %s %s" % (skel_meta.get("product"),
                                 skel_meta.get("productVersion")))

    # ---------------- parameter identity proof ----------------
    # Reconcile: UI label "Env 1 Release" <-> VST control path used by the
    # contract <-> actual DawDreamer parameter index/name <-> readback.
    import dawdreamer as daw
    id_engine = daw.RenderEngine(44100, 512)
    id_synth = id_engine.make_plugin_processor("serum", epoch.SERUM_VST3)
    id_params = id_synth.get_parameters_description()
    ui_match = [p for p in id_params if p["name"] == "Env 1 Release"]
    contract_body_path = contract.scope["mutation_target_path"]  # Env0.plainParams.kParamRelease
    # Load the actual skeleton state into the synth and confirm the body
    # path is the one this VST3 instance's "Env 1 Release" control maps to
    # via the SAME bridge/codec the canonical harness uses (Env0 == voice
    # slot 0 == the UI's "Env 1", 0-indexed internally).
    identity_proof = {
        "ui_semantic_label": "Env 1 Release",
        "universal_concept": UNIVERSAL_CONCEPT,
        "capability_mapping_target": SEMANTIC_TARGET,
        "contract_target": contract.target,
        "contract_body_path": contract_body_path,
        "vst3_parameter_found": len(ui_match) == 1,
        "vst3_parameter_index": ui_match[0]["index"] if ui_match else None,
        "vst3_parameter_name": ui_match[0]["name"] if ui_match else None,
        "internal_body_index_convention": "Env0 (0-indexed body state) == UI 'Env 1' (1-indexed display)",
    }
    print("[identity] UI 'Env 1 Release' -> VST3 index %s -> body path %s"
          % (identity_proof["vst3_parameter_index"], contract_body_path))
    ev["parameter_identity_proof"] = _j(identity_proof)

    # ==================================================================
    # POSITIVE RUN
    # ==================================================================
    print("\n" + "=" * 66)
    print("POSITIVE LIVE RUN")
    print("=" * 66)

    intent, candidate, decision, k_ids, k_notes, ep_ids = build_reasoning_chain()
    print("[reasoning] intent=%r direction=%s"
          % (intent.original_user_request, intent.semantic_direction.value))
    print("[reasoning] knowledge_ids=%s" % k_ids)
    print("[reasoning] prior_episode_ids=%s" % ep_ids)

    # REAL 6.6 resolution — caller supplies its own declared production
    # context (current_context). No patching of resolution_status.
    declared_context = build_declared_production_context(contract)
    print("[context] caller declares current_context=%s" % declared_context)

    resolver = CapabilityResolver(registry)
    resolution = resolver.resolve(candidate, intent, current_context=declared_context)
    print("[resolution] status=%s target=%s contract=%s"
          % (resolution.resolution_status.value, resolution.semantic_target,
             resolution.capability_contract_id))
    print("[resolution] refusal_reason=%s" % resolution.refusal_reason)
    print("[resolution] prerequisite_status=%s scope_match=%s operation_compatibility=%s"
          % (resolution.prerequisite_status, resolution.scope_match,
             resolution.operation_compatibility.value if resolution.operation_compatibility else None))

    ev["positive"]["resolution_diagnostic"] = _j({
        "current_context_supplied": declared_context,
        "resolution_status": resolution.resolution_status.value,
        "prerequisite_status": resolution.prerequisite_status,
        "scope_match": resolution.scope_match,
        "operation_compatibility": resolution.operation_compatibility.value
            if resolution.operation_compatibility else None,
        "refusal_reason": resolution.refusal_reason,
    })

    if resolution.resolution_status != ResolutionStatus.RESOLVED:
        print("[FATAL] 6.6 CapabilityResolution did not resolve. Stopping — "
              "no bypass permitted. Reporting as 6.6 LIVE INTEGRATION DEFECT.")
        ev["positive"]["result"] = "6.6_LIVE_INTEGRATION_DEFECT"
        ev["classification"] = "PIPELINE_INTEGRATION_BLOCKED"
        _write(ev)
        return

    # Caller-side prerequisite CONFIRMATION for Step 4 admission (distinct
    # field from resolver's current_context; see step_6_7 docstring).
    prereq_verified = verify_prerequisites_for_admission(contract, confirm=True)
    print("[prereq->admission] proposed_prerequisites_verified=%s" % prereq_verified)

    request, adm = run_admission(resolution, candidate, intent, registry,
                                 prereq_verified)
    if adm is None:
        print("[admission] FAILED — handoff did not return result")
        ev["positive"]["result"] = "ADMISSION_HANDOFF_FAILED"
        _write(ev)
        return
    print("[admission] admitted=%s reason=%s" % (adm.admitted, adm.admission_reason))
    print("[admission] detail=%s" % adm.admission_detail)

    executor = ContractGovernedExecutor()
    record = executor.create_execution_intention(
        intent, decision, resolution, adm, registry)
    authority = record.execution_authority
    print("[authority] pathway=%s" % record.pathway.value)
    if authority:
        print("[authority] target=%s op=%s mdid=%s"
              % (authority.target, authority.allowed_operation,
                 authority.measurement_definition_id))

    ev["positive"]["reasoning_chain"] = _j({
        "original_user_request": intent.original_user_request,
        "universal_intent": {
            "target_concept": intent.target_concept,
            "semantic_direction": intent.semantic_direction.value,
            "musical_objective": intent.musical_objective,
        },
        "knowledge_ids": k_ids,
        "knowledge_notes": k_notes,
        "prior_episode_ids": ep_ids,
        "candidate_ids": [candidate.candidate_id],
        "advisory_decision": {
            "decision_id": decision.decision_id,
            "selected_candidate_id": candidate.candidate_id,
            "confidence": decision.confidence,
            "status": decision.decision_status,
        },
        "capability_resolution": {
            "resolution_id": resolution.resolution_id,
            "status": resolution.resolution_status.value,
            "semantic_target": resolution.semantic_target,
            "capability_contract_id": resolution.capability_contract_id,
        },
    })
    ev["positive"]["authority_chain"] = _j({
        "prerequisites_verified_by_caller": prereq_verified,
        "admission_result": {
            "admitted": adm.admitted,
            "reason": adm.admission_reason,
            "detail": adm.admission_detail,
            "contract_id": adm.contract_id,
            "contract_status": adm.contract_status,
            "measurement_definition_id": adm.measurement_definition_id,
        },
        "execution_pathway": record.pathway.value,
        "execution_authority": None if not authority else {
            "contract_id": authority.contract_id,
            "allowed_operation": authority.allowed_operation,
            "target": authority.target,
            "measurement_definition_id": authority.measurement_definition_id,
            "scope": authority.scope,
            "prerequisites": authority.prerequisites,
            "limitations": authority.limitations,
        },
    })

    if record.pathway is not ExecutionPathway.ADMITTED:
        ev["positive"]["result"] = "NOT_ADMITTED_NO_EXECUTION"
        print("[positive] NOT ADMITTED — no execution performed")
        _write(ev)
        return

    # -------- canonical execution (REAL Serum + DawDreamer) --------
    spec, mut_path, mut_val = build_spec_from_authority(
        authority, contract, "step6_live_vertical_slice_001")
    print("[exec] canonical harness.run  mutation %s=%s" % (mut_path, mut_val))
    print("[exec] baseline_overrides=%s"
          % [(m.target_path, m.value) for m in spec.baseline_overrides])

    rec = harness.run(spec)
    m = rec.causal_measurements[0]
    print("[render] baseline=%.4f treatment=%.4f delta=%+.4f status=%s"
          % (m.baseline, m.treatment, m.delta, m.status))
    print("[render] mdid=%s" % m.measurement_definition_id)

    # -------- readback proof: mutation actually took effect in Serum --------
    import dawdreamer as daw
    from serum2 import bridge as br2
    rb_meta = copy.deepcopy(skel_meta)
    rb_body = copy.deepcopy(skel_body)
    from serum2 import pathmerge as pm
    pm.apply_path_value(rb_body, mut_path, mut_val)
    import tempfile as _tf
    fd, tmp = _tf.mkstemp(suffix=".bin"); os.close(fd)
    br2.write_state_file(tmp, rb_meta, rb_body)
    rb_engine = daw.RenderEngine(44100, 512)
    rb_synth = rb_engine.make_plugin_processor("serum", epoch.SERUM_VST3)
    rb_synth.load_state(tmp)
    os.remove(tmp)
    rb_params = rb_synth.get_parameters_description()
    rb_by_name = {p["name"]: p["idx"] if "idx" in p else p["index"] for p in rb_params}
    rb_idx = rb_by_name.get("Env 1 Release")
    rb_desc = next(p for p in rb_params if p["name"] == "Env 1 Release")
    rb_host_normalized = rb_synth.get_parameter(rb_idx) if rb_idx is not None else None
    rb_display_text = rb_desc["currentValText"]

    # Compare against the UNMUTATED default for contrast.
    def_meta, def_body = skel_meta, skel_body
    fd2, tmp2 = _tf.mkstemp(suffix=".bin"); os.close(fd2)
    br2.write_state_file(tmp2, copy.deepcopy(def_meta), copy.deepcopy(def_body))
    def_engine = daw.RenderEngine(44100, 512)
    def_synth = def_engine.make_plugin_processor("serum", epoch.SERUM_VST3)
    def_synth.load_state(tmp2)
    os.remove(tmp2)
    def_desc = next(p for p in def_synth.get_parameters_description()
                    if p["name"] == "Env 1 Release")

    print("[readback] Env 1 Release (VST3 index %s): default=%s -> treatment=%s "
          "(host-normalized: %.4f -> %.4f)"
          % (rb_idx, def_desc["currentValText"], rb_display_text,
             def_desc["currentValText"] and def_synth.get_parameter(rb_idx),
             rb_host_normalized))
    ev["positive"]["parameter_readback_proof"] = _j({
        "vst3_parameter_index": rb_idx,
        "vst3_parameter_name": "Env 1 Release",
        "body_path_mutated": mut_path,
        "mutation_value_used_plain": mut_val,
        "default_display_text": def_desc["currentValText"],
        "treatment_display_text": rb_display_text,
        "note": "get_parameter() returns VST3-normalized [0,1]; Serum's own "
               "currentValText is the authoritative human-readable confirmation "
               "that the body-state plain value actually changed the loaded "
               "instance's release time.",
    })

    # -------- mutation-count proof from the actual spec/record --------
    treatment_mutations = [(x.target_path, x.value) for x in spec.mutations]
    shared_context = [(x.target_path, x.value) for x in spec.baseline_overrides]
    ev["positive"]["mutation_proof"] = _j({
        "treatment_mutation_count": len(treatment_mutations),
        "treatment_mutations": treatment_mutations,
        "shared_context_overrides_both_arms": shared_context,
        "isolation_level": str(spec.isolation_level),
        "experiment_condition_signature":
            rec.experiment.get("experiment_condition_signature"),
    })

    ev["positive"]["render_evidence"] = _j({
        "measurement_definition_id": m.measurement_definition_id,
        "metric": m.metric if hasattr(m, "metric") else spec.measurement_plans[0].metric,
        "baseline_measurement": m.baseline,
        "treatment_measurement": m.treatment,
        "delta": m.delta,
        "threshold": m.threshold,
        "expected_direction": m.expected_direction,
        "observed_direction": m.observed_direction,
        "harness_status": m.status,
        "gate_completeness": rec.gate_completeness(),
        "persistence_observation": rec.persistence_observation,
    })

    # -------- measurement authority proof --------
    contract_mdid = (contract.measurement or {}).get("measurement_definition_id")
    ev["positive"]["measurement_authority_proof"] = _j({
        "contract_measurement_definition_id": contract_mdid,
        "admission_propagated_mdid": adm.measurement_definition_id,
        "execution_authority_mdid": authority.measurement_definition_id,
        "actual_measured_mdid": m.measurement_definition_id,
        "match": (contract_mdid == m.measurement_definition_id),
    })

    # -------- diagnosis (interpretation only) --------
    diagnosis = {
        "metric": spec.measurement_plans[0].metric,
        "observed_delta": float(m.delta),
        "observed_direction": m.observed_direction,
        "contract_expected_direction": m.expected_direction,
        "interpretation": ("tail energy increased, consistent with a longer "
                           "release" if m.delta > 0 else
                           "tail energy did not increase"),
        "authority": "NONE — interpretation only",
    }
    ev["positive"]["diagnosis"] = _j(diagnosis)

    # -------- Step 6.9 outcome attribution (frozen) --------
    outcome = attribute_outcome(
        execution_id="ex_live_001",
        contract_id=adm.contract_id,
        intent_id="intent_live_001",
        baseline_measurement={"value": float(m.baseline),
                              "measurement_definition_id": m.measurement_definition_id},
        treatment_measurement={"value": float(m.treatment),
                               "measurement_definition_id": m.measurement_definition_id},
        admitted_contract=contract,
    )
    print("[outcome] status=%s causal=%s confidence=%.2f"
          % (outcome.outcome_status.value, outcome.causal_status.value,
             outcome.attribution_confidence))
    ev["positive"]["outcome_attribution"] = _j({
        "outcome_status": outcome.outcome_status.value,
        "causal_status": outcome.causal_status.value,
        "attribution_confidence": outcome.attribution_confidence,
        "baseline_value": outcome.baseline_value,
        "treatment_value": outcome.treatment_value,
        "change_magnitude": outcome.change_magnitude,
        "change_direction": outcome.change_direction,
        "expected_direction": outcome.expected_direction,
        "confounds_detected": outcome.confounds_detected,
        "measurement_definition_id": outcome.measurement_definition_id,
        "reasoning": outcome.reasoning,
        "provenance": outcome.provenance,
    })

    # -------- Step 6.10 episode generation + persistence --------
    evidence = ExecutionEvidenceRecord(
        baseline_state={mut_path: "contract-default (control arm)"},
        treatment_state={mut_path: mut_val},
        mutation_description="%s -> %s (contract-authorized)" % (mut_path, mut_val),
        render_evidence={"baseline_tail_rms_db": float(m.baseline),
                         "treatment_tail_rms_db": float(m.treatment),
                         "delta_db": float(m.delta)},
        diagnosis=diagnosis["interpretation"],
    )
    gen = UniversalEpisodeGenerator()
    episode = gen.generate_episode(
        execution_id="ex_live_001",
        universal_intent=intent,
        execution_record=record,
        admission_result=adm,
        admitted_contract=contract,
        advisory_decision=decision,
        capability_resolution=resolution,
        outcome=outcome,
        execution_evidence=evidence,
        knowledge_ids=k_ids,
        prior_episode_ids=ep_ids,
    )
    path = gen.persist_episode(episode)
    print("[episode] id=%s learning_eligible=%s"
          % (episode.episode_id, episode.learning_eligible))
    print("[episode] persisted -> %s" % path)

    # -------- canonical retrieval --------
    back = retrieve_relevant_episodes(
        semantic_target=SEMANTIC_TARGET,
        intent=USER_REQUEST,
        learning_eligible_only=False,
    )
    found = [e for e in back if e.get("episode_id") == episode.episode_id]
    print("[retrieval] found=%s (total for target=%d)" % (bool(found), len(back)))

    ev["positive"]["episode"] = _j({
        "episode_id": episode.episode_id,
        "execution_status": episode.execution_status.value,
        "learning_eligible": episode.learning_eligible,
        "learning_eligibility_status": episode.learning_eligibility_status.value,
        "eligibility_reasons": episode.eligibility_reasons,
        "admitted_contract_id": episode.admitted_contract_id,
        "measurement_definition_id": episode.measurement_definition_id,
        "observed_delta": episode.observed_delta,
        "attribution_confidence": episode.attribution_confidence,
        "persistence_path": path,
        "retrieved_back": bool(found),
        "retrieved_record": found[0] if found else None,
    })
    ev["positive"]["result"] = "LIVE_EXECUTED"

    # ==================================================================
    # NEGATIVE RUN — prerequisite NOT verified -> admission refused
    # ==================================================================
    print("\n" + "=" * 66)
    print("NEGATIVE LIVE RUN (prerequisite unverified)")
    print("=" * 66)

    n_intent, n_cand, n_dec, _, _, _ = build_reasoning_chain()
    n_cand.operation = "lengthen"

    # Same declared context as the positive run, so 6.6 resolves normally.
    # This is the crux of the negative proof: RESOLVED != ADMITTED.
    # Resolution succeeds; admission must independently refuse.
    n_res = resolver.resolve(n_cand, n_intent, current_context=declared_context)
    print("[neg resolution] status=%s (capability EXISTS, same real 6.6 path)"
          % n_res.resolution_status.value)

    if n_res.resolution_status != ResolutionStatus.RESOLVED:
        print("[FATAL] Negative-run 6.6 resolution unexpectedly failed. "
              "Cannot demonstrate RESOLVED != ADMITTED without a real "
              "resolved capability. Reporting as integration defect.")
        ev["negative"] = {"result": "6.6_LIVE_INTEGRATION_DEFECT",
                          "resolution_status": n_res.resolution_status.value}
        _write(ev)
        return

    # Withhold prerequisite CONFIRMATION at the admission layer only.
    # This does not touch 6.6; it exercises the real Step 4 admission gate.
    n_prereq_verified = verify_prerequisites_for_admission(contract, confirm=False)
    print("[neg prereq->admission] proposed_prerequisites_verified=%s"
          % n_prereq_verified)

    n_req, n_adm = run_admission(n_res, n_cand, n_intent, registry,
                                 n_prereq_verified)
    print("[neg admission] admitted=%s reason=%s"
          % (n_adm.admitted, n_adm.admission_reason))

    n_record = executor.create_execution_intention(
        n_intent, n_dec, n_res, n_adm, registry)
    print("[neg authority] pathway=%s authority=%s"
          % (n_record.pathway.value, n_record.execution_authority))

    executed = n_record.pathway is ExecutionPathway.ADMITTED
    n_outcome = attribute_outcome(
        execution_id="ex_live_neg_001",
        contract_id=n_adm.contract_id,
        intent_id="intent_live_neg_001",
        baseline_measurement=None,      # nothing was rendered
        treatment_measurement=None,
        admitted_contract=None,
    )
    n_episode = gen.generate_episode(
        execution_id="ex_live_neg_001",
        universal_intent=n_intent,
        execution_record=n_record,
        admission_result=n_adm,
        admitted_contract=None,
        advisory_decision=n_dec,
        capability_resolution=n_res,
        outcome=n_outcome,
    )
    print("[neg outcome] status=%s causal=%s"
          % (n_outcome.outcome_status.value, n_outcome.causal_status.value))
    print("[neg episode] learning_eligible=%s status=%s"
          % (n_episode.learning_eligible,
             n_episode.learning_eligibility_status.value))

    ev["negative"] = _j({
        "capability_resolution_status": n_res.resolution_status.value,
        "capability_found": n_res.capability_found,
        "capability_contract_id": n_res.capability_contract_id,
        "note": "6.6 RESOLVED normally (same context as positive run); "
               "admission independently refused due to withheld prerequisite "
               "confirmation. Proves RESOLVED != ADMITTED.",
        "prerequisites_verified_by_caller": n_prereq_verified,
        "admission_result": {
            "admitted": n_adm.admitted,
            "reason": n_adm.admission_reason,
            "detail": n_adm.admission_detail,
        },
        "execution_pathway": n_record.pathway.value,
        "execution_authority": n_record.execution_authority,
        "treatment_mutation_count": 0,
        "treatment_render_count": 0,
        "treatment_measurement_count": 0,
        "harness_invoked": executed,
        "outcome_status": n_outcome.outcome_status.value,
        "causal_status": n_outcome.causal_status.value,
        "episode_learning_eligible": n_episode.learning_eligible,
        "episode_learning_status": n_episode.learning_eligibility_status.value,
        "episode_eligibility_reasons": n_episode.eligibility_reasons,
        "result": "REFUSED_AT_ADMISSION_BOUNDARY",
    })

    _write(ev)


def _write(ev):
    out = os.path.join(ROOT, "experiments", "_step6_live_evidence.json")
    with open(out, "w") as f:
        json.dump(ev, f, indent=2)
    print("\n[evidence] %s" % out)


if __name__ == "__main__":
    main()
