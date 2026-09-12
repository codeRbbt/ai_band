from pathlib import Path

import pytest

from ghostician.audio_engine import GuitarAudioStream
from ghostician.comp_generator import generate_backing_tracks
from ghostician.comp_rules import JazzCompEngine
from ghostician.realtime_engine import build_chord_messages, build_kick_snare_messages
from ghostician.transcriber import transcribe_guitar
from ghostician.watcher import GuitarAudioHandler


def test_generate_backing_tracks_creates_midi_file(tmp_path):
    output_dir = tmp_path / "out"
    output_dir.mkdir()

    midi_path = generate_backing_tracks(
        guitar_midi_path="/tmp/example.mid",
        output_dir=str(output_dir),
        bpm=155,
    )

    assert Path(midi_path).exists()
    assert Path(midi_path).name == "ai_drums.mid"


def test_transcribe_guitar_reports_missing_basic_pitch_dependency(tmp_path):
    audio_path = tmp_path / "guitar.wav"
    audio_path.write_bytes(b"fake")

    with pytest.raises(RuntimeError, match="basic-pitch"):
        transcribe_guitar(str(audio_path), str(tmp_path))


def test_watcher_processes_new_wav(monkeypatch, tmp_path):
    calls = []

    monkeypatch.setattr("ghostician.watcher.transcribe_guitar", lambda path, out_dir: calls.append((path, out_dir)) or "/tmp/generated.mid")
    monkeypatch.setattr("ghostician.watcher.generate_backing_tracks", lambda midi_path, out_dir, bpm=155: calls.append((midi_path, out_dir, bpm)) or "/tmp/drums.mid")

    handler = GuitarAudioHandler()
    event = type("Event", (), {"is_directory": False, "src_path": str(tmp_path / "clip.wav")})()

    handler.on_created(event)

    assert calls[0][0] == str(tmp_path / "clip.wav")
    assert calls[1][0] == "/tmp/generated.mid"


def test_realtime_engine_builds_jazz_chord_and_drum_messages():
    chord_messages = build_chord_messages(60)
    assert [msg.note for msg in chord_messages] == [60, 64, 70]
    assert all(msg.kind == "note_on" for msg in chord_messages)

    drum_messages = build_kick_snare_messages()
    assert [msg.note for msg in drum_messages] == [36, 51]
    assert all(msg.channel == 9 for msg in drum_messages)


def test_guitar_audio_stream_and_jazz_comp_engine_api_exist():
    stream = GuitarAudioStream(sample_rate=44100, buffer_size=512, callback_fn=lambda pitch: None)
    assert stream.sample_rate == 44100
    assert stream.buffer_size == 512

    assert JazzCompEngine.get_piano_shell(60) == [60, 64, 70]
    assert JazzCompEngine.get_drum_triggers() == [36, 51]
