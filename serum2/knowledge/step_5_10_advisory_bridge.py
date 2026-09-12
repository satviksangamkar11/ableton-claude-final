"""
STEP 5.10 — KNOWLEDGE → PRODUCTION ADVISORY BRIDGE

Connect universal music knowledge to production reasoning without authorizing execution.

CRITICAL CONSTRAINT: Knowledge informs but does NOT authorize.

The frozen Step 4 authority chain remains:
    EvidenceRecord → ClaimDefinition → ClaimEngine → ClaimGroup →
    CapabilityContract → Admission → Execution

Knowledge sits OUTSIDE this chain.

AdvisoryProposal = "Based on available knowledge, this may be useful"
NOT = "This is authorized"
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

from step_5_6_knowledge_store import KnowledgeStore
from step_5_9_universal_procedures import UniversalProcedure, UniversalProcedureExtractor
from knowledge_item import KnowledgeItem, EpistemicStatus


class ProposalConfidence(Enum):
    """Confidence in an advisory proposal based on source evidence."""
    HIGH = "high"  # Multiple sources, SOURCE_REPORTED/OBSERVED
    MEDIUM = "medium"  # SOURCE_RECOMMENDED or single SOURCE_REPORTED
    LOW = "low"  # SOURCE_RECOMMENDED alone or EXPERIMENTALLY_VERIFIED
    UNKNOWN = "unknown"  # UNKNOWN epistemic status


class ProposalStatus(Enum):
    """Status of proposal generation and capability lookup."""
    ADVISORY_CREATED = "advisory_created"  # Proposal created, advisory only
    CAPABILITY_FOUND = "capability_found"  # Existing CapabilityContract available
    CAPABILITY_ABSENT = "capability_absent"  # No capable contract available
    AMBIGUOUS_SOURCE = "ambiguous_source"  # Source material is UNKNOWN
    CONFLICTING_SOURCES = "conflicting_sources"  # Sources contradict
    INSUFFICIENT_DETAIL = "insufficient_detail"  # Not enough source info for proposal


@dataclass
class UniversalAdvisoryProposal:
    """
    Backend-independent production proposal informed by knowledge.

    This is advisory only. It does NOT represent authorization.
    It may inform capability selection but cannot override CapabilityContract.
    """
    proposal_id: str  # Derived from source knowledge_item_ids

    # Semantic content (universal, no backend terms)
    intent: str  # What the user wants to achieve
    objective: str  # What the proposal aims to do
    proposed_action: str  # Actionable step (universal terms)
    target_concept: Optional[str] = None  # What the action targets
    expected_effect: Optional[str] = None  # Expected outcome

    # Conditions and context
    conditions: List[str] = field(default_factory=list)  # When to apply
    context: Optional[str] = None  # Musical/production context
    verification_criterion: Optional[str] = None  # How to verify success

    # Provenance (MUST be complete)
    source_knowledge_item_ids: List[str] = field(default_factory=list)
    source_procedure_ids: List[str] = field(default_factory=list)
    source_episode_ids: List[str] = field(default_factory=list)
    segment_ids: List[str] = field(default_factory=list)

    # Epistemic state (preserved from source, never upgraded)
    epistemic_status: str = "UNKNOWN"  # Inherited from source
    extraction_confidence: float = 0.5
    proposal_confidence: ProposalConfidence = ProposalConfidence.MEDIUM

    # Ambiguity and conflicts (explicit, not suppressed)
    ambiguity: Optional[str] = None
    ambiguity_candidates: List[str] = field(default_factory=list)
    conflicting_sources: List[Dict[str, Any]] = field(default_factory=list)

    # Backend hint (ADVISORY, NON-AUTHORITATIVE)
    backend_hint: Optional[str] = None

    # Status and metadata
    status: ProposalStatus = ProposalStatus.ADVISORY_CREATED
    generation_rationale: str = ""

    def is_advisorily_complete(self) -> bool:
        """Check if proposal has sufficient advisory information."""
        return bool(
            self.intent and
            self.objective and
            self.proposed_action and
            self.source_knowledge_item_ids
        )

    def is_fully_sourced(self) -> bool:
        """Check if all content is traceable to source."""
        return bool(
            self.source_knowledge_item_ids and
            self.segment_ids and
            self.generation_rationale
        )

    def has_unresolved_ambiguity(self) -> bool:
        """Check if proposal contains unresolved ambiguity."""
        return (
            self.epistemic_status == "UNKNOWN" or
            bool(self.ambiguity) or
            bool(self.ambiguity_candidates)
        )

    def has_conflicts(self) -> bool:
        """Check if proposal reflects source conflicts."""
        return bool(self.conflicting_sources)


@dataclass
class AdvisoryProposalResult:
    """Result of advisory proposal generation and capability lookup."""
    proposal: Optional[UniversalAdvisoryProposal] = None

    # Source context
    source_knowledge_items: List[KnowledgeItem] = field(default_factory=list)
    source_procedures: List[UniversalProcedure] = field(default_factory=list)

    # Capability lookup result
    capability_found: bool = False
    capability_contract_id: Optional[str] = None

    # Refusal reason if blocked
    refusal_reason: Optional[str] = None

    # Is the proposal itself actionable?
    is_actionable: bool = False

    # Supporting explanation
    explanation: str = ""

    def __str__(self) -> str:
        if not self.proposal:
            return f"PROPOSAL REFUSED: {self.refusal_reason}"

        lines = [
            f"ADVISORY PROPOSAL: {self.proposal.intent}",
            f"  Objective: {self.proposal.objective}",
            f"  Action: {self.proposal.proposed_action}",
            f"  Status: {self.proposal.status.value}",
        ]

        if self.proposal.epistemic_status != "UNKNOWN":
            lines.append(f"  Epistemic: {self.proposal.epistemic_status}")

        if self.proposal.has_unresolved_ambiguity():
            lines.append(f"  ⚠ AMBIGUITY: {self.proposal.ambiguity}")

        if self.proposal.conflicting_sources:
            lines.append(f"  ⚠ CONFLICTS: {len(self.proposal.conflicting_sources)} sources disagree")

        if self.capability_found:
            lines.append(f"  ✓ Existing capability available: {self.capability_contract_id}")
        else:
            lines.append(f"  ✗ No existing capability")

        if self.refusal_reason:
            lines.append(f"  REFUSED: {self.refusal_reason}")

        return "\n".join(lines)


class UniversalAdvisoryBridge:
    """
    Bridge between knowledge layer and production advisory.

    Converts knowledge, procedures, and episodes into universal proposals
    that can inform (but not authorize) production decisions.

    Does NOT create new authority.
    Does NOT execute.
    Does NOT modify existing CapabilityContracts.
    """

    def __init__(self, store: KnowledgeStore):
        """Initialize bridge with knowledge store."""
        self.store = store
        self.procedure_extractor = UniversalProcedureExtractor(store)

    def propose_from_knowledge(
        self,
        intent: str,
        knowledge_items: Optional[List[KnowledgeItem]] = None
    ) -> AdvisoryProposalResult:
        """
        Generate an advisory proposal from knowledge items.

        Args:
            intent: User's stated intent
            knowledge_items: Retrieved knowledge items to base proposal on

        Returns:
            AdvisoryProposalResult with proposal or refusal reason
        """
        if not knowledge_items:
            return AdvisoryProposalResult(
                refusal_reason="No knowledge items provided",
                explanation="Cannot generate proposal without source knowledge."
            )

        # Check for ambiguity
        unknown_items = [k for k in knowledge_items if k.epistemic_status == EpistemicStatus.UNKNOWN]
        if unknown_items and len(unknown_items) > len(knowledge_items) / 2:
            return AdvisoryProposalResult(
                refusal_reason="Source material is predominantly ambiguous",
                explanation=f"{len(unknown_items)} of {len(knowledge_items)} sources have UNKNOWN epistemic status.",
                source_knowledge_items=knowledge_items
            )

        # Check for conflicts
        conflicting = self._detect_conflicts(knowledge_items)

        # Generate proposal
        proposal = self._synthesize_proposal(
            intent=intent,
            knowledge_items=knowledge_items,
            conflicts=conflicting
        )

        if not proposal:
            return AdvisoryProposalResult(
                refusal_reason="Insufficient detail to construct proposal",
                explanation="Knowledge items do not contain enough actionable content.",
                source_knowledge_items=knowledge_items
            )

        return AdvisoryProposalResult(
            proposal=proposal,
            source_knowledge_items=knowledge_items,
            is_actionable=proposal.is_advisorily_complete(),
            explanation=proposal.generation_rationale
        )

    def propose_from_procedure(
        self,
        procedure: UniversalProcedure,
        user_intent: str
    ) -> AdvisoryProposalResult:
        """
        Generate an advisory proposal from a procedure.

        Args:
            procedure: Extracted universal procedure
            user_intent: User's stated intent

        Returns:
            AdvisoryProposalResult
        """
        if procedure.epistemic_status == EpistemicStatus.UNKNOWN.value:
            return AdvisoryProposalResult(
                refusal_reason="Source procedure has unresolved ambiguity",
                explanation=f"Procedure from {procedure.source_knowledge_item_id} is marked UNKNOWN.",
                source_procedures=[procedure]
            )

        # Get source knowledge item
        source_item = self.store.get(procedure.source_knowledge_item_id)
        if not source_item:
            return AdvisoryProposalResult(
                refusal_reason="Source knowledge item not found in store",
                source_procedures=[procedure]
            )

        # Synthesize proposal from procedure
        proposal = UniversalAdvisoryProposal(
            proposal_id=f"prop_{procedure.procedure_id[5:]}",
            intent=user_intent,
            objective=procedure.objective,
            proposed_action=". ".join([s.action for s in procedure.steps]) if procedure.steps else procedure.objective,
            target_concept=procedure.context,
            expected_effect=procedure.expected_effect,
            conditions=procedure.conditions,
            context=procedure.context,
            verification_criterion=procedure.verification_criterion,
            source_knowledge_item_ids=[procedure.source_knowledge_item_id],
            source_procedure_ids=[procedure.procedure_id],
            segment_ids=procedure.segment_ids,
            epistemic_status=procedure.epistemic_status,
            extraction_confidence=procedure.extraction_confidence,
            proposal_confidence=self._map_to_proposal_confidence(procedure.epistemic_status),
            status=ProposalStatus.ADVISORY_CREATED,
            generation_rationale=f"Synthesized from procedure {procedure.procedure_id} (from knowledge item {procedure.source_knowledge_item_id})"
        )

        return AdvisoryProposalResult(
            proposal=proposal,
            source_knowledge_items=[source_item],
            source_procedures=[procedure],
            is_actionable=proposal.is_advisorily_complete(),
            explanation=proposal.generation_rationale
        )

    def mark_capability_available(
        self,
        result: AdvisoryProposalResult,
        capability_contract_id: str
    ) -> AdvisoryProposalResult:
        """
        Mark that an existing capability contract is available for this proposal.

        This does NOT authorize execution.
        It notes that a path through admission exists.

        Args:
            result: Existing proposal result
            capability_contract_id: ID of available contract (advisory)

        Returns:
            Updated result with capability info
        """
        if result.proposal:
            result.proposal.status = ProposalStatus.CAPABILITY_FOUND
            result.capability_contract_id = capability_contract_id
            result.capability_found = True

        return result

    def mark_capability_absent(
        self,
        result: AdvisoryProposalResult,
        reason: str
    ) -> AdvisoryProposalResult:
        """
        Mark that no capability contract is available for this proposal.

        This is the critical negative control: knowledge alone is insufficient.

        Args:
            result: Existing proposal result
            reason: Why no capability is available

        Returns:
            Updated result
        """
        if result.proposal:
            result.proposal.status = ProposalStatus.CAPABILITY_ABSENT

        result.refusal_reason = f"No capability available: {reason}"
        result.capability_found = False

        return result

    def _synthesize_proposal(
        self,
        intent: str,
        knowledge_items: List[KnowledgeItem],
        conflicts: List[Dict[str, Any]]
    ) -> Optional[UniversalAdvisoryProposal]:
        """Synthesize an advisory proposal from knowledge items."""
        if not knowledge_items:
            return None

        # Use highest-confidence item as primary
        by_status = {}
        for item in knowledge_items:
            status = item.epistemic_status.value
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(item)

        primary_item = None
        for status in ["SOURCE_REPORTED", "SOURCE_OBSERVED", "SOURCE_RECOMMENDED", "EXPERIMENTALLY_VERIFIED"]:
            if status in by_status and by_status[status]:
                primary_item = by_status[status][0]
                break

        if not primary_item:
            primary_item = knowledge_items[0]

        # Extract objective from proposition
        prop = primary_item.original_proposition
        objective = self._extract_objective_from_proposition(prop)

        # Extract context from semantic bindings if available
        context_binding = None
        for binding in primary_item.semantic_bindings:
            if binding.dimension == "context":
                context_binding = binding.value
                break

        proposal = UniversalAdvisoryProposal(
            proposal_id=f"prop_{primary_item.knowledge_item_id[3:]}",
            intent=intent,
            objective=objective,
            proposed_action=prop[:150],  # First 150 chars as action summary
            target_concept=self._extract_concept(prop),
            expected_effect=self._extract_expected_effect(prop),
            conditions=primary_item.conditions,
            context=context_binding,
            verification_criterion=None,
            source_knowledge_item_ids=[item.knowledge_item_id for item in knowledge_items],
            segment_ids=primary_item.source_reference.segment_ids,
            epistemic_status=primary_item.epistemic_status.value,
            extraction_confidence=primary_item.extraction_confidence,
            proposal_confidence=self._map_to_proposal_confidence(primary_item.epistemic_status.value),
            ambiguity=primary_item.ambiguity,
            ambiguity_candidates=[],  # Pulled from source if available
            conflicting_sources=conflicts,
            status=ProposalStatus.ADVISORY_CREATED,
            generation_rationale=f"Synthesized from {len(knowledge_items)} knowledge items; primary source: {primary_item.knowledge_item_id}"
        )

        return proposal if proposal.is_advisorily_complete() else None

    def _detect_conflicts(self, items: List[KnowledgeItem]) -> List[Dict[str, Any]]:
        """Detect conflicting recommendations in knowledge items."""
        conflicts = []

        recommendations = [i for i in items if i.knowledge_type.value == "RECOMMENDATION"]

        if len(recommendations) > 1:
            for i, rec1 in enumerate(recommendations[:-1]):
                for rec2 in recommendations[i+1:]:
                    # Check if from different sources and mention opposite concepts
                    if rec1.source_reference.source_id != rec2.source_reference.source_id:
                        conflicts.append({
                            "source_a": rec1.source_reference.source_id,
                            "claim_a": rec1.original_proposition[:100],
                            "source_b": rec2.source_reference.source_id,
                            "claim_b": rec2.original_proposition[:100],
                        })

        return conflicts

    def _extract_objective_from_proposition(self, prop: str) -> str:
        """Extract objective/goal from proposition text."""
        indicators = ["to", "for", "make", "create", "achieve"]
        for ind in indicators:
            idx = prop.lower().find(ind)
            if idx >= 0:
                end = prop.find(".", idx)
                if end < 0:
                    end = len(prop)
                goal = prop[idx:min(idx + 80, end)].strip()
                if goal:
                    return goal
        return prop[:80]

    def _extract_concept(self, prop: str) -> Optional[str]:
        """Extract concept from proposition."""
        concepts = ["arpeggiator", "envelope", "oscillator", "filter", "resonance", "sustain", "release"]
        prop_lower = prop.lower()
        for concept in concepts:
            if concept in prop_lower:
                return concept
        return None

    def _extract_expected_effect(self, prop: str) -> Optional[str]:
        """Extract expected effect from proposition."""
        indicators = ["result", "effect", "makes", "creates", "causes"]
        for ind in indicators:
            idx = prop.lower().find(ind)
            if idx >= 0:
                end = prop.find(".", idx)
                if end < 0:
                    end = len(prop)
                effect = prop[idx:min(idx + 80, end)].strip()
                if effect:
                    return effect
        return None

    def _map_to_proposal_confidence(self, epistemic_status: str) -> ProposalConfidence:
        """Map epistemic status to proposal confidence."""
        mapping = {
            "SOURCE_REPORTED": ProposalConfidence.HIGH,
            "SOURCE_OBSERVED": ProposalConfidence.HIGH,
            "SOURCE_RECOMMENDED": ProposalConfidence.MEDIUM,
            "EXPERIMENTALLY_VERIFIED": ProposalConfidence.MEDIUM,
            "SYSTEM_INTERPRETATION": ProposalConfidence.LOW,
            "UNKNOWN": ProposalConfidence.UNKNOWN,
        }
        return mapping.get(epistemic_status, ProposalConfidence.UNKNOWN)
