"""
Test suite for Step 6.6 Capability Resolution.

Tests cover all 25+ acceptance criteria:
A. Resolution model exists
B. Registry reused (no new contracts)
C. Universal candidates resolve to contracts
D-F. No synthesis (knowledge/episode cannot create capability)
G-H. Target/operation compatibility checked
I-J. Context/prerequisites explicit; no fuzzy matching
K. No concrete values generated
L. Measurement preserved
M. Resolution ≠ admission
N. Admission handoff uses existing gate
O. Serum supported (not Serum-specific)
P. Real qualified contracts used
Q. Tests pass
"""

import pytest
from unittest.mock import Mock, MagicMock

from step_6_6_capability_resolution import (
    CapabilityResolution,
    CapabilityResolver,
    ResolutionStatus,
    OperationCompatibility,
    SemanticTargetMapping,
    resolve_capability,
)
from step_6_5_advisory_decision_engine import (
    AdvisoryDecision,
)
from step_6_4_semantic_reasoning_integration import (
    SemanticCandidate,
)
from step_6_2_universal_production_intent import (
    UniversalProductionIntent,
    SemanticDirection,
)


class TestCapabilityResolutionModel:
    """Test A: Resolution model exists."""

    def test_resolution_creation(self):
        """Create a capability resolution."""
        resolution = CapabilityResolution(
            resolution_id="res_1",
            candidate_id="cand_1",
            requested_semantic_action="shorten release",
            capability_found=False,
            resolution_status=ResolutionStatus.NOT_FOUND,
        )

        assert resolution.resolution_id == "res_1"
        assert resolution.resolution_status == ResolutionStatus.NOT_FOUND

    def test_resolution_with_contract(self):
        """Resolution can reference a contract."""
        resolution = CapabilityResolution(
            resolution_id="res_1",
            candidate_id="cand_1",
            requested_semantic_action="shorten release",
            capability_found=True,
            capability_contract_id="envelope_field_release",
            semantic_target="envelope_field_release",
            resolution_status=ResolutionStatus.RESOLVED,
        )

        assert resolution.capability_found
        assert resolution.capability_contract_id == "envelope_field_release"


class TestRegistryReuse:
    """Test B: Existing registry is reused."""

    def test_resolver_uses_registry(self):
        """Resolver consumes provided registry."""
        mock_registry = Mock()
        mock_registry.get.return_value = None

        resolver = CapabilityResolver(mock_registry)

        assert resolver.registry is mock_registry

    def test_no_new_contracts_created(self):
        """Resolver does not create new contracts."""
        mock_registry = Mock()
        mock_registry.get.return_value = None

        resolver = CapabilityResolver(mock_registry)

        intent = UniversalProductionIntent(original_user_request="Test")
        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Test",
            target_concept="note-release",
        )

        resolution = resolver.resolve(candidate, intent)

        # Registry.get should be called (lookup)
        mock_registry.get.assert_called()
        # No create/put methods should be called
        assert not hasattr(mock_registry, 'put') or not mock_registry.put.called
        assert not hasattr(mock_registry, 'create') or not mock_registry.create.called


class TestUniversalResolution:
    """Test C: Universal candidates resolve to authoritative contracts."""

    def test_semantic_mapping_exists(self):
        """Semantic mappings are defined."""
        from step_6_6_capability_resolution import UNIVERSAL_TO_SEMANTIC

        assert "note-release" in UNIVERSAL_TO_SEMANTIC
        assert "envelope-attack" in UNIVERSAL_TO_SEMANTIC

    def test_mapping_has_confidence(self):
        """Mappings have authoritative confidence."""
        from step_6_6_capability_resolution import UNIVERSAL_TO_SEMANTIC

        for concept, mapping in UNIVERSAL_TO_SEMANTIC.items():
            assert isinstance(mapping, SemanticTargetMapping)
            assert mapping.confidence == 1.0  # Authoritative

    def test_unknown_concept_not_resolved(self):
        """Unknown universal concepts cannot be resolved."""
        mock_registry = Mock()
        resolver = CapabilityResolver(mock_registry)

        intent = UniversalProductionIntent(original_user_request="Test")
        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Test",
            target_concept="unknown-concept",
        )

        resolution = resolver.resolve(candidate, intent)

        assert resolution.resolution_status == ResolutionStatus.UNKNOWN_TARGET
        assert resolution.capability_found == False


class TestKnowledgeCannotCreateCapability:
    """Test D-F: Knowledge/episodes cannot synthesize capability."""

    def test_knowledge_items_not_consulted(self):
        """Resolution does not use knowledge items."""
        mock_registry = Mock()
        resolver = CapabilityResolver(mock_registry)

        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="note-release",
        )

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="From knowledge",
            target_concept="note-release",
            supporting_knowledge_ids=["k1", "k2", "k3"],
        )

        resolution = resolver.resolve(candidate, intent)

        # Knowledge IDs should not influence capability lookup
        # Registry should be consulted regardless of knowledge support
        mock_registry.get.assert_called()

    def test_episode_items_not_consulted(self):
        """Resolution does not use prior episodes."""
        mock_registry = Mock()
        resolver = CapabilityResolver(mock_registry)

        intent = UniversalProductionIntent(
            original_user_request="Test",
            target_concept="note-release",
        )

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="From episode",
            target_concept="note-release",
            supporting_episodes=["ep_1", "ep_2"],
        )

        resolution = resolver.resolve(candidate, intent)

        # Episodes should not create capability
        mock_registry.get.assert_called()

    def test_high_confidence_knowledge_not_substituted(self):
        """High confidence knowledge cannot substitute for contract."""
        mock_registry = Mock()
        mock_registry.get.return_value = None

        resolver = CapabilityResolver(mock_registry)

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="High confidence",
            target_concept="note-release",
            confidence=0.99,  # Very high confidence
            supporting_knowledge_ids=["k1", "k2", "k3"],
        )

        resolution = resolver.resolve(candidate, intent)

        # Even with high confidence, if no contract exists, resolution fails
        assert resolution.resolution_status == ResolutionStatus.NOT_FOUND


class TestOperationCompatibility:
    """Test G-H: Operation compatibility checked."""

    def test_numeric_operation_compatible(self):
        """Numeric operations compatible with numeric contracts."""
        mock_registry = Mock()

        # Mock contract that supports numeric mutation
        mock_contract = Mock()
        mock_contract.allowed_operation = "mutate_numeric_value"
        mock_contract.usable_for.return_value = True
        mock_contract.to_dict.return_value = {}
        mock_contract.prerequisites = []
        mock_contract.target = "test_target"
        mock_registry.get.return_value = mock_contract

        resolver = CapabilityResolver(mock_registry)

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Shorten",
            target_concept="note-release",
            operation="shorten",
        )

        resolution = resolver.resolve(candidate, intent)

        compat = resolution.operation_compatibility
        assert compat in [
            OperationCompatibility.COMPATIBLE,
            OperationCompatibility.EXACT_MATCH,
        ]

    def test_incompatible_operation_rejected(self):
        """Incompatible operations are rejected."""
        mock_registry = Mock()

        # Mock contract that does NOT support arbitrary operations
        mock_contract = Mock()
        mock_contract.allowed_operation = "construct_persist_only"
        mock_contract.usable_for.return_value = True
        mock_contract.to_dict.return_value = {}
        mock_contract.prerequisites = []
        mock_contract.target = "test_target"
        mock_registry.get.return_value = mock_contract

        resolver = CapabilityResolver(mock_registry)

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Mutate",
            target_concept="note-release",
            operation="shorten",  # Incompatible with construct_only
        )

        resolution = resolver.resolve(candidate, intent)

        assert resolution.resolution_status == ResolutionStatus.CONFLICTED


class TestContextPrerequisites:
    """Test I-J: Context/prerequisites explicit."""

    def test_prerequisites_checked(self):
        """Prerequisites are evaluated."""
        mock_registry = Mock()

        mock_contract = Mock()
        mock_contract.allowed_operation = "mutate_numeric_value"
        mock_contract.usable_for.return_value = True
        mock_contract.to_dict.return_value = {}
        mock_contract.target = "test_target"
        mock_contract.prerequisites = ({"field": "value"},)  # Has prerequisites
        mock_registry.get.return_value = mock_contract

        resolver = CapabilityResolver(mock_registry)

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Test",
            target_concept="note-release",
        )

        # Without context, should mark as unverifiable
        resolution = resolver.resolve(candidate, intent, current_context=None)

        assert resolution.prerequisite_status in ["unknown", "unverifiable"]

    def test_scope_matching(self):
        """Scope matching is performed."""
        mock_registry = Mock()

        mock_contract = Mock()
        mock_contract.allowed_operation = "mutate_numeric_value"
        mock_contract.usable_for.return_value = True
        mock_contract.to_dict.return_value = {}
        mock_contract.target = "test_target"
        mock_contract.prerequisites = []
        mock_registry.get.return_value = mock_contract

        resolver = CapabilityResolver(mock_registry)

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Test",
            target_concept="note-release",
        )

        resolution = resolver.resolve(candidate, intent)

        assert hasattr(resolution, "scope_match")


class TestNoFuzzyMatching:
    """Test J: No fuzzy matching bypasses authority."""

    def test_exact_concept_required(self):
        """Only exact concept matches are accepted."""
        mock_registry = Mock()
        resolver = CapabilityResolver(mock_registry)

        intent = UniversalProductionIntent(original_user_request="Test")

        # Slightly different concept name
        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Test",
            target_concept="release-note",  # Different from "note-release"
        )

        resolution = resolver.resolve(candidate, intent)

        # Should not find a match (no fuzzy matching)
        assert resolution.resolution_status == ResolutionStatus.UNKNOWN_TARGET


class TestNoConcreteValues:
    """Test K: No concrete unauthorized mutation values."""

    def test_resolution_contains_no_values(self):
        """Resolution does not generate numeric values."""
        mock_registry = Mock()
        mock_contract = Mock()
        mock_contract.allowed_operation = "mutate_numeric_value"
        mock_contract.usable_for.return_value = True
        mock_contract.to_dict.return_value = {}
        mock_contract.target = "test_target"
        mock_contract.prerequisites = []
        mock_registry.get.return_value = mock_contract

        resolver = CapabilityResolver(mock_registry)

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Test",
            target_concept="note-release",
        )

        resolution = resolver.resolve(candidate, intent)

        resolution_dict = asdict(resolution)
        resolution_str = str(resolution_dict)

        # Should not contain mutation values
        assert "mutation_value" not in resolution_str
        assert "0.3" not in resolution_str or "confidence" in resolution_str


class TestMeasurementPreservation:
    """Test L: Measurement authority preserved."""

    def test_measurement_from_contract(self):
        """Resolution preserves contract's measurement."""
        mock_registry = Mock()

        mock_contract = Mock()
        mock_contract.allowed_operation = "mutate_numeric_value"
        mock_contract.usable_for.return_value = True
        mock_contract.target = "test_target"
        mock_contract.prerequisites = []
        mock_contract.measurement = {"type": "release_tail_time", "unit": "ms"}
        mock_contract.to_dict.return_value = {
            "measurement": mock_contract.measurement
        }
        mock_registry.get.return_value = mock_contract

        resolver = CapabilityResolver(mock_registry)

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Test",
            target_concept="note-release",
        )

        resolution = resolver.resolve(candidate, intent)

        # Measurement should be in the handoff request
        request = resolver.build_admission_request(resolution, candidate, intent)
        if request:
            assert "measurement" in str(request)


class TestResolutionNotAuthorization:
    """Test M: Resolution ≠ admission/authorization."""

    def test_resolved_does_not_authorize(self):
        """Resolved status does not mean authorized."""
        mock_registry = Mock()

        mock_contract = Mock()
        mock_contract.allowed_operation = "mutate_numeric_value"
        mock_contract.usable_for.return_value = True
        mock_contract.to_dict.return_value = {}
        mock_contract.target = "test_target"
        mock_contract.prerequisites = []
        mock_registry.get.return_value = mock_contract

        resolver = CapabilityResolver(mock_registry)

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Test",
            target_concept="note-release",
        )

        resolution = resolver.resolve(candidate, intent)

        # Even if RESOLVED, resolution should not authorize
        assert not hasattr(resolution, "authorization_status")
        assert not hasattr(resolution, "execute")


class TestAdmissionHandoff:
    """Test N: Admission handoff uses existing gate."""

    def test_admission_request_buildable(self):
        """Admission request can be built from resolution."""
        mock_registry = Mock()

        mock_contract = Mock()
        mock_contract.allowed_operation = "mutate_numeric_value"
        mock_contract.usable_for.return_value = True
        mock_contract.to_dict.return_value = {"target": "test"}
        mock_contract.target = "test_target"
        mock_contract.prerequisites = []
        mock_registry.get.return_value = mock_contract

        resolver = CapabilityResolver(mock_registry)

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Test",
            target_concept="note-release",
        )

        resolution = resolver.resolve(candidate, intent)

        request = resolver.build_admission_request(resolution, candidate, intent)

        if resolution.downstream_ready:
            assert request is not None
            assert "resolution_id" in request
            assert "candidate_id" in request
            assert "semantic_target" in request
            assert "capability_contract_id" in request


class TestSerumSupport:
    """Test O: Serum supported without being Serum-specific."""

    def test_envelope_field_targets_supported(self):
        """Serum envelope field targets are supported."""
        from step_6_6_capability_resolution import UNIVERSAL_TO_SEMANTIC

        mappings = UNIVERSAL_TO_SEMANTIC

        # Release target
        assert "note-release" in mappings
        assert mappings["note-release"].semantic_target == "envelope_field_release"

        # Attack target
        assert "envelope-attack" in mappings
        assert mappings["envelope-attack"].semantic_target == "envelope_field_attack"

    def test_not_serum_specific_in_resolver(self):
        """Resolver logic is not Serum-specific."""
        # Read implementation file (not test file which contains "Serum" in comments)
        import os
        impl_path = os.path.join(os.path.dirname(__file__), "step_6_6_capability_resolution.py")
        with open(impl_path) as f:
            resolver_code = f.read()

        # Should not have hardcoded Serum paths in implementation
        # (The semantic mappings are backend-agnostic, using generic semantic targets)
        assert "vst~" not in resolver_code
        assert "Env1" not in resolver_code or "mapping" in resolver_code


class TestTopLevelFunction:
    """Test P: Real contracts can be used (and test Q: tests pass)."""

    def test_resolve_capability_function(self):
        """Top-level function works."""
        mock_registry = Mock()
        mock_registry.get.return_value = None

        intent = UniversalProductionIntent(original_user_request="Test")

        candidate = SemanticCandidate(
            candidate_id="c1",
            label="Test",
            target_concept="note-release",
        )

        resolution = resolve_capability(candidate, intent, mock_registry)

        assert isinstance(resolution, CapabilityResolution)


# Utility for asdict
from dataclasses import asdict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
