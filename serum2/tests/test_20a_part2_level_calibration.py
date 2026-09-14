"""STEP 20A PART 2: Level (kParamVolume) calibration."""
import os
import tempfile
import copy
import dawdreamer as daw
from serum2 import bridge, codec, vst3_state
from serum2.evidence import epoch as epoch_mod
from serum2.evidence import runtime as runtime_mod

VST3 = epoch_mod.SERUM_VST3
SR = 44100
BLOCK = 512

PRESET_DIR = r"C:\Users\Satvik\Documents\Xfer\Serum 2 Presets\Presets\User"


def load_and_measure(preset_path):
    """Load a preset, extract CBOR kParamVolume, and measure VST3 A Level readback."""
    meta, body = codec.load_preset_file(preset_path)
    cbor_volume = body['Oscillator0']['plainParams'].get('kParamVolume', 'default')

    skeleton = bridge.capture_v8_skeleton(VST3)
    meta_template, body_template = skeleton[0], copy.deepcopy(skeleton[1])

    body_template['Oscillator0']['plainParams'] = body['Oscillator0']['plainParams'].copy()

    fd, tmp = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    bridge.write_state_file(tmp, meta_template, body_template)

    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("serum", VST3)
    synth.load_state(tmp)
    os.remove(tmp)

    vst3_level = runtime_mod.read_host_param(synth, "A Level")
    del engine

    return {
        'preset_path': os.path.basename(preset_path),
        'cbor_kparamvolume': cbor_volume,
        'vst3_a_level': vst3_level,
    }


if __name__ == "__main__":
    print("\n" + "="*70)
    print("STEP 20A PART 2: LEVEL (kParamVolume) CALIBRATION")
    print("="*70)

    presets = [
        "STEP20A_LEVEL_TEST.SerumPreset",
        "STEP20A_LEVEL_TESTSTEP20A_LEVEL_CAL1_85PCT.SerumPreset",
        "STEP20A_LEVEL_TESTSTEP20A_LEVEL_CAL1_85PCTSTEP20A_LEVEL_CAL2_MAX.SerumPreset",
    ]

    results = []
    for preset_name in presets:
        preset_path = os.path.join(PRESET_DIR, preset_name)
        if os.path.exists(preset_path):
            print(f"\n[{preset_name}]")
            try:
                result = load_and_measure(preset_path)
                results.append(result)
                print(f"  CBOR kParamVolume: {result['cbor_kparamvolume']}")
                print(f"  VST3 A Level:     {result['vst3_a_level']}")
            except Exception as e:
                print(f"  ERROR: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[{preset_name}] NOT FOUND")

    print("\n" + "="*70)
    print("CALIBRATION RESULTS")
    print("="*70)
    print(f"{'Preset':<45} {'CBOR kParamVolume':<20} {'VST3 A Level':<15}")
    print("-"*80)
    for r in results:
        print(f"{r['preset_path']:<45} {str(r['cbor_kparamvolume']):<20} {r['vst3_a_level']:<15.6f}")

    # Analyze the mapping
    print("\n" + "="*70)
    print("MAPPING ANALYSIS")
    print("="*70)
    if len(results) >= 2:
        # Extract numeric values
        cbor_vals = []
        vst3_vals = []
        for r in results:
            if isinstance(r['cbor_kparamvolume'], (int, float)):
                cbor_vals.append(r['cbor_kparamvolume'])
                vst3_vals.append(r['vst3_a_level'])

        if len(cbor_vals) >= 2:
            # Check for linearity
            print(f"Data points collected: {len(cbor_vals)}")
            print(f"CBOR range: {min(cbor_vals):.6f} to {max(cbor_vals):.6f}")
            print(f"VST3 range: {min(vst3_vals):.6f} to {max(vst3_vals):.6f}")

            # Fit a simple linear model: vst3 = a * cbor + b
            if len(cbor_vals) >= 2:
                x1, x2 = cbor_vals[0], cbor_vals[-1]
                y1, y2 = vst3_vals[0], vst3_vals[-1]

                if abs(x2 - x1) > 1e-6:
                    slope = (y2 - y1) / (x2 - x1)
                    intercept = y1 - slope * x1
                    print(f"\nLinear hypothesis: VST3 = {slope:.6f} * CBOR + {intercept:.6f}")

                    # Check residuals
                    print(f"\nResidual analysis:")
                    for i, (cbor, vst3) in enumerate(zip(cbor_vals, vst3_vals)):
                        predicted = slope * cbor + intercept
                        residual = vst3 - predicted
                        print(f"  Point {i}: predicted {predicted:.6f}, actual {vst3:.6f}, residual {residual:.6f}")
