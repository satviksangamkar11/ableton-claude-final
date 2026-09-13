#!/usr/bin/env python
"""Unit tests for the YouTube transcript resolver, mocking TranscriptList/Transcript.

Covers: manual English, generated English, manual non-English, generated
non-English, translatable transcript, no transcript, network/API failure,
malformed URL, Shorts URL, standard watch URL.

No live YouTube calls in this file - see test_youtube_live.py for the two
explicit live integration tests.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "source"))

from youtube_transcript_resolver import resolve_youtube_transcript  # noqa: E402
from fetch_youtube import extract_video_id  # noqa: E402


class FakeSnippet:
    def __init__(self, text, start, duration):
        self.text = text
        self.start = start
        self.duration = duration


class FakeTranscript:
    def __init__(self, language, language_code, is_generated, is_translatable=False,
                 translation_languages=None, snippets=None, fetch_error=None):
        self.language = language
        self.language_code = language_code
        self.is_generated = is_generated
        self.is_translatable = is_translatable
        self.translation_languages = translation_languages or []
        self._snippets = snippets or [FakeSnippet("hello world", 0.0, 1.0)]
        self._fetch_error = fetch_error

    def fetch(self):
        if self._fetch_error:
            raise self._fetch_error
        return list(self._snippets)

    def translate(self, lang_code):
        if not self.is_translatable:
            raise RuntimeError("not translatable")
        return FakeTranscript(f"{self.language} (translated)", lang_code, self.is_generated,
                               snippets=self._snippets)


class FakeTranscriptList:
    def __init__(self, transcripts):
        self._transcripts = transcripts

    def __iter__(self):
        return iter(self._transcripts)


def _patch_api(transcript_list=None, list_error=None):
    mock_api_cls = MagicMock()
    mock_api_instance = MagicMock()
    if list_error is not None:
        mock_api_instance.list.side_effect = list_error
    else:
        mock_api_instance.list.return_value = transcript_list
    mock_api_cls.return_value = mock_api_instance
    return patch("youtube_transcript_api.YouTubeTranscriptApi", mock_api_cls)


# --- A. manual English ---
def test_manual_english():
    tl = FakeTranscriptList([FakeTranscript("English", "en", is_generated=False)])
    with _patch_api(tl):
        r = resolve_youtube_transcript("vid1")
    assert r.status == "AVAILABLE"
    assert r.language_code == "en"
    assert r.is_generated is False
    assert r.segment_count == 1


# --- B. generated English ---
def test_generated_english():
    tl = FakeTranscriptList([FakeTranscript("English", "en", is_generated=True)])
    with _patch_api(tl):
        r = resolve_youtube_transcript("vid2")
    assert r.status == "AVAILABLE"
    assert r.is_generated is True


# --- C. manual non-English ---
def test_manual_non_english():
    tl = FakeTranscriptList([FakeTranscript("Deutsch", "de", is_generated=False)])
    with _patch_api(tl):
        r = resolve_youtube_transcript("vid3", preferred_languages=["de"])
    assert r.status == "AVAILABLE"
    assert r.language_code == "de"
    assert r.is_generated is False


# --- D. generated non-English ---
def test_generated_non_english():
    tl = FakeTranscriptList([FakeTranscript("Deutsch", "de", is_generated=True)])
    with _patch_api(tl):
        r = resolve_youtube_transcript("vid4")
    assert r.status == "AVAILABLE"
    assert r.language_code == "de"
    assert r.is_generated is True


# --- E. translatable transcript ---
# Direct fetch of the source-language track fails (simulating a track that
# cannot be fetched in its own language but can be translated), forcing the
# resolver past steps 5/6 (other available language) into step 7 (translate).
def test_translatable_transcript():
    tl = FakeTranscriptList([
        FakeTranscript("Japanese", "ja", is_generated=True, is_translatable=True,
                        fetch_error=RuntimeError("native fetch unavailable")),
    ])
    with _patch_api(tl):
        r = resolve_youtube_transcript("vid5")
    assert r.status == "TRANSLATED"
    assert r.is_translated is True
    assert r.original_language == "ja"
    assert r.translated_language == "en"


# --- F. no transcript ---
def test_no_transcript():
    from youtube_transcript_api._errors import TranscriptsDisabled
    with _patch_api(list_error=TranscriptsDisabled("novid")):
        r = resolve_youtube_transcript("vid6")
    assert r.status == "NO_TRANSCRIPT"


# --- G. network/API failure ---
def test_network_error():
    from youtube_transcript_api._errors import YouTubeRequestFailed
    with _patch_api(list_error=YouTubeRequestFailed("novid", MagicMock())):
        r = resolve_youtube_transcript("vid7")
    assert r.status in ("NETWORK_ERROR", "API_ERROR")


def test_no_supported_language_when_nothing_matches_and_untranslatable():
    # No en, no other requested language, untranslatable.
    # Falls through all steps because the non-English track can be fetched but doesn't match any preference.
    # The resolver will fetch it (step 5 or 6) and return it as AVAILABLE.
    # To get NO_SUPPORTED_LANGUAGE, all candidates must either fail to fetch or be absent.
    tl = FakeTranscriptList([
        FakeTranscript("Klingon", "tlh", is_generated=True, is_translatable=False,
                        fetch_error=RuntimeError("unable to fetch tlh")),
    ])
    with _patch_api(tl):
        r = resolve_youtube_transcript("vid8")
    assert r.status == "NO_SUPPORTED_LANGUAGE"


# --- H. malformed URL ---
def test_malformed_url():
    import pytest
    with pytest.raises(ValueError):
        extract_video_id("https://example.com/not-a-youtube-link")


# --- I. Shorts URL ---
def test_shorts_url():
    assert extract_video_id("https://www.youtube.com/shorts/QqYlEc_6E6A") == "QqYlEc_6E6A"


# --- J. standard watch URL ---
def test_watch_url():
    assert extract_video_id("https://www.youtube.com/watch?v=oW4C7txJEgM&t=349s") == "oW4C7txJEgM"


def test_youtu_be_url():
    assert extract_video_id("https://youtu.be/oW4C7txJEgM") == "oW4C7txJEgM"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
