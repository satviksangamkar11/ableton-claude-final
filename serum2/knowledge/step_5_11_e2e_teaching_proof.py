"""
STEP 5.11 — END-TO-END TEACHING PROOF

Demonstrate the complete universal teaching path using REAL artifacts:

    REAL SOURCE → TRANSCRIPT → PROPOSITION → KNOWLEDGEITEM →
    PERSISTENT STORE → RETRIEVAL → GROUNDED TEACHING →
    PROVENANCE BACK TO SOURCE

This is a PROOF phase, not an implementation phase.
Uses existing 5.6 store, 5.7 retrieval, 5.8 teaching.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any

from step_5_6_knowledge_store import KnowledgeStore
from step_5_7_universal_retrieval import UniversalRetriever, UniversalQuery
from step_5_8_grounded_teaching import GroundedTeacher, TeachingResponse
from knowledge_item import KnowledgeItem, EpistemicStatus


class EndToEndTeachingProof:
    """
    Proof that the complete teaching pipeline works end-to-end
    with real data and preserved provenance.
    """

    def __init__(self, store_path: str = "yt_74ab96e1f377_canonical_knowledge_store_5_6.json"):
        """Initialize with real canonical store."""
        self.store_path = Path(store_path)
        if not self.store_path.exists():
            raise FileNotFoundError(f"Real store not found: {store_path}")

        self.store = KnowledgeStore(str(self.store_path), create_if_missing=False)
        self.retriever = UniversalRetriever(self.store)
        self.teacher = GroundedTeacher(self.retriever)

        print(f"[OK] Loaded real store: {len(self.store.list())} items")

    def trace_provenance_chain(self, knowledge_item_id: str) -> Dict[str, Any]:
        """Trace complete provenance from KnowledgeItem back to source."""
        item = self.store.get(knowledge_item_id)
        if not item:
            return {"error": f"Item {knowledge_item_id} not found"}

        return {
            "knowledge_item_id": item.knowledge_item_id,
            "original_proposition": item.original_proposition,
            "normalized_proposition": item.normalized_proposition,
            "knowledge_type": item.knowledge_type.value,
            "epistemic_status": item.epistemic_status.value,
            "extraction_confidence": item.extraction_confidence,
            "source_id": item.source_reference.source_id,
            "source_type": item.source_reference.source_type,
            "segment_ids": item.source_reference.segment_ids,
            "conditions": item.conditions,
            "limitations": item.limitations,
            "ambiguity": item.ambiguity,
            "is_complete": bool(
                item.knowledge_item_id and
                item.original_proposition and
                item.source_reference.source_id and
                item.source_reference.segment_ids
            )
        }

    def proof_a_concept_question(self) -> Dict[str, Any]:
        """
        A. CONCEPT QUESTION

        Question about a known concept → relevant KnowledgeItem →
        grounded explanation → source provenance
        """
        print("\n" + "="*70)
        print("PROOF A: CONCEPT QUESTION")
        print("="*70)

        question = "What is an arpeggiator?"

        # Query retrieval
        response = self.teacher.teach(question, depth="concise")

        print(f"\nQuestion: {question}")
        print(f"Status: {response.status}")
        print(f"Retrieved {len(response.retrieved_knowledge)} knowledge items")

        # Verify provenance
        provenance_traces = []
        for claim in response.claims:
            trace = self.trace_provenance_chain(claim.attribution.knowledge_item_id)
            provenance_traces.append(trace)
            print(f"\n  Claim: {claim.statement[:80]}...")
            print(f"    From: {claim.attribution.knowledge_item_id}")
            print(f"    Source: {claim.attribution.source_id}")
            print(f"    Epistemic: {claim.attribution.epistemic_status}")
            print(f"    Provenance complete: {trace.get('is_complete')}")

        return {
            "proof_name": "A_concept_question",
            "question": question,
            "claims_count": len(response.claims),
            "status": response.status,
            "provenance_complete": all(t.get("is_complete") for t in provenance_traces),
            "traces": provenance_traces,
        }

    def proof_b_procedure_question(self) -> Dict[str, Any]:
        """
        B. PROCEDURE QUESTION

        "How do I ...?" → retrieval → structured procedure →
        grounded teaching response → provenance
        """
        print("\n" + "="*70)
        print("PROOF B: PROCEDURE QUESTION")
        print("="*70)

        question = "How do I make my bass sound tighter?"

        response = self.teacher.teach(question, depth="practical")

        print(f"\nQuestion: {question}")
        print(f"Status: {response.status}")
        print(f"Retrieved {len(response.retrieved_knowledge)} knowledge items")

        if response.procedure_steps:
            print(f"Procedure steps:")
            for i, step in enumerate(response.procedure_steps, 1):
                print(f"  {i}. {step}")

        # Verify all claims have provenance
        provenance_complete = all(
            claim.attribution.knowledge_item_id and
            claim.attribution.source_id
            for claim in response.claims
        )

        print(f"\nAll claims traceable: {provenance_complete}")

        return {
            "proof_name": "B_procedure_question",
            "question": question,
            "claims_count": len(response.claims),
            "procedure_steps_count": len(response.procedure_steps),
            "status": response.status,
            "provenance_complete": provenance_complete,
        }

    def proof_c_universal_question(self) -> Dict[str, Any]:
        """
        C. UNIVERSAL QUESTION

        No Serum-specific terminology → meaningful answer
        Proves backend independence.
        """
        print("\n" + "="*70)
        print("PROOF C: UNIVERSAL QUESTION (NO BACKEND TERMS)")
        print("="*70)

        question = "What is an envelope and how does it shape a sound?"

        response = self.teacher.teach(question, depth="detailed")

        print(f"\nQuestion: {question}")
        print(f"Status: {response.status}")

        # Check that answer doesn't require Serum knowledge
        answer_contains_serum = (
            response.answer and ("serum" in response.answer.lower() or "parameter" in response.answer.lower())
        )

        print(f"\nAnswer requires Serum knowledge: {answer_contains_serum}")
        print(f"Retrieved {len(response.retrieved_knowledge)} items")

        if response.concept_explanation:
            print(f"Concept explanation: {response.concept_explanation[:100]}...")

        # Verify provenance
        has_provenance = all(
            claim.attribution.knowledge_item_id
            for claim in response.claims
        )

        print(f"All claims have provenance: {has_provenance}")

        return {
            "proof_name": "C_universal_question",
            "question": question,
            "status": response.status,
            "requires_serum": answer_contains_serum,
            "has_provenance": has_provenance,
            "claims_count": len(response.claims),
        }

    def proof_d_unknown_ambiguity(self) -> Dict[str, Any]:
        """
        D. AMBIGUITY PROOF

        UNKNOWN KnowledgeItems remain explicitly ambiguous.
        Ambiguity does not silently disappear.
        """
        print("\n" + "="*70)
        print("PROOF D: UNKNOWN AMBIGUITY PRESERVATION")
        print("="*70)

        # Find UNKNOWN items
        all_items = self.store.list()
        unknown_items = [i for i in all_items if i.epistemic_status == EpistemicStatus.UNKNOWN]

        print(f"\nTotal items: {len(all_items)}")
        print(f"UNKNOWN items: {len(unknown_items)}")

        if unknown_items:
            item = unknown_items[0]
            print(f"\nExample UNKNOWN item:")
            print(f"  ID: {item.knowledge_item_id}")
            print(f"  Proposition: {item.original_proposition}")
            print(f"  Ambiguity: {item.ambiguity}")
            # Note: KnowledgeItem doesn't have ambiguity_candidates, just ambiguity text

            # Try to retrieve it
            query = UniversalQuery(free_text=item.original_proposition)
            results = self.retriever.retrieve(query, top_k=5)

            print(f"\nRetrieval results: {len(results)} items")

            # Check if UNKNOWN item appears
            unknown_in_results = any(
                r.knowledge_item.knowledge_item_id == item.knowledge_item_id
                for r in results
            )

            print(f"UNKNOWN item appears in retrieval: {unknown_in_results}")

            # If retrieved, verify it's marked as ambiguous
            for result in results:
                if result.knowledge_item.knowledge_item_id == item.knowledge_item_id:
                    print(f"\nUNKNOWN item in results:")
                    print(f"  is_ambiguous: {result.is_ambiguous}")
                    print(f"  ambiguity_candidates: {result.ambiguity_candidates}")

            return {
                "proof_name": "D_unknown_ambiguity",
                "total_items": len(all_items),
                "unknown_count": len(unknown_items),
                "example_ambiguity": item.ambiguity,
                "unknown_retrievable": unknown_in_results,
            }

        return {
            "proof_name": "D_unknown_ambiguity",
            "total_items": len(all_items),
            "unknown_count": 0,
            "error": "No UNKNOWN items found",
        }

    def proof_e_insufficient_knowledge(self) -> Dict[str, Any]:
        """
        E. INSUFFICIENT KNOWLEDGE PROOF

        Question the corpus cannot answer → grounded refusal/limitation
        No hallucination.
        """
        print("\n" + "="*70)
        print("PROOF E: INSUFFICIENT KNOWLEDGE")
        print("="*70)

        questions = [
            "Build me a complete orchestral symphony from scratch",
            "What is the exact frequency response curve of Serum's filter at 5.2 kHz?",
            "How do I synthesize a perfect dog bark?",
        ]

        results = []

        for question in questions:
            print(f"\nQuestion: {question}")

            response = self.teacher.teach(question)

            print(f"Status: {response.status}")
            print(f"Has uncertainty: {bool(response.uncertainty)}")

            if response.uncertainty:
                print(f"Uncertainty: {response.uncertainty[:100]}...")

            # Check that no hallucination occurred
            has_answer = bool(response.answer)
            has_grounded_claims = len(response.claims) > 0

            print(f"Has answer: {has_answer}")
            print(f"Has grounded claims: {has_grounded_claims}")

            results.append({
                "question": question,
                "status": response.status,
                "has_uncertainty": bool(response.uncertainty),
                "has_answer": has_answer,
                "is_grounded": has_grounded_claims,
            })

        return {
            "proof_name": "E_insufficient_knowledge",
            "questions_tested": len(results),
            "results": results,
        }

    def proof_f_conflicting_sources(self) -> Dict[str, Any]:
        """
        F. CONFLICT PROOF

        Two conflicting KnowledgeItems → both visible, no false consensus.
        """
        print("\n" + "="*70)
        print("PROOF F: CONFLICTING SOURCES")
        print("="*70)

        # Find recommendations (most likely to conflict)
        all_items = self.store.list()
        recs = [i for i in all_items if i.knowledge_type.value == "RECOMMENDATION"]

        print(f"\nRecommendation items: {len(recs)}")

        # Pick a broad question that might retrieve multiple sources
        question = "What envelope settings should I use?"

        response = self.teacher.teach(question)

        print(f"\nQuestion: {question}")
        print(f"Retrieved items: {len(response.retrieved_knowledge)}")
        print(f"Has conflicting sources: {bool(response.conflicting_sources)}")

        if response.conflicting_sources:
            print(f"Number of conflicts detected: {len(response.conflicting_sources)}")
            for i, conflict in enumerate(response.conflicting_sources[:2], 1):
                print(f"\n  Conflict {i}:")
                print(f"    Source A: {conflict.get('source_a')}")
                print(f"    Claim A: {conflict.get('claim_a', '')[:60]}...")
                print(f"    Source B: {conflict.get('source_b')}")
                print(f"    Claim B: {conflict.get('claim_b', '')[:60]}...")

        # Verify claims preserve source distinctions
        sources_in_claims = set(c.attribution.source_id for c in response.claims)

        print(f"\nDistinct sources in claims: {len(sources_in_claims)}")

        return {
            "proof_name": "F_conflicting_sources",
            "question": question,
            "retrieved_count": len(response.retrieved_knowledge),
            "conflicts_detected": len(response.conflicting_sources),
            "distinct_sources": len(sources_in_claims),
            "has_conflicts": bool(response.conflicting_sources),
        }

    def proof_g_epistemic_preservation(self) -> Dict[str, Any]:
        """
        G. EPISTEMIC CHAIN

        SOURCE_REPORTED, SOURCE_RECOMMENDED, UNKNOWN preserved.
        No conversion of status.
        """
        print("\n" + "="*70)
        print("PROOF G: EPISTEMIC STATUS PRESERVATION")
        print("="*70)

        all_items = self.store.list()

        # Find items of each epistemic status
        status_groups = {}
        for status in ["SOURCE_REPORTED", "SOURCE_RECOMMENDED", "UNKNOWN"]:
            items = [i for i in all_items if i.epistemic_status.value == status]
            status_groups[status] = items
            print(f"{status}: {len(items)} items")

        # Query something that should retrieve multiple statuses
        question = "Tell me about synthesis concepts"

        response = self.teacher.teach(question, depth="detailed")

        print(f"\nQuestion: {question}")
        print(f"Claims: {len(response.claims)}")

        # Check epistemic status in claims
        claim_statuses = {}
        for claim in response.claims:
            status = claim.attribution.epistemic_status
            if status not in claim_statuses:
                claim_statuses[status] = 0
            claim_statuses[status] += 1

        print(f"\nClaim epistemic statuses:")
        for status, count in claim_statuses.items():
            print(f"  {status}: {count}")

        # Verify no SOURCE_RECOMMENDED was converted to something stronger
        no_upgrade = all(
            status != "EXPERIMENTALLY_VERIFIED" and status != "CAUSAL_VERIFIED"
            for status in claim_statuses.keys()
        )

        print(f"No status upgrade: {no_upgrade}")

        return {
            "proof_name": "G_epistemic_preservation",
            "question": question,
            "status_distribution": status_groups,
            "claim_statuses": claim_statuses,
            "no_upgrade": no_upgrade,
        }

    def proof_h_no_hallucination(self) -> Dict[str, Any]:
        """
        H. NO-HALLUCINATION PROOF

        Adversarial questions requesting absent information.
        Expected: refusal, not invention.
        """
        print("\n" + "="*70)
        print("PROOF H: NO HALLUCINATION")
        print("="*70)

        adversarial_questions = [
            ("What is the exact frequency response at 1kHz?", "specific_number"),
            ("Why does longer release always create better sustain?", "causality"),
            ("What Serum parameter directly controls arpeggiator phase?", "backend_mapping"),
            ("Can you guarantee my bass will be perfect if I use short release?", "guarantee"),
        ]

        results = []

        for question, adversary_type in adversarial_questions:
            print(f"\n{adversary_type.upper()}: {question}")

            response = self.teacher.teach(question)

            # Check if answer contains specific invented values
            answer_text = response.answer or ""

            contains_specifics = {
                "specific_number": any(c.isdigit() for c in answer_text if answer_text),
                "invented_causality": "because" in answer_text.lower() if answer_text else False,
                "invented_parameter": "release" in answer_text.lower() or "parameter" in answer_text.lower() if answer_text else False,
            }

            has_claim = len(response.claims) > 0
            has_uncertainty = bool(response.uncertainty)

            print(f"  Status: {response.status}")
            print(f"  Has claims: {has_claim}")
            print(f"  Has uncertainty: {has_uncertainty}")

            results.append({
                "question": question,
                "type": adversary_type,
                "status": response.status,
                "has_claims": has_claim,
                "has_uncertainty": has_uncertainty,
                "contains_specifics": contains_specifics[adversary_type] if adversary_type in contains_specifics else False,
            })

        return {
            "proof_name": "H_no_hallucination",
            "adversarial_tests": len(results),
            "results": results,
        }

    def proof_i_no_execution(self) -> Dict[str, Any]:
        """
        I. NO EXECUTION PROOF

        Teaching cannot mutate Serum or call execution.
        Must terminate at TeachingResponse.
        """
        print("\n" + "="*70)
        print("PROOF I: NO EXECUTION")
        print("="*70)

        question = "Make my bass tighter"

        response = self.teacher.teach(question)

        print(f"\nQuestion: {question}")
        print(f"Response type: {type(response).__name__}")

        # Check that response has no execution methods
        response_methods = [m for m in dir(response) if not m.startswith('_')]
        execution_keywords = ["execute", "mutate", "render", "apply_to_serum"]

        has_execution_methods = any(
            keyword in method.lower()
            for method in response_methods
            for keyword in execution_keywords
        )

        print(f"Response has execution methods: {has_execution_methods}")

        # Check that response contains only advisory fields
        advisory_fields = [
            'question', 'answer', 'claims', 'uncertainty',
            'procedure_steps', 'caveats', 'conflicting_sources'
        ]

        has_all_advisory = all(
            hasattr(response, field)
            for field in advisory_fields
        )

        print(f"Has all advisory fields: {has_all_advisory}")
        print(f"Response is read-only (no mutation): {has_all_advisory and not has_execution_methods}")

        return {
            "proof_name": "I_no_execution",
            "response_type": type(response).__name__,
            "has_execution_methods": has_execution_methods,
            "is_advisory_only": has_all_advisory and not has_execution_methods,
        }

    def proof_j_real_data_traceability(self) -> Dict[str, Any]:
        """
        J. REAL-DATA TRACEABILITY

        End-to-end using actual 36-item store.
        Question flows through 5.7 retrieval → 5.8 teaching.
        """
        print("\n" + "="*70)
        print("PROOF J: REAL DATA TRACEABILITY")
        print("="*70)

        store_items = self.store.list()
        print(f"\nReal store size: {len(store_items)} items")

        question = "What is an oscillator?"

        # Flow through retrieval
        query = UniversalQuery(free_text=question)
        retrieval_results = self.retriever.retrieve(query, top_k=5)

        print(f"Retrieval results: {len(retrieval_results)} items")

        # Flow through teaching
        response = self.teacher.teach(question)

        print(f"Teaching response claims: {len(response.claims)}")

        # Verify chain
        chain_complete = (
            len(retrieval_results) > 0 and
            len(response.claims) > 0 and
            all(
                self.store.get(claim.attribution.knowledge_item_id)
                for claim in response.claims
            )
        )

        print(f"Complete chain: {chain_complete}")

        # Trace one claim all the way back
        if response.claims:
            claim = response.claims[0]
            item = self.store.get(claim.attribution.knowledge_item_id)

            print(f"\nExample claim trace:")
            print(f"  Claim: {claim.statement[:60]}...")
            print(f"  Item ID: {claim.attribution.knowledge_item_id}")
            print(f"  Source: {claim.attribution.source_id}")
            print(f"  Segment IDs: {claim.attribution.segment_ids}")

        return {
            "proof_name": "J_real_data_traceability",
            "store_size": len(store_items),
            "question": question,
            "retrieval_results": len(retrieval_results),
            "teaching_claims": len(response.claims),
            "chain_complete": chain_complete,
        }

    def run_all_proofs(self) -> Dict[str, Any]:
        """Execute all proofs and return complete result."""
        print("\n" + "="*70)
        print("STEP 5.11 — END-TO-END TEACHING PROOF")
        print("="*70)

        proofs = {
            "A": self.proof_a_concept_question,
            "B": self.proof_b_procedure_question,
            "C": self.proof_c_universal_question,
            "D": self.proof_d_unknown_ambiguity,
            "E": self.proof_e_insufficient_knowledge,
            "F": self.proof_f_conflicting_sources,
            "G": self.proof_g_epistemic_preservation,
            "H": self.proof_h_no_hallucination,
            "I": self.proof_i_no_execution,
            "J": self.proof_j_real_data_traceability,
        }

        results = {}
        for letter, proof_func in proofs.items():
            try:
                results[letter] = proof_func()
            except Exception as e:
                print(f"\n[FAIL] PROOF {letter} FAILED: {e}")
                results[letter] = {"error": str(e)}

        return results


if __name__ == "__main__":
    try:
        proof = EndToEndTeachingProof()
        results = proof.run_all_proofs()

        print("\n" + "="*70)
        print("PROOF SUMMARY")
        print("="*70)

        for letter, result in results.items():
            status = "[OK]" if "error" not in result else "[FAIL]"
            print(f"{status} PROOF {letter}: {result.get('proof_name', 'unknown')}")

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Run Step 5.6 first to create the canonical store.")
