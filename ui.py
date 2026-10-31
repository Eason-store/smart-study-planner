"""
Smart Study Planner
Shared terminal presentation helpers.
"""

import os
import re
import shutil
import sys
import textwrap


MIN_INNER_WIDTH = 20
MAX_INNER_WIDTH = 96

COLORS = {
    "cyan": "\033[96m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "grey": "\033[90m",
    "reset": "\033[0m",
}

ANSI_PATTERN = re.compile(r"\033\[[0-9;]*m")
COLOR_ENABLED = (
    sys.stdout.isatty()
    and os.environ.get("NO_COLOR") is None
)


def colorize(text, color):
    """Add terminal colour when the output supports it."""
    if not COLOR_ENABLED or color not in COLORS:
        return text

    return COLORS[color] + text + COLORS["reset"]


def visible_length(text):
    """Return text length without counting terminal colour codes."""
    return len(ANSI_PATTERN.sub("", text))


def get_terminal_width():
    """Return the current terminal width with a safe fallback."""
    return shutil.get_terminal_size(fallback=(80, 24)).columns


def get_inner_width():
    """Return a responsive content width for the current terminal."""
    terminal_width = get_terminal_width()
    return max(MIN_INNER_WIDTH, min(MAX_INNER_WIDTH, terminal_width - 6))


def get_left_margin():
    """Return the default left alignment for the interface."""
    return 0


def clear_screen():
    """Clear an interactive terminal before drawing the next screen."""
    if sys.stdout.isatty():
        print("\033[2J\033[H", end="")


def split_box_text(text, width):
    """Wrap text to the number of visible columns allowed in a box."""
    if not text or visible_length(text) <= width:
        return [text]

    plain_text = ANSI_PATTERN.sub("", text)
    leading_spaces = " " * (len(plain_text) - len(plain_text.lstrip(" ")))
    body_width = max(1, width - len(leading_spaces))
    body = plain_text.strip()

    return textwrap.wrap(
        body,
        width=body_width,
        initial_indent=leading_spaces,
        subsequent_indent=leading_spaces,
        break_long_words=True,
        break_on_hyphens=False,
    ) or [leading_spaces]


def print_border(character="-"):
    """Print a horizontal border that matches the interface width."""
    inner_width = get_inner_width()
    margin = " " * get_left_margin()
    print(margin + "+" + character * (inner_width + 2) + "+")


def print_box_line(text=""):
    """Print one padded line inside the interface border."""
    inner_width = get_inner_width()
    margin = " " * get_left_margin()

    for line in split_box_text(text, inner_width):
        padding = max(0, inner_width - visible_length(line))
        print(margin + "| " + line + (" " * padding) + " |")


def print_box_paragraph(text, indent="  "):
    """Print wrapped text without breaking the interface border."""
    print_box_line(indent + text)


def show_page_header(title):
    """Display a consistent title panel."""
    inner_width = get_inner_width()
    print()
    print_border("=")
    print_box_line(colorize(title.center(inner_width), "cyan"))
    print_border("=")


def show_message(message, color):
    """Print a wrapped, left-aligned status message."""
    margin = " " * get_left_margin()
    available_width = max(10, get_terminal_width() - len(margin))
    lines = textwrap.wrap(
        message,
        width=available_width,
        break_long_words=True,
        break_on_hyphens=False,
    )

    for line in lines or [""]:
        print(margin + colorize(line, color))


def show_success(message):
    """Display a success message."""
    show_message(f"[Success] {message}", "green")


def show_error(message):
    """Display an error message."""
    show_message(f"[Error] {message}", "red")


def show_warning(message):
    """Display a warning or invalid-input message."""
    show_message(f"[Warning] {message}", "yellow")


def show_info(message):
    """Display neutral information."""
    show_message(f"[Info] {message}", "cyan")


def read_input(prompt):
    """Read input with the prompt aligned to the centred interface."""
    print(" " * get_left_margin(), end="")
    return input(prompt)


def make_progress_bar(percentage, width=None):
    """Create an ASCII progress bar for the given percentage."""
    if width is None:
        width = max(10, min(30, get_inner_width() - 14))

    safe_percentage = max(0.0, min(100.0, percentage))
    filled_width = round((safe_percentage / 100) * width)
    empty_width = width - filled_width
    return "[" + "#" * filled_width + "-" * empty_width + "]"
