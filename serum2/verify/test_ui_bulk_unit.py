"""Unit tests for serum2.verify.ui_bulk's UI-text classification logic.
No Serum/DawDreamer required."""

from serum2.verify.ui_bulk import UIClassification


def test_ui_classification_vocabulary_distinct_from_machine_tier():
    """UI-text statuses must never collide with classify.py's machine-tier
    Classification names -- the two tiers are never allowed to be
    conflated (CLAUDE.md: preserve evidence distinctions)."""
    from serum2.verify.classify import Classification
    machine_values = {c.value for c in Classification}
    ui_values = {UIClassification.UI_TEXT_VERIFIED, UIClassification.UI_TEXT_MISMATCH,
                 UIClassification.UI_TEXT_UNREADABLE, UIClassification.NO_DETERMINISTIC_UI_PROXY,
                 UIClassification.FORENSIC_REQUIRED}
    assert "UI_VERIFIED" not in ui_values, "must never claim the agent-screenshot UI_VERIFIED tier"
    assert ui_values.isdisjoint(machine_values - {"FORENSIC_REQUIRED", "NOT_EXECUTABLE"})


if __name__ == "__main__":
    test_ui_classification_vocabulary_distinct_from_machine_tier()
    print("[PASS] test_ui_classification_vocabulary_distinct_from_machine_tier")
