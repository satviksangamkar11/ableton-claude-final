# META_STRING V4 Population Pass Report

## Bound (real .SerumPreset meta-dict evidence + real codec round-trip)

- `BROWSER.METADATA.PRESET_NAME` -> meta.presetName: RESOURCE_OPERATION -> **PRESET_METADATA** (capability_id=`PRESET_METADATA:d1646b9846cd793d`)
- `BROWSER.METADATA.AUTHOR` -> meta.presetAuthor: RESOURCE_OPERATION -> **PRESET_METADATA** (capability_id=`PRESET_METADATA:8a024d55352d3871`)
- `BROWSER.METADATA.DESCRIPTION` -> meta.presetDescription: RESOURCE_OPERATION -> **PRESET_METADATA** (capability_id=`PRESET_METADATA:f983596a707c7b25`)
- `BROWSER.METADATA.TAGS_PANEL` -> meta.tags: RESOURCE_OPERATION -> **PRESET_METADATA** (capability_id=`PRESET_METADATA:ba3c3672f203d0c1`)

## Corrected family, left unbound (no serialized field evidence exists)

- `BROWSER.METADATA.CATEGORY`: RESOURCE_OPERATION -> PRESET_METADATA (NOT_YET_DERIVED) -- no `category` key found in real .SerumPreset meta dict evidence (checked: BA - 303 Punchier.SerumPreset, archive/golden_presets/arp.SerumPreset) or in v8 VST3 processor-state meta -- may belong to Serum's external browser/database layer, not proven this pass
- `BROWSER.METADATA.NOTES`: RESOURCE_OPERATION -> PRESET_METADATA (NOT_YET_DERIVED) -- no `notes` key found in real .SerumPreset meta dict evidence (checked: BA - 303 Punchier.SerumPreset, archive/golden_presets/arp.SerumPreset) or in v8 VST3 processor-state meta -- may belong to Serum's external browser/database layer, not proven this pass
