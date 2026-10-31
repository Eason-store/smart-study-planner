"""
Smart Study Planner
Smart Study Advisor scoring and recommendation logic.
"""

from datetime import date


PRIORITY_POINTS = {
    "High": 3,
    "Medium": 2,
    "Low": 1,
}


def get_deadline_points(days_left):
    """Return deadline points based on the number of days left."""
    if days_left < 0:
        return 6
    if days_left <= 1:
        return 5
    if days_left <= 3:
        return 4
    if days_left <= 7:
        return 3
    if days_left <= 14:
        return 2

    return 1


def calculate_urgency(task, today=None):
    """Calculate the urgency score and show how it was produced."""
    if today is None:
        today = date.today()

    days_left = (task.due_date - today).days
    priority_points = PRIORITY_POINTS[task.priority]
    deadline_points = get_deadline_points(days_left)

    return {
        "days_left": days_left,
        "priority_points": priority_points,
        "deadline_points": deadline_points,
        "score": priority_points + deadline_points,
    }


def get_sort_key(task, today):
    """
    Rank by urgency, then due date, priority, and a stable task ID.

    Negative values are used because Python sorts from smallest to largest,
    while a larger urgency score should be ranked first.
    """
    urgency = calculate_urgency(task, today)

    return (
        -urgency["score"],
        task.due_date,
        -urgency["priority_points"],
        task.task_id,
    )


def rank_tasks(tasks, today=None):
    """Return incomplete tasks in urgency order."""
    if today is None:
        today = date.today()

    incomplete_tasks = []

    for task in tasks:
        if not task.completed:
            incomplete_tasks.append(task)

    incomplete_tasks.sort(key=lambda task: get_sort_key(task, today))
    return incomplete_tasks


def recommend_next_task(tasks, today=None):
    """Return the highest-ranked incomplete task, or None."""
    ranked_tasks = rank_tasks(tasks, today)

    if not ranked_tasks:
        return None

    return ranked_tasks[0]


def explain_recommendation(task, today=None):
    """Create a plain-English explanation for the recommended task."""
    urgency = calculate_urgency(task, today)
    days_left = urgency["days_left"]

    if days_left < 0:
        timing_reason = f"its deadline passed {-days_left} day(s) ago"
    elif days_left == 0:
        timing_reason = "it is due today"
    elif days_left == 1:
        timing_reason = "it is due tomorrow"
    else:
        timing_reason = f"it is due in {days_left} days"

    return (
        f"{task.name} is recommended because {timing_reason} and it has "
        f"{task.priority.lower()} importance. The total urgency score is "
        f"{urgency['score']} ({urgency['priority_points']} priority points + "
        f"{urgency['deadline_points']} deadline points)."
    )


if __name__ == "__main__":
    from task import Task

    test_tasks = [
        Task(1, "High-priority project", "COMP9001", "2026-11-10", "High"),
        Task(2, "Review quiz", "INFO5990", "2026-11-03", "Medium"),
        Task(3, "Completed overdue task", "COMP9001", "2026-10-20", "High", True),
    ]

    recommendation = recommend_next_task(test_tasks, date(2026, 11, 1))

    print("Recommended task:")
    print(recommendation)
    print("\nExplanation:")
    print(explain_recommendation(recommendation, date(2026, 11, 1)))
