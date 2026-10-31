"""Automated tests for responsive terminal UI helpers."""

import os
import unittest
from unittest.mock import patch

from ui import (
    get_inner_width,
    get_left_margin,
    make_progress_bar,
    split_box_text,
)


class ResponsiveLayoutTests(unittest.TestCase):
    def test_wide_box_uses_default_left_alignment(self):
        terminal_size = os.terminal_size((120, 30))

        with patch("ui.shutil.get_terminal_size", return_value=terminal_size):
            self.assertEqual(get_inner_width(), 96)
            self.assertEqual(get_left_margin(), 0)

    def test_narrow_box_fits_terminal(self):
        terminal_size = os.terminal_size((40, 20))

        with patch("ui.shutil.get_terminal_size", return_value=terminal_size):
            inner_width = get_inner_width()
            left_margin = get_left_margin()

            self.assertLessEqual(inner_width + 4 + left_margin, 40)

    def test_long_text_is_split_into_fitting_lines(self):
        text = "A very long task name that must wrap inside the terminal panel"
        lines = split_box_text(text, 24)

        self.assertGreater(len(lines), 1)
        for line in lines:
            self.assertLessEqual(len(line), 24)


class ProgressBarTests(unittest.TestCase):
    def test_progress_bar_boundaries(self):
        self.assertEqual(make_progress_bar(0, 10), "[----------]")
        self.assertEqual(make_progress_bar(50, 10), "[#####-----]")
        self.assertEqual(make_progress_bar(100, 10), "[##########]")

    def test_progress_percentage_is_clamped(self):
        self.assertEqual(make_progress_bar(-10, 10), "[----------]")
        self.assertEqual(make_progress_bar(150, 10), "[##########]")


if __name__ == "__main__":
    unittest.main()
