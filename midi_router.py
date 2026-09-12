"""Live virtual MIDI router for Ableton Live and Addictive Keys/Drums."""

from __future__ import annotations

import mido

from audio_stream import RealTimeGuitarStream

MIDI_PORT = "IAC Driver Bus 1"


try:
    midi_out = mido.open_output(MIDI_PORT)
    print(f"[ai_band] Connected to virtual MIDI: {MIDI_PORT}")
except Exception as exc:  # pragma: no cover - live environment only
    print(f"[ai_band] Error: Ensure IAC Driver is active in Mac Audio MIDI Setup. Details: {exc}")
    midi_out = None


def on_guitar_strum(root_pitch: int) -> None:
    print(f"[Live Trigger] Strum Detected! Root: {root_pitch}")
    if midi_out is None:
        return

    piano_chord = [root_pitch, root_pitch + 4, root_pitch + 10]
    for note in piano_chord:
        midi_out.send(mido.Message("note_on", channel=0, note=note, velocity=80))

    for drum_note in (36, 51):
        midi_out.send(mido.Message("note_on", channel=9, note=drum_note, velocity=85 if drum_note == 36 else 75))


if __name__ == "__main__":
    engine = RealTimeGuitarStream(callback=on_guitar_strum)
    engine.start()
