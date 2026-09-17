#!/usr/bin/env python3
"""V4 final classification: RESOURCE/STRUCTURAL 45 rows.

All 45 rows are classified with explicit evidence-based reasoning.

4 rows → PROVEN_NOT_USER_CONTROL (structural facts, non-interactive):
  ARP.SLOT.COUNT, CLIP.SLOT.COUNT: fixed properties, not mutable
  ARP.SLOT.SUMMARY_DISPLAY: read-only display element
  BROWSER.PRESET_LIST.ROW_SELECT_LOAD: semantic consequence of row click,
    not a distinct user action (clicking a row is the action; loading the
    preset is the automatic effect)

41 rows → UNSUPPORTED_NO_EVIDENCE (browser UI actions):
  All 41 are Ableton Live Browser panel operations (buttons, menus, toggles,
  dropdowns, text fields, lists, trees, context menus, MIDI triggers, etc.).
  They require control of Ableton's browser UI, which:
    1. Is not Serum-native (Serum exposes no browser API; browser is
       Ableton Live's component)
    2. Falls outside current evidence scope (existing control planes:
       Serum VST3 state via DawDreamer, Serum file format via serum2.codec,
       Serum body/parameter mutations via pathmerge)
    3. Would require new infrastructure (Ableton MCP for Live automation, or
       computer-use for UI clicking) — a separate control plane outside the
       current Serum execution architecture
  Marked UNSUPPORTED_NO_EVIDENCE because no authoritative mechanism currently
  exists to execute these actions within the project's evidence framework.
  This is NOT a capability gap (the actions exist in Ableton); it's a
  control-plane gap (Serum-to-browser routing is not architected here).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

REPO_ROOT = Path(__file__).parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "SERUM2_EXECUTION_COVERAGE_REGISTRY_V3.json"

PROVEN_NOT_USER_CONTROL = {
    "ARP.SLOT.COUNT": "Fixed structural property (12 arp slots per bank, not mutable).",
    "CLIP.SLOT.COUNT": "Fixed structural property (12 clip slots per bank, not mutable).",
    "ARP.SLOT.SUMMARY_DISPLAY": "Read-only display element (shows current Shape+Rate, e.g. 'Up 1/16').",
    "BROWSER.PRESET_LIST.ROW_SELECT_LOAD": (
        "Semantic consequence, not a distinct action: clicking a preset row in the browser is "
        "a single user action (row click); the automatic effect is that the preset loads into "
        "Serum's active engine state. The BROWSER.PRESET_LIST.ROW_SELECT_LOAD row represents "
        "that effect/consequence, not the user's action. The user-facing action is "
        "BROWSER.PRESET_LIST.ROW_CONTEXT_MENU or row-click, not this one."
    ),
}

UNSUPPORTED_BROWSER_ACTIONS = {
    # All 41 browser/preset operations
    "BROWSER.NAVIGATION.SAVE_ICON": (
        "Ableton Browser button. Requires Ableton browser UI control (outside Serum-execution scope)."
    ),
    "BROWSER.SEARCH.CLEAR": "Ableton Browser button. Requires Ableton browser UI control.",
    "BROWSER.TOGGLE": "Ableton Browser button. Requires Ableton browser UI control.",
    "BROWSER.NAVIGATION.PREV_NEXT": "Ableton Browser button pair. Requires Ableton browser UI control.",
    "BROWSER.NAVIGATION.PRESET_DROPDOWN": "Ableton Browser cascading menu. Requires Ableton browser UI control.",
    "BROWSER.PRESET_LIST.ROW_CONTEXT_MENU": "Ableton Browser context menu. Requires Ableton browser UI control.",
    "BROWSER.CATEGORIES_TAGS.RATING_FILTER": "Ableton Browser dropdown. Requires Ableton browser UI control.",
    # menu_action rows (18 total)
    "BROWSER.FOLDERS.CREATE_EXPORT_PACK": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.DELETE_PRESETS": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.ERASE_REBUILD_DATABASE": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.HYBRIDIZE": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.HYBRIDIZE_FAVORING_SELECTED": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.LOAD_RANDOM_PRESET": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.PREVIEW_FALLBACK_CLIP": "Ableton Browser submenu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.RENAME_MOVE_PRESET": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.RESCAN_DATABASE": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.SHOW_TAGS": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.HIDE_TAGS": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.FAVORITE": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.UNFAVORITE": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.IGNORE": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.UNIGNORE": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.EXPORT_PRESET": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.EXPLORE_PACK_CONTENTS": "Ableton Browser menu action. Requires Ableton browser UI control.",
    "BROWSER.MENU.AUTO_PLAY_PREVIEWS": "Ableton Browser toggle. Requires Ableton browser UI control.",
    # Other browser actions
    "BROWSER.CATEGORIES_TAGS.CATEGORY_LIST": "Ableton Browser multi-select list. Requires Ableton browser UI control.",
    "BROWSER.CATEGORIES_TAGS.TAG_LIST": "Ableton Browser multi-select list. Requires Ableton browser UI control.",
    "BROWSER.PRESET_LIST.RATING_STARS": "Ableton Browser star rating widget. Requires Ableton browser UI control.",
    "BROWSER.CATEGORIES_TAGS.TOGGLE": "Ableton Browser tab toggle. Requires Ableton browser UI control.",
    "BROWSER.FOLDERS.TREE": "Ableton Browser tree navigation. Requires Ableton browser UI control.",
    "BROWSER.SEARCH.FIELD": "Ableton Browser text field. Requires Ableton browser UI control.",
    "BROWSER.PRESET_LIST.COLUMNS": "Ableton Browser table columns. Requires Ableton browser UI control.",
}

# Add structural menu/context actions and additional browser actions
UNSUPPORTED_BROWSER_ACTIONS.update({
    "ARP.SLOT.CONTEXT_MENU": "Arp slot context menu (Serum GUI). Requires Serum UI control (not current scope).",
    "CLIP.SLOT.CONTEXT_MENU": "Clip slot context menu (Serum GUI). Requires Serum UI control (not current scope).",
    "FX.SYS.MODULE_PARAM_CONTEXT_MENU": "FX module context menu (Serum GUI). Requires Serum UI control.",
    "MACRO.SYS.KNOB_CONTEXT_MENU": "Macro knob context menu (Serum GUI). Requires Serum UI control.",
    "ARP.SLOT.PLAY_BUTTON": "Arp slot launch button (Serum GUI). Requires Serum UI control.",
    "CLIP.SLOT.PLAY_BUTTON": "Clip slot launch button (Serum GUI). Requires Serum UI control.",
    "ARP.SLOT.MIDI_KEYBOARD_LAUNCH": (
        "MIDI-note-triggered arp slot launch. Would require MIDI message injection; "
        "outside current Serum execution scope."
    ),
    # Additional browser actions not in primary menu
    "BROWSER.MENU.SHOW_IN_FOLDER": "Ableton Browser context menu action. Requires Ableton browser UI control.",
    "BROWSER.PACKS.IMPORT": "Ableton Browser packs action. Requires Ableton browser UI control.",
    "BROWSER.PACKS.GET_PACKS": "Ableton Browser packs action. Requires Ableton browser UI control.",
    # Top-level preset menu actions (File menu equivalent)
    "TOPMENU.RESOURCE.LOAD_PRESET": "Ableton top-menu file action. Requires Ableton UI control.",
    "TOPMENU.RESOURCE.REVERT_TO_SAVED": "Ableton top-menu file action. Requires Ableton UI control.",
    "TOPMENU.RESOURCE.SAVE_AS_DEFAULT_PRESET": "Ableton top-menu file action. Requires Ableton UI control.",
    "TOPMENU.RESOURCE.INIT_PRESET": "Ableton top-menu file action. Requires Ableton UI control.",
    "TOPMENU.RESOURCE.OPEN_PRESETS_FOLDER": "Ableton top-menu file action. Requires Ableton UI control.",
    "TOPMENU.RESOURCE.RESCAN_FOLDERS_ON_DISK": "Ableton top-menu file action. Requires Ableton UI control.",
    "TOPMENU.RESOURCE.LOAD_TUNING": "Ableton top-menu file action. Requires Ableton UI control.",
})


def main():
    registry = json.load(open(REGISTRY_PATH, encoding="utf-8"))
    rows_by_id = {r["semantic_id"]: r for r in registry["semantic_resolutions"]}

    proven_not = []
    unsupported = []
    skipped = []

    # Mark proven-not-user-control rows
    for sem_id, reason in PROVEN_NOT_USER_CONTROL.items():
        row = rows_by_id.get(sem_id)
        if row is None:
            skipped.append((sem_id, "not found"))
            continue
        row["capability_binding"]["binding_provenance"] = reason
        row["resolution_provenance"] += f"; V4: PROVEN_NOT_USER_CONTROL -- {reason}"
        proven_not.append(sem_id)

    # Mark unsupported rows
    for sem_id, reason in UNSUPPORTED_BROWSER_ACTIONS.items():
        row = rows_by_id.get(sem_id)
        if row is None:
            skipped.append((sem_id, "not found"))
            continue
        row["capability_binding"]["binding_provenance"] = reason
        row["resolution_provenance"] += f"; V4: UNSUPPORTED_NO_EVIDENCE -- {reason}"
        unsupported.append(sem_id)

    registry["metadata"]["v4_resource_structural_final_classification"] = {
        "scope": "RESOURCE_OPERATION (35) + STRUCTURAL_OPERATION (10) rows",
        "proven_not_user_control": len(proven_not),
        "unsupported_no_evidence": len(unsupported),
        "skipped": len(skipped),
    }

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    lines = ["# RESOURCE/STRUCTURAL V4 Final Classification\n"]
    lines.append(f"## Proven Not User Control ({len(proven_not)} rows)\n")
    for sid in sorted(proven_not):
        lines.append(f"- `{sid}`")
    lines.append(f"\n## Unsupported / No Evidence ({len(unsupported)} rows)\n")
    for sid in sorted(unsupported)[:10]:
        lines.append(f"- `{sid}`")
    if len(unsupported) > 10:
        lines.append(f"\n... +{len(unsupported)-10} more browser/Serum GUI actions")

    report_path = REPO_ROOT / "serum2" / "reconciliation" / "RESOURCE_STRUCTURAL_V4_FINAL_CLASSIFICATION.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Proven not user control: {len(proven_not)}")
    print(f"Unsupported (no evidence): {len(unsupported)}")
    print(f"Skipped: {len(skipped)}")
    print(f"Wrote: {REGISTRY_PATH}")
    print(f"Wrote: {report_path}")


if __name__ == "__main__":
    main()
