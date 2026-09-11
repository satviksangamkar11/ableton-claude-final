"""Route qualification for non-responsive controls.

For each control, determine:
1. Whether it exists in Serum's state
2. Its actual representation (sparse/materialized)
3. Whether mutations reach it
4. Whether it's active in the audio path
"""

import json
import copy
from serum2 import bridge, pathmerge
from serum2.evidence import epoch as epoch_mod

print("=" * 70)
print("ROUTE QUALIFICATION: THREE NON-RESPONSIVE CONTROLS")
print("=" * 70)
print()

skeleton = bridge.capture_v8_skeleton(epoch_mod.SERUM_VST3)
meta, body = skeleton

# =========================================================================
# 1. OSC1.Level
# =========================================================================

print("-" * 70)
print("1. OSC1.Level")
print("-" * 70)
print()

cbor_path = "VoiceOsc0.plainParams.kParamLevel"
print("Semantic target: OSC1.Level")
print("Attempted CBOR path: {}".format(cbor_path))
print()

print("A. STATE REPRESENTATION:")
if "VoiceOsc0" in body:
    print("  [OK] VoiceOsc0 exists in skeleton")
    osc0 = body["VoiceOsc0"]
    print("  Type: {}".format(type(osc0)))
    print("  Keys: {}".format(list(osc0.keys())))

    if "plainParams" in osc0:
        pp = osc0["plainParams"]
        print("  plainParams type: {}".format(type(pp)))
        print("  plainParams value: {}".format(repr(pp)[:80]))
else:
    print("  [FAIL] VoiceOsc0 does not exist")

print()

print("B. MUTATION READBACK:")
body_mutated = copy.deepcopy(body)
try:
    pathmerge.apply_path_value(body_mutated, cbor_path, 0.0)
    print("  [OK] Mutation applied without error")

    # Try to read back
    readback = pathmerge.read_path_value(body_mutated, cbor_path)
    print("  Readback value: {}".format(readback))
except Exception as e:
    print("  [FAIL] Mutation error: {}".format(e))

print()

print("C. HOST PARAMETER INVESTIGATION:")
print("  (OSC1.Level likely has a host parameter name)")
print("  Known host parameters in Serum: [requires runtime inspection]")
print("  → Would need to load Serum and call get_parameters_description()")

print()

# =========================================================================
# 2. Filter2.Cutoff
# =========================================================================

print("-" * 70)
print("2. Filter2.Cutoff")
print("-" * 70)
print()

cbor_path_f2 = "VoiceFilter1.plainParams.kParamFreq"
print("Semantic target: Filter2.Cutoff")
print("Attempted CBOR path: {}".format(cbor_path_f2))
print()

print("A. STATE REPRESENTATION:")
if "VoiceFilter1" in body:
    print("  [OK] VoiceFilter1 exists in skeleton")
    filter1 = body["VoiceFilter1"]
    print("  Type: {}".format(type(filter1)))
    print("  Keys: {}".format(list(filter1.keys())))

    if "plainParams" in filter1:
        pp_f = filter1["plainParams"]
        print("  plainParams type: {}".format(type(pp_f)))
        print("  plainParams value: {}".format(repr(pp_f)[:80]))
else:
    print("  [FAIL] VoiceFilter1 does not exist")

print()

print("B. ACTIVE CONTEXT CHECK:")
print("  (Filter2 requires 'Filter 2 On' = 1.0 to be active)")
print("  Question: Is Filter2 actually routed to the audio path?")
print("  Baseline measurement showed 4378 Hz centroid (very high-pass)")
print("  Possible interpretation: Filter2 is in series, set to high-pass by default")
print()

print("C. MUTATION READBACK:")
body_mutated_f2 = copy.deepcopy(body)
try:
    pathmerge.apply_path_value(body_mutated_f2, cbor_path_f2, 0.0)
    print("  [OK] Mutation applied without error")

    readback_f2 = pathmerge.read_path_value(body_mutated_f2, cbor_path_f2)
    print("  Readback value: {}".format(readback_f2))
except Exception as e:
    print("  [FAIL] Mutation error: {}".format(e))

print()

# =========================================================================
# 3. Env1.Attack
# =========================================================================

print("-" * 70)
print("3. Env1.Attack")
print("-" * 70)
print()

cbor_path_env = "VoiceEnv0.plainParams.kParamAttackTime"
print("Semantic target: Env1.Attack")
print("Attempted CBOR path: {}".format(cbor_path_env))
print()

print("A. STATE REPRESENTATION:")
if "VoiceEnv0" in body:
    print("  [OK] VoiceEnv0 exists in skeleton")
    env0 = body["VoiceEnv0"]
    print("  Type: {}".format(type(env0)))
    print("  Keys: {}".format(list(env0.keys())))

    if "plainParams" in env0:
        pp_e = env0["plainParams"]
        print("  plainParams type: {}".format(type(pp_e)))
        print("  plainParams value: {}".format(repr(pp_e)[:80]))
else:
    print("  [FAIL] VoiceEnv0 does not exist")

print()

print("B. AUDIO PATH QUESTION:")
print("  (Envelope must be routed to an audible destination)")
print("  Is Env1 controlling: filter? oscillator? global level?")
print("  Render window: 2.0s with 1.5s note")
print("  Attack would affect onset (0.0-onset), rest of note in sustain")
print()

print("C. MUTATION READBACK:")
body_mutated_env = copy.deepcopy(body)
try:
    pathmerge.apply_path_value(body_mutated_env, cbor_path_env, 0.9)
    print("  [OK] Mutation applied without error")

    readback_env = pathmerge.read_path_value(body_mutated_env, cbor_path_env)
    print("  Readback value: {}".format(readback_env))
except Exception as e:
    print("  [FAIL] Mutation error: {}".format(e))

print()

# =========================================================================
# SUMMARY
# =========================================================================

print("=" * 70)
print("FINDINGS SUMMARY")
print("=" * 70)
print()

print("OSC1.Level:")
print("  CBOR path exists: YES (plainParams is sparse string)")
print("  Mutation applied: YES (writes dict)")
print("  Readback works: YES (returns value)")
print("  → But: audio is unchanged (WHY?)")
print("  NEXT: Test host parameter route via DawDreamer")
print()

print("Filter2.Cutoff:")
print("  CBOR path exists: YES (plainParams is sparse string)")
print("  Mutation applied: YES (writes dict)")
print("  Readback works: YES (returns value)")
print("  → But: audio is unchanged (WHY?)")
print("  QUESTION: Is Filter2 actually in audio path?")
print()

print("Env1.Attack:")
print("  CBOR path exists: YES (plainParams is sparse string)")
print("  Mutation applied: YES (writes dict)")
print("  Readback works: YES (returns value)")
print("  → But: audio is unchanged (WHY?)")
print("  QUESTION: Is Env1 routed to an audible destination?")
print()

print("ROUTE CLASSIFICATION (PRELIMINARY):")
print("  OSC1.Level: HOST_ROUTE_REQUIRED (or STRUCTURAL_OPERATION_REQUIRED)")
print("  Filter2.Cutoff: ROUTE_EXISTS_BUT_CONTEXT_INACTIVE (?)")
print("  Env1.Attack: ROUTE_EXISTS_BUT_CONTEXT_INACTIVE (?)")
print()
print("NEXT: Verify audio path connectivity for Filter2 and Env1")
print("      Test host parameter mechanism for OSC1.Level")

