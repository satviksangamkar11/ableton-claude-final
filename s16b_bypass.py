"""Step 16 - Capture State B: Distortion BYPASSED.
Loads state A into Serum. Opens UI. Waits for trigger.txt.
User should BYPASS (not remove) the Distortion. Then creates trigger.txt.
"""
import time, cbor2, pickle, os
import dawdreamer as dw

SERUM_PATH = "C:/Program Files/Common Files/VST3/Serum2.vst3/Contents/x86_64-win/Serum2.vst3"
IN_FILE = "D:/ableton claude/s16_state_a.pkl"
OUT_FILE = "D:/ableton claude/s16_state_b.pkl"
TRIGGER = "D:/ableton claude/trigger.txt"

if os.path.exists(TRIGGER):
    os.remove(TRIGGER)

data = pickle.load(open(IN_FILE, "rb"))
state_a_bytes = data["bytes"]
print(f"[OK] Loaded state A ({len(state_a_bytes)} bytes)")

engine = dw.RenderEngine(44100, 512)
synth = engine.make_plugin_processor("serum", SERUM_PATH)
synth.load_state(state_a_bytes)
print("[OK] State A loaded into Serum")

synth.open_editor()
print("[OK] Serum editor opened with Distortion ACTIVE")
print("BYPASS the Distortion (click bypass toggle). Do NOT remove it.")
print("Then create trigger.txt to capture.")

while not os.path.exists(TRIGGER):
    time.sleep(0.5)

print("Trigger detected. Capturing State B...")
state_bytes = synth.save_state()
state = cbor2.loads(state_bytes)
rack = state.get("FXRack0", {})
fx_array = rack.get("FX", [])
print(f"  FXRack0.FX length: {len(fx_array)}")

os.remove(TRIGGER)
pickle.dump({"bytes": state_bytes, "decoded": state}, open(OUT_FILE, "wb"))
print(f"[SAVED] State B -> {OUT_FILE}")
