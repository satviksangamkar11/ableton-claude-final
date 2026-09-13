"""
STEP 5.4-Q REGRESSION TEST SUITE

Verify that the original 23 misclassified propositions now classify correctly
using the repaired semantic classifier.

These are the exact cases that failed in the original 5.4 extraction.
"""

import pytest
from step_5_4_q_semantic_contract import classify_semantic


class TestRegressionOn5_4_Failures:
    """Regression tests for the original 23 misclassifications."""

    # Original failures: PROCEDURE misclassified (counted as PROCEDURE, should be something else)

    def test_regression_prop_000000_biography_not_procedure(self):
        """prop_000000: Biography should be CONTEXT, not PROCEDURE."""
        text = "So, after teaching Serum for over 10 years now, and being one of the sound designers who worked on Serum 2's factory patches, I've decided to create a full free course on it."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONTEXT"

    def test_regression_prop_000001_not_procedure(self):
        """prop_000001: NOT PROCEDURE (was misclassified)."""
        text = "sound generators, filters, and modulation. There's a little bit more to it, of course, but these are the areas we'll be spending the most time for now."
        result = classify_semantic(text, [])
        assert result["classification"] != "PROCEDURE"

    def test_regression_prop_000002_ui_description_not_procedure(self):
        """prop_000002: UI description should be OBSERVATION, not PROCEDURE."""
        text = "previews. There's a save icon which you can also alt or optionclick to quick save if the preset has already been saved before."
        result = classify_semantic(text, [])
        assert result["classification"] == "OBSERVATION"

    def test_regression_prop_000004_not_procedure(self):
        """prop_000004: NOT PROCEDURE (was misclassified)."""
        text = "now all you need to know is that these make up the building blocks of our sound."
        result = classify_semantic(text, [])
        assert result["classification"] != "PROCEDURE"

    def test_regression_prop_000006_not_procedure(self):
        """prop_000006: NOT PROCEDURE (was misclassified)."""
        text = "sound, which brings us on to the next part of the signal flow, the filters."
        result = classify_semantic(text, [])
        assert result["classification"] != "PROCEDURE"

    def test_regression_prop_000010_not_procedure(self):
        """prop_000010: NOT PROCEDURE (was misclassified as procedure)."""
        text = "In this example, we're effectively splitting the signal into two, meaning our filters are acting on the signal in parallel with one another."
        result = classify_semantic(text, [])
        assert result["classification"] != "PROCEDURE"

    def test_regression_prop_000011_not_procedure(self):
        """prop_000011: NOT PROCEDURE (was misclassified)."""
        text = "As well as being simple frequency carving tools, Serum 2 also has plenty of more interesting filter types that can sometimes be a big part of the sound design."
        result = classify_semantic(text, [])
        assert result["classification"] != "PROCEDURE"

    def test_regression_prop_000015_summary_not_procedure(self):
        """prop_000015: Summary statement should NOT be PROCEDURE."""
        text = "So to summarize our signal flow, the..."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONTEXT"

    def test_regression_prop_000016_not_procedure(self):
        """prop_000016: NOT PROCEDURE (was misclassified)."""
        text = "sound begins in our sound generators. It's then sent to our filters, then out of the filters into the effects before finally being sent out of the synth."
        result = classify_semantic(text, [])
        assert result["classification"] != "PROCEDURE"

    def test_regression_prop_000020_definition_not_procedure(self):
        """prop_000020: Definition should be CONCEPT, not PROCEDURE."""
        text = "highest amplitude. [Music] after this peak. Decay is the amount of time it takes the amplitude to reach the sustain level."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONCEPT"

    def test_regression_prop_000023_principle_not_procedure(self):
        """prop_000023: Behavioral principle should be PRINCIPLE, not PROCEDURE."""
        text = "Envelopes behave exactly the same way when we use them to modulate other parameters."
        result = classify_semantic(text, [])
        assert result["classification"] == "PRINCIPLE"

    def test_regression_prop_000024_not_procedure(self):
        """prop_000024: NOT PROCEDURE (was misclassified)."""
        text = "Envelopes are most useful when we want linear modulation to occur once per note. If however we want modulation that is continuous and repeating, this is where LFOs can be incredibly useful."
        result = classify_semantic(text, [])
        assert result["classification"] != "PROCEDURE"

    def test_regression_prop_000025_filler_not_procedure(self):
        """prop_000025: Filler should be FILLER, not PROCEDURE."""
        text = "simple or much more [Music] advanced. There's way too much here to cover outside of a dedicated video, but..."
        result = classify_semantic(text, [])
        assert result["classification"] == "FILLER"

    def test_regression_prop_000026_not_procedure(self):
        """prop_000026: NOT PROCEDURE (was misclassified)."""
        text = "some basics to be aware of is that they can be shaped similar to envelopes by clicking and dragging."
        result = classify_semantic(text, [])
        assert result["classification"] != "PROCEDURE"

    def test_regression_prop_000028_observation_not_procedure(self):
        """prop_000028: Observation should be OBSERVATION, not PROCEDURE."""
        text = "Finally, it's also worth mentioning you can save and load LFO [Music] presets. In Serum, we also have velocity modulation, which lets you use your notes velocity."
        result = classify_semantic(text, [])
        # Could be OBSERVATION or CONTEXT
        assert result["classification"] in ["OBSERVATION", "CONTEXT"]

    def test_regression_prop_000029_not_procedure(self):
        """prop_000029: NOT PROCEDURE (was misclassified)."""
        text = "source. Especially useful for presets you want to behave more similar to real instruments when [Music] played. And finally, note modulation."
        result = classify_semantic(text, [])
        assert result["classification"] != "PROCEDURE"

    def test_regression_prop_000030_observation_not_procedure(self):
        """prop_000030: Observation/explanation should not be PROCEDURE."""
        text = "sound designers use to create interesting and dynamic sounding patches. If you ever like the sound of a preset and want to figure out why, taking a glance at the modulation matrix."
        result = classify_semantic(text, [])
        assert result["classification"] != "PROCEDURE"

    def test_regression_prop_000032_concept_not_procedure(self):
        """prop_000032: Arpeggiator definition should be CONCEPT, not PROCEDURE."""
        text = "roll, as well as the arpeggiator, which takes chords and sequences them into melodies."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONCEPT"

    def test_regression_prop_000033_concept_not_procedure(self):
        """prop_000033: Keyboard description should be CONCEPT or OBSERVATION, not PROCEDURE."""
        text = "Next, we have Serum's keyboard, which shows incoming notes as well as giving transposition, scale, and swing [Music]"
        result = classify_semantic(text, [])
        assert result["classification"] in ["CONCEPT", "OBSERVATION", "CONTEXT"]

    def test_regression_prop_000035_context_not_procedure(self):
        """prop_000035: Transition should be CONTEXT, not PROCEDURE."""
        text = "So far when adjusting parameters, we've just been clicking and dragging. But there are two other options to be aware of."
        result = classify_semantic(text, [])
        assert result["classification"] == "CONTEXT"

    def test_regression_prop_000037_observation_not_procedure(self):
        """prop_000037: Observation about UI should not be pure PROCEDURE."""
        text = "Finally, it's worth noting that while Serum 2's UI does a pretty good job of making its important controls accessible."
        result = classify_semantic(text, [])
        # Should be OBSERVATION or PRINCIPLE, not PROCEDURE
        assert result["classification"] != "PROCEDURE"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
