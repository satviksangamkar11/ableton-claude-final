"""Failure/status classification for bulk verification results.

Explicit machine-readable statuses -- never collapsed into one generic
PASS/FAIL. A binding that mutates correctly but fails persistence is a
different fact than one whose UI never reflects the mutation, and both are
different from one that was never executable at all.
"""

from __future__ import annotations
from enum import Enum


class Classification(str, Enum):
    MACHINE_VERIFIED = "MACHINE_VERIFIED"          # authority mutate + persist, both probes, no UI check
    UI_VERIFIED = "UI_VERIFIED"                     # + real Serum GUI confirmed (agent-driven pass only)
    PERSISTENCE_VERIFIED = "PERSISTENCE_VERIFIED"   # alias used when only persistence (not both probes) was checked
    PERSISTENCE_MISMATCH = "PERSISTENCE_MISMATCH"   # in-process mutate OK, save/reload does not preserve it
    UI_MISMATCH = "UI_MISMATCH"                     # real Serum GUI does not reflect the requested value
    UI_UNREADABLE = "UI_UNREADABLE"                 # UI control could not be located/read
    INVALID_PROBE = "INVALID_PROBE"                 # could not generate a legal probe value for this binding
    BINDING_ERROR = "BINDING_ERROR"                 # binding metadata itself is broken (missing resolver entry, etc.)
    FORENSIC_REQUIRED = "FORENSIC_REQUIRED"          # anomaly needing a manual/agent-driven forensic pass
    NOT_EXECUTABLE = "NOT_EXECUTABLE"                # binding_status != LIVE_VERIFIED, nothing to run yet


# Statuses that represent a fully-closed-loop success for the tier that was run.
PASSING = {Classification.MACHINE_VERIFIED, Classification.UI_VERIFIED, Classification.PERSISTENCE_VERIFIED}

# Statuses that belong in the forensic queue for follow-up (excludes NOT_EXECUTABLE,
# which just means "nothing to run yet", not "something is wrong").
NEEDS_FOLLOWUP = {
    Classification.PERSISTENCE_MISMATCH,
    Classification.UI_MISMATCH,
    Classification.UI_UNREADABLE,
    Classification.INVALID_PROBE,
    Classification.BINDING_ERROR,
    Classification.FORENSIC_REQUIRED,
}
