"""Execution Coverage V2 -- schema, canonicalization, and reconciliation.

See SERUM2_EXECUTION_COVERAGE_REGISTRY_V2_REPORT.md for the coverage
report produced from this package, and this session's architecture
discussion for the frozen design this package implements:

  SemanticResolution (908 rows, keyed by semantic_id)
      -- resolves each semantic row to an execution_resolution state
         and, for target-linked rows, a technical_target_id.

  CapabilityBinding (deduplicated, keyed by capability_id)
      -- capability_id = hash(execution_family, canonical_authoritative_binding)
      -- many semantic_id rows may reference the same CapabilityBinding.
"""
