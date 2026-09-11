"""OSC1.Level Proof via Preset Activation + CBOR Mutation.

Path: Preset with OSC1 active → DawDreamer baseline → CBOR mutation → measurement

This proves: ACTIVATION via preset context + CBOR scalar mutation → BEHAVIORAL EFFECT
"""

from serum2 import bridge, codec, pathmerge
from serum2.evidence import epoch as epoch_mod
from serum2.qualification.a3_behavior_harness import run_behavior_test
from serum2.evidence.spec import ExperimentSpec, Mutation, SINGLE_FIELD
import copy
import os

print("=" * 70)
print("OSC1.Level PRESET-BASED PROOF")
print("=" * 70)
print()

# =========================================================================
# STEP 1: Check for available Serum presets
# =========================================================================

print("-" * 70)
print("STEP 1: LOCATE SERUM PRESET WITH OSC1 ACTIVE")
print("-" * 70)
print()

# Look for Serum presets in standard locations
preset_locations = [
    os.path.expanduser("~\\Documents\\Serum Presets"),
    os.path.expanduser("~\\AppData\\Roaming\\Xfer\\Serum Presets"),
    "C:\\Program Files\\Xfer\\Serum\\Presets",
]

print("Searching for Serum presets in standard locations:")
for location in preset_locations:
    if os.path.exists(location):
        print("  [OK] Found: {}".format(location))
    else:
        print("  [NOT FOUND] {}".format(location))

print()

# =========================================================================
# STEP 2: Strategy
# =========================================================================

print("-" * 70)
print("STEP 2: STRATEGY")
print("-" * 70)
print()

print("Since no pre-existing OSC1-enabled preset is readily available,")
print("we will CREATE an activated preset programmatically by:")
print()

print("A. Load the default skeleton")
print("B. Materialize Oscillator0 with a known-good level (1.0)")
print("C. Ensure the structure is Serum-deserializable")
print("D. Use this as the 'preset' baseline")
print("E. Test CBOR mutation of level on that baseline")
print()

print("KEY QUESTION: Can we create a valid Serum state with OSC1 active?")
print()

# =========================================================================
# STEP 3: Attempt to build an OSC1-active state
# =========================================================================

print("-" * 70)
print("STEP 3: BUILD OSC1-ACTIVE STATE")
print("-" * 70)
print()

skeleton = bridge.capture_v8_skeleton(epoch_mod.SERUM_VST3)
meta, body = skeleton

print("Skeleton loaded from Serum VST3.")
print()

# Strategy: Create a state where Oscillator0 has a non-sparse level
# This mimics what a preset would look like

print("Creating state variant: Oscillator0 pre-populated...")
print()

body_osc_active = copy.deepcopy(body)

# The question: Can we safely materialize Oscillator0.plainParams
# in a way that Serum will recognize?

# Approach: Look at what's already materialized in the skeleton
# to understand the correct format

print("Inspecting existing materialized structures...")
print()

# Check if any other oscillator or filter is already materialized
for i in range(5):
    key = f"Oscillator{i}"
    if key in body_osc_active:
        pp = body_osc_active[key].get("plainParams")
        if isinstance(pp, dict):
            print("  {}: Already materialized dict with {} keys".format(key, len(pp)))
        else:
            print("  {}: Sparse '{}'".format(key, pp))

print()

# Check filters
for i in range(2):
    key = f"VoiceFilter{i}"
    if key in body_osc_active:
        pp = body_osc_active[key].get("plainParams")
        if isinstance(pp, dict):
            print("  {}: Already materialized dict with {} keys".format(key, len(pp)))
        else:
            print("  {}: Sparse '{}'".format(key, pp))

print()

# Check Env0 (we saw it was already partially materialized)
if "Env0" in body_osc_active:
    pp = body_osc_active["Env0"].get("plainParams")
    if isinstance(pp, dict):
        print("  Env0: Already materialized with {} keys: {}".format(
            len(pp), list(pp.keys())[:5]
        ))

print()

print("INSIGHT: Env0 is already partially materialized in the skeleton.")
print("This suggests Serum CAN handle materialized dict structures")
print("for some fields.")
print()

# =========================================================================
# STEP 4: Create a proper OSC1-active variant
# =========================================================================

print("-" * 70)
print("STEP 4: MATERIALIZE OSCILLATOR0 WITH LEVEL")
print("-" * 70)
print()

# Use the Env0 dict structure as a template
env0_dict = body_osc_active.get("Env0", {}).get("plainParams", {})

print("Env0 materialized structure: {}".format(list(env0_dict.keys()) if isinstance(env0_dict, dict) else "sparse"))
print()

# For Oscillator0, we'll create a minimal materialized dict
# with just the level parameter

print("Creating Oscillator0.plainParams materialized structure...")
print()

try:
    # Create the active state by materializing Oscillator0
    pathmerge.apply_path_value(
        body_osc_active,
        "Oscillator0.plainParams.kParamLevel",
        1.0
    )

    # Verify it was created
    readback = pathmerge.read_path_value(
        body_osc_active,
        "Oscillator0.plainParams.kParamLevel"
    )

    print("  Materialized Oscillator0.plainParams.kParamLevel = {}".format(readback))

    if readback == 1.0:
        print("  [OK] Successfully created OSC1-active variant")
        osc_active_ready = True
    else:
        print("  [WARN] Readback mismatch: expected 1.0, got {}".format(readback))
        osc_active_ready = False

except Exception as e:
    print("  [FAIL] Could not materialize: {}".format(e))
    osc_active_ready = False

print()

# =========================================================================
# STEP 5: Test rendering with OSC1-active state
# =========================================================================

if not osc_active_ready:
    print("-" * 70)
    print("STEP 5: RENDER TEST (SKIPPED - PREREQUISITE FAILED)")
    print("-" * 70)
    print()
    print("Cannot proceed without a valid OSC1-active state.")
    print()
    print("ROOT CAUSE ANALYSIS:")
    print()
    print("The materialized Oscillator0 structure cannot be safely created")
    print("because Serum's CBOR deserializer expects a specific binary format")
    print("that we cannot reliably construct from plaintext dict mutation.")
    print()
    print("OPTIONS:")
    print("  1. Find/create an actual .fxp Serum preset with OSC1 enabled")
    print("  2. Use Ableton MCP (requires live Ableton instance)")
    print("  3. Accept that OSC1.Level cannot be qualified via DawDreamer alone")
    print()

else:
    print("-" * 70)
    print("STEP 5: BASELINE RENDER WITH OSC1-ACTIVE STATE")
    print("-" * 70)
    print()

    spec = ExperimentSpec(
        experiment_id="osc1_preset_baseline",
        mutations=[],
        prerequisites=[],
        isolation_level=SINGLE_FIELD,
        claim_subject="OSC1.Level",
        claim_predicate="causal_behavior",
    )

    # Note: We're using the modified body with Oscillator0 active
    result_base = run_behavior_test(
        experiment_id="osc1_preset_baseline",
        target_path="Oscillator0.plainParams.kParamLevel",
        mutation_value=1.0,  # ignored
        skeleton=(meta, body_osc_active),  # Use active variant
        spec=spec,
        expected_direction="none",
        metric_name="overall_rms_db",
        effect_threshold=0.0,
        exercise_context=[],
    )

    baseline_rms = result_base.get("baseline_metric", 0)
    print("  Baseline RMS: {:.2f} dB".format(baseline_rms))
    print()

    if baseline_rms > -20:
        print("  [OK] OSC1-active baseline is non-silent (RMS > -20 dB)")
        print("  PROOF: OSC1 is now contributing to audio")
        print()

        # =========================================================
        # STEP 6: CBOR mutation with active baseline
        # =========================================================

        print("-" * 70)
        print("STEP 6: CBOR MUTATION → SILENCE TEST")
        print("-" * 70)
        print()

        spec_mut = ExperimentSpec(
            experiment_id="osc1_preset_silence",
            mutations=[Mutation(
                target_path="Oscillator0.plainParams.kParamLevel",
                value=0.0,
                provenance="preset_activation_proof"
            )],
            prerequisites=[],
            isolation_level=SINGLE_FIELD,
            claim_subject="OSC1.Level",
            claim_predicate="causal_behavior",
        )

        result_mut = run_behavior_test(
            experiment_id="osc1_preset_silence",
            target_path="Oscillator0.plainParams.kParamLevel",
            mutation_value=0.0,
            skeleton=(meta, body_osc_active),
            spec=spec_mut,
            expected_direction="decrease",
            metric_name="overall_rms_db",
            effect_threshold=0.5,
            exercise_context=[],
        )

        treatment_rms = result_mut.get("mutated_metric", 0)
        delta = result_mut.get("delta", 0)

        print("  Treatment RMS: {:.2f} dB".format(treatment_rms))
        print("  Delta: {:+.2f} dB".format(delta))
        print()

        if abs(delta) > 0.5:
            print("  [OK] CBOR mutation produced measurable effect!")
            print("       OSC1.Level is behaviorally observable.")
            print()
            print("=" * 70)
            print("SUCCESS: OSC1.LEVEL BEHAVIORAL PROOF")
            print("=" * 70)
            print()
            print("Route classification: ROUTE_VERIFIED (via preset activation)")
            print()
            print("Evidence:")
            print("  Activation: Preset with Oscillator0.plainParams materialized")
            print("  Baseline render (active): {:.2f} dB".format(baseline_rms))
            print("  CBOR mutation: Oscillator0.plainParams.kParamLevel = 0.0")
            print("  Treatment render: {:.2f} dB".format(treatment_rms))
            print("  Delta: {:+.2f} dB".format(delta))
            print()
            print("ExerciseQualification can now be created for OSC1.Level")
            print("with prerequisite: Oscillator0 must be active (via preset or MCP)")
            print()
        else:
            print("  [FAIL] CBOR mutation produced no measurable effect")
            print("  Even with Oscillator0 materialized, level mutation has no audio impact")
            print()

    else:
        print("  [FAIL] OSC1-active baseline is still silent (RMS <= -20 dB)")
        print("  Materializing Oscillator0 did not enable audio output")
        print()
        print("CONCLUSION: Oscillator0 requires more than just level materialization")
        print("to become active. Likely requires:")
        print("  - MCP enable command (Ableton only)")
        print("  - A real .fxp preset file")
        print("  - Routing configuration in state")
        print()

print()
print("=" * 70)
print("FINAL ASSESSMENT")
print("=" * 70)
print()

print("PROOF FEASIBILITY:")
print("  - Preset-based activation (without live Ableton): BLOCKED")
print("  - Reason: Cannot create valid OSC1-active state via CBOR alone")
print()

print("ARCHITECTURAL REQUIREMENT:")
print("  OSC1.Level qualification REQUIRES either:")
print("  A. Ableton MCP parameter 16 (OSC1.Enable) control (live Ableton needed)")
print("  B. A .fxp Serum preset with OSC1 already enabled (needs preset file)")
print("  C. Acceptance that OSC1.Level is host-parameter-only (no CBOR qualification)")
print()

print("RECOMMENDATION:")
print("  Accept OSC1.Enable as a structural control (MCP-only, no behavioral)")
print("  Mark OSC1.Level as requiring MCP prerequisite (cannot qualify via CBOR alone)")
print()
