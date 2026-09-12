"""Stereo stem mixer with volume, pan, mute, solo, and effects."""

from dataclasses import dataclass

import numpy as np

from .effects_chain import compress, delay, reverb


@dataclass
class TrackState:
    volume: float = 1.0
    pan: float = 0.0
    mute: bool = False
    solo: bool = False
    effects: bool = True


class StemMixer:
    def __init__(self, sample_rate: int = 44100) -> None:
        self.sample_rate = sample_rate
        self.tracks = {
            "keys": TrackState(volume=0.72, pan=-0.2),
            "bass": TrackState(volume=0.8),
            "drums": TrackState(volume=0.78),
        }

    def set_volume(self, name: str, value: float) -> None:
        self.tracks[name].volume = float(np.clip(value, 0, 1))

    def set_pan(self, name: str, value: float) -> None:
        self.tracks[name].pan = float(np.clip(value, -1, 1))

    def set_mute(self, name: str, muted: bool = True) -> None:
        self.tracks[name].mute = muted

    def set_solo(self, name: str, solo: bool = True) -> None:
        self.tracks[name].solo = solo

    def mix(self, stems: dict[str, np.ndarray]) -> np.ndarray:
        if not stems:
            return np.zeros((0, 2), dtype=np.float32)
        length = max(audio.size for audio in stems.values())
        output = np.zeros((length, 2), dtype=np.float32)
        any_solo = any(state.solo for state in self.tracks.values())
        for name, audio in stems.items():
            state = self.tracks.get(name)
            if state is None or state.mute or (any_solo and not state.solo):
                continue
            processed = np.pad(audio, (0, length - audio.size))
            if state.effects:
                processed = reverb(delay(compress(processed), self.sample_rate), self.sample_rate)
            angle = (state.pan + 1) * np.pi / 4
            output[:, 0] += processed * state.volume * np.cos(angle)
            output[:, 1] += processed * state.volume * np.sin(angle)
        return np.tanh(output * 1.2).astype(np.float32)