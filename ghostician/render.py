"""Offline stem renderer for the Ghostician sound-engine MVP."""

from pathlib import Path
import wave

import numpy as np

from .conductor import BandSpec, progression_notes
from .mixer import StemMixer
from .sound_engine import BassSynth, DrumSynth, KeysSynth


SAMPLE_RATE = 44100


def _add(buffer: np.ndarray, sound: np.ndarray, start: int) -> None:
    end = min(buffer.size, start + sound.size)
    if start < end:
        buffer[start:end] += sound[: end - start]


def _write_wav(path: Path, samples: np.ndarray) -> None:
    pcm = (np.clip(samples, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(pcm.tobytes())


def render_background_band(
    path: str | Path,
    seconds: float = 24.0,
    seed: int = 7,
    muted_stems: set[str] | None = None,
    band: BandSpec | None = None,
) -> Path:
    """Render an evolving, mixed stereo backing band to a WAV file."""
    if seconds <= 0:
        raise ValueError("seconds must be positive")
    band = band or BandSpec(duration=seconds)
    seconds = band.duration if seconds == 24.0 and band.duration != 24.0 else seconds
    total_samples = int(SAMPLE_RATE * seconds)
    stems = {name: np.zeros(total_samples, dtype=np.float32) for name in ("keys", "bass", "drums")}
    keys = KeysSynth(SAMPLE_RATE)
    bass = BassSynth(SAMPLE_RATE)
    drums = DrumSynth(SAMPLE_RATE, seed)
    mixer = StemMixer(SAMPLE_RATE)
    for name in muted_stems or set():
        mixer.set_mute(name)

    beat_duration = 60 / band.tempo
    beats = int(seconds / beat_duration)
    bar_beats = band.beats_per_bar
    for beat in range(beats):
        start = int(beat * beat_duration * SAMPLE_RATE)
        tension = 0.5 + 0.5 * np.sin(2 * np.pi * beat / max(1, beats - 1) - np.pi / 2)
        symbol = band.progression[(beat // bar_beats) % len(band.progression)]
        chord = progression_notes(band, symbol)
        bass_root = chord[0] - 24
        bass_targets = (bass_root, chord[2] - 12, chord[1] - 12, chord[0] - 12)
        bass_note = bass_targets[beat % len(bass_targets)]
        bass_duration = beat_duration * (0.62 if band.bass_style in ("upright", "1970s_jazz") else 0.72)
        if "bass" in band.instruments:
            _add(stems["bass"], bass.note(bass_note, bass_duration, 72 + int(tension * 30), band.bass_style), start)

        # Rootless shell voicing: 3rd, 7th, and color tone, voiced above middle C.
        piano_notes = tuple(note + 12 for note in (chord[1], chord[3], chord[2]))
        if "keys" in band.instruments:
            chord_start = start + int(beat_duration * SAMPLE_RATE * (0.0 if beat % 2 == 0 else 0.67))
            _add(stems["keys"], keys.chord(piano_notes, beat_duration * 0.42, 48 + int(tension * 24), tension), chord_start)

        if "drums" not in band.instruments:
            continue
        # Jazz kick feathers time; it avoids the four-on-the-floor techno pulse.
        kick_velocity = 34 + int(tension * 12) if band.drum_style in ("jazz", "brush") else 70 + int(tension * 20)
        if beat % bar_beats in (0, 2) or band.drum_style not in ("jazz", "brush"):
            _add(stems["drums"], drums.hit("kick", kick_velocity), start)
        if band.drum_style == "brush":
            _add(stems["drums"], drums.hit("brush", 72 + int(tension * 15)), start + int(beat_duration * SAMPLE_RATE * 0.25))
        backbeat = (1, 3) if band.drum_style in ("rock", "blues") else ((2,) if band.drum_style in ("jazz", "brush") else (1, 3))
        if beat % bar_beats in backbeat:
            snare_velocity = 92 + int(tension * 18) if band.drum_style == "brush" else 65 + int(tension * 25)
            _add(stems["drums"], drums.hit("snare", snare_velocity), start)
        half_beat = start + int(beat_duration * SAMPLE_RATE * 0.67)
        if band.drum_style in ("jazz", "brush"):
            _add(stems["drums"], drums.hit("ride", 42 + int(tension * 22)), start)
        else:
            _add(stems["drums"], drums.hit("hat", 35 + int(tension * 30)), half_beat)
        if tension > 0.72 and beat % bar_beats == bar_beats - 1:
            _add(stems["drums"], drums.hit("tom", 85), half_beat)

    mixed = mixer.mix(stems)
    destination = Path(path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    _write_wav(destination, mixed)
    return destination