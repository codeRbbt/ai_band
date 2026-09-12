"""Audio-frame feature extraction with no hardware dependency."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AudioFeatures:
    """Musically useful measurements for one input frame."""

    rms: float
    pitch_hz: float | None
    note_density: float
    register: float
    attack: float


def _estimate_pitch(samples: np.ndarray, sample_rate: int) -> float | None:
    centered = samples - np.mean(samples)
    crossings = np.flatnonzero(np.diff(np.signbit(centered)))
    if len(crossings) < 2:
        return None
    periods = np.diff(crossings) * 2
    period = float(np.median(periods[periods > 0])) if np.any(periods > 0) else 0
    if period <= 0:
        return None
    pitch = sample_rate / period
    return pitch if 30 <= pitch <= 1400 else None


def analyze_frame(
    samples: np.ndarray,
    sample_rate: int,
    previous_rms: float = 0.0,
) -> AudioFeatures:
    """Extract normalized features from a mono audio frame."""
    values = np.asarray(samples, dtype=np.float32).reshape(-1)
    if values.size == 0:
        raise ValueError("audio frame cannot be empty")
    rms = float(np.sqrt(np.mean(values * values)))
    pitch = _estimate_pitch(values, sample_rate)
    zero_crossings = np.count_nonzero(np.diff(np.signbit(values - np.mean(values))))
    note_density = min(1.0, zero_crossings / max(1, values.size * 0.12))
    register = 0.0 if pitch is None else float(np.clip((pitch - 60) / 720, 0, 1))
    attack = float(np.clip((rms - previous_rms) / 0.25, 0, 1))
    return AudioFeatures(rms, pitch, note_density, register, attack)