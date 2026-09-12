"""Small MIDI event model and Mido adapter."""

from dataclasses import dataclass
import threading
from typing import Protocol


class EventOutput(Protocol):
    def send(self, event: "MidiEvent") -> None: ...

    def close(self) -> None: ...


@dataclass(frozen=True)
class MidiEvent:
    kind: str
    note: int
    velocity: int
    channel: int
    duration_beats: float = 0.25


class MidiOutput:
    """Send events to a named Mido output, when one is configured."""

    def __init__(self, port_name: str | None = None) -> None:
        self._port = None
        self._timers: list[threading.Timer] = []
        if port_name:
            try:
                import mido
                self._port = mido.open_output(port_name)
            except ImportError as error:
                raise RuntimeError("MIDI ports require python-rtmidi: python -m pip install -e '.[midi]'") from error

    def send(self, event: MidiEvent) -> None:
        if self._port is None:
            return
        import mido

        message_type = "note_on" if event.kind == "note_on" else "note_off"
        self._port.send(mido.Message(message_type, note=event.note, velocity=event.velocity, channel=event.channel))
        if event.kind == "note_on" and event.duration_beats > 0:
            timer = threading.Timer(event.duration_beats * 0.65, self._send_note_off, args=(event,))
            timer.daemon = True
            timer.start()
            self._timers.append(timer)

    def _send_note_off(self, event: MidiEvent) -> None:
        if self._port is None:
            return
        import mido
        self._port.send(mido.Message("note_off", note=event.note, velocity=0, channel=event.channel))

    def close(self) -> None:
        for timer in self._timers:
            timer.cancel()
        self._timers.clear()
        if self._port is not None:
            self._port.close()


class FluidSynthOutput:
    """Render MIDI events through FluidSynth and a SoundFont."""

    def __init__(self, soundfont_path: str, driver: str = "coreaudio") -> None:
        try:
            import fluidsynth
        except ImportError as error:
            raise RuntimeError("FluidSynth output requires: python -m pip install -e '.[fluidsynth]'") from error
        self._synth = fluidsynth.Synth()
        self._soundfont_id = self._synth.sfload(soundfont_path)
        self._synth.start(driver=driver)
        self._timers: list[threading.Timer] = []

    def send(self, event: MidiEvent) -> None:
        if event.kind == "note_on":
            self._synth.noteon(event.channel, event.note, event.velocity)
            if event.duration_beats > 0:
                timer = threading.Timer(event.duration_beats * 0.65, self._send_note_off, args=(event,))
                timer.daemon = True
                timer.start()
                self._timers.append(timer)
        elif event.kind == "note_off":
            self._send_note_off(event)

    def _send_note_off(self, event: MidiEvent) -> None:
        self._synth.noteoff(event.channel, event.note)

    def close(self) -> None:
        for timer in self._timers:
            timer.cancel()
        self._timers.clear()
        self._synth.system_reset()
        self._synth.delete()