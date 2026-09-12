"""Optional PyAudio input adapter for real-time guitar frames."""

from contextlib import AbstractContextManager
from typing import Iterator

import numpy as np


class AudioInput(AbstractContextManager):
    """Read mono float frames from a PyAudio input device."""

    def __init__(self, sample_rate: int = 44100, frame_size: int = 2048, device_index: int | None = None) -> None:
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.device_index = device_index
        self._audio = None
        self._stream = None

    def __enter__(self) -> "AudioInput":
        try:
            import pyaudio
        except ImportError as error:
            raise RuntimeError("live input requires the optional audio dependencies: python -m pip install -e '.[audio]'") from error

        self._audio = pyaudio.PyAudio()
        self._stream = self._audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.frame_size,
        )
        return self

    def frames(self) -> Iterator[np.ndarray]:
        if self._stream is None:
            raise RuntimeError("AudioInput must be used as a context manager")
        while True:
            raw = self._stream.read(self.frame_size, exception_on_overflow=False)
            yield np.frombuffer(raw, dtype=np.float32)

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
        if self._audio is not None:
            self._audio.terminate()