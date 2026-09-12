"""Simple jazz comp rules for triggering shell voicings and drum hits."""


class JazzCompEngine:
    @staticmethod
    def get_piano_shell(root_note):
        """Generate a classic jazz shell voicing: root, third, seventh."""
        return [root_note, root_note + 4, root_note + 10]

    @staticmethod
    def get_drum_triggers():
        """Return kick and ride triggers for a simple live drum comp."""
        return [36, 51]
