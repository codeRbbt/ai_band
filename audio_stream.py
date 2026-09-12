"""Low-latency live guitar stream for Focusrite Scarlett 2i2 input."""

from __future__ import annotations


class RealTimeGuitarStream:
    def __init__(self, callback, sample_rate: int = 44100, buffer_size: int = 512):
        self.callback = callback
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.sd = None
        self.aubio = None
        self.onset_detector = None
        self.pitch_detector = None

        try:
            import aubio
            import numpy as np
            import sounddevice as sd
        except ImportError:
            return

        self.sd = sd
        self.aubio = aubio
        self.np = np

        self.onset_detector = aubio.onset("default", buffer_size * 2, buffer_size, sample_rate)
        self.pitch_detector = aubio.pitch("default", buffer_size * 2, buffer_size, sample_rate)
        self.pitch_detector.set_unit("midi")

    def _process_audio(self, indata, frames, time_info, status):
        if self.sd is None or self.onset_detector is None or self.pitch_detector is None:
            return

        audio_buffer = indata[:, 0].astype(self.np.float32)
        if self.onset_detector(audio_buffer):
            pitch = int(round(self.pitch_detector(audio_buffer)[0]))
            if 36 <= pitch <= 84 and self.callback is not None:
                self.callback(pitch)

    def start(self):
        if self.sd is None:
            raise RuntimeError("real-time audio support requires: python -m pip install sounddevice aubio")

        print(f"[ai_band] Listening to Scarlett 2i2 on Input 1 ({self.sample_rate}Hz)...")
        with self.sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            callback=self._process_audio,
        ):
            while True:
                self.sd.sleep(100)
