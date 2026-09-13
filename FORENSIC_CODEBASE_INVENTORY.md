# COMPLETE FORENSIC CODEBASE INVENTORY
## D:\ableton claude — Serum 2.0.21 AI Producer System
**Date: 2026-09-13 | Branch: step-4-q-authority-audit | Status: Read-only inventory, no modifications**

---

## 1. EXECUTIVE SUMMARY

This codebase is an **epistemically rigorous Serum 2.0.21 synthesis control system** built on measured evidence and strict admission gates. However, it contains **critical evidence-fabrication violations** that undermine integrity claims, alongside a massive **capability deployment gap** between design architecture and actual admitted control.

### State of the Codebase

**Single Git Repository:**
- 757 tracked files, 82 untracked
- 550 Python files, 262 JSON (mostly evidence/experiments), 78 Markdown docs, 8 text docs
- Current branch: `step-4-q-authority-audit` (HEAD: `b44fd49`, "Execute final recreation")
- 263MB experiments folder (evidence/audit results), 20MB serum2/ core, 19MB archive (VST3 binary + presets), 3.2MB producer-recreation (untracked parallel copy)

### Projects Identified

1. **serum2/** — established, tracked, primary Serum control core
   - Compiler (semantic targets, admission, context resolution)
   - Evidence/Claims/Contracts system (strict rule enforcement)
   - DawDreamer harness (real Serum/VST3 execution, verified)
   - Producer brain (feedback loops, route selection)
   - Knowledge ingestion (YouTube transcripts)
   - Behavioral measurement kernels
   - Qualification pipeline

2. **producer-recreation/** — untracked, appears newer, but is mostly a **byte-identical duplicate** of serum2/ plus a thin new ingestion layer
   - NOT independent; imports from serum2 to function
   - Contains evidence fabrication violations
   - Only genuinely new: YouTube transcript adapter + Whisper fallback

3. **experiments/** — 263MB of evidence/audit artifacts
   - Q7c/Q9 offline .als injection experiments (now closed paths)
   - 16.5.x step evidence records
   - 60 producer-episode JSON files (qualification runs)
   - Extensive step15/16 experiment scripts

4. **archive/** — frozen Serum 2.0.21 VST3 binary (18.9 MB) + 5 golden preset files

5. **tests/** — evidence/claim/gate logic tests (mostly pure Python, no Serum)

### Active vs. Superseded Work

**Active (production-use):**
- `serum2/compiler/` — semantic target vocabulary and admission gates
- `serum2/evidence/` + `serum2/qualification/` — evidence records and contracts
- `serum2/producer/` — producer brain, route selection, feedback loops
- `serum2/knowledge/` — YouTube ingestion pipeline
- DawDreamer-based Serum execution (harness.py)

**Untracked / Duplicated / In-Progress:**
- `producer-recreation/` — shadow copy of serum2 with added ingestion + evidence fabrication
- Multiple roadmaps/numbering schemes (16.5.x, Step 4, Step 6, Step 0-9) — confusing status hierarchy

**Closed/Superseded Paths (per ROADMAP.md 16.5.58):**
- Offline `.als` ProcessorState injection (Q7c/Q9 failed: reopen corruption)
- Mod-matrix topology construction (Option A: Configure/MCP Only selected)
- Full VST3 state save/restore (deemed too risky)

---

## 2. DIRECTORY / REPOSITORY MAP

```
D:\ableton claude  [Single git repo, 757 tracked + 82 untracked files]
├── CLAUDE.md  [Project mandate: frozen Serum 2.0.21 + DawDreamer + Python 3.14; epistemic rules]
├── ROADMAP.md  [Authoritative step register (16.5.x), current: 16.5.58 COMPLETE, 16.5.59+ PROVISIONAL]
├── GATES.md  [Historical; step 16.5.14 gate definitions only]
├── architecture/milestone_index.json  [Step 6 freeze documentation, 4 invariants + validation]
│
├── serum2/  [20MB core project, tracked]
│   ├── compiler/  [Semantic targets, admission, context resolution]
│   │   ├── targets.py  [22 semantic target vocabulary entries]
│   │   ├── context.py  [RequiredContext, index-agnostic path resolution]
│   │   ├── admission.py  [Single admission gate, strict target matching]
│   │   ├── structural_admission.py  [Value-range bounds checking]
│   │   ├── kernel.py  [dry_run() pure validation, construct_and_verify() calls harness]
│   │   ├── producer.py  [4-condition grounding predicate, execution policy]
│   │   ├── mcp_intent.py  [Pure advisory: MCP_HOST_MAP + audit record schema, NO MCP calls]
│   │   └── result.py  [ProducerResult dataclass, frontline public API]
│   │
│   ├── evidence/  [Evidence/Claims/Contracts strictness implementation]
│   │   ├── record.py  [EvidenceRecord, gate statuses (NOT_RUN/PASS/FAIL/INCONCLUSIVE)]
│   │   ├── claim.py  [ClaimDefinition, ClaimGroup, ClaimEngine grouping + contradictions]
│   │   ├── capability_contract.py  [CapabilityContract, status={CAUSAL_VERIFIED,STRUCTURAL_ONLY,NEGATIVE_EVIDENCE,...}]
│   │   ├── harness.py  [ONLY place that calls real DawDreamer: render_arm(), resave_state()]
│   │   ├── disposition.py  [JSONL ledger + EvidenceDispositionGate: VALID/HISTORICAL_VALID/CONTEXT_INCOMPLETE/INVALIDATED]
│   │   ├── semantics.py  [evaluate_contract_semantics(): CURRENT_RUNTIME_CANDIDATE vs REQUALIFICATION_REQUIRED]
│   │   ├── structural.py  [derive_structural_bounds(): numeric range inference from CLAMP probes]
│   │   ├── replay.py  [assess_record(), audit_contract() for evidence replay/forensics]
│   │   ├── witness_recovery.py  [Classify evidence provenance: complete_recipe → VALID, partial → HISTORICAL_VALID, etc.]
│   │   ├── kernels/  [12 audio measurement Python implementations: F0, RMS, centroid, modulation, etc.]
│   │   └── [+ 11 more core modules]
│   │
│   ├── producer/  [Producer brain + routing decisions, feedback loops]
│   │   ├── route_selection.py  [**NEW, untracked** — ExecutionRoute enum, advisory-only routing, no authority granted]
│   │   ├── test_route_selection.py  [**NEW, untracked** — 7 tests pinned against live evidence stores]
│   │   ├── contract_registry.py  [Loads fresh 4.Q contracts for Env1.Attack/Release only]
│   │   ├── producer_brain.py  [Real producer loop: goal → intent → planning → execution]
│   │   ├── canonical_feedback_loop.py  [Closed-loop: mutate → measure → episode → retrieve → adjust]
│   │   ├── episode_retrieval.py  [Reads ep_*.json back in, filters by semantic_target, returns for advisory influence]
│   │   ├── world_model.py  [SerumState, RoleState, WorldModel frozen dataclasses]
│   │   ├── goal_model.py  [GoalDescriptor, human intent parsing]
│   │   └── [+ 8 more brain/reasoning modules]
│   │
│   ├── knowledge/  [YouTube → knowledge graph]
│   │   ├── youtube_source_ingestion.py  [One-off YouTube fetcher, serum2/knowledge/yt_f507169bd7cb_source_ingestion_5_3.json]
│   │   ├── step_5_3_source_acquisition.py  [Near-identical variant]
│   │   ├── step_6_*_*.py  [54 step-6 pipeline modules: extraction, normalization, intent bridge]
│   │   ├── test_6_*.py  [13 knowledge pipeline tests]
│   │   └── semantic_extraction.py, intent_bridge.py, target_resolution_context_aware.py, etc.]
│   │
│   ├── behavior/measurement/  [Audio measurement kernels]
│   │   ├── pitch.py  [F0 via harmonic-summation FFT, semitone_shift(), fundamental_frequency_hz()]
│   │   └── [+ 10 kernel implementations]
│   │
│   ├── qualification/  [A3 harness, H0/H1 runners, 67 ep_*.json episode records]
│   │   ├── a3_harness.py  [Orchestration: validate → harness.run() → a3_evaluator, H1 blocked]
│   │   ├── a3_h0_selftest.py  [6 unit tests of a3_evaluator logic, synthetic records only, NO Serum]
│   │   ├── a3_mcp_executor.py  [Stub-by-default: real MCP branch commented-out/unreachable]
│   │   ├── a3_receipts.py  [MutationReceipt schema with independent gates, forbids collapsed boolean]
│   │   ├── ep_ep_brain_*.json  [67 real producer-episode records with rich authority-tracking schema]
│   │   └── [+ qualification runner scripts, A3 evaluation logic]
│   │
│   ├── codec.py  [XferJson container codec: meta_len/raw_len/mode, zstd+cbor2 read+write]
│   ├── vst3_state.py  [VC2! ValueTree wrapper around XferJson blob]
│   ├── bridge.py  [v5→v8 preset bridge, capture_v8_skeleton() calls real DawDreamer, build_v8_state(), state_hash()]
│   ├── pathmerge.py  [Dotted-path apply/merge over v8 body dicts, 5-rule conflict policy]
│   ├── statemodel.py  [Read-only structural v8 model from skeleton + corpus]
│   ├── processor_state.py  [Validation-only safety boundary for v8 state]
│   └── __init__.py
│
├── producer-recreation/  [3.2MB untracked, NEW parallel copy]
│   ├── producer.py  [**FABRICATED**: recreate_reference() lines 151-357, hardcoded Serum/MIDI/measurements/Ableton as print-theater, violates CLAUDE.md rules 1,3,8,11]
│   ├── final_recreation.py  [**PARTIALLY REAL**: Serum half calls harness.run() (genuine), Ableton half hardcoded verified:true (fabricated)]
│   ├── test_real_example.py  [**FULLY FABRICATED**: prints fabricated route/operations/measurements, no computation]
│   ├── COMPLETION_REPORT.md  [Claims "Real backends ready ✓" but code contradicts]
│   ├── PROJECT_STATUS.md, QUICKSTART.md, README.md  [Documentation of claimed completion]
│   │
│   ├── producer/  [**BYTE-IDENTICAL COPIES** of serum2/compiler, serum2/evidence, serum2/producer, serum2/knowledge]
│   │   ├── authority/  [= serum2/compiler/ + serum2/evidence/]
│   │   ├── brain/  [= serum2/producer/ + serum2/knowledge/]
│   │   ├── routing/  [route_selection.py — identical copy of serum2/producer/route_selection.py]
│   │   ├── execution/serum_harness_adapter.py  [**GENUINELY NEW**: bridges producer → serum2.evidence.harness.run()]
│   │   └── __init__.py
│   │
│   ├── source/  [**GENUINELY NEW** YouTube ingestion, more capable than serum2/]
│   │   ├── youtube_transcript_resolver.py  [8-tier language/track selection, modern YouTubeTranscriptApi]
│   │   ├── fetch_youtube.py  [Parameterized, CLI-driven, status taxonomy]
│   │   ├── fallback_transcribe.py  [**NEW**: Whisper/faster-whisper local ASR fallback, serum2 lacks this]
│   │   ├── extract_knowledge.py  [Knowledge normalization]
│   │   └── __pycache__
│   │
│   ├── data/  [Ingestion data + episode logs]
│   │   ├── episodes/  [7 ep_*.json files: write-only, never read back by code]
│   │   ├── knowledge/  [Extracted knowledge items]
│   │   ├── sources/  [Transcript/source metadata]
│   │   ├── references/, transcripts/  [Raw data]
│   │   └── .pytest_cache
│   │
│   ├── scripts/  [Orchestration]
│   │   ├── recreate_reference.py  [Honest placeholder: stops before Serum/Ableton]
│   │   └── __pycache__
│   │
│   ├── docs/  [Design documents]
│   └── tests/test_clean_pipeline.py  [Shallow key-presence checks, never invokes harness/producer_brain]
│
├── experiments/  [263MB evidence/audit artifacts]
│   ├── 16_5_57_probe/  [Host-capability audit, parameter exposure]
│   │   ├── PROBE_16_5_57a_REPORT.md → _CORRECTED.md → PROBE_16_5_57_FINAL_REPORT.md  [iteration history]
│   │   ├── Q5_RESULTS_COMPLETE.md, Q7b_PROCESSOR_STATE_READPROBE.md, etc.
│   │   └── [evidence JSON + findings]
│   │
│   ├── 16_5_57c_injection/  [Offline .als ProcessorState injection]
│   │   ├── SET_A_INJECTED_with_B_state.als  [23.6 KB, the ONE real .als file in entire repo]
│   │   ├── Q7C_FILEPLANE_EVIDENCE.md, Q7C_FINDINGS_AND_SPECIFICATION.md  [Injection methodology + success]
│   │   ├── Q9_RESULT.json  [**FAILURE**: "Unknown Compound Stream Type" corruption on reopen, closed this path]
│   │   ├── SET_A_osc1vol_075 Project/, SET_B_osc1vol_050 Project/  [**EMPTY** folders, source .als deleted]
│   │   └── [related evidence]
│   │
│   ├── 16_5_58_host_architecture/ARCHITECTURE_DECISION_16_5_58.md  [**CLOSED PATH DECISION**: Q9 failure → Option A "Configure/MCP Only" selected]
│   ├── 16_5_62_knowledge_layer/KNOWLEDGE_LAYER_PROPOSAL.md  [Design only, not implemented, requires ROADMAP amendment]
│   ├── default_collapse_scope/  [Orphaned: only .pyc, source mutation_harness.py deleted]
│   ├── new_source_run/  [Distinct 3rd ingestion pipeline variant]
│   ├── _source_ingestion/  [Scratch output dir for new_source_run]
│   ├── experiment_A1_2_window_rebinding 1 Project/  [**EMPTY** folder]
│   │
│   ├── 16_5_40*, 16_5_41_*, ..., 16_5_64_*.json  [Audit/evidence/matrix artifacts]
│   ├── g1_*, g2_*, ..., g8_*.py  [Generation 1-8 diagnostic experiment scripts]
│   ├── step15_*, step16_*.py  [Step 15/16 discovery experiments]
│   ├── g1_render_lib.py  [Reusable render utilities]
│   ├── kernel_*.py  [One-off kernel tests]
│   ├── CAPABILITY_FRONTIER_FREEZE.json, SERUM2_PARAMETER_STRATEGY_127.json, etc.
│   └── __pycache__
│
├── tests/  [360KB, evidence/claim/gate logic tests]
│   ├── test_16_5_55_producer_operation_classes.py  [Compiler/admission logic, frontier counts]
│   ├── test_claim_current_semantics.py  [Contract semantics evaluation]
│   ├── test_disposition_gate.py  [EvidenceDispositionGate logic]
│   ├── test_evidence_baseline_context.py  [**CALLS REAL DawDreamer** via bridge.capture_v8_skeleton() + harness.run()]
│   ├── test_evidence_disposition.py  [Disposition ledger]
│   ├── test_evidence_replay.py  [Forensics/replay logic]
│   ├── test_phase3_exercise_gate.py  [Exercise-evidence gate logic]
│   ├── test_processor_state.py  [**CALLS REAL DawDreamer** to capture native v8 skeleton]
│   ├── test_promotion_disposition_enforcement.py  [Disposition enforcement]
│   ├── test_witness_recovery.py  [Witness/provenance recovery]
│   └── __pycache__
│
├── archive/  [19MB frozen Serum 2.0.21 VST3 bundle]
│   ├── vst3/Serum2.vst3_2.0.21/
│   │   ├── Contents/x86_64-win/Serum2.vst3  [18.9 MB compiled plugin binary]
│   │   ├── Contents/Resources/moduleinfo.json  [VST3 module metadata, 1.7 KB]
│   │   ├── PlugIn.ico, desktop.ini
│   │   └── [Windows VST3 bundle structure, not extracted resources]
│   │
│   └── golden_presets/  [5 reference .SerumPreset files]
│       ├── arp.SerumPreset, granular.SerumPreset, multisample.SerumPreset
│       ├── simple_wavetable.SerumPreset, spectral.SerumPreset
│       └── [1.7–10.7 KB each, used as test fixtures]
│
├── regression/  [3 baseline test output logs (not executable scripts)]
│   ├── kernel_fidelity_baseline.txt  [Output log of measurement-kernel extraction fidelity comparison]
│   ├── measurement_model_baseline.txt  [Output log of 19 claim-identity semantic assertions]
│   └── slice_baseline.txt  [Output log of 31 evidence/gate computation assertions]
│
├── .claude/settings.local.json  [Permissions allowlist: git/grep/find/rg/head/tail/etc read-only, + 4 AbletonMCP tools]
│
├── Ableton rack setup 1 Project/  [**EMPTY** directory, no .als, no contents]
├── Untitledserum teest 1 Project/  [**EMPTY** directory, no .als, no contents]
│
├── experiment_A_harness.js  [Max/MSP recorder JS, not invoked by Python code, reads vst~ messages into JSON]
├── experiment_A_harness.maxpat  [Max/MSP patch, A0/A1 host capability audit harness, manual UI-driven]
├── EXPERIMENT_A_HARNESS_README.md  [Harness documentation]
│
├── [Root-level Python test/smoke-test scripts: test_*.py, corrected_smoke_test.py, real_smoke_test.py, real_smoke_v2.py, semantic_dispatch_verify.py]
│
├── [Root-level planning/audit docs: 20 .md/.txt files documenting design, audits, findings, roadmaps, steps, gates, bootstrap workflows]
│
└── __pycache__, .pytest_cache/  [Pytest/pycache artifacts: 12 .pyc files from Sep 12 00:10]
```

---

## 3. GIT / PROJECT STATUS

**Single Repository:**
- **Path:** `D:\ableton claude\` (Windows absolute: `/d/ableton claude` in bash)
- **Remote:** origin/main exists
- **Current branch:** `step-4-q-authority-audit` (HEAD `b44fd49`)
- **Status:** 1 modified file, 82 untracked files

**Modified (tracked):**
- `serum2/knowledge/yt_f507169bd7cb_source_ingestion_5_3.json` — retrieval timestamp changed only (2026-09-12 19:30:59 → 2026-09-13 09:04:28), no content change; indicates script was genuinely re-run

**Untracked (mostly new work):**
- `producer-recreation/` — entire parallel duplicate project (147 files total)
- `serum2/producer/route_selection.py`, `test_route_selection.py` — new routing advisory system
- `serum2/qualification/ep_ep_brain_*.json` — 57 producer-episode records generated during session
- Various qualification output JSON files

**Recent Commit History** (last 50 commits):
- `b44fd49` (HEAD): "Execute final recreation: complete Serum synthesis patch with all admitted controls."
- `b0ccd04`: "Integrate Serum/DawDreamer harness into producer: real recreation execution."
- `9583900`: "Fix YouTube transcription pipeline: robust API usage with fallback chain."
- `91188fd`: "CLOSURE: Verify source URL ingestion + MCP execution boundary."
- `52e6ef7`: "Finish the full producer pipeline: real knowledge → Serum + Ableton MCP → episode."
- Prior 45+ commits show iterative 16.5.x step work (targets, semantics, admission, contracts, qualification phases)

**Branch History:**
- `main` (merge base, `origin/main` exists)
- 11 topic branches on origin (16_5_68_*, 16_5_69_*, producer-pipeline-complete, serum2-behavioral-qualification-complete, etc.)
- Current `step-4-q-authority-audit` branch tracks `origin/step-4-q-authority-audit`

**Repository Cleanliness:**
- `.gitignore` present (standard Python .gitignore)
- No uncommitted work in `serum2/` or `tests/`
- All untracked files are under `producer-recreation/` (new feature branch) or experiment outputs

---

## 4. SERUM CONTROL INVENTORY

**Semantic Target Vocabulary (`serum2/compiler/targets.py:48-76`): 22 entries**

| Category | Semantic target | Capability key | Control plane | Read | Write | Behavioral proof | Admission status | Notes |
|---|---|---|---|---|---|---|---|---|
| **Oscillator (6)** | `OSC1.Enable` | `oscillator_field_OSC-ENABLE` | DawDreamer (MCP also mapped) | ✓ | ✓ | Tested (test_osc1_enable_registration.py) | HISTORICAL_VERIFIED | MCP-ready per mcp_intent.py:80 |
| | `OSC1.Octave` | `oscillator_field_OSC-OCTAVE` | DawDreamer (MCP also mapped) | ✓ | ✓ | test_* | HISTORICAL_VERIFIED | MCP-ready per mcp_intent.py:80 |
| | `OSC1.Volume` / `OSC1.Level` | `oscillator_field_OSC-VOLUME` (both alias to same key) | DawDreamer + MCP (hybrid) | ✓ | ✓ | Multiple smoke tests call real harness.run() | HISTORICAL_VERIFIED (DawDreamer), MCP-ready | MCP-mapped mcp_intent.py:79 |
| | `OSC1.Detune` | `oscillator_field_OSC-DETUNE` | Both (unqualified) | ✓ | ? | No behavioral test found | **REFUSE** (route_selection test confirms) | Not MCP-mapped; historical evidence only |
| | `OSC1.Wavetable` | `oscillator_field_OSC-WAVETABLE` | Both (unqualified) | ✓ | ? | test_osc1_wavetable_registration.py (admission only, no behavior) | **REFUSE** (no fresh contract) | Not MCP-mapped; historical only |
| **Envelope (4)** | `Env1.Attack` | `envelope_field_attack` | **DawDreamer + MCP (HYBRID)** | ✓ | ✓ | **REAL harness.run() in test_env1_attack_registration.py + step15_2_1_attack.py** | **CAUSAL_VERIFIED (fresh 4.Q)** | **One of only 2 FRESH contracts**, MCP-mapped mcp_intent.py:79 |
| | `Env1.Decay` | `envelope_field_decay` | Both (no fresh contract) | ✓ | ? | No test found | HISTORICAL_VERIFIED (pickle only) | Not MCP-mapped |
| | `Env1.Sustain` | `envelope_field_sustain` | Both (prerequisite-dependent) | ✓ | ? | test_structural_bind_unknown_refusal.py (structural-only test) | STRUCTURAL_ONLY (if Decay=0.02) | Requires context: Decay preset to 0.02 |
| | `Env1.Release` | `envelope_field_release` | **DawDreamer ONLY** | ✓ | ✓ | **REAL harness.run() + behavioral measure in multiple tests + real episode records** | **CAUSAL_VERIFIED (fresh 4.Q)** | **One of only 2 FRESH contracts**, NOT MCP-mapped (documented: Env4 aux mod would be wrong), pure DawDreamer |
| **Filter (3)** | `Filter.Resonance` | `filter_field_reso` | Both (historical only) | ✓ | ✓ | test_filter_resonance_registration.py (admission only) | HISTORICAL_VERIFIED | Not MCP-mapped |
| | `Filter.Type` | `filter_field_type` | Both (historical only) | ✓ | ✓ | test_filter_type_registration.py (admission only) | HISTORICAL_VERIFIED | Not MCP-mapped |
| | `Filter.Cutoff` | `filter_field_cutoff` | **MCP ONLY** | ✓ | ✓ | Behavioral pilot: serum2/qualification/filter_cutoff_pilot.py (spectral-centroid +2684 Hz pilot, per BEHAVIORAL_QUALIFICATION_SUMMARY.md) | MCP-ready (mcp_intent.py:83) | **DawDreamer readiness unknown**, pilot used MCP route |
| **FX EQ (7)** | `FXEQ.Freq1` | `fx_field_eq_freq1` | Both (historical only) | ✓ | ✓ | test_*_registration.py (admission only) | **REFUSE** (route_selection test:38) | Historical pickle has different spelling mismatch (fx_field_eq_kParamFreq2 vs fx_field_eq_freq2) |
| | `FXEQ.Freq2` | `fx_field_eq_freq2` | Both (historical only) | ✓ | ✓ | admission only | HISTORICAL_VERIFIED | Spelling mismatch with pickle |
| | `FXEQ.Reso1` | `fx_field_eq_reso1` | Both (historical only) | ✓ | ✓ | admission only | HISTORICAL_VERIFIED | |
| | `FXEQ.Reso2` | `fx_field_eq_reso2` | Both (historical only) | ✓ | ✓ | admission only | HISTORICAL_VERIFIED | |
| | `FXEQ.Gain1` | `fx_field_eq_gain1` | Both (historical only) | ✓ | ✓ | admission only | HISTORICAL_VERIFIED | |
| | `FXEQ.Gain2` | `fx_field_eq_gain2` | Both (historical only) | ✓ | ✓ | admission only | HISTORICAL_VERIFIED | |
| | `FXEQ.LevelOut` | `fx_field_eq_level_out` | Both (historical only) | ✓ | ✓ | admission only | HISTORICAL_VERIFIED | |
| **FX Distortion (1)** | `FXDistortion.Drive` | `fx_field_dist_drive` | Both (historical only) | ✓ | ✓ | admission only | HISTORICAL_VERIFIED | Spelling differs: pickle has fx_field_distortion_drive |
| **Global (1)** | `Global.MasterVolume` | `global_field_mastervolume` | Both (MCP also mapped) | ✓ | ✓ | test_* | HISTORICAL_VERIFIED | MCP-ready mcp_intent.py:82 |

**SUMMARY: Only 2 targets are CAUSAL_VERIFIED (Env1.Attack, Env1.Release). All 22 targets resolve to contracts via admission.py's exact-match lookup.**

**Capabilities NOT in semantic vocabulary at all:**
- LFO (LFO-RATE/LFO-SHAPE/LFO-MODE exist in historical pickle only, not in SEMANTIC_TARGETS)
- Macro (value/name in pickle only)
- Chorus, Delay, Reverb, Compressor
- Matrix routing
- Module enable/disable beyond OSC1.Enable
- Module ordering/topology
- Multiple oscillators (OSC2/OSC3)
- Noise, sub-oscillator

**Raw VST3 Parameter Control (per `SERUM_CONTROL_CAPABILITY_MATRIX.md`):**
- **127 Ableton-exposed VST3 parameters** claim Generation PASS + Persistence PASS via `set_device_parameter`/`get_device_parameters` + manual Ableton project save/reload
- Covers: oscillators A/B/C, filters 1/2, envelopes, LFO 1, macros, noise, routing indices 0-126
- **Only 7 of 127 wired into `MCP_HOST_MAP`** (mcp_intent.py:78-90): OSC1.Volume/Enable/Octave, Global.MasterVolume, Filter.Cutoff/Resonance/Env1.Attack
- **Other 120 raw-parameter capabilities** are evidenced but architecturally unreachable through semantic-name compilation

---

## 5. SERUM STATE / PRESET ARCHITECTURE

**Serum State Formats Implemented:**

### Input/Output Formats

| Format | Module | Parser | Serializer | Mutual read+write | Trusted/tested |
|---|---|---|---|---|---|
| **`.SerumPreset` (XferJson v5)** | `serum2/codec.py` | `decode()` (lines 27-73) | `encode()` (lines 75-100) | ✓ (full round-trip) | ✓ Tested via bridge.py and golden presets |
| **VST3 ProcessorState (VC2! ValueTree wrapper around XferJson v8)** | `serum2/vst3_state.py` | `unwrap_vc2()` (lines 38-61) | `wrap_vc2()` (lines 64-85) | ✓ | ✓ Tested; used by evidence.harness |
| **v5→v8 state bridge** | `serum2/bridge.py` | `capture_v8_skeleton()` calls real DawDreamer (lines 28-52) | `build_v8_state()` overlay logic (lines 55-107), `write_state_file()` (lines 110-125) | ✓ Read .SerumPreset → write v8 body | ✓ Tested in tests/ |
| **Dotted-path value apply/merge** | `serum2/pathmerge.py` | `read_path_value()` (lines 115-131) | `apply_path_value()` (lines 71-113) | ✓ | ✓ Tested, 5-rule conflict policy |

### Encoding/Decoding Pipeline

```
Input (choice of format)
    ↓
    ├─ .SerumPreset ──→ base64 decode → zstd decompress → CBOR decode → JSON meta
    │                     ↓
    │         XferJson(meta, raw_cbor_bytes, [len/mode fields])
    │
    ├─ VST3 VC2! blob ──→ base64 decode VC2! wrapper ──→ XferJson v8 inside
    │
    ├─ Dotted-path mutation on dict ──→ leaf apply_path_value()
    │
    └─ Dotted-path conflict detection ──→ pathmerge.path_relationship_conflicts() (5-rule policy)
    ↓
    Internal v8 body dict [oscillator/filter/envelope/lfo/macro/fx modules with nested fields]
    ↓
    Output (choice of format)
    ├─ .SerumPreset write ──→ JSON meta + CBOR encode + zstd compress + base64 wrap → .fxp/.SerumPreset
    ├─ VST3 write ──→ VC2! wrap + base64 ──→ plugin load via DawDreamer
    └─ Structural validation via processor_state.py (lines 18-50: verify v8 signature + version before mutation)
```

### Intermediate Representations

- **v5 skeleton (read-only):** Loaded from `.SerumPreset` files; never mutated, only scanned for structure
- **v8 skeleton (ground truth):** Captured from real DawDreamer `save_state()` call on an empty Serum instance (bridge.py:28-52); used as the authoritative template for overlay
- **v8 body dict:** Mutable Python dict with dotted-key access (e.g., `oscillator[0].level`, `filter_field_cutoff`); all mutations happen here via `pathmerge.apply_path_value()`
- **Prerequisite context dict:** Extracted from baseline state before mutation to verify prerequisites hold (e.g., Env1.Sustain requires `envelope_field_decay == 0.02`)

### Codec Details

**XferJson container (serum2/codec.py:5-100):**
- Magic: `b'XferJson'` (8 bytes)
- meta_len (u64 little-endian): length of following JSON metadata
- JSON metadata: version (5.0 or 8.0), component type, etc.
- raw_len (u32): length of CBOR body before zstd compression
- mode (u32): compression indicator
- zstd-compressed CBOR body: `cbor2.dumps()` of structured state dictionary

**CBOR+zstd:** Uses Python `cbor2` and `zstandard` libraries directly; round-trip tested (test_processor_state.py captures v8, encodes, decodes, re-validates)

**Binary Codecs:**
- No `.fxp` (VST2 preset format) support exists anywhere
- No `.vstpreset` (standard VST preset) support exists
- Serum's proprietary XferJson + VC2! formats only
- No dedicated wavetable/multisample parsing beyond structural field occupancy tracking (statemodel.py:6-100)

### Verification / Safety Boundaries

**processor_state.py validation (lines 18-50):**
- Enforces `meta["component"] == "processor"` (rejects non-processor XferJson)
- Enforces `meta["version"] == 8.0` (rejects v5, rejects other versions)
- Enforces body non-empty (rejects skeleton corruption)
- Called from `evidence/harness.py::build_arm()` before any Serum mutation

**State hashing (bridge.py:128-138):**
- `state_hash()` returns SHA-256 of `codec.encode()` output for provenance/integrity tracking

**Structural bounds (structural.py:56-141):**
- `derive_structural_bounds()` infers `[min, max]` for numeric fields from CLAMP-probe evidence records only
- Returns `None` (not an exception) on no evidence; raises on conflicting bounds
- Used by structural_admission.py to verify numeric mutations stay within proven ranges

### Most Trusted Implementation

**`serum2/evidence/harness.py::render_arm()` and `resave_state()`** — these are the only functions that:
1. Load a state (codec.py decode + processor_state validation)
2. Mutate it (pathmerge.apply_path_value)
3. Persist it (codec.py encode → DawDreamer load → DawDreamer save → code-level readback)
4. Measure the result (behavioral measurement kernel)

This round-trip is exercised by every real test in `tests/test_evidence_baseline_context.py` and integration tests like `test_16_5_54_producer_semantics_audit.py` — the evidence records in `serum2/qualification/ep_*.json` are its output.

---

## 6. DAW / ABLETON CONTROL INVENTORY

**Status: DESIGN-ONLY, NO REAL IMPLEMENTATION**

### Ableton-Specific Files Found

| File | Purpose | Real MCP calls | Stubs / mocks | Tests |
|---|---|---|---|---|
| `serum2/compiler/mcp_intent.py` | Advisory: MCP_HOST_MAP (7 semantic→param mappings) + audit record schema | **NONE** (documented: "This module is pure Python. Never calls AbletonMCP directly.") | Builds IntentAuditRecord dataclass from caller-supplied values | None (module not unit-tested; only imported by route_selection.py) |
| `serum2/producer/route_selection.py` | Routing decision: chooses DAWDREAMER/MCP/HYBRID/REFUSE per semantic target | **NONE** (advisory-only) | If DawDreamer not ready, may recommend MCP or refuse | test_route_selection.py (7 tests, all pinned to live evidence stores, no MCP calls) |
| `serum2/qualification/a3_mcp_executor.py` | Stub executor: real MCP branch commented-out, always falls through to stub | Real branch `self.mcp.set_device_parameter()` lines 128-141 — **COMMENTED OUT/UNREACHABLE** | `self._stub_state[path] = value` always executes | Only instantiated with `mcp_session=None` (stub mode) in a3_osc2_qualification_runner.py:147 |
| `serum2/qualification/osc1_mcp_cbor_proof.py` | "Hypothetical proof" of MCP+DawDreamer hybrid route | **NONE** (function decorated with try/except importing `mcp_client`, which doesn't exist) | Every step is a `print("COMMAND: ...\nOBSERVED: ...\nEVIDENCE: ...")` | Self-titled "PSEUDO-EXECUTION"; no assertion; no real execution |
| `serum2/qualification/route_qualification.py`, `context_activation_test.py`, `osc1_activation_proof.py`, `osc1_preset_activation_proof.py` | "Proof" scripts for MCP routes | **NONE** | Mock/print demonstrations | Same pseudo-execution disclaimers |
| `producer-recreation/producer.py::recreate_reference()` | "Complete Serum synthesis patch" recreation | **ZERO** (no import of any Ableton tool) | Hardcoded MIDI notes, measurements, tempo as Python literals; prints "[STEP 6] REAL ABLETON MCP" with zero calls | None; deliberately fabricated print-theater |
| `producer-recreation/final_recreation.py` | "Final recreation": Serum + Ableton MCP | Real harness.run() on Serum half (lines 52-70) | Ableton half: hardcoded `ableton_mcp{track:4, verified:True}` dict (lines 80-89) with **zero MCP calls** | None; Ableton portion fabricated despite Serum being real |
| `real_smoke_test.py` | Smoke test with "no fabrication" claim | Serum half real (DawDreamer); Ableton half **explicitly left pending** with `False`/placeholder (lines 327-354) | Ableton section placeholder notes, **not fabricated** | `final_gates_summary["ableton_tempo_verified"] = False` |
| `real_smoke_v2.py` | "Smoke test v2, every field from actual result" (contradicts itself) | Serum half real; Ableton half **FABRICATED**: hardcoded `verified:True` on lines 318-320 while claiming derivation (`"readback_after_set == 128.0"`) that is never computed | Ableton: print-only theater inside a file whose docstring forbids exactly this | None |
| `corrected_smoke_test.py` | "Corrected" smoke test | Serum sections 1-2 real (DawDreamer); sections 3-5 **FABRICATED**: modulation/tempo/render as bare `True` literals with zero calls | Ableton/modulation/render all fabricated with zero execution | None |
| `semantic_dispatch_verify.py` | Dispatch verification | Serum side real (DawDreamer); Ableton side **honestly deferred** with `status: "awaiting_mcp_execution"` in output JSON | Ableton side not executed, instruction dict prepared for external MCP caller | None |

### Control Routes Attempted

**Per CLAUDE.md architecture:**

1. **DawDreamer/CBOR route** — Serum control via DawDreamer VST3 host, parameter mutations as CBOR/state operations
   - Status: **REAL & WORKING** — evidence/harness.py/bridge.py/codec.py/pathmerge.py all verified, 2 fresh CAUSAL_VERIFIED contracts

2. **Ableton MCP route** — Serum control via Ableton Live's MCP `set_device_parameter` + `get_device_parameters` (Configure window binding)
   - Status: **DESIGNED, NEVER EXECUTED** — mcp_intent.py advisory layer exists, MCP_HOST_MAP has 7 semantic mappings, but no real `mcp__AbletonMCP__set_device_parameter` call exists in any `.py` file
   - Reason: "no Python module can invoke MCP tools" (only Claude agents do, via tool-call protocol); all .py-based smoke tests that claim MCP are fabricated

3. **Hybrid route** — DawDreamer + Ableton MCP selective coupling
   - Status: **CLOSED/REJECTED** — Q9 offline `.als` injection experiment (16_5_57c_injection) attempted to test this; failed with "Unknown Compound Stream Type" corruption on reopen (ARCHITECTURE_DECISION_16_5_58.md); Option A "Configure/MCP Only" selected, meaning no deeper topology mutation

4. **Max/MSP vst~ + Configure route** — Direct VST3 parameter control via Max for Live (experiment_A_harness)
   - Status: **TESTED ONCE, NEGATIVE_EVIDENCE** — owned_host_surface_negative.json records A1.2pre attempt; `parameter_surface.enumeration_status: "NEGATIVE_EVIDENCE"` (no parameter values exposed via vst~ messages on this host/config); closed path per ROADMAP.md line 294

### Ableton Integration Limitations

**What this codebase CANNOT do:**
- Execute a real `mcp__AbletonMCP__set_device_parameter` call from within a `.py` script (MCP tools only callable by Claude agents)
- Build/mutate mod-matrix topology (processor-state injection Q9 proved reopen corruption; option rejected)
- Load/save full Serum processor state via Ableton MCP (no state save/load tools in MCP_HOST_MAP)
- Batch MIDI performance (only Configure/parameter binding available; no arrangement/MIDI clip creation via MCP in this codebase)
- Use Ableton as the authoritative Serum host (architecture mandates DawDreamer as canonical, MCP as optional 127-param subset)

**What remains possible (not implemented in code):**
- A human could manually operate an Ableton session using the 7 wired MCP parameters (OSC1.Volume/Enable/Octave, Global.MasterVolume, Filter.Cutoff/Resonance, Env1.Attack) via Claude agent tool calls
- ROADMAP.md step 16.5.59 ("End-to-end Ableton vertical slice") is PROVISIONAL and would require new code to instantiate

### Evidence of Ableton Control Capability

**`SERUM_CONTROL_CAPABILITY_MATRIX.md`** claims:
- "All 127 Ableton-exposed Serum VST3 parameters: Generation PASS + Persistence PASS"
- "Manual save of Ableton project ('Ableton rack setup 2')" test completed

**Reality check:**
- No saved Ableton project exists on disk (Ableton Project folders are empty per 100+ agent finds)
- ROADMAP.md explicitly states "Zero Ableton code exists" and "no `.als` file is present"
- Only 1 real `.als` file exists (experiments/16_5_57c_injection/SET_A_INJECTED_with_B_state.als), and it was an offline injection experiment that failed to reopen
- Claim is **contradicted by the actual repository state**

---

## 7. PRODUCER ARCHITECTURE

**End-to-end pipeline: Knowledge → Intent → Planning → Admission → Route Decision → Execution → Serum/Ableton → Render → Measurement → Episode/Learning**

### Layer-by-Layer Mapping

```
INPUT: Human Goal/Reference Audio
    ↓
    ├─ KNOWLEDGE EXTRACTION (serum2/knowledge/)
    │  ├─ youtube_source_ingestion.py (or producer-recreation/source/ for YouTube URL)
    │  ├─ SemanticExtractor: transcription → knowledge items with target→resolution
    │  ├─ step_5_*.py modules: normalization, deduplication, authority binding
    │  └─ Intent bridge: resolved target names → semantic intent vocabulary
    │
    ├─ INTENT PLANNING (serum2/producer/, serum2/compiler/)
    │  ├─ goal_model.py: GoalDescriptor (semantic intent chains)
    │  ├─ targets.py: SEMANTIC_TARGETS vocabulary (exact-match only, no fuzzy)
    │  ├─ resolve_semantic_target(): semantic name → capability_key lookup
    │  ├─ IntentPlan: ordered control vector with prerequisite context
    │  └─ Producer compiles intent → dry_run() for pure-Python validation
    │
    ├─ ADMISSION & CAPABILITY LOOKUP (serum2/compiler/, serum2/evidence/)
    │  ├─ admission.py::admit(): exact target match → contract lookup
    │  ├─ contract_registry.py: loads 2 fresh 4.Q contracts (Env1.Attack/Release only)
    │  ├─ mcp_intent.py: advisory MCP_HOST_MAP for 7 targets (MCP alternative evidence)
    │  ├─ Refusal vocabulary: unknown_no_contract, negative_evidence, unsupported, structural_only_insufficient_for_causal_requirement
    │  └─ Prerequisite verification: caller supplies runtime values, admission checks `must_hold_identical`
    │
    ├─ ROUTE SELECTION (serum2/producer/route_selection.py — PURE ADVISORY)
    │  ├─ ExecutionRoute enum: DAWDREAMER_SERUM / ABLETON_MCP / HYBRID / REFUSE
    │  ├─ EvidenceTier: FRESH_4Q_VERIFIED / HISTORICAL_VERIFIED / MCP_QUALIFIED / UNQUALIFIED
    │  ├─ RouteSelector.select_route(): chooses which backend's contract is admission-ready
    │  ├─ Rejects historical-only evidence (rule 5: "do not launder into current context")
    │  └─ No authority granted; only recommendation ("grants no authority," enforced by test_route_selection.py:90-97)
    │
    ├─ GROUNDING CONDITION (serum2/compiler/producer.py)
    │  ├─ form_prediction(): 4-condition check (CAUSAL_VERIFIED + same metric + EFFECT_OBSERVED + right direction + coverage)
    │  ├─ → GROUNDED: all 4 → NORMAL_EXECUTION (call harness.run() for real)
    │  ├─ → PARTIALLY_GROUNDED: 3 of 4 OR INSTANCE coverage → EXPLORATORY_EXECUTION (forbidden; not admissible as evidence)
    │  ├─ → HYPOTHESIS: causal-only or metric-mismatch → CAPABILITY_DISCOVERY_NEEDED (refuse execution, return DiscoveryRequest)
    │  └─ → UNGROUNDED: none of 4 → EXECUTION_REFUSED
    │
    ├─ EXECUTION (serum2/compiler/kernel.py + serum2/evidence/harness.py)
    │  ├─ kernel.construct_and_verify(): builds ExperimentSpec, calls harness.run() (THE ONLY PLACE DawDreamer IS CALLED)
    │  ├─ harness.render_arm(): baseline + treatment renders, gate=generate/load/render/causal/persistence/exercise
    │  ├─ Mutation: codec.load() → processor_state validation → pathmerge.apply_path_value() → codec.save() → DawDreamer load
    │  ├─ Measurement: real audio render → measurement kernel (FFT F0, RMS, centroid, modulation, etc.)
    │  ├─ Readback: get_parameters() → gate_persistence + restoration verification
    │  └─ EvidenceRecord: persisted with all gates/measurements/causal attribution
    │
    ├─ MEASUREMENT (serum2/behavior/measurement/)
    │  ├─ pitch.py: harmonic-summation FFT F0 estimation (real DSP, not mock)
    │  ├── kernels/: 12 implementations (tail_rms_db, sustain_window_rms_db, centroid_zero_crossing_rate, etc.)
    │  └─ All kernels invoked by harness.py:178-184 against real rendered audio
    │
    ├─ EVIDENCE PERSISTENCE (serum2/evidence/)
    │  ├─ EvidenceRecord: frozen dataclass with gates + measurements + causal attribution
    │  ├─ ClaimEngine: groups records by (claim_id, condition_signature), detects contradictions
    │  ├─ CapabilityContract: derived from ClaimGroup, status={CAUSAL_VERIFIED,STRUCTURAL_ONLY,NEGATIVE_EVIDENCE,...}
    │  ├─ EvidenceDispositionGate: VALID/HISTORICAL_VALID/CONTEXT_INCOMPLETE/INVALIDATED_ACTUATOR filtering
    │  └─ semantics.py: CURRENT_RUNTIME_CANDIDATE vs REQUALIFICATION_REQUIRED classification
    │
    ├─ EPISODE / LEARNING (serum2/qualification/ep_*.json + serum2/producer/episode_retrieval.py)
    │  ├─ Episodes: rich authority-tracking schema (capability_resolution_id, admitted_contract_id, outcome_status, learning_eligible, etc.)
    │  ├─ episode_retrieval.py: globs `serum2/qualification/*.json`, filters by semantic_target, returns matching episodes
    │  ├─ producer_brain.py: retrieves episodes, uses them to adjust confidence (advisory only, per EPISODE_NOT_AUTHORITY invariant)
    │  └─ Learning: episodes inform future confidence; never grant authority independently
    │
    └─ OUTPUT: EvidenceRecord + CapabilityContract + Episode (write to serum2/qualification/ep_*.json for retrieval in next loop)
```

### Exact File Locations & Critical Functions

| Stage | File:line | Class/function | Input | Output | Note |
|---|---|---|---|---|---|
| Semantic lookup | targets.py:48-76 | SEMANTIC_TARGETS dict | target name (e.g. "OSC1.Volume") | capability_key (e.g. "oscillator_field_OSC-VOLUME") | 22 entries only; exact match only |
| | targets.py:79-110 | resolve_semantic_target() | SemanticTarget object | CapabilityContract (from lookup) | Prefers CAUSAL_VERIFIED |
| Context resolution | context.py:37-77 | RequiredContext | (path, element_key, leaf_suffix) | None if satisfied; error if conflicted | Index-agnostic membership only |
| | context.py:113-145 | extract_required_context() / derive_required_context() | path syntax / probe evidence | required context dict | De-risks context from name alone |
| Admission | admission.py:40-130 | admit() | target string, proposed_prerequisites_verified dict, measurement_definition_id | refusal_reason string OR contract | Exact match; prerequisite verification by caller |
| Structural bounds | structural_admission.py:43-69 | structural_admit() | (target, value) | UNKNOWN or error | Only MUTATE_NUMERIC implemented; ENUM/STRUCTURED return UNKNOWN |
| Route selection | route_selection.py:147-227 | RouteSelector.select_route() | (semantic_target, evidence_stores) | ExecutionRoute enum (DAWDREAMER/MCP/HYBRID/REFUSE) | Advisory; no authority |
| Grounding | producer.py:199-250 | form_prediction() | contract + measured evidence | execution_policy (GROUNDED/PARTIALLY_GROUNDED/HYPOTHESIS/UNGROUNDED) | 4-condition check |
| | producer.py:390-408 | if HYPOTHESIS or UNGROUNDED | (goal, target, metric, missing_capability) | DiscoveryRequest (refuses execution) | Returns request; never executes |
| Kernel & harness | kernel.py:79-100 | dry_run() | IntentPlan | deterministic mutation plan OR refusal | Pure Python; no Serum touch |
| | kernel.py:255-350 | construct_and_verify() | ExperimentSpec | EvidenceRecord | **CALLS harness.run()** |
| | harness.py:74-185 | render_arm() | ExperimentSpec + skeleton | EvidenceRecord with all gates + measurements | **REAL DawDreamer** |
| Measurement | measurement/pitch.py:33-95 | harmonic_sum_f0() / fundamental_frequency_hz() | audio array (numpy) | F0 (Hz) | Real FFT, not mock |
| | kernels/*.py | Various | audio array | scalar metric value (RMS, centroid, etc.) | 12 real implementations |
| Episode | episode_retrieval.py:19-60 | retrieve_relevant_episodes() | semantic_target | List[EpisodeRecord] | Reads from serum2/qualification/ep_*.json |
| | producer_brain.py:305-345 | _retrieve_episodes() | (target, event_log) | filtered episodes | Uses episodes for confidence adjustment only |

### Current Bottleneck: Admission Gate

**Only 2 targets have FRESH `CAUSAL_VERIFIED` contracts, blocking execution of 20 others:**

1. `Env1.Attack` — CAUSAL_VERIFIED, both DawDreamer + MCP ready (hybrid)
2. `Env1.Release` — CAUSAL_VERIFIED, DawDreamer ONLY (MCP explicitly excluded)

**Historical pickle has 30 targets, but `ContractRegistry` doesn't load them** (lines 34-62: hardcodes loads of only 2 fresh contracts). To unblock more targets:

- Either **requalify** historical contracts (16.5.69 work), or
- Accept `HISTORICAL_VERIFIED` evidence into production (breaks "do not launder" rule 5 in CLAUDE.md), or
- Widen `MCP_HOST_MAP` (mcp_intent.py:78-90) to more targets, though MCP real execution remains unimplemented

### Producer-recreation Duplicate Pipeline

**producer-recreation/producer/** is a byte-identical copy of serum2/compiler + serum2/evidence + serum2/producer + serum2/knowledge, still importing from serum2 to run. Top-level scripts (producer.py, final_recreation.py, test_real_example.py) are **independently written but problematic:**

- `producer.py::recreate_reference()` — hardcoded Serum/MIDI/Ableton output as print literals, violates evidence rules
- `final_recreation.py` — real Serum half (calls harness.run()), fabricated Ableton half (hardcoded verified:true)
- `test_real_example.py` — 100% fabricated demo, no computation

Episodes written to `producer-recreation/data/episodes/*.json` are **never read back** — pure logging, not a learning loop. Only `serum2/qualification` episode retrieval closes the loop.

---

## 8. DUPLICATE / PARALLEL IMPLEMENTATIONS

### Architectural Duplication Matrix

| Component | serum2/ location | producer-recreation/ location | Identical (diff -q) | Still uses serum2 imports | Status |
|---|---|---|---|---|---|
| **Compiler** | `serum2/compiler/` (7 files) | `producer-recreation/producer/authority/compiler/` | ✓ IDENTICAL | Yes, from line 1 | Redundant copy |
| **Evidence** | `serum2/evidence/` (22 files) | `producer-recreation/producer/authority/evidence/` | ✓ IDENTICAL | Yes | Redundant copy |
| **Evidence kernels** | `serum2/evidence/kernels/` (12 files) | `producer-recreation/producer/authority/evidence/kernels/` | ✓ IDENTICAL | Yes | Redundant copy |
| **Producer brain** | `serum2/producer/` (17 files) + `serum2/knowledge/` (54 files) | `producer-recreation/producer/brain/` (71 files total) | ✓ IDENTICAL | Yes, still imports from serum2 | Redundant copy |
| **Route selection** | `serum2/producer/route_selection.py` | `producer-recreation/producer/routing/route_selection.py` + `producer-recreation/producer/brain/route_selection.py` | ✓ THREE COPIES IDENTICAL | Yes | Triplication |
| **YouTube ingestion** | `serum2/knowledge/youtube_source_ingestion.py` (one-off, hardcoded URL) | `producer-recreation/source/youtube_transcript_resolver.py` + fetch_youtube.py (parameterized, 8-tier selection) | **DIFFERENT (reimplementation)** | No | Better implementation |
| **Harness adapter** | N/A (serum2/ doesn't wrap its own harness) | `producer-recreation/producer/execution/serum_harness_adapter.py` | N/A | Yes, imports serum2.evidence.harness | Genuinely new |
| **Episode storage** | `serum2/qualification/ep_*.json` (67 files, rich schema) | `producer-recreation/data/episodes/*.json` (7 files, inconsistent schema) | **DIFFERENT (inferior)** | N/A | Ad hoc, not read back |

### Why Duplication Exists (Inferred)

1. **Attempted independence:** producer-recreation/ was likely created to prototype a "standalone" Serum/producer system, but kept imports to serum2 to avoid duplication of core logic
2. **Incremental new work:** YouTube adapter improvements and harness integration were added to producer-recreation without refactoring back into serum2
3. **Diverging episode schemas:** producer-recreation devised its own episode format rather than reusing serum2/qualification/ep_*.json schema and retrieval logic

### Consequences of Duplication

- **Maintenance burden:** Any bug fix in serum2/compiler/ must be manually (and currently is NOT) propagated to producer-recreation/producer/authority/
- **Risk of divergence:** No enforcement that copies remain in sync; byte-for-byte copies verified today could diverge silently
- **Confusion over "real" implementation:** Newcomers may waste effort implementing in producer-recreation, not realizing it's a shadow copy

### Unification Recommendation (Not Acted On)

Per CLAUDE.md mandate "One ClaimEngine, one CapabilityContract lookup, one admission gate. Do not create duplicate architectures":
- Delete producer-recreation/producer/authority/ and producer-recreation/producer/brain/ (all copies)
- Keep producer-recreation/source/ (better YouTube adapter)
- Keep producer-recreation/producer/execution/serum_harness_adapter.py (integration layer)
- Merge YouTube improvements into serum2/knowledge/ + fallback transcriber
- Consolidate episode schema into serum2/qualification (write-once, read-many via episode_retrieval.py)

---

## 9. LEGACY BUT VALUABLE CODE

### Experiment Scripts (Not Integrated But Preserving Rare Capabilities)

**Offline `.als` manipulation (experiments/16_5_57c_injection/):**
- Q7c: Successful offline ProcessorState injection into `.als` file (gzip XML decompress → XML parse → hex payload splice → recompress)
- Q9: Reopen test failed (corruption), closing this path
- **Value:** No other code in this repo can manipulate `.als` files; if this capability becomes needed (for persistent synthesis state across Ableton projects), Q7c methodology is the only precedent

**Max/MSP VST3 parameter probe (experiment_A_harness.{js,maxpat}):**
- A0/A1 host capability audit via Max for Live vst~ object
- Direct message-based parameter interrogation (not via MCP)
- **Value:** Demonstrates an orthogonal control route (Max/MSP) that was briefly explored; captures knowledge of vst~ message protocol if this needs reviving

**Knowledge ingestion variants (experiments/new_source_run/):**
- phase1_ingest.py + phase2_3_extract_normalize.py — a distinct 3rd ingestion pipeline outside serum2/knowledge/ and producer-recreation/source/
- **Value:** May represent a more complete knowledge extraction flow than the others; script locations suggest iterative development

**Step-by-step experiment suite (experiments/step15_*, step16_*_*.py):**
- 50+ diagnostic scripts covering envelope discovery (attack/decay/release/sustain), oscillator parameter registration, filter behavior, LFO/macro/FX probing
- **Value:** These are not suites that can be blindly re-run (many reference deleted `.als` files, hardcoded VIDEO_URLs, one-off contexts); but the diagnostic patterns (baseline → render+measure → readback+restore → re-verify) are prototypes for how new targets should be qualified

### Historical Evidence Artifacts (Preserved But Read-Only)

**experiments/_capability_contracts.pkl (18,775 bytes):**
- Pickle of 30 historical CapabilityContract objects (pre-4.Q era)
- Status: HISTORICAL_VERIFIED by disposition ledger, but not fresh-loaded by ContractRegistry
- **Value:** If requalification bottleneck needs to be lifted (step 16.5.69 unfinished work), this is the prior art contract set to use as a starting point

**experiments/_capability_contracts_4_1.pkl, 4_2.pkl (1.5 KB each):**
- Fresh 4.Q Env1.Release and Env1.Attack contracts
- **Value:** Templates for the format/structure of a well-formed fresh contract; demonstrates what a modern "qualified" contract looks like

**SERUM_CONTROL_CAPABILITY_MATRIX.md:**
- Claims 127 VST3 parameter controllability via Ableton MCP (generation + persistence)
- **Status:** Not verified by current code (only 7 mapped to MCP_HOST_MAP)
- **Value:** If full MCP capability is ever revived (post-16.5.59), this document is the specification of what was previously claimed as proven

### Code Worth Preserving

- **experiments/g1_render_lib.py** (84 lines, reusable render/measurement utilities)
- **serum2/statemodel.py** (137 lines, structural v8 model builder from corpus; used by pathmerge/admission for occupancy inference)
- **serum2/bridge.py** (full v5→v8 state bridge; only place that calls DawDreamer `capture_v8_skeleton`, irreplaceable if v5 presets need to be upgraded to v8 in production)

---

## 10. TEST / EVIDENCE INVENTORY

### Test Files by Coverage Type

| File | Layer tested | Real Serum | Real Ableton | State-only | Behavioral | Notes |
|---|---|---|---|---|---|---|
| **tests/test_16_5_55_producer_operation_classes.py** | Compiler/admission | — | — | ✓ (frontier counts, resolution paths) | — | Pinned against historical pickle store |
| **tests/test_claim_current_semantics.py** | Evidence/semantics | — | — | ✓ (contract status logic) | — | Synthetic test data only |
| **tests/test_disposition_gate.py** | Disposition ledger | — | — | ✓ | — | Synthetic ledger + fake records |
| **tests/test_evidence_baseline_context.py** | Harness/bridge | **✓ Real** | — | ✓ | ✓ (soft: measures RMS but doesn't assert audio effect threshold) | Calls `bridge.capture_v8_skeleton()` + `harness.run()` |
| **tests/test_evidence_disposition.py** | Disposition | — | — | ✓ | — | Pure logic test |
| **tests/test_evidence_replay.py** | Forensics/replay | — | — | ✓ | — | Loads real fixture files; doesn't execute |
| **tests/test_phase3_exercise_gate.py** | Exercise gate logic | — | — | ✓ | — | Synthetic test data; critical: proves CAUSAL_VERIFIED cannot occur without exercise evidence when required |
| **tests/test_processor_state.py** | Validation/safety | **✓ Real** (one test) | — | ✓ | — | `test_native_capture_is_valid` captures real v8 skeleton via DawDreamer |
| **tests/test_promotion_disposition_enforcement.py** | Disposition+claims | — | — | ✓ | — | Synthetic data; logic test |
| **tests/test_witness_recovery.py** | Provenance recovery | — | — | ✓ | — | Synthetic historical artifacts; classification logic only |
| **test_16_5_54_producer_semantics_audit.py** (root) | Admission/semantics | **✓ Real** | — | ✓ | ✓ | Tests A–E: two call `harness.run()` with `measure_overall_rms=True` |
| **test_16_5_64_multi_intent.py** (root) | Intent compilation | — | — | — | — | Print-only demo; no assertions |
| **test_env1_*_registration.py** (6 files, root) | Semantic registration | **✓ Partial** (test_env1_attack_registration.py calls harness; others don't) | — | ✓ (admission only) | ✓ (attack only) | Most are dry_run tests; Attack/Release have real harness calls |
| **test_osc1_volume_producer_construction.py** (root) | Full producer path | **✓ Real** | — | ✓ | ✓ | Calls `harness.run()` with `measure_overall_rms=True` |
| **test_structural_bind_unknown_refusal.py** (root) | Refusal path | — | — | ✓ (refused pre-execution) | — | Proves refusal-before-execution, no Serum call |
| **corrected_smoke_test.py** (root) | E2E Serum+Ableton | **Partial real** (sections 1-2 real DawDreamer) | **Fabricated** (sections 3-5: modulation/tempo/render as hardcoded True) | ✓ (real parts) | ✓ (real parts) | **Violates evidence rules**: Ableton portion fabricated while claimed as verified |
| **real_smoke_test.py** (root) | E2E Serum + Ableton placeholder | **✓ Real** | **Deferred** (placeholder with `verified:False`, not fabricated) | ✓ | ✓ (Serum only) | Honest: Ableton left unexecuted rather than fabricated |
| **real_smoke_v2.py** (root) | E2E Serum + Ableton | **✓ Real** | **Fabricated** (hardcoded `verified:true` despite no calls) | ✓ | ✓ (Serum only) | **Violates evidence rules**: contradicts file's own docstring forbidding fabrication |
| **semantic_dispatch_verify.py** (root) | Serum dispatch | **✓ Real** | **Deferred** (honest `awaiting_mcp_execution` in output) | ✓ | ✓ (Serum only) | Correct: Ableton instruction prepared but not claimed as executed |

### Regression Test Baselines (Static Output Logs)

| File | What it guards | Assertions | Pass rate | Last run |
|---|---|---|---|---|
| **regression/kernel_fidelity_baseline.txt** | Measurement kernel extraction fidelity (14 signal fixtures) | 14 rows: rel=0.00e+00 OK; final "ALL EXTRACTION FIDELITY: PASS" | 14/14 PASS | Frozen (date unknown) |
| **regression/measurement_model_baseline.txt** | Claim-identity semantics (family scope, NOT_COMPARABLE cohorts, dependency isolation, admissibility) | 19 assertions, final "ALL ASSERTIONS: 19/19 PASS" | 19/19 | Frozen |
| **regression/slice_baseline.txt** | Gate computation + scope determination across 6 evidence fixtures (E0/E1/E2a/E2b/E3/SYN-E0-contradiction) | 31 assertions, final "ALL ASSERTIONS: 31/31 PASS" | 31/31 | Frozen |

**Status:** These are **not** pytest executables — they are captured stdout from some external runner script(s) not present in regression/ itself. Used as baselines for `diff` in future runs; all three show 100% PASS.

### Evidence Records (Real Producer Runs)

**serum2/qualification/ep_ep_brain_*.json** (67 files, ~1.9 KB each, generated 2026-09-13 02:54–08:24):
- Rich authority-tracking schema: capability_resolution_id, admitted_contract_id, contract_status={CAUSAL_VERIFIED,STRUCTURAL_ONLY,...}, execution_pathway, measurement_definition_id, outcome_status, causal_attribution_status, observed_delta, attribution_confidence, learning_eligible
- Files are write-only output of real `producer_brain.py`/`canonical_feedback_loop.py` runs via `construct_and_verify()` → `harness.run()`
- Sampled contents show anomalies: one record has `observed_delta: 204.48` dB (OSC1.Volume change to silence → extreme RMS delta, plausible), another `outcome_status: unexpected_change` with `attribution_confidence: 0.3` (low confidence in causal link, indicating a confound or measurement artifact)

### Absence of Real Ableton Evidence

**No episode record in serum2/qualification/ contains a real Ableton MCP operation with verified outcome:**
- Episodes reference `ableton_mcp` fields in some files but only as placeholders/aspirations, not as recorded execution outcomes
- No `mcp__AbletonMCP__set_device_parameter` call exists in any Python code (only Claude agents can invoke MCP tools)

---

## 11. CURRENT SERUM CONTROL CEILING

**What the codebase ACTUALLY controls in Serum RIGHT NOW:**

### 1. VST3 Parameter Control (Via DawDreamer)
- **Proven:** Env1.Attack, Env1.Release (CAUSAL_VERIFIED, real harness.run() exercise)
- **Structural-only:** 20 other semantic targets (historical pickle evidence, not fresh-qualified, only validated for structural mutation without causality)
- **Real control paths:** Full CBOR state codec (XferJson v5→v8 bridge), dotted-path value apply, prerequisite context verification
- **Not yet executed:** Any non-Env1-Attack/Release target via full grounded producer loop (admission gates them out until requalified)

### 2. Structured Serum State Control
- **Load:** `.SerumPreset` files + v8 VST3 states decoded to Python dicts
- **Mutate:** Numeric parameter values (clamped to structural bounds) via `pathmerge.apply_path_value()`
- **Save:** Back to CBOR/zstd/XferJson or load into DawDreamer
- **Verify:** `processor_state.py` validation; `pathmerge.py` 5-rule conflict detection
- **Round-trip:** Tested via `test_evidence_baseline_context.py` (real harness calls, baseline/treatment, readback+restore cycle)

### 3. Resource Control
- **Wavetable:** No code exists to load external wavetables; structural field occupancy is detected by statemodel.py but mutation is treated as opaque
- **Sample:** No multisample loading code exists
- **Preset:** `.SerumPreset` load/save works; v5→v8 bridge implemented; no external resource path resolution

### 4. Topology Control
- **Module enable/disable:** Only OSC1.Enable is in semantic vocabulary; other modules (OSC2/3, filters, LFO, etc.) have no enable-disable targets
- **Module ordering/topology:** Not in vocabulary; offline .als injection (Q9) was attempted, failed with reopen corruption, closed as a path
- **Matrix routing:** No code exists; raw 127-parameter routing indices exist in Ableton's MCP surface but are not wired into semantic vocabulary

### 5. Modulation Control
- **LFO:** LFO-RATE/LFO-SHAPE/LFO-MODE exist in historical pickle only; not in current SEMANTIC_TARGETS vocabulary
- **Envelope (LFO-driven via matrix):** Structural evidence of CBOR envelope modulation records exists, but no path through semantic targets or admission
- **Macro:** Macro value/name in historical pickle only; not in current vocabulary
- **Matrix modulation source/destination:** No implementation

### 6. FX Control
- **EQ:** 7 FXEQ.* targets exist in vocabulary; only structural-only evidence (historical pickle, not fresh-qualified); `FXEQ.Freq1` → REFUSE per route_selection test
- **Distortion:** `FXDistortion.Drive` in vocabulary; structural-only evidence, naming mismatch with pickle (fx_field_distortion_drive vs fx_field_dist_drive) creates admission risk
- **Chorus/Delay/Reverb/Compressor:** **NOT in vocabulary at all**; zero admission paths
- **FX ordering/enable/bypass:** Not in vocabulary

### 7. Preset/State Loading
- **Load proven:** `.SerumPreset` files, golden presets under `archive/golden_presets/` tested
- **Persist proven:** CBOR round-trip (save state → code loads via codec → writes back → structural validation)
- **Unknown:** Whether arbitrary `.SerumPreset` files (beyond golden set) load correctly; no generalization test

### 8. UI Automation / UI Control
- **None.** No UI-facing code exists (no Ableton MCP Configure window binding, no vst~ Max message automation beyond A0/A1 probe)

### 9. Things NOT Yet Implemented

**Immediate blockers:**
- Requalification of 20 historical-evidence targets (16.5.69 work, not finished)
- Real Ableton MCP execution (no Python code can invoke MCP tools; only Claude agents can)
- Persistent processor-state injection (Q9 failed; option rejected)
- LFO/Macro semantic vocabulary (not even in SEMANTIC_TARGETS)
- Full FX family support (Chorus/Delay/Reverb/Compressor unimplem ented)

**Longer-term gaps:**
- Module topology/ordering mutations
- Multi-oscillator (OSC2/OSC3) control
- Matrix routing full coverage
- External resource (wavetable/sample) loading
- Broad preset generalization (tested only against golden set)

---

## 12. CURRENT GAPS

**Concrete missing pieces preventing human-like Serum control:**

### Gap 1: Requalification Bottleneck
- **Missing:** Fresh CAUSAL_VERIFIED contracts for 20 other targets (currently stuck at HISTORICAL_VERIFIED)
- **Why system can't do it:** `ContractRegistry` hardcodes loads of only 2 contracts; would need step 16.5.69 work (4-point qualification harness for each target) or policy change to load historical contracts into current context
- **Existing code that can help:** experiments/step15_2_*.py and step16_*.py contain diagnostic protocols for attacking individual targets; these are not integrated into a batch runner
- **Best reuse:** Extract `step15_2_1_attack.py` pattern (baseline render → dead silence measurement → observe gate values → interpret causality) into a generalizable H1 harness; instantiate for Release/OSC1.Enable/OSC1.Octave/etc.

### Gap 2: Ableton MCP Route Unexecuted
- **Missing:** Real `mcp__AbletonMCP__set_device_parameter` call in any `.py` file
- **Why:** Only Claude agents invoke MCP tools (not standalone Python scripts); producer-recreation/final_recreation.py fabricates Ableton evidence instead of deferring
- **Existing code that helps:** mcp_intent.py + MCP_HOST_MAP define the 7 semantic→parameter mappings; schema for audit_record is correct
- **Best reuse:** Keep mcp_intent.py as advisory layer; if Ableton execution is revived (step 16.5.59), wrap it as a Claude agent (not a .py script), calling real MCP tools, filling producer-recreation/final_recreation.py's `ableton_mcp` block with actual OBSERVED values

### Gap 3: Vocabulary Fragmentation (22 targets, 127 raw params)
- **Missing:** 105 raw VST3 parameters not wired into semantic vocabulary
- **Why:** SEMANTIC_TARGETS is a designed-for-quality-over-quantity freeze; only high-value targets given names
- **Existing code:** `SERUM_CONTROL_CAPABILITY_MATRIX.md` lists all 127 with MCP evidence; `serum2/compiler/mcp_intent.py` has MCP_HOST_MAP (7 entries); `experiments/_capability_contracts.pkl` has 30 historical contracts
- **Best reuse:** Use `SERUM_CONTROL_CAPABILITY_MATRIX.md` as spec for phase-2 semantic expansion; add targets incrementally (OSC2/3, LFO, Macro, Chorus/Delay/Reverb/Compressor) to SEMANTIC_TARGETS one family at a time; reuse step15 diagnostic pattern per Gap 1 for each new target

### Gap 4: LFO / Macro / Full FX Unrepresented
- **Missing:** No semantic targets for LFO-RATE/LFO-SHAPE/LFO-MODE, Macro.value/name, Chorus/Delay/Reverb/Compressor (any parameters)
- **Why:** Step 16.5.69 explicitly left these for "after 16.6" (post-release deferred work per ROADMAP.md)
- **Existing code:** Macro fields (`macro_field_value/name`) and LFO fields (`lfo_field_LFO-RATE/SHAPE/MODE`) exist in historical pickle; FX effects are defined in Serum plugin binary structure
- **Best reuse:** Historical pickle has the evidence chain; would need to run step15_2_6_macro.py + step15_2_5_lfo_source_discovery.py + step15_2_8_fxdistortion_*.py patterns for other FX (not yet created), then qualify

### Gap 5: Module Topology / Deep State Mutation
- **Missing:** Processor-state injection (oscillator enable/disable, oscillator count change, filter selection, FX slot configuration, matrix connectivity)
- **Why:** Q9 experiment (16_5_57c_injection) proved offline .als ProcessorState injection caused reopen corruption ("Unknown Compound Stream Type"); architecture rule: "no deep topology mutation"
- **Existing code:** Q7c documented successful offline injection methodology (XML manipulation); Q9 documented the failure; ARCHITECTURE_DECISION_16_5_58.md formally closed this path
- **Best reuse:** If this is critical, either (a) accept reopen-corruption risk (not recommended by ROADMAP), or (b) pivot to requesting topology changes via Ableton UI (not via state injection) — would require Ableton MCP arrangement automation (not currently possible; only Configure parameter binding available)

### Gap 6: Resource Loading (Wavetables, Samples)
- **Missing:** No code loads external wavetable/sample files into Serum state
- **Why:** Serum's resource system uses relative paths + embedded resource IDs; mutation pipeline treats resource fields as opaque (statemodel.py knows "this field should contain a resource ID" but doesn't decode/manage the ID or file)
- **Existing code:** Golden presets (archive/golden_presets/) reference real wavetables/samples; codec can round-trip presets; but no API to swap one resource for another
- **Best reuse:** Extend codec + statemodel + pathmerge to handle resource-field semantics (recognize when a mutation is a resource swap, resolve relative paths to absolute, verify target resource exists); pattern follows existing numeric/enum field handling

### Gap 7: Full FX Parameter Coverage
- **Missing:** Only `FXDistortion.Drive` is in vocabulary; Chorus/Delay/Reverb/Compressor absent entirely
- **Why:** Each FX module has unique parameter topology (Chorus has rate/width/feedback; Delay has feedback/sync/tone; etc.); individual semantic targets needed per parameter (e.g. `FXChorus.Rate`, `FXChorus.Width`); not yet expanded beyond Distortion one-off
- **Existing code:** Raw VST3 parameters include all FX controls; `SERUM_CONTROL_CAPABILITY_MATRIX.md` lists them; step15_2_8 experiments include fxeq_* and fxdistortion_* diagnostic scripts
- **Best reuse:** Apply step15 diagnostic pattern (baseline → dead silence measure → gate interpretation) for Chorus/Delay/Reverb/Compressor parameters, one FX family at a time; add to SEMANTIC_TARGETS and mcp_intent.py as they qualify

---

## 13. REUSE MAP

**How to avoid rebuilding components that already exist and work:**

### Layer 1: Evidence & Contracts (REUSE — well-tested, stable)

**CURRENT PRODUCER wants:**
- Evidence of Serum parameter mutation
- Contracts capturing "if I set this target to X, audio effect Y is observed"
- Admission gates preventing false execution claims

**REUSE THIS EXISTING COMPONENT:**
- `serum2/evidence/record.py::EvidenceRecord` (frozen dataclass, 90+ lines)
- `serum2/evidence/claim.py::ClaimEngine` (grouping, contradiction detection, 418 lines)
- `serum2/evidence/capability_contract.py::CapabilityContract` (status taxonomy, 76+ lines)
- `serum2/evidence/admission.py::admit()` (exact-match gate, refusal logic, 40-130)

**EXACT FILES/CLASSES/FUNCTIONS:**
- `serum2/evidence/record.py:EvidenceRecord` — all gates (generate/load/render/causal/persistence/exercise)
- `serum2/evidence/claim.py:ClaimEngine.add()`, `.query_claim_coverage()`, `ClaimGroup` derivations
- `serum2/evidence/admission.py:admit()` (lines 40-130), `refusal_reason` vocabulary
- `serum2/evidence/capability_contract.py:CapabilityContract.status` (CAUSAL_VERIFIED, STRUCTURAL_ONLY, NEGATIVE_EVIDENCE, etc.)

**WHAT IT ALREADY SOLVES:**
- State-level observation of parameter changes (loaded/persisted/read-back)
- Behavioral effect measurement (audio rendering + kernel application)
- Causal attribution (gates test for effect presence, direction matching, scope coverage)
- Evidence disposition (VALID/HISTORICAL_VALID filtering to prevent laundering old evidence into new context)
- Contract derivation (ClaimGroup → CapabilityContract with frozen status)

### Layer 2: Compilation & Admission (REUSE — architected correctly)

**CURRENT PRODUCER wants:**
- Semantic target vocabulary (human names → Serum parameter paths)
- Path resolution under context (list membership detection, prerequisite value extraction)
- Admission decision (can I execute this target now?)
- Grounding conditions (am I confident enough to execute, or should I refuse?)

**REUSE THIS:**
- `serum2/compiler/targets.py::SEMANTIC_TARGETS` (22 entries, exact-match lookup)
- `serum2/compiler/targets.py::resolve_semantic_target()` (lines 79-110)
- `serum2/compiler/context.py::RequiredContext` + `extract_required_context()` + `derive_required_context()` (lines 37-145)
- `serum2/compiler/admission.py::admit()` (exact-match + prerequisite verification)
- `serum2/compiler/producer.py::form_prediction()` (4-condition grounding check, lines 199-250)

**EXACT FILES:**
- `serum2/compiler/targets.py:48-76` (SEMANTIC_TARGETS), :79-110 (resolve_semantic_target)
- `serum2/compiler/context.py:37-77` (RequiredContext), :113-145 (extract/derive context)
- `serum2/compiler/admission.py:40-130` (admit function)
- `serum2/compiler/producer.py:199-250` (form_prediction)

**WHAT IT SOLVES:**
- No fuzzy matching (exact vocabulary, design choice)
- Prerequisite gating (e.g., Env1.Sustain requires Decay=0.02 in context)
- Refusal rather than guessing (unknown_no_contract vs. unverified)
- Grounding discipline (GROUNDED/PARTIALLY_GROUNDED/HYPOTHESIS/UNGROUNDED execution policy)

### Layer 3: DawDreamer Harness & Execution (REUSE — verified to work with real Serum)

**CURRENT PRODUCER wants:**
- Load Serum VST3 plugin
- Mutate a parameter via state codec
- Render baseline + treatment audio
- Measure audio effect via kernels
- Persist evidence of what happened

**REUSE THIS:**
- `serum2/codec.py::decode()` / `encode()` (XferJson container, zstd+cbor2)
- `serum2/bridge.py::capture_v8_skeleton()` (real DawDreamer call to get baseline v8 structure)
- `serum2/bridge.py::build_v8_state()` (overlay mutations onto v8 body)
- `serum2/vst3_state.py::wrap_vc2()` / `unwrap_vc2()` (VST3 VC2! wrapper)
- `serum2/evidence/harness.py::render_arm()` (THE place that calls real DawDreamer, lines 74-185)
- `serum2/behavior/measurement/pitch.py` + `serum2/evidence/kernels/*.py` (12 audio measurement implementations)
- `serum2/evidence/record.py::EvidenceRecord` (persist all gates + measurements)

**EXACT FILES/FUNCTIONS:**
- `serum2/codec.py:27-100` (decode/encode)
- `serum2/bridge.py:28-138` (capture_v8_skeleton, build_v8_state, state_hash)
- `serum2/vst3_state.py:38-85` (wrap/unwrap)
- `serum2/evidence/harness.py:74-185` (render_arm, the center of gravity)
- `serum2/behavior/measurement/pitch.py:33-95` (F0 estimation)
- `serum2/evidence/kernels/*.py` (RMS, centroid, modulation kernels)

**WHAT IT SOLVES:**
- Real end-to-end Serum state mutation + audio render + measurement
- Baseline+treatment comparison with gate discipline (no "success" claim without measuring)
- Readback verification (get_parameters + comparison)
- Restoration verification (change back to original, verify readback matches)
- EvidenceRecord persistence for later claim derivation

### Layer 4: Semantic Routing (REUSE — correct separation of concerns)

**CURRENT PRODUCER wants:**
- Decide whether to execute via DawDreamer vs. Ableton MCP vs. refuse
- Avoid claiming capability when evidence is only historical (not fresh-qualified)

**REUSE THIS:**
- `serum2/producer/route_selection.py::RouteSelector.select_route()` (lines 147-227)
- `serum2/producer/contract_registry.py` (loads fresh 4.Q contracts)
- `serum2/compiler/mcp_intent.py::MCP_HOST_MAP` (7 semantic→VST3 parameter mappings for MCP route)

**EXACT FILES:**
- `serum2/producer/route_selection.py:57-227` (ExecutionRoute enum, EvidenceTier, select_route logic)
- `serum2/producer/contract_registry.py:34-62` (fresh contract loading)
- `serum2/compiler/mcp_intent.py:78-90` (MCP_HOST_MAP)

**WHAT IT SOLVES:**
- Architectural separation of Serum/Ableton routes
- Advisory-only recommendation (no authority granted; enforced by `test_route_selection_grants_no_authority`)
- Historical-evidence rejection (rule 5 enforcement)

### Layer 5: Knowledge & Intent (PARTIAL REUSE — mixed quality)

**CURRENT PRODUCER wants:**
- Extract control intent from YouTube transcripts
- Map intent (e.g., "make darker") to semantic targets (e.g., Filter.Cutoff down)
- Resolve ambiguities via context

**REUSE THIS:**
- `serum2/knowledge/` (54 modules covering extraction, normalization, intent bridging)
- `serum2/knowledge/step_5_3_source_acquisition.py` (YouTube ingestion)
- `serum2/knowledge/semantic_extraction.py` (intent parsing)
- `serum2/knowledge/target_resolution_context_aware.py` (resolve "darker" → Filter.Cutoff)
- `serum2/knowledge/step_6_10_episode_generation.py` (format episode records)

**BUT ALSO CONSIDER:**
- `producer-recreation/source/youtube_transcript_resolver.py` (better YouTube adapter with 8-tier language selection + fallback Whisper)
- `producer-recreation/source/fallback_transcribe.py` (Whisper ASR fallback for videos with no transcript track)

**EXACT FILES:**
- `serum2/knowledge/step_5_3_source_acquisition.py` (ingestion)
- `serum2/knowledge/target_resolution_context_aware.py` (intent→target resolution)
- `serum2/knowledge/step_6_8_contract_governed_execution.py` (execution end-to-end)
- For YouTube: **prefer** `producer-recreation/source/` over serum2/knowledge/ (more capable)

**WHAT IT SOLVES:**
- Knowledge normalization (deduplication, authority binding)
- Intent→target mapping (with context fallback to avoid false positives)
- Episode formatting (compatibility with episode_retrieval.py for learning loop)

### Layer 6: Episodes & Learning (REUSE — serum2 version is the real one)

**CURRENT PRODUCER wants:**
- Persist execution records for future learning
- Retrieve past episodes for same target to influence confidence
- Close the feedback loop

**REUSE THIS:**
- `serum2/qualification/` episode JSON schema (67 files provide reference)
- `serum2/producer/episode_retrieval.py::retrieve_relevant_episodes()` (lines 19-60)
- `serum2/producer/producer_brain.py::_retrieve_episodes()` (lines 305-345, uses episodes to adjust confidence)

**DO NOT reuse:**
- `producer-recreation/data/episodes/` (different schema, never read back)

**EXACT FILES:**
- `serum2/producer/episode_retrieval.py:19-60` (read-back logic)
- `serum2/qualification/ep_*.json` (example episode structure)
- `serum2/producer/producer_brain.py:305-345` (integration point)

**WHAT IT SOLVES:**
- Write-once, read-many episode persistence
- Learning loop closure (episodes inform future confidence advisory)
- Authority preservation (episodes are advisory-only per EPISODE_NOT_AUTHORITY invariant)

---

## 14. RECOMMENDED UNIFIED ARCHITECTURE

**Do NOT redesign from scratch. Merge the existing pieces correctly.**

### Current State

```
ESTABLISHED (serum2/):
├── compiler/ ✓ [targets, context, admission, kernel]
├── evidence/ ✓ [record, claim, contract, disposition, harness]
├── producer/ ✓ [route selection, producer brain, episode retrieval]
├── knowledge/ ✓ [YouTube ingestion, intent resolution, step 5-6 pipeline]
└── qualification/ ✓ [67 episode records, A3 harness, H0 self-tests]

DUPLICATE (producer-recreation/):
├── producer/authority/ [copy of compiler + evidence]
├── producer/brain/ [copy of producer + knowledge]
├── data/episodes/ [write-only, never read]
└── **NEW (actually useful)**:
    ├── source/ [better YouTube + Whisper fallback]
    ├── execution/serum_harness_adapter.py [integration]
    └── orchestration scripts (mixed quality)

LEGACY (experiments/):
├── step15_2_*.py [diagnostic patterns for target qualification]
├── step16_*.py [phase-specific evidence records]
├── 16_5_57c_injection/ [offline .als manipulation, Q9 failed]
└── Max/MSP harness [A0/A1 host probe, standalone]
```

### Unified Design (What to Actually Do)

**DO:**

1. **Delete producer-recreation/producer/authority/ and producer-recreation/producer/brain/**
   - They are redundant byte-for-byte copies of serum2/compiler + serum2/evidence + serum2/producer + serum2/knowledge
   - Maintenance burden with zero benefit

2. **Merge YouTube improvements into serum2/knowledge/**
   - Take `producer-recreation/source/youtube_transcript_resolver.py` (8-tier language selection, parameterized)
   - Take `producer-recreation/source/fallback_transcribe.py` (Whisper local ASR fallback)
   - Replace serum2/knowledge/youtube_source_ingestion.py with unified version
   - Consolidate fetch_youtube.py into step_5_3_source_acquisition.py

3. **Keep producer-recreation/producer/execution/serum_harness_adapter.py**
   - This is a legitimate integration layer bridging producer→serum2.evidence.harness
   - Move it to serum2/producer/serum_harness_adapter.py or serum2/compiler/kernel.py context

4. **Consolidate episode schemas**
   - Use serum2/qualification ep_*.json schema as the canonical format
   - Delete producer-recreation/data/episodes/ (inconsistent ad hoc schemas, write-only)
   - All producers (serum2, future producer-recreation orchestrators) write to serum2/qualification/ep_*.json
   - episode_retrieval.py already reads from there; learning loop is unified

5. **Fix evidence fabrication in producer-recreation/**
   - Delete producer-recreation/producer.py::recreate_reference() (hardcoded print-theater)
   - Delete producer-recreation/final_recreation.py::Ableton half (hardcoded verified:true)
   - Rewrite final_recreation.py to call real Serum harness (do) + defer Ableton via placeholder (don't fabricate)
   - Delete producer-recreation/test_real_example.py (fully fabricated demo)

6. **Integrate route selection into main flow**
   - serum2/producer/route_selection.py is new, untracked; add to main branch, test suite
   - Make it the decision point before kernel.construct_and_verify() (don't execute if route is REFUSE)
   - Clarify in documentation: route selection is advisory, not authoritative; admission gate remains the authority

7. **Expand SEMANTIC_TARGETS incrementally**
   - Use step15_2_*.py diagnostic patterns to qualify OSC2/3, LFO, Macro, Chorus/Delay/Reverb/Compressor one family at a time
   - For each target: baseline render → dead silence measure → gate inspection → interpret causality → if CAUSAL_VERIFIED → add to targets.py and mcp_intent.py
   - This is step 16.5.69 "unfinished work"; not changing current architecture, just completing it

**DO NOT:**

- Redesign the core compiler/evidence/harness layers (they work correctly)
- Create a new admission gate (admit() is sufficient and correct)
- Invent a new state codec (codec.py+bridge.py handle v5/v8 correctly)
- Bypass episode_retrieval.py for learning (it's the canonical loop)
- Use producer-recreation's duplicates of serum2 code (redundant, divergence risk)

---

## 15. FINAL ANSWER

### WHAT WE ALREADY HAVE

1. **Epistemically rigorous evidence/claim/contract system** — rule-enforced (witness recovery, disposition gating, status taxonomy, prerequisite verification)
2. **Proven DawDreamer harness** — full baseline+treatment render cycle with gate discipline, real audio measurement (FFT-based F0, RMS, centroid, modulation, etc.)
3. **Sound compiler architecture** — semantic targets, context resolution, strict admission gate, grounding conditions, execution policy
4. **Real producer feedback loop** — goal → intent → planning → admission → execution → episode → learning closure
5. **Knowledge ingestion pipeline** — YouTube transcripts → semantic extraction → intent→target resolution → episode records
6. **Route selection advisory system** — architectural separation of DawDreamer/Ableton control planes, historical-evidence rejection
7. **Serum state codec** — full round-trip (load `.SerumPreset` v5 / VST3 v8 → mutate via CBOR → persist + readback)

### WHAT IS ACTUALLY WORKING

1. **Env1.Attack + Env1.Release** — CAUSAL_VERIFIED, both executed via real harness.run(), 67 episode records produced, evidence closed-loop (episode_retrieval.py reads them back)
2. **DawDreamer/CBOR control plane** — tested end-to-end via test_evidence_baseline_context.py, test_processor_state.py, test_osc1_volume_producer_construction.py
3. **Structural mutation** — 20 other targets (Env1.Decay, Env1.Sustain, Oscillator/Filter/EQ parameters) proven to load, persist, and restore without crash; just not yet proven for behavioral causality
4. **Evidence disposition gates** — integrated, tested, preventing historical evidence from being laundered into new execution decisions
5. **Knowledge→intent→target pipeline** — tested for Env1.Attack/Release; produces intent chains linked to specific semantic targets with context-aware resolution

### WHAT EXISTS BUT IS UNUSED

1. **Byte-identical copy of entire compiler/evidence/producer/knowledge architecture** in `producer-recreation/` (redundant, risk of divergence)
2. **70+ experimental diagnostic scripts** (step15_2_*.py, step16_*.py, g1–g8 series) — proven patterns for target qualification that are not integrated into main H1 harness
3. **Max/MSP VST3 parameter probe** (experiment_A_harness) — standalone A0/A1 host audit harness, never called by Python code
4. **Historical 30-contract pickle** (experiments/_capability_contracts.pkl) — prior art, useful if requalification is unblocked
5. **Offline `.als` manipulation code** — Q7c successful injection methodology documented but Q9 reopen corruption closed this path

### WHAT IS DUPLICATED

1. **Entire compiler/evidence/producer/knowledge stacks** — serum2/compiler/ ≡ producer-recreation/producer/authority/compiler/, etc. (7+22+12=41 files, 3× triplication of route_selection.py)
2. **YouTube transcript ingestion** — serum2/knowledge/youtube_source_ingestion.py vs. producer-recreation/source/ (different maturity, no integration)
3. **Episode storage** — serum2/qualification/ep_*.json (rich schema, read-back loop working) vs. producer-recreation/data/episodes/*.json (ad hoc, never read)

### WHAT IS MISSING

1. **Fresh CAUSAL_VERIFIED contracts for 20 other semantic targets** — blocked by step 16.5.69 (unfinished requalification harness)
2. **Ableton MPC execution in Python** — mcp_intent.py advisory layer exists, but no real `set_device_parameter` call anywhere in code (MCP tools only callable by Claude agents, not .py scripts)
3. **LFO/Macro/Full FX semantic vocabulary** — not in SEMANTIC_TARGETS; exists in historical pickle only
4. **Processor-state injection** — Q9 experiment proved reopen corruption; closed path per architecture decision
5. **Module topology mutations** — no code to enable/disable OSC2-3, select different filters, configure matrix routing
6. **Resource loading** — no code to swap wavetables/samples
7. **Ableton real execution from within producer code** — fabrication present in producer-recreation/{producer.py, final_recreation.py}

### WHAT SHOULD BE REUSED

1. **serum2/evidence/** — admission gate, record/claim/contract, disposition filtering, witness recovery
2. **serum2/compiler/** — semantic targets, context resolution, grounding conditions
3. **serum2/evidence/harness.py::render_arm()** — THE place to call DawDreamer; no alternatives
4. **serum2/producer/episode_retrieval.py** — read-back learning loop
5. **serum2/knowledge/step_5_3_*.py + step_6_*.py** — knowledge pipeline (use in serum2, not duplicates)
6. **producer-recreation/source/** YouTube adapter — REPLACE serum2/knowledge/youtube_source_ingestion.py with this better version
7. **Step 15/16 diagnostic patterns** — basis for batching new target qualification (reuse in step 16.5.69 work)

### WHAT SHOULD NOT BE REBUILT

- Compiler layers (targets.py, context.py, admission.py, kernel.py) — already correct
- Evidence system (record, claim, contract, disposition) — already correct
- DawDreamer harness — only place that can call Serum; building another breaks unity
- Episode retrieval loop — already closes the learning feedback
- State codec (CBOR/zstd/XferJson) — already proven by bridge.py and tests
- Route selection advisory logic — already separates control planes correctly

---

## CONCLUSION

**Current state: Architecture is sound, implementation of core layers is correct, but deployment is bottlenecked and fabrication undermines integrity claims.**

The codebase is **closest to its stated goal (trustworthy AI music producer) in the evidence/claim/contract layer, DawDreamer execution path, and producer brain feedback loop**. The **integrity damage is concentrated in producer-recreation/ orchestration scripts** (fabricated Ableton evidence) and **duplicated code** (confuses status, increases maintenance burden).

**Realistic assessment:** This codebase can **currently and reliably control 2 Serum parameters** (Env1.Attack, Env1.Release) via proven DawDreamer execution. It has **proven infrastructure for 20 others** (structural mutation works; behavioral causality not yet demonstrated for current context). It has **designed but unexecuted Ableton MCP integration** (mcp_intent.py advisory layer, 7 target mappings, but no real execution from Python). It has **clear path to full 127-parameter control** (step 16.5.69 requalification work, step 16.5.59 Ableton vertical slice) but neither is finished.

**How close to human-like control:** Cannot responsibly quantify without defining "human-like" (what percentage of Serum's control space should be targetable? should be automated? should require human interaction?). Observable facts:
- 2/22 semantic targets are CAUSAL_VERIFIED and working
- 20/22 are structurally-only (state-proven, causality-unproven)
- 127/127 raw VST3 parameters exist; 7/127 wired to semantic vocabulary
- 0% Ableton MCP execution in code (designed, not implemented)
- Full control plane is architecturally sound but materially incomplete

---

**END OF FORENSIC INVENTORY**

Generated 2026-09-13 | Status: Read-only, no modifications made | All findings from inspection of actual code, not documentation | Evidence-backed throughout with file:line citations
