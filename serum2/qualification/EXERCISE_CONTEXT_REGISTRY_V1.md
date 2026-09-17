# Exercise Context Registry V1

**Authoritative, persistent source of truth for proven Serum causal-qualification
exercise contexts.** Future qualification runs and future chats must read
`EXERCISE_CONTEXT_REGISTRY_V1.json` first, instead of rediscovering contexts.

This registry records causal **qualification** evidence — a separate concern
from the frozen execution-coverage registry (`SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json`,
frozen at commit `d512575`). It does not modify or reopen that registry.

## What an exercise context is

An exercise context is a set of **host-level VST3 parameters** (e.g. `Filter 1 On`,
`B Enable`) applied identically to both the baseline and treatment render arms,
via `synth.set_parameter()`, *before* the single target mutation and *before*
rendering. It activates/gates the module under test. It is qualification-time
setup, not a mutation, and it is **not** part of execution-binding identity —
it only exists to make a capability's causal effect observable.

## PROVEN (6 — golden regression set)

| capability_id | exercise_context | mutation | metric | delta |
|---|---|---|---|---|
| Filter1.Cutoff | `Filter 1 On=1.0` | `VoiceFilter0.plainParams.kParamFreq` → 0.9 | spectral_centroid_hz | +2684.3 Hz |
| OSC1.Level | (none — A Enable defaults ON) | host_param `A Level` 0.25→1.0 | overall_rms_db | +24.0 dB |
| OSC2.Level | `B Enable=1.0` | host_param `B Level` 0.0→1.0 | overall_rms_db | +8.8 dB |
| OSC3.Level | `C Enable=1.0` | host_param `C Level` 0.0→1.0 | overall_rms_db | +8.8 dB |
| Env1.Attack | (none — no prerequisites) | `Env0.plainParams.kParamAttack` → 0.9 | overall_rms_db | -2.2 dB |
| FXEQ.Freq1 | (none — FXEQ has no wet/dry gate) | `FXRack0.FX.0.FXEQ.plainParams.kParamFreq1` → 8000 Hz (Altar preset FX injected) | spectral_centroid_hz | +7622.9 Hz |

Plus one **structural-only** proof (not an audio causal proof):

| capability_id | mechanism | status |
|---|---|---|
| MODULATION_ROUTE.LFO_TO_BUS_STRUCTURAL | `compound_create_modulation_route` | PROVEN (structural persistence via real Serum round-trip only — no render/measurement step) |

## BLOCKED (documented, not forced)

| capability_id | reason |
|---|---|
| Filter2.Cutoff | `Filter 2 On=1.0` gate confirmed applied; render succeeds; zero spectral delta. `FILTER_P1_RESOLUTION.md` (direct UI inspection) confirms Filter 2 shows no visible response curve even when "on" — an additional routing/mode parameter is required and has not been identified. |
| Env2.Attack | Mutation mirrors the proven Env1.Attack path exactly; render succeeds; zero RMS delta. Env1 (UI "Env 2") is not routed to an audible destination by default. No modulation-routing exercise context identified yet. |
| Filter1.Resonance | Documented exercise context applied; zero delta this run vs. a documented expectation of +2.74 dB elsewhere in the repo (`a3_exercise_contexts.py`). Needs re-verification, not forcing. |
| OSC1.Detune / OSC2.Detune | `VoiceOsc0`/`VoiceOsc1` path family is suspect — other repo evidence (`A_SEED_EXPERIMENT_04`) shows this family returns `None` (nonexistent path) for the analogous Level field. Needs path re-verification before reclassification. |
| Env1.Release / Filter1.Drive | Correct direction, magnitude below threshold (0.3 dB vs 0.5 dB threshold) — likely a stimulus/measurement-window issue, not a broken mechanism. |
| LFO1.Rate | Expected finding: LFO rate has no audible effect without an active modulation-route destination. Requires the `MODULATION_ROUTE` fixture as a prerequisite, then a render+measurement step that does not yet exist. |

## Fixtures

See `serum2/qualification/fixtures/` — one reproducible fixture module per
PROVEN capability family. Fixtures are only created where real evidence
supports them (no `FILTER2_ACTIVE` or `ENV2_ACTIVE` fixture exists, by design).

## Consuming the registry

`serum2/qualification/behavioral_seed_batch.py` loads `TargetDef` entries
whose `status="PROVEN"` from this registry via
`load_targets_from_registry()`, instead of hard-coding the golden six.
BLOCKED entries remain declared in the registry for traceability but are not
re-run as if new — they must not be silently promoted to `CAUSAL_VERIFIED`.
