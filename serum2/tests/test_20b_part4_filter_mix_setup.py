"""STEP 20B PART 4: Filter Mix discovery — create test presets with known values."""
import os
import tempfile
import copy
from serum2 import bridge, codec, pathmerge
from serum2.evidence import epoch as epoch_mod

VST3 = epoch_mod.SERUM_VST3
PRESET_DIR = r"C:\Users\Satvik\Documents\Xfer\Serum 2 Presets\Presets\User"


def create_filter_test_preset(test_name, filter_index, filter_mix_value):
    """Create a test preset with Filter Mix set to a known value.

    Approach:
    1. Load skeleton to get default CBOR structure
    2. Find Filter plainParams location and mutation key for mix
    3. Create three calibration presets: 0%, 50%, 100% mix
    4. Save and decode to identify CBOR path and scale
    """
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], copy.deepcopy(skeleton[1])

    # Try to identify filter mix parameter
    # Common candidates: kParamMixOrGain, kParamWet, kParamDry, kParamMix
    filter_mod = body.get(f"VoiceFilter{filter_index}")
    if not filter_mod:
        print(f"ERROR: VoiceFilter{filter_index} not found in skeleton")
        return False

    # Ensure plainParams is a dict (not "default")
    pp = filter_mod.get("plainParams", "default")
    if pp == "default":
        filter_mod["plainParams"] = {}

    # Hypothesis: filter mix uses kParamMixOrGain (based on Filter global control)
    # Try normalized 0..1 scale for now (same as Level)
    filter_mod["plainParams"]["kParamMixOrGain"] = filter_mix_value

    # Save to temp file
    fd, tmp_path = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp_path, meta, body)

    # Save as preset
    preset_path = os.path.join(PRESET_DIR, f"STEP20B_FILTER{filter_index}_MIX_{test_name}.SerumPreset")
    os.rename(tmp_path, preset_path)

    print(f"Created: {os.path.basename(preset_path)}")
    print(f"  Filter{filter_index} Mix value: {filter_mix_value}")

    return preset_path


if __name__ == "__main__":
    print("="*70)
    print("STEP 20B PART 4: FILTER MIX TEST PRESET CREATION")
    print("="*70)
    print()

    # Create calibration presets
    print("Creating calibration presets for Filter0 Mix...")
    presets = []

    try:
        # 0% mix (fully dry, bypass filter)
        presets.append(create_filter_test_preset("0PCT_DRY", 0, 0.0))

        # 50% mix (equal wet/dry)
        presets.append(create_filter_test_preset("50PCT_MID", 0, 0.5))

        # 100% mix (fully wet, filter on)
        presets.append(create_filter_test_preset("100PCT_WET", 0, 1.0))

        print()
        print("="*70)
        print("NEXT STEPS:")
        print("="*70)
        print("1. Decode the created presets to verify CBOR path:")
        print("   - Check VoiceFilter0.plainParams.kParamMixOrGain values")
        print("   - Confirm value scale (0..1 normalized or 0..100 percentage)")
        print()
        print("2. Load presets in Serum UI to verify they sound correct:")
        print("   - 0% should be fully dry (no filter)")
        print("   - 50% should be equal wet/dry")
        print("   - 100% should be fully wet (filter applied)")
        print()
        print("3. Create parametric round-trip test (like test_20b_parametric_osc23.py)")
        print("   - Mutate kParamMixOrGain via pathmerge")
        print("   - Save and reload via DawDreamer")
        print("   - Verify persistence")
        print()
        print("Presets created:")
        for p in presets:
            if p:
                print(f"  {os.path.basename(p)}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
