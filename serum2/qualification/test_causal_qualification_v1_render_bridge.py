#!/usr/bin/env python3
"""Regression test: causal qualification render bridge returns valid audio array."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
from serum2 import codec
from serum2.qualification.causal_qualification_v1_scalar_batch import _render_state

GOLDEN_PRESET = "archive/golden_presets/arp.SerumPreset"


def _load_golden_state():
    """Load golden preset directly."""
    with open(GOLDEN_PRESET, 'rb') as f:
        data = f.read()
    return codec.decode(data)


def test_render_returns_numpy_array():
    """_render_state returns numpy array, not bool."""
    meta, body = _load_golden_state()

    audio = _render_state(meta, body, duration=0.5)

    assert audio is not None, "render returned None"
    assert isinstance(audio, np.ndarray), f"expected ndarray, got {type(audio)}"
    print(f"[PASS] Returns numpy array: {audio.dtype}")


def test_render_returns_expected_sample_count():
    """_render_state produces correct sample count for duration."""
    SR = 44100
    duration = 0.5
    expected_samples = int(SR * duration)

    meta, body = _load_golden_state()
    audio = _render_state(meta, body, duration=duration)

    assert audio is not None, "render returned None"
    sample_count = audio.shape[-1]
    assert sample_count > 0, f"zero samples: {audio.shape}"
    # Allow ±2% tolerance for block rounding
    assert abs(sample_count - expected_samples) / expected_samples < 0.02, \
        f"sample count {sample_count} does not match expected {expected_samples}"
    print(f"[PASS] Sample count correct: {sample_count} samples for {duration}s @ {SR}Hz")


def test_render_returns_finite_samples():
    """_render_state produces finite numeric samples (no NaN/Inf)."""
    meta, body = _load_golden_state()
    audio = _render_state(meta, body, duration=0.5)

    assert audio is not None, "render returned None"
    assert np.all(np.isfinite(audio)), f"audio contains NaN or Inf: {np.sum(~np.isfinite(audio))} non-finite samples"
    print(f"[PASS] All samples are finite")


def test_render_returns_ndarray_with_ndim():
    """_render_state audio has ndim attribute (real array, not bool)."""
    meta, body = _load_golden_state()
    audio = _render_state(meta, body, duration=0.5)

    assert audio is not None, "render returned None"
    assert hasattr(audio, 'ndim'), f"audio object has no ndim attribute: {type(audio)}"
    assert audio.ndim >= 1, f"audio.ndim is {audio.ndim}, expected >= 1"
    print(f"[PASS] Audio has ndim: {audio.ndim}")


if __name__ == "__main__":
    test_render_returns_numpy_array()
    test_render_returns_expected_sample_count()
    test_render_returns_finite_samples()
    test_render_returns_ndarray_with_ndim()
    print("\nALL RENDER BRIDGE REGRESSION TESTS PASSED")
