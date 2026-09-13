"""
STEP 5.9 — UNIVERSAL PROCEDURE REPRESENTATION

Create structured, sourced procedural knowledge independent of backend.

CORE PRINCIPLE: Only extract procedures that are explicitly supported by
source material. Better to skip than to invent.

Procedure ≠ Recommendation ≠ Principle ≠ Capability ≠ Execution
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

from step_5_6_knowledge_store import KnowledgeStore
from knowledge_item import KnowledgeItem, KnowledgeType, EpistemicStatus


class ProcedureStatus(Enum):
    """Status of procedure extraction."""
    EXTRACTED = "extracted"  # Procedure created
    INSUFFICIENT_DETAIL = "insufficient_detail"  # Has steps but lacks structure
    RECOMMENDATION_ONLY = "recommendation_only"  # Recommendation, not full procedure
    TYPE_MISMATCH = "type_mismatch"  # Knowledge type not procedure-appropriate
    AMBIGUOUS = "ambiguous"  # UNKNOWN epistemic status
    NO_STEPS = "no_steps"  # Can't identify actionable steps


@dataclass
class ProcedureStep:
    """A single actionable step in a procedure."""
    order: Optional[int] = None  # None if steps are unordered
    action: str = ""  # The action to perform
    target: Optional[str] = None  # What the action targets (e.g., "release", "filter")
    expected_result: Optional[str] = None  # Expected outcome (source-stated)
    condition: Optional[str] = None  # When this step applies
    caution: Optional[str] = None  # Warning about this step


@dataclass
class UniversalProcedure:
    """
    Universal music/production procedure.

    Linked to source KnowledgeItem but independent of backend.
    Only contains source-supported information.
    """
    procedure_id: str  # Derived from knowledge_item_id
    source_knowledge_item_id: str  # Immutable link to source
    source_id: str  # Where this came from
    knowledge_item_type: str  # Original KnowledgeType

    objective: str  # What the procedure achieves
    steps: List[ProcedureStep] = field(default_factory=list)
    steps_ordered: bool = True  # False if steps are unordered

    # Expected outcomes
    expected_effect: Optional[str] = None

    # Context when procedure applies
    prerequisites: List[str] = field(default_factory=list)  # Must be true first
    conditions: List[str] = field(default_factory=list)  # Applicability conditions
    context: Optional[str] = None  # Musical/production context

    # Safety information
    cautions: List[str] = field(default_factory=list)

    # Verification
    verification_criterion: Optional[str] = None

    # Source semantics
    epistemic_status: str = "UNKNOWN"
    extraction_confidence: float = 0.5

    # Provenance
    segment_ids: List[str] = field(default_factory=list)
    original_proposition: str = ""

    def is_sourced(self) -> bool:
        """Check if procedure is fully sourced."""
        return bool(
            self.source_knowledge_item_id
            and self.original_proposition
            and self.segment_ids
        )


class UniversalProcedureExtractor:
    """
    Extract procedures from KnowledgeItems.

    Conservative extraction: only create procedures with explicit support.
    """

    def __init__(self, store: KnowledgeStore):
        """Initialize with knowledge store."""
        self.store = store

    def extract_procedures(self) -> Dict[str, UniversalProcedure]:
        """
        Extract procedures from all KnowledgeItems in store.

        Returns:
            Dict of procedure_id -> UniversalProcedure
            Only includes successfully extracted procedures.
        """
        procedures = {}

        all_items = self.store.list()

        for item in all_items:
            procedure = self._extract_from_item(item)

            if procedure:
                procedures[procedure.procedure_id] = procedure

        return procedures

    def _extract_from_item(self, item: KnowledgeItem) -> Optional[UniversalProcedure]:
        """Extract procedure from a single KnowledgeItem, if appropriate."""
        # Reject UNKNOWN items
        if item.epistemic_status == EpistemicStatus.UNKNOWN:
            return None

        # Only extract from procedure-appropriate types
        ktype = item.knowledge_type
        if ktype == KnowledgeType.PROCEDURE:
            return self._extract_procedure(item)
        elif ktype == KnowledgeType.RECOMMENDATION:
            return self._extract_from_recommendation(item)
        elif ktype == KnowledgeType.PRINCIPLE:
            # Principles explain relationships, not procedures
            # Only create procedure if principle contains actionable guidance
            return self._extract_from_principle(item)
        elif ktype == KnowledgeType.OBSERVATION:
            # Observations are facts, not procedures
            return None
        elif ktype == KnowledgeType.EXAMPLE:
            # Examples may illustrate procedures but aren't procedures themselves
            return self._extract_from_example(item)
        elif ktype == KnowledgeType.CONCEPT:
            # Concepts are definitions, not procedures
            return None
        elif ktype == KnowledgeType.CONTEXT:
            # Context is situational, not procedural
            return None
        elif ktype == KnowledgeType.LIMITATION:
            # Limitations are constraints, not procedures
            return None
        elif ktype == KnowledgeType.CONDITION:
            # Conditions describe when something applies
            return None
        else:
            return None

    def _extract_procedure(self, item: KnowledgeItem) -> Optional[UniversalProcedure]:
        """Extract from a PROCEDURE KnowledgeItem."""
        prop = item.original_proposition

        # Parse the proposition for steps
        # Simple heuristic: split on action verbs
        steps = self._parse_steps(prop)

        if not steps:
            return None

        objective = self._extract_objective(prop)

        return UniversalProcedure(
            procedure_id=f"proc_{item.knowledge_item_id[3:]}",
            source_knowledge_item_id=item.knowledge_item_id,
            source_id=item.source_reference.source_id,
            knowledge_item_type=item.knowledge_type.value,
            objective=objective,
            steps=steps,
            epistemic_status=item.epistemic_status.value,
            extraction_confidence=item.extraction_confidence,
            segment_ids=item.source_reference.segment_ids,
            original_proposition=prop,
            conditions=item.conditions,
            cautions=item.limitations,
        )

    def _extract_from_recommendation(self, item: KnowledgeItem) -> Optional[UniversalProcedure]:
        """Extract from a RECOMMENDATION KnowledgeItem."""
        prop = item.original_proposition.lower()

        # Only create procedure if recommendation is sufficiently actionable
        # Keywords indicating procedural content
        procedural_keywords = [
            "use", "set", "adjust", "change", "enable", "disable",
            "shorten", "lengthen", "increase", "decrease", "apply",
            "try", "select", "avoid"
        ]

        has_procedural_verb = any(kw in prop for kw in procedural_keywords)

        if not has_procedural_verb:
            # Recommendation without procedural structure
            return None

        steps = self._parse_steps(item.original_proposition)

        if not steps:
            # Couldn't parse steps
            return None

        objective = self._extract_objective(item.original_proposition)

        return UniversalProcedure(
            procedure_id=f"proc_{item.knowledge_item_id[3:]}",
            source_knowledge_item_id=item.knowledge_item_id,
            source_id=item.source_reference.source_id,
            knowledge_item_type=item.knowledge_type.value,
            objective=objective,
            steps=steps,
            steps_ordered=False,  # Recommendations often unordered
            epistemic_status=item.epistemic_status.value,
            extraction_confidence=item.extraction_confidence,
            segment_ids=item.source_reference.segment_ids,
            original_proposition=item.original_proposition,
            conditions=item.conditions,
        )

    def _extract_from_principle(self, item: KnowledgeItem) -> Optional[UniversalProcedure]:
        """Extract from a PRINCIPLE KnowledgeItem if it contains actionable guidance."""
        prop = item.original_proposition.lower()

        # Principles explain relationships
        # Only extract if principle includes "should", "can", "use", etc.
        actionable_keywords = ["should", "use", "try", "set", "adjust", "apply"]

        has_actionable = any(kw in prop for kw in actionable_keywords)

        if not has_actionable:
            return None

        # Very conservative: only if clearly actionable
        steps = self._parse_steps(item.original_proposition)

        if not steps:
            return None

        return UniversalProcedure(
            procedure_id=f"proc_{item.knowledge_item_id[3:]}",
            source_knowledge_item_id=item.knowledge_item_id,
            source_id=item.source_reference.source_id,
            knowledge_item_type=item.knowledge_type.value,
            objective=self._extract_objective(item.original_proposition),
            steps=steps,
            epistemic_status=item.epistemic_status.value,
            extraction_confidence=item.extraction_confidence,
            segment_ids=item.source_reference.segment_ids,
            original_proposition=item.original_proposition,
        )

    def _extract_from_example(self, item: KnowledgeItem) -> Optional[UniversalProcedure]:
        """Extract from EXAMPLE KnowledgeItem if it illustrates a procedure."""
        # Examples illustrate but aren't generalizable procedures
        # Only extract if example is sufficiently general
        prop = item.original_proposition

        # Check for specific instance markers (avoid these)
        instance_markers = ["for example", "like", "such as", "this", "that"]

        if any(prop.lower().startswith(marker) for marker in instance_markers):
            # Too specific to be a universal procedure
            return None

        # Try to extract
        steps = self._parse_steps(prop)

        if not steps:
            return None

        return UniversalProcedure(
            procedure_id=f"proc_{item.knowledge_item_id[3:]}",
            source_knowledge_item_id=item.knowledge_item_id,
            source_id=item.source_reference.source_id,
            knowledge_item_type=item.knowledge_type.value,
            objective=self._extract_objective(prop),
            steps=steps,
            epistemic_status=item.epistemic_status.value,
            extraction_confidence=item.extraction_confidence,
            segment_ids=item.source_reference.segment_ids,
            original_proposition=prop,
        )

    def _parse_steps(self, proposition: str) -> List[ProcedureStep]:
        """
        Parse actionable steps from proposition text.

        Conservative: only if clearly identifiable.
        Returns empty list if steps cannot be reliably parsed.
        """
        steps = []

        # Very simple heuristic: look for imperative verbs
        # In a real system, this would use NLP/parsing
        verbs = ["use", "set", "adjust", "select", "shorten", "lengthen", "increase", "decrease"]

        for verb in verbs:
            if verb in proposition.lower():
                # Found an imperative sentence
                # Extract it as a step (very naive parsing)
                start_idx = proposition.lower().find(verb)
                if start_idx >= 0:
                    # Extract from verb to end of sentence or period
                    end_idx = proposition.find(".", start_idx)
                    if end_idx < 0:
                        end_idx = len(proposition)

                    action_text = proposition[start_idx:end_idx].strip()

                    if action_text:
                        step = ProcedureStep(
                            order=None,  # No ordering inferred
                            action=action_text,
                        )
                        steps.append(step)
                        break  # Only one step extracted from simple parsing

        return steps

    def _extract_objective(self, proposition: str) -> str:
        """Extract the objective/goal from proposition."""
        # Very simple: take first clause or goal indicator
        prop_lower = proposition.lower()

        goal_indicators = ["to", "for", "make", "create", "achieve"]

        for indicator in goal_indicators:
            idx = prop_lower.find(indicator)
            if idx >= 0:
                # Extract from indicator to end or period
                end_idx = proposition.find(".", idx)
                if end_idx < 0:
                    end_idx = len(proposition)

                goal_text = proposition[idx:min(idx + 80, end_idx)].strip()

                if goal_text:
                    return goal_text

        # Fallback: first 80 chars
        return proposition[:80]

    def get_coverage_report(self, procedures: Dict[str, UniversalProcedure]) -> Dict[str, Any]:
        """Generate coverage report."""
        all_items = self.store.list()

        by_type = {}
        procedure_count_by_type = {}

        for item in all_items:
            ktype = item.knowledge_type.value

            if ktype not in by_type:
                by_type[ktype] = 0
                procedure_count_by_type[ktype] = 0

            by_type[ktype] += 1

            # Check if this item produced a procedure
            proc_id = f"proc_{item.knowledge_item_id[3:]}"
            if proc_id in procedures:
                procedure_count_by_type[ktype] += 1

        return {
            "total_items": len(all_items),
            "total_procedures_extracted": len(procedures),
            "by_type": by_type,
            "procedures_by_type": procedure_count_by_type,
            "unknown_items_rejected": sum(1 for i in all_items if i.epistemic_status == EpistemicStatus.UNKNOWN),
        }
