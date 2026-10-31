"""Automated tests for saving and loading tasks."""

import unittest
from pathlib import Path

from storage import FIELD_NAMES, load_tasks, save_tasks
from task import Task


class StorageTests(unittest.TestCase):
    def setUp(self):
        tests_directory = Path(__file__).resolve().parent
        self.file_path = tests_directory / "_storage_test_tasks.txt"
        self.file_path.unlink(missing_ok=True)

    def tearDown(self):
        self.file_path.unlink(missing_ok=True)

    def write_header_and_rows(self, rows):
        header = ",".join(FIELD_NAMES)
        content = header + "\n" + rows
        self.file_path.write_text(content, encoding="utf-8")

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_tasks(self.file_path), [])

    def test_header_only_file_returns_empty_list(self):
        self.write_header_and_rows("")
        self.assertEqual(load_tasks(self.file_path), [])

    def test_save_and_load_round_trip_preserves_all_fields(self):
        tasks = [
            Task(
                1,
                "Review notes, chapter 1",
                "COMP9001",
                "2026-11-03",
                "Medium",
            ),
            Task(
                2,
                "中文任务 | test",
                "INFO5990",
                "2026-11-10",
                "High",
                completed=True,
            ),
        ]

        save_tasks(tasks, self.file_path)
        loaded_tasks = load_tasks(self.file_path)

        self.assertEqual(len(loaded_tasks), 2)
        for original, loaded in zip(tasks, loaded_tasks):
            self.assertEqual(loaded.task_id, original.task_id)
            self.assertEqual(loaded.name, original.name)
            self.assertEqual(loaded.course, original.course)
            self.assertEqual(loaded.due_date, original.due_date)
            self.assertEqual(loaded.priority, original.priority)
            self.assertEqual(loaded.completed, original.completed)

    def test_invalid_header_raises_value_error(self):
        self.file_path.write_text(
            "id,name,course,due_date,priority,completed\n",
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            load_tasks(self.file_path)

    def test_duplicate_task_id_raises_value_error(self):
        self.write_header_and_rows(
            "1,First task,COMP9001,2026-11-03,High,False\n"
            "1,Second task,INFO5990,2026-11-04,Low,True\n"
        )

        with self.assertRaisesRegex(ValueError, "Duplicate task ID 1"):
            load_tasks(self.file_path)

    def test_missing_completed_value_does_not_overwrite_file(self):
        original_content = (
            "task_id,name,course,due_date,priority,completed\n"
            "1,Missing status,COMP9001,2026-11-03,High,\n"
        )
        self.file_path.write_text(original_content, encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "line 2"):
            load_tasks(self.file_path)

        self.assertEqual(
            self.file_path.read_text(encoding="utf-8"),
            original_content,
        )

    def test_extra_value_raises_value_error(self):
        self.write_header_and_rows(
            "1,Extra value,COMP9001,2026-11-03,High,False,unexpected\n"
        )

        with self.assertRaisesRegex(ValueError, "Too many values"):
            load_tasks(self.file_path)


if __name__ == "__main__":
    unittest.main()
