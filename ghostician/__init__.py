"""Ghostician: a real-time AI accompanist for guitar."""

from .comp_generator import generate_backing_tracks
from .engine import Ghostician
from .features import AudioFeatures, analyze_frame
from .realtime_engine import build_chord_messages, build_kick_snare_messages
from .transcriber import transcribe_guitar
from .watcher import GuitarAudioHandler, watch_folder

__all__ = [
    "AudioFeatures",
    "Ghostician",
    "GuitarAudioHandler",
    "analyze_frame",
    "build_chord_messages",
    "build_kick_snare_messages",
    "generate_backing_tracks",
    "transcribe_guitar",
    "watch_folder",
]