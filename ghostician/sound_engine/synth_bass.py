"""Subtractive triangle/sine bass voice."""

import numpy as np

from .voice import envelope, midi_frequency


class BassSynth:
    def __init__(self, sample_rate: int = 44100) -> None:
        self.sample_rate = sample_rate

    def note(self, note: int, duration: float, velocity: int = 80, style: str = "upright") -> np.ndarray:
        length = max(1, int(self.sample_rate * duration))
        time = np.arange(length, dtype=np.float32) / self.sample_rate
        frequency = midi_frequency(note)
        triangle = 2 * np.abs(2 * ((frequency * time) % 1) - 1) - 1
        if style == "1970s_jazz":
            sound = triangle * 0.45 + np.sin(2 * np.pi * frequency * time) * 0.55
            sound += 0.08 * np.sin(2 * np.pi * frequency * 2 * time)
            attack, release = 0.012, 0.22
        elif style == "electric":
            sound = triangle * 0.7 + np.sin(2 * np.pi * frequency * time) * 0.3
            attack, release = 0.004, 0.12
        else:
            sound = triangle * 0.7 + np.sin(2 * np.pi * frequency * time) * 0.3
            attack, release = 0.004, 0.12
        sound *= envelope(self.sample_rate, length, attack, release)
        return (sound * (velocity / 127) * 0.42).astype(np.float32)