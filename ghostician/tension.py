"""Tension mapping for the accompanist."""

from .features import AudioFeatures


def tension_score(features: AudioFeatures) -> float:
    """Return a stable 0-100 tension score from frame features."""
    energy = min(1.0, features.rms / 0.35)
    score = (energy * 0.30 + features.note_density * 0.30 + features.register * 0.20 + features.attack * 0.20) * 100
    return round(max(0.0, min(100.0, score)), 2)