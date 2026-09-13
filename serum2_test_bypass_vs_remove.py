"""DawDreamer inspection: Actual Serum v8 state for BYPASS vs REMOVE

This script uses DawDreamer to:
1. Load a Serum instance with an FX effect
2. Read the v8 state (effect active)
3. Bypass the effect via UI
4. Read the v8 state (effect bypassed)
5. Remove the effect
6. Read the v8 state (effect removed)

Show the ACTUAL state differences.
"""

import json
import sys
from pathlib import Path

# Try to use DawDreamer if available
try:
    import dawdreamer as dw
    from serum2.evidence import codec
    print("✓ DawDreamer available")
except ImportError:
    print("✗ DawDreamer not available - cannot do real state inspection")
    print("Proceeding with theoretical analysis only")
    sys.exit(0)

print("\n" + "="*70)
print("SERUM STATE INSPECTION: BYPASS vs REMOVE")
print("="*70)

# Load a simple Serum instance
try:
    print("\n1. Loading Serum instance...")
    engine = dw.AudioEngine()
    engine.set_sample_rate(44100)
    engine.set_buffer_size(512)

    synth = engine.add_synth("synth", "/Program Files/VstPlugins/Serum_x64.vst3")
    print("   ✓ Serum instance loaded")

    # Get initial v8 state (should have empty or default FX)
    print("\n2. Reading INITIAL v8 state...")
    initial_state = synth.plugin.get_state()
    print(f"   State type: {type(initial_state)}")
    print(f"   State size: {len(initial_state) if isinstance(initial_state, bytes) else 'N/A'}")

    # Decode state if CBOR
    try:
        import cbor2
        decoded = cbor2.loads(initial_state)
        print(f"   ✓ State is CBOR-encoded")

        # Look for FXRack structure
        if "FXRack0" in decoded:
            print(f"   ✓ Found FXRack0")
            rack = decoded["FXRack0"]
            if "FX" in rack:
                fx_array = rack["FX"]
                print(f"   Initial FX array length: {len(fx_array)}")
                if len(fx_array) > 0:
                    print(f"   First FX: {list(fx_array[0].keys())}")
    except:
        print(f"   Could not decode CBOR state")

    print("\nNOTE: Full state inspection requires:")
    print("  - Serum instance that allows parameter/state writes")
    print("  - UI automation for bypass toggle")
    print("  - Codec library for CBOR decoding")
    print("\nDeferring to forensic evidence...")

except Exception as e:
    print(f"   ✗ Error: {e}")
    print("   Proceeding with forensic analysis only")

print("\n" + "="*70)
print("FORENSIC EVIDENCE ANALYSIS")
print("="*70)

print("""
From existing code and analysis:

1. MODULATION ROUTES use bypass:
   - ModSlot{N}.bypass = boolean field
   - Presence in ModSlot0-63 array = route is defined
   - bypass=true → processing disabled but structure preserved
   - bypass=false → processing enabled

2. FILTERS appear to use bypass via 'default':
   - VoiceFilter0.plainParams='default' suggests bypass/inactive
   - But actual bypass field (if any) unknown

3. FX EFFECTS:
   - No explicit kParamBypass found in current catalog
   - Could be:
     A. Stored in plainParams.kParamBypass (not yet discovered)
     B. Represented by array removal (current implementation)
     C. Represented by presence/absence like ModSlots
     D. Represented through another mechanism

RECOMMENDATION:
==================

Before implementing FX bypass operations, must do:

1. Inspect actual SERUM v8 structure for:
   - FXRack0.FX[N].kParamBypass or similar
   - FXRack0.FX[N].bypass field
   - Any enable/disable flag in effect plainParams

2. Compare with ModSlot pattern:
   - If FX follow ModSlot pattern: bypass field exists
   - If different: determine actual mechanism

3. Verify hypothesis with:
   - Preset corpus inspection (if decodable)
   - DawDreamer state snapshot (if accessible)
   - Serum documentation (if available)

CORRECT OPERATIONS (pending verification):
===========================================

enable_effect(bus, slot):
  if bypass field exists:
    FXRack{R}.FX.{N}.kParamBypass = false
  else:
    (verify alternative mechanism)

bypass_effect(bus, slot):
  if bypass field exists:
    FXRack{R}.FX.{N}.kParamBypass = true
  else:
    (verify alternative mechanism)

remove_effect(bus, slot):
  Remove element from FXRack{R}.FX array (current approach)
  This is TOPOLOGY change, not parameter change

These are THREE separate operations.
""")

print("\n" + "="*70)
print("CURRENT STATE: UNRESOLVED")
print("="*70)
print("""
Until bypass mechanism is verified, the FX-FULL implementation must:

1. NOT assume disable_effect = remove_effect
2. Implement bypass as separate operation with correct semantics
3. Test that bypass preserves:
   - Effect type
   - Effect parameters
   - Effect ordering
   - Resource references
   - Bus assignment

4. Test that remove_effect:
   - Changes array topology
   - Shifts subsequent effects
   - Cannot preserve parameters (effect is gone)
""")
