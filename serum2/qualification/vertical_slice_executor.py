"""Vertical slice executor: capability admission → real Serum execution → measurement

Reuses existing semantic target resolver, admission layer, producer, and DawDreamer.
"""
import json
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import numpy as np

# Reuse existing imports
from serum2.compiler.targets import SEMANTIC_TARGETS
from serum2.evidence.measure import METRICS
from serum2.knowledge.intent_bridge import CandidateOperation


@dataclass
class ExecutionRecord:
    episode_id: str
    timestamp: str
    human_intent: str
    candidate_operation: Dict[str, Any]
    semantic_target: Optional[str]
    admission_status: str  # ADMITTED, UNKNOWN_TARGET, NOT_QUALIFIED
    admission_reason: str
    serum_readback_before: Optional[float]
    serum_mutation_value: Optional[float]
    serum_readback_after: Optional[float]
    audio_baseline: Optional[Dict[str, Any]]  # peak, nonzero_fraction, valid
    audio_treatment: Optional[Dict[str, Any]]
    measurement_metric: Optional[str]
    measurement_baseline: Optional[float]
    measurement_treatment: Optional[float]
    measurement_delta: Optional[float]
    restoration_value: Optional[float]
    restoration_readback: Optional[float]
    notes: str = ""
    learning_eligible: bool = True  # True if suitable for learning loop, False if observation-only
    observation_only: bool = False  # True if recorded but not for evidence derivation
    prerequisite_scope_violated: bool = False  # True if baseline outside contract scope

    def to_dict(self) -> dict:
        return asdict(self)


def check_admission(target_name: str, candidate_op: CandidateOperation) -> tuple:
    """
    Check if target is admissible using existing SEMANTIC_TARGETS.

    Returns: (status, reason)
    - ADMITTED if target exists in SEMANTIC_TARGETS
    - UNKNOWN_TARGET if not in vocabulary
    - NOT_QUALIFIED if target exists but has no CAUSAL_VERIFIED contract
    """
    if target_name not in SEMANTIC_TARGETS:
        return "UNKNOWN_TARGET", f"{target_name} not in SEMANTIC_TARGETS vocabulary"

    # Check if it has a capability contract (simplified; real path uses admission.py)
    # For this slice, we trust the 6 pre-qualified targets
    qualified_targets = {
        "OSC1.Level",
        "OSC1.Detune",
        "Env1.Attack",
        "Env1.Release",
        "Filter.Cutoff",
        "OSC1.Octave",
    }

    if target_name in qualified_targets:
        return "ADMITTED", f"{target_name} has CAUSAL_VERIFIED capability"
    else:
        return "NOT_QUALIFIED", f"{target_name} exists but not CAUSAL_VERIFIED"


def select_measurement_metric(target: str) -> Optional[str]:
    """Select measurement metric based on target type."""
    metric_map = {
        "OSC1.Level": "rms_db",
        "OSC1.Detune": "pitch_shift_semitones",
        "OSC1.Octave": "pitch_shift_semitones",
        "Env1.Attack": "rms_db",
        "Env1.Release": "tail_rms_db",
        "Filter.Cutoff": "spectral_centroid_hz",
    }
    return metric_map.get(target)


def create_execution_record(
    episode_id: str,
    human_intent: str,
    candidate_op: CandidateOperation,
    admission_status: str,
    admission_reason: str,
) -> ExecutionRecord:
    """Create execution record template (before actual execution)."""
    return ExecutionRecord(
        episode_id=episode_id,
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        human_intent=human_intent,
        candidate_operation=asdict(candidate_op),
        semantic_target=candidate_op.target,
        admission_status=admission_status,
        admission_reason=admission_reason,
        serum_readback_before=None,
        serum_mutation_value=None,
        serum_readback_after=None,
        audio_baseline=None,
        audio_treatment=None,
        measurement_metric=select_measurement_metric(candidate_op.target),
        measurement_baseline=None,
        measurement_treatment=None,
        measurement_delta=None,
        restoration_value=None,
        restoration_readback=None,
    )
