"""Inspect XML structure of Ableton .als file to find Serum plugin state."""
import gzip
from xml.etree import ElementTree as ET

als_path = r"D:\ableton claude\step16_state_a_active Project\step16_state_a_active.als"
with gzip.open(als_path, "rb") as f:
    xml_data = f.read()

root = ET.fromstring(xml_data)

# Find all Vst3PluginInfo elements
print("All Vst3PluginInfo elements:")
for elem in root.iter("Vst3PluginInfo"):
    print(f"  tag={elem.tag} Name={elem.get('Name')!r}")

print()

# Find Serum-related elements
print("Searching for 'Serum' in all element text/attribs:")
for elem in root.iter():
    for k, v in elem.attrib.items():
        if "serum" in str(v).lower():
            print(f"  {elem.tag}.{k} = {v!r}")
            break

print()

# Look at all PluginDevice elements
print("PluginDevice elements:")
for elem in root.iter("PluginDevice"):
    print(f"  PluginDevice id={elem.get('Id')} children: {[c.tag for c in elem][:5]}")
    # Look for Buffer children
    for buf in elem.iter("Buffer"):
        t = buf.text or ""
        print(f"    Buffer text length: {len(t.strip())} chars")
        break

print()
# Look for any Buffer elements at all
print("All Buffer elements (top 5):")
count = 0
for elem in root.iter("Buffer"):
    t = elem.text or ""
    stripped = t.strip()
    if stripped:
        print(f"  Buffer len={len(stripped)} chars, first 40: {stripped[:40]!r}")
        count += 1
        if count >= 5:
            break
