Markdown# JamZone Core Architecture & Implementation Specification

## 1. System Overview
This project is an open-source, real-time interactive virtual band and stem-mixing engine ("Custom JamZone") built in Python. The system listens to a live guitar input via a Focusrite Scarlett interface, calculates dynamic performance metrics (picking attack, pitch/register, note density), derives a real-time **Tension Index (0–100)**, and dynamically controls AI musician agents (Keys, Bass, Drums).

The audio engine synthesizes custom instrument timbres natively, applies real-time DSP effects, and routes stems through an isolated multi-track mixer with full mute, solo, volume, and panning control.

---

## 2. Hardware Setup & Signal Flow

[ 1969 Gibson SG ]│▼[ Focusrite Scarlett Input 1 ]│├── USB ──► [ PC/Mac (Python Audio Engine & AI Agents) ]│                 ││                 └── Audio Output ──► Studio Monitors / Headphones (Backing Stems)│└── Line Direct Out ──► [ Fender Twin Reverb ] (Dedicated Clean Guitar Tone)
- **Audio Interface:** Focusrite Scarlett Solo / 2i2 (Input 1 for Guitar).
- **Buffer Settings:** 64 to 128 samples at 44.1 kHz / 48 kHz for <10ms round-trip latency.
- **Monitoring Strategy:** Keep your electric guitar routed directly to your Fender Twin Reverb while routing the synthesized backing track stems to studio monitors or headphones.

---

## 3. Tech Stack (100% Open Source)

| Layer | Open-Source Library | Function |
|---|---|---|
| **Audio I/O & Streaming** | `pyaudio`, `sounddevice` | Low-latency audio buffer streaming (<10ms). |
| **Audio Analysis** | `numpy`, `scipy`, `aubio` | Real-time RMS envelope following, pick attack, note density, and pitch tracking. |
| **MIDI Management** | `mido`, `python-rtmidi` | MIDI routing and event dispatching. |
| **Real-Time DSP Effects** | `pedalboard` | Spotify's open-source C++ Python wrapper for studio FX (Reverb, Delay, Compression, EQ). |
| **Sound Synthesis** | `numpy`, `scipy`, FluidSynth | Additive/FM synthesis and SoundFont/sample triggering for custom instruments. |

---

## 4. Software Architecture Diagram

[ Focusrite Input 1 (Guitar) ]│▼┌──────────────────────────┐│  1. Guitar Analyzer      │  (RMS Volume, Pitch, Note Density)└────────────┬─────────────┘│  Tension Index (0-100)▼┌──────────────────────────┐│  2. Master Conductor     │  (Song Map, Key, Meter, Bar Clock)└────────────┬─────────────┘│  Trigger Events & Intensity Levels▼┌──────────────────────────┐│  3. Musician AI Agents   │  (Piano, Bass, Drum Player Logic)└────────────┬─────────────┘│  MIDI / Control Events▼┌──────────────────────────┐│  4. Sound Engine         │  (FM/Additive Synth Keys, Sub Bass, Sample Drums)└────────────┬─────────────┘│  Audio Stems▼┌──────────────────────────┐│  5. Multi-Track Mixer    │  (Vol, Pan, Mute, Solo, Pedalboard FX per Stem)└────────────┬─────────────┘│▼[ Stereo Output / Headphones ]
---

## 5. Directory Structure

```text
jamzone-core/
├── .github/
│   └── agents/
│       └── jamzone-builder.agent.md
├── listener/
│   ├── __init__.py
│   └── guitar_analyzer.py
├── agents/
│   ├── __init__.py
│   ├── master_conductor.py
│   ├── piano_player.py
│   ├── bass_player.py
│   └── drum_player.py
├── sound_engine/
│   ├── __init__.py
│   ├── synth_keys.py
│   ├── synth_bass.py
│   ├── drum_sampler.py
│   └── effects_chain.py
├── mixer/
│   ├── __init__.py
│   ├── stem_mixer.py
│   └── audio_bus.py
├── JAMZONE_AGENT_SPEC.md
├── requirements.txt
└── main.py
6. Project Configuration Filesrequirements.txtPlaintextpyaudio>=0.2.14
sounddevice>=0.4.6
numpy>=1.26.0
scipy>=1.11.0
mido>=1.3.0
python-rtmidi>=1.5.8
aubio>=0.4.9
pedalboard>=0.8.7
python-dotenv>=1.0.0
.github/agents/jamzone-builder.agent.mdMarkdown---
name: JamZoneArchitect
description: Specialist in real-time audio synthesis, multi-track mixing, and intelligent AI rhythm section generation in Python.
model: auto
---

# Objective
Build a modular, open-source JamZone alternative in Python. The system listens to live guitar via Focusrite Scarlett (Input 1), calculates dynamic tension metrics, generates dynamic accompaniment on Keys, Bass, and Drums, synthesizes audio natively, and routes isolated multi-track stems through a real-time software mixer.

# Core Requirements
1. **Low-Latency Audio Engine:** Use `sounddevice` / `pyaudio` with audio buffer sizes between 64 and 128 samples.
2. **Custom Sound Generation:** Synthesize custom instrument sounds using additive/FM synthesis (`scipy`, `numpy`) or sample playback.
3. **Multi-Track Mixer:** Provide dynamic volume, panning, mute, and solo controls per track stem (`keys`, `bass`, `drums`, `guitar`).
4. **Dynamic Musician Agents:**
   - **Piano Player:** Rootless voicings, altered chord extensions ($b9, \#9, b13$), rhythmic syncopation based on dynamic tension index.
   - **Bass Player:** Walking basslines, scalar approach notes, chromatic passes.
   - **Drummer:** Procedural groove patterns, automated snare/tom fills on tension spikes.
5. **DSP Effects:** Apply real-time FX using Spotify's `pedalboard` (Reverb, Delay, Compression) per stem track.

# Development Guidelines
- Build modular, cleanly documented Python 3.11+ classes.
- Ensure all real-time audio loops remain non-blocking.
7. Key Python Source Code Moduleslistener/guitar_analyzer.pyPythonimport numpy as np
import pyaudio

class GuitarAnalyzer:
    """Listens to Focusrite Scarlett Input 1 and computes continuous dynamic tension metrics."""
    def __init__(self, sample_rate=44100, chunk_size=128):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.p = pyaudio.PyAudio()
        
    def start_listening(self, input_device_index=1):
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            input_device_index=input_device_index,
            frames_per_buffer=self.chunk_size
        )

    def calculate_tension(self, pcm_data):
        audio_array = np.frombuffer(pcm_data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_array**2)) if len(audio_array) > 0 else 0
        volume_score = min(100.0, (rms / 3000.0) * 100.0)
        
        # Simple weighted tension formula (RMS / Picking Attack)
        tension_index = volume_score
        return tension_index
sound_engine/synth_keys.pyPythonimport numpy as np

class CustomRhodesSynth:
    """Custom synthesized Electric Piano sound engine using FM/Additive synthesis."""
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def note_to_freq(self, note_number):
        return 440.0 * (2.0 ** ((note_number - 69) / 12.0))

    def generate_note(self, note_number, duration=1.0, velocity=100, bell_tone=0.5):
        freq = self.note_to_freq(note_number)
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        fundamental = np.sin(2 * np.pi * freq * t)
        second_harmonic = 0.5 * np.sin(2 * np.pi * freq * 2 * t)
        
        tine_freq = freq * 3.14
        tine = bell_tone * (velocity / 127.0) * np.sin(2 * np.pi * tine_freq * t) * np.exp(-t * 15.0)
        
        decay = np.exp(-t * (3.0 / (max(1, velocity) / 64.0)))
        audio = (fundamental + second_harmonic + tine) * decay
        
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val
            
        return (audio * (velocity / 127.0) * 0.7).astype(np.float32)
mixer/stem_mixer.pyPythonimport numpy as np

class JamZoneMixer:
    """Multi-track stem mixer with volume, panning, mute, and solo controls per channel."""
    def __init__(self):
        self.tracks = {
            "keys": {"volume": 0.8, "mute": False, "solo": False, "pan": -0.2},
            "bass": {"volume": 0.9, "mute": False, "solo": False, "pan": 0.0},
            "drums": {"volume": 0.85, "mute": False, "solo": False, "pan": 0.0},
            "guitar_in": {"volume": 1.0, "mute": False, "solo": False, "pan": 0.0}
        }

    def set_track_volume(self, track_name, volume):
        if track_name in self.tracks:
            self.tracks[track_name]["volume"] = max(0.0, min(1.0, volume))

    def toggle_mute(self, track_name):
        if track_name in self.tracks:
            self.tracks[track_name]["mute"] = not self.tracks[track_name]["mute"]

    def process_mix(self, track_buffers):
        any_solo = any(t["solo"] for t in self.tracks.values())
        mix_left = None
        mix_right = None

        for track_name, buffer in track_buffers.items():
            state = self.tracks.get(track_name)
            if not state or state["mute"]:
                continue
            if any_solo and not state["solo"]:
                continue

            vol = state["volume"]
            pan = state["pan"]
            left_gain = vol * np.cos((pan + 1) * np.pi / 4)
            right_gain = vol * np.sin((pan + 1) * np.pi / 4)

            left_channel = buffer * left_gain
            right_channel = buffer * right_gain

            if mix_left is None:
                mix_left = np.zeros_like(left_channel)
                mix_right = np.zeros_like(right_channel)

            mix_left += left_channel
            mix_right += right_channel

        if mix_left is None:
            return np.zeros((128, 2), dtype=np.float32)

        return np.column_stack((mix_left, mix_right))
8. Implementation RoadmapPhase 1: Input & Metrics (listener/guitar_analyzer.py)Connect Focusrite Scarlett Input 1, verify sub-10ms buffer capture, and output real-time RMS/Tension index values.Phase 2: Sound Engine Synthesis (sound_engine/)Implement native sound synthesis classes for keys, bass, and drum sample playback.Phase 3: Musician Agents (agents/)Implement rule-based chord comping and walking bassline generators driven by chord charts ($3/4$ and $4/4$).Phase 4: Stem Mixer & Effects (mixer/)Assemble multi-track busing with volume, pan, mute, solo, and pedalboard DSP processing.Phase 5: Master Integration (main.py)Connect non-blocking event loops for live guitar play-along.