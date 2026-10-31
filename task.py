"""
Smart Study Planner
Task model and validation.
"""

from datetime import datetime


VALID_PRIORITIES = ("High", "Medium", "Low")


def normalize_priority(priority):
    """Return High, Medium, or Low in a consistent format."""
    if not isinstance(priority, str):
        raise ValueError("Priority must be High, Medium, or Low.")

    cleaned_priority = priority.strip().lower()

    for valid_priority in VALID_PRIORITIES:
        if cleaned_priority == valid_priority.lower():
            return valid_priority

    raise ValueError("Priority must be High, Medium, or Low.")


def parse_due_date(date_text):
    """Convert YYYY-MM-DD text into a datetime.date object."""
    if not isinstance(date_text, str):
        raise ValueError("Due date must use YYYY-MM-DD format.")

    cleaned_date = date_text.strip()

    try:
        parsed_date = datetime.strptime(cleaned_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Please enter a real date in YYYY-MM-DD format.") from None

    if parsed_date.strftime("%Y-%m-%d") != cleaned_date:
        raise ValueError("Please use YYYY-MM-DD, for example 2026-11-01.")

    return parsed_date


class Task:
    """Store one study task."""

    def __init__(
        self,
        task_id,
        name,
        course,
        due_date,
        priority,
        completed=False,
    ):
        if not isinstance(task_id, int) or isinstance(task_id, bool) or task_id <= 0:
            raise ValueError("Task ID must be a positive integer.")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Task name cannot be empty.")

        if not isinstance(course, str) or not course.strip():
            raise ValueError("Course cannot be empty.")

        if not isinstance(completed, bool):
            raise ValueError("Completed must be True or False.")

        self.task_id = task_id
        self.name = name.strip()
        self.course = course.strip()
        self.due_date = parse_due_date(due_date)
        self.priority = normalize_priority(priority)
        self.completed = completed

    def __str__(self):
        """Return a readable summary of the task."""
        if self.completed:
            status = "Completed"
        else:
            status = "Incomplete"

        return (
            f"[{self.task_id}] {self.name} | {self.course} | "
            f"{self.due_date.isoformat()} | {self.priority} | {status}"
        )


if __name__ == "__main__":
    example_task = Task(
        task_id=1,
        name="Finish COMP9001 Project",
        course="COMP9001",
        due_date="2026-11-01",
        priority="High",
    )

    print(example_task)
