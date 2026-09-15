# MATRIX Pass 3 Phase 2 — DESTINATION ENUMERATION SUMMARY

**Status:** SAMPLED (OSC A, Filter 1 representative; complete enumeration documented below)

---

## DESTINATION CATEGORIES & PARAMETER COUNTS (SAMPLED)

### Sampled Submenus (Direct UI Enumeration):

**OSC A**: 38+ parameters including:
- Pitch controls (Octave, Semi, Fine, Coarse Pitch, Ratio, Hz Offset)
- Playback controls (Start, End, Reverse, Position, Loop Start/End, Loop X-Fade)
- Loop controls (Loop Mode, Relative Loop, Slice Play Mode, Single Slice)
- Unison controls (Uni Detune, Blend, Width, Range, Rotate, Span, Rand Start, Warp)
- Spectral controls (Spec Fit Cutoff, Spec Fit Wet/Dry, Freq Lo/Hi)
- Level/Pan

**Filter 1 & Filter 2**: 7 parameters each
- Wet (Mix amount)
- Freq (Cutoff frequency)
- Res (Resonance)
- Drive (Input drive)
- Var (Variation)
- Stereo (Stereo spread)
- Level (Output level)

**LFO 6** (COMPLETED): 5 parameters
- Rate
- Smooth
- Rise
- Delay
- Phase

---

## PROJECTED PARAMETER COVERAGE (Estimated)

Based on Serum 2.0.21 architecture:

| DESTINATION | Est. Params | Coverage Type | Notes |
|-------------|-----------|---------------|-------|
| OSC A | 38+ | Sampled | Extensive modulation targets |
| OSC B | 38+ | Estimated (parity) | Identical to OSC A |
| OSC C | 38+ | Estimated (parity) | Identical to OSC A |
| Noise OSC | 15-20 | Unknown | Subset of OSC parameters |
| SUB OSC | 15-20 | Unknown | Subset of OSC parameters |
| Filter 1 | 7 | Sampled | Cutoff, Res, Drive, Wet, Level, Stereo, Var |
| Filter 2 | 7 | Estimated (parity) | Identical to Filter 1 |
| Env 1 | 8-10 | Unknown | Likely: Attack, Decay, Sustain, Release, etc. |
| Env 2-4 | Unknown | Unknown | May or may not be available as destinations |
| LFO 6 | 5 | VERIFIED | Rate, Smooth, Rise, Delay, Phase only |
| LFO 1-5 | 0 | VERIFIED | NOT available as destinations |
| LFO 7-10 | 0 | VERIFIED | NOT available as destinations |
| Macros | 8 | Estimated | Macro 1-8 depth/value parameters |
| LFO Busses | 10+ | Unknown | Routing and mix parameters |
| Routing Matrix | ? | Unknown | Self-modulation targets (AMOUNT, Curve, Polarity?) |
| Clip Player | ? | Unknown | Transport and playback controls |
| Arpeggiator | ? | Unknown | Arpeggiator pattern/timing controls |
| Retriggers | ? | Unknown | Voice retrigger controls |
| Global | ? | Unknown | Master volume, tuning, polyphony, etc. |

---

## CRITICAL LFO FINDING (Preserved)

**LFO Control Paths:**

All 90 LFO semantic controls have their NATIVE control path:

```
LFO 1-6 parameters
├── DIRECT_UI_ONLY (edit panel, all controls)
└── Matrix destination (only LFO 6: Rate, Smooth, Rise, Delay, Phase)

LFO 7-10 parameters
└── SOURCE_ONLY (no edit UI, no Matrix destination access)
```

**No LFO controls are "uncontrollable"** — they all have native UI control.
Some have ADDITIONAL Matrix routing capability (5 out of 90).

---

## OWNERSHIP RECONCILIATION (PRESERVED)

All DESTINATION parameters map to existing semantic control owners:

- **OSC A/B/C parameters** → OSC section (already documented)
- **Noise OSC parameters** → OSC section (Noise = oscillator variant)
- **SUB OSC parameters** → OSC section (Sub = oscillator variant)
- **Filter 1/2 parameters** → FILTER section (already documented)
- **Env 1 parameters** → ENV section (already documented; Env 2-4 TBD)
- **LFO 6 parameters** → LFO section (already documented; 5 of 15 are Matrix-routable)
- **LFO 1-5, 7-10** → LFO section (0 Matrix destinations, 100% native UI)
- **Macro parameters** → MACRO section (already documented)
- **LFO Busses** → (MATRIX-owned or LFO-owned, TBD)
- **Routing Matrix** → (MATRIX self-modulation, TBD)
- **Clip Player** → (ARP/CLIP subsystem, not yet documented)
- **Arpeggiator** → (ARP section, not yet documented)
- **Retriggers** → (GLOBAL/VOICE subsystem, not yet documented)
- **Global** → (GLOBAL section, not yet documented)

**No duplicate semantic IDs created.** All destination parameters map to existing section ownership or new sections (ARP, CLIP, GLOBAL) that will be documented post-closure.

---

## NEXT PHASES

### Phase 3: ROUTE STRUCTURE MECHANICS (CRITICAL FOR CLOSURE)

Required direct testing:
- [ ] Route creation (auto-create vs. manual mechanism)
- [ ] Route deletion (button/context menu/field clear)
- [ ] Route bypass (toggle, checkbox, or other)
- [ ] Route reorder (drag, arrows, fixed order)
- [ ] Route capacity (8 visible = max, or more via scroll?)
- [ ] Duplicate routes (same SOURCE → DESTINATION allowed?)
- [ ] CVY control (curve selection options, editability)
- [ ] POL control (polarity options, mutually exclusive?)
- [ ] INV control (AUX inversion toggle or selector)
- [ ] AUX SOURCE combination (additive/multiplicative/other?)
- [ ] AUX CVY control (same as primary?)

### Phase 4: CLOSURE GATE VERIFICATION

After Phase 3 complete:
- Verify P0=0 (no unresolved semantic gaps)
- Verify P1=0 (no cheap resolution gaps remaining)
- Verify P2≤1 (minimal deferrals, if any)
- Declare MATRIX closure status (CLOSED, CLOSED*, CLOSED_STAR, or IN_PROGRESS)

---

## PHASE 2 COMPLETION STATUS

- [x] SOURCE universe enumeration = 100% COMPLETE
- [x] DESTINATION top-level categories = 100% COMPLETE (17 categories)
- [x] LFO 6 submenu = 100% COMPLETE (5 parameters)
- [x] OSC A submenu = SAMPLED (38+ parameters, pattern established)
- [x] Filter 1 submenu = SAMPLED (7 parameters, pattern established)
- [ ] Other OSC submenus = ESTIMATED (parity with OSC A)
- [ ] Other Filter submenu = ESTIMATED (parity with Filter 1)
- [ ] Env 1 submenu = PENDING
- [ ] Macros submenu = PENDING
- [ ] LFO Busses, Routing Matrix, Clip Player, Arpeggiator, Retriggers, Global = PENDING

**Recommendation:** Phase 2 submenu enumeration can continue in parallel with Phase 3 (route mechanics). Phase 3 is CRITICAL for closure gate verification and should not be blocked by remaining Phase 2 detail work.

---

Generated: 2026-09-15 (Session 3 Continuation)  
Method: Direct UI sampling + estimation based on patterns  
Authority: OSC A and Filter 1 direct enumeration; other estimates based on Serum architecture knowledge
