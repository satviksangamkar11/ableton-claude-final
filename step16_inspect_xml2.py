"""Deep inspection of PluginDevice structure in Ableton .als file."""
import gzip
from xml.etree import ElementTree as ET

als_path = r"D:\ableton claude\step16_state_a_active Project\step16_state_a_active.als"
with gzip.open(als_path, "rb") as f:
    xml_data = f.read()

root = ET.fromstring(xml_data)

# Find the PluginDevice
for elem in root.iter("PluginDevice"):
    print(f"PluginDevice Id={elem.get('Id')}")
    # Print full subtree tags
    def print_tree(e, indent=0):
        text = (e.text or "").strip()
        attribs = dict(e.attrib)
        # Show text if short, otherwise show length
        if text and len(text) > 50:
            text_display = f"<{len(text)} chars>"
        else:
            text_display = repr(text) if text else ""
        print("  " * indent + f"<{e.tag}> attribs={attribs} text={text_display}")
        for child in e:
            print_tree(child, indent + 1)

    print_tree(elem)
    print()
    break  # Just first PluginDevice
