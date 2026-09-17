"""Phase 6: Resource abstraction for wavetables, samples, multisamples.

SerumResource encapsulates resource metadata without executing file I/O.
Resolver handles locating, verifying, and mapping resources to Serum state paths.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class ResourceKind(Enum):
    """Supported resource types in Serum v8 state."""
    WAVETABLE = "wavetable"
    SAMPLE = "sample"
    MULTISAMPLE = "multisample"


class ResourceAvailability(Enum):
    """Resource existence status."""
    FOUND = "found"
    NOT_FOUND = "not_found"
    AMBIGUOUS = "ambiguous"
    INVALID_KIND = "invalid_kind"


@dataclass(frozen=True)
class SerumResource:
    """Canonical resource representation."""

    kind: ResourceKind
    canonical_id: str  # e.g., "serum2://wavetable/operator" or "serum2://sample/drum_kick"
    display_name: str  # e.g., "Operator" or "Drum Kick"
    absolute_path: str  # e.g., "C:\\Program Files\\Xfer Records\\Serum\\..."
    serum_relative_path: str  # e.g., "Tables/Operator" or "Samples/Drums/Kick"
    file_hash: Optional[str] = None  # SHA256 hash for verification
    file_size: Optional[int] = None  # File size in bytes
    source: str = "user"  # "user", "preset", "library", "bundled"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "kind": self.kind.value,
            "canonical_id": self.canonical_id,
            "display_name": self.display_name,
            "absolute_path": self.absolute_path,
            "serum_relative_path": self.serum_relative_path,
            "file_hash": self.file_hash,
            "file_size": self.file_size,
            "source": self.source,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class ResourceResolution:
    """Result of resource resolution attempt."""

    requested_id: str  # What user asked for
    availability: ResourceAvailability
    resource: Optional[SerumResource] = None
    error_detail: Optional[str] = None
    candidates: List[SerumResource] = field(default_factory=list)
    search_roots: List[str] = field(default_factory=list)

    def success(self) -> bool:
        """Resource was found and unambiguous."""
        return self.availability == ResourceAvailability.FOUND and self.resource is not None

    def failed_reason(self) -> str:
        """Human-readable failure reason."""
        if self.availability == ResourceAvailability.NOT_FOUND:
            return f"Resource not found: {self.requested_id}"
        elif self.availability == ResourceAvailability.AMBIGUOUS:
            return f"Ambiguous resource: {len(self.candidates)} matches for {self.requested_id}"
        elif self.availability == ResourceAvailability.INVALID_KIND:
            return f"Invalid resource kind: {self.requested_id}"
        else:
            return self.error_detail or "Unknown error"


class ResourceSearch:
    """Resource search configuration and results.

    Search roots corrected against the REAL, verified content directory
    (this session): "S2 Tables"/"Serum Data/Tables" and the
    serum_install_dir-relative scheme were both fabricated -- Serum 2's
    actual factory/user content root is a Documents-based directory (the
    same one serum2/statemodel.py and several tests already use for
    PRESET_DIR), structured as <root>/Tables/{S2 Tables,User,Analog,...}
    and <root>/Samples/{Factory,User,...}, not <install_dir>/S2 Tables.
    Confirmed via a real preset's Oscillator0.WTOsc0.relativePathToWT ==
    "S2 Tables/Default Shapes.wav", matching a real file at
    <root>/Tables/S2 Tables/Default Shapes.wav.
    """

    DEFAULT_CONTENT_ROOT = r"C:\Users\Satvik\Documents\Xfer\Serum 2 Presets"

    @staticmethod
    def get_wavetable_search_roots(serum_install_dir: Optional[str] = None) -> List[str]:
        """Get search roots for wavetables.

        Args:
            serum_install_dir: content root override (defaults to the real,
                verified DEFAULT_CONTENT_ROOT if not given).

        Returns:
            Absolute directory paths to search, each corresponding to a
            first path segment Serum itself uses in relativePathToWT
            (e.g. "S2 Tables/...", "User/...").
        """
        root = serum_install_dir or ResourceSearch.DEFAULT_CONTENT_ROOT
        tables_root = f"{root}\\Tables"
        return [f"{tables_root}\\{sub}" for sub in ("S2 Tables", "User", "Analog", "Digital", "Spectral", "Vowel")]

    @staticmethod
    def get_sample_search_roots(serum_install_dir: Optional[str] = None) -> List[str]:
        """Get search roots for samples."""
        root = serum_install_dir or ResourceSearch.DEFAULT_CONTENT_ROOT
        samples_root = f"{root}\\Samples"
        return [f"{samples_root}\\{sub}" for sub in ("Factory", "Factory Non-Tonal", "User")]


# NOTE: no hardcoded "standard library" shortcut dict here anymore. The
# previous STANDARD_WAVETABLES/STANDARD_SAMPLES entries ("operator",
# "brass", "pad", "drum_kick") were fabricated placeholders
# (absolute_path="", no file_hash/file_size -- never verified against a
# real installation) and, checked directly against the real content
# directory this session, do not correspond to any real file: no
# "Operator.wav"/"Brass.wav"/"Pad.wav" exist, and no kick sample was found
# under Samples/Factory at all. A hardcoded list that silently resolves to
# a wrong or nonexistent path is worse than requiring a real filesystem
# search every time -- resolution now ALWAYS verifies against real files
# (see ResourceResolver._search_filesystem), never a cached guess.
