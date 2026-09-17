"""Persistent, reproducible qualification fixtures.

Each fixture module exposes a single function returning
(skeleton, exercise_context):

  skeleton         -- (meta, body) tuple from bridge.capture_v8_skeleton()
  exercise_context -- list of (host_param_name, value) to apply to BOTH
                       baseline and treatment arms via set_parameter()
                       before rendering (see EXERCISE_CONTEXT_REGISTRY_V1.md)

Fixtures exist ONLY for capabilities with PROVEN status in
EXERCISE_CONTEXT_REGISTRY_V1.json. Do not add a fixture for a BLOCKED
capability just to make it appear resolved.
"""
