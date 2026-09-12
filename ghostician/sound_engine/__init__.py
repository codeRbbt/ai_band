"""Native instrument voices used by the offline and live sound engines."""

from .drum_sampler import DrumSynth
from .synth_bass import BassSynth
from .synth_keys import KeysSynth

__all__ = ["BassSynth", "DrumSynth", "KeysSynth"]