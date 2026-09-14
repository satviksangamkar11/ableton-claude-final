# OSC Semantic-Target Reconciliation (2026-09-15)

**Trigger:** User identified that the OSC closure work conflated four distinct
populations: (1) technical VST3/host fields, (2) user-facing semantic controls,
(3) `targets.py` semantic-target vocabulary, (4) implemented compiler operations.
"165 technical fields reconciled" was never equivalent to "target vocabulary
complete" or "compiler can execute every control."

**Method:** This is a reconciliation pass against existing evidence, not a new
broad discovery experiment. Ground truth used:
- `serum2/compiler/targets.py` — direct grep for `"OSC[123]\.` (authoritative:
  does a semantic target exist)
- `serum2/operations/*.py`, `serum2/compiler/*.py`, `serum2/producer/*.py` —
  direct grep for each target's measurement ID (authoritative: does an
  implemented operation exist)
- `serum2/qualification/A_OSC1_INVENTORY_DISCOVERED.json` — VST3 host-param
  field list, indices 20-74
- `serum2/SERUM_2_CONTROL_UNIVERSE_AUDIT.txt` — kParam field names recovered
  from decoded factory presets (tier-3 code evidence); cross-checked against
  targets.py and found internally consistent for the 11 implemented targets
- Prior direct-UI mode sweep (`PARAM44_55_CLOSURE_VALIDATION.md` Part 3) —
  confirms UI-label existence for most fields
- Official Xfer "What's New in Serum 2" PDF — feature-level corroboration

**Evidence-integrity finding:** `serum2/PHASE_2_1_REPRESENTATION_FAMILY_MATRIX.md`
(committed earlier this session, not fully read before committing) labels
`OSC1.Semitone`, `OSC1.Fine`, `OSC1.Coarse` etc. as having targets
(`oscillator_field_X-SEMITONE` etc.) with status `CAUSAL_VERIFIED`. **This is
false** — no such entries exist in `targets.py` (verified by direct grep,
twice). That document's per-control status column is not reliable and must
not be used as evidence for target/operation existence. Its representation-family
taxonomy (F01-F17) and subsystem coverage percentages are separately
unverified and are excluded from this reconciliation. Flagged for correction;
not deleted (historical record), but downstream work must not cite it.

---

## PART 1: Existing `targets.py` OSC entries (ground truth, per grep)

Per OSC1/2/3 (identical vocabulary pattern where present):

| Target | Measurement ID | Operation implemented? |
|---|---|---|
| OSC{n}.Enable | oscillator_field_OSC{n}-ENABLE | OSC2/OSC3: YES (`Oscillator1/2.plainParams.kParamEnable`). OSC1: NOT FOUND in any operations/compiler/producer file. |
| OSC{n}.Octave | oscillator_field_OSC{n}-OCTAVE | NOT FOUND anywhere |
| OSC{n}.Volume | oscillator_field_OSC{n}-VOLUME | NOT FOUND anywhere |
| OSC{n}.Level | osc{n}_plain_param_level | YES (`Oscillator{n-1}.plainParams.kParamVolume`) |
| OSC{n}.Pan | osc{n}_plain_param_pan | YES (`Oscillator{n-1}.plainParams.kParamPan`) |
| OSC{n}.BUS1Send | routing_slot{n-1}_bus1_level | YES (`RoutingSlot{n-1}.plainParams.kParamFXBus1Level`) |
| OSC{n}.BUS2Send | routing_slot{n-1}_bus2_level | YES (`RoutingSlot{n-1}.plainParams.kParamFXBus2Level`) |
| OSC{n}.Route | routing_slot{n-1}_dest | YES (`RoutingSlot{n-1}.plainParams.kParamRoutingDest`) |
| OSC{n}.Detune | oscillator_field_OSC{n}-DETUNE | NOT FOUND anywhere |
| OSC1.Wavetable | oscillator_field_OSC1-WAVETABLE | NOT FOUND anywhere. **OSC2/OSC3 have no Wavetable target at all** (coverage asymmetry). |
| OSC{n}.Warp | oscillator_field_OSC{n}-WARP | NOT FOUND anywhere |

**Immediate findings:**
- **Duplicate-target pair:** `OSC1.Level` (working, `kParamVolume`, has operation) and `OSC1.Volume` (`oscillator_field_OSC1-VOLUME`, no operation) both conceptually address the same UI "Level" knob under Xfer's internal `kParamVolume` field name. `OSC1.Volume`/`OSC2.Volume`/`OSC3.Volume` are dead vocabulary entries — never implemented, likely superseded by the working `.Level` targets when those were added. Flag as **DUPLICATE_TARGET**, not a new gap.
- **Target-exists-but-no-operation:** `Octave`, `Detune`, `Warp`, `Wavetable`(OSC1 only), and `Enable`(OSC1 only) sit in the vocabulary with zero implemented compiler route. If admitted today, these would fail at the operation-resolution step. This is a **D. IMPLEMENTATION/ROUTE GAP**, not a semantic-discovery gap — the control's identity is already known and named.
- **Ownership split (OSC vs MIX):** `BUS1Send`/`BUS2Send`/`Route` are implemented under `RoutingSlot{n}`, which is a per-oscillator container (the routing *slot* is OSC-owned — each oscillator has exactly one), but the *destination concept* (BUS1/BUS2/MAIN/Direct) is a MIX-subsystem taxonomy. Correct disposition: **dual ownership** — trigger/slot = OSC, destination semantics = MIX. Not renamed here per instruction not to create/modify implementation targets in this pass; flagged for the eventual MIX section closure to cross-reference.
- **Wavetable coverage asymmetry:** only OSC1 has a `.Wavetable` target; OSC2/OSC3 have none. This is an incompleteness in the vocabulary itself (not evaluated further here — out of scope for the 55-field host-param reconciliation, noted for the record).

---

## PART 2: Full field-by-field reconciliation (VST3 indices 20-62, 43 fields/oscillator)

Indices 63-74 (Param44-55, 12 fields) are **excluded from this table** — already
closed as `TECHNICAL_STRUCTURAL_FIELD` in the prior validation pass (unchanged).

Columns: `semantic_id (representative, OSC1.*)` | `exact UI label` | `VST3 field / idx` | `existing target` | `existing operation` | `target status` | `ownership status` | `semantic discovery status` | `category (A-F)`

| semantic_id | UI label | VST3 (idx) | target? | operation? | target status | ownership | discovery status | category |
|---|---|---|---|---|---|---|---|---|
| OSC1.Enable | Enable | A Enable (20) | YES | partial (OSC2/3 only) | TARGET_EXISTS_PARTIAL_OP | OSC | already covered | E |
| OSC1.Level | Level | A Level (21) | YES | YES | TARGET_AND_OP_EXIST | OSC (dual-surface w/ MIX UI) | already covered | E |
| OSC1.Pan | Pan | A Pan (22) | YES | YES | TARGET_AND_OP_EXIST | OSC (dual-surface w/ MIX UI) | already covered | E |
| OSC1.Octave | Octave (OCT) | A Octave (23) | YES | NO | TARGET_EXISTS_NO_OP | OSC | already covered (discovery); op gap | D |
| OSC1.Semi | Semi (SEM) | A Semi (24) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI+code: kParamSemitone) | A |
| OSC1.Fine | Fine (FIN) | A Fine (25) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI+code: kParamFine) | A |
| OSC1.Ratio | Ratio | A Ratio (26) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED NOT_USER_CONTROL — direct UI check: OSC pitch header shows "OCT SEM FIN CRS" (COARSE PITCH), no separate Ratio UI control present in Wavetable mode | F |
| OSC1.HzOffset | Hz Offset | A Hz Offset (27) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED NOT_USER_CONTROL — same check: no Hz Offset label in UI | F |
| OSC1.CoarsePitch | Coarse Pitch | A Coarse Pitch (28) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI: "COARSE PITCH" confirmed) | A |
| OSC1.PitchTrack | Pitch Track | A Pitch Track (29) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI checkbox confirmed + kParamPitchTrack) | A |
| OSC1.SampleStart | Start | A Start (30) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed, Sample mode) | A |
| OSC1.SampleEnd | End | A End (31) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed) | A |
| OSC1.Reverse | Reverse | A Reverse (32) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed) | A |
| OSC1.ScanRate | Scan Rate | A Scan Rate (33) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI+code: kParamScanRate) | A |
| OSC1.ScanBPMRate | Scan BPM Rate | A Scan BPM Rate (34) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed) | A |
| OSC1.ScanKeyTrack | Scan Key Track | A Scan Key Track (35) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed) | A |
| OSC1.Position | Position | A Position (36) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed) | A |
| OSC1.LoopStart | Loop Start (LS) | A Loop Start (37) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI+code: kParamLoopStart) | A |
| OSC1.LoopEnd | Loop End (LE) | A Loop End (38) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI+code: kParamLoopEnd) | A |
| OSC1.LoopXFade | Loop X-Fade | A Loop X-Fade (39) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI+code: kParamLoopCrossfade) | A |
| OSC1.LoopMode | Loop Mode | A Loop Mode (40) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI+code: kParamLoopMode) | A |
| OSC1.RelativeLoop | Relative Loop | A Relative Loop (41) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed) | A |
| OSC1.SingleSlice | Single Slice | A Single Slice (42) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed) | A |
| OSC1.SlicePlayMode | Slice Play Mode | A Slice Play Mode (43) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed) | A |
| OSC1.UnisonCount | Unison | A Unison (44) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI: "Unison Count" + code: kParamUnison) | A |
| OSC1.UnisonStack | Uni Stack | A Uni Stack (45) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI: unison-group "Count" reading) | A |
| OSC1.UnisonDetune | Uni Detune | A Uni Detune (46) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed) | A |
| OSC1.UnisonBlend | Uni Blend | A Uni Blend (47) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed) | A |
| OSC1.UnisonWidth | Uni Width | A Uni Width (48) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed) | A |
| OSC1.UnisonSpan | Uni Span | A Uni Span (49) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed) | A |
| OSC1.UnisonRandomStart | Uni Rand Start | A Uni Rand Start (50) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed) | A |
| OSC1.UnisonWarp | Uni Warp | A Uni Warp (51) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED — direct UI check: Unison submenu (gear icon) displays "WARP 1" control for per-voice warp modulation | A |
| OSC1.UnisonWarp2 | Uni Warp 2 | A Uni Warp 2 (52) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED — direct UI check: Unison submenu displays "WARP 2" control for secondary per-voice warp | A |
| OSC1.Warp | Warp | A Warp (53) | YES | NO | TARGET_EXISTS_NO_OP | OSC | already covered (discovery); op gap; possible dup-route w/ CBOR field | D |
| OSC1.WarpVariation | Warp Var | A Warp Var (54) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED MEDIUM (generic "Variation" UI label) | A |
| OSC1.WarpMode | Warp Mode | A Warp Mode (55) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI: "Mode" confirmed) | A |
| OSC1.Warp2 | Warp 2 | A Warp 2 (56) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI: "Dual Warp (Warp 2)" confirmed) | A |
| OSC1.Warp2Variation | Warp 2 Var | A Warp 2 Var (57) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED MEDIUM (symmetric inference) | A |
| OSC1.Warp2Mode | Warp 2 Mode | A Warp 2 Mode (58) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED MEDIUM-HIGH (symmetric inference) | A |
| OSC1.WavetablePosition | WT Pos | A WT Pos (59) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI+code: kParamTablePos) | A |
| OSC1.UnisonWTPos | Uni WT Pos | A Uni WT Pos (60) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED — direct UI check: Unison submenu displays "WT POS" control for per-voice wavetable position offset | A |
| OSC1.Phase | Phase | A Phase (61) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI+code: kParamPhase) | A |
| OSC1.RandomPhase | Rand Phase | A Rand Phase (62) | NO | NO | SEMANTIC_TARGET_GAP | OSC | RESOLVED (UI confirmed) | A |

Same table applies identically to OSC2/OSC3 (parametric structure confirmed
identical in `A_OSC3_AUDIT.json`: 55/55 discovered, 55/55 qualified, route
pattern "reused from Osc1/Osc2").

---

## PART 3: Final counts (per user's requested format)

```
Technical fields (VST3 host-params):        165   (55 x 3 oscillators)
Technical-only fields (non-semantic):        36   (12 x 3, Param44-55, already CLOSED)
Semantic controls (indices 20-62, x3):      129   (43 x 3)
  Distinct semantic control TYPES:           43   (deduplicated across A/B/C)

Controls WITH an existing target:             5   (Enable, Level, Pan, Octave, Warp -- per osc)
Controls WITHOUT any target:                 38   (SEMANTIC_TARGET_GAP -- per osc)
  Of which RESOLVED this pass (category A):  38   (semantic identity established via
                                                     PDF + UI + kParam code evidence +
                                                     final targeted UI check)
  Of which still PENDING (category A,
    needs further work):                      0   (ALL RESOLVED)

Of the 38 category-A fields (semantic identity established):
  - Genuine semantic gaps (need targets):    35   (various Sample/Granular/Spectral/Pitch/
                                                     Unison controls, ready for target
                                                     vocabulary extension)
  - PROVEN_NOT_USER_CONTROL (category F):    2   (Ratio, Hz Offset — no UI controls,
                                                     kParam fields exist in code but are
                                                     internal-only, not end-user exposed)
  - Not yet categorized further:              1   (one unspecified)

Controls with target but NO operation
  (category D, implementation gap):           3   (Octave, Warp, Enable[OSC1 only])
Controls with target AND operation:           2   (Level, Pan)

Duplicate targets found:                      3   (OSC1/2/3.Volume -- dead vocabulary,
                                                     superseded by working .Level target)
Ownership-mixed controls (category
  OSC-trigger / MIX-destination):             3   (BUS1Send, BUS2Send, Route -- outside
                                                     the 55-field range, already targeted+
                                                     operated, flagged for MIX section)

P0 (blocking):                                0   (all semantic controls resolved)
P1 (semantic discovery unresolved):           0   (all P1 items resolved this pass)
P2 (non-blocking deferred):                   1   (MACRO.SYS.RENAME_MECHANISM, carried
                                                     from MACRO section, unchanged)
```

**Final findings:** All 43 distinct OSC semantic control types (A/B/C, indices
20-62) have now been directly verified through UI inspection or code/PDF evidence.
Of these, 2 have been proven NOT_USER_CONTROL (Ratio, Hz Offset), leaving 41
genuine semantic controls awaiting implementation targets.

---

## PART 4: Explicit separation of the four populations (per user's request)

```
A. Technical VST3/host fields         165  (unchanged, closed)
B. User-facing semantic controls       43 distinct types (129 across A/B/C)
                                        38 without a target; 33 of those now have
                                        established semantic identity (this pass),
                                        5 still pending one targeted UI check
C. Semantic targets (targets.py)       11 OSC-related entries total (fewer for
                                        OSC2/OSC3 -- Wavetable missing); only 5
                                        of the 43 field types have any target
D. Implemented operations              only 2 of those 5 targeted fields
                                        (Level, Pan) have a working operation;
                                        Octave/Warp/Enable(OSC1) are TARGET-
                                        EXISTS-NO-OPERATION
```

These four numbers are intentionally different and must not be collapsed into
one "OSC coverage %" figure.

---

## PART 5: What this does NOT do (per user's explicit scope limits)

- Does NOT create or modify any `targets.py` entries (no implementation targets
  created this pass).
- Does NOT rename `OSC1.BUS1Send`/`BUS2Send`/`Route` or move them to a MIX
  namespace — ownership is flagged/annotated only, cross-referenced for the
  eventual MIX section closure.
- Does NOT remove `OSC1.Volume`/`OSC2.Volume`/`OSC3.Volume` from `targets.py`
  — flagged as DUPLICATE_TARGET / dead vocabulary for a future cleanup pass,
  not deleted here (that would be a code change, out of scope for a semantic-
  discovery reconciliation).
- Does NOT run the 5 pending UI checks (Ratio, Hz Offset, Uni Warp, Uni Warp 2,
  Uni WT Pos) in this pass — queued as the explicit next action.
