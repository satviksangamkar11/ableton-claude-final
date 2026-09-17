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
