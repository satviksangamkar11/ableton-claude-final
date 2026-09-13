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
    """Resource search configuration and results."""

    # Standard Serum resource locations (relative to Serum installation)
    DEFAULT_WAVETABLE_SEARCH_ROOTS = [
        "S2 Tables",  # Bundled wavetables
        "Serum Data/Tables",  # User-imported wavetables
    ]

    DEFAULT_SAMPLE_SEARCH_ROOTS = [
        "S2 Samples",  # Bundled samples
        "Serum Data/Samples",  # User-imported samples
    ]

    @staticmethod
    def get_wavetable_search_roots(serum_install_dir: Optional[str] = None) -> List[str]:
        """Get search roots for wavetables.

        Args:
            serum_install_dir: Serum installation directory. If None, uses environment.

        Returns:
            List of search roots (absolute paths if serum_install_dir provided, else relative).
        """
        if serum_install_dir:
            return [
                f"{serum_install_dir}\\S2 Tables",
                f"{serum_install_dir}\\Serum Data\\Tables",
            ]
        return ResourceSearch.DEFAULT_WAVETABLE_SEARCH_ROOTS

    @staticmethod
    def get_sample_search_roots(serum_install_dir: Optional[str] = None) -> List[str]:
        """Get search roots for samples."""
        if serum_install_dir:
            return [
                f"{serum_install_dir}\\S2 Samples",
                f"{serum_install_dir}\\Serum Data\\Samples",
            ]
        return ResourceSearch.DEFAULT_SAMPLE_SEARCH_ROOTS


# Standard built-in resources (discovered from Serum installations)
STANDARD_WAVETABLES = {
    "operator": SerumResource(
        kind=ResourceKind.WAVETABLE,
        canonical_id="serum2://wavetable/operator",
        display_name="Operator",
        absolute_path="",  # Set at resolution time
        serum_relative_path="Tables/Operator",
        source="bundled",
    ),
    "brass": SerumResource(
        kind=ResourceKind.WAVETABLE,
        canonical_id="serum2://wavetable/brass",
        display_name="Brass",
        absolute_path="",
        serum_relative_path="Tables/Brass",
        source="bundled",
    ),
    "pad": SerumResource(
        kind=ResourceKind.WAVETABLE,
        canonical_id="serum2://wavetable/pad",
        display_name="Pad",
        absolute_path="",
        serum_relative_path="Tables/Pad",
        source="bundled",
    ),
}

STANDARD_SAMPLES = {
    "drum_kick": SerumResource(
        kind=ResourceKind.SAMPLE,
        canonical_id="serum2://sample/drum_kick",
        display_name="Drum Kick",
        absolute_path="",
        serum_relative_path="Samples/Drums/Kick",
        source="bundled",
    ),
}
