"""Pure-logic unit tests for serum2.verify.bulk -- dedup, probe generation,
classification, evidence serialization. No Serum/DawDreamer required."""

import json
import tempfile
from pathlib import Path

from serum2.verify import bulk
from serum2.verify.classify import Classification, NEEDS_FOLLOWUP


def test_dedup_collapses_shared_binding():
    registry = {"semantic_resolutions": [
        {"semantic_id": "A.1", "technical_target_id": "T1", "capability_binding": {
            "capability_id": "X:1", "execution_family": "HOST_PARAMETER", "binding_status": "LIVE_VERIFIED",
            "authoritative_binding": {"parameter_name": "Foo"}}},
        {"semantic_id": "A.2", "technical_target_id": "T2", "capability_binding": {
            "capability_id": "X:1", "execution_family": "HOST_PARAMETER", "binding_status": "LIVE_VERIFIED",
            "authoritative_binding": {"parameter_name": "Foo"}}},
        {"semantic_id": "A.3", "technical_target_id": None, "capability_binding": None},
    ]}
    queue = bulk.build_queue(registry)
    assert len(queue) == 1
    assert set(queue["X:1"]["semantic_ids"]) == {"A.1", "A.2"}
    assert queue["X:1"]["target_ids"] == ["T1", "T2"]


def test_host_param_probes_boolean():
    meta = {"defaultValue": 0.0, "isBoolean": True, "numSteps": 2}
    a, b = bulk.host_param_probes(meta)
    assert {a, b} == {0.0, 1.0}
    assert a != b


def test_host_param_probes_discrete_avoids_default():
    meta = {"defaultValue": 0.8, "isDiscrete": True, "isBoolean": False, "numSteps": 16}
    a, b = bulk.host_param_probes(meta)
    assert a != b
    assert abs(a - meta["defaultValue"]) > 1e-6
    # both must be exact legal steps (i / 15)
    for v in (a, b):
        idx = v * 15
        assert abs(idx - round(idx)) < 1e-6


def test_host_param_probes_continuous():
    meta = {"defaultValue": 0.5, "isDiscrete": False, "isBoolean": False, "numSteps": 2147483647}
    a, b = bulk.host_param_probes(meta)
    assert a == 0.75 and b == 0.25


def test_snap_to_discrete():
    assert bulk._snap(0.75, 16) == 11 / 15
    assert bulk._snap(0.0, 5) == 0.0
    assert bulk._snap(1.0, 5) == 1.0


def test_evidence_serialization_and_forensic_queue(tmp_path=None):
    queue = {
        "A:1": {"execution_family": "HOST_PARAMETER", "authoritative_binding": {"parameter_name": "Foo"},
                "semantic_ids": ["S.1"], "target_ids": ["T.1"]},
        "A:2": {"execution_family": "HOST_PARAMETER", "authoritative_binding": {"parameter_name": "Bar"},
                "semantic_ids": ["S.2"], "target_ids": ["T.2"]},
    }
    results = {
        "A:1": {"classification": Classification.MACHINE_VERIFIED, "before": 0.5, "authority_after": 0.75},
        "A:2": {"classification": Classification.PERSISTENCE_MISMATCH, "detail": "did not persist"},
    }
    with tempfile.TemporaryDirectory() as d:
        run_dir = Path(d) / "run"
        summary = bulk.write_evidence(run_dir, queue, results)
        assert summary["unique_capability_count"] == 2
        assert summary["status_counts"]["MACHINE_VERIFIED"] == 1
        assert summary["status_counts"]["PERSISTENCE_MISMATCH"] == 1
        assert summary["failure_count"] == 1

        failures = json.load(open(run_dir / "failures.json"))
        assert len(failures) == 1
        assert failures[0]["capability_id"] == "A:2"

        forensic = json.load(open(run_dir / "forensic_queue.json"))
        assert len(forensic) == 1
        assert forensic[0]["capability_id"] == "A:2"

        lines = open(run_dir / "results.jsonl").read().strip().split("\n")
        assert len(lines) == 2
        recs = [json.loads(l) for l in lines]
        ids = {r["capability_id"] for r in recs}
        assert ids == {"A:1", "A:2"}


def test_needs_followup_excludes_not_executable():
    assert Classification.NOT_EXECUTABLE not in NEEDS_FOLLOWUP
    assert Classification.PERSISTENCE_MISMATCH in NEEDS_FOLLOWUP
    assert Classification.MACHINE_VERIFIED not in NEEDS_FOLLOWUP


if __name__ == "__main__":
    import sys
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"[PASS] {t.__name__}")
    print(f"\n{len(tests)} unit tests passed")
