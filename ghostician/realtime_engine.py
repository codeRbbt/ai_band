"""Optional real-time MIDI helper layer for live guitar-triggered comping."""

from __future__ import annotations

from .midi import MidiEvent


def build_chord_messages(root_note: int) -> list[MidiEvent]:
    """Create a simple jazz shell voicing from a detected guitar root note."""
    return [
        MidiEvent(kind="note_on", note=root_note, velocity=85, channel=0, duration_beats=0.5),
        MidiEvent(kind="note_on", note=root_note + 4, velocity=85, channel=0, duration_beats=0.5),
        MidiEvent(kind="note_on", note=root_note + 10, velocity=85, channel=0, duration_beats=0.5),
    ]


def build_kick_snare_messages() -> list[MidiEvent]:
    """Create a minimal syncopated kick/ride pair for a live comping loop."""
    return [
        MidiEvent(kind="note_on", note=36, velocity=90, channel=9, duration_beats=0.25),
        MidiEvent(kind="note_on", note=51, velocity=75, channel=9, duration_beats=0.25),
    ]
