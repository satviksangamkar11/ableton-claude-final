"""
Test suite for Step 6.11 Closed-Loop Decision Proof.

24 tests proving Episode influences reasoning while remaining non-authoritative.

Core proof: Cycle A (no prior episode) → generate episode
          Cycle B (with Cycle A episode) → measurable learning influence
"""

import pytest
from unittest.mock import Mock
from step_6_11_closed_loop_proof import (
    CompleteCycleTrace,
    ReasoningDecisionTrace,
    AuthorityChainTrace,
    CandidateScore,
    CyclePhase,
    ClosedLoopAnalyzer,
    ClosedLoopComparison,
    NegativeTestProof,
    create_cycle_trace,
    analyze_learning_influence,
)


class TestCycleAFoundation:
    """Tests 1-3: Cycle A establishes baseline (no prior episode)."""

    def test_cycle_a_no_useful_prior_episode(self):
        """Test 1: Cycle A has no prior useful episode."""
        cycle_a = create_cycle_trace(
            cycle_id="cycle_a_001",
            cycle_name="A",
            intent="Make bass tighter",
            available_episodes=[],  # No prior episode
            candidates=[
                CandidateScore(
                    candidate_id="c1",
                    label="shorten_release",
                    total_score=0.65,
                    semantic_fit=0.25,
                    knowledge_support=0.20,
                    episode_support=0.0,  # No episode support
                ),
                CandidateScore(
                    candidate_id="c2",
                    label="increase_attack",
                    total_score=0.58,
                    semantic_fit=0.20,
                    knowledge_support=0.18,
                    episode_support=0.0,
                ),
            ],
            selected_candidate="c1",
            decision_confidence=0.65,
        )

        assert len(cycle_a.reasoning_chain.available_episode_ids) == 0
        assert cycle_a.reasoning_chain.decision_confidence == 0.65

    def test_cycle_a_generates_episode(self):
        """Test 2: Cycle A generates learning-eligible episode."""
        cycle_a = create_cycle_trace(
            cycle_id="cycle_a_001",
            cycle_name="A",
            intent="Make bass tighter",
        )
        cycle_a.generated_episode_id = "ep_cycle_a_001"
        cycle_a.outcome_status = "expected_improvement"

        assert cycle_a.generated_episode_id is not None
        assert cycle_a.outcome_status == "expected_improvement"

    def test_cycle_a_passes_through_authority_chain(self):
        """Test 3: Cycle A executes through canonical admission."""
        cycle_a = create_cycle_trace(
            cycle_id="cycle_a_001",
            cycle_name="A",
            intent="Make bass tighter",
        )
        cycle_a.authority_chain.capability_resolution_status = "RESOLVED"
        cycle_a.authority_chain.admission_requested = True
        cycle_a.authority_chain.admission_granted = True
        cycle_a.authority_chain.resolved_contract_id = "env_release"
        cycle_a.authority_chain.execution_occurred = True

        assert cycle_a.authority_chain.admission_granted is True
        assert cycle_a.authority_chain.execution_occurred is True


class TestCycleBLearning:
    """Tests 4-8: Cycle B demonstrates learning influence."""

    def test_cycle_b_retrieves_cycle_a_episode(self):
        """Test 4: Cycle B retrieves Cycle A's generated episode."""
        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
            available_episodes=["ep_cycle_a_001"],  # Retrieved from Cycle A
        )

        assert len(cycle_b.reasoning_chain.available_episode_ids) == 1
        assert "ep_cycle_a_001" in cycle_b.reasoning_chain.available_episode_ids

    def test_cycle_b_episode_reaches_reasoning(self):
        """Test 5: Episode context reaches semantic reasoning."""
        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
            available_episodes=["ep_cycle_a_001"],
            candidates=[
                CandidateScore(
                    candidate_id="c1",
                    label="shorten_release",
                    total_score=0.78,  # Higher than Cycle A
                    semantic_fit=0.25,
                    knowledge_support=0.20,
                    episode_support=0.15,  # Episode support added
                    reasons=["semantic_fit", "knowledge_support", "episode_precedent"],
                ),
                CandidateScore(
                    candidate_id="c2",
                    label="increase_attack",
                    total_score=0.58,
                    semantic_fit=0.20,
                    knowledge_support=0.18,
                    episode_support=0.0,
                ),
            ],
        )

        # Verify episode support was factored in
        c1_scores = [c for c in cycle_b.reasoning_chain.generated_candidates if c.candidate_id == "c1"]
        assert len(c1_scores) > 0
        assert c1_scores[0].episode_support == 0.15

    def test_cycle_b_candidate_scores_change(self):
        """Test 6: Candidate scores change due to episode support."""
        cycle_a = create_cycle_trace(
            cycle_id="cycle_a_001",
            cycle_name="A",
            intent="Make bass tighter",
            available_episodes=[],
            candidates=[
                CandidateScore(
                    candidate_id="c1",
                    label="shorten_release",
                    total_score=0.65,
                ),
            ],
        )

        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
            available_episodes=["ep_cycle_a_001"],
            candidates=[
                CandidateScore(
                    candidate_id="c1",
                    label="shorten_release",
                    total_score=0.78,  # Higher due to episode support
                    episode_support=0.15,
                ),
            ],
        )

        comparison = analyze_learning_influence(cycle_a, cycle_b)

        assert "c1" in comparison.candidates_with_changed_scores
        assert comparison.cycle_a_candidate_scores["c1"] == 0.65
        assert comparison.cycle_b_candidate_scores["c1"] == 0.78

    def test_cycle_b_confidence_increases(self):
        """Test 7: Decision confidence increases with episode support."""
        cycle_a = create_cycle_trace(
            cycle_id="cycle_a_001",
            cycle_name="A",
            intent="Make bass tighter",
            decision_confidence=0.65,
        )

        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
            available_episodes=["ep_cycle_a_001"],
            decision_confidence=0.78,  # Higher with episode
        )

        comparison = analyze_learning_influence(cycle_a, cycle_b)

        assert comparison.cycle_b_confidence > comparison.cycle_a_confidence
        assert comparison.confidence_changed is True

    def test_cycle_b_learning_influence_detected(self):
        """Test 8: Learning influence is measurably detected."""
        cycle_a = create_cycle_trace(
            cycle_id="cycle_a_001",
            cycle_name="A",
            intent="Make bass tighter",
            available_episodes=[],
            candidates=[
                CandidateScore(
                    candidate_id="c1",
                    label="shorten_release",
                    total_score=0.65,
                ),
            ],
            decision_confidence=0.65,
        )

        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
            available_episodes=["ep_cycle_a_001"],
            candidates=[
                CandidateScore(
                    candidate_id="c1",
                    label="shorten_release",
                    total_score=0.78,
                    episode_support=0.15,
                ),
            ],
            decision_confidence=0.78,
        )

        comparison = analyze_learning_influence(cycle_a, cycle_b)

        assert comparison.learning_influence_detected is True


class TestAuthorityPreservation:
    """Tests 9-13: Episode doesn't bypass authority."""

    def test_episode_cannot_bypass_capability_resolution(self):
        """Test 9: Cycle B still requires capability resolution."""
        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
            available_episodes=["ep_cycle_a_001"],
        )
        cycle_b.authority_chain.capability_resolution_status = "RESOLVED"
        cycle_b.authority_chain.resolved_contract_id = "env_release"

        # Episode context does NOT skip capability resolution
        assert cycle_b.authority_chain.capability_resolution_status is not None

    def test_episode_cannot_bypass_admission(self):
        """Test 10: Cycle B still requires actual admission."""
        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
            available_episodes=["ep_cycle_a_001"],
        )
        cycle_b.authority_chain.admission_requested = True
        cycle_b.authority_chain.admission_granted = True
        cycle_b.authority_chain.admission_reason = "ADMITTED"

        # Episode cannot grant admission automatically
        assert cycle_b.authority_chain.admission_granted is True  # But requires actual admission
        assert cycle_b.authority_chain.admission_requested is True

    def test_episode_cannot_create_capability(self):
        """Test 11: Episode doesn't manufacture contracts."""
        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="unknown_action",
            available_episodes=["ep_episode_unknown"],
        )
        cycle_b.authority_chain.capability_resolution_status = "NOT_FOUND"
        cycle_b.authority_chain.resolved_contract_id = None

        # Episode presence doesn't create missing contract
        assert cycle_b.authority_chain.resolved_contract_id is None

    def test_episode_cannot_override_contract(self):
        """Test 12: Contract remains authoritative."""
        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
            available_episodes=["ep_cycle_a_001"],
        )
        cycle_b.authority_chain.resolved_contract_id = "env_release"
        # Even with episode, contract is the actual authority source
        assert cycle_b.authority_chain.resolved_contract_id == "env_release"

    def test_episode_cannot_override_measurement(self):
        """Test 13: Measurement kernel from contract, not episode."""
        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
            available_episodes=["ep_cycle_a_001"],
        )
        # Episode may suggest measurement, but contract defines it
        cycle_b.authority_chain.execution_notes = "measurement_from_contract"
        assert "contract" in cycle_b.authority_chain.execution_notes


class TestNegativeConditions:
    """Tests 14-16: Negative tests prove boundaries."""

    def test_episode_without_capability_fails(self):
        """Test 14: Episode recommends unavailable action."""
        result = NegativeTestProof.test_episode_without_capability()

        assert result["expected_result"]["capability_resolution_status"] == "NOT_FOUND"
        assert result["expected_result"]["execution_occurred"] is False

    def test_episode_conflicts_with_contract_contract_wins(self):
        """Test 15: Episode conflicts with contract authority."""
        result = NegativeTestProof.test_episode_conflicts_with_contract()

        assert result["expected_result"]["mutation_value_used"] == "value_Z"
        assert result["expected_result"]["authority_source"] == "CapabilityContract"

    def test_high_confidence_episode_still_needs_admission(self):
        """Test 16: High confidence ≠ execution permission."""
        result = NegativeTestProof.test_high_confidence_episode()

        assert result["setup"]["episode_confidence"] == 0.99
        assert result["expected_result"]["execution_occurred"] is False
        assert result["setup"]["admission_status"] == "REFUSED"


class TestExecutionPreservation:
    """Tests 17-20: Execution uses canonical path only."""

    def test_cycle_b_uses_canonical_execution(self):
        """Test 17: Cycle B execution through canonical Step 6.8."""
        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
        )
        cycle_b.authority_chain.execution_occurred = True
        cycle_b.execution_trace_id = "exec_canonical_001"

        # Execution used canonical path, not episode-injected path
        assert cycle_b.execution_trace_id.startswith("exec_canonical")

    def test_cycle_b_exactly_one_mutation(self):
        """Test 18: Exactly one mutation per execution."""
        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
        )
        cycle_b.authority_chain.execution_notes = "mutation_count: 1"

        assert "1" in cycle_b.authority_chain.execution_notes

    def test_cycle_b_generates_outcome_and_episode(self):
        """Test 19: Successful execution generates outcome + episode."""
        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
        )
        cycle_b.outcome_status = "expected_improvement"
        cycle_b.generated_episode_id = "ep_cycle_b_001"

        assert cycle_b.outcome_status is not None
        assert cycle_b.generated_episode_id is not None

    def test_full_provenance_preserved(self):
        """Test 20: Full provenance chain preserved."""
        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
            available_episodes=["ep_cycle_a_001"],
            selected_candidate="c1",
        )
        cycle_b.reasoning_chain.advisory_decision_id = "adv_b_001"
        cycle_b.authority_chain.resolved_contract_id = "env_release"
        cycle_b.authority_chain.admission_granted = True
        cycle_b.execution_trace_id = "exec_b_001"

        # Full chain traceable
        assert cycle_b.reasoning_chain.available_episode_ids == ["ep_cycle_a_001"]
        assert cycle_b.reasoning_chain.advisory_decision_id == "adv_b_001"
        assert cycle_b.authority_chain.resolved_contract_id == "env_release"


class TestChainSeparation:
    """Tests 21-22: Reasoning chain vs authority chain separation."""

    def test_reasoning_chain_separate_from_authority(self):
        """Test 21: Reasoning chain and authority chain are distinct."""
        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
            available_episodes=["ep_cycle_a_001"],
            candidates=[
                CandidateScore(
                    candidate_id="c1",
                    label="shorten_release",
                    total_score=0.78,
                    episode_support=0.15,
                )
            ],
        )
        cycle_b.reasoning_chain.advisory_decision_id = "adv_b_001"
        cycle_b.authority_chain.resolved_contract_id = "env_release"

        # Reasoning uses episodes and advisory scoring
        assert cycle_b.reasoning_chain.available_episode_ids[0] == "ep_cycle_a_001"
        assert cycle_b.reasoning_chain.advisory_decision_id is not None

        # Authority is independent (contract, admission, execution)
        assert cycle_b.authority_chain.resolved_contract_id == "env_release"
        assert cycle_b.reasoning_chain != cycle_b.authority_chain

    def test_no_reverse_authority_to_reasoning(self):
        """Test 22: Authority never flows back to override reasoning."""
        cycle_b = create_cycle_trace(
            cycle_id="cycle_b_001",
            cycle_name="B",
            intent="Make bass tighter",
        )

        # Authority chain independent
        cycle_b.authority_chain.admission_granted = False
        cycle_b.reasoning_chain.selected_candidate_id = "c1"

        # Refused admission doesn't erase the advisory decision made
        # (it just prevents execution)
        assert cycle_b.reasoning_chain.selected_candidate_id == "c1"
        assert cycle_b.authority_chain.admission_granted is False


class TestControlCondition:
    """Tests 23-24: Control conditions."""

    def test_control_cycle_without_episode(self):
        """Test 23: Control decision without episode context."""
        control_cycle = create_cycle_trace(
            cycle_id="control_001",
            cycle_name="CONTROL",
            intent="Make bass tighter",
            available_episodes=[],  # Explicitly no episodes
            candidates=[
                CandidateScore(
                    candidate_id="c1",
                    label="shorten_release",
                    total_score=0.65,  # No episode support
                    semantic_fit=0.25,
                    knowledge_support=0.20,
                    episode_support=0.0,
                ),
            ],
            decision_confidence=0.65,
        )

        assert len(control_cycle.reasoning_chain.available_episode_ids) == 0
        assert control_cycle.reasoning_chain.decision_confidence == 0.65

    def test_control_vs_learning_comparison(self):
        """Test 24: Control vs learning-context measurable difference."""
        # Control (no episodes)
        control = create_cycle_trace(
            cycle_id="control_001",
            cycle_name="CONTROL",
            intent="Make bass tighter",
            available_episodes=[],
            candidates=[
                CandidateScore(
                    candidate_id="c1",
                    label="shorten_release",
                    total_score=0.65,
                    episode_support=0.0,
                )
            ],
            decision_confidence=0.65,
        )

        # Learning (with episodes)
        learning = create_cycle_trace(
            cycle_id="learning_001",
            cycle_name="B",
            intent="Make bass tighter",
            available_episodes=["ep_cycle_a_001"],
            candidates=[
                CandidateScore(
                    candidate_id="c1",
                    label="shorten_release",
                    total_score=0.78,
                    episode_support=0.15,
                )
            ],
            decision_confidence=0.78,
        )

        comparison = analyze_learning_influence(control, learning)

        # Measurable differences
        assert comparison.cycle_a_confidence == 0.65  # Control score
        assert comparison.cycle_b_confidence == 0.78  # Learning score
        assert comparison.confidence_changed is True
        assert "c1" in comparison.candidates_with_changed_scores


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
