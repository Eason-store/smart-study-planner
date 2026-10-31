"""
Smart Study Planner
Save and load tasks using a plain text CSV file.
"""

import csv
from pathlib import Path

from task import Task


DATA_FILE = Path(__file__).resolve().parent / "tasks.txt"
FIELD_NAMES = (
    "task_id",
    "name",
    "course",
    "due_date",
    "priority",
    "completed",
)


def parse_completed(value):
    """Convert True/False text from the file into a Boolean value."""
    if not isinstance(value, str):
        raise ValueError("Completed status must be True or False.")

    cleaned_value = value.strip().lower()

    if cleaned_value == "true":
        return True
    if cleaned_value == "false":
        return False

    raise ValueError("Completed status must be True or False.")


def save_tasks(tasks, file_path=DATA_FILE):
    """Write all tasks to a UTF-8 text file."""
    try:
        with file_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELD_NAMES)
            writer.writeheader()

            for task in tasks:
                writer.writerow(
                    {
                        "task_id": task.task_id,
                        "name": task.name,
                        "course": task.course,
                        "due_date": task.due_date.isoformat(),
                        "priority": task.priority,
                        "completed": task.completed,
                    }
                )
    except csv.Error as error:
        raise ValueError(f"Could not write task data: {error}") from None


def load_tasks(file_path=DATA_FILE):
    """Read tasks from a text file, validating every record."""
    if not file_path.exists():
        return []

    try:
        with file_path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            if tuple(reader.fieldnames or ()) != FIELD_NAMES:
                raise ValueError(
                    "tasks.txt has an invalid header. "
                    "Expected: task_id,name,course,due_date,priority,completed"
                )

            tasks = []
            used_ids = set()

            for line_number, row in enumerate(reader, start=2):
                if None in row:
                    raise ValueError(
                        f"Too many values on line {line_number}."
                    )

                try:
                    task_id = int(row["task_id"])
                    completed = parse_completed(row["completed"])

                    task = Task(
                        task_id=task_id,
                        name=row["name"],
                        course=row["course"],
                        due_date=row["due_date"],
                        priority=row["priority"],
                        completed=completed,
                    )
                except (KeyError, TypeError, ValueError) as error:
                    raise ValueError(
                        f"Invalid task data on line {line_number}: {error}"
                    ) from None

                if task.task_id in used_ids:
                    raise ValueError(
                        f"Duplicate task ID {task.task_id} on line {line_number}."
                    )

                used_ids.add(task.task_id)
                tasks.append(task)

            return tasks
    except csv.Error as error:
        raise ValueError(f"Could not read task data: {error}") from None
