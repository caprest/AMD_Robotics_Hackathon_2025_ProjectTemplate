import time

from .scores import (
    NOTE_TO_NUMBER,
    JingleBells,
)
import numpy as np


def count_total_duration_in_eigth_notes(score: list[tuple[str, int]]) -> int:
    _sum = 0
    for _, duration in score:
        _sum += duration
    return _sum


class Sheet:
    BPM = 10
    FPS = 30

    NOTE_DURATION = 60
    REWIND = 15
    PRE_OFFSET = 10
    POST_OFFSET = 180

    def __init__(self):
        self.scores = JingleBells
        self.total_duration_in_eighth_notes = count_total_duration_in_eigth_notes(
            self.scores
        )

        seconds_per_beat = 60 / self.BPM
        seconds_per_eighth = seconds_per_beat / 2

        self.frames_per_eighth = int(seconds_per_eighth * self.FPS)
        self.total_frames_for_notes = (
            self.total_duration_in_eighth_notes * self.frames_per_eighth
        )

        self.total_array_length = (
            self.PRE_OFFSET
            + self.POST_OFFSET
            + self.REWIND
            + self.total_frames_for_notes
        )
        self.array = np.zeros(self.total_array_length)

        cur_index = self.PRE_OFFSET
        for note, duration_eighths in self.scores:
            frames_for_note = duration_eighths * self.frames_per_eighth

            if note != "z":
                number = NOTE_TO_NUMBER[note]
                self.array[cur_index : cur_index + self.NOTE_DURATION] = number

            cur_index += frames_for_note

        self.sequence_number = 0

        self.number_to_note_map = {v: k for k, v in NOTE_TO_NUMBER.items()}

    def _elapsed_time(self):
        return time.time() - self.start_time

    def number_to_note(self, number: int) -> str:
        return self.number_to_note_map[number]

    def start(self):
        print("🎼 Starting sheet...")
        self.start_time = time.time()

    def get_note(self) -> int | None:
        elapsed = self._elapsed_time()
        frame = int(elapsed * self.FPS) % self.total_array_length + self.REWIND

        if frame >= self.total_array_length:
            return None

        return int(self.array[frame])


if __name__ == "__main__":
    sheet = Sheet()
    sheet.start()
    while True:
        note = sheet.get_note()
        print(note)
        time.sleep(1.0 / sheet.FPS)
