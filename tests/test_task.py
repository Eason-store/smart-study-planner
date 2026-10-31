"""Automated tests for Task validation."""

import unittest
from datetime import date

from task import Task, normalize_priority, parse_due_date


class PriorityValidationTests(unittest.TestCase):
    def test_priority_is_normalized(self):
        self.assertEqual(normalize_priority(" high "), "High")
        self.assertEqual(normalize_priority("MEDIUM"), "Medium")
        self.assertEqual(normalize_priority("low"), "Low")

    def test_invalid_priority_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_priority("Urgent")

    def test_non_text_priority_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_priority(3)


class DueDateValidationTests(unittest.TestCase):
    def test_valid_date_is_parsed(self):
        self.assertEqual(parse_due_date("2026-11-01"), date(2026, 11, 1))

    def test_valid_leap_day_is_accepted(self):
        self.assertEqual(parse_due_date("2028-02-29"), date(2028, 2, 29))

    def test_impossible_leap_day_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_due_date("2026-02-29")

    def test_nonstandard_date_format_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_due_date("2026-1-1")

    def test_non_text_date_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_due_date(date(2026, 11, 1))


class TaskValidationTests(unittest.TestCase):
    def test_valid_task_stores_normalized_values(self):
        task = Task(
            1,
            "  Finish COMP9001 Project  ",
            "  COMP9001 ",
            "2026-11-01",
            "high",
        )

        self.assertEqual(task.task_id, 1)
        self.assertEqual(task.name, "Finish COMP9001 Project")
        self.assertEqual(task.course, "COMP9001")
        self.assertEqual(task.due_date, date(2026, 11, 1))
        self.assertEqual(task.priority, "High")
        self.assertFalse(task.completed)

    def test_past_due_date_is_allowed(self):
        task = Task(1, "Overdue task", "COMP9001", "2026-10-20", "Medium")
        self.assertEqual(task.due_date, date(2026, 10, 20))

    def test_invalid_task_ids_are_rejected(self):
        invalid_ids = (0, -1, True, "1")

        for invalid_id in invalid_ids:
            with self.subTest(task_id=invalid_id):
                with self.assertRaises(ValueError):
                    Task(
                        invalid_id,
                        "Task",
                        "COMP9001",
                        "2026-11-01",
                        "High",
                    )

    def test_empty_name_is_rejected(self):
        with self.assertRaises(ValueError):
            Task(1, "   ", "COMP9001", "2026-11-01", "High")

    def test_empty_course_is_rejected(self):
        with self.assertRaises(ValueError):
            Task(1, "Task", "", "2026-11-01", "High")

    def test_nonboolean_completed_value_is_rejected(self):
        with self.assertRaises(ValueError):
            Task(
                1,
                "Task",
                "COMP9001",
                "2026-11-01",
                "High",
                completed="yes",
            )

    def test_task_summary(self):
        task = Task(1, "Task", "COMP9001", "2026-11-01", "High")

        self.assertEqual(
            str(task),
            "[1] Task | COMP9001 | 2026-11-01 | High | Incomplete",
        )


if __name__ == "__main__":
    unittest.main()
