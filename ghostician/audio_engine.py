"""Low-latency guitar audio stream and onset detection helpers."""

from __future__ import annotations

from typing import Callable


class GuitarAudioStream:
    """Wrap low-latency audio capture and pitch detection for real-time guitar input."""

    def __init__(self, sample_rate: int = 44100, buffer_size: int = 512, callback_fn: Callable[[int], None] | None = None):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.callback_fn = callback_fn
        self.aubio = None
        self.np = None
        self.sd = None
        self.onset_det = None
        self.pitch_det = None

        try:
            import aubio
            import numpy as np
            import sounddevice as sd
        except ImportError:
            self.aubio = None
            self.np = None
            self.sd = None
            return

        self.aubio = aubio
        self.np = np
        self.sd = sd

        self.onset_det = aubio.onset("default", buffer_size * 2, buffer_size, sample_rate)
        self.pitch_det = aubio.pitch("default", buffer_size * 2, buffer_size, sample_rate)
        self.pitch_det.set_unit("midi")

    def _audio_callback(self, indata, frames, time_info, status):
        audio_buffer = indata[:, 0].astype(self.np.float32)
        if self.onset_det(audio_buffer):
            midi_pitch = int(round(self.pitch_det(audio_buffer)[0]))
            if 36 <= midi_pitch <= 84 and self.callback_fn is not None:
                self.callback_fn(midi_pitch)

    def start(self):
        if self.sd is None or self.aubio is None:
            raise RuntimeError(
                "real-time audio support requires: python -m pip install sounddevice aubio"
            )

        print(f"[ai_band] Listening to Scarlett 2i2 at {self.sample_rate}Hz...")
        with self.sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            callback=self._audio_callback,
        ):
            while True:
                self.sd.sleep(100)
