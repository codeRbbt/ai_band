import unittest
import tempfile
import wave

import numpy as np

from ghostician.arranger import arrange
from ghostician.features import AudioFeatures, analyze_frame
from ghostician.tension import tension_score
from ghostician.render import render_background_band
from ghostician.mixer import StemMixer
from ghostician.conductor import parse_band_request, progression_notes


class GhosticianTests(unittest.TestCase):
    def test_pitch_and_rms_are_detected(self):
        rate = 44100
        samples = 0.2 * np.sin(2 * np.pi * 110 * np.arange(4096) / rate)
        features = analyze_frame(samples, rate)
        self.assertAlmostEqual(features.rms, 0.2 / np.sqrt(2), places=2)
        self.assertAlmostEqual(features.pitch_hz, 110, delta=4)

    def test_tension_is_bounded_and_high_state_adds_fill(self):
        quiet = AudioFeatures(0.05, 110, 0.1, 0.1, 0.0)
        loud = AudioFeatures(0.35, 440, 1.0, 0.8, 1.0)
        self.assertLess(tension_score(quiet), tension_score(loud))
        events = arrange(loud, tension_score(loud), beat=3)
        self.assertGreaterEqual(sum(event.note in (38, 40) for event in events), 2)

    def test_silence_does_not_generate_midi(self):
        silent = AudioFeatures(0.0, None, 0.0, 0.0, 0.0)
        self.assertEqual(arrange(silent, 0), [])

    def test_background_renderer_writes_stereo_wav(self):
        with tempfile.TemporaryDirectory() as directory:
            path = render_background_band(f"{directory}/band.wav", seconds=1)
            with wave.open(str(path), "rb") as audio:
                self.assertEqual(audio.getnchannels(), 2)
                self.assertEqual(audio.getframerate(), 44100)
                self.assertGreater(audio.getnframes(), 0)

    def test_mixer_mute_and_solo_controls(self):
        mixer = StemMixer(sample_rate=100)
        stems = {"keys": np.ones(100, dtype=np.float32), "bass": np.ones(100, dtype=np.float32)}
        full = mixer.mix(stems)
        mixer.set_mute("keys")
        muted = mixer.mix(stems)
        self.assertGreater(float(np.max(np.abs(full))), float(np.max(np.abs(muted))))
        mixer.set_mute("keys", False)
        mixer.set_solo("bass")
        solo = mixer.mix(stems)
        self.assertTrue(np.allclose(solo, mixer.mix({"bass": stems["bass"]})))

    def test_band_director_parses_example_request(self):
        spec = parse_band_request("3/4 jazz drums with upright bass in E minor in ii-v-i fashion 3 seconds")
        self.assertEqual((spec.beats_per_bar, spec.beat_unit), (3, 4))
        self.assertEqual(spec.drum_style, "jazz")
        self.assertEqual(spec.bass_style, "upright")
        self.assertEqual(spec.key, "E Minor")
        self.assertEqual(spec.progression, ("ii", "V", "i"))
        self.assertEqual(spec.duration, 3)
        self.assertEqual(len(progression_notes(spec, "ii")), 4)

    def test_band_director_uses_latest_duration_and_sound_variants(self):
        spec = parse_band_request("3/4 jazz drums with upright bass in E minor 3 seconds; make the song 3 minutes, brush drums, 1970s jazz bass")
        self.assertEqual(spec.duration, 180)
        self.assertEqual(spec.drum_style, "brush")
        self.assertEqual(spec.bass_style, "1970s_jazz")

    def test_brush_render_contains_kick_and_snare_energy(self):
        from ghostician.conductor import BandSpec
        from ghostician.render import SAMPLE_RATE

        spec = BandSpec(key="E minor", beats_per_bar=3, beat_unit=4, drum_style="brush", bass_style="1970s_jazz", duration=2)
        with tempfile.TemporaryDirectory() as directory:
            path = render_background_band(f"{directory}/brush.wav", seconds=2, band=spec)
            with wave.open(str(path), "rb") as audio:
                samples = np.frombuffer(audio.readframes(audio.getnframes()), dtype=np.int16).reshape(-1, 2).mean(axis=1)
            self.assertGreater(float(np.max(np.abs(samples[: int(SAMPLE_RATE * 0.3)]))), 1000)
            self.assertGreater(float(np.max(np.abs(samples[int(SAMPLE_RATE * 0.45): int(SAMPLE_RATE * 0.8)]))), 1000)

    def test_audio_input_requires_optional_dependency(self):
        from ghostician.capture import AudioInput

        try:
            with AudioInput():
                pass
        except RuntimeError as error:
            self.assertIn("optional audio dependencies", str(error))


if __name__ == "__main__":
    unittest.main()