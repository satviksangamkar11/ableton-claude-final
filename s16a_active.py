"""Step 16 - Capture State A: Distortion ACTIVE.
Opens Serum UI. Waits for D:/ableton claude/trigger.txt to appear.
When file detected, captures and saves state A, then exits.
"""
import time, cbor2, pickle, os
import dawdreamer as dw

SERUM_PATH = "C:/Program Files/Common Files/VST3/Serum2.vst3/Contents/x86_64-win/Serum2.vst3"
OUT_FILE = "D:/ableton claude/s16_state_a.pkl"
TRIGGER = "D:/ableton claude/trigger.txt"

# Remove old trigger if present
if os.path.exists(TRIGGER):
    os.remove(TRIGGER)

engine = dw.RenderEngine(44100, 512)
synth = engine.make_plugin_processor("serum", SERUM_PATH)
print("[OK] Serum loaded (default state - no FX)")

synth.open_editor()
print("[OK] Serum editor opened")
print("ADD FXDistortion to MAIN rack and set ACTIVE.")
print("Then create trigger.txt to capture.")

while not os.path.exists(TRIGGER):
    time.sleep(0.5)

print("Trigger detected. Capturing State A...")
state_bytes = synth.save_state()
state = cbor2.loads(state_bytes)
rack = state.get("FXRack0", {})
fx_array = rack.get("FX", [])
print(f"  FXRack0.FX length: {len(fx_array)}")
if fx_array:
    print(f"  FX[0] keys: {list(fx_array[0].keys())}")

os.remove(TRIGGER)
pickle.dump({"bytes": state_bytes, "decoded": state}, open(OUT_FILE, "wb"))
print(f"[SAVED] State A -> {OUT_FILE}")
