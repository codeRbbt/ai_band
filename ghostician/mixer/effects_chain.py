"""Small dependency-free effects for rendered stems."""

import numpy as np


def compress(audio: np.ndarray, threshold: float = 0.55, ratio: float = 3.0) -> np.ndarray:
    magnitude = np.abs(audio)
    over = np.maximum(0, magnitude - threshold)
    return np.sign(audio) * (np.minimum(magnitude, threshold) + over / ratio)


def delay(audio: np.ndarray, sample_rate: int, seconds: float = 0.18, feedback: float = 0.22) -> np.ndarray:
    output = audio.copy()
    offset = max(1, int(sample_rate * seconds))
    if offset < audio.size:
        output[offset:] += audio[:-offset] * feedback
    return output


def reverb(audio: np.ndarray, sample_rate: int, mix: float = 0.12) -> np.ndarray:
    result = audio.copy()
    for seconds, gain in ((0.037, 0.3), (0.071, 0.18), (0.113, 0.1)):
        offset = int(sample_rate * seconds)
        if offset < audio.size:
            result[offset:] += audio[:-offset] * gain * mix
    return result