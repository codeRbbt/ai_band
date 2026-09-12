"""Natural-language band direction and harmonic planning."""

from dataclasses import dataclass, field
import re


NOTE_NAMES = {"C": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3, "E": 4, "F": 5, "F#": 6, "GB": 6, "G": 7, "G#": 8, "AB": 8, "A": 9, "A#": 10, "BB": 10, "B": 11}


@dataclass(frozen=True)
class BandSpec:
    """A complete, renderable instruction for a backing band."""

    key: str = "C major"
    tempo: int = 92
    beats_per_bar: int = 4
    beat_unit: int = 4
    drum_style: str = "jazz"
    bass_style: str = "upright"
    instruments: tuple[str, ...] = ("keys", "bass", "drums")
    progression: tuple[str, ...] = ("I", "VI", "IV", "V")
    duration: float = 24.0
    options: dict[str, str] = field(default_factory=dict)

    @property
    def root_midi(self) -> int:
        match = re.match(r"([A-Ga-g][#b]?)", self.key)
        if not match:
            raise ValueError(f"unsupported key: {self.key}")
        return 48 + NOTE_NAMES[match.group(1).upper()]

    @property
    def is_minor(self) -> bool:
        return "minor" in self.key.lower() or self.key.lower().endswith("m")


def _progression_for(spec: BandSpec, roman: str) -> tuple[int, ...]:
    scale = (0, 2, 3, 5, 7, 8, 10) if spec.is_minor else (0, 2, 4, 5, 7, 9, 11)
    degrees = {"I": 0, "II": 1, "III": 2, "IV": 3, "V": 4, "VI": 5, "VII": 6}
    degree = roman.upper().replace("O", "").replace("ø", "")
    interval = scale[degrees.get(degree, 0)]
    third = 3 if "ii" in roman.lower() or "iii" in roman.lower() or "vi" in roman.lower() else 4
    return (spec.root_midi + interval, spec.root_midi + interval + third, spec.root_midi + interval + 7, spec.root_midi + interval + 10)


def progression_notes(spec: BandSpec, symbol: str) -> tuple[int, ...]:
    """Convert a Roman numeral into a compact triad for the synth engine."""
    return _progression_for(spec, symbol)


def parse_band_request(request: str) -> BandSpec:
    """Parse a practical subset of natural-language band directions."""
    text = request.strip()
    lowered = text.lower()
    meter = re.search(r"(\d+)\s*/\s*(\d+)", lowered)
    key = re.search(r"\b([a-g](?:#|b)?\s*(?:major|minor|m))\b", lowered)
    tempo = re.search(r"(?:at|tempo)\s*(\d+)\s*bpm", lowered)
    duration_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(second|seconds|sec|secs|minute|minutes|min|mins)\b", lowered)
    progression = ("ii", "V", "i") if re.search(r"ii\s*-\s*v\s*-\s*i", lowered) else ("I", "VI", "IV", "V")
    drum_style = "brush" if "brush" in lowered else next((style for style in ("jazz", "rock", "blues") if style in lowered), "jazz")
    if "1970s" in lowered or "70s" in lowered:
        bass_style = "1970s_jazz"
    elif "upright" in lowered:
        bass_style = "upright"
    elif "electric bass" in lowered:
        bass_style = "electric"
    else:
        bass_style = "upright"
    instruments = tuple(name for name, terms in (("keys", ("piano", "keys", "rhodes", "organ")), ("bass", ("bass",)), ("drums", ("drum", "drums"))) if any(term in lowered for term in terms))
    if not instruments:
        instruments = ("keys", "bass", "drums")
    return BandSpec(
        key=key.group(1).title() if key else "C major",
        tempo=int(tempo.group(1)) if tempo else 92,
        beats_per_bar=int(meter.group(1)) if meter else 4,
        beat_unit=int(meter.group(2)) if meter else 4,
        drum_style=drum_style,
        bass_style=bass_style,
        instruments=instruments,
        progression=progression,
        duration=(float(duration_matches[-1][0]) * (60 if duration_matches[-1][1].startswith("min") else 1)) if duration_matches else 24.0,
        options={"request": text},
    )