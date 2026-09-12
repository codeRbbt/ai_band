"""FM/additive electric-piano style keys voice."""

import numpy as np

from .voice import envelope, midi_frequency


class KeysSynth:
    def __init__(self, sample_rate: int = 44100) -> None:
        self.sample_rate = sample_rate

    def note(self, note: int, duration: float, velocity: int = 80, tension: float = 0.0) -> np.ndarray:
        length = max(1, int(self.sample_rate * duration))
        time = np.arange(length, dtype=np.float32) / self.sample_rate
        frequency = midi_frequency(note)
        carrier = np.sin(2 * np.pi * frequency * time)
        bell = np.sin(2 * np.pi * frequency * (2.0 + tension * 1.2) * time) * np.exp(-7 * time)
        body = 0.35 * np.sin(2 * np.pi * frequency * 2 * time)
        sound = (carrier + body + (0.2 + tension * 0.25) * bell) * envelope(self.sample_rate, length, 0.008, 0.2)
        return (sound * (velocity / 127) * 0.22).astype(np.float32)

    def chord(self, notes: tuple[int, ...], duration: float, velocity: int = 80, tension: float = 0.0) -> np.ndarray:
        voices = [self.note(note, duration, velocity, tension) for note in notes]
        return np.sum(voices, axis=0, dtype=np.float32) if voices else np.zeros(1, dtype=np.float32)