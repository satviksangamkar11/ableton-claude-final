"""Step 16 - Capture State C: Distortion REMOVED.
Loads state B into Serum. Opens UI. Waits for trigger.txt.
User should REMOVE the Distortion from the rack. Then creates trigger.txt.
"""
import time, cbor2, pickle, os
import dawdreamer as dw

SERUM_PATH = "C:/Program Files/Common Files/VST3/Serum2.vst3/Contents/x86_64-win/Serum2.vst3"
IN_FILE = "D:/ableton claude/s16_state_b.pkl"
OUT_FILE = "D:/ableton claude/s16_state_c.pkl"
TRIGGER = "D:/ableton claude/trigger.txt"

if os.path.exists(TRIGGER):
    os.remove(TRIGGER)

data = pickle.load(open(IN_FILE, "rb"))
state_b_bytes = data["bytes"]
print(f"[OK] Loaded state B ({len(state_b_bytes)} bytes)")

engine = dw.RenderEngine(44100, 512)
synth = engine.make_plugin_processor("serum", SERUM_PATH)
synth.load_state(state_b_bytes)
print("[OK] State B loaded into Serum")

synth.open_editor()
print("[OK] Serum editor opened with Distortion BYPASSED")
print("REMOVE the Distortion from the MAIN rack (right-click -> Remove, or X button).")
print("Then create trigger.txt to capture.")

while not os.path.exists(TRIGGER):
    time.sleep(0.5)

print("Trigger detected. Capturing State C...")
state_bytes = synth.save_state()
state = cbor2.loads(state_bytes)
rack = state.get("FXRack0", {})
fx_array = rack.get("FX", [])
print(f"  FXRack0.FX length: {len(fx_array)}")

os.remove(TRIGGER)
pickle.dump({"bytes": state_bytes, "decoded": state}, open(OUT_FILE, "wb"))
print(f"[SAVED] State C -> {OUT_FILE}")
