"""Compatibility names for the live guitar stream."""

from audio_input import LowLatencyGuitarStream


class RealTimeGuitarStream(LowLatencyGuitarStream):
    def __init__(self, callback, sample_rate: int = 44100, buffer_size: int = 512):
        super().__init__(callback, sample_rate=sample_rate, buffer_size=buffer_size)

    def start(self):
        self.listen()
