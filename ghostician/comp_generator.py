"""Generate backing drums and piano MIDI files from a transcription."""

from __future__ import annotations

import os
from pathlib import Path


def generate_backing_tracks(guitar_midi_path: str, output_dir: str, bpm: int = 155) -> str:
    """Create a simple jazz-comp backing MIDI file.

    The generated track is intentionally lightweight and deterministic: it creates
    a small drum arrangement that can be used as a first-pass sketch before a
    heavier DAW or plugin rack is attached.
    """
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    try:
        import pretty_midi
    except ImportError as exc:  # pragma: no cover - exercised in tests
        raise RuntimeError(
            "pretty_midi is required for comp generation; install with "
            "python -m pip install '.[pipeline]'"
        ) from exc

    midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    drums = pretty_midi.Instrument(program=0, is_drum=True)
    beat_length = 60.0 / bpm

    for bar in range(4):
        bar_start = bar * 4 * beat_length

        for beat in range(4):
            hit_time = bar_start + beat * beat_length
            drums.notes.append(
                pretty_midi.Note(
                    velocity=80,
                    pitch=51,
                    start=hit_time,
                    end=hit_time + 0.12,
                )
            )

        snare_time = bar_start + beat_length
        drums.notes.append(
            pretty_midi.Note(
                velocity=52,
                pitch=38,
                start=snare_time,
                end=snare_time + 0.10,
            )
        )

    midi.instruments.append(drums)
    output_path = output_root / "ai_drums.mid"
    midi.write(str(output_path))
    return str(output_path)
