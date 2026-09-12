"""Shared synthesis helpers."""

import numpy as np


def midi_frequency(note: int) -> float:
    return 440.0 * 2 ** ((note - 69) / 12)


def envelope(sample_rate: int, length: int, attack: float, release: float) -> np.ndarray:
    result = np.ones(length, dtype=np.float32)
    attack_samples = min(length, max(1, int(sample_rate * attack)))
    release_samples = min(length, max(1, int(sample_rate * release)))
    result[:attack_samples] = np.linspace(0, 1, attack_samples, endpoint=False)
    result[-release_samples:] *= np.linspace(1, 0, release_samples)
    return result