"""Kernel: Harmonic distortion measure for saturation/drive detection.

Measures total harmonic distortion (THD) — the ratio of harmonic power
to fundamental power. Used to detect drive/saturation parameter effects.

Design:
  1. Compute FFT of the audio signal
  2. Identify the fundamental frequency (dominant peak in low frequencies)
  3. Sum power in harmonic bands (2x, 3x, 4x, etc. the fundamental)
  4. Sum power in the fundamental band
  5. Return THD = harmonic_power / fundamental_power (ratio, not dB)

Drive/saturation increases THD by adding harmonic overtones. When drive
increases:
  - More energy in 2nd, 3rd, 4th... harmonics
  - Fundamental power may also increase slightly
  - THD ratio increases (typical range 0.01 to 1.0+)

This kernel complements spectral_centroid_hz and spectral_kurtosis:
  - Centroid measures frequency shift (cutoff changes)
  - Kurtosis measures peakiness (resonance/Q)
  - THD measures harmonic content (drive/saturation)

Validated on: Filter1.Drive (expected THD increase with high drive).

Returns: Total harmonic distortion ratio (0 to ~2.0 for moderate distortion).
"""
import numpy as np

SR = 44100
HARMONIC_BANDS = 8  # Number of harmonics to include in THD calculation


def kernel(audio, sample_rate=SR, n_harmonics=HARMONIC_BANDS):
    """Measure total harmonic distortion (THD).

    Args:
        audio: Rendered audio (mono or stereo).
        sample_rate: Sample rate (default 44100).
        n_harmonics: Number of harmonics to include (default 8).

    Returns:
        THD ratio (harmonic power / fundamental power).
    """
    x = audio.mean(axis=0) if audio.ndim == 2 else audio
    if len(x) < 256:
        return 0.0  # Insufficient data

    # FFT of the full signal
    n = len(x)
    spec = np.abs(np.fft.rfft(x * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sample_rate)

    if len(spec) < n_harmonics * 2:
        return 0.0

    # Find fundamental frequency (peak in 50-500 Hz range, typical for MIDI note 60)
    # This assumes a pitched note (which it is, in qualification tests)
    fundamental_range = (freqs > 50) & (freqs < 500)
    if not np.any(fundamental_range):
        # No clear fundamental, estimate from spectral centroid
        centroid_idx = np.argmax(spec)
        if centroid_idx == 0:
            return 0.0
        fundamental_freq = freqs[centroid_idx]
    else:
        fundamental_idx = np.argmax(spec[fundamental_range])
        fundamental_freq = freqs[np.where(fundamental_range)[0][fundamental_idx]]

    if fundamental_freq < 20:
        return 0.0  # Not a valid pitch

    # Band width for harmonic detection (±50 Hz around each harmonic)
    bandwidth = 50

    # Measure power in fundamental band
    fundamental_mask = np.abs(freqs - fundamental_freq) < bandwidth
    fundamental_power = np.sum(spec[fundamental_mask] ** 2)

    if fundamental_power < 1e-12:
        return 0.0

    # Measure power in harmonic bands (2x, 3x, 4x, ... fundamental)
    harmonic_power = 0.0
    for h in range(2, n_harmonics + 1):
        harmonic_freq = fundamental_freq * h
        harmonic_mask = np.abs(freqs - harmonic_freq) < bandwidth
        harmonic_power += np.sum(spec[harmonic_mask] ** 2)

    # THD = sqrt(harmonic_power / fundamental_power)
    thd = np.sqrt(harmonic_power / (fundamental_power + 1e-12))

    return float(thd)
