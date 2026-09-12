"""Command-line entry point for the Ghostician prototype."""

import argparse
import math
import time

import numpy as np

from .engine import Ghostician
from .conductor import parse_band_request
from .features import analyze_frame
from .midi import FluidSynthOutput, MidiOutput
from .render import render_background_band


def main() -> None:
    parser = argparse.ArgumentParser(prog="ghostician")
    parser.add_argument("--demo", action="store_true", help="print the offline accompaniment demo")
    parser.add_argument("--render-demo", metavar="PATH", help="render a playable background band WAV")
    parser.add_argument("--band", metavar="REQUEST", help="natural-language band direction to render")
    parser.add_argument("--seconds", type=float, default=24.0, help="length of the rendered band")
    parser.add_argument("--live", action="store_true", help="analyze live mono input from the default audio device")
    parser.add_argument("--device", type=int, help="PyAudio input device index")
    parser.add_argument("--midi-port", help="Mido output port name")
    parser.add_argument("--soundfont", help="SoundFont path for direct FluidSynth output")
    parser.add_argument("--list-midi", action="store_true", help="list available MIDI output ports")
    parser.add_argument("--realtime", action="store_true", help="emit a simple live MIDI comp shell using the realtime helper layer")
    args = parser.parse_args()
    band = parse_band_request(args.band) if args.band else None
    if args.list_midi:
        try:
            import mido

            for port_name in mido.get_output_names():
                print(port_name)
        except (ImportError, RuntimeError) as error:
            print(f"MIDI discovery unavailable: install the optional backend with python -m pip install -e '.[midi]' ({error})")
        return
    if args.render_demo:
        render_seconds = band.duration if band else args.seconds
        destination = render_background_band(args.render_demo, render_seconds, band=band)
        print(f"Rendered {render_seconds:.1f}s background band to {destination}")
        return
    if args.realtime:
        from .realtime_engine import build_chord_messages, build_kick_snare_messages

        print("[Real-time AI] demo chord messages:")
        for message in build_chord_messages(60):
            print(message)
        print("[Real-time AI] demo drum messages:")
        for message in build_kick_snare_messages():
            print(message)
        return
    if args.live:
        _run_live(args.device, args.seconds, args.midi_port, args.soundfont)
        return
    if not args.demo:
        parser.error("live capture is not wired yet; use --demo or --render-demo PATH")
    sample_rate = 44100
    engine = Ghostician()
    for frame_number in range(8):
        frequency = 110 + frame_number * 18
        samples = 0.16 * np.sin(2 * math.pi * frequency * np.arange(2048) / sample_rate)
        features = analyze_frame(samples, sample_rate, engine.previous_rms)
        score, events = engine.process(features)
        print(f"frame={frame_number} pitch={features.pitch_hz or 0:.1f}Hz tension={score:05.2f} events={events}")


def _run_live(device_index: int | None, duration: float, midi_port: str | None, soundfont: str | None) -> None:
    from .capture import AudioInput

    output = None
    started = time.monotonic()
    try:
        output = _make_output(midi_port, soundfont)
        engine = Ghostician(output=output)
        with AudioInput(device_index=device_index) as audio:
            print("Listening for guitar input. Press Ctrl-C to stop.")
            for frame in audio.frames():
                features = analyze_frame(frame, audio.sample_rate, engine.previous_rms)
                score, events = engine.process(features)
                print(f"pitch={features.pitch_hz or 0:6.1f}Hz tension={score:05.2f} events={len(events)}")
                if duration > 0 and time.monotonic() - started >= duration:
                    break
    except RuntimeError as error:
        print(f"Live input unavailable: {error}")
    except KeyboardInterrupt:
        print("\nStopped listening.")
    finally:
        if output is not None:
            output.close()


def _make_output(midi_port: str | None, soundfont: str | None):
    if midi_port and soundfont:
        raise RuntimeError("choose either --midi-port or --soundfont, not both")
    if midi_port:
        return MidiOutput(midi_port)
    if soundfont:
        return FluidSynthOutput(soundfont)
    return None