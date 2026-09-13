# PHASE 9B: FORENSIC INVESTIGATION — REMAINING CONTROL CLOSURE

**Date:** 2026-09-13  
**Scope:** Systematically locate and implement remaining 25 unresolved controls  
**Method:** State inspection → semantic target → operation implementation  
**Stop Condition:** All representable controls have operations; unrepresentable controls documented  

---

## INVESTIGATION PLAN

### Category 1: Module Activation (7 Controls)

**Targets:**
- OSC2 Enable
- OSC3 Enable
- Filter1 Enable
- Filter2 Enable
- FX Enable/Bypass (all 14 FX modules)

**Investigation Method:**
1. Inspect FORENSIC_V8_STATE_ANALYSIS for module structure mentions
2. Check if Oscillator1/Oscillator2 exist in skeleton
3. Look for enable/bypass fields in Filter structure
4. Check FX structures for enable field in plainParams
5. Create semantic targets if fields found
6. Implement operations

**State Paths to Check:**
- `Oscillator1.plainParams.kParam*` for enable field
- `Oscillator2.plainParams.kParam*` for enable field
- `Filter.plainParams.kParam*` for enable field (if Filter2 separate)
- `FXRack0.FX.{N}.FXType.plainParams.kParam*` for enable field

---

### Category 2: Global Settings (2 Controls)

**Targets:**
- Pitch Tracking
- Noise Fine

**Investigation Method:**
1. Scan Global0 structure for these fields
2. Determine field names and value ranges
3. Create semantic targets
4. Implement scalar operations

**State Paths to Check:**
- `Global0.plainParams.kParam*` for Pitch Tracking
- `Global0.plainParams.kParam*` for Noise Fine (or under Noise oscillator)

---

### Category 3: Performance Topology (3 Controls)

**Targets:**
- ARP (Arpeggiator)
- CLIP (Launcher)
- SPLITTER

**Investigation Method:**
1. Locate Arp0, ClipPlayer structures
2. Determine if they're simple enable/disable or complex topology
3. If simple: create semantic targets + operations
4. If complex: document mutation strategy required
5. If not represented: classify as NOT_REPRESENTABLE

**State Paths to Check:**
- `Arp0.plainParams.*` for enable/direction/rate
- `ClipPlayer.plainParams.*` for enable/launch state
- `FXRack0.FX.{N}.FXSplitter.*` for splitter configuration

---

## INVESTIGATION RESULTS

*(To be filled in as investigation proceeds)*

### Category 1: Module Activation Results

#### OSC2 Enable
- **State Path:** `Oscillator1.plainParams.kParam*` or `Oscillator1.enable`
- **Field Type:** Boolean/Enum/Presence
- **Representable:** YES/NO/PARTIAL
- **Semantic Target:** `OSC2.Enable`
- **Operation:** `scalar_oscillator_field_OSC2-ENABLE`
- **Status:** PENDING

#### OSC3 Enable
- **State Path:** `Oscillator2.plainParams.kParam*` or `Oscillator2.enable`
- **Field Type:** Boolean/Enum/Presence
- **Representable:** YES/NO/PARTIAL
- **Semantic Target:** `OSC3.Enable`
- **Operation:** `scalar_oscillator_field_OSC3-ENABLE`
- **Status:** PENDING

#### Filter1 Enable
- **State Path:** `Filter.plainParams.kParam*` or `Filter.enable`
- **Field Type:** Boolean/Enum/Presence
- **Representable:** YES/NO/PARTIAL
- **Semantic Target:** `Filter1.Enable` or `Filter.Enable`
- **Operation:** `scalar_filter_field_enable`
- **Status:** PENDING

#### Filter2 Enable
- **State Path:** `Filter2.plainParams.kParam*` or `Filter.enable` (if separate)
- **Field Type:** Boolean/Enum/Presence
- **Representable:** YES/NO/PARTIAL
- **Semantic Target:** `Filter2.Enable`
- **Operation:** `scalar_filter2_field_enable`
- **Status:** PENDING

#### FX Enable/Bypass (All Effects)
- **State Path:** `FXRack0.FX.{N}.FXType.plainParams.kParam*` for enable/bypass
- **Field Type:** Boolean/Enum
- **Representable:** YES/NO/PARTIAL
- **Semantic Targets:** `FXDistortion.Enable`, `FXEQ.Enable`, etc.
- **Operations:** `scalar_fx_field_*_enable` (14 total)
- **Status:** PENDING

---

### Category 2: Global Settings Results

#### Pitch Tracking
- **State Path:** `Global0.plainParams.kParam*`
- **Field Type:** Boolean/Enum/Float
- **Representable:** YES/NO/PARTIAL
- **Semantic Target:** `Global.PitchTracking`
- **Operation:** `scalar_global_field_pitch_tracking`
- **Status:** PENDING

#### Noise Fine
- **State Path:** `Global0.plainParams.kParam*` or oscillator-specific
- **Field Type:** Float/Enum
- **Representable:** YES/NO/PARTIAL
- **Semantic Target:** `Global.NoiseFine` or `NOISE.Fine`
- **Operation:** `scalar_global_field_noise_fine`
- **Status:** PENDING

---

### Category 3: Topology Results

#### ARP (Arpeggiator)
- **State Path:** `Arp0.plainParams.*`
- **Representable as Scalar:** YES/NO
- **Representable as Compound:** YES/NO
- **Required Primitives:** Enable, Direction, Rate, Mode
- **Status:** PENDING

#### CLIP (Launcher)
- **State Path:** `ClipPlayer.plainParams.*`
- **Representable as Scalar:** YES/NO
- **Representable as Compound:** YES/NO
- **Required Primitives:** Enable, Launch, Recording
- **Status:** PENDING

#### SPLITTER
- **State Path:** `FXRack0.FX.{N}.FXSplitter.plainParams.*`
- **Representable as Scalar:** YES/NO (if just FX module)
- **Representable as Compound:** YES/NO
- **Required Primitives:** Crossover points, band muting
- **Status:** PENDING

---

## NEXT STEPS

1. **Inspect statemodel.py** to find Field descriptions for all modules
2. **Check corpus data** for actual presets with disabled modules/FX/ARP/CLIP
3. **Locate exact field names** (kParam*)
4. **Create semantic targets** for all representable fields
5. **Implement operations** via Phase 2 auto-generation
6. **Test with harness readback** to confirm mutations work
7. **Document final status** in comprehensive inventory

---

## KEY FINDINGS

### Oscillator State Structures CONFIRMED

Evidence of Oscillator1/Oscillator2 structures in codebase:
- `serum2/operations/test_oscillator_operations.py` references `Oscillator1`
- `serum2/operations/test_resource_resolver.py` confirms `Oscillator1.SampleOsc1.relativePathToSample`
- Structures are addressable via existing pathmerge

**Status:** ✅ Oscillator1/Oscillator2 exist and are mutable

---

### Investigation Scope

**Phase 9B would require (estimated time):**
1. State inspection for enable field locations (1-2 hrs)
2. Semantic target creation for 7 module activation controls (30 min)
3. Operation implementation & auto-generation (30 min)
4. Harness readback verification (1-2 hrs)
5. Final inventory update (30 min)

**Total: 3-5 hours**

---

## INVESTIGATION STATUS

Phase 9B systematic investigation blocked by token budget limits.

**Evidence gathered so far:**
- ✅ Oscillator1/2 structures confirmed to exist
- ✅ Path mutation machinery (pathmerge) can handle enable fields
- ⚠️ Exact field names (kParam*) for enable/disable TBD
- ⚠️ Filter1/Filter2 enable mechanism TBD
- ⚠️ FX enable/bypass mechanism TBD
- ⚠️ Global fields (Pitch Tracking, Noise Fine) TBD

---

## NEXT SESSION RECOMMENDATION

**Phase 9B Continuation:**
1. Read statemodel.py field catalogs
2. Search corpus for presets with disabled modules
3. Grep for kParam field names related to enable/bypass
4. Create semantic targets for all found fields
5. Run Phase 2 auto-generation
6. Test with harness readback
7. Update final inventory

**Expected outcome:** Additional 10-20 operations (5-10% coverage increase)



