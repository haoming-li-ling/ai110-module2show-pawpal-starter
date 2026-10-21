"""Display helpers shared by the CLI demo and the Streamlit app."""
import os
import sys

from tabulate import tabulate

from pawpal_system import Task

PRIORITY_BADGES = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}
ANSI = {"high": "\033[31m", "medium": "\033[33m", "low": "\033[32m", "reset": "\033[0m"}

# First matching keyword in the title picks the emoji.
TASK_EMOJIS = [
    (("walk", "stroll", "run"), "🦮"),
    (("feed", "breakfast", "dinner", "lunch", "meal"), "🍽️"),
    (("med", "pill", "vet", "insulin"), "💊"),
    (("groom", "brush", "bath", "nail"), "✂️"),
    (("play", "toy", "train"), "🎾"),
]


def task_emoji(task: Task) -> str:
    """Return an emoji for the kind of task, guessed from its title."""
    title = task.title.lower()
    for keywords, emoji in TASK_EMOJIS:
        if any(k in title for k in keywords):
            return emoji
    return "🐾"


def status_icon(task: Task) -> str:
    """Return ✅ for a completed task and ⏳ for a pending one."""
    return "✅" if task.completed else "⏳"


def priority_badge(priority: str) -> str:
    """Return the priority with a colored-circle emoji, e.g. '🔴 High'."""
    return PRIORITY_BADGES.get(priority, priority)


def colorize(text: str, priority: str) -> str:
    """Wrap text in an ANSI color for its priority, only when printing to a terminal."""
    if not sys.stdout.isatty() or "NO_COLOR" in os.environ or priority not in ANSI:
        return text
    return f"{ANSI[priority]}{text}{ANSI['reset']}"


def schedule_table(plan: list, fmt: str = "simple") -> str:
    """Render a plan as a text table using tabulate."""
    rows = [
        [
            i,
            t.preferred_time or "--",
            f"{task_emoji(t)} {t.title}",
            t.pet_name,
            t.duration_minutes,
            colorize(priority_badge(t.priority), t.priority),
        ]
        for i, t in enumerate(plan, 1)
    ]
    headers = ["#", "Preferred", "Task", "Pet", "Min", "Priority"]
    return tabulate(rows, headers=headers, tablefmt=fmt, colalign=("right", "left", "left", "left", "right", "left"))
