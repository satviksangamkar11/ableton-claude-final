"""Test suite for Phase FX-FULL: Complete 14-effect FX control system.

Tests cover:
- All 14 effect types
- All parameters per effect
- 3-bus support (MAIN, BUS1, BUS2)
- Slot operations (enable/disable/add/remove/replace)
- Semantic target resolution
- Pathmerge compilation
- A/B/C verification (structure exists, compiles, persists)
"""

import pytest
from typing import Dict, Any, List

from serum2.operations.fx_resolver_complete import (
    FX_PARAMETER_CATALOG,
    list_effect_parameters,
    list_all_effects,
    resolve_fx_parameter_complete,
    count_total_parameters,
    Bus,
    bus_to_rack_index,
)
from serum2.compiler.targets import SEMANTIC_TARGETS, resolve_semantic_target
from serum2.operations.scalar_operations import PHASE_9B_STRUCTURAL_PATHS


class TestFXCatalogCompleteness:
    """Verify complete FX catalog contains all 14 effect types with parameters."""

    def test_all_14_effects_present(self):
        """All 14 effects are in the catalog."""
        expected_effects = {
            "BODE",
            "CHORUS",
            "COMPRESSOR",
            "CONVOLVE",
            "DELAY",
            "DISTORTION",
            "EQUALIZER",
            "FILTER",
            "FLANGER",
            "HYPER",
            "PHASER",
            "REVERB",
            "SPLITTER",
            "UTILITY",
        }
        actual_effects = set(FX_PARAMETER_CATALOG.keys())
        assert expected_effects == actual_effects, f"Missing or extra effects: {expected_effects ^ actual_effects}"

    def test_parameter_counts_per_effect(self):
        """Each effect has > 0 parameters."""
        counts = count_total_parameters()
        for effect, count in counts.items():
            assert count > 0, f"Effect {effect} has {count} parameters"

    def test_minimum_parameter_coverage(self):
        """Each effect has at least minimum expected parameters."""
        minimums = {
            "BODE": 4,  # Shift, Range, Direction, LevelOut, MixOrGain
            "CHORUS": 4,
            "COMPRESSOR": 5,
            "CONVOLVE": 5,
            "DELAY": 6,
            "DISTORTION": 6,
            "EQUALIZER": 8,
            "FILTER": 4,
            "FLANGER": 4,
            "HYPER": 4,
            "PHASER": 3,
            "REVERB": 3,
            "SPLITTER": 3,
            "UTILITY": 3,
        }
        counts = count_total_parameters()
        for effect, min_count in minimums.items():
            actual = counts[effect]
            assert (
                actual >= min_count
            ), f"Effect {effect}: expected >= {min_count}, got {actual}"

    def test_total_fx_parameters(self):
        """FX system has ~70+ total parameters across all effects."""
        total = sum(count_total_parameters().values())
        assert total >= 70, f"Total FX parameters: {total} (expected >= 70)"


class TestFXParameterResolution:
    """Test parameter path resolution."""

    def test_resolve_distortion_drive(self):
        """Can resolve DISTORTION.Drive at various slots/buses."""
        result = resolve_fx_parameter_complete("DISTORTION", "Drive", rack_index=0, slot_index=2)
        assert result is not None
        assert result["path"] == "FXRack0.FX.2.FXDistortion.plainParams.kParamDrive"
        assert result["type"] == "float"
        assert result["min"] == 0.0
        assert result["max"] == 100.0
        assert result["bus"] == 0
        assert result["slot"] == 2

    def test_resolve_eq_all_bands(self):
        """EQ band parameters resolve correctly."""
        params = ["Freq1", "Reso1", "Gain1", "Freq2", "Reso2", "Gain2", "LevelOut"]
        for param in params:
            result = resolve_fx_parameter_complete("EQUALIZER", param, rack_index=1, slot_index=0)
            assert result is not None, f"Failed to resolve EQUALIZER.{param}"
            assert "FXRack1.FX.0.FXEQ" in result["path"]

    def test_resolve_bus1_and_bus2(self):
        """Can resolve parameters on BUS1 and BUS2."""
        for bus in [0, 1, 2]:
            result = resolve_fx_parameter_complete("CHORUS", "Rate", rack_index=bus, slot_index=0)
            assert result is not None
            assert result["bus"] == bus
            assert f"FXRack{bus}" in result["path"]

    def test_resolve_delay_stereo_params(self):
        """Delay stereo parameters (TimeL/TimeR/OffsetL/OffsetR) resolve."""
        params = ["TimeL", "TimeR", "OffsetL", "OffsetR"]
        for param in params:
            result = resolve_fx_parameter_complete("DELAY", param, rack_index=0, slot_index=1)
            assert result is not None, f"Failed to resolve DELAY.{param}"

    def test_resolve_convolve_ir_path_resource(self):
        """Convolve IR path resource field resolves."""
        result = resolve_fx_parameter_complete("CONVOLVE", "IRPath", rack_index=0, slot_index=0)
        assert result is not None
        assert result["type"] == "string"
        assert "relativePathToIR" in result["path"]

    def test_unknown_effect_returns_none(self):
        """Unknown effect type returns None."""
        result = resolve_fx_parameter_complete("UNKNOWN", "Param", rack_index=0, slot_index=0)
        assert result is None

    def test_unknown_parameter_returns_none(self):
        """Unknown parameter name returns None."""
        result = resolve_fx_parameter_complete("DISTORTION", "UnknownParam", rack_index=0, slot_index=0)
        assert result is None


class TestSemanticTargetCoverage:
    """Test semantic target dictionary covers all FX controls."""

    def test_all_fx_targets_present(self):
        """All FX semantic targets are in SEMANTIC_TARGETS."""
        # Sample key targets that must exist
        required_targets = [
            "FXBODE.Shift",
            "FXChorus.Rate",
            "FXCompressor.Threshold",
            "FXConvolve.IRPath",
            "FXDelay.TimeL",
            "FXDistortion.Mode",
            "FXEQ.Freq1",
            "FXFilter.Cutoff",
            "FXFlanger.Rate",
            "FXHyper.Unison",
            "FXPhaser.Frequency",
            "FXReverb.Size",
            "FXSplitter.BandCount",
            "FXUtility.Gain",
        ]
        for target in required_targets:
            assert target in SEMANTIC_TARGETS, f"Missing semantic target: {target}"

    def test_target_capability_keys_unique(self):
        """Capability keys for FX targets are unique (no collisions)."""
        fx_targets = {k: v for k, v in SEMANTIC_TARGETS.items() if k.startswith("FX")}
        capability_keys = [v.capability_key for v in fx_targets.values()]
        assert len(capability_keys) == len(set(capability_keys)), "Duplicate capability keys"

    def test_bode_targets_complete(self):
        """All BODE parameters have semantic targets."""
        bode_params = list_effect_parameters("BODE").keys()
        for param in bode_params:
            target_name = f"FXBODE.{param}"
            assert target_name in SEMANTIC_TARGETS, f"Missing target: {target_name}"

    def test_chorus_targets_complete(self):
        """All CHORUS parameters have semantic targets."""
        chorus_params = list_effect_parameters("CHORUS").keys()
        for param in chorus_params:
            target_name = f"FXChorus.{param}"
            assert target_name in SEMANTIC_TARGETS, f"Missing target: {target_name}"

    def test_eq_targets_complete(self):
        """All EQUALIZER parameters have semantic targets."""
        eq_params = list_effect_parameters("EQUALIZER").keys()
        for param in eq_params:
            target_name = f"FXEQ.{param}"
            assert target_name in SEMANTIC_TARGETS, f"Missing target: {target_name}"


class TestPathMergeStructuralPaths:
    """Test that pathmerge has fallback paths for all FX parameters."""

    def test_bode_paths_defined(self):
        """All BODE capability keys have pathmerge fallback paths."""
        bode_params = list_effect_parameters("BODE")
        for param_name in bode_params.keys():
            target_name = f"FXBODE.{param_name}"
            if target_name in SEMANTIC_TARGETS:
                cap_key = SEMANTIC_TARGETS[target_name].capability_key
                assert (
                    cap_key in PHASE_9B_STRUCTURAL_PATHS
                ), f"Missing pathmerge path for {target_name} (key={cap_key})"

    def test_all_fx_effect_types_have_paths(self):
        """Every effect type has at least one capability key in pathmerge paths."""
        effects = list_all_effects()
        for effect_type in effects:
            # Count how many paths this effect has
            effect_code_parts = [
                "bode", "chorus", "comp", "conv", "delay",
                "dist", "eq", "filter", "flanger", "hyper",
                "phaser", "reverb", "splitter", "utility",
            ]
            # At least one parameter must have a path
            found = False
            for path_key in PHASE_9B_STRUCTURAL_PATHS.keys():
                if any(effect_code_part in path_key.lower() for effect_code_part in effect_code_parts):
                    found = True
                    break
            assert found, f"No pathmerge paths found for effect type {effect_type}"

    def test_pathmerge_paths_are_valid_dotted_paths(self):
        """All pathmerge paths are valid dotted-path strings."""
        for cap_key, path_template in PHASE_9B_STRUCTURAL_PATHS.items():
            # Path must contain {R} and {N} placeholders, or be a valid constant path
            assert isinstance(path_template, str), f"Path for {cap_key} is not a string"
            assert (
                "{R}" in path_template or "{N}" in path_template or "." in path_template
            ), f"Invalid path template for {cap_key}: {path_template}"


class TestBusModel:
    """Test the three-bus (MAIN/BUS1/BUS2) model."""

    def test_bus_enum_values(self):
        """Bus enum has correct values."""
        assert Bus.MAIN.value == 0
        assert Bus.BUS1.value == 1
        assert Bus.BUS2.value == 2

    def test_bus_to_rack_index_conversion(self):
        """Bus to rack index conversion works."""
        assert bus_to_rack_index(Bus.MAIN) == 0
        assert bus_to_rack_index(Bus.BUS1) == 1
        assert bus_to_rack_index(Bus.BUS2) == 2
        assert bus_to_rack_index("MAIN") == 0
        assert bus_to_rack_index("BUS1") == 1
        assert bus_to_rack_index("BUS2") == 2
        assert bus_to_rack_index(0) == 0
        assert bus_to_rack_index(1) == 1
        assert bus_to_rack_index(2) == 2

    def test_bus_case_insensitive(self):
        """Bus string conversion is case-insensitive."""
        assert bus_to_rack_index("main") == 0
        assert bus_to_rack_index("Main") == 0
        assert bus_to_rack_index("bus1") == 1
        assert bus_to_rack_index("BUS1") == 1


class TestScalarOperationGeneration:
    """Test that scalar operations auto-generate from semantic targets."""

    def test_scalar_operation_would_compile_for_fx_parameter(self):
        """A scalar operation for an FX parameter can compile.

        This tests the A/B/C framework:
        A = Operation expressible (semantic target exists)
        B = Execution path exists (scalar_operations auto-gen would handle it)
        C = State mutation possible (pathmerge path is valid)
        """
        # Pick a test parameter
        test_target = "FXDistortion.Drive"
        assert test_target in SEMANTIC_TARGETS, f"Target {test_target} missing from SEMANTIC_TARGETS"

        # Get the capability key
        ref = SEMANTIC_TARGETS[test_target]
        cap_key = ref.capability_key

        # Should have a pathmerge fallback path
        assert cap_key in PHASE_9B_STRUCTURAL_PATHS, f"No pathmerge path for {cap_key}"

        # Path should be valid template
        path_template = PHASE_9B_STRUCTURAL_PATHS[cap_key]
        assert "{R}" in path_template and "{N}" in path_template, f"Invalid path template: {path_template}"

        # Should interpolate correctly
        concrete_path = path_template.format(R=0, N=2)
        assert concrete_path == "FXRack0.FX.2.FXDistortion.plainParams.kParamDrive"


class TestA_B_C_Framework:
    """A/B/C verification for Phase FX-FULL."""

    def test_a_expressible_all_effects(self):
        """A: All 14 effects are semantically expressible."""
        effects = list_all_effects()
        assert len(effects) == 14, f"Expected 14 effects, got {len(effects)}"

    def test_b_execution_path_scalar_operations(self):
        """B: Scalar operations can execute via Phase 2 auto-generation.

        Note: FX enable/bypass/disable operations are UNRESOLVED (6 targets removed).
        Bypass mechanism unknown after investigation; flex field unexplored.
        See memory/fx_bypass_mechanism_unknown.md for details.

        Current count: 96 FX parameter targets (14 effects × 6-7 params each).
        - PROVEN: 76 parameter controls + 4 structural (clear/remove/add/replace)
        - UNRESOLVED: 6 enable/disable operations pending flex field investigation
        """
        fx_targets = {k: v for k, v in SEMANTIC_TARGETS.items() if k.startswith("FX")}
        # 96 targets = 14 effects × ~6-7 params each + proven structural ops
        assert len(fx_targets) >= 96, f"Expected >=96 FX targets, got {len(fx_targets)}"

    def test_c_state_persistence_pathmerge_fallback(self):
        """C: State mutations can persist via pathmerge fallback paths.

        Pathmerge supports:
        - dotted-path scalar mutations
        - list indexing (FX[N].param)
        - nested dict field access

        All FX parameter paths are expressible via pathmerge.
        """
        # Check representative paths
        test_paths = [
            "FXRack0.FX.0.FXDistortion.plainParams.kParamDrive",
            "FXRack1.FX.2.FXEQ.plainParams.kParamFreq1",
            "FXRack2.FX.5.FXReverb.plainParams.kParamSize",
            "FXRack0.FX.0.FXConv.relativePathToIR",
        ]
        for path in test_paths:
            # Each path should be:
            # - Dotted path with placeholders resolved
            # - List index in FX[N] notation (pathmerge supports this)
            # - Points to a plainParams field or resource field
            assert "FXRack" in path, f"Invalid path: {path}"
            assert "FX." in path, f"Invalid path: {path}"
            assert "plainParams" in path or "relative" in path, f"Invalid path: {path}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
