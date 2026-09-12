"""Public Band Director skill interface."""

from .conductor import BandSpec, parse_band_request, progression_notes


class BandDirector:
    """Turn a natural-language direction into a BandSpec."""

    def direct(self, request: str) -> BandSpec:
        return parse_band_request(request)


__all__ = ["BandDirector", "BandSpec", "parse_band_request", "progression_notes"]