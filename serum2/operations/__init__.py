"""Serum operation abstraction layer.

SerumOperation is a COMPILER/PLANNING abstraction that translates human
synthesis intent into state mutations for the existing harness.

Architecture:

  human intent
      ↓
  SerumOperation (this module)
      ↓
  compiler: SerumOperation → Mutation[]
      ↓
  existing pathmerge + harness
      ↓
  DawDreamer
      ↓
  Serum

Execution still uses existing code paths. This layer adds no new backends.
"""

from .model import (
    SerumOperation,
    OperationKind,
    OperationParameter,
    OperationResult,
)
from .registry import (
    OperationRegistry,
    OperationDefinition,
)
from .compiler import (
    compile_operation,
    CompilationError,
)

__all__ = [
    "SerumOperation",
    "OperationKind",
    "OperationParameter",
    "OperationResult",
    "OperationRegistry",
    "OperationDefinition",
    "compile_operation",
    "CompilationError",
]
