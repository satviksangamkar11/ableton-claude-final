"""Tests for pathmerge array mutation primitives (Phase FX-FULL)."""

import pytest
from serum2 import pathmerge


class TestArrayRemove:
    """Test array_remove primitive."""

    def test_remove_single_element(self):
        """Remove element from array."""
        body = {"FXRack0": {"FX": [
            {"FXDistortion": {}},
            {"FXReverb": {}},
            {"FXDelay": {}},
        ]}}

        pathmerge.array_remove(body, "FXRack0.FX", 1)

        assert len(body["FXRack0"]["FX"]) == 2
        assert "FXReverb" not in str(body["FXRack0"]["FX"])
        assert "FXDistortion" in str(body["FXRack0"]["FX"])
        assert "FXDelay" in str(body["FXRack0"]["FX"])

    def test_remove_first_element(self):
        """Remove first element."""
        body = {"FXRack0": {"FX": [
            {"FXDistortion": {}},
            {"FXReverb": {}},
        ]}}

        pathmerge.array_remove(body, "FXRack0.FX", 0)

        assert len(body["FXRack0"]["FX"]) == 1
        assert "FXDistortion" not in str(body["FXRack0"]["FX"])

    def test_remove_last_element(self):
        """Remove last element."""
        body = {"FXRack0": {"FX": [
            {"FXDistortion": {}},
            {"FXReverb": {}},
        ]}}

        pathmerge.array_remove(body, "FXRack0.FX", 1)

        assert len(body["FXRack0"]["FX"]) == 1
        assert "FXReverb" not in str(body["FXRack0"]["FX"])

    def test_remove_out_of_range(self):
        """Remove at invalid index raises PathError."""
        body = {"FXRack0": {"FX": [{"FXDistortion": {}}]}}

        with pytest.raises(pathmerge.PathError):
            pathmerge.array_remove(body, "FXRack0.FX", 5)

    def test_remove_negative_index(self):
        """Negative index raises PathError."""
        body = {"FXRack0": {"FX": [{"FXDistortion": {}}]}}

        with pytest.raises(pathmerge.PathError):
            pathmerge.array_remove(body, "FXRack0.FX", -1)

    def test_remove_from_nonarray(self):
        """Remove from non-array path raises PathError."""
        body = {"FXRack0": {"FX": {}}}

        with pytest.raises(pathmerge.PathError):
            pathmerge.array_remove(body, "FXRack0.FX", 0)


class TestArrayInsert:
    """Test array_insert primitive."""

    def test_insert_at_beginning(self):
        """Insert element at start."""
        body = {"FXRack0": {"FX": [{"FXReverb": {}}]}}

        pathmerge.array_insert(body, "FXRack0.FX", 0, {"FXDistortion": {}})

        assert len(body["FXRack0"]["FX"]) == 2
        assert "FXDistortion" in str(body["FXRack0"]["FX"][0])
        assert "FXReverb" in str(body["FXRack0"]["FX"][1])

    def test_insert_at_end(self):
        """Insert element at end."""
        body = {"FXRack0": {"FX": [{"FXDistortion": {}}]}}

        pathmerge.array_insert(body, "FXRack0.FX", 1, {"FXReverb": {}})

        assert len(body["FXRack0"]["FX"]) == 2
        assert "FXDistortion" in str(body["FXRack0"]["FX"][0])
        assert "FXReverb" in str(body["FXRack0"]["FX"][1])

    def test_insert_in_middle(self):
        """Insert element in middle."""
        body = {"FXRack0": {"FX": [
            {"FXDistortion": {}},
            {"FXReverb": {}},
        ]}}

        pathmerge.array_insert(body, "FXRack0.FX", 1, {"FXDelay": {}})

        assert len(body["FXRack0"]["FX"]) == 3
        assert "FXDelay" in str(body["FXRack0"]["FX"][1])
        assert "FXReverb" in str(body["FXRack0"]["FX"][2])

    def test_insert_empty_array(self):
        """Insert into empty array."""
        body = {"FXRack0": {"FX": []}}

        pathmerge.array_insert(body, "FXRack0.FX", 0, {"FXDistortion": {}})

        assert len(body["FXRack0"]["FX"]) == 1

    def test_insert_out_of_range(self):
        """Insert at invalid index raises PathError."""
        body = {"FXRack0": {"FX": [{"FXDistortion": {}}]}}

        with pytest.raises(pathmerge.PathError):
            pathmerge.array_insert(body, "FXRack0.FX", 5, {"FXReverb": {}})

    def test_insert_negative_index(self):
        """Negative index raises PathError."""
        body = {"FXRack0": {"FX": [{"FXDistortion": {}}]}}

        with pytest.raises(pathmerge.PathError):
            pathmerge.array_insert(body, "FXRack0.FX", -1, {"FXReverb": {}})


class TestArrayReplaceElement:
    """Test array_replace_element primitive."""

    def test_replace_first_element(self):
        """Replace first element."""
        body = {"FXRack0": {"FX": [
            {"FXDistortion": {}},
            {"FXReverb": {}},
        ]}}

        pathmerge.array_replace_element(body, "FXRack0.FX", 0, {"FXDelay": {}})

        assert len(body["FXRack0"]["FX"]) == 2
        assert "FXDelay" in str(body["FXRack0"]["FX"][0])
        assert "FXDistortion" not in str(body["FXRack0"]["FX"])

    def test_replace_middle_element(self):
        """Replace middle element."""
        body = {"FXRack0": {"FX": [
            {"FXDistortion": {}},
            {"FXReverb": {}},
            {"FXDelay": {}},
        ]}}

        pathmerge.array_replace_element(body, "FXRack0.FX", 1, {"FXChorus": {}})

        assert len(body["FXRack0"]["FX"]) == 3
        assert "FXChorus" in str(body["FXRack0"]["FX"][1])
        assert "FXReverb" not in str(body["FXRack0"]["FX"])

    def test_replace_out_of_range(self):
        """Replace at invalid index raises PathError."""
        body = {"FXRack0": {"FX": [{"FXDistortion": {}}]}}

        with pytest.raises(pathmerge.PathError):
            pathmerge.array_replace_element(body, "FXRack0.FX", 5, {"FXReverb": {}})


class TestArrayRemoveByType:
    """Test array_remove_by_type primitive."""

    def test_remove_first_distortion(self):
        """Remove first effect of type FXDistortion."""
        body = {"FXRack0": {"FX": [
            {"FXDistortion": {}},
            {"FXReverb": {}},
            {"FXDistortion": {}},
        ]}}

        pathmerge.array_remove_by_type(body, "FXRack0.FX", "FXDistortion")

        assert len(body["FXRack0"]["FX"]) == 2
        # Should have removed first distortion, kept reverb and second distortion
        assert "FXReverb" in str(body["FXRack0"]["FX"])

    def test_remove_nonexistent_type(self):
        """Remove nonexistent type raises PathError."""
        body = {"FXRack0": {"FX": [{"FXDistortion": {}}]}}

        with pytest.raises(pathmerge.PathError):
            pathmerge.array_remove_by_type(body, "FXRack0.FX", "FXNonexistent")


class TestIntegrationWithExistingPathmerge:
    """Test that new array primitives don't break existing pathmerge."""

    def test_scalar_parameter_still_works(self):
        """Existing scalar path mutations still work."""
        body = {"FXRack0": {"FX": [
            {"FXDistortion": {"plainParams": {"kParamDrive": 0.0}}},
        ]}}

        pathmerge.apply_path_value(body, "FXRack0.FX.0.FXDistortion.plainParams.kParamDrive", 50.0)

        value = pathmerge.read_path_value(body, "FXRack0.FX.0.FXDistortion.plainParams.kParamDrive")
        assert pathmerge.tolerant_equal(value, 50.0)

    def test_array_mutation_preserves_parameters(self):
        """Array operations preserve effect parameters."""
        body = {"FXRack0": {"FX": [
            {"FXDistortion": {"plainParams": {"kParamDrive": 50.0}}},
            {"FXReverb": {"plainParams": {"kParamSize": 100.0}}},
        ]}}

        # Remove first effect
        pathmerge.array_remove(body, "FXRack0.FX", 0)

        # Check reverb parameters are intact
        value = pathmerge.read_path_value(body, "FXRack0.FX.0.FXReverb.plainParams.kParamSize")
        assert pathmerge.tolerant_equal(value, 100.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
