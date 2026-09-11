"""
Regression tests for target resolution repair.

These tests protect against false positives and ensure the repair doesn't
introduce incorrect mappings:

1. Octave confusion: level keywords shouldn't map to octave targets
2. Generic frequency confusion: cutoff shouldn't map to irrelevant targets
3. Detune precision: detune keywords shouldn't map to other targets
4. Hypothesis count monotonicity: existing targets should have >= prior count
"""

import pytest
from serum2.knowledge.semantic_intent_resolver import (
    resolve_semantic_intent,
)


class TestTargetResolutionRegression:
    """Regression tests for target resolution pipeline repair."""

    def test_quieter_resolves_correctly(self):
        """Verify 'quieter' intent resolves to OSC1.Level, not octave."""
        resolution = resolve_semantic_intent(
            "make the sound quieter",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        assert resolution.semantic_target == "OSC1.Level"
        assert resolution.semantic_target != "OSC1.Octave"

    def test_detune_resolves_correctly(self):
        """Verify 'detune' intent resolves to OSC1.Detune, not octave."""
        resolution = resolve_semantic_intent(
            "oscillator detune",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        assert resolution.semantic_target == "OSC1.Detune"
        assert resolution.semantic_target != "OSC1.Octave"

    def test_brighter_resolves_correctly(self):
        """Verify 'brighter' intent resolves to Filter.Cutoff."""
        resolution = resolve_semantic_intent(
            "make the sound brighter",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        assert resolution.semantic_target == "Filter.Cutoff"
        # Filter.Cutoff is distinct from Filter.Resonance
        assert resolution.semantic_target != "Filter.Resonance"

    def test_existing_targets_maintained(self):
        """Ensure existing target resolutions still work (Env1.Attack, OSC1.Octave)."""
        # Env1.Attack should still resolve
        resolution_attack = resolve_semantic_intent(
            "make the attack slower",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )
        assert resolution_attack.resolution_status == "RESOLVED"
        assert resolution_attack.semantic_target == "Env1.Attack"
        assert len(resolution_attack.hypothesis_ids) >= 3  # 3 existing + any new

        # OSC1.Octave should still resolve
        resolution_octave = resolve_semantic_intent(
            "make the oscillator one octave higher",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )
        assert resolution_octave.resolution_status == "RESOLVED"
        assert resolution_octave.semantic_target == "OSC1.Octave"
        assert len(resolution_octave.hypothesis_ids) >= 16  # 16 existing + any new

    def test_new_targets_have_hypotheses(self):
        """Ensure newly repaired targets have hypotheses."""
        # OSC1.Level should now have hypotheses (was 0, now 95)
        resolution_level = resolve_semantic_intent(
            "make the sound quieter",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )
        assert resolution_level.resolution_status == "RESOLVED"
        assert len(resolution_level.hypothesis_ids) > 0
        assert len(resolution_level.hypothesis_ids) >= 95

        # OSC1.Detune should now have hypotheses (was 0, now 38)
        resolution_detune = resolve_semantic_intent(
            "slightly detune the oscillator",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )
        assert resolution_detune.resolution_status == "RESOLVED"
        assert len(resolution_detune.hypothesis_ids) > 0
        assert len(resolution_detune.hypothesis_ids) >= 38

        # Filter.Cutoff should now have hypotheses (was 0, now 22)
        resolution_cutoff = resolve_semantic_intent(
            "make the sound brighter",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )
        assert resolution_cutoff.resolution_status == "RESOLVED"
        assert len(resolution_cutoff.hypothesis_ids) > 0
        assert len(resolution_cutoff.hypothesis_ids) >= 22

    def test_unrelated_intent_still_unsupported(self):
        """Ensure unrelated intents still return UNSUPPORTED."""
        resolution = resolve_semantic_intent(
            "make it purple",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        assert resolution.resolution_status == "UNSUPPORTED"
        assert resolution.semantic_target == "UNKNOWN"
        assert len(resolution.hypothesis_ids) == 0

    def test_provenance_chains_valid_ids(self):
        """Ensure hypothesis_ids and knowledge_item_ids follow valid format."""
        resolution = resolve_semantic_intent(
            "make the sound quieter",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        # All hypothesis IDs should start with 'hyp_'
        for hyp_id in resolution.hypothesis_ids:
            assert hyp_id.startswith('hyp_'), f"Invalid hypothesis ID: {hyp_id}"

        # All knowledge item IDs should start with 'ki_'
        for ki_id in resolution.knowledge_item_ids:
            assert ki_id.startswith('ki_'), f"Invalid knowledge item ID: {ki_id}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
