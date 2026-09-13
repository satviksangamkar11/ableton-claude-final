"""STEP 20B PART 3: Send Levels (RoutingSlot kParamFXBus*Level) persistence discovery."""
import sys
sys.path.insert(0, '.')
import os
import tempfile
import copy
from serum2 import bridge, codec, vst3_state, pathmerge
from serum2.evidence import epoch as epoch_mod

VST3 = epoch_mod.SERUM_VST3
PRESET_DIR = r"C:\Users\Satvik\Documents\Xfer\Serum 2 Presets\Presets\User"


def create_routing_test_preset(test_name, routing_slot_index, bus_level_1, bus_level_2=None):
    """Create test preset with specific send/routing levels.

    Structure discovered:
    - RoutingSlot{i}.plainParams.kParamFXBus1Level: Send to FX Bus 1 (0..100)
    - RoutingSlot{i}.plainParams.kParamFXBus2Level: Send to FX Bus 2 (0..100)

    Reference: LD - Split.SerumPreset shows kParamFXBus1Level = 100.0, kParamFXBus2Level = 100.0
    """
    skeleton = bridge.capture_v8_skeleton(VST3)
    meta, body = skeleton[0], copy.deepcopy(skeleton[1])

    # Configure RoutingSlot
    slot = body.get(f"RoutingSlot{routing_slot_index}")
    if not slot:
        slot = {}
        body[f"RoutingSlot{routing_slot_index}"] = slot

    pp = slot.get("plainParams")
    if pp == "default" or not isinstance(pp, dict):
        slot["plainParams"] = {}

    # Set send levels
    slot["plainParams"]["kParamFXBus1Level"] = bus_level_1
    if bus_level_2 is not None:
        slot["plainParams"]["kParamFXBus2Level"] = bus_level_2

    # Save as preset (using codec, not bridge.write_state_file)
    preset_path = os.path.join(PRESET_DIR, f"STEP20B_ROUTE{routing_slot_index}_BUS1_{test_name}.SerumPreset")
    codec.dump_preset_file(preset_path, meta, body)

    print(f"Created: {os.path.basename(preset_path)}")
    print(f"  RoutingSlot{routing_slot_index}.kParamFXBus1Level = {bus_level_1}")
    if bus_level_2 is not None:
        print(f"  RoutingSlot{routing_slot_index}.kParamFXBus2Level = {bus_level_2}")

    return preset_path


if __name__ == "__main__":
    print("="*70)
    print("STEP 20B PART 3: SEND LEVELS (RoutingSlot FXBus*Level) DISCOVERY")
    print("="*70)
    print()

    # Create test presets with different send levels
    print("Creating calibration presets for send levels...")
    presets = []

    try:
        # Calibration point 1: 0% send (bus muted)
        presets.append(create_routing_test_preset("0PCT", 0, 0.0))
        print()

        # Calibration point 2: 50% send (half level)
        presets.append(create_routing_test_preset("50PCT", 0, 50.0))
        print()

        # Calibration point 3: 100% send (full level)
        presets.append(create_routing_test_preset("100PCT", 0, 100.0))
        print()

        print("="*70)
        print("VERIFICATION: Decode presets to confirm persistence")
        print("="*70)
        print()

        for preset in presets:
            if preset and os.path.exists(preset):
                meta, body = codec.load_preset_file(preset)
                slot0 = body.get("RoutingSlot0")
                if slot0 and isinstance(slot0, dict):
                    pp = slot0.get("plainParams")
                    if isinstance(pp, dict):
                        bus1_level = pp.get("kParamFXBus1Level", "N/A")
                        print(f"{os.path.basename(preset)}")
                        print(f"  RoutingSlot0.kParamFXBus1Level = {bus1_level}")

        print()
        print("="*70)
        print("NEXT STEPS FOR PART 3:")
        print("="*70)
        print("1. Load presets in Serum UI to verify send routing is audible")
        print("   - 0% should have no send (dry only)")
        print("   - 50% should have reduced send level")
        print("   - 100% should have full send to FX Bus 1")
        print()
        print("2. Verify VST3 host parameter readback:")
        print("   - Check if sends expose HOST_PARAM controls")
        print("   - Determine parameter name/range")
        print()
        print("3. Identify scale calibration:")
        print("   - Hypothesis: 0..100 percentage scale")
        print("   - Verify via DawDreamer VST3 parameter readback")
        print()
        print("4. Create parametric round-trip test:")
        print("   - Mutate kParamFXBus1Level via pathmerge")
        print("   - Test dict-merge semantics (kParamFXBus2Level independent)")
        print("   - Verify persistence through save/reload")
        print()
        print("5. Add semantic targets (after pattern confirmed):")
        print("   - ROUTE0.BUS1Level, ROUTE1.BUS1Level, etc.")
        print("   - ROUTE0.BUS2Level, ROUTE1.BUS2Level, etc.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
