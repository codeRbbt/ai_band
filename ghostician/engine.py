"""Top-level stateful accompaniment engine."""

from dataclasses import dataclass

from .arranger import arrange
from .features import AudioFeatures
from .midi import EventOutput, MidiEvent
from .tension import tension_score


@dataclass
class Ghostician:
    """Convert analyzed guitar frames into MIDI events."""

    output: EventOutput | None = None
    beat: int = 0
    previous_rms: float = 0.0

    def process(self, features: AudioFeatures) -> tuple[float, list[MidiEvent]]:
        score = tension_score(features)
        events = arrange(features, score, self.beat)
        self.beat = (self.beat + 1) % 16
        self.previous_rms = features.rms
        if self.output:
            for event in events:
                self.output.send(event)
        return score, events