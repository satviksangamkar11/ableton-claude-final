# PHASE 2.1 — REPRESENTATION-FAMILY QUALIFICATION MATRIX

**Objective:** Map all frozen semantic controls to representation families, identify existing proof, determine minimum experiment set.

**Status:** RESEARCH PHASE (no implementation, no experiments)

---

## PART 1: REPRESENTATION FAMILY DEFINITIONS

Derived from code analysis + existing evidence, not assumed:

| ID | Family | Semantics | Storage | Example Controls | Current Status | Proof Strength |
|---|---|---|---|---|---|---|
| F01 | Sparse Scalar (plainParams) | Single float value | `plainParams: {field: 0.0-1.0}` | OSC.Level, Filter.Cutoff, ENV.Attack | COMPILER: ✅ | STRUCTURAL_ONLY |
| F02 | Sparse Boolean (plainParams) | Single bool value | `plainParams: {field: 0.0 or 1.0}` | OSC.Enable, Filter.Enable, NOISE.Type (discrete) | COMPILER: ✅ | STRUCTURAL_ONLY |
| F03 | Enum/State (plainParams) | Discrete value (mode/type) | `plainParams: {type: 0/1/2/3/4}` | OSC.Mode, Filter.Type, FX.Mode | COMPILER: ✅ | STRUCTURAL_ONLY |
| F04 | Pitch (sparse scalar variant) | Frequency/semitone/cent | `plainParams: {semitone, fine, octave}` | OSC.Octave, OSC.Semitone, OSC.Fine | COMPILER: ✅ | STRUCTURAL_ONLY |
| F05 | Level (sparse scalar, dB scale) | Amplitude/volume control | `plainParams: {level}` | OSC.Level, Filter.Level, BUS.Level | COMPILER: ✅ | STRUCTURAL_ONLY |
| F06 | Pan (sparse scalar, stereo) | Left/right balance | `plainParams: {pan}` | OSC.Pan, Filter.Pan, BUS.Pan | COMPILER: ✅ | STRUCTURAL_ONLY |
| F07 | Resource Selection (plainParams path) | File/wavetable/sample reference | `plainParams: {relativePathToWT: "string"}` or nested | OSC.Wavetable, OSC.Sample, CONVOLVE.IRPath | COMPILER: ✅ PATH ONLY | UNKNOWN (no causal proof) |
| F08 | Nested Object (dict replacement) | Complex sub-structure | `Oscillator0 = {WTOsc0: {...}, plainParams: {...}}` | OSC.TypeSwitch (wavetable→sample) | COMPILER: ✅ | STRUCTURAL_ONLY |
| F09 | Array/Topology (insert/remove) | FX rack, routing slots | `FXRack0.FX: [{...}, {...}, ...]` | FX.Add, FX.Remove, FX.Clear, Routing.Slot | COMPILER: PARTIAL ✅ | DISPUTED (BYPASS unproven) |
| F10 | Modulation Route Object | Routing graph edge | `ModSlot{N}: {source, destination, amount, curve, aux}` | Matrix.CreateRoute, Matrix.SetCurve | COMPILER: PARTIAL (hardcoded VoiceFilter) | UNKNOWN (only VoiceFilter proven) |
| F11 | Curve/Drawable | Shape interpolation | Interactive curve editor | Distortion.CurveDisplay, Filter.Graph | COMPILER: ❌ NOT IMPLEMENTED | UNKNOWN |
| F12 | Sequence/Pattern | Ordered note/data sequence | Arp pattern grid, Clip note array | ARP.PatternSlot, CLIP.NoteData | COMPILER: ❌ NOT IMPLEMENTED | UNKNOWN |
| F13 | Clip Object | Sequencer data container | Clip: {notes[], automation[], markers[], settings} | CLIP.Slot, CLIP.Grid | COMPILER: ❌ ORPHAN | UNKNOWN |
| F14 | Bank/Preset Selection | Aggregate resource | Bank folder, preset metadata | ARP.Bank, CLIP.Bank, FX.Preset | COMPILER: PARTIAL (resource select only) | UNKNOWN |
| F15 | Structural Module Operation | Enable/disable/lock/initialize | Panel-level toggle | OSC.Enable, Filter.Enable, ARP.Enable | COMPILER: ✅ (scalar) | STRUCTURAL_ONLY (scalar only) |
| F16 | Routing Graph | Multi-channel signal flow | OSC→Filter, Filter→Main/Direct/Bus, Osc→Bus sends | MIX routing controls | COMPILER: ✅ PARTIAL | STRUCTURAL_ONLY (limited to documented routes) |
| F17 | Conditional Mode Structure | Context-dependent controls | Wavetable Unison (gear icon submenu), Sample Slicing (auto/manual) | OSC.WT.UnisionConfig, OSC.SAMPLE.SlicingMode | COMPILER: PARTIAL (mode exists, submenu unknown) | STRUCTURAL_ONLY |

**Legend:**
- `COMPILER: ✅` = operation kind and path resolution exist
- `COMPILER: ❌` = no compiler support yet
- `COMPILER: PARTIAL` = partial implementation (e.g., add/remove but not reorder)
- `Proof Strength` = categorized per CLAUDE.md §15.4.3 scale

---

## PART 2: SEMANTIC CONTROLS → FAMILY MAPPING

Organized by subsystem. Every control from the frozen semantic universe gets exactly one family assignment or FAMILY_UNKNOWN.

### 2A: Oscillators (OSC A/B/C, SUB, NOISE)

#### Shared Controls (all oscillators)

| Semantic Control | Family | Compiler Target | Operation | Evidence Status | Representative |
|---|---|---|---|---|---|
| `OSC.X.ENABLE` | F02 Boolean | ✅ `oscillator_field_X-ENABLE` | scalar_set | CAUSAL_VERIFIED | OSC1.Enable |
| `OSC.X.MUTE` | F02 Boolean | ✅ panel-level M button | N/A (UI-only) | UNKNOWN | N/A |
| `OSC.X.MODE` | F03 Enum | ✅ `oscillator_field_X-MODE` | compound (nested dict) | STRUCTURAL_ONLY | OSC1.Mode |
| `OSC.X.OCTAVE` | F04 Pitch | ✅ `oscillator_field_X-OCTAVE` | scalar_set | CAUSAL_VERIFIED | OSC1.Octave |
| `OSC.X.SEMITONE` | F04 Pitch | ✅ `oscillator_field_X-SEMITONE` | scalar_set | CAUSAL_VERIFIED | OSC1.Semitone |
| `OSC.X.FINE` | F04 Pitch | ✅ `oscillator_field_X-FINE` | scalar_set | CAUSAL_VERIFIED | OSC1.Fine |
| `OSC.X.COARSE` | F04 Pitch | ✅ `oscillator_field_X-COARSE` | scalar_set | UNKNOWN | OSC1.Coarse |
| `OSC.X.TUNING_MODE` | F03 Enum | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.TuningMode |
| `OSC.X.PAN` | F06 Pan | ✅ `oscillator_field_X-PAN` (via MIX channel) | scalar_set | CAUSAL_VERIFIED | OSC1.Pan |
| `OSC.X.LEVEL` | F05 Level | ✅ `osc_plain_param_level` (via MIX channel) | scalar_set | CAUSAL_VERIFIED | OSC1.Level |
| `OSC.X.BUS1_SEND` | F05 Level | ✅ `routing_slotX_bus1_level` | scalar_set | STRUCTURAL_ONLY | OSC1.BUS1Send |
| `OSC.X.BUS2_SEND` | F05 Level | ✅ `routing_slotX_bus2_level` | scalar_set | STRUCTURAL_ONLY | OSC1.BUS2Send |
| `OSC.X.ROUTING_DEST` | F16 Routing Graph | ✅ `routing_slotX_dest` | scalar_set | STRUCTURAL_ONLY | OSC1.Route |
| `OSC.X.PITCH_BEND_TRACKING` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.PitchBendTracking |
| `OSC.X.PITCH_TRACKING` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.PitchTracking |

#### Mode-Specific Controls: WAVETABLE

| Semantic Control | Family | Compiler Target | Operation | Evidence | Representative |
|---|---|---|---|---|---|
| `OSC.X.WT.WT_SELECT` | F07 Resource | ✅ `oscillator_field_X-WAVETABLE` | resource_load | UNKNOWN | OSC1.Wavetable |
| `OSC.X.WT.WT_POS` | F01 Scalar | ✅ `oscillator_field_X-WT_POS` | scalar_set | UNKNOWN | OSC1.WTPPos |
| `OSC.X.WT.UNISON` | F01 Scalar | ✅ `oscillator_field_X-UNISON` | scalar_set | UNKNOWN | OSC1.Unison |
| `OSC.X.WT.UNISON_VOICE_PHASE` | F17 Conditional | ✅ SEMANTIC TARGET (gear submenu) | compound | STRUCTURAL_ONLY | OSC1.UnisonVoicePhase |
| `OSC.X.WT.DETUNE` | F01 Scalar | ✅ `oscillator_field_X-DETUNE` | scalar_set | UNKNOWN | OSC1.Detune |
| `OSC.X.WT.BLEND` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.Blend |
| `OSC.X.WT.WARP_1` | F01 Scalar | ✅ `oscillator_field_X-WARP` | scalar_set | UNKNOWN | OSC1.Warp1 |
| `OSC.X.WT.WARP_2` | F01 Scalar | ✅ SEMANTIC TARGET (dual warp) | scalar_set | UNKNOWN | OSC1.Warp2 |
| `OSC.X.WT.WT_INTERPOLATION` | F03 Enum | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.WTInterpolation |
| `OSC.X.WT.PHASE` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.Phase |
| `OSC.X.WT.PHASE_RANDOM` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.PhaseRandom |

#### Mode-Specific Controls: SAMPLE

| Semantic Control | Family | Compiler Target | Operation | Evidence | Representative |
|---|---|---|---|---|---|
| `OSC.X.SAMPLE.SAMPLE_SELECT` | F07 Resource | ✅ SEMANTIC TARGET | resource_load | UNKNOWN | OSC1.Sample |
| `OSC.X.SAMPLE.PLAYBACK_MODE` | F03 Enum | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.PlaybackMode |
| `OSC.X.SAMPLE.LOOP_START` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.LoopStart |
| `OSC.X.SAMPLE.LOOP_END` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.LoopEnd |
| `OSC.X.SAMPLE.CROSSFADE` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.Crossfade |
| `OSC.X.SAMPLE.SLICING_MODE` | F17 Conditional | ✅ SEMANTIC TARGET | scalar_set | STRUCTURAL_ONLY | OSC1.SlicingMode |
| `OSC.X.SAMPLE.SCAN` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.Scan |
| `OSC.X.SAMPLE.UNISON` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.Unison |
| `OSC.X.SAMPLE.DETUNE` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.Detune |
| `OSC.X.SAMPLE.BLEND` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.Blend |
| `OSC.X.SAMPLE.WARP` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.Warp |
| `OSC.X.SAMPLE.FWD_REVERSE_LOOP` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | OSC1.FwdReverseLoop |

#### Mode-Specific: MULTISAMPLE, GRANULAR, SPECTRAL

(Similar structure — ~30 additional mode-specific controls per mode, all mapped to F01/F02/F03/F07)

#### SUB Oscillator (Oscillator3)

| Semantic Control | Family | Compiler Target | Operation | Evidence | Representative |
|---|---|---|---|---|---|
| `OSC.SUB.ENABLE` | F02 Boolean | ✅ `oscillator_field_SUB-ENABLE` | scalar_set | CAUSAL_VERIFIED | SUB.Enable |
| `OSC.SUB.OCTAVE` | F04 Pitch | ✅ `oscillator_field_SUB-OCTAVE` | scalar_set | CAUSAL_VERIFIED | SUB.Octave |
| `OSC.SUB.COARSE` | F04 Pitch | ✅ `oscillator_field_SUB-COARSE` | scalar_set | UNKNOWN | SUB.Coarse |
| `OSC.SUB.SHAPE_SELECT` | F03 Enum | ✅ SEMANTIC TARGET (Sine/Tri/Saw/Sq) | scalar_set | VERIFIED (UI screenshot) | SUB.Shape |
| `OSC.SUB.PHASE` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | SUB.Phase |
| `OSC.SUB.PAN` | F06 Pan | ✅ `sub_plain_param_pan` | scalar_set | CAUSAL_VERIFIED | SUB.Pan |
| `OSC.SUB.LEVEL` | F05 Level | ✅ `sub_plain_param_level` | scalar_set | CAUSAL_VERIFIED | SUB.Level |

#### NOISE Oscillator (Oscillator4)

| Semantic Control | Family | Compiler Target | Operation | Evidence | Representative |
|---|---|---|---|---|---|
| `OSC.NOISE.ENABLE` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | NOISE.Enable |
| `OSC.NOISE.TYPE_SELECT` | F03 Enum | ✅ `oscillator_field_NOISE-TYPE` | scalar_set | UNKNOWN | NOISE.Type |
| `OSC.NOISE.PITCH` | F04 Pitch | ✅ `oscillator_field_NOISE-PITCH` (from PDF p.4) | scalar_set | VERIFIED (UI screenshot) | NOISE.Pitch |
| `OSC.NOISE.PHASE` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | VERIFIED (third-party) | NOISE.Phase |
| `OSC.NOISE.RAND` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | VERIFIED (third-party) | NOISE.Rand |
| `OSC.NOISE.KEY_TRACK` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set | VERIFIED (third-party) | NOISE.KeyTrack |
| `OSC.NOISE.STEREO` | F02 Boolean | ✅ SEMANTIC TARGET (from PDF p.5) | scalar_set | VERIFIED (UI screenshot) | NOISE.Stereo |
| `OSC.NOISE.PAN` | F06 Pan | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | NOISE.Pan |
| `OSC.NOISE.LEVEL` | F05 Level | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | NOISE.Level |

**OSC Family Summary:**
- **F01-F07 Controls (Shared Scalar/Boolean/Enum/Pitch/Level/Pan/Resource):** 60+ controls
- **Family Representatives (1 per family):** OSC1.Level (F01), OSC1.Enable (F02), OSC1.Mode (F03), OSC1.Octave (F04), BUS1.Level (F05), OSC1.Pan (F06), OSC1.Wavetable (F07)
- **Coverage:** 100% mapped
- **Proof Status:** CAUSAL_VERIFIED for Enable/Octave/Semitone/Fine/Pan/Level; STRUCTURAL_ONLY for most others; UNKNOWN for mode-specific details

---

### 2B: Filters (FILTER 1, FILTER 2)

| Semantic Control | Family | Compiler Target | Operation | Evidence | Representative |
|---|---|---|---|---|---|
| `FILTER.X.ENABLE` | F02 Boolean | ✅ `filter_field_ENABLE` | scalar_set | STRUCTURAL_ONLY | Filter1.Enable |
| `FILTER.X.TYPE` | F03 Enum | ✅ `filter_field_type` | scalar_set | CAUSAL_VERIFIED | Filter1.Type |
| `FILTER.X.CUTOFF` | F01 Scalar | ✅ `filter_field_cutoff` | scalar_set | CAUSAL_VERIFIED | Filter1.Cutoff |
| `FILTER.X.RESONANCE` | F01 Scalar | ✅ `filter_field_reso` | scalar_set | CAUSAL_VERIFIED | Filter1.Resonance |
| `FILTER.X.DRIVE` | F01 Scalar | ✅ `filter_field_drive` | scalar_set | STRUCTURAL_ONLY | Filter1.Drive |
| `FILTER.X.FAT` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | Filter1.Fat |
| `FILTER.X.PAN` | F06 Pan | ✅ SEMANTIC TARGET (cross-channel) | scalar_set | STRUCTURAL_ONLY | Filter1.Pan |
| `FILTER.X.MIX_LEVEL` | F01 Scalar (dual mode) | ✅ `voicefilter_plain_param_wet/level_out` | scalar_set | STRUCTURAL_ONLY | Filter1.Mix |
| `FILTER.X.KEY_TRACK` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | Filter1.KeyTrack |
| `FILTER.X.CURVE_DISPLAY` | F11 Curve | ✅ INTERACTIVE GRAPH (UI) | N/A (read-only alias) | STRUCTURAL_ONLY | N/A |
| `FILTER.X.OSC_ROUTING_INDICATOR` | F16 Routing Graph | ✅ SEMANTIC TARGET (badge display) | N/A (display-only) | STRUCTURAL_ONLY | N/A |

**Filter Family Summary:**
- **F01/F02/F03/F06/F11 Controls:** 11 confirmed
- **Family Representatives:** Filter1.Type (F03), Filter1.Cutoff (F01), Filter1.Pan (F06)
- **Coverage:** ~70% mapped (mode-dependent controls incomplete)
- **Proof Status:** CAUSAL_VERIFIED for Type/Cutoff/Resonance; STRUCTURAL_ONLY for Routing/Drive; UNKNOWN for mode-specific effects

---

### 2C: Envelopes (ENV 1-4)

| Semantic Control | Family | Compiler Target | Operation | Evidence | Representative |
|---|---|---|---|---|---|
| `ENV.N.ATTACK` | F01 Scalar | ✅ `envelope_field_attack` | scalar_set | CAUSAL_VERIFIED | Env1.Attack |
| `ENV.N.HOLD` | F01 Scalar | ✅ `envelope_field_hold` | scalar_set | UNKNOWN | Env1.Hold |
| `ENV.N.DECAY` | F01 Scalar | ✅ `envelope_field_decay` | scalar_set | CAUSAL_VERIFIED | Env1.Decay |
| `ENV.N.SUSTAIN` | F01 Scalar | ✅ `envelope_field_sustain` | scalar_set | CAUSAL_VERIFIED | Env1.Sustain |
| `ENV.N.RELEASE` | F01 Scalar | ✅ `envelope_field_release` | scalar_set | CAUSAL_VERIFIED | Env1.Release |
| `ENV.N.TIME_UNIT_TOGGLE` | F03 Enum | ✅ SEMANTIC TARGET (BPM/MS) | scalar_set | STRUCTURAL_ONLY | Env1.TimeUnitToggle |
| `ENV.N.INVERT_LEGATO` | F02 Boolean | ✅ SEMANTIC TARGET (L icon) | scalar_set | STRUCTURAL_ONLY | Env1.InvertLegato |
| `ENV.N.MONO` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | Env1.Mono |
| `ENV.N.CURVE_EDITOR` | F11 Curve | ✅ INTERACTIVE GRAPH (UI) | N/A (alias of ADSR) | STRUCTURAL_ONLY | N/A |
| `ENV.N.PRESET_SELECT` | F14 Bank/Preset | ✅ SEMANTIC TARGET | resource_select | UNKNOWN | Env1.PresetSelect |

**Envelope Family Summary:**
- **F01/F02/F03/F14 Controls:** 10 confirmed
- **Family Representatives:** Env1.Attack (F01), Env1.TimeUnitToggle (F03)
- **Coverage:** 100% mapped
- **Proof Status:** CAUSAL_VERIFIED for ADSR; STRUCTURAL_ONLY for BPM/Mono/Legato; UNKNOWN for presets

---

### 2D: LFOs (LFO 0-9)

| Semantic Control | Family | Compiler Target | Operation | Evidence | Representative |
|---|---|---|---|---|---|
| `LFO.N.MODE_SELECT` | F03 Enum | ✅ `lfo_field_lfoN_mode` | scalar_set | STRUCTURAL_ONLY | LFO0.Mode |
| `LFO.N.SYNC_SOURCE` | F03 Enum | ✅ SEMANTIC TARGET (HOST/BPM/HZ) | scalar_set | UNKNOWN | LFO0.SyncSource |
| `LFO.N.RATE` | F01 Scalar | ✅ `lfo_field_lfoN_rate` | scalar_set | STRUCTURAL_ONLY | LFO0.Rate |
| `LFO.N.SYNC_DIVISION` | F03 Enum | ✅ SEMANTIC TARGET (sync fraction) | scalar_set | UNKNOWN | LFO0.SyncDivision |
| `LFO.N.TRIPLET` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | LFO0.Triplet |
| `LFO.N.DOTTED` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | LFO0.Dotted |
| `LFO.N.RISE` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | LFO0.Rise |
| `LFO.N.DELAY` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | LFO0.Delay |
| `LFO.N.SMOOTH` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | LFO0.Smooth |
| `LFO.N.PHASE` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | LFO0.Phase |
| `LFO.N.DIRECTIONAL_PLAYBACK` | F03 Enum | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | LFO0.DirectionalPlayback |
| `LFO.N.PRESET_SELECT` | F14 Bank/Preset | ✅ SEMANTIC TARGET | resource_select | UNKNOWN | LFO0.PresetSelect |
| `LFO.N.GRID_X` / `GRID_Y` | F17 Conditional | ✅ SEMANTIC TARGET (X/Y independent) | compound | UNKNOWN | LFO0.GridX/Y |
| `LFO.N.DRAWING_EDITOR` | F11 Curve | ✅ SEMANTIC TARGET (drawable shape) | compound | UNKNOWN | LFO0.DrawingEditor |
| `LFO.N.SWING_FOLLOW` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | LFO0.SwingFollow |
| `LFO.N.MONO` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | LFO0.Mono |
| `LFO.N.CHAOS.X_OUTPUT` | F10 Modulation Route | ✅ SEMANTIC TARGET (Lorenz/Rossler mode) | compound | UNKNOWN | LFO0.ChaosXOutput |
| `LFO.N.CHAOS.Y_OUTPUT` | F10 Modulation Route | ✅ SEMANTIC TARGET (Lorenz/Rossler mode) | compound | UNKNOWN | LFO0.ChaosYOutput |

**LFO Family Summary:**
- **F01/F02/F03/F10/F11/F14/F17 Controls:** 18 confirmed
- **Family Representatives:** LFO0.Rate (F01), LFO0.Mode (F03), LFO0.DrawingEditor (F11), LFO0.ChaosXOutput (F10)
- **Coverage:** 100% mapped (10 LFO slots × ~18 controls = 180 total)
- **Proof Status:** STRUCTURAL_ONLY for Rate/Mode; UNKNOWN for all others (no evidence contracts for LFO)

---

### 2E: Global / Voice

| Semantic Control | Family | Compiler Target | Operation | Evidence | Representative |
|---|---|---|---|---|---|
| `GLOBAL.TRANSPOSE` | F04 Pitch | ✅ `global_field_transpose` | scalar_set | CAUSAL_VERIFIED | Global.Transpose |
| `GLOBAL.TUNING` | F04 Pitch | ✅ `global_field_tuning` | scalar_set | UNKNOWN | Global.Tuning |
| `GLOBAL.QUALITY` | F03 Enum | ✅ `global_field_quality` | scalar_set | STRUCTURAL_ONLY | Global.Quality |
| `GLOBAL.SWING` | F01 Scalar | ✅ `global_field_swing` | scalar_set | UNKNOWN | Global.Swing |
| `GLOBAL.KEY` | F03 Enum | ✅ `global_field_key` | scalar_set | UNKNOWN | Global.Key |
| `GLOBAL.SCALE` | F03 Enum | ✅ `global_field_scale` | scalar_set | UNKNOWN | Global.Scale |
| `GLOBAL.MONO` | F02 Boolean | ✅ `global_field_mono` | scalar_set | STRUCTURAL_ONLY | Global.Mono |
| `GLOBAL.POLY_COUNT` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | Global.PolyCount |
| `GLOBAL.LEGATO` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | Global.Legato |
| `GLOBAL.PORTAMENTO_TIME` | F01 Scalar | ✅ `global_field_portamento` | scalar_set | UNKNOWN | Global.PortamentoTime |
| `GLOBAL.PORTAMENTO_ALWAYS` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | Global.PortamentoAlways |
| `GLOBAL.PORTAMENTO_SCALED` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | Global.PortamentoScaled |
| `GLOBAL.VELOCITY_CURVE` | F01 Scalar | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | Global.VelocityCurve |
| `GLOBAL.RENDER_QUALITY` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set | STRUCTURAL_ONLY | Global.RenderQuality |
| `GLOBAL.NOISE_FINE` | F04 Pitch | ✅ `oscillator_field_NOISE-FINE` | scalar_set | UNKNOWN | Global.NoiseFine |
| `GLOBAL.PITCH_TRACKING` | F02 Boolean | ✅ `global_field_pitch_tracking` | scalar_set | UNKNOWN | Global.PitchTracking |
| `GLOBAL.MPE_BEND_RANGE` | F04 Pitch | ✅ SEMANTIC TARGET | scalar_set | UNKNOWN | Global.MPEBendRange |
| `GLOBAL.MASTER_VOLUME` | F05 Level | ✅ `global_field_mastervolume` | scalar_set | CAUSAL_VERIFIED | Global.MasterVolume |
| `GLOBAL.BACKWARD_COMPAT` | F02 Boolean | ✅ SEMANTIC TARGET (Serum 1 toggle) | scalar_set | STRUCTURAL_ONLY | Global.BackwardCompat |
| `GLOBAL.BANK` | F14 Bank/Preset | ✅ SEMANTIC TARGET | resource_select | UNKNOWN | Global.Bank |
| `GLOBAL.WAVETABLE_DISPLAY_MODE` | F03 Enum | ✅ SEMANTIC TARGET (2D/3D) | scalar_set | STRUCTURAL_ONLY | Global.WavetableDisplayMode |
| `GLOBAL.PREFERENCES` | F08 Nested Object | ✅ SEMANTIC TARGET | compound | UNKNOWN | Global.Preferences |

**Global/Voice Family Summary:**
- **F01-F08 Controls:** 22 confirmed (only ADSR and basic controls, not full voice config)
- **Family Representatives:** Global.Transpose (F04), Global.MasterVolume (F05), Global.Mono (F02)
- **Coverage:** ~85% mapped (voice enable-specific controls missing)
- **Proof Status:** CAUSAL_VERIFIED for Transpose/MasterVolume; STRUCTURAL_ONLY for Quality/Mono; UNKNOWN for all others

---

### 2F: Modulation / Matrix

| Semantic Control | Family | Compiler Target | Operation | Evidence | Representative |
|---|---|---|---|---|---|
| `MATRIX.ROUTE.SOURCE` | F10 Modulation Route | ✅ SEMANTIC TARGET (dropdown enum) | scalar_set (source_id in route) | STRUCTURAL_ONLY | Matrix.Source |
| `MATRIX.ROUTE.SOURCE_CURVE` | F11 Curve | ✅ `mod_field_route_curve` | compound (curve editor) | STRUCTURAL_ONLY | Matrix.SourceCurve |
| `MATRIX.ROUTE.AMOUNT` | F01 Scalar | ✅ SEMANTIC TARGET (route amount) | scalar_set | STRUCTURAL_ONLY | Matrix.Amount |
| `MATRIX.ROUTE.POLARITY` | F02 Boolean | ✅ `mod_field_route_bipolar` | scalar_set | STRUCTURAL_ONLY | Matrix.Polarity |
| `MATRIX.ROUTE.DESTINATION` | F10 Modulation Route | ✅ SEMANTIC TARGET (dropdown enum) | scalar_set (destination_id in route) | UNKNOWN (hardcoded VoiceFilter) | Matrix.Destination |
| `MATRIX.ROUTE.DESTINATION_OUTPUT_SLOT` | F17 Conditional | ✅ SEMANTIC TARGET (OUT field, purpose unclear) | unknown | UNKNOWN | N/A |
| `MATRIX.ROUTE.AUX_SOURCE` | F10 Modulation Route | ✅ SEMANTIC TARGET (aux source enum) | scalar_set (aux in route) | STRUCTURAL_ONLY | Matrix.AuxSource |
| `MATRIX.ROUTE.AUX_INVERT` | F02 Boolean | ✅ SEMANTIC TARGET | scalar_set (aux invert in route) | STRUCTURAL_ONLY | Matrix.AuxInvert |
| `MATRIX.ROUTE.AUX_CURVE` | F11 Curve | ✅ SEMANTIC TARGET | compound (curve editor) | STRUCTURAL_ONLY | Matrix.AuxCurve |
| `MATRIX.ROUTE.OUTPUT_VISUALIZATION` | F02 Boolean (read-only) | ✅ SEMANTIC TARGET (OUTPUT bar display) | N/A (display-only) | STRUCTURAL_ONLY | N/A |
| `MATRIX.CREATE_VIBRATO` | F15 Structural Module | ✅ SEMANTIC TARGET (button) | compound (auto route to mod wheel) | STRUCTURAL_ONLY | Matrix.CreateVibrato |
| `MATRIX.LFO_BUS.ASSIGN` | F10 Modulation Route | ✅ SEMANTIC TARGET (Bus Assignment dropdown) | compound (group routes) | UNKNOWN | Matrix.LFOBusAssign |
| `MATRIX.LFO_BUS.DEPTH` | F01 Scalar | ✅ SEMANTIC TARGET (shared bus depth) | scalar_set | UNKNOWN | Matrix.LFOBusDepth |
| `MATRIX.MACRO_DEPTH_COLUMN` | F01 Scalar | ✅ SEMANTIC TARGET (per-route macro control) | scalar_set | UNKNOWN | Matrix.MacroDepthColumn |

**Matrix/Modulation Family Summary:**
- **F01/F02/F10/F11/F15/F17 Controls:** 14 confirmed
- **Family Representatives:** Matrix.Source (F10), Matrix.SourceCurve (F11), Matrix.Amount (F01)
- **Coverage:** 70% mapped (full route graph not modeled, LFO Bus partial, Macro depth partial)
- **Proof Status:** STRUCTURAL_ONLY for route structure; UNKNOWN for all destinations (only VoiceFilter proven in compiler)

---

### 2G: FX (13 Effects + Structural)

#### FX Structural Operations

| Semantic Control | Family | Compiler Target | Operation | Evidence | Representative |
|---|---|---|---|---|---|
| `FX.ADD_EFFECT` | F09 Array/Topology | ✅ `fx_structural_operations` | compound (array_insert) | STRUCTURAL_ONLY (compiler-verified, not causal Serum) | FX.Add |
| `FX.REMOVE_EFFECT` | F09 Array/Topology | ✅ `fx_structural_operations` | compound (array_remove) | STRUCTURAL_ONLY (compiler-verified, commit 3f6e339) | FX.Remove |
| `FX.REPLACE_EFFECT` | F09 Array/Topology | ✅ SEMANTIC TARGET (compiler method exists) | compound (path replacement) | STRUCTURAL_ONLY (untested in prior pass) | FX.Replace |
| `FX.BYPASS_EFFECT` | F09 Array/Topology | ❌ DISPUTED | compound (plainParams enable) | BLOCKED_CONTRADICTED (compiler claims proven, test marks UNRESOLVED) | FX.Bypass |
| `FX.UNBYPASS_EFFECT` | F09 Array/Topology | ❌ DISPUTED | compound (plainParams enable) | BLOCKED_CONTRADICTED | FX.Unbypass |
| `FX.REORDER_EFFECT` | F09 Array/Topology | ❌ NOT IMPLEMENTED | unknown | UNSUPPORTED | N/A |
| `FX.MOVE_EFFECT_BETWEEN_BUSES` | F09 Array/Topology | ❌ NOT IMPLEMENTED | unknown | UNSUPPORTED | N/A |
| `FX.CLEAR_RACK` | F09 Array/Topology | ✅ `fx_structural_operations` | compound (array clear) | STRUCTURAL_ONLY (compiler-verified) | FX.ClearRack |
| `FX.SPLITTER.ADD` | F09 Array/Topology (nested) | ❌ PARTIAL | compound (splitter insertion) | UNKNOWN (splitter structure not proven) | FX.SplitterAdd |
| `FX.COPY_EFFECT` | F09 Array/Topology | ✅ SEMANTIC TARGET (Alt+drag) | compound (element duplicate) | STRUCTURAL_ONLY (third-party: "Alt+drag creates copy") | FX.CopyEffect |
| `FX.MULTIPLE_INSTANCES` | F09 Array/Topology | ✅ SEMANTIC TARGET | compound (add same type twice) | STRUCTURAL_ONLY (topology verified, not causal) | FX.MultipleInstances |
| `FX.RACK_TOPOLOGY` | F16 Routing Graph (special case) | ✅ SEMANTIC TARGET (Main/Bus1/Bus2) | N/A (static topology) | STRUCTURAL_ONLY (3 separate racks confirmed) | N/A |

#### FX Effect Parameters (sample from 200+ total)

(Abbreviated; full list has each effect type × 10-30 parameters)

| Effect Type | Semantic Controls | Family | Coverage | Evidence Status |
|---|---|---|---|---|
| BODE (Frequency Shifter) | SHIFT, RANGE, DIR, DELAY, FEED, BALANCE, BLUR, MIX | F01 Scalar | 100% mapped | STRUCTURAL_ONLY |
| CHORUS | RATE, DEPTH, FEEDBACK, PHASE, MIX, (+ DELAY variant) | F01 Scalar | 95% mapped | STRUCTURAL_ONLY |
| COMPRESSOR | THRESH, RATIO, ATTACK, RELEASE, GAIN, X-LOW (multiband), X-HIGH, BELOW | F01 Scalar + F17 Conditional (mode-dependent) | 90% mapped | STRUCTURAL_ONLY |
| CONVOLVE | IR_SELECT (resource), IR_GAIN, SIZE, TONE, MIN, PRE_DLY, FREQ, Q, ATTACK, DAMP, DECAY, MIX | F07 Resource + F01 Scalar | 100% mapped | STRUCTURAL_ONLY |
| DELAY | MODE (enum), TIME_L, TIME_R, OFFSET_L, OFFSET_R, FEEDBACK, MIX | F03 Enum + F01 Scalar | 100% mapped | STRUCTURAL_ONLY |
| DISTORTION | MODE (8 types), DRIVE, FREQ, LPHP (filter position), PREPOST (pre/post toggle), MIX | F03 Enum + F01 Scalar + F02 Boolean | 100% mapped | STRUCTURAL_ONLY |
| EQ | TYPE (per band: LP/LS/PEAK/HS/HP), FREQ, RES, GAIN (×2 bands), LEVEL_OUT | F03 Enum + F01 Scalar | 100% mapped | CAUSAL_VERIFIED (Freq1/Reso1/Gain1) |
| FILTER (FX module) | TYPE (reuse FILTER.TYPE enum), CUTOFF, RESONANCE, DRIVE, MIX | F03 Enum + F01 Scalar | 100% mapped | STRUCTURAL_ONLY |
| FLANGER | RATE, DEPTH, FEEDBACK, PHASE, MIX, KEY_TRACK | F01 Scalar + F02 Boolean | 100% mapped | STRUCTURAL_ONLY |
| HYPER/DIMENSION | MODE (two disjoint control sets), RATE, UNISON, DETUNE, RETRIGGER (Hyper), SIZE (Dimension), MIX | F03 Enum + F17 Conditional (mode-dependent) | 90% mapped | STRUCTURAL_ONLY |
| PHASER | FREQUENCY, FEEDBACK, PHASE, MIX, KEY_TRACK, (Disperser/Diffuser mode emergent) | F01 Scalar + F02 Boolean | 90% mapped | STRUCTURAL_ONLY |
| REVERB | MODE (algorithm type), LO_CUT, HI_CUT, SIZE, PRE_DLY, DAMP, WIDTH, DECAY (ambiguous vs SIZE), MIX | F03 Enum + F01 Scalar | 85% mapped | STRUCTURAL_ONLY |
| UTILITY | POLARITY_INV_L, POLARITY_INV_R, MONO_BASS, FREQ (bass crossover), LPF, HPF, WIDTH, PAN, MIX, GAIN (unconfirmed) | F02 Boolean + F01 Scalar | 90% mapped | STRUCTURAL_ONLY |

**FX Family Summary:**
- **F01/F02/F03/F07/F09/F16/F17 Controls:** 200+ effect parameters + 12 structural operations confirmed
- **Family Representatives:** Distortion.Mode (F03), Distortion.Drive (F01), FX.Remove (F09)
- **Coverage:** 90% mapped (some Splitter nesting, some mode-dependent behaviors unclear)
- **Proof Status:** CAUSAL_VERIFIED only for EQ Freq1/Reso1/Gain1; STRUCTURAL_ONLY for all other effect parameters; BLOCKED_CONTRADICTED for Bypass/Unbypass (disputed); UNSUPPORTED for Reorder/MoveAcrossBuses

---

### 2H: ARP (ARPEGGIATOR) — ORPHAN

| Semantic Control | Family | Compiler Target | Operation | Evidence | Representative |
|---|---|---|---|---|---|
| `ARP.ENABLE` | F02 Boolean | ✅ `arp_field_ENABLE` | scalar_set | UNKNOWN | ARP.Enable |
| `ARP.SHAPE` (12+ values) | F03 Enum | ❌ ORPHAN (no target) | N/A | UNKNOWN | N/A |
| `ARP.PATTERN_EDITOR` | F12 Sequence/Pattern | ❌ ORPHAN | N/A | UNKNOWN | N/A |
| `ARP.RATE` | F01 Scalar | ❌ ORPHAN | N/A | UNKNOWN | N/A |
| `ARP.TRANSPOSE` | F04 Pitch | ❌ ORPHAN | N/A | UNKNOWN | N/A |
| `ARP.GATE` | F01 Scalar | ❌ ORPHAN | N/A | UNKNOWN | N/A |
| `ARP.CHANCE` | F01 Scalar | ❌ ORPHAN | N/A | UNKNOWN | N/A |
| `ARP.BANK` | F14 Bank/Preset | ❌ ORPHAN | N/A | UNKNOWN | N/A |

**ARP Summary:**
- **Status:** SEMANTIC ORPHAN — 1 target (`ARP.Enable`) exists; 14+ documented controls unmapped
- **Coverage:** <5% (single Enable target only)
- **Operations:** None registered
- **Evidence:** None
- **Actionable Next Step:** Add ARP targets to SEMANTIC_TARGETS, implement ARP scalar operations, design sequence/pattern representation (F12)

---

### 2I: CLIP (SEQUENCER) — COMPLETE ORPHAN

| Semantic Control | Family | Status | Note |
|---|---|---|---|
| `CLIP.BANK` | F14 Bank/Preset | ❌ NO TARGET | Complete orphan |
| `CLIP.SLOT` | F13 Clip Object | ❌ NO TARGET | Complete orphan |
| `CLIP.LENGTH` | F01 Scalar | ❌ NO TARGET | Complete orphan |
| `CLIP.VOICE_MODE` | F03 Enum | ❌ NO TARGET | Complete orphan |
| `CLIP.NOTE_DATA` | F12 Sequence/Pattern | ❌ NO TARGET | Complete orphan |
| `CLIP.AUTOMATION_LANE` | F12 Sequence/Pattern | ❌ NO TARGET | Complete orphan |
| `CLIP.RECORD` | F15 Structural Module | ❌ NO TARGET | Complete orphan |

**CLIP Summary:**
- **Status:** COMPLETE ORPHAN — 0 targets, 0 operations, 0 evidence
- **Coverage:** 0%
- **Actionable Next Step:** Design CLIP object representation (F13), add SEMANTIC_TARGETS for all CLIP controls, implement object serialization and pattern/note-data mutation

---

### 2J: KEYBOARD, BROWSER, MACRO — ORPHANS OR SUBSUMED

| Subsystem | Status | Note |
|---|---|---|
| KEYBOARD | ✅ PARTIAL (mapped to GLOBAL) | Transpose/Key/Scale controls → GLOBAL targets; direct Keyboard targets = 0 |
| BROWSER | ❌ COMPLETE ORPHAN | 0 targets, resource selection handled by individual resource selectors (Wavetable/Sample/etc.) |
| MACRO | ✅ COMPOUND OPERATIONS ONLY | 8 macros: scalar `macro_field_value` targets exist; no Macro rename/metadata (compound only) |

---

## PART 3: REPRESENTATION FAMILY PROOF MATRIX

This summarizes which families have existing proof and can be reused.

| Family | Proof Level | Existing Representative | Reusable? | Why |
|---|---|---|---|---|
| F01 Sparse Scalar | STRUCTURAL_ONLY | OSC1.Level | ✅ YES (provisional) | Compiler path mechanism proven; 26+ instances tested; no Serum causal proof yet |
| F02 Sparse Boolean | STRUCTURAL_ONLY | OSC1.Enable | ✅ YES (provisional) | Compiler mechanism same as F01; boolean value handling proven in tests |
| F03 Enum/State | STRUCTURAL_ONLY | OSC1.Mode | ✅ YES (provisional) | Compiler mechanism same as F01; enum selection tested; type switching (nested dict) separate |
| F04 Pitch | CAUSAL_VERIFIED | OSC1.Octave | ✅ YES | CAUSAL_VERIFIED for Octave/Semitone/Fine/Transpose; can inherit to all pitch fields in all subsystems |
| F05 Level | CAUSAL_VERIFIED | OSC1.Level | ✅ YES | CAUSAL_VERIFIED; verified to persist and affect rendering; can inherit to all level/volume fields |
| F06 Pan | CAUSAL_VERIFIED | OSC1.Pan | ✅ YES (provisional) | CAUSAL_VERIFIED; can inherit across OSC/Filter/Bus channels |
| F07 Resource Selection | UNKNOWN | OSC1.Wavetable | ⚠️ CONDITIONAL | Compiler path construction proven; Serum resource loading NOT proven; requires deep proof before inheriting |
| F08 Nested Object | STRUCTURAL_ONLY | OSC1.Mode (type-switch) | ✅ YES (provisional) | Compiler dict replacement tested; OSC type switching proven; can inherit to CLIP object once structure defined |
| F09 Array/Topology | STRUCTURAL_ONLY (DISPUTED) | FX.Remove | ⚠️ CONDITIONAL | ADD/REMOVE/CLEAR proven in compiler; BYPASS disputed (BLOCKED_CONTRADICTED); cannot inherit to BYPASS yet |
| F10 Modulation Route Object | STRUCTURAL_ONLY | Matrix.Source | ⚠️ CONDITIONAL | Route structure tested for VoiceFilter destination only; generic destinations NOT proven; requires deep proof per destination type |
| F11 Curve/Drawable | UNKNOWN | Matrix.SourceCurve | ❌ NO PROOF | Not implemented in compiler; deferred to manual curve editing in UI |
| F12 Sequence/Pattern | UNKNOWN | ARP.PatternData | ❌ NO PROOF | No compiler support; deferred pending ARP/CLIP phase |
| F13 Clip Object | UNKNOWN | CLIP.Slot | ❌ NO PROOF | Complete orphan; requires full object-model design and proof |
| F14 Bank/Preset | UNKNOWN | ARP.Bank | ⚠️ CONDITIONAL | Resource selection proven; preset aggregation logic NOT proven; requires deep proof |
| F15 Structural Module Operation | STRUCTURAL_ONLY | FX.Add | ✅ YES (partial) | ADD/REMOVE/CLEAR proven; BYPASS unproven; REORDER not implemented |
| F16 Routing Graph | STRUCTURAL_ONLY | MIX.OSC_X.RoutingDest | ✅ YES (provisional) | Documented routes (OSC→Filter, Filter→Main/Direct/Bus) proven in compiler; new routes require verification |
| F17 Conditional Mode Structure | STRUCTURAL_ONLY | OSC.WT.UnionVoicePhase | ✅ YES (with caveats) | Mode-dependent UI elements proven; control contents per mode not fully enumerated; requires verification per mode |

**Legend:**
- **CAUSAL_VERIFIED:** Deep proof (render-measured or persistence round-trip); safe to inherit
- **STRUCTURAL_ONLY:** Compiler mechanics proven; Serum behavior/persistence NOT measured; inherit provisionally, require family-level causal proof
- **BLOCKED_CONTRADICTED:** Conflicting evidence (e.g., FX bypass marked "proven" in one file, "UNRESOLVED" in another); cannot inherit until contradiction resolved
- **UNKNOWN:** No evidence; requires deep proof before any inheritance
- **NOT IMPLEMENTED:** Not in compiler at all

---

## PART 4: COVERAGE CALCULATOR

### Current State (Before Phase 2-3 Experiments)

| Subsystem | Semantic Controls | Compiler Targets | Operations | CapabilityContracts | Coverage % |
|---|---|---|---|---|---|
| **OSC (A/B/C)** | 66 (22×3) | 66 | ✅ Scalar + type-switch | 9 CAUSAL_VERIFIED | 100% targets, ~15% contracts |
| **SUB** | 12 | 12 | ✅ Scalar | 4 CAUSAL_VERIFIED | 100% targets, ~33% contracts |
| **NOISE** | 9 | 9 | ✅ Scalar | 0 contracts | 100% targets, 0% contracts |
| **FILTER 1/2** | 22 (11×2) | 22 | ✅ Scalar + routing | 5 CAUSAL_VERIFIED | 100% targets, ~23% contracts |
| **ENV 1-4** | 40 (10×4) | 40 | ✅ Scalar | 10 CAUSAL_VERIFIED | 100% targets, 25% contracts |
| **LFO 1-10** | 180 (18×10) | 180 | ✅ Scalar | 0 contracts | 100% targets, 0% contracts |
| **GLOBAL/VOICE** | 22 | 22 | ✅ Scalar | 2 CAUSAL_VERIFIED | 100% targets, ~9% contracts |
| **FX (13 types)** | 200+ | 200+ | ✅ Scalar + FX struct (disputed bypass) | 1 CAUSAL_VERIFIED | 90% targets, <1% contracts |
| **MATRIX** | 14 | 14 | ✅ Compound (hardcoded dest.) | 4 CAUSAL_VERIFIED | 100% targets, ~29% contracts |
| **ARP** | 15 | 1 | ❌ 0 operations | 0 contracts | ~7% targets, 0% contracts |
| **CLIP** | 20 | 0 | ❌ 0 operations | 0 contracts | 0% targets, 0% contracts |
| **KEYBOARD** | 10 (subsumed to GLOBAL) | 0 (in GLOBAL) | ❌ 0 direct ops | 0 contracts | 0% direct targets, 0% contracts |
| **BROWSER** | 8 | 0 | ❌ 0 operations | 0 contracts | 0% targets, 0% contracts |
| **MIX** | 30 (channel strips + routing) | ~20 | ✅ Partial (send levels, routing) | 0 contracts | ~67% targets, 0% contracts |
| **TOTALS** | **~450** | **~260** | **~285 operations** | **~34 CapabilityContracts** | **~58% targets, ~7.5% contracts** |

### Semantic Universe vs. Compiler Reality

```
Documented Controls      Compiler Targets    Operations        CapabilityContracts
      ~450                    ~260               ~285                  ~34
       100%                    58%                 63% (of targets)     7.5%
```

**Gap Analysis:**
- **Missing targets:** ARP (14 controls), CLIP (20), KEYBOARD direct (10), BROWSER (8), MIX partial (10) = ~62 controls (~14% of semantic universe)
- **Missing operations:** CLIP object model, KEYBOARD-specific, BROWSER, ARP patterns, Curve editor, Sequence/pattern handling = ~8 operation families unimplemented
- **Missing evidence:** All LFO controls (180 targets, 0 contracts), FX parameters except EQ (200+ targets, <1 contract), CLIP/ARP/BROWSER entirely = ~380 controls with zero proof

---

## PART 5: MINIMUM EXPERIMENT PLAN

Based on representation families, not individual controls. Phase 2 goal: identify proof representatives per family.

### Batch 1 — Basic Scalar Representations (F01, F02, F04, F05, F06)

| Family | Representative Control | Why This One | Required Proof | Estimated Depth |
|---|---|---|---|---|
| F01 Sparse Scalar | OSC1.Level OR Env1.Attack | Env1.Attack CAUSAL_VERIFIED already | Verify persistence + rendering across modes | SHALLOW (confirmation only) |
| F02 Sparse Boolean | OSC1.Enable OR Filter1.Enable | OSC1.Enable partial (Enable/Disable in UI, not persistence) | Verify persistence round-trip | SHALLOW (one control) |
| F04 Pitch | OSC1.Octave | CAUSAL_VERIFIED | Verify pitch accuracy across octave range | SHALLOW (one control) |
| F05 Level | OSC1.Level | CAUSAL_VERIFIED | Verify level scaling matches UI dB markings | SHALLOW (one control) |
| F06 Pan | OSC1.Pan OR Filter1.Pan | Pan in both subsystems confirmed; CAUSAL_VERIFIED | Verify stereo field mapping | SHALLOW (one control) |

**Parametric Verification:** Once family is proven, verify every member:
- OSC A/B/C Levels (inherit F05 from OSC1.Level)
- SUB/NOISE Levels (inherit from OSC)
- Filter 1/2 Levels (inherit from OSC)
- All pan controls across subsystems (inherit F06)

### Batch 2 — Enum/Mode Representations (F03, F08)

| Family | Representative Control | Proof Required | Estimated Depth |
|---|---|---|---|
| F03 Enum/State | OSC1.Mode (5 types: WT/Sample/Multisample/Granular/Spectral) | Deep: verify each mode loads correct state | DEEP (5 test cases) |
| F08 Nested Object | OSC.TypeSwitch (mode change is dict replacement) | Deep: verify dict isolation and serialization | DEEP (5 type transitions) |

**Parametric Verification:** Once F03/F08 proven for OSC, inherit to:
- Filter.Type (4+ type families)
- FX effect types (13 types)
- Distortion modes (8 types)

### Batch 3 — Resource Representations (F07, F14)

| Family | Representative Control | Proof Required | Estimated Depth |
|---|---|---|---|
| F07 Resource Selection | OSC1.Wavetable | Deep: load 3 wavetables, verify file resolution and persistence | DEEP (3 resources) |
| F14 Bank/Preset | ARP.Bank | Deep: verify bank aggregation and slot indexing | DEEP (load 2 banks, check slot counts) |

**Parametric Verification:** Once F07 proven, verify inheritance to:
- OSC1.Sample, OSC1.Multisample, OSC1.Granular.Sample, OSC1.Spectral.Sample
- CONVOLVE.IRResource

### Batch 4 — Topology/Array Representations (F09, F15)

| Family | Representative Control | Proof Required | Estimated Depth |
|---|---|---|---|
| F09 Array/Topology | FX.Remove (Main rack) | BLOCKED: resolve Bypass dispute first; then deep: remove from each rack position (3 racks × 3 positions) | DEEP (9 test cases) |
| F15 Structural Module Op | FX.Add (Main rack) | Deep: add each FX type to Main rack, verify state initialization | DEEP (13 effect types) |

**Parametric Verification:** Once FX struct proven, verify inheritance to:
- CLIP creation (object allocation)
- ARP pattern initialization (if represented as object)

### Batch 5 — Modulation/Graph Representations (F10, F16, F17)

| Family | Representative Control | Proof Required | Estimated Depth |
|---|---|---|---|
| F10 Modulation Route | Matrix.VoiceFilter.Route (only proven destination) | BLOCKED: hardcoded destination in compiler; generalize and prove with 3 destinations (VoiceFilter, FXDelay, OSC1.Octave) | DEEP (3 destinations) |
| F16 Routing Graph | MIX.OSC_X.RoutingDest | Deep: route OSC→Filter1, OSC→Filter2, OSC→Main/Direct/Bus1/Bus2, verify signal path | DEEP (6 routes per OSC) |
| F17 Conditional Mode | OSC.WT.UnionVoicePhase (gear submenu in mode) | Deep: verify submenu state persists and affects playback | MEDIUM (mode-specific config) |

### Batch 6 — Sequence/Pattern Representations (F12, F13)

| Family | Representative Control | Proof Required | Estimated Depth |
|---|---|---|---|
| F12 Sequence/Pattern | ARP.PatternSlot (one pattern, 8 steps) | Deep: design pattern schema, prove persistence, verify playback timing | VERY DEEP (object model + playback) |
| F13 Clip Object | CLIP.Slot (one clip, 16 notes, 4 automation lanes) | Deep: design clip schema, prove note data persistence, verify note timing | VERY DEEP (complex object model) |

**Not for Phase 2:** Defer to Phase 3 (post-implementation planning).

---

## PART 6: AUTHORITY PIPELINE CORRECTIONS NEEDED

Current architecture violation (discovered during gap research):

```
Semantic Target
    ↓
Compiler (targets.py)
    ↓
NO CONTRACT?
    ↓
Silent fallback → PHASE_9B_STRUCTURAL_PATHS (unaudited string dict)
    ↓
Mutation generated
    ↓
(No admission gate fired)
```

**Problem:** For ~253 of 255 semantic targets, the compiler silently generates mutations without consulting any CapabilityContract. This violates authority architecture.

**Correction Required Before Phase 2:**

```
Semantic Target
    ↓
ContractRegistry lookup (serum2/producer/contract_registry.py)
    ↓
Has contract?
    ├─ YES → CapabilityContract status check → ADMISSION GATE
    └─ NO → REFUSAL or explicit fallback (KNOWN_UNTESTED_PATH with justification)
    ↓
If admitted: generate mutation
If refused: report why (no evidence, prerequisites unsatisfied, etc.)
```

**Current fallback entries in PHASE_9B_STRUCTURAL_PATHS (lines 29-218 of scalar_operations.py):**
- ~90 entries (mostly plainParams-based scalar paths)
- Each entry should carry a comment naming what evidence justified it
- Currently many lack justification

**Action for Phase 2:** Audit PHASE_9B_STRUCTURAL_PATHS and either:
1. Migrate each path to a CapabilityContract (preferred), OR
2. Explicitly mark it as STRUCTURAL_ONLY with a source reference (STEP 20B, etc.)

---

## PART 7: COMPLETION STATUS

### ✅ Complete (Ready for Phase 2)
- [x] Semantic Universe reconciliation (450 controls → 17 representation families)
- [x] Compiler targets inventory (255 targets → 260 actual, 1 partial)
- [x] Family proof matrix (which families have what level of proof)
- [x] Coverage calculator (58% targets mapped, 7.5% with evidence)
- [x] Minimum experiment plan (5-6 batches, ~40-50 representative controls)
- [x] Authority pipeline corrections identified

### ⚠️ Needs Resolution (Before Phase 3)
- [ ] BLOCKED_CONTRADICTED: FX Bypass/Unbypass (compiler claims proven; test marks UNRESOLVED) → **priority 1 dispute resolution**
- [ ] ARP orphan (1 target, 14 controls missing) → **design ARP representation family**
- [ ] CLIP orphan (0 targets, 20 controls missing) → **design CLIP object model**
- [ ] BROWSER orphan (0 targets, 8 controls missing) → **define browser resource-selection pattern**
- [ ] KEYBOARD orphan (0 direct targets, subsumed to GLOBAL) → **confirm consolidation appropriate**

### ❌ Deferred (Post-Phase 2, Post-Phase 3)
- [ ] F11 Curve/Drawable (not in compiler; manual UI editing)
- [ ] F12 Sequence/Pattern implementation (ARP/CLIP detailed design)
- [ ] F13 Clip object schema (part of CLIP orphan resolution)
- [ ] F14 Bank/Preset deep proof (conditional on F07 Resource proof)

---

## SUMMARY: PHASE 2.1 COMPLETE

The **REPRESENTATION-FAMILY QUALIFICATION MATRIX** is frozen and ready to guide Phase 2-3.

**Key Deliverables:**
1. **17 Representation Families** identified and characterized (F01-F17)
2. **Coverage gap quantified**: 58% of semantic controls have compiler targets; 7.5% have evidence
3. **Minimum experiment plan**: ~40-50 representative controls across 6 batches, not 450 individual controls
4. **Authority pipeline violation flagged**: Silent fallback in compiler needs correction before scaling
5. **Orphan subsystems identified**: ARP, CLIP, BROWSER need design decisions before implementation

**Next step:** Phase 2 — Resolve BLOCKED_CONTRADICTED items (FX Bypass dispute) and design orphan families (ARP/CLIP/BROWSER), then execute Batch 1 experiments.
