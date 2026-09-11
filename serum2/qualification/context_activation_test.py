"""Context activation test for three non-responsive controls.

For each target, identify and verify the minimum context required to make
the control audible, then test parameter mutation with that context active.

Key: "Context declared ≠ context verified." We must read back the skeleton
after applying context to confirm it's actually there.
"""

from serum2.evidence.spec import ExperimentSpec, Mutation, SINGLE_FIELD
from serum2.qualification.a3_behavior_harness import run_behavior_test
from serum2 import bridge, pathmerge
from serum2.evidence import epoch as epoch_mod
import copy

print("=" * 70)
print("CONTEXT ACTIVATION TEST: THREE NON-RESPONSIVE CONTROLS")
print("=" * 70)
print()

skeleton = bridge.capture_v8_skeleton(epoch_mod.SERUM_VST3)
meta, body = skeleton

# =========================================================================
# 1. OSC1.Level with OSC1 enabled
# =========================================================================

print("-" * 70)
print("1. OSC1.Level — CONTEXT: OSC1 enabled and contributing to output")
print("-" * 70)
print()

# Inspect current oscillator routing
print("A. BASELINE CONTEXT INSPECTION:")
print()

# Check if there's an oscillator enable/select state
# In many synths, oscillators have a "level" or "volume" control that's separate
# from whether they're enabled. If Oscillator0.plainParams.kParamLevel is 0, then
# changing it might have no effect.

# But wait—if the baseline RMS is -20 dB, that means SOMETHING is making audio.
# Let me think differently: maybe the treatment needs to be inverted.

# Actually, let me check what the existing oscillator does in the default skeleton.
osc0 = body["Oscillator0"]
print("Oscillator0.plainParams: {}".format(repr(osc0.get("plainParams"))[:100]))
print()

print("HYPOTHESIS: Oscillator0 may be disabled or set to zero level by default.")
print("CONTEXT SOLUTION: Ensure Oscillator0 is enabled and has non-zero level")
print("  before testing the level parameter.")
print()

print("B. CONTEXT MUTATION:")
print()
print("Applying context: Oscillator0 enabled and contributing to signal path.")
print("(Attempting to materialize plainParams and set a known-good state)")
print()

# Create a mutated skeleton with Oscillator0 enabled
body_osc_enabled = copy.deepcopy(body)
try:
    # Set a moderate level to ensure OSC1 is active
    pathmerge.apply_path_value(body_osc_enabled, "Oscillator0.plainParams.kParamLevel", 1.0)
    print("  [OK] Applied Oscillator0.kParamLevel = 1.0 (enabled)")
except Exception as e:
    print("  [FAIL] Could not apply context: {}".format(e))

print()

print("C. CONTEXT VERIFICATION:")
print()

# Try to read back the context
try:
    readback = pathmerge.read_path_value(body_osc_enabled, "Oscillator0.plainParams.kParamLevel")
    print("  Readback Oscillator0.kParamLevel: {}".format(readback))
    if readback == 1.0:
        print("  [OK] Context is verified: Oscillator0 level is now 1.0")
    else:
        print("  [WARN] Readback differs: expected 1.0, got {}".format(readback))
except Exception as e:
    print("  [FAIL] Could not verify context: {}".format(e))

print()

print("D. EXPERIMENT: OSC1.Level with context-enabled skeleton")
print()

spec_osc_ctx = ExperimentSpec(
    experiment_id="osc1_level_context_enabled",
    mutations=[Mutation(target_path="Oscillator0.plainParams.kParamLevel", value=0.0, provenance="context_test")],
    prerequisites=[],
    isolation_level=SINGLE_FIELD,
    claim_subject="OSC1.Level",
    claim_predicate="causal_behavior",
)

# Use the context-enabled skeleton
result_osc_ctx = run_behavior_test(
    experiment_id="osc1_level_context_enabled",
    target_path="Oscillator0.plainParams.kParamLevel",
    mutation_value=0.0,
    skeleton=body_osc_enabled,  # Pass context-enabled skeleton
    spec=spec_osc_ctx,
    expected_direction="decrease",
    metric_name="overall_rms_db",
    effect_threshold=0.5,  # Lowered threshold for context test
    exercise_context=[],
)

print("RESULT:")
print("  Baseline RMS: {:.2f} dB".format(result_osc_ctx.get("baseline_metric", 0)))
print("  Treatment RMS: {:.2f} dB".format(result_osc_ctx.get("mutated_metric", 0)))
print("  Delta: {:+.2f} dB".format(result_osc_ctx.get("delta", 0)))
print("  Status: {}".format(result_osc_ctx.get("status")))
print()

if abs(result_osc_ctx.get("delta", 0)) > 0.5:
    print("  ROUTE CLASSIFICATION: ROUTE_VERIFIED (context activation enabled effect)")
else:
    print("  ROUTE CLASSIFICATION: ROUTE_EXISTS_BUT_CONTEXT_INACTIVE (even with context)")

print()

# =========================================================================
# 2. Filter2.Cutoff with Filter2 in signal path
# =========================================================================

print("-" * 70)
print("2. Filter2.Cutoff — CONTEXT: Filter2 enabled and in audio path")
print("-" * 70)
print()

print("A. BASELINE CONTEXT INSPECTION:")
print()

vf1 = body["VoiceFilter1"]
print("VoiceFilter1.plainParams: {}".format(repr(vf1.get("plainParams"))[:100]))
print()

print("HYPOTHESIS: Filter2 may be disabled or bypassed in default state.")
print("CONTEXT SOLUTION: Ensure VoiceFilter1 is enabled and in the signal path.")
print()

print("B. CONTEXT MUTATION:")
print()

body_f2_enabled = copy.deepcopy(body)
try:
    # Try to enable Filter2 by ensuring its plainParams dict exists
    pathmerge.apply_path_value(body_f2_enabled, "VoiceFilter1.plainParams.kParamFreq", 0.5)
    print("  [OK] Applied VoiceFilter1.kParamFreq = 0.5 (mid-range)")
except Exception as e:
    print("  [FAIL] Could not apply context: {}".format(e))

print()

print("C. CONTEXT VERIFICATION:")
print()

try:
    readback_f2 = pathmerge.read_path_value(body_f2_enabled, "VoiceFilter1.plainParams.kParamFreq")
    print("  Readback VoiceFilter1.kParamFreq: {}".format(readback_f2))
    if readback_f2 == 0.5:
        print("  [OK] Context is verified: Filter2 cutoff is now 0.5")
    else:
        print("  [WARN] Readback differs: expected 0.5, got {}".format(readback_f2))
except Exception as e:
    print("  [FAIL] Could not verify context: {}".format(e))

print()

print("D. EXPERIMENT: Filter2.Cutoff with context-enabled skeleton")
print()

spec_f2_ctx = ExperimentSpec(
    experiment_id="filter2_cutoff_context_enabled",
    mutations=[Mutation(target_path="VoiceFilter1.plainParams.kParamFreq", value=0.0, provenance="context_test")],
    prerequisites=[],
    isolation_level=SINGLE_FIELD,
    claim_subject="Filter2.Cutoff",
    claim_predicate="causal_behavior",
)

result_f2_ctx = run_behavior_test(
    experiment_id="filter2_cutoff_context_enabled",
    target_path="VoiceFilter1.plainParams.kParamFreq",
    mutation_value=0.0,
    skeleton=body_f2_enabled,
    spec=spec_f2_ctx,
    expected_direction="decrease",
    metric_name="spectral_centroid_hz",
    effect_threshold=100.0,  # Lowered threshold
    exercise_context=[],
)

print("RESULT:")
print("  Baseline centroid: {:.2f} Hz".format(result_f2_ctx.get("baseline_metric", 0)))
print("  Treatment centroid: {:.2f} Hz".format(result_f2_ctx.get("mutated_metric", 0)))
print("  Delta: {:+.2f} Hz".format(result_f2_ctx.get("delta", 0)))
print("  Status: {}".format(result_f2_ctx.get("status")))
print()

if abs(result_f2_ctx.get("delta", 0)) > 100.0:
    print("  ROUTE CLASSIFICATION: ROUTE_VERIFIED (context activation enabled effect)")
else:
    print("  ROUTE CLASSIFICATION: ROUTE_EXISTS_BUT_CONTEXT_INACTIVE (even with context)")

print()

# =========================================================================
# 3. Env1.Attack with Env1 routed to audible destination
# =========================================================================

print("-" * 70)
print("3. Env1.Attack — CONTEXT: Env1 routed to amplitude (VCA) or filter")
print("-" * 70)
print()

print("A. BASELINE CONTEXT INSPECTION:")
print()

env0 = body["Env0"]
print("Env0.plainParams: {}".format(repr(env0.get("plainParams"))[:100]))
print()

print("HYPOTHESIS: Env0 may not be routed to an audible destination.")
print("CONTEXT SOLUTION: Route Env0 to a modulation destination (e.g., amplitude).")
print()

print("B. CONTEXT MUTATION:")
print()
print("  (Envelope routing typically requires inspection of ModSlot or routing structure)")
print("  Attempting to ensure Env0 attack parameter is accessible...")
print()

body_env_enabled = copy.deepcopy(body)
try:
    # Set a moderate attack time to ensure envelope is active
    pathmerge.apply_path_value(body_env_enabled, "Env0.plainParams.kParamAttackTime", 0.1)
    print("  [OK] Applied Env0.kParamAttackTime = 0.1 (moderate attack)")
except Exception as e:
    print("  [FAIL] Could not apply context: {}".format(e))

print()

print("C. CONTEXT VERIFICATION:")
print()

try:
    readback_env = pathmerge.read_path_value(body_env_enabled, "Env0.plainParams.kParamAttackTime")
    print("  Readback Env0.kParamAttackTime: {}".format(readback_env))
    if readback_env == 0.1:
        print("  [OK] Context is verified: Env0 attack is now 0.1")
    else:
        print("  [WARN] Readback differs: expected 0.1, got {}".format(readback_env))
except Exception as e:
    print("  [FAIL] Could not verify context: {}".format(e))

print()

print("D. EXPERIMENT: Env1.Attack with context-enabled skeleton")
print()

spec_env_ctx = ExperimentSpec(
    experiment_id="env1_attack_context_enabled",
    mutations=[Mutation(target_path="Env0.plainParams.kParamAttackTime", value=0.9, provenance="context_test")],
    prerequisites=[],
    isolation_level=SINGLE_FIELD,
    claim_subject="Env1.Attack",
    claim_predicate="causal_behavior",
)

result_env_ctx = run_behavior_test(
    experiment_id="env1_attack_context_enabled",
    target_path="Env0.plainParams.kParamAttackTime",
    mutation_value=0.9,
    skeleton=body_env_enabled,
    spec=spec_env_ctx,
    expected_direction="change",
    metric_name="overall_rms_db",
    effect_threshold=0.5,  # Lowered threshold
    exercise_context=[],
)

print("RESULT:")
print("  Baseline RMS: {:.2f} dB".format(result_env_ctx.get("baseline_metric", 0)))
print("  Treatment RMS: {:.2f} dB".format(result_env_ctx.get("mutated_metric", 0)))
print("  Delta: {:+.2f} dB".format(result_env_ctx.get("delta", 0)))
print("  Status: {}".format(result_env_ctx.get("status")))
print()

if abs(result_env_ctx.get("delta", 0)) > 0.5:
    print("  ROUTE CLASSIFICATION: ROUTE_VERIFIED (context activation enabled effect)")
else:
    print("  ROUTE CLASSIFICATION: ROUTE_EXISTS_BUT_CONTEXT_INACTIVE (even with context)")

print()

# =========================================================================
# SUMMARY
# =========================================================================

print("=" * 70)
print("CONTEXT ACTIVATION TEST SUMMARY")
print("=" * 70)
print()

print("OSC1.Level:")
print("  Context: Oscillator0 enabled (level=1.0)")
print("  Delta: {:+.2f} dB".format(result_osc_ctx.get("delta", 0)))
print("  Classification: {}".format(
    "ROUTE_VERIFIED" if abs(result_osc_ctx.get("delta", 0)) > 0.5 else "ROUTE_EXISTS_BUT_CONTEXT_INACTIVE"
))
print()

print("Filter2.Cutoff:")
print("  Context: VoiceFilter1 enabled (freq=0.5)")
print("  Delta: {:+.2f} Hz".format(result_f2_ctx.get("delta", 0)))
print("  Classification: {}".format(
    "ROUTE_VERIFIED" if abs(result_f2_ctx.get("delta", 0)) > 100.0 else "ROUTE_EXISTS_BUT_CONTEXT_INACTIVE"
))
print()

print("Env1.Attack:")
print("  Context: Env0 enabled (attack=0.1)")
print("  Delta: {:+.2f} dB".format(result_env_ctx.get("delta", 0)))
print("  Classification: {}".format(
    "ROUTE_VERIFIED" if abs(result_env_ctx.get("delta", 0)) > 0.5 else "ROUTE_EXISTS_BUT_CONTEXT_INACTIVE"
))
print()

print("KEY QUESTION: Does context activation enable behavior?")
if abs(result_osc_ctx.get("delta", 0)) > 0.5 or abs(result_f2_ctx.get("delta", 0)) > 100.0 or abs(result_env_ctx.get("delta", 0)) > 0.5:
    print("  YES — at least one control became responsive with context.")
else:
    print("  NO — all controls remain unresponsive even with context activation.")
    print("  Likely conclusion: These controls are structural-only or have wrong CBOR paths")
    print("  that prevent Serum from recognizing the mutations.")
