"""Audio-to-MIDI transcription helpers for guitar recordings."""

from __future__ import annotations

import os
from pathlib import Path


def transcribe_guitar(audio_path: str, output_dir: str) -> str:
    """Convert a guitar recording into a MIDI file using Basic Pitch.

    The function intentionally raises a clear error when the optional pipeline
    dependencies are not installed, so the project can keep its core unit tests
    and CLI usable without heavy audio tooling installed.
    """
    try:
        from basic_pitch.inference import predict_and_save
    except ImportError as exc:  # pragma: no cover - exercised in tests
        raise RuntimeError(
            "basic-pitch is required for audio transcription; install with "
            "python -m pip install '.[pipeline]'"
        ) from exc

    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    input_path = Path(audio_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    base_name = input_path.stem
    predict_and_save(
        audio_path_list=[str(input_path)],
        output_directory=str(output_root),
        save_midi=True,
        sonify_midi=False,
        save_model_outputs=False,
        save_notes=False,
    )

    midi_name = f"{base_name}_basic_pitch.mid"
    midi_path = output_root / midi_name
    if not midi_path.exists():
        midi_path = output_root / "predictions" / f"{base_name}.mid"

    return str(midi_path)
