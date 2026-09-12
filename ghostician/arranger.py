"""Rule-based first arranger for the Ghostician prototype."""

from .features import AudioFeatures
from .midi import MidiEvent


def _note(kind: str, note: int, velocity: int, channel: int, duration: float = 0.25) -> MidiEvent:
    return MidiEvent(kind, note, max(1, min(127, velocity)), channel, duration)


def arrange(features: AudioFeatures, tension: float, beat: int = 0) -> list[MidiEvent]:
    """Create one beat of accompaniment for the current guitar state."""
    if features.pitch_hz is None or features.rms < 0.008:
        return []
    root = int(round(69 + 12 * __import__("math").log2(features.pitch_hz / 440)))
    root = max(36, min(72, root))
    velocity = int(42 + tension * 0.55)
    events = [_note("note_on", root - 12, velocity, 1, 0.8)]

    if tension < 35:
        piano_notes = (root + 4, root + 7)
    elif tension < 70:
        piano_notes = (root + 3, root + 7, root + 10)
    else:
        piano_notes = (root + 1, root + 4, root + 8, root + 10)
    events.extend(_note("note_on", note, velocity - 8, 0, 0.45) for note in piano_notes)

    drum_note = 42 if tension < 65 else 51
    events.append(_note("note_on", drum_note, min(127, velocity + 5), 9, 0.1))
    if beat % 4 == 3 and tension > 72:
        events.extend(_note("note_on", note, velocity, 9, 0.1) for note in (38, 40))
    return events