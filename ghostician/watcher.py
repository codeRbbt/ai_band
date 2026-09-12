"""Monitor a directory for WAV exports and trigger the AI band pipeline."""

from __future__ import annotations

import time
from pathlib import Path

from .comp_generator import generate_backing_tracks
from .transcriber import transcribe_guitar


class GuitarAudioHandler:
    """Simple callback-style handler for file-system events."""

    def __init__(self, watch_directory: str | None = None, output_directory: str | None = None, bpm: int = 155):
        self.watch_directory = Path(watch_directory) if watch_directory else None
        self.output_directory = Path(output_directory) if output_directory else Path.home() / "Desktop"
        self.bpm = bpm

    def on_created(self, event) -> None:
        if getattr(event, "is_directory", False):
            return
        if not str(event.src_path).lower().endswith(".wav"):
            return

        source_path = str(event.src_path)
        generated_midi = transcribe_guitar(source_path, str(self.output_directory))
        generate_backing_tracks(generated_midi, str(self.output_directory), bpm=self.bpm)


def watch_folder(watch_directory: str, output_directory: str | None = None, bpm: int = 155) -> None:
    """Run a polling watcher loop for WAV exports."""
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "watchdog is required for the folder watcher; install with "
            "python -m pip install '.[pipeline]'"
        ) from exc

    class _EventHandler(FileSystemEventHandler):
        def __init__(self, handler: GuitarAudioHandler):
            self.handler = handler

        def on_created(self, event):
            self.handler.on_created(event)

    directory = Path(watch_directory)
    directory.mkdir(parents=True, exist_ok=True)
    output_root = Path(output_directory) if output_directory else Path.home() / "Desktop"
    output_root.mkdir(parents=True, exist_ok=True)
    event_handler = _EventHandler(GuitarAudioHandler(str(directory), str(output_root), bpm=bpm))
    observer = Observer()
    observer.schedule(event_handler, str(directory), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
