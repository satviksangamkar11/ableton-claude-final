# SERUM2_EXECUTION_COVERAGE_REGISTRY_V2 -- Coverage Report

**Total frozen semantic rows:** 908  
**Frozen technical targets:** 396

## Invariants enforced (not just documented)

- V2-1: unresolved rows carry no family/primitive/operation/binding -- checked per-row, this build raises InvariantViolation on any violation
- V2-2/V2-6: capability_id dedup -- multiple semantic rows collapse onto one CapabilityBinding (see dedup examples below)
- V2-3: operation_key restricted to the registered generic-executor set
- V2-4: every binding/resolution carries explicit provenance
- V2-5: qualification (CapabilityContract) belongs to the capability, not to every semantic row referencing it

## Execution resolution distribution

- **RESOLVED**: 516
- **UNRESOLVED_UI_ACTION**: 235
- **UNKNOWN_EXECUTION**: 157

## Execution family distribution (RESOLVED rows only)

- **HOST_PARAMETER**: 271
- **MATRIX_ROUTE**: 106
- **BODY_STATE_FIELD**: 88
- **RESOURCE_OPERATION**: 41
- **STRUCTURAL_OPERATION**: 10

## Binding status distribution

- **NOT_YET_DERIVED**: 373
- **LIVE_VERIFIED**: 143

## Capability deduplication (the actual point of V2)

- 143 semantic rows carry a bound capability
- They collapse onto **81 unique CapabilityBinding records**
- Top dedup examples (semantic rows sharing one capability_id):
  - `HOST_PARAMETER:9fef3bdca86274f4`: 3 semantic rows
  - `HOST_PARAMETER:2073ea160af32eca`: 3 semantic rows
  - `HOST_PARAMETER:98afff14e93137f3`: 3 semantic rows
  - `HOST_PARAMETER:154567fbd2ee664c`: 3 semantic rows
  - `HOST_PARAMETER:2399d5fdd08ba09a`: 3 semantic rows

## Two-path design validated: target-link promotion

- 3 semantic rows that Phase D's semantic-only classification left as `UNKNOWN_EXECUTION` were resolved once joined to a technical target (target evidence overriding the weaker semantic-only classification, exactly as the frozen two-path rule specifies):
  - `FX.CONVOLVE.IR_GAIN` -> `FXConvolve.IRGain` -> `HOST_PARAMETER`
  - `FX.DELAY.TIME_L` -> `FXDelay.TimeL` -> `HOST_PARAMETER`
  - `FX.DELAY.TIME_R` -> `FXDelay.TimeR` -> `HOST_PARAMETER`

## Semantic <-> technical target join

- 210/908 semantic rows joined to a technical_target_id
  - 1 via formal, evidence-backed post-freeze reconciliation (STEP_4_1 precedent)
  - 209 via mechanical normalized-string match (this run) -- a reproducible heuristic, NOT the same evidentiary strength as the formal precedent; each carries this provenance explicitly in its record
- 698/908 semantic rows have no technical target join (target-less path, or unmatched -- both legitimate per the frozen architecture: 'some may legitimately have no technical target')

## Generic executor (operation_key) status

- **SCALAR**: VERIFIED_IMPORTABLE: serum2.evidence.mutation_executor_extended.execute_mutation_request_with_authority
- **STATE**: VERIFIED_IMPORTABLE: serum2.evidence.mutation_executor_extended.execute_mutation_request_with_authority
- **COMPOUND**: VERIFIED_IMPORTABLE: serum2.evidence.mutation_executor_extended.execute_mutation_request_with_authority
- **TOPOLOGY**: VERIFIED_IMPORTABLE: serum2.evidence.mutation_executor_extended.execute_mutation_request_with_authority
- **RESOURCE**: VERIFIED_IMPORTABLE: serum2.evidence.mutation_executor_extended.execute_mutation_request_with_authority

**Architectural finding, resolved across this milestone:** a separate, pre-D.1.x `OperationRegistry` (serum2/operations/registry.py) had real, registered compilers for STATE/COMPOUND/RESOURCE/TOPOLOGY operations, but was originally disconnected from the admission-gated authority chain -- `get_registry()` called from nowhere in producer/evidence/compiler, a verified-by-grep bypass risk. All four have since been wired in as backends invoked ONLY from inside `execute_mutation_request_with_authority()` via `ExecutionBinding.resolver_operation_id` (contract-derived, never caller-chosen), each gated by an explicit allowlist of PROVEN operations (not the whole enum/catalog). `get_registry()` remains called from exactly one place in producer/evidence/compiler, re-verified mechanically on every test run, not just asserted once. Two real defects were found and fixed during this audit rather than carried forward: COMPOUND's hard-coded VoiceFilter/kParamFreq destination, and TOPOLOGY's non-functional "*" wildcard bypass path. RESOURCE is scoped to WAVETABLE only -- SAMPLE and MULTISAMPLE remain explicitly unresolved (see below).

## Known limitations of this V2 pass

- The semantic<->target join is majority-mechanical (string-normalized match), not majority-formal-evidence. Every joined row's provenance says which kind it got.
- `binding_status=LIVE_VERIFIED` for HOST_PARAMETER rows means the parameter NAME is confirmed present in the current plugin -- it does NOT mean the mutation has been causally qualified (see CapabilityContract count separately: still only 2 of 908/396).
- BODY_STATE_FIELD/MATRIX_ROUTE/STRUCTURAL_OPERATION/RESOURCE_OPERATION bindings are `NOT_YET_DERIVED` across the board: the 396-target vocabulary's `mutation_path` is UNKNOWN for all targets, so no concrete body-path/route/topology/resource binding exists yet for any of them. This is the concrete next-work item, family by family.
