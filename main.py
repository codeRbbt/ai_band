"""Real-time MIDI router for the ai_band architecture."""

from __future__ import annotations

import mido

from audio_engine import GuitarAudioStream
from comp_rules import JazzCompEngine

MIDI_PORT_NAME = "IAC Driver Bus 1"

try:
    midi_out = mido.open_output(MIDI_PORT_NAME)
    print(f"[ai_band] Connected to Virtual MIDI: {MIDI_PORT_NAME}")
except Exception as exc:  # pragma: no cover - live environment only
    print(f"[ai_band] Error: Ensure IAC Driver is enabled in Mac Audio MIDI Setup. {exc}")
    raise SystemExit(1)


def handle_guitar_strum(pitch: int) -> None:
    print(f"[ai_band] Strum detected! Root Pitch: {pitch}")

    for note in JazzCompEngine.get_piano_shell(pitch):
        midi_out.send(mido.Message("note_on", channel=0, note=note, velocity=85))

    for drum_note in JazzCompEngine.get_drum_triggers():
        midi_out.send(mido.Message("note_on", channel=9, note=drum_note, velocity=90))


if __name__ == "__main__":
    stream = GuitarAudioStream(callback_fn=handle_guitar_strum)
    stream.start()
