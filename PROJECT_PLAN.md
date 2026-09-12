# Real-Time Python Accompanist System

## System Objective
Build an open-source, real-time interactive band agent in Python that listens to a guitar signal (Focusrite Scarlett Input 1) and dynamically comps on Piano, Upright Bass, and Drums.

## Key Requirements
- **Audio Routing:** Focusrite Scarlett Solo/2i2 (Channel 1, 64–128 sample buffer).
- **Pitch & Feature Tracking:** Measure RMS volume, pitch, and note density in real-time.
- **Tension Index:** Calculate a continuous score (0–100) based on picking attack, density, and register.
- **Instrument Logic:**
  - Piano: Shell voicings (low tension) -> altered extensions & block syncopation (high tension).
  - Bass: Root notes/space -> walking quarter-note lines with chromatic approach notes.
  - Drums: Brushes/hi-hat -> ride bell, open hi-hats, and automated snare fills on climax.
- **Output:** Route MIDI directly into FluidSynth using a free SoundFont (e.g., GeneralUser GS).
- **Tech Stack:** Open-source Python (`pyaudio`, `numpy`, `mido`, `python-rtmidi`, `aubio`, `fluidsynth`).