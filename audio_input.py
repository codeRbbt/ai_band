"""Low-latency guitar input from a Scarlett 2i2."""

from __future__ import annotations


class LowLatencyGuitarStream:
    def __init__(self, strum_callback, sample_rate: int = 44100, buffer_size: int = 512):
        self.strum_callback = strum_callback
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.sd = None
        self.np = None
        self.onset_detector = None
        self.pitch_detector = None
        self._dependency_error = None

        try:
            import aubio
            import numpy as np
            import sounddevice as sd
        except ImportError as exc:
            self._dependency_error = exc
            return

        self.sd = sd
        self.np = np
        self.onset_detector = aubio.onset("default", buffer_size * 2, buffer_size, sample_rate)
        self.pitch_detector = aubio.pitch("default", buffer_size * 2, buffer_size, sample_rate)
        self.pitch_detector.set_unit("midi")

    def _audio_callback(self, indata, frames, time_info, status):
        if self.onset_detector is None or self.pitch_detector is None:
            return

        audio_buffer = indata[:, 0].astype(self.np.float32)
        if self.onset_detector(audio_buffer):
            detected_pitch = int(round(self.pitch_detector(audio_buffer)[0]))
            if 40 <= detected_pitch <= 88 and self.strum_callback is not None:
                self.strum_callback(detected_pitch)

    def listen(self):
        if self.sd is None:
            raise RuntimeError(
                "real-time audio support requires: "
                "python -m pip install sounddevice aubio numpy"
            ) from self._dependency_error

        print(f"[ai_band] Streaming audio from Scarlett 2i2 ({self.sample_rate} Hz)...")
        with self.sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            callback=self._audio_callback,
        ):
            while True:
                self.sd.sleep(100)
