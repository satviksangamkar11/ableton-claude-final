"""Integration adapter: Producer requests → Existing Serum/DawDreamer harness.

This adapter translates producer-level execution requests into the existing
proven ExperimentSpec/harness.run() infrastructure.

Does NOT reimplement the harness.
Does NOT create new capability contracts.
Does NOT modify authority logic.

Bridges: Producer intent → harness invocation → EvidenceRecord → Episode.
"""
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

# Add serum2 to path (main project contains proven harness + dependencies)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from serum2.evidence.harness import run as harness_run
from serum2.evidence.spec import ExperimentSpec, Mutation, Prerequisite, MeasurementPlan, TargetSpec, Stimulus, CONTROLLED_MULTI_FIELD
from serum2.evidence.record import EvidenceRecord


@dataclass
class SerumExecutionRequest:
    """Producer-level Serum execution request."""
    experiment_id: str
    semantic_operation: str  # e.g., "lengthen_release", "boost_filter_cutoff"
    mutation: Dict[str, Any]  # {path: value} from resolved capability
    prerequisites: Optional[List[Dict]] = None
    midi_stimulus: Optional[Dict] = None  # {note, velocity, note_len, render_seconds}
    measurement_metric: str = "overall_rms_db"
    baseline_overrides: Optional[List] = None
    reference_context: Optional[Dict] = None  # source/knowledge info
    skeleton: Optional[tuple] = None  # [meta, body] if pre-captured


@dataclass
class SerumExecutionResult:
    """Result of harness execution."""
    success: bool
    evidence_record: Optional[EvidenceRecord]
    baseline: Optional[float]
    treatment: Optional[float]
    delta: Optional[float]
    measurement_id: Optional[str]
    error: Optional[str]
    unsupported_operations: List[str]


def execute_serum_request(request: SerumExecutionRequest) -> SerumExecutionResult:
    """Execute a producer-level Serum operation through the proven harness.

    Args:
        request: SerumExecutionRequest with mutation and stimulus

    Returns:
        SerumExecutionResult with measurement data and evidence record
    """
    unsupported = []

    try:
        # Build mutations from the request
        mutations = []
        for path, value in (request.mutation or {}).items():
            mutations.append(Mutation(
                path,
                value,
                f"producer: {request.semantic_operation}"
            ))

        # Build prerequisites
        prerequisites = []
        if request.prerequisites:
            for p in request.prerequisites:
                prerequisites.append(Prerequisite(
                    p.get("field_path", ""),
                    p.get("declared_value"),
                    p.get("must_hold_identical", False)
                ))

        # Build MIDI stimulus (default: C4, vel 110, 1.8 sec)
        stim = request.midi_stimulus or {}
        stimulus = Stimulus(
            note=stim.get("note", 48),
            velocity=stim.get("velocity", 110),
            note_len=stim.get("note_len", 1.8),
            render_seconds=stim.get("render_seconds", 2.0),
        )

        # Build measurement plan
        measurement_plans = [MeasurementPlan(
            metric=request.measurement_metric,
            target=TargetSpec("producer_patch", None, None),
            expected_direction="none",  # No direction expected for reference recreation
            threshold=0.5,
            stimulus=stimulus,
            kernel_artifact=f"{request.measurement_metric}.py"
        )]

        # Build ExperimentSpec
        spec = ExperimentSpec(
            experiment_id=request.experiment_id,
            mutations=mutations,
            prerequisites=prerequisites,
            isolation_level=CONTROLLED_MULTI_FIELD,
            claim_subject=f"producer_patch:{request.experiment_id}",
            claim_predicate="recreatable",
            baseline_overrides=list(request.baseline_overrides or []),
            measurement_plans=measurement_plans,
            notes=f"Recreation: {request.semantic_operation}, context: {request.reference_context}",
        )

        # Call the existing proven harness
        evidence_record = harness_run(spec, skeleton=request.skeleton)

        # Extract measurements
        baseline = None
        treatment = None
        delta = None
        measurement_id = None

        if evidence_record and evidence_record.causal_measurements:
            m = evidence_record.causal_measurements[0]
            baseline = m.baseline
            treatment = m.treatment
            delta = m.delta
            measurement_id = m.measurement_definition_id

        # Check if execution succeeded
        load_ok = evidence_record.load_observation.get("ok", False) if evidence_record else False

        return SerumExecutionResult(
            success=load_ok,
            evidence_record=evidence_record,
            baseline=baseline,
            treatment=treatment,
            delta=delta,
            measurement_id=measurement_id,
            error=None,
            unsupported_operations=unsupported,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return SerumExecutionResult(
            success=False,
            evidence_record=None,
            baseline=None,
            treatment=None,
            delta=None,
            measurement_id=None,
            error=f"{type(e).__name__}: {str(e)[:200]}",
            unsupported_operations=unsupported,
        )
