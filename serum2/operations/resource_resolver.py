"""Phase 6: Resource resolver - locate, verify, and resolve resources to state paths.

The resolver converts human-friendly resource identities to verified
SerumResource objects with canonical metadata required by Serum state.
"""

from __future__ import annotations
import os
import hashlib
from typing import Optional, List
from pathlib import Path

from .resource_model import (
    ResourceKind,
    ResourceAvailability,
    SerumResource,
    ResourceResolution,
    ResourceSearch,
    STANDARD_WAVETABLES,
    STANDARD_SAMPLES,
)


class ResourceResolver:
    """Resolve resource identities to verified SerumResource metadata."""

    def __init__(self, serum_install_dir: Optional[str] = None):
        """Initialize resolver.

        Args:
            serum_install_dir: Serum installation directory (e.g., "C:\\Program Files\\...")
                              If None, uses relative paths only (no file verification).
        """
        self.serum_install_dir = serum_install_dir
        self.wavetable_search_roots = ResourceSearch.get_wavetable_search_roots(serum_install_dir)
        self.sample_search_roots = ResourceSearch.get_sample_search_roots(serum_install_dir)

    def resolve_wavetable(self, identifier: str) -> ResourceResolution:
        """Resolve a wavetable identifier.

        Args:
            identifier: Wavetable name/path (e.g., "Operator", "serum2://wavetable/operator",
                       or "S2 Tables/Operator.wav")

        Returns:
            ResourceResolution with resource if found and unambiguous.
        """
        return self._resolve_resource(identifier, ResourceKind.WAVETABLE, self.wavetable_search_roots)

    def resolve_sample(self, identifier: str) -> ResourceResolution:
        """Resolve a sample identifier.

        Args:
            identifier: Sample name/path (e.g., "Kick", "Drums/Kick")

        Returns:
            ResourceResolution with resource if found and unambiguous.
        """
        return self._resolve_resource(identifier, ResourceKind.SAMPLE, self.sample_search_roots)

    def _resolve_resource(
        self,
        identifier: str,
        kind: ResourceKind,
        search_roots: List[str],
    ) -> ResourceResolution:
        """Core resource resolution logic.

        Args:
            identifier: Resource identifier (name, path, or canonical ID)
            kind: Resource kind (WAVETABLE, SAMPLE, etc.)
            search_roots: Directories to search

        Returns:
            ResourceResolution with resource or error.
        """
        # Step 1: Check standard library
        standard_lookup = self._lookup_standard_library(identifier, kind)
        if standard_lookup:
            resource = standard_lookup
            # Resolve absolute path if serum_install_dir is set
            if self.serum_install_dir:
                abs_path = os.path.join(self.serum_install_dir, resource.serum_relative_path)
                if os.path.exists(abs_path):
                    resource = SerumResource(
                        kind=resource.kind,
                        canonical_id=resource.canonical_id,
                        display_name=resource.display_name,
                        absolute_path=abs_path,
                        serum_relative_path=resource.serum_relative_path,
                        file_hash=self._compute_file_hash(abs_path),
                        file_size=os.path.getsize(abs_path) if os.path.exists(abs_path) else None,
                        source=resource.source,
                    )
                    return ResourceResolution(
                        requested_id=identifier,
                        availability=ResourceAvailability.FOUND,
                        resource=resource,
                        search_roots=search_roots,
                    )

        # Step 2: Search filesystem if serum_install_dir is set
        if self.serum_install_dir:
            candidates = self._search_filesystem(identifier, kind, search_roots)
            if len(candidates) == 0:
                return ResourceResolution(
                    requested_id=identifier,
                    availability=ResourceAvailability.NOT_FOUND,
                    error_detail=f"No {kind.value} found matching '{identifier}'",
                    search_roots=search_roots,
                )
            elif len(candidates) == 1:
                resource = candidates[0]
                return ResourceResolution(
                    requested_id=identifier,
                    availability=ResourceAvailability.FOUND,
                    resource=resource,
                    candidates=candidates,
                    search_roots=search_roots,
                )
            else:
                # Ambiguous - multiple matches
                return ResourceResolution(
                    requested_id=identifier,
                    availability=ResourceAvailability.AMBIGUOUS,
                    candidates=candidates,
                    search_roots=search_roots,
                    error_detail=f"Ambiguous: {len(candidates)} matches for '{identifier}'",
                )

        # Step 3: No serum_install_dir; return "found" for known standard resources only
        if standard_lookup:
            return ResourceResolution(
                requested_id=identifier,
                availability=ResourceAvailability.FOUND,
                resource=standard_lookup,
                search_roots=search_roots,
            )

        # Not found and couldn't search filesystem
        return ResourceResolution(
            requested_id=identifier,
            availability=ResourceAvailability.NOT_FOUND,
            error_detail=f"Resource '{identifier}' not found in standard library and no serum_install_dir provided",
            search_roots=search_roots,
        )

    def _lookup_standard_library(self, identifier: str, kind: ResourceKind) -> Optional[SerumResource]:
        """Look up a resource in standard library.

        Args:
            identifier: Resource identifier
            kind: Resource kind

        Returns:
            SerumResource if found in standard library, else None.
        """
        library = STANDARD_WAVETABLES if kind == ResourceKind.WAVETABLE else STANDARD_SAMPLES

        # Normalize identifier
        search_key = identifier.lower().replace(" ", "_").strip("/\\")

        # Try exact match
        if search_key in library:
            return library[search_key]

        # Try prefix match
        for key, resource in library.items():
            if key.startswith(search_key) or search_key.startswith(key):
                return resource

        return None

    def _search_filesystem(
        self,
        identifier: str,
        kind: ResourceKind,
        search_roots: List[str],
    ) -> List[SerumResource]:
        """Search filesystem for matching resources.

        Args:
            identifier: Resource identifier
            kind: Resource kind
            search_roots: Directories to search

        Returns:
            List of found resources.
        """
        candidates = []

        # File extensions by kind
        extensions = {
            ResourceKind.WAVETABLE: (".wav", ".wavetable"),
            ResourceKind.SAMPLE: (".wav", ".mp3", ".aif", ".aiff"),
            ResourceKind.MULTISAMPLE: (".sfz", ".wav"),
        }

        exts = extensions.get(kind, (".wav",))
        search_term = identifier.lower().replace(" ", "_")

        for root in search_roots:
            if not os.path.exists(root):
                continue

            for dirpath, dirnames, filenames in os.walk(root):
                for filename in filenames:
                    # Check extension
                    if not any(filename.lower().endswith(ext) for ext in exts):
                        continue

                    # Check name match
                    file_base = Path(filename).stem.lower()
                    if search_term in file_base or file_base in search_term:
                        abs_path = os.path.join(dirpath, filename)
                        rel_path = os.path.relpath(abs_path, self.serum_install_dir) if self.serum_install_dir else ""

                        resource = SerumResource(
                            kind=kind,
                            canonical_id=f"serum2://{kind.value}/{Path(filename).stem}",
                            display_name=Path(filename).stem,
                            absolute_path=abs_path,
                            serum_relative_path=rel_path,
                            file_hash=self._compute_file_hash(abs_path),
                            file_size=os.path.getsize(abs_path),
                            source="user",
                        )
                        candidates.append(resource)

        return candidates

    def _compute_file_hash(self, file_path: str) -> Optional[str]:
        """Compute SHA256 hash of file.

        Args:
            file_path: Absolute path to file

        Returns:
            Hex hash string, or None if file doesn't exist.
        """
        if not os.path.exists(file_path):
            return None

        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()[:16]  # 16-char prefix for compact representation
        except Exception:
            return None

    def resource_to_state_path(self, resource: SerumResource, oscillator: int) -> str:
        """Convert resource to Serum state mutation path.

        Args:
            resource: Resolved resource
            oscillator: Oscillator index (0, 1, ...)

        Returns:
            State path for pathmerge mutation (e.g., "Oscillator0.WTOsc0.relativePathToWT")
        """
        if resource.kind == ResourceKind.WAVETABLE:
            return f"Oscillator{oscillator}.WTOsc{oscillator}.relativePathToWT"
        elif resource.kind == ResourceKind.SAMPLE:
            return f"Oscillator{oscillator}.SampleOsc{oscillator}.relativePathToSample"
        elif resource.kind == ResourceKind.MULTISAMPLE:
            return f"Oscillator{oscillator}.MultiSampleOsc{oscillator}.relativePathToMultisample"
        else:
            raise ValueError(f"Unknown resource kind: {resource.kind}")
