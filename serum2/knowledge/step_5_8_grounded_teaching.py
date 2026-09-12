"""
STEP 5.8 — GROUNDED TEACHING RUNTIME

Transform user questions into grounded explanations using retrieved knowledge.

CRITICAL CONSTRAINT: Only assert what is supported by retrieved sources.
Do NOT invent: causality, mechanisms, numbers, backend mappings, conditions.

Teaching ≠ Execution ≠ Authority ≠ Capability
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

from step_5_7_universal_retrieval import (
    UniversalQuery, UniversalRetriever, RetrievalResult, MatchType
)
from step_5_6_knowledge_store import KnowledgeStore
from knowledge_item import KnowledgeItem, EpistemicStatus


class ConfidenceLevel(Enum):
    """Confidence in a teaching claim based on evidence."""
    HIGH = "high"  # Directly stated by source
    MEDIUM = "medium"  # Synthesized from multiple sources
    LOW = "low"  # Partial evidence, requires inference
    UNKNOWN = "unknown"  # Insufficient evidence


@dataclass
class QuestionResolution:
    """
    Structured representation of what the question is asking.

    All fields represent RESOLVED aspects; unresolved aspects are absent.
    """
    original_question: str
    normalized_question: str
    concept: Optional[str] = None
    intent: Optional[str] = None
    technique: Optional[str] = None
    role: Optional[str] = None
    instrument: Optional[str] = None
    context: Optional[str] = None
    backend: Optional[str] = None  # Optional backend scope
    ambiguous: bool = False
    ambiguity_reason: Optional[str] = None


@dataclass
class SourceAttribution:
    """Track where a claim comes from."""
    knowledge_item_id: str
    source_id: str
    source_type: str
    source_title: Optional[str] = None
    segment_ids: List[str] = field(default_factory=list)
    epistemic_status: str = "UNKNOWN"
    confidence: float = 0.5


@dataclass
class TeachingClaim:
    """A single claim in the teaching explanation."""
    statement: str  # The claim
    confidence: ConfidenceLevel  # Confidence level
    attribution: SourceAttribution  # Where it comes from
    is_direct_quote: bool = False  # True if directly from source
    supporting_items: List[str] = field(default_factory=list)  # Related knowledge_item_ids


@dataclass
class TeachingResponse:
    """Structured teaching response."""
    question: QuestionResolution
    answer: Optional[str] = None
    concept_explanation: Optional[str] = None
    procedure_steps: List[str] = field(default_factory=list)
    expected_result: Optional[str] = None
    verification_criteria: Optional[str] = None
    caveats: List[str] = field(default_factory=list)
    uncertainty: Optional[str] = None
    conflicting_sources: List[Dict[str, str]] = field(default_factory=list)
    claims: List[TeachingClaim] = field(default_factory=list)
    retrieved_knowledge: List[RetrievalResult] = field(default_factory=list)
    status: str = "OK"  # OK, INSUFFICIENT_KNOWLEDGE, AMBIGUOUS, CONFLICTING
    depth: str = "concise"  # concise, practical, detailed


class GroundedTeacher:
    """
    Teaching runtime using grounded knowledge retrieval.

    All explanations are attributed and sourced.
    No hallucinations, no invented facts.
    """

    def __init__(self, retriever: UniversalRetriever):
        """
        Initialize teacher with a retriever.

        Args:
            retriever: UniversalRetriever instance (from 5.7)
        """
        self.retriever = retriever
        self.store = retriever.store

    def teach(
        self,
        question: str,
        depth: str = "concise",
        backend_scope: Optional[str] = None
    ) -> TeachingResponse:
        """
        Teach in response to a user question.

        Args:
            question: User's question
            depth: "concise", "practical", or "detailed"
            backend_scope: Optional backend (e.g., "Serum")

        Returns:
            TeachingResponse with grounded explanation
        """
        # Step 1: Resolve question
        resolution = self._resolve_question(question, backend_scope)

        # Step 2: Retrieve relevant knowledge
        retrieved = self._retrieve_for_question(resolution)

        # Step 3: Check if we have sufficient knowledge
        if not retrieved:
            return TeachingResponse(
                question=resolution,
                status="INSUFFICIENT_KNOWLEDGE",
                uncertainty="I don't have enough grounded knowledge in the current store to answer that confidently.",
                depth=depth,
            )

        # Step 4: Generate explanation
        response = self._generate_explanation(resolution, retrieved, depth)
        return response

    def _resolve_question(
        self,
        question: str,
        backend_scope: Optional[str] = None
    ) -> QuestionResolution:
        """
        Resolve a question into semantic dimensions.

        Does NOT invent dimensions. Only identifies what's explicitly asked.
        """
        question_lower = question.lower()

        # Extract keywords (simple heuristics; could be more sophisticated)
        concept = self._extract_concept(question)
        intent = self._extract_intent(question)
        technique = self._extract_technique(question)
        role = self._extract_role(question)
        instrument = self._extract_instrument(question)
        context = self._extract_context(question)

        # Check for ambiguity signals
        ambiguous = any(word in question_lower for word in [
            "ambiguous", "unclear", "what if", "could it", "might it"
        ])

        return QuestionResolution(
            original_question=question,
            normalized_question=question.strip(),
            concept=concept,
            intent=intent,
            technique=technique,
            role=role,
            instrument=instrument,
            context=context,
            backend=backend_scope,
            ambiguous=ambiguous,
        )

    def _retrieve_for_question(self, resolution: QuestionResolution) -> List[RetrievalResult]:
        """Retrieve knowledge relevant to the resolved question."""
        query = UniversalQuery(
            free_text=resolution.normalized_question,
            concept=resolution.concept,
            intent=resolution.intent,
            technique=resolution.technique,
            role=resolution.role,
            instrument=resolution.instrument,
            context=resolution.context,
            backend=resolution.backend,
        )

        results = self.retriever.retrieve(query, top_k=5)
        return results

    def _generate_explanation(
        self,
        resolution: QuestionResolution,
        retrieved: List[RetrievalResult],
        depth: str
    ) -> TeachingResponse:
        """Generate grounded explanation from retrieved knowledge."""
        response = TeachingResponse(
            question=resolution,
            retrieved_knowledge=retrieved,
            depth=depth,
        )

        if not retrieved:
            response.status = "INSUFFICIENT_KNOWLEDGE"
            response.uncertainty = "No relevant knowledge found."
            return response

        # Organize retrieved knowledge by type
        by_type = self._organize_by_type(retrieved)

        # Check for ambiguity in retrieved items
        unknown_items = [r for r in retrieved if r.is_ambiguous]
        if unknown_items and len(unknown_items) > len(retrieved) / 2:
            response.status = "AMBIGUOUS"
            response.uncertainty = self._generate_ambiguity_statement(unknown_items)

        # Check for conflicts
        conflicts = self._detect_conflicts(retrieved)
        if conflicts:
            response.conflicting_sources = conflicts

        # Generate main explanation
        response.answer = self._synthesize_answer(retrieved, depth)

        # Generate concept explanation if applicable
        if resolution.concept:
            response.concept_explanation = self._explain_concept(resolution.concept, retrieved)

        # Generate procedure if applicable
        if resolution.intent or resolution.technique:
            steps = self._extract_procedure(retrieved)
            if steps:
                response.procedure_steps = steps

        # Extract verification criteria
        response.verification_criteria = self._extract_verification(retrieved)

        # Extract caveats and conditions
        response.caveats = self._extract_caveats(retrieved)

        # Mark claims with provenance
        response.claims = self._generate_claims(retrieved)

        return response

    def _synthesize_answer(self, retrieved: List[RetrievalResult], depth: str) -> str:
        """
        Synthesize an answer from retrieved knowledge.

        GROUNDING RULE: Only use knowledge directly from the retrieved items.
        Do NOT invent, extrapolate, or assume.
        """
        lines = []

        for i, result in enumerate(retrieved[:3], 1):  # Top 3 results
            item = result.knowledge_item

            # Start with source attribution
            source_line = f"Source ({item.source_reference.source_id}): "

            # Add epistemic status
            status = item.epistemic_status.value
            if status == "UNKNOWN":
                source_line += "The available material is ambiguous but notes: "
            elif status == "SOURCE_RECOMMENDED":
                source_line += "The source recommends: "
            elif status == "SOURCE_OBSERVED":
                source_line += "The source explains: "
            elif status == "SOURCE_REPORTED":
                source_line += "The source states: "
            else:
                source_line += "The source indicates: "

            # Add the knowledge
            prop = item.normalized_proposition or item.original_proposition
            lines.append(source_line + prop)

            # Depth-specific additions
            if depth == "detailed":
                if item.conditions:
                    lines.append(f"  Conditions: {'; '.join(item.conditions)}")
                if item.limitations:
                    lines.append(f"  Limitations: {'; '.join(item.limitations)}")

        return "\n".join(lines) if lines else "No grounded knowledge available."

    def _explain_concept(self, concept: str, retrieved: List[RetrievalResult]) -> Optional[str]:
        """Generate grounded concept explanation."""
        concept_items = [
            r for r in retrieved
            if r.knowledge_item.knowledge_type.value == "CONCEPT"
        ]

        if not concept_items:
            return None

        item = concept_items[0].knowledge_item
        prop = item.normalized_proposition or item.original_proposition

        return f"{concept.title()}: {prop}"

    def _extract_procedure(self, retrieved: List[RetrievalResult]) -> List[str]:
        """Extract procedure steps from retrieved knowledge."""
        procedures = [
            r for r in retrieved
            if r.knowledge_item.knowledge_type.value == "PROCEDURE"
        ]

        if not procedures:
            return []

        steps = []
        for proc in procedures:
            prop = proc.knowledge_item.normalized_proposition or proc.knowledge_item.original_proposition
            steps.append(prop)

        return steps

    def _extract_verification(self, retrieved: List[RetrievalResult]) -> Optional[str]:
        """Extract how to verify or measure the result."""
        for result in retrieved:
            if result.knowledge_item.conditions:
                return "; ".join(result.knowledge_item.conditions)
        return None

    def _extract_caveats(self, retrieved: List[RetrievalResult]) -> List[str]:
        """Extract limitations and caveats from retrieved knowledge."""
        caveats = []

        for result in retrieved:
            item = result.knowledge_item

            # Add ambiguity as caveat
            if item.ambiguity:
                caveats.append(f"Ambiguous: {item.ambiguity}")

            # Add limitations
            if item.limitations:
                caveats.extend(item.limitations)

            # Add epistemic cautions
            if item.epistemic_status.value == "UNKNOWN":
                caveats.append("This item has unresolved semantic meaning")

        return caveats

    def _generate_claims(self, retrieved: List[RetrievalResult]) -> List[TeachingClaim]:
        """Generate attributed claims from retrieved knowledge."""
        claims = []

        for result in retrieved:
            item = result.knowledge_item

            claim = TeachingClaim(
                statement=item.original_proposition,
                confidence=self._map_confidence(item.epistemic_status.value),
                attribution=SourceAttribution(
                    knowledge_item_id=item.knowledge_item_id,
                    source_id=item.source_reference.source_id,
                    source_type=item.source_reference.source_type,
                    source_title=item.source_reference.source_title,
                    segment_ids=item.source_reference.segment_ids,
                    epistemic_status=item.epistemic_status.value,
                    confidence=item.extraction_confidence,
                ),
                is_direct_quote=True,
                supporting_items=[item.knowledge_item_id],
            )
            claims.append(claim)

        return claims

    def _organize_by_type(self, retrieved: List[RetrievalResult]) -> Dict[str, List[RetrievalResult]]:
        """Organize retrieved knowledge by type."""
        by_type = {}
        for result in retrieved:
            ktype = result.knowledge_item.knowledge_type.value
            if ktype not in by_type:
                by_type[ktype] = []
            by_type[ktype].append(result)
        return by_type

    def _detect_conflicts(self, retrieved: List[RetrievalResult]) -> List[Dict[str, str]]:
        """Detect conflicting recommendations in retrieved knowledge."""
        conflicts = []

        # Simple conflict detection: different recommendations for same concept
        recommendations = [
            r for r in retrieved
            if r.knowledge_item.knowledge_type.value == "RECOMMENDATION"
        ]

        if len(recommendations) > 1:
            for i, rec1 in enumerate(recommendations[:-1]):
                for rec2 in recommendations[i+1:]:
                    # If from different sources and mention opposite actions
                    if rec1.knowledge_item.source_reference.source_id != rec2.knowledge_item.source_reference.source_id:
                        conflicts.append({
                            "source_a": rec1.knowledge_item.source_reference.source_id,
                            "claim_a": rec1.knowledge_item.original_proposition[:100],
                            "source_b": rec2.knowledge_item.source_reference.source_id,
                            "claim_b": rec2.knowledge_item.original_proposition[:100],
                        })

        return conflicts

    def _generate_ambiguity_statement(self, unknown_items: List[RetrievalResult]) -> str:
        """Generate statement about ambiguous knowledge."""
        candidates = []
        for result in unknown_items:
            if result.ambiguity_candidates:
                candidates.extend(result.ambiguity_candidates)

        if candidates:
            unique_candidates = list(set(candidates))
            return f"The available source material is ambiguous and could interpret as: {', '.join(unique_candidates)}"
        else:
            return "The available source material is ambiguous and cannot be resolved with current knowledge."

    # ===== QUESTION EXTRACTION HELPERS =====

    def _extract_concept(self, question: str) -> Optional[str]:
        """Extract concept term from question."""
        concepts = ["arpeggiator", "envelope", "oscillator", "filter", "resonance", "sustain"]
        q_lower = question.lower()
        for concept in concepts:
            if concept in q_lower:
                return concept
        return None

    def _extract_intent(self, question: str) -> Optional[str]:
        """Extract intent/goal from question."""
        intents = ["tighter", "darker", "brighter", "longer", "shorter", "smoother"]
        q_lower = question.lower()
        for intent in intents:
            if intent in q_lower:
                return intent
        return None

    def _extract_technique(self, question: str) -> Optional[str]:
        """Extract technique from question."""
        techniques = ["modulation", "sequencing", "filtering", "sampling", "mapping"]
        q_lower = question.lower()
        for technique in techniques:
            if technique in q_lower:
                return technique
        return None

    def _extract_role(self, question: str) -> Optional[str]:
        """Extract musical role from question."""
        roles = ["bass", "pad", "lead", "drum", "percussion", "melody"]
        q_lower = question.lower()
        for role in roles:
            if role in q_lower:
                return role
        return None

    def _extract_instrument(self, question: str) -> Optional[str]:
        """Extract instrument from question."""
        instruments = ["synth", "piano", "guitar", "strings", "horn"]
        q_lower = question.lower()
        for instrument in instruments:
            if instrument in q_lower:
                return instrument
        return None

    def _extract_context(self, question: str) -> Optional[str]:
        """Extract context from question."""
        contexts = ["ambient", "dance", "film", "classical", "electronic"]
        q_lower = question.lower()
        for context in contexts:
            if context in q_lower:
                return context
        return None

    def _map_confidence(self, epistemic_status: str) -> ConfidenceLevel:
        """Map epistemic status to confidence level."""
        mapping = {
            "SOURCE_REPORTED": ConfidenceLevel.HIGH,
            "SOURCE_RECOMMENDED": ConfidenceLevel.HIGH,
            "SOURCE_OBSERVED": ConfidenceLevel.MEDIUM,
            "SYSTEM_INTERPRETATION": ConfidenceLevel.MEDIUM,
            "EXPERIMENTALLY_VERIFIED": ConfidenceLevel.HIGH,
            "UNKNOWN": ConfidenceLevel.LOW,
        }
        return mapping.get(epistemic_status, ConfidenceLevel.UNKNOWN)

    def explain_response(self, response: TeachingResponse) -> str:
        """Generate human-readable explanation of response."""
        lines = [
            f"Question: {response.question.original_question}",
            f"Status: {response.status}",
        ]

        if response.answer:
            lines.append(f"\nAnswer:\n{response.answer}")

        if response.concept_explanation:
            lines.append(f"\nConcept:\n{response.concept_explanation}")

        if response.procedure_steps:
            lines.append("\nProcedure:")
            for i, step in enumerate(response.procedure_steps, 1):
                lines.append(f"  {i}. {step}")

        if response.verification_criteria:
            lines.append(f"\nVerification:\n{response.verification_criteria}")

        if response.caveats:
            lines.append("\nCaveats:")
            for caveat in response.caveats:
                lines.append(f"  • {caveat}")

        if response.uncertainty:
            lines.append(f"\nUncertainty:\n{response.uncertainty}")

        if response.conflicting_sources:
            lines.append("\nConflicting Sources:")
            for conflict in response.conflicting_sources:
                lines.append(f"  {conflict['source_a']}: {conflict['claim_a']}...")
                lines.append(f"  {conflict['source_b']}: {conflict['claim_b']}...")

        return "\n".join(lines)
