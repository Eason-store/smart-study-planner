Smart Study Planner
===================

Author: Yuhao Huang (Niko)
Course: COMP9001

Overview
--------
Smart Study Planner is a terminal-based Python program for recording
university study tasks. It supports task management, progress statistics,
local text-file persistence, an explainable Smart Study Advisor, sort and
filter tools, and a simple daily study plan.

The program uses only the Python standard library. It does not require a
database, third-party package, web service, external API, or network access.

The terminal interface clears between screens, uses the default left alignment,
adapts to the current terminal width, and wraps long task names and messages.
Colour is disabled automatically when the output does not support it.

Requirements
------------
- Python 3
- A terminal or PowerShell

How to Run
----------
Open a terminal in the folder containing this README and run:

    python main.py

main.py is the required entry point.

Main Features
-------------
1. Add Task
2. View and Sort
3. Search and Filter
4. Edit Task
5. Complete Task
6. Delete Task
7. View Statistics
8. Smart Study Advisor
9. Daily Study Plan
10. Save and Exit

Search is case-insensitive and matches partial text in either the task name or
the course. Tasks can also be filtered by completion status and priority.
Complete, Edit, and Delete use a stable task ID rather than the task's position
in the displayed list.

Tasks can be sorted by ID, due date, priority, or urgency. The statistics page
shows an ASCII progress bar, overdue tasks, tasks due today, tasks due within
three days, and incomplete tasks grouped by priority.

Daily Study Plan
----------------
The daily study plan asks for the number of minutes available. It ranks
incomplete tasks using the same urgency rules as Smart Study Advisor. The user
must enter at least 60 minutes. Each scheduled task receives at least 30
minutes, and all remaining time is shared in proportion to urgency scores.
Integer rounding uses the largest remainders so the allocated minutes always
add up to the exact budget entered by the user.

If the available time cannot cover every incomplete task with a 30-minute
block, the most urgent tasks are scheduled first and the remaining tasks are
deferred. Planning time does not mark any task as completed.

Smart Study Advisor
-------------------
The advisor considers incomplete tasks only. Its urgency score is:

    urgency score = priority points + deadline points

Priority points are:

    High   = 3
    Medium = 2
    Low    = 1

Deadline points are:

    Overdue              = 6
    Due in 0 or 1 days   = 5
    Due in 2 or 3 days   = 4
    Due in 4 to 7 days   = 3
    Due in 8 to 14 days  = 2
    Due after 14 days    = 1

Tasks are ranked by the highest urgency score. Ties are resolved by the earlier
due date, then the higher priority, and finally the lower task ID.

The recommendation is a transparent rule-based study aid. It is not a claim of
an objectively optimal study schedule.

Saved Data
----------
Tasks are stored in:

    tasks.txt

The file is created in the same folder as main.py when the user selects
"Save and Exit". It uses UTF-8 text in CSV format with this header:

    task_id,name,course,due_date,priority,completed

The included tasks.txt contains six sample tasks for demonstration and testing.
It includes overdue, due-today, completed, different-priority, and long-name
examples. Users can edit or delete them through the program.

Task changes are kept in memory until Save and Exit is selected. If loading or
saving fails, the program displays an error. A malformed data file is not
silently overwritten.

Running the Tests
-----------------
From this project folder, run:

    python -m unittest discover -s tests -v

The automated tests cover:

- Task field and date validation, including leap years.
- Smart Study Advisor score boundaries, completion filtering, and tie-breaking.
- Saving and loading all task fields.
- Unicode text, commas, duplicate IDs, missing values, and malformed headers.
- Sorting, filtering, additional statistics, and daily-plan time allocation.
- Responsive interface width, long-text wrapping, and progress-bar boundaries.

File Structure
--------------
main.py
    Terminal interface, menu, and user-input handling.

task.py
    Task class, priority normalization, and date validation.

advisor.py
    Urgency scoring, task ranking, and recommendation explanations.

planner.py
    Task filtering, sorting, additional statistics, and daily-plan logic.

storage.py
    Saving and loading tasks.txt with CSV from the standard library.

ui.py
    Shared terminal borders, colour handling, message styles, and progress bars.

tasks.txt
    Runtime task data. It is created after the first successful save.

tests/
    Automated unit tests using the standard-library unittest module.

Known Limitations
-----------------
- The program is terminal-based; it does not include a Tkinter GUI.
- Daily-plan minutes are based on urgency scores, not estimated task duration.
- A daily plan requires at least 60 minutes.
- It does not automatically save after every task change.
- It manages one local task list and does not support user accounts.
