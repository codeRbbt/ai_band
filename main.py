"""Entry point for the live guitar accompaniment engine."""

from audio_input import LowLatencyGuitarStream
from midi_engine import RealTimeMidiBand


if __name__ == "__main__":
    band_engine = RealTimeMidiBand(port_name="ai_band Bus 1")
    guitar_stream = LowLatencyGuitarStream(strum_callback=band_engine.trigger_accompaniment)

    try:
        guitar_stream.listen()
    except KeyboardInterrupt:
        print("\n[ai_band] Real-time engine stopped.")
    finally:
        band_engine.close()
