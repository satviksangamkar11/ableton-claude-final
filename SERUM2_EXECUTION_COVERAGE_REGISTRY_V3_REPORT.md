# SERUM2_EXECUTION_COVERAGE_REGISTRY_V3 -- Population Pass Report

First substep of Execution Coverage Population, using the now-complete authority substrate (SCALAR/STATE/COMPOUND/TOPOLOGY/RESOURCE all authority-integrated).

**Invariant preserved:** RESOLVED != BOUND != EXECUTABLE != CAUSAL_VERIFIED != ADMITTED. This pass only advances rows from RESOLVED to BOUND (a real, evidence-backed CapabilityBinding). No qualification or admission work is claimed here.

## Scope of this pass

FX_PARAMETER targets (96 total in the 396-vocabulary), restricted to exact 1:1 normalized semantic<->target matches with a real, resolvable fx_resolver.py catalog entry AND an independently confirmed FX-type-key (see CONFIRMED_SAFE_EFFECTS).

- Candidates found: 20
- Bound this pass: 11
- Skipped: 9

## Key correction made this pass (evidence-backed)

The frozen 396-target vocabulary tags all 96 FX_PARAMETER targets as `parameter_kind=VST3_HOST_FIELD`. Checked directly against the live VST3 parameter list this session (2623 params): **no host parameter exists** for any of the 14 bound here (e.g. no "EQ Freq1", no "Distortion Drive" -- only "Filter 1/2 Drive", a different capability, the main VoiceFilter). The real mechanism is CBOR body state via the already authority-integrated `fx_set_parameter` resolver, cross-validated against real preset structures captured earlier this session. This coverage registry (a derived layer) corrects the family for these rows; the frozen `SERUM2_TARGET_NORMALIZED_V4.json` file itself is untouched.

## Bound this pass

- `FX.DISTORTION.DRIVE` -> `FXDistortion.Drive`: HOST_PARAMETER -> **BODY_STATE_FIELD** (capability_id=`BODY_STATE_FIELD:547a37c850ddef93`)
- `FX.DELAY.FEEDBACK` -> `FXDelay.Feedback`: HOST_PARAMETER -> **BODY_STATE_FIELD** (capability_id=`BODY_STATE_FIELD:138832e026306362`)
- `FX.COMPRESSOR.RATIO` -> `FXCompressor.Ratio`: HOST_PARAMETER -> **BODY_STATE_FIELD** (capability_id=`BODY_STATE_FIELD:4c504a186066eecd`)
- `FX.COMPRESSOR.ATTACK` -> `FXCompressor.Attack`: HOST_PARAMETER -> **BODY_STATE_FIELD** (capability_id=`BODY_STATE_FIELD:d1bf409b5e1ccf89`)
- `FX.COMPRESSOR.RELEASE` -> `FXCompressor.Release`: HOST_PARAMETER -> **BODY_STATE_FIELD** (capability_id=`BODY_STATE_FIELD:31b72dcf1070760a`)
- `FX.BODE.RANGE` -> `FXBODE.Range`: HOST_PARAMETER -> **BODY_STATE_FIELD** (capability_id=`BODY_STATE_FIELD:b5b30851fbae302a`)
- `FX.PHASER.FEEDBACK` -> `FXPhaser.Feedback`: HOST_PARAMETER -> **BODY_STATE_FIELD** (capability_id=`BODY_STATE_FIELD:9b70443c187b54a9`)
- `FX.PHASER.PHASE` -> `FXPhaser.Phase`: HOST_PARAMETER -> **BODY_STATE_FIELD** (capability_id=`BODY_STATE_FIELD:91067f82eb1a2f45`)
- `FX.HYPER.RATE` -> `FXHyper.Rate`: HOST_PARAMETER -> **BODY_STATE_FIELD** (capability_id=`BODY_STATE_FIELD:2b6a054baecbd0dd`)
- `FX.HYPER.UNISON` -> `FXHyper.Unison`: HOST_PARAMETER -> **BODY_STATE_FIELD** (capability_id=`BODY_STATE_FIELD:56be42b535780777`)
- `FX.HYPER.DETUNE` -> `FXHyper.Detune`: HOST_PARAMETER -> **BODY_STATE_FIELD** (capability_id=`BODY_STATE_FIELD:01e16d4bc51b9d8c`)

## UI Truth Gate (V3 Pass 2 -- post-BOUND verification, all 11 rows)

**Invariant preserved:** BOUND != CAUSAL_VERIFIED != UI_VERIFIED. UI_VERIFIED is a *stronger* evidence tier than anything else in this file: not a code-level CBOR/path/pathmerge check, but a real Serum GUI running inside Ableton, mutated through the same authority path (`execute_mutation_request_with_authority`), and inspected visually via Serum's own "Double-click params: TYPE VALUE" numeric readout. Protocol per capability: read BEFORE in the live UI -> authority mutation -> read UI_AFTER in the live UI -> save via Serum's own "Save Preset As..." -> load a different preset (state-disruption step) -> reload the test preset -> read RELOADED_UI in the live UI. A row is UI_VERIFIED only if UI_AFTER and RELOADED_UI both equal the requested value.

All 11 BOUND rows above were run through this protocol this session.

| Capability | BEFORE | REQUESTED | UI_AFTER | RELOADED_UI | STATUS |
|---|---|---|---|---|---|
| FX.DISTORTION.DRIVE | 25 | 75.0 | 75 | 75 | UI_VERIFIED |
| FX.DELAY.FEEDBACK | 40 | 50.0 | 50 | 50 | UI_VERIFIED |
| FX.COMPRESSOR.RATIO | 4.0 | 5.5 | 5.5 | 5.5 | UI_VERIFIED |
| FX.COMPRESSOR.ATTACK | 90.1 | 50.0 | 50.0 | 50.0 | UI_VERIFIED |
| FX.COMPRESSOR.RELEASE | 90.1 | 500.0 | 500.0 | 500.0 | UI_VERIFIED |
| FX.BODE.RANGE | 22 | 50.0 | 50 | 50 | UI_VERIFIED |
| FX.PHASER.FEEDBACK | 80 | 0.0 | 0 | 0 | UI_VERIFIED |
| FX.PHASER.PHASE | 180 | 90.0 | 90 | 90 | UI_VERIFIED (see finding below) |
| FX.HYPER.RATE | 4.0 | 9.0 | 9.0 | 9.0 | UI_VERIFIED |
| FX.HYPER.UNISON | 4 | 7 | 7 | 7 | UI_VERIFIED |
| FX.HYPER.DETUNE | 25 | 75.0 | 75 | 75 | UI_VERIFIED |

**Result: 11/11 UI_VERIFIED, 0 mismatches.**

### Finding: FX.PHASER.PHASE resolver defect caught and fixed by the UI Truth Gate

The gate first caught a real defect: mutating `FXPhaser.plainParams.kParamPhase` (the original binding) round-tripped correctly at the CBOR/code level -- the exact same class of false-positive already known for Convolve -- but the real Serum "PHASE" knob never moved (BEFORE=180, requested 90 then 350, UI_AFTER=180 both times). This is invisible to every check in this file above the UI Truth Gate, because the mechanism check only proves the byte round-trips through `codec`/`pathmerge`, not that Serum's real DSP reads that key.

Forensic root-cause (per the exact protocol: manual UI edit -> Serum's own save -> diff): with the real Phaser module loaded, the Phase knob was set to 90 by hand in Serum (not through any authority code path), saved with Serum's own "Save Preset As...", and the resulting `.SerumPreset` was diffed against the prior state. Result: `kParamPhase` was **not present at all** in Serum's own output (silently dropped -- Serum ignores unrecognized `plainParams` keys rather than erroring), and `kParamWidth=90.0` was present instead. The UI label "Phase" and the real persisted field `kParamWidth` do not match -- a legacy internal naming mismatch.

`fx_resolver.py`'s `("Phaser", "Phase")` catalog entry now points at `kParamWidth` (see resolver source comment for the evidence trail). Re-run through the full authority-mutation path with the fix in place: UI_AFTER=90, RELOADED_UI=90, matching requested. A permanent regression guard (`test_phaser_phase_real_roundtrip_and_kparamphase_regression_guard` in `serum2/evidence/test_v3_fx_parameter_real_roundtrip.py`) proves both directions against real Serum: `kParamWidth` round-trips, and `kParamPhase` (the old binding) still silently does not.

**Why `capability_id` did not change:** `FX.PHASER.PHASE`'s `capability_id` (`BODY_STATE_FIELD:91067f82eb1a2f45`) is unchanged by this fix and was NOT regenerated with a new value. Per the frozen canonicalization rule (`serum2/coverage/canonicalize.py::canonicalize_fx_parameter`), an FX_PARAMETER capability's identity is `(effect, parameter)` only -- e.g. "the capability to control Phaser's Phase" -- deliberately excluding the underlying state-path/field-name, exactly as rack/slot index is excluded. The actual `kParamWidth` vs `kParamPhase` field name is resolver *mechanism*, resolved dynamically at request time by `fx_resolver.py`, not part of what identifies the capability. The registry was re-run through `serum2_execution_coverage_registry_v3_builder.py` this session and produced a byte-identical `SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json`/`.md` -- confirming the fix is correctly scoped to the mechanism layer and required no registry-identity change.

## Skipped (with reason)

- `FX.CHORUS.RATE`: effect 'Chorus' FX-type-key not confirmed against real Serum output (no matching preset evidence found this session) -- refusing to bind on an unverified key
- `FX.CHORUS.DEPTH`: effect 'Chorus' FX-type-key not confirmed against real Serum output (no matching preset evidence found this session) -- refusing to bind on an unverified key
- `FX.FLANGER.RATE`: effect 'Flanger' FX-type-key not confirmed against real Serum output (no matching preset evidence found this session) -- refusing to bind on an unverified key
- `FX.FLANGER.DEPTH`: effect 'Flanger' FX-type-key not confirmed against real Serum output (no matching preset evidence found this session) -- refusing to bind on an unverified key
- `FX.FLANGER.FEEDBACK`: effect 'Flanger' FX-type-key not confirmed against real Serum output (no matching preset evidence found this session) -- refusing to bind on an unverified key
- `FX.FLANGER.PHASE`: effect 'Flanger' FX-type-key not confirmed against real Serum output (no matching preset evidence found this session) -- refusing to bind on an unverified key
- `FX.CONVOLVE.IR_GAIN`: effect 'Convolve' FX-type-key not confirmed against real Serum output (no matching preset evidence found this session) -- refusing to bind on an unverified key
- `FX.CONVOLVE.ATTACK`: effect 'Convolve' FX-type-key not confirmed against real Serum output (no matching preset evidence found this session) -- refusing to bind on an unverified key
- `FX.CONVOLVE.DECAY`: effect 'Convolve' FX-type-key not confirmed against real Serum output (no matching preset evidence found this session) -- refusing to bind on an unverified key

## Deferred to follow-up substeps (explicitly NOT attempted this pass)

- **6 FX_PARAMETER targets matched but excluded**: Chorus (2: Rate, Depth) and Flanger (4: Rate, Depth, Feedback, Phase) resolve in fx_resolver.py's catalog and have an exact semantic match, but their FX-type-key (FXChorus, FXFlanger) is unconfirmed against real Serum output -- no preset evidence found this session. Binding them would repeat the exact mistake just caught for Compressor/Convolve/Hyper/Bode. Needs a real preset containing a loaded Chorus or Flanger module before these can be safely bound.
- **~76 more FX_PARAMETER targets** with no exact 1:1 semantic_id normalized match at all (e.g. `FXEQ.Freq1` has no `FX.EQ.FREQ1`-shaped semantic row -- the actual semantic naming for EQ uses `FX.EQUALIZER.LEFT_FREQ`/`RIGHT_FREQ`, a genuinely different convention requiring evidence-based reconciliation, not a mechanical string match) or no fx_resolver.py catalog entry at all under exact parameter-name match (e.g. "Mix" vs "Wet") -- needs per-parameter evidence check, not guessed.
- **MATRIX_ROUTE family** (106 rows): a3_modulation_route.py has real source/destination tables; semantic<->route population not attempted this pass.
- **RESOURCE_OPERATION family** (41 rows) beyond WAVETABLE: unresolved.
- **STRUCTURAL_OPERATION family** (10 rows): fx_structural_operations.py's proven operations are rack/bus-level, not naturally per-semantic-row bindings; disposition not yet determined.
- **HOST_PARAMETER family remainder**: rows with no technical_target_id join at all cannot be live-verified without expanding the semantic<->target join beyond the existing mechanical string match.
