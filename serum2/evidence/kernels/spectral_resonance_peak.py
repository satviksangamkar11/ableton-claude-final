"""Kernel: Spectral peakiness (kurtosis-based measure of resonance/Q).

Measures the sharpness/concentration of energy in the frequency spectrum
to detect resonance/Q parameter effects.

Design:
  1. Compute FFT of the entire audio signal
  2. Normalize spectrum to a probability distribution (energy per bin)
  3. Compute spectral kurtosis (concentration/peakiness)
  4. High kurtosis = narrow peaks (high Q), Low kurtosis = flat (low Q)

Resonance increases Q, which makes spectral peaks sharper and narrower.
Unlike peak power (which can be dominated by overall amplitude), kurtosis
captures the DISTRIBUTION of energy across frequency bins.

This kernel complements spectral_centroid_hz:
  - Centroid measures frequency SHIFT (e.g., cutoff change +2684 Hz)
  - Peakiness measures SHARPNESS/Q change (high Q -> high kurtosis)

Validated on: FXEQ.Reso1/2 (expected Q increase -> kurtosis increase).

Returns: Spectral kurtosis (dimensionless, typical range 1-10+).
"""
import numpy as np

SR = 44100


def kernel(audio, sample_rate=SR):
    """Measure spectral peakiness (kurtosis).

    Args:
        audio: Rendered audio (mono or stereo).
        sample_rate: Sample rate (default 44100).

    Returns:
        Spectral kurtosis (dimensionless measure of peakiness).
    """
    x = audio.mean(axis=0) if audio.ndim == 2 else audio
    if len(x) < 64:
        return 1.0  # Silence = flat spectrum

    # FFT of the full signal
    n = len(x)
    spec = np.abs(np.fft.rfft(x * np.hanning(n)))

    if len(spec) == 0 or np.all(spec == 0):
        return 1.0

    # Normalize spectrum to a probability distribution
    spec_normalized = spec / (np.sum(spec) + 1e-12)

    # Spectral kurtosis: E[(X - mu)^4] / (E[(X - mu)^2])^2
    # High kurtosis = narrow, peaky distribution (high Q resonance)
    # Low kurtosis = flat distribution (no resonance)
    mean = np.mean(spec_normalized)
    centered = spec_normalized - mean
    variance = np.mean(centered ** 2)

    if variance < 1e-12:
        return 1.0  # Flat spectrum

    kurtosis = np.mean(centered ** 4) / (variance ** 2)

    return float(kurtosis)
