"""Contract registry for canonical producer.

Unified access to fresh CapabilityContracts from 4.Q.4 qualifications.
Source of truth for which contracts are available to the producer.

Maps semantic targets to their CAUSAL_VERIFIED contracts.
Never falls back to design-JSON or archived contracts.
"""
import json
import pickle
import dataclasses
from typing import Optional, Dict, Tuple
from pathlib import Path

from serum2.evidence.capability_contract import CapabilityContract, ExecutionBinding


class ContractRegistry:
    """Unified registry for fresh CapabilityContracts.

    Loads contracts from 4.Q.4 pickle stores:
    - _capability_contracts_4_1.pkl (Release)
    - _capability_contracts_4_2.pkl (Attack)

    Never consults design-JSON or archived stores.

    D.1.2: Attaches ExecutionBinding to loaded contracts, derived from the
    authoritative semantic_vst3_mapping.json (the same source
    resolve_host_param_name() already uses). This does NOT edit the pickled
    evidence artifacts; it augments the in-memory contract object at load
    time via dataclasses.replace(), since CapabilityContract is frozen.
    """

    def __init__(self):
        self.contracts = {}
        self._host_param_mapping = self._load_host_param_mapping()
        self._load_fresh_contracts()

    def _load_host_param_mapping(self) -> Dict[str, str]:
        """Load the authoritative capability_key -> host parameter name mapping.

        Same source used by canonical_feedback_loop.resolve_host_param_name().
        """
        mapping_path = Path(__file__).parent.parent / "qualification" / "semantic_vst3_mapping.json"
        try:
            with open(mapping_path) as f:
                data = json.load(f)
            return data.get("mappings", {})
        except FileNotFoundError:
            print(f"[ContractRegistry] Warning: mapping not found: {mapping_path}")
            return {}

    def _attach_execution_binding(self, contract: CapabilityContract) -> CapabilityContract:
        """Derive and attach the authoritative ExecutionBinding for a contract.

        contract.target IS the capability_key (e.g. 'envelope_field_release').
        Binding source is semantic_vst3_mapping.json -- the same authoritative,
        runtime-verified mapping the producer already trusts. If no mapping
        entry exists, the contract is returned unchanged (execution_binding
        stays None) and the executor will correctly refuse it.
        """
        host_param_name = self._host_param_mapping.get(contract.target)
        if host_param_name is None:
            return contract

        binding = ExecutionBinding(
            mutation_type="HOST_PARAMETER",
            body_path=None,
            host_parameter_name=host_param_name,
            binding_source="semantic_vst3_mapping.json",
            binding_version=str(1),
        )
        return dataclasses.replace(contract, execution_binding=binding)

    def _load_fresh_contracts(self):
        """Load fresh contracts from 4.Q.4 qualification pickle stores."""
        base_path = Path(__file__).parent.parent.parent / "experiments"

        # Load 4.1 Release contract
        store_4_1_path = base_path / "_capability_contracts_4_1.pkl"
        if store_4_1_path.exists():
            try:
                with open(store_4_1_path, 'rb') as f:
                    store_4_1 = pickle.load(f)
                    for (claim_id, sig_hash), contract in store_4_1.items():
                        if contract.target == 'envelope_field_release':
                            contract = self._attach_execution_binding(contract)
                            self.contracts['envelope_field_release'] = contract
                            print(f"[ContractRegistry] Loaded Release contract: {contract.status}")
            except Exception as e:
                print(f"[ContractRegistry] Warning: Could not load Release contract: {e}")
        else:
            print(f"[ContractRegistry] Warning: Release contract store not found: {store_4_1_path}")

        # Load 4.2 Attack contract
        store_4_2_path = base_path / "_capability_contracts_4_2.pkl"
        if store_4_2_path.exists():
            try:
                with open(store_4_2_path, 'rb') as f:
                    store_4_2 = pickle.load(f)
                    for (claim_id, sig_hash), contract in store_4_2.items():
                        if contract.target == 'envelope_field_attack':
                            contract = self._attach_execution_binding(contract)
                            self.contracts['envelope_field_attack'] = contract
                            print(f"[ContractRegistry] Loaded Attack contract: {contract.status}")
            except Exception as e:
                print(f"[ContractRegistry] Warning: Could not load Attack contract: {e}")
        else:
            print(f"[ContractRegistry] Warning: Attack contract store not found: {store_4_2_path}")

    def get_contracts_dict(self) -> Dict[Tuple[str, str], CapabilityContract]:
        """Return contracts in format expected by admission.admit().

        admission.admit() expects Dict[(claim_id, condition_sig_hash) -> CapabilityContract]
        We reconstruct these keys from the contract's internal provenance.

        Returns:
            Dict mapping (claim_id, condition_sig_hash) to contract
        """
        result = {}
        for target, contract in self.contracts.items():
            # Extract claim_id from contract (set during build_contract)
            claim_id = getattr(contract, 'claim_definition_id', target)
            # Extract condition signature hash from scope
            sig_hash = contract.scope.get('condition_signature_hash', 'unknown')
            key = (claim_id, sig_hash)
            result[key] = contract
        return result

    def get(self, semantic_target: str) -> Optional[CapabilityContract]:
        """Get contract for a semantic target.

        Args:
            semantic_target: e.g., "envelope_field_release"

        Returns:
            CapabilityContract if available, None otherwise
        """
        return self.contracts.get(semantic_target)

    def all_targets(self) -> list:
        """Return list of all registered semantic targets."""
        return list(self.contracts.keys())
