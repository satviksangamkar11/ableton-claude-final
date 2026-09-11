"""Tests for semantic intent resolver."""
import pytest
from serum2.knowledge.semantic_intent_resolver import (
    resolve_semantic_intent,
    resolve_intent_batch,
)


class TestIntentResolution:
    """Test semantic intent resolution to existing knowledge."""

    def test_attack_slower_resolves_to_env1_attack(self):
        """Intent 'make the attack slower' → Env1.Attack."""
        resolution = resolve_semantic_intent(
            "make the attack slower",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        assert resolution.resolution_status == "RESOLVED"
        assert resolution.semantic_target == "Env1.Attack"
        assert resolution.semantic_concept == "envelope onset time increase"
        assert len(resolution.hypothesis_ids) == 3  # 3 Env1.Attack hypotheses
        assert resolution.measurement_metric == "rms_db"
        assert resolution.confidence == 0.95

    def test_octave_higher_resolves_to_osc1_octave(self):
        """Intent 'make the oscillator one octave higher' → OSC1.Octave."""
        resolution = resolve_semantic_intent(
            "make the oscillator one octave higher",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        assert resolution.resolution_status == "RESOLVED"
        assert resolution.semantic_target == "OSC1.Octave"
        assert resolution.semantic_concept == "oscillator pitch by octave up"
        assert len(resolution.hypothesis_ids) == 16  # 16 OSC1.Octave hypotheses
        assert resolution.measurement_metric == "pitch_shift_semitones"

    def test_sustain_longer_resolves_to_env1_release(self):
        """Intent 'make the note sustain longer' → Env1.Release."""
        resolution = resolve_semantic_intent(
            "make the note sustain longer",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        assert resolution.resolution_status == "RESOLVED"
        assert resolution.semantic_target == "Env1.Release"
        assert len(resolution.hypothesis_ids) == 7  # 7 Env1.Release hypotheses
        assert resolution.measurement_metric == "tail_rms_db"

    def test_quieter_resolves_to_osc1_level(self):
        """Intent 'make the sound quieter' → OSC1.Level (95 YouTube hypotheses)."""
        resolution = resolve_semantic_intent(
            "make the sound quieter",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        # OSC1.Level now has YouTube knowledge
        assert resolution.resolution_status == "RESOLVED"
        assert resolution.semantic_target == "OSC1.Level"
        assert len(resolution.hypothesis_ids) == 95  # 95 OSC1.Level hypotheses
        assert resolution.measurement_metric == "rms_db"

    def test_brighter_resolves_to_filter_cutoff(self):
        """Intent 'make the sound brighter' → Filter.Cutoff (22 YouTube hypotheses)."""
        resolution = resolve_semantic_intent(
            "make the sound brighter",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        # Filter.Cutoff now has YouTube knowledge
        assert resolution.resolution_status == "RESOLVED"
        assert resolution.semantic_target == "Filter.Cutoff"
        assert len(resolution.hypothesis_ids) == 22  # 22 Filter.Cutoff hypotheses
        assert resolution.measurement_metric == "spectral_centroid_hz"

    def test_detune_resolves_to_osc1_detune(self):
        """Intent 'slightly detune the oscillator' → OSC1.Detune (38 YouTube hypotheses)."""
        resolution = resolve_semantic_intent(
            "slightly detune the oscillator",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        # OSC1.Detune now has YouTube knowledge
        assert resolution.resolution_status == "RESOLVED"
        assert resolution.semantic_target == "OSC1.Detune"
        assert len(resolution.hypothesis_ids) == 38  # 38 OSC1.Detune hypotheses
        assert resolution.measurement_metric == "pitch_shift_semitones"

    def test_unsupported_intent_returns_unsupported(self):
        """Intent that doesn't match known patterns → UNSUPPORTED."""
        resolution = resolve_semantic_intent(
            "make it purple",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        assert resolution.resolution_status == "UNSUPPORTED"
        assert resolution.semantic_target == "UNKNOWN"
        assert len(resolution.hypothesis_ids) == 0

    def test_provenance_preserved(self):
        """Resolution includes provenance to actual hypotheses."""
        resolution = resolve_semantic_intent(
            "make the attack slower",
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        assert resolution.resolution_status == "RESOLVED"
        # Provenance points to actual hypothesis IDs
        assert all(h.startswith("hyp_") for h in resolution.hypothesis_ids)
        # Provenance points to actual knowledge item IDs
        assert all(k.startswith("ki_") for k in resolution.knowledge_item_ids)

    def test_batch_resolution(self):
        """Batch resolution of multiple intents."""
        intents = [
            "make the attack slower",
            "make the oscillator one octave higher",
            "make the sound quieter",
            "make it purple",
        ]

        resolutions = resolve_intent_batch(
            intents,
            "serum2/knowledge/yt_f507169bd7cb_hypotheses.json",
            "serum2/knowledge/yt_f507169bd7cb_target_resolution.json",
        )

        assert len(resolutions) == 4
        assert resolutions[0].resolution_status == "RESOLVED"  # attack slower (3 hypotheses)
        assert resolutions[1].resolution_status == "RESOLVED"  # octave higher (16 hypotheses)
        assert resolutions[2].resolution_status == "RESOLVED"  # quieter (95 hypotheses now)
        assert resolutions[3].resolution_status == "UNSUPPORTED"  # purple (no pattern match)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
