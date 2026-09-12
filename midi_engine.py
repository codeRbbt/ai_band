"""Asynchronous jazz accompaniment output over CoreMIDI."""

from __future__ import annotations

from queue import Queue
from threading import Event, Thread

import mido


class RealTimeMidiBand:
    def __init__(self, port_name: str = "ai_band Bus 1", midi_out=None):
        self.port_name = port_name
        self.midi_out = midi_out if midi_out is not None else self._open_output(port_name)
        self._events = Queue()
        self._stopped = Event()
        self._worker = Thread(target=self._dispatch_events, name="midi-dispatch", daemon=True)
        self._worker.start()

    @staticmethod
    def _open_output(port_name):
        try:
            midi_out = mido.open_output(port_name)
        except Exception as exc:
            raise RuntimeError(
                "CoreMIDI unavailable. Ensure IAC Driver is enabled in Audio MIDI Setup."
            ) from exc

        print(f"[ai_band] Virtual MIDI routing active on: {port_name}")
        return midi_out

    def trigger_accompaniment(self, root_pitch: int) -> None:
        self._events.put(root_pitch)

    def _dispatch_events(self) -> None:
        while not self._stopped.is_set():
            root_pitch = self._events.get()
            if root_pitch is None:
                self._events.task_done()
                return

            print(f"[Live Event] Guitar Strum -> Root Pitch: {root_pitch}")
            piano_shell = [root_pitch, root_pitch + 4, root_pitch + 10]
            for note in piano_shell:
                self.midi_out.send(mido.Message("note_on", channel=0, note=note, velocity=82))

            self.midi_out.send(mido.Message("note_on", channel=9, note=36, velocity=88))
            self.midi_out.send(mido.Message("note_on", channel=9, note=51, velocity=75))
            self._events.task_done()

    def close(self) -> None:
        if self._stopped.is_set():
            return

        self._stopped.set()
        self._events.put(None)
        self._worker.join(timeout=1)
        close = getattr(self.midi_out, "close", None)
        if close is not None:
            close()
