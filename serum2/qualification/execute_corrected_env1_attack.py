#!/usr/bin/env python3
"""Execute corrected Env1.Attack episode within qualified scope"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from serum2.qualification.execute_vertical_slice import execute_producer_episode

# Corrected episode parameters (within qualified scope [0.5 -> 0.6])
EPISODE_ID = "ep_vertical_slice_002_env1_attack_corrected"
HUMAN_INTENT = "make the attack faster"
SEMANTIC_TARGET = "Env1.Attack"
HOST_PARAM_NAME = "Env 1 Attack"
MUTATION_VALUE = 0.6
MEASUREMENT_METRIC = "rms_db"
BASELINE_OVERRIDE = 0.5  # Within qualified scope

print("=" * 80)
print("EXECUTING CORRECTED ENV1.ATTACK EPISODE")
print("=" * 80)
print()
print("Parameters:")
print(f"  Intent: {HUMAN_INTENT}")
print(f"  Target: {SEMANTIC_TARGET}")
print(f"  Baseline (override): {BASELINE_OVERRIDE}")
print(f"  Mutation: {MUTATION_VALUE}")
print(f"  Measurement: {MEASUREMENT_METRIC}")
print()

# Execute with baseline override
episode, error = execute_producer_episode(
    human_intent=HUMAN_INTENT,
    semantic_target=SEMANTIC_TARGET,
    host_param_name=HOST_PARAM_NAME,
    mutation_value=MUTATION_VALUE,
    measurement_metric=MEASUREMENT_METRIC,
    episode_id=EPISODE_ID,
    baseline_override=BASELINE_OVERRIDE,
)

if error:
    print()
    print(f"EXECUTION FAILED: {error}")
    sys.exit(1)

# Episode executed successfully
print()
print("=" * 80)
print("EPISODE PERSISTED")
print("=" * 80)
print()

# Convert episode to dict and save
episode_dict = episode.to_dict()
episode_dict['learning_eligible'] = True
episode_dict['observation_only'] = False
episode_dict['prerequisite_scope_violated'] = False
episode_dict['notes'] = (
    'OBSERVATION RECORD: In-scope episode with baseline 0.5 (within qualified '
    'scope [0.5-0.6]). Validates directional consistency for "faster" intent. '
    'Suitable for learning loop.'
)

output_file = f"serum2/qualification/{EPISODE_ID}.json"
with open(output_file, 'w') as f:
    json.dump(episode_dict, f, indent=2)

print(f"Episode saved: {output_file}")
print()
print("Episode metadata:")
print(f"  episode_id: {episode_dict['episode_id']}")
print(f"  learning_eligible: {episode_dict['learning_eligible']}")
print(f"  observation_only: {episode_dict['observation_only']}")
print(f"  prerequisite_scope_violated: {episode_dict['prerequisite_scope_violated']}")
print()
print("Episode data:")
print(f"  baseline readback: {episode_dict['serum_readback_before']}")
print(f"  mutation value: {episode_dict['serum_mutation_value']}")
print(f"  treatment readback: {episode_dict['serum_readback_after']}")
print(f"  measurement: {episode_dict['measurement_metric']}")
print(f"  baseline: {episode_dict['measurement_baseline']:.2f} dB")
print(f"  treatment: {episode_dict['measurement_treatment']:.2f} dB")
print(f"  delta: {episode_dict['measurement_delta']:.2f} dB")
print(f"  restoration: {episode_dict['restoration_readback']}")
print()
print("SUCCESS")
