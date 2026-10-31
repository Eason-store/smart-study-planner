"""
Smart Study Planner
Author: Yuhao Huang (Niko)

Entry point for the terminal version of the program.
"""
from datetime import date

from advisor import (
    calculate_urgency,
    explain_recommendation,
    recommend_next_task,
)
from planner import (
    filter_tasks,
    generate_daily_plan,
    get_task_statistics,
    sort_tasks,
)
from storage import load_tasks, save_tasks
from task import Task, normalize_priority, parse_due_date
from ui import (
    clear_screen,
    colorize,
    get_inner_width,
    make_progress_bar,
    print_border,
    print_box_line,
    print_box_paragraph,
    show_error,
    show_info,
    show_page_header,
    show_success,
    show_warning,
    read_input,
)


def show_menu():
    """Display a clearly grouped main menu."""
    print()
    print_border("=")
    print_box_line(
        colorize(
            "SMART STUDY PLANNER".center(get_inner_width()),
            "cyan",
        )
    )
    print_border("=")

    print_box_line(colorize("  TASK MANAGEMENT", "yellow"))
    print_box_line(f"  [{colorize('1', 'yellow')}] Add Task")
    print_box_line(f"  [{colorize('2', 'yellow')}] View and Sort")
    print_box_line(f"  [{colorize('3', 'yellow')}] Search and Filter")
    print_box_line(f"  [{colorize('4', 'yellow')}] Edit Task")
    print_box_line(f"  [{colorize('5', 'yellow')}] Complete Task")
    print_box_line(f"  [{colorize('6', 'yellow')}] Delete Task")

    print_border()
    print_box_line(colorize("  INSIGHTS", "yellow"))
    print_box_line(f"  [{colorize('7', 'yellow')}] View Statistics")
    print_box_line(f"  [{colorize('8', 'yellow')}] Smart Study Advisor")
    print_box_line(f"  [{colorize('9', 'yellow')}] Daily Study Plan")

    print_border()
    print_box_line(f"  [{colorize('10', 'yellow')}] Save and Exit")
    print_border()


def pause_for_enter():
    """Wait until the user presses Enter before showing the menu again."""
    read_input("\nPress Enter to return to the main menu...")
    clear_screen()


def read_required_text(prompt):
    """Keep asking until the user enters non-empty text."""
    while True:
        value = read_input(prompt).strip()

        if value:
            return value

        show_warning("This field cannot be empty.")


def read_due_date():
    """Read and validate a date in YYYY-MM-DD format."""
    while True:
        date_text = read_input("Due date (YYYY-MM-DD): ").strip()

        try:
            parsed_date = parse_due_date(date_text)
            return parsed_date.isoformat()
        except ValueError as error:
            show_error(f"Invalid date: {error}")


def read_priority():
    """Read and normalize a priority value."""
    while True:
        priority_text = read_input("Priority (High/Medium/Low): ").strip()

        try:
            return normalize_priority(priority_text)
        except ValueError as error:
            show_error(f"Invalid priority: {error}")


def read_task_id():
    """Read and validate a positive task ID."""
    while True:
        task_id_text = read_input("Task ID: ").strip()

        try:
            task_id = int(task_id_text)
        except ValueError:
            show_warning("Task ID must be a whole number.")
            continue

        if task_id <= 0:
            show_warning("Task ID must be greater than zero.")
        else:
            return task_id


def read_yes_no(prompt):
    """Return True for yes, False for no, and repeat for invalid input."""
    while True:
        answer = read_input(prompt).strip().lower()

        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False

        show_warning("Please enter Y or N.")


def read_sort_order():
    """Read a task sorting option."""
    options = {
        "": "ID",
        "1": "ID",
        "2": "Due date",
        "3": "Priority",
        "4": "Urgency",
    }

    show_info("Sort by: [1] ID  [2] Due date  [3] Priority  [4] Urgency")

    while True:
        choice = read_input("Sort option (Enter for ID): ").strip()

        if choice in options:
            return options[choice]

        show_warning("Enter 1, 2, 3, 4, or press Enter.")


def read_status_filter():
    """Read an optional completion-status filter."""
    options = {
        "": "All",
        "a": "All",
        "all": "All",
        "i": "Incomplete",
        "incomplete": "Incomplete",
        "c": "Completed",
        "completed": "Completed",
    }

    while True:
        choice = read_input(
            "Status filter (All/Incomplete/Completed): "
        ).strip()
        cleaned_choice = choice.lower()

        if cleaned_choice in options:
            return options[cleaned_choice]

        show_warning("Enter All, Incomplete, or Completed.")


def read_priority_filter():
    """Read an optional priority filter."""
    while True:
        choice = read_input(
            "Priority filter (All/High/Medium/Low): "
        ).strip()

        if not choice or choice.lower() == "all":
            return "All"

        try:
            return normalize_priority(choice)
        except ValueError:
            show_warning("Enter All, High, Medium, or Low.")


def read_optional_text(prompt, current_value):
    """Read replacement text, using the current value when input is blank."""
    value = read_input(f"{prompt} [{current_value}]: ").strip()
    return value or current_value


def read_optional_due_date(current_date):
    """Read a replacement date, using the current date when input is blank."""
    current_text = current_date.isoformat()

    while True:
        date_text = read_input(
            f"Due date (YYYY-MM-DD) [{current_text}]: "
        ).strip()

        if not date_text:
            return current_text

        try:
            return parse_due_date(date_text).isoformat()
        except ValueError as error:
            show_error(f"Invalid date: {error}")


def read_optional_priority(current_priority):
    """Read a replacement priority, using the current priority when blank."""
    while True:
        priority_text = read_input(
            f"Priority (High/Medium/Low) [{current_priority}]: "
        ).strip()

        if not priority_text:
            return current_priority

        try:
            return normalize_priority(priority_text)
        except ValueError as error:
            show_error(f"Invalid priority: {error}")


def read_study_minutes():
    """Read a positive number of minutes for the daily plan."""
    while True:
        minutes_text = read_input("Available study minutes today: ").strip()

        try:
            minutes = int(minutes_text)
        except ValueError:
            show_warning("Please enter a whole number of minutes.")
            continue

        if minutes < 60:
            show_warning(
                "Your setting is below one hour. Please enter at least "
                "60 minutes; a session this short is not worth starting."
            )
        else:
            return minutes


def get_next_task_id(tasks):
    """Return one more than the highest task ID."""
    highest_id = 0

    for task in tasks:
        if task.task_id > highest_id:
            highest_id = task.task_id

    return highest_id + 1


def find_task_by_id(tasks, task_id):
    """Return the task with the requested ID, or None if it does not exist."""
    for task in tasks:
        if task.task_id == task_id:
            return task

    return None


def show_task_list(tasks):
    """Display tasks inside a consistent bordered panel."""
    print_border()

    for task in tasks:
        print_box_paragraph(str(task), indent="  ")

    print_border()


def add_task(tasks):
    """Collect valid task information and append a new task."""
    show_page_header("ADD TASK")

    name = read_required_text("Task name: ")
    course = read_required_text("Course: ")
    due_date = read_due_date()
    priority = read_priority()

    new_task = Task(
        task_id=get_next_task_id(tasks),
        name=name,
        course=course,
        due_date=due_date,
        priority=priority,
    )

    tasks.append(new_task)
    show_success(f"Task {new_task.task_id} has been added.")


def view_tasks(tasks):
    """Display all tasks, or a message when the list is empty."""
    show_page_header("VIEW AND SORT")

    if not tasks:
        show_info("There are no saved tasks yet.")
        return

    sort_order = read_sort_order()
    ordered_tasks = sort_tasks(tasks, sort_order)

    show_info(f"Sorted by: {sort_order}")
    show_task_list(ordered_tasks)
    show_info(f"Total tasks: {len(ordered_tasks)}")


def search_tasks(tasks):
    """Search and filter tasks by text, status, and priority."""
    show_page_header("SEARCH AND FILTER")

    if not tasks:
        show_info("There are no tasks to search.")
        return

    search_text = read_input(
        "Search name or course (Enter for all): "
    ).strip()
    status = read_status_filter()
    priority = read_priority_filter()
    matching_tasks = filter_tasks(tasks, search_text, status, priority)

    if not matching_tasks:
        show_warning("No tasks matched these filters.")
        return

    show_task_list(matching_tasks)
    show_info(f"Matches found: {len(matching_tasks)}")


def edit_task(tasks):
    """Edit an existing task while keeping its ID and completion status."""
    show_page_header("EDIT TASK")

    if not tasks:
        show_info("There are no tasks to edit.")
        return

    show_info("Current tasks")
    show_task_list(tasks)

    task_id = read_task_id()
    selected_task = find_task_by_id(tasks, task_id)

    if selected_task is None:
        show_warning(f"No task has ID {task_id}.")
        return

    show_info("Press Enter to keep the value shown in brackets.")
    name = read_optional_text("Task name", selected_task.name)
    course = read_optional_text("Course", selected_task.course)
    due_date = read_optional_due_date(selected_task.due_date)
    priority = read_optional_priority(selected_task.priority)

    try:
        updated_task = Task(
            task_id=selected_task.task_id,
            name=name,
            course=course,
            due_date=due_date,
            priority=priority,
            completed=selected_task.completed,
        )
    except ValueError as error:
        show_error(f"Task was not updated: {error}")
        return

    tasks[tasks.index(selected_task)] = updated_task
    show_success(f"Task {task_id} has been updated.")


def complete_task(tasks):
    """Mark an existing task as completed."""
    show_page_header("COMPLETE TASK")

    if not tasks:
        show_info("There are no tasks to complete.")
        return

    show_info("Current tasks")
    show_task_list(tasks)

    task_id = read_task_id()
    selected_task = find_task_by_id(tasks, task_id)

    if selected_task is None:
        show_warning(f"No task has ID {task_id}.")
        return

    if selected_task.completed:
        show_warning(f"Task {task_id} is already completed.")
        return

    selected_task.completed = True
    show_success(f"Task {task_id} has been marked as completed.")


def delete_task(tasks):
    """Delete a task after the user confirms the choice."""
    show_page_header("DELETE TASK")

    if not tasks:
        show_info("There are no tasks to delete.")
        return

    show_info("Current tasks")
    show_task_list(tasks)

    task_id = read_task_id()
    selected_task = find_task_by_id(tasks, task_id)

    if selected_task is None:
        show_warning(f"No task has ID {task_id}.")
        return

    show_info(f"Selected task: {selected_task}")

    confirmed = read_yes_no("Delete this task? (Y/N): ")

    if not confirmed:
        show_info(f"Task {task_id} was not deleted.")
        return

    tasks.remove(selected_task)
    show_success(f"Task {task_id} has been deleted.")
    show_info(f"Remaining tasks: {len(tasks)}")


def show_statistics(tasks):
    """Display progress and additional task statistics."""
    show_page_header("TASK STATISTICS")

    statistics = get_task_statistics(tasks)
    completion_percentage = statistics["completion_percentage"]

    print_border()
    print_box_line(f"  Total tasks    : {statistics['total']}")
    print_box_line(f"  Completed      : {statistics['completed']}")
    print_box_line(f"  Remaining      : {statistics['remaining']}")
    print_box_line(
        f"  Completion     : {completion_percentage:.1f}%"
    )
    print_box_line()
    print_box_line(colorize("  PROGRESS", "yellow"))
    print_box_line(
        f"  {make_progress_bar(completion_percentage)} "
        f"{completion_percentage:.1f}%"
    )
    print_border()
    print_box_line(colorize("  INCOMPLETE TASKS", "yellow"))
    print_box_line(f"  Overdue        : {statistics['overdue']}")
    print_box_line(f"  Due today      : {statistics['due_today']}")
    print_box_line(f"  Due in 1-3 days: {statistics['due_soon']}")
    print_box_line(f"  High priority  : {statistics['high_remaining']}")
    print_box_line(f"  Medium priority: {statistics['medium_remaining']}")
    print_box_line(f"  Low priority   : {statistics['low_remaining']}")
    print_border()


def show_daily_plan(tasks):
    """Generate a simple time-boxed plan for today's incomplete tasks."""
    show_page_header("DAILY STUDY PLAN")

    incomplete_tasks = [task for task in tasks if not task.completed]

    if not incomplete_tasks:
        show_info("There are no incomplete tasks to plan.")
        return

    show_info(
        "Each scheduled task receives at least 30 minutes. "
        "Extra time is shared by urgency score."
    )
    available_minutes = read_study_minutes()
    plan_data = generate_daily_plan(tasks, available_minutes)
    plan = plan_data["plan"]

    print_border()
    print_box_line(colorize("  TODAY'S SUGGESTED SEQUENCE", "yellow"))
    print_box_line()

    for position, item in enumerate(plan, start=1):
        task = item["task"]
        minutes = item["minutes"]
        label = (
            f"{position}. [{task.task_id}] {task.name} - "
            f"{minutes} minute(s) | Urgency {item['urgency_score']}"
        )
        print_box_paragraph(label, indent="  ")

    print_border()
    print_box_line(f"  Planned time   : {available_minutes - plan_data['unallocated_minutes']} minute(s)")
    print_box_line(f"  Available time : {available_minutes} minute(s)")
    print_box_line(f"  Unallocated    : {plan_data['unallocated_minutes']} minute(s)")
    print_border()
    show_success("All available study time has been allocated.")
    unscheduled_tasks = len(incomplete_tasks) - len(plan)

    if unscheduled_tasks > 0:
        show_info(
            f"{unscheduled_tasks} lower-urgency task(s) were not scheduled "
            "because there is not enough time for another 30-minute block."
        )

    show_info("Planned time does not mark tasks as completed automatically.")


def show_advisor(tasks):
    """Display the recommended task in a clear recommendation panel."""
    show_page_header("SMART STUDY ADVISOR")

    today = date.today()
    recommended_task = recommend_next_task(tasks, today)

    if recommended_task is None:
        print_box_line("  NO RECOMMENDATION")
        print_box_line()
        print_box_paragraph(
            "There are no incomplete tasks right now. "
            "Add a new task to receive study advice."
        )
        print_border("=")
        return

    urgency = calculate_urgency(recommended_task, today)
    days_left = urgency["days_left"]

    if days_left < 0:
        status = "OVERDUE"
        status_color = "red"
        timing = f"{-days_left} day(s) overdue"
    elif days_left == 0:
        status = "DUE TODAY"
        status_color = "red"
        timing = "Due today"
    elif days_left <= 3:
        status = "DUE SOON"
        status_color = "yellow"
        timing = f"{days_left} day(s) remaining"
    else:
        status = "UPCOMING"
        status_color = "green"
        timing = f"{days_left} day(s) remaining"

    print_box_line("  YOUR NEXT TASK")
    print_box_line()
    print_box_paragraph(
        f"[{recommended_task.task_id}] {recommended_task.name}",
        indent="    ",
    )
    print_box_paragraph(
        f"{recommended_task.course} | {recommended_task.priority} importance",
        indent="    ",
    )

    print_border()
    print_box_line(f"  Status       : {colorize(status, status_color)}")
    print_box_line(f"  Due date     : {recommended_task.due_date.isoformat()}")
    print_box_line(f"  Time left    : {timing}")
    print_box_line()
    print_box_line(f"  Urgency      : {urgency['score']} / 9")
    print_box_line(
        f"  Breakdown    : {urgency['priority_points']} priority"
        f" + {urgency['deadline_points']} deadline"
    )

    print_border()
    print_box_line("  WHY THIS TASK?")
    print_box_line()
    print_box_paragraph(explain_recommendation(recommended_task, today))

    print_border()
    print_box_paragraph(
        "Tie-break: earlier due date, higher priority, then lower task ID."
    )
    print_box_line()
    print_box_paragraph(
        "This is transparent rule-based guidance, not a guaranteed "
        "optimal study schedule."
    )
    print_border("=")


def run_menu(tasks):
    """Keep showing one clean screen at a time until the user exits."""
    while True:
        show_menu()
        choice = read_input("  Select an option (1-10): ").strip()

        if choice == "10":
            clear_screen()

            try:
                save_tasks(tasks)
            except (OSError, ValueError) as error:
                show_error(f"Could not save tasks: {error}")
                show_info("Your tasks are still open in memory.")
                show_info("Press Enter and try saving again.")
                pause_for_enter()
                continue

            show_success(f"{len(tasks)} task(s) written to tasks.txt.")
            show_info("Goodbye!")
            break

        clear_screen()

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            view_tasks(tasks)
        elif choice == "3":
            search_tasks(tasks)
        elif choice == "4":
            edit_task(tasks)
        elif choice == "5":
            complete_task(tasks)
        elif choice == "6":
            delete_task(tasks)
        elif choice == "7":
            show_statistics(tasks)
        elif choice == "8":
            show_advisor(tasks)
        elif choice == "9":
            show_daily_plan(tasks)
        else:
            show_warning("Please enter a number from 1 to 10.")

        pause_for_enter()


def main():
    """Start the program and load saved tasks when available."""
    clear_screen()
    show_info("Welcome to Smart Study Planner.")
    show_info("Organise your tasks and study with purpose.")

    try:
        tasks = load_tasks()
    except (OSError, ValueError) as error:
        print()
        show_error(f"Could not load tasks: {error}")
        show_info("The program will close without overwriting tasks.txt.")
        return

    if tasks:
        show_info(f"Loaded {len(tasks)} task(s) from tasks.txt.")
    else:
        show_info("Starting with an empty task list.")

    run_menu(tasks)


if __name__ == "__main__":
    main()
