"""Procedural kick, snare, hat, and tom voices."""

import numpy as np


class DrumSynth:
    def __init__(self, sample_rate: int = 44100, seed: int = 7) -> None:
        self.sample_rate = sample_rate
        self.rng = np.random.default_rng(seed)

    def hit(self, name: str, velocity: int = 90, duration: float | None = None) -> np.ndarray:
        duration = duration or {"kick": 0.24, "snare": 0.18, "hat": 0.06, "brush": 0.32, "ride": 0.11, "tom": 0.2}.get(name, 0.1)
        length = max(1, int(self.sample_rate * duration))
        time = np.arange(length, dtype=np.float32) / self.sample_rate
        level = velocity / 127
        if name == "kick":
            frequency = 120 - 75 * np.minimum(1, time / duration)
            phase = 2 * np.pi * np.cumsum(frequency) / self.sample_rate
            sound = np.sin(phase) * np.exp(-18 * time) * 0.8
        elif name == "tom":
            sound = np.sin(2 * np.pi * 145 * time) * np.exp(-15 * time) * 0.55
        elif name == "brush":
            noise = self.rng.normal(0, 1, length).astype(np.float32)
            sweep = np.sin(2 * np.pi * 2.2 * time) * 0.5 + 0.5
            sound = noise * np.exp(-3.5 * time) * (0.08 + 0.16 * sweep)
        elif name == "ride":
            noise = self.rng.normal(0, 1, length).astype(np.float32)
            ping = np.sin(2 * np.pi * 3100 * time) * np.exp(-22 * time)
            sound = (noise * 0.1 + ping * 0.55) * np.exp(-7 * time)
        elif name == "snare":
            noise = self.rng.normal(0, 1, length).astype(np.float32)
            crack = np.sin(2 * np.pi * 185 * time) * np.exp(-28 * time)
            sound = (noise * 0.42 + crack * 0.28) * np.exp(-16 * time)
        else:
            sound = self.rng.normal(0, 1, length).astype(np.float32)
            sound *= np.exp((-35 if name == "hat" else -22) * time)
            sound *= 0.12 if name == "hat" else 0.3
        return (sound * level).astype(np.float32)