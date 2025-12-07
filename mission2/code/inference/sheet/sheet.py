from __future__ import annotations

import time
from collections.abc import Sequence

import numpy as np

from .scores import NOTE_TO_NUMBER


Score = Sequence[tuple[str, int]]


def count_total_duration_in_eigth_notes(score: Score) -> int:
    """Return total duration measured in eighth notes."""
    return sum(duration for _, duration in score)


class Sheet:
    # Timing configuration
    BPM = 10
    FPS = 30

    # Frame-based layout
    NOTE_DURATION = 210
    PRE_OFFSET = BPM * 1
    POST_OFFSET = BPM * 6

    def __init__(self, score: Score) -> None:
        # Use provided score or default to JingleBells
        self.scores: Score = score

        # Timing state
        self._start_time: float | None = None

        # --- duration / timing ---
        self.total_duration_in_eighth_notes: int = count_total_duration_in_eigth_notes(
            self.scores
        )

        self._init_timing()

        # --- array construction ---
        self.array: np.ndarray = self._build_array()

        # --- misc state ---
        self.number_to_note_map: dict[int, str] = {
            v: k for k, v in NOTE_TO_NUMBER.items()
        }

        self.sequence_number: int = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _init_timing(self) -> None:
        """Pre-compute timing and frame counts."""
        seconds_per_beat = 60.0 / self.BPM
        seconds_per_eighth = seconds_per_beat / 2.0

        # How many frames each eighth note occupies
        self.frames_per_eighth: int = int(seconds_per_eighth * self.FPS)

        # Frames occupied by all notes (without pre/post offsets)
        self.total_frames_for_notes: int = (
            self.total_duration_in_eighth_notes * self.frames_per_eighth
        )

        # Total length of the sheet array
        self.total_array_length: int = (
            self.PRE_OFFSET + self.POST_OFFSET + self.total_frames_for_notes
        )

    def _build_array(self) -> np.ndarray:
        """Create the full time→note-number array."""
        arr = np.zeros(self.total_array_length, dtype=int)

        cur_index = self.PRE_OFFSET
        for note, duration_eighths in self.scores:
            frames_for_note = duration_eighths * self.frames_per_eighth

            if note != "z":
                number = NOTE_TO_NUMBER.get(note, -1)
                end_index = min(cur_index + self.NOTE_DURATION, self.total_array_length)
                arr[cur_index:end_index] = number

            cur_index += frames_for_note

        return arr

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def number_to_note(self, number: int) -> str:
        """Map a numeric note representation back to its symbol."""
        return self.number_to_note_map[number]

    def start(self) -> None:
        """Begin playback timing."""
        print("🎼 Starting sheet...")
        self._start_time = time.time()
        self.sequence_number = 0

    def _elapsed_time(self) -> float:
        """Return elapsed time since start() was called, or 0 if not started."""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    def tick_note(self) -> int | None:
        """
        Get the current note as an integer (NOTE_TO_NUMBER value).

        Returns:
            int | None: note number at the current frame, or None when
            `frame >= total_array_length`. The frame is computed from
            elapsed time since start() was called.
        """
        elapsed = self._elapsed_time()
        frame = int(elapsed * self.FPS)

        if frame >= self.total_array_length:
            return None

        return int(self.array[frame])


if __name__ == "__main__":
    sheet = Sheet()
    sheet.start()
    while True:
        note = sheet.tick_note()
        print(note)
        time.sleep(1.0 / sheet.FPS)
