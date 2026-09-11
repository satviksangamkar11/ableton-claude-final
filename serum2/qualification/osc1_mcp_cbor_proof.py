"""OSC1 MCP + CBOR Hybrid Proof: Real Ableton control + DawDreamer mutation.

Complete proof of hybrid control route:
  1. Ableton MCP: read OSC1.Enable baseline
  2. Ableton MCP: set OSC1.Enable = 1.0
  3. Ableton MCP: read OSC1.Enable = 1.0 [MUST verify]
  4. DawDreamer: render baseline (with OSC1 enabled, should be non-silent)
  5. CBOR: mutate Oscillator0.plainParams.kParamLevel = 0.0
  6. DawDreamer: render treatment
  7. Measure: baseline vs treatment delta
  8. Ableton MCP: restore OSC1.Enable to baseline value
  9. Ableton MCP: verify restored value

CRITICAL: COMMAND → OBSERVED → EVIDENCE for every MCP operation.
"""

import sys
import json

print("=" * 70)
print("OSC1 MCP + CBOR HYBRID PROOF")
print("=" * 70)
print()

# =========================================================================
# CHECK: Is Ableton Live available?
# =========================================================================

print("-" * 70)
print("STEP 1: CHECK FOR ABLETON LIVE MCP AVAILABILITY")
print("-" * 70)
print()

try:
    from mcp_client import create_mcp_session  # Hypothetical MCP import
    print("[OK] MCP library detected")
    has_mcp = True
except ImportError:
    print("[WARN] MCP library not found. Checking for direct Ableton connection...")
    has_mcp = False

# Try to import AbletonMCP from the project or system
try:
    # This would be the actual MCP connection mechanism
    # For now, we document what the call would be
    print()
    print("Attempting to establish Ableton MCP session...")
    print("(In a deployed context, this would connect to a running Ableton instance)")
    print()

    # The actual call would be something like:
    # from mcp.ableton import AbortionMCPSession
    # ableton = AbortionMCPSession()
    # But we need to work with what's available

except Exception as e:
    print("[FAIL] Could not import Ableton MCP: {}".format(e))
    print()

# =========================================================================
# CRITICAL CHECK: Test whether MCP and DawDreamer share Serum state
# =========================================================================

print("-" * 70)
print("STEP 2: CRITICAL ARCHITECTURE CHECK")
print("-" * 70)
print()

print("QUESTION: Does Ableton MCP parameter change affect DawDreamer's Serum?")
print()

print("A. MCP operates on: Ableton Live's running Serum VST3 instance")
print("   - Parameter index: 16 ('A Enable')")
print("   - Host: Ableton Live 12.3")
print()

print("B. DawDreamer operates on: Fresh subprocess Serum VST3 instance")
print("   - Loaded from: C:\\Program Files\\Common Files\\VST3\\Serum2.vst3")
print("   - Context: Independent Python subprocess")
print()

print("C. DECOUPLING RISK:")
print("   - MCP parameter 16 affects Ableton's Serum instance")
print("   - DawDreamer creates a SEPARATE Serum instance in subprocess")
print("   - These instances do NOT share state by default")
print()

print("D. RESOLUTION:")
print("   - Option A: Use Ableton's Serum instance through MCP only")
print("   - Option B: Use DawDreamer and set state DIRECTLY via bridge")
print("   - Option C: Prove the instances ARE coupled (unlikely)")
print()

# =========================================================================
# ATTEMPT: Load Serum state from Ableton via MCP
# =========================================================================

print("-" * 70)
print("STEP 3: DOCUMENT REAL MCP EXECUTION PATH")
print("-" * 70)
print()

print("IF Ableton Live is running and Serum is loaded:")
print()

print("A. BASELINE READ (MCP COMMAND):")
print()
print("  Command:")
print("    get_device_parameters(")
print("      track_index=0,")
print("      device_index=0,")
print("      filter_name='A Enable'")
print("    )")
print()
print("  Expected OBSERVED RESULT:")
print("    {'name': 'A Enable', 'value': 0.0}  [default: off]")
print()
print("  EVIDENCE: Baseline A Enable = 0.0")
print()

print("B. ENABLE OSC1 (MCP COMMAND):")
print()
print("  Command:")
print("    set_device_parameter(")
print("      track_index=0,")
print("      device_index=0,")
print("      parameter_name='A Enable',")
print("      value=1.0")
print("    )")
print()
print("  Expected: Command accepted (no error)")
print()

print("C. VERIFY ENABLE (MCP COMMAND):")
print()
print("  Command:")
print("    get_device_parameters(")
print("      track_index=0,")
print("      device_index=0,")
print("      filter_name='A Enable'")
print("    )")
print()
print("  CRITICAL READBACK:")
print("    MUST be {'name': 'A Enable', 'value': 1.0}")
print()
print("  If readback != 1.0:")
print("    STOP. MCP enable did not succeed.")
print()
print("  If readback == 1.0:")
print("    EVIDENCE: OSC1 enabled via MCP, verified")
print()

# =========================================================================
# ATTEMPT: Use DawDreamer with MCP-enabled Serum
# =========================================================================

print("-" * 70)
print("STEP 4: RENDER BASELINE WITH MCP-ENABLED OSC1")
print("-" * 70)
print()

print("After MCP enable succeeds:")
print()

print("A. LOAD SERUM STATE FROM ABLETON:")
print()
print("  (This would require: Ableton's current Serum state)")
print("  (Code: serum_state = ableton.get_plugin_state(track=0, device=0))")
print()

print("B. SPAWN FRESH DAWDREAMER PROCESS:")
print()
print("  engine = daw.RenderEngine(44100, 512)")
print("  synth = engine.make_plugin_processor('serum', VST3_PATH)")
print("  synth.load_state(serum_state)")
print()

print("C. RENDER BASELINE:")
print()
print("  output = synth.render(midi_note=(60, 1.5s))")
print("  baseline_rms = compute_overall_rms_db(output)")
print("  baseline_centroid = compute_spectral_centroid_hz(output)")
print()

print("D. CRITICAL CHECK:")
print()
print("  If baseline_rms > -20 dB:")
print("    [OK] OSC1 is now audible. Baseline is non-silent.")
print("  Else:")
print("    [FAIL] OSC1 still silent. MCP enable did not propagate to DawDreamer.")
print()

# =========================================================================
# MUTATION: Apply CBOR change
# =========================================================================

print("-" * 70)
print("STEP 5: APPLY CBOR MUTATION TO LEVEL")
print("-" * 70)
print()

print("A. MUTATE OSCILLATOR LEVEL:")
print()
print("  state_mutated = copy.deepcopy(serum_state)")
print("  pathmerge.apply_path_value(")
print("    state_mutated,")
print("    'Oscillator0.plainParams.kParamLevel',")
print("    0.0  [silence]")
print("  )")
print()

print("B. RENDER TREATMENT:")
print()
print("  synth.load_state(state_mutated)")
print("  output_treatment = synth.render(midi_note=(60, 1.5s))")
print("  treatment_rms = compute_overall_rms_db(output_treatment)")
print("  treatment_centroid = compute_spectral_centroid_hz(output_treatment)")
print()

print("C. MEASUREMENT DELTA:")
print()
print("  delta_rms = treatment_rms - baseline_rms")
print("  delta_centroid = treatment_centroid - baseline_centroid")
print()
print("  Expected:")
print("    delta_rms < -1.0 dB  (treatment quieter)")
print("    delta_centroid: may change depending on harmonic content")
print()

# =========================================================================
# RESTORE: Return to baseline via MCP
# =========================================================================

print("-" * 70)
print("STEP 6: RESTORE VIA MCP")
print("-" * 70)
print()

print("A. RESTORE COMMAND (MCP):")
print()
print("  set_device_parameter(")
print("    track_index=0,")
print("    device_index=0,")
print("    parameter_name='A Enable',")
print("    value=0.0  [restore to baseline]")
print("  )")
print()

print("B. VERIFY RESTORATION (MCP):")
print()
print("  result = get_device_parameters(..., filter_name='A Enable')")
print()
print("  If result['value'] == 0.0:")
print("    EVIDENCE: Restored successfully")
print("  Else:")
print("    [WARN] Restore may not have succeeded")
print()

# =========================================================================
# SUMMARY
# =========================================================================

print("=" * 70)
print("PROOF STRUCTURE (PSEUDO-EXECUTION)")
print("=" * 70)
print()

print("FOR THIS TO WORK:")
print()

print("1. Ableton Live MUST be running with Serum loaded on track 0")
print()

print("2. MCP MUST be connected and functional")
print()

print("3. The connection between Ableton MCP and DawDreamer MUST be via:")
print("   - MCP reads/writes Ableton's Serum VST3 instance")
print("   - save_state() captures that instance's state")
print("   - DawDreamer loads and renders that saved state")
print()

print("4. If Ableton and DawDreamer instances are DECOUPLED:")
print("   - MCP enable will not affect DawDreamer's render")
print("   - Baseline will still be silent")
print("   - STOP and report decoupling")
print()

print("=" * 70)
print("ALTERNATIVE: USE ABLETON AS EXECUTION ENGINE")
print("=" * 70)
print()

print("If MCP and DawDreamer are decoupled:")
print()

print("Redesign to use Ableton MCP for BOTH enable and observation:")
print()

print("1. MCP set 'A Enable' = 1.0")
print("2. MCP read 'A Level' = baseline")
print("3. MCP set 'A Level' = 0.0 (or different value)")
print("4. MCP read 'A Level' = treatment")
print("5. Measure the difference via Ableton's current state")
print()

print("This would prove OSC1.Level is behaviorally observable")
print("via the Ableton MCP control plane ONLY, not CBOR.")
print()

print("=" * 70)
print("NEXT: RUN WITH LIVE ABLETON IF AVAILABLE")
print("=" * 70)
print()

print("To execute this proof:")
print("1. Start Ableton Live 12.3")
print("2. Load Serum on a MIDI track")
print("3. Re-run this script with Ableton MCP enabled")
print()

print("Script halts here pending live Ableton availability.")
print()
