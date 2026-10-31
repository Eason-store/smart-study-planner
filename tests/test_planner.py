"""Automated tests for filtering, sorting, statistics, and daily plans."""

import unittest
from datetime import date

from planner import (
    filter_tasks,
    generate_daily_plan,
    get_task_statistics,
    sort_tasks,
)
from task import Task


class PlannerTestCase(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 11, 1)
        self.tasks = [
            Task(1, "Overdue project", "COMP9001", "2026-10-31", "High"),
            Task(2, "Quiz review", "INFO5990", "2026-11-01", "Medium"),
            Task(3, "Reading notes", "COMP9001", "2026-11-03", "Low"),
            Task(
                4,
                "Finished essay",
                "ENGL1000",
                "2026-11-05",
                "High",
                completed=True,
            ),
        ]


class FilterTests(PlannerTestCase):
    def test_text_status_and_priority_filters_combine(self):
        matches = filter_tasks(
            self.tasks,
            search_text="comp",
            status="Incomplete",
            priority="High",
        )

        self.assertEqual([task.task_id for task in matches], [1])

    def test_empty_filters_return_all_tasks(self):
        matches = filter_tasks(self.tasks)

        self.assertEqual(len(matches), 4)

    def test_filter_is_case_insensitive(self):
        matches = filter_tasks(self.tasks, search_text="INFO")

        self.assertEqual([task.task_id for task in matches], [2])


class SortTests(PlannerTestCase):
    def test_sort_by_id(self):
        ordered = sort_tasks(list(reversed(self.tasks)), "ID")

        self.assertEqual(
            [task.task_id for task in ordered],
            [1, 2, 3, 4],
        )

    def test_sort_by_due_date(self):
        ordered = sort_tasks(self.tasks, "Due date")

        self.assertEqual(
            [task.task_id for task in ordered],
            [1, 2, 3, 4],
        )

    def test_sort_by_priority(self):
        ordered = sort_tasks(self.tasks, "Priority")

        self.assertEqual(
            [task.task_id for task in ordered],
            [1, 4, 2, 3],
        )

    def test_urgency_sort_keeps_completed_tasks_last(self):
        ordered = sort_tasks(self.tasks, "Urgency", self.today)

        self.assertEqual(
            [task.task_id for task in ordered],
            [1, 2, 3, 4],
        )


class StatisticsTests(PlannerTestCase):
    def test_additional_statistics(self):
        statistics = get_task_statistics(self.tasks, self.today)

        self.assertEqual(statistics["total"], 4)
        self.assertEqual(statistics["completed"], 1)
        self.assertEqual(statistics["remaining"], 3)
        self.assertEqual(statistics["completion_percentage"], 25.0)
        self.assertEqual(statistics["overdue"], 1)
        self.assertEqual(statistics["due_today"], 1)
        self.assertEqual(statistics["due_soon"], 1)
        self.assertEqual(statistics["high_remaining"], 1)
        self.assertEqual(statistics["medium_remaining"], 1)
        self.assertEqual(statistics["low_remaining"], 1)

    def test_empty_statistics_handle_zero_total(self):
        statistics = get_task_statistics([], self.today)

        self.assertEqual(statistics["total"], 0)
        self.assertEqual(statistics["completion_percentage"], 0.0)


class DailyPlanTests(PlannerTestCase):
    def test_plan_uses_urgency_order_and_respects_budget(self):
        plan_data = generate_daily_plan(self.tasks, 75, self.today)
        plan = plan_data["plan"]

        self.assertEqual(
            [item["task"].task_id for item in plan],
            [1, 2],
        )
        self.assertEqual(
            [item["minutes"] for item in plan],
            [38, 37],
        )
        self.assertEqual(plan_data["unallocated_minutes"], 0)

    def test_completed_tasks_are_not_included(self):
        plan_data = generate_daily_plan(self.tasks, 200, self.today)
        planned_ids = [item["task"].task_id for item in plan_data["plan"]]

        self.assertNotIn(4, planned_ids)
        self.assertEqual(
            sum(item["minutes"] for item in plan_data["plan"]),
            200,
        )
        self.assertEqual(plan_data["unallocated_minutes"], 0)

    def test_sixty_minutes_gives_two_tasks_thirty_minutes_each(self):
        plan_data = generate_daily_plan(self.tasks, 60, self.today)
        plan = plan_data["plan"]

        self.assertEqual(
            [item["task"].task_id for item in plan],
            [1, 2],
        )
        self.assertEqual(
            [item["minutes"] for item in plan],
            [30, 30],
        )

    def test_one_task_receives_the_full_time_budget(self):
        tasks = [
            Task(1, "Only task", "COMP9001", "2026-11-03", "High"),
        ]

        plan_data = generate_daily_plan(tasks, 95, self.today)

        self.assertEqual(plan_data["plan"][0]["minutes"], 95)
        self.assertEqual(plan_data["unallocated_minutes"], 0)

    def test_invalid_time_budget_is_rejected(self):
        invalid_values = (0, 30, 59, -10, True, "60")

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    generate_daily_plan(self.tasks, value, self.today)


if __name__ == "__main__":
    unittest.main()
