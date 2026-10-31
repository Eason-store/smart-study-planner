"""
Smart Study Planner
Task filtering, sorting, statistics, and daily-plan logic.
"""

from datetime import date

from advisor import (
    PRIORITY_POINTS,
    calculate_urgency,
    get_sort_key,
    rank_tasks,
)


def filter_tasks(tasks, search_text="", status="All", priority="All"):
    """Return tasks matching the search, completion status, and priority."""
    cleaned_search = search_text.strip().lower()
    matching_tasks = []

    for task in tasks:
        text_matches = (
            not cleaned_search
            or cleaned_search in task.name.lower()
            or cleaned_search in task.course.lower()
        )
        status_matches = (
            status == "All"
            or (status == "Incomplete" and not task.completed)
            or (status == "Completed" and task.completed)
        )
        priority_matches = priority == "All" or task.priority == priority

        if text_matches and status_matches and priority_matches:
            matching_tasks.append(task)

    return matching_tasks


def sort_tasks(tasks, order="ID", today=None):
    """Return a sorted copy of the task list."""
    if today is None:
        today = date.today()

    if order == "Due date":
        return sorted(tasks, key=lambda task: (task.due_date, task.task_id))

    if order == "Priority":
        return sorted(
            tasks,
            key=lambda task: (
                -PRIORITY_POINTS[task.priority],
                task.due_date,
                task.task_id,
            ),
        )

    if order == "Urgency":
        incomplete_tasks = sorted(
            [task for task in tasks if not task.completed],
            key=lambda task: get_sort_key(task, today),
        )
        completed_tasks = sorted(
            [task for task in tasks if task.completed],
            key=lambda task: (task.due_date, task.task_id),
        )
        return incomplete_tasks + completed_tasks

    return sorted(tasks, key=lambda task: task.task_id)


def get_task_statistics(tasks, today=None):
    """Return progress and additional task statistics."""
    if today is None:
        today = date.today()

    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.completed)
    remaining_tasks = total_tasks - completed_tasks
    overdue_tasks = 0
    due_today = 0
    due_soon = 0
    priority_totals = {"High": 0, "Medium": 0, "Low": 0}

    for task in tasks:
        if task.completed:
            continue

        priority_totals[task.priority] += 1
        days_left = (task.due_date - today).days

        if days_left < 0:
            overdue_tasks += 1
        elif days_left == 0:
            due_today += 1
        elif days_left <= 3:
            due_soon += 1

    if total_tasks == 0:
        completion_percentage = 0.0
    else:
        completion_percentage = (completed_tasks / total_tasks) * 100

    return {
        "total": total_tasks,
        "completed": completed_tasks,
        "remaining": remaining_tasks,
        "completion_percentage": completion_percentage,
        "overdue": overdue_tasks,
        "due_today": due_today,
        "due_soon": due_soon,
        "high_remaining": priority_totals["High"],
        "medium_remaining": priority_totals["Medium"],
        "low_remaining": priority_totals["Low"],
    }


def generate_daily_plan(tasks, available_minutes, today=None):
    """Allocate all minutes with at least 30 minutes per scheduled task."""
    if (
        not isinstance(available_minutes, int)
        or isinstance(available_minutes, bool)
        or available_minutes < 60
    ):
        raise ValueError(
            "Available study time must be at least 60 minutes."
        )

    if today is None:
        today = date.today()

    ranked_tasks = rank_tasks(tasks, today)
    if not ranked_tasks:
        return {
            "plan": [],
            "unallocated_minutes": available_minutes,
        }

    maximum_tasks = available_minutes // 30
    scheduled_tasks = ranked_tasks[:maximum_tasks]
    urgency_scores = [
        calculate_urgency(task, today)["score"]
        for task in scheduled_tasks
    ]
    total_urgency = sum(urgency_scores)
    allocations = [30 for task in scheduled_tasks]
    extra_minutes = available_minutes - (30 * len(scheduled_tasks))
    remainders = []

    for index, (task, score) in enumerate(
        zip(scheduled_tasks, urgency_scores)
    ):
        weighted_minutes = extra_minutes * score
        allocations[index] += weighted_minutes // total_urgency
        remainders.append(weighted_minutes % total_urgency)

    remaining_minutes = available_minutes - sum(allocations)
    remainder_order = sorted(
        range(len(scheduled_tasks)),
        key=lambda index: (-remainders[index], index),
    )

    for index in remainder_order[:remaining_minutes]:
        allocations[index] += 1

    plan = []
    for task, score, minutes in zip(
        scheduled_tasks,
        urgency_scores,
        allocations,
    ):
        plan.append(
            {
                "task": task,
                "minutes": minutes,
                "urgency_score": score,
            }
        )

    return {
        "plan": plan,
        "unallocated_minutes": 0,
    }
