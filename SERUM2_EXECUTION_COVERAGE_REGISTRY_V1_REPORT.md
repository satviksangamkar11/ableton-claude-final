# SERUM2_EXECUTION_COVERAGE_REGISTRY_V1 -- Coverage Report

**Total frozen technical targets:** 396

## State distribution

- **EXECUTABLE_HOST**: 141
- **EXECUTABLE_BODY**: 0
- **EXECUTABLE_COMPOUND**: 0
- **EXECUTABLE_TOPOLOGY**: 0
- **EXECUTABLE_RESOURCE**: 0
- **UNRESOLVED**: 255
- **REFUSED_NON_USER_CONTROL**: 0

## Execution family distribution

- **HOST_PARAMETER**: 359
- **MATRIX_ROUTE**: 21
- **BODY_STATE**: 16

## Production / qualification status

- Registered in production `SEMANTIC_TARGETS` (has capability_key): 255/396
- NOT registered in production at all: 141/396
- Has a real, qualified `CapabilityContract`: 2/396

## Key structural finding: two SEPARATE gaps, not one

- `EXECUTABLE_HOST` (141): all `target_source=SYNTH_PARAMETER`, host name now live-verified against the current plugin. **0/141** already have a `capability_key` in production -- i.e. **141 are fully binding-ready but completely unregistered in `SEMANTIC_TARGETS`.**
- `UNRESOLVED` (255): all `target_source=FX_PARAMETER` (or routing). **255/255** already have a `capability_key` in production but no `host_parameter_name` claim exists in the V4 vocabulary at all -- these were registered via a different path (fx_resolver-style) and need mutation-path derivation, not name lookup.
- These are two independent, non-overlapping problems requiring different fixes: (1) register the 141 already-binding-ready SYNTH_PARAMETER targets into `SEMANTIC_TARGETS` (mechanical, low-risk, follows the exact D.1.2 Release/Attack precedent), vs (2) derive real mutation paths for the 255 already-registered FX_PARAMETER targets (requires fx_resolver / body-state path work, higher effort per target).

## Blocking reasons (UNRESOLVED targets, grouped)

- 218x: no host_parameter_name claim recorded in target vocabulary V4
- 21x: parameter_kind=ROUTING_SLOT_FIELD / target_source=MATRIX_ROUTE
- 16x: parameter_kind=VST3_PLAIN_PARAM (CBOR body field candidate) but no body_path derived/verified yet

## Known limitations of this V1 pass

- `semantic_rows` is NOT populated: there is no existing, general, authoritative mapping from the 396 `target_id`s back to the 908 `semantic_id`s (only ENV1.ATTACK has a formal post-freeze reconciliation record). Building that join at scale is separate, unstarted work, not reopened semantic discovery.
- `EXECUTABLE_HOST` here means the host parameter NAME is live-verified to exist in the current plugin's parameter list -- it does NOT mean the mutation has been causally proven, or that a CapabilityContract exists. That distinction is `qualification_status`.
- `EXECUTABLE_BODY` / `EXECUTABLE_COMPOUND` counts are currently 0: the V4 vocabulary's `mutation_path` field is UNKNOWN for all 396 targets, so no body-path or routing-path has been derived/verified yet for any target. This is the concrete next-work item for those families.
- `EXECUTABLE_TOPOLOGY` / `EXECUTABLE_RESOURCE` / `REFUSED_NON_USER_CONTROL` are 0 in this pass: no target in the frozen 396-vocabulary V4 is currently tagged with a structural or resource `target_source`/`parameter_kind` distinguishable from the three categories above. The 908-semantic-level STRUCTURAL_OPERATION (10) and RESOURCE_OPERATION (41) families exist but have not yet been joined to specific `target_id`s in the 396 vocabulary.
