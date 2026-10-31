"""Automated tests for the Smart Study Advisor."""

import unittest
from datetime import date

from advisor import (
    calculate_urgency,
    get_deadline_points,
    recommend_next_task,
)
from task import Task


class DeadlinePointTests(unittest.TestCase):
    def test_all_deadline_boundaries(self):
        expected_points = {
            -1: 6,
            0: 5,
            1: 5,
            2: 4,
            3: 4,
            4: 3,
            7: 3,
            8: 2,
            14: 2,
            15: 1,
        }

        for days_left, expected in expected_points.items():
            with self.subTest(days_left=days_left):
                self.assertEqual(
                    get_deadline_points(days_left),
                    expected,
                )


class UrgencyCalculationTests(unittest.TestCase):
    def test_priority_and_deadline_points_are_combined(self):
        today = date(2026, 11, 1)
        task = Task(
            task_id=1,
            name="Finish project",
            course="COMP9001",
            due_date="2026-11-01",
            priority="High",
        )

        urgency = calculate_urgency(task, today)

        self.assertEqual(urgency["days_left"], 0)
        self.assertEqual(urgency["priority_points"], 3)
        self.assertEqual(urgency["deadline_points"], 5)
        self.assertEqual(urgency["score"], 8)

    def test_date_difference_works_across_new_year(self):
        today = date(2026, 12, 31)
        task = Task(
            task_id=1,
            name="New year task",
            course="COMP9001",
            due_date="2027-01-01",
            priority="Low",
        )

        urgency = calculate_urgency(task, today)

        self.assertEqual(urgency["days_left"], 1)
        self.assertEqual(urgency["deadline_points"], 5)


class RecommendationTests(unittest.TestCase):
    def test_completed_tasks_are_ignored(self):
        today = date(2026, 11, 1)
        tasks = [
            Task(
                task_id=1,
                name="Completed overdue task",
                course="COMP9001",
                due_date="2026-10-20",
                priority="High",
                completed=True,
            ),
            Task(
                task_id=2,
                name="Future incomplete task",
                course="INFO5990",
                due_date="2026-11-20",
                priority="Low",
            ),
        ]

        recommendation = recommend_next_task(tasks, today)

        self.assertEqual(recommendation.task_id, 2)

    def test_same_score_uses_earlier_due_date(self):
        today = date(2026, 11, 1)
        tasks = [
            Task(2, "Later task", "COMP9001", "2026-11-04", "High"),
            Task(1, "Earlier task", "COMP9001", "2026-11-03", "High"),
        ]

        recommendation = recommend_next_task(tasks, today)

        self.assertEqual(recommendation.name, "Earlier task")

    def test_identical_score_and_date_use_lower_id(self):
        today = date(2026, 11, 1)
        tasks = [
            Task(2, "Second task", "COMP9001", "2026-11-03", "High"),
            Task(1, "First task", "COMP9001", "2026-11-03", "High"),
        ]

        recommendation = recommend_next_task(tasks, today)

        self.assertEqual(recommendation.task_id, 1)

    def test_no_recommendation_when_all_tasks_are_completed(self):
        today = date(2026, 11, 1)
        tasks = [
            Task(
                1,
                "Finished task",
                "COMP9001",
                "2026-11-01",
                "High",
                completed=True,
            )
        ]

        recommendation = recommend_next_task(tasks, today)

        self.assertIsNone(recommendation)


if __name__ == "__main__":
    unittest.main()
