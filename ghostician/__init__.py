"""Ghostician: a real-time AI accompanist for guitar."""

from .engine import Ghostician
from .features import AudioFeatures, analyze_frame

__all__ = ["AudioFeatures", "Ghostician", "analyze_frame"]