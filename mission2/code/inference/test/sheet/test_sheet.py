import unittest
from unittest.mock import patch

from inference.sheet.sheet import Sheet, count_total_duration_in_eigth_notes
from inference.sheet.scores import NOTE_TO_NUMBER, JingleBells


class TestCountTotalDuration(unittest.TestCase):
    def test_empty_score(self):
        result = count_total_duration_in_eigth_notes([])
        self.assertEqual(result, 0)

    def test_single_note(self):
        score = [("C4", 4)]
        result = count_total_duration_in_eigth_notes(score)
        self.assertEqual(result, 4)

    def test_multiple_notes(self):
        score = [("C4", 2), ("D4", 3), ("E4", 1)]
        result = count_total_duration_in_eigth_notes(score)
        self.assertEqual(result, 6)

    def test_jingle_bells(self):
        result = count_total_duration_in_eigth_notes(JingleBells)
        expected = sum(duration for _, duration in JingleBells)
        self.assertEqual(result, expected)


class TestSheet(unittest.TestCase):
    def setUp(self):
        self.sheet = Sheet()

    def test_initialization(self):
        self.assertEqual(self.sheet.BPM, 10)
        self.assertEqual(self.sheet.FPS, 30)
        self.assertEqual(self.sheet.NOTE_DURATION, 60)
        self.assertEqual(self.sheet.scores, JingleBells)

    def test_initialization_with_custom_scores(self):
        custom_score = [("C4", 2), ("D4", 2)]
        sheet = Sheet(scores=custom_score)
        self.assertEqual(sheet.scores, custom_score)
        self.assertEqual(sheet.total_duration_in_eighth_notes, 4)

    def test_start_time_initially_none(self):
        self.assertIsNone(self.sheet._start_time)

    def test_total_duration_calculation(self):
        expected = count_total_duration_in_eigth_notes(JingleBells)
        self.assertEqual(self.sheet.total_duration_in_eighth_notes, expected)

    def test_frames_per_eighth_calculation(self):
        seconds_per_beat = 60 / self.sheet.BPM
        seconds_per_eighth = seconds_per_beat / 2
        expected_frames = int(seconds_per_eighth * self.sheet.FPS)
        self.assertEqual(self.sheet.frames_per_eighth, expected_frames)

    def test_array_length(self):
        expected = (
            self.sheet.PRE_OFFSET
            + self.sheet.POST_OFFSET
            + self.sheet.REWIND
            + self.sheet.total_frames_for_notes
        )
        self.assertEqual(len(self.sheet.array), expected)

    def test_array_dtype_is_int(self):
        self.assertTrue(self.sheet.array.dtype == int)

    def test_number_to_note(self):
        for note, number in NOTE_TO_NUMBER.items():
            self.assertEqual(self.sheet.number_to_note(number), note)

    def test_number_to_note_map_is_inverse(self):
        for note, number in NOTE_TO_NUMBER.items():
            self.assertEqual(self.sheet.number_to_note_map[number], note)

    @patch("inference.sheet.sheet.time.time")
    def test_start_sets_start_time(self, mock_time):
        mock_time.return_value = 1000.0
        self.sheet.start()
        self.assertEqual(self.sheet._start_time, 1000.0)

    def test_elapsed_time_before_start(self):
        elapsed = self.sheet._elapsed_time()
        self.assertEqual(elapsed, 0.0)

    @patch("inference.sheet.sheet.time.time")
    def test_elapsed_time_after_start(self, mock_time):
        mock_time.return_value = 1000.0
        self.sheet.start()
        mock_time.return_value = 1005.0
        elapsed = self.sheet._elapsed_time()
        self.assertEqual(elapsed, 5.0)

    @patch("inference.sheet.sheet.time.time")
    def test_get_note_returns_int(self, mock_time):
        mock_time.return_value = 0.0
        self.sheet.start()
        mock_time.return_value = 0.5
        note = self.sheet.tick_note()
        self.assertIsInstance(note, int)

    @patch("inference.sheet.sheet.time.time")
    def test_get_note_at_start(self, mock_time):
        mock_time.return_value = 0.0
        self.sheet.start()
        note = self.sheet.tick_note()
        self.assertIsNotNone(note)
        self.assertGreaterEqual(note, 0)


if __name__ == "__main__":
    unittest.main()
