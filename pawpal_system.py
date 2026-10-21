import json
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional, Union

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    title: str
    duration_minutes: int
    priority: str
    preferred_time: str = ""
    pet_name: str = ""
    completed: bool = False
    recurrence: str = ""  # "", "daily" or "weekly"
    due_date: str = ""  # ISO date; empty means due today

    def __post_init__(self) -> None:
        """Normalize priority to lowercase and reject unknown levels."""
        self.priority = self.priority.strip().lower()
        if self.priority not in PRIORITY_RANK:
            raise ValueError(
                f"priority must be one of {', '.join(PRIORITY_RANK)}, got {self.priority!r}"
            )

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as done; return the next occurrence if it recurs."""
        if self.completed:
            return None  # already done; don't spawn a duplicate occurrence
        self.completed = True
        days = RECURRENCE_DAYS.get(self.recurrence)
        if days is None:
            return None
        start = date.fromisoformat(self.due_date) if self.due_date else date.today()
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            preferred_time=self.preferred_time,
            pet_name=self.pet_name,
            recurrence=self.recurrence,
            due_date=(start + timedelta(days=days)).isoformat(),
        )

    def is_due(self, today: Optional[date] = None) -> bool:
        """Return True if this task is due on or before the given day."""
        return not self.due_date or date.fromisoformat(self.due_date) <= (
            today or date.today()
        )

    def to_dict(self) -> dict:
        """Return this task as a JSON-serializable dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Rebuild a task from a dict produced by to_dict()."""
        return cls(**data)


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and record the pet's name on the task."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet. Raises ValueError if it isn't there."""
        self.tasks.remove(task)

    def get_pending_tasks(self) -> List[Task]:
        """Return this pet's tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]

    def complete_task(self, task: Task) -> Optional[Task]:
        """Complete a task and, if it recurs, add and return its next occurrence."""
        nxt = task.mark_complete()
        if nxt is not None:
            self.add_task(nxt)
        return nxt

    def rename(self, new_name: str) -> None:
        """Rename this pet and keep its tasks' pet_name in sync."""
        self.name = new_name
        for task in self.tasks:
            task.pet_name = new_name

    def to_dict(self) -> dict:
        """Return this pet and its tasks as a JSON-serializable dict."""
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Rebuild a pet and its tasks from a dict produced by to_dict()."""
        pet = cls(name=data["name"], species=data["species"])
        for task_data in data.get("tasks", []):
            pet.add_task(Task.from_dict(task_data))
        return pet


@dataclass
class Owner:
    """A pet owner with a daily time budget and one or more pets."""

    name: str
    available_minutes: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner. Raises ValueError if it isn't there."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        return [t for pet in self.pets for t in pet.tasks]

    def to_dict(self) -> dict:
        """Return this owner, pets and tasks as a JSON-serializable dict."""
        return {
            "name": self.name,
            "available_minutes": self.available_minutes,
            "pets": [p.to_dict() for p in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Rebuild an owner, pets and tasks from a dict produced by to_dict()."""
        return cls(
            name=data["name"],
            available_minutes=data["available_minutes"],
            pets=[Pet.from_dict(p) for p in data.get("pets", [])],
        )

    def save_to_json(self, path: Union[str, Path]) -> None:
        """Write this owner (with pets and tasks) to a JSON file."""
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load_from_json(cls, path: Union[str, Path]) -> "Owner":
        """Read an owner from a JSON file written by save_to_json()."""
        return cls.from_dict(json.loads(Path(path).read_text()))


def _minutes(hhmm: str) -> Optional[int]:
    """Convert an HH:MM string to minutes since midnight, or None if invalid."""
    try:
        h, m = hhmm.split(":")
        return int(h) * 60 + int(m)
    except ValueError:
        return None


def _time_key(task: "Task") -> tuple:
    """Sort key: earliest preferred time first, tasks with no time last."""
    return (task.preferred_time == "", task.preferred_time)


class Scheduler:
    """Builds and explains a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for the given owner with an empty plan."""
        self.owner = owner
        self.plan: List[Task] = []

    def generate_daily_plan(self) -> List[Task]:
        """Build today's plan from pending tasks, store it, and return it."""
        self.plan = self.fits_in_time(self.sort_by_priority(self._due_pending()))
        return self.plan

    def _due_pending(self) -> List[Task]:
        """Return incomplete tasks that are due today or earlier."""
        today = date.today()
        return [
            t for t in self.owner.get_all_tasks()
            if not t.completed and t.is_due(today)
        ]

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered by priority, then preferred time, then length."""
        # High priority first; ties go to the earlier preferred time (tasks
        # with no preference last), then to the shorter task.
        return sorted(
            tasks,
            key=lambda t: (
                PRIORITY_RANK.get(t.priority.lower(), len(PRIORITY_RANK)),
                *_time_key(t),
                t.duration_minutes,
            ),
        )

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task; if it recurs, its next occurrence is added to its pet."""
        for pet in self.owner.pets:
            if any(t is task for t in pet.tasks):
                return pet.complete_task(task)
        raise ValueError("Task does not belong to any of this owner's pets.")

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks ordered by preferred time (HH:MM); unset times go last."""
        return sorted(tasks, key=_time_key)

    def filter_tasks(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Task]:
        """Return all tasks, optionally limited to one pet and/or a status."""
        return [
            t
            for t in self.owner.get_all_tasks()
            if (pet_name is None or t.pet_name == pet_name)
            and (completed is None or t.completed == completed)
        ]

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Return warnings for tasks whose preferred time windows overlap.

        Defaults to the current plan. Tasks without a preferred time are
        ignored. Never raises, so callers can show warnings and carry on.
        """
        timed = []
        for t in self.plan if tasks is None else tasks:
            start = _minutes(t.preferred_time) if t.preferred_time else None
            if start is not None:
                timed.append((start, t))
        timed.sort(key=lambda pair: pair[0])
        warnings = []
        # Sorted by start, so each task only needs checking against later ones
        # until one starts after it ends.
        for i, (start, a) in enumerate(timed):
            end = start + a.duration_minutes
            for other_start, b in timed[i + 1:]:
                if other_start >= end:
                    break
                who = (
                    f"for {a.pet_name}"
                    if a.pet_name == b.pet_name
                    else f"({a.pet_name} and {b.pet_name})"
                )
                warnings.append(
                    f"Conflict {who}: '{a.title}' at {a.preferred_time} "
                    f"({a.duration_minutes} min) overlaps '{b.title}' at "
                    f"{b.preferred_time}."
                )
        return warnings

    def find_next_available_slot(
        self,
        duration_minutes: int,
        earliest: str = "07:00",
        latest: str = "21:00",
        tasks: Optional[List[Task]] = None,
    ) -> Optional[str]:
        """Return the first HH:MM where a task of this length fits without overlap.

        Looks between `earliest` and `latest` for a gap in the timed tasks
        (the current plan by default). Tasks without a valid preferred time
        take up no space. Returns None if no gap is long enough.
        """
        start, end = _minutes(earliest), _minutes(latest)
        if start is None or end is None or duration_minutes <= 0:
            return None
        busy = []
        for t in self.plan if tasks is None else tasks:
            t_start = _minutes(t.preferred_time) if t.preferred_time else None
            if t_start is not None:
                busy.append((t_start, t_start + t.duration_minutes))
        busy.sort()
        cursor = start
        # Sweep forward: if the candidate window hits a busy block, jump past it.
        for b_start, b_end in busy:
            if b_start - cursor >= duration_minutes:
                break
            cursor = max(cursor, b_end)
        if cursor + duration_minutes > end:
            return None
        return f"{cursor // 60:02d}:{cursor % 60:02d}"

    def fits_in_time(self, tasks: List[Task]) -> List[Task]:
        """Return the tasks, in order, that fit in the owner's available minutes."""
        # Greedy in the given order; a task that doesn't fit is skipped so
        # smaller, lower-priority tasks can still use the remaining time.
        remaining = self.owner.available_minutes
        chosen = []
        for task in tasks:
            if task.duration_minutes <= remaining:
                chosen.append(task)
                remaining -= task.duration_minutes
        return chosen

    def explain_plan(self) -> str:
        """Describe the current plan and any tasks that were skipped."""
        if not self.plan:
            return "No tasks scheduled."
        used = sum(t.duration_minutes for t in self.plan)
        lines = [
            f"{self.owner.name} has {self.owner.available_minutes} minutes today; "
            f"the plan uses {used}."
        ]
        for i, t in enumerate(self.plan, 1):
            when = f", preferred {t.preferred_time}" if t.preferred_time else ""
            lines.append(
                f"{i}. {t.title} ({t.pet_name}) - {t.duration_minutes} min, "
                f"{t.priority} priority{when}"
            )
        scheduled = {id(t) for t in self.plan}
        skipped = [t for t in self._due_pending() if id(t) not in scheduled]
        for t in skipped:
            lines.append(
                f"Skipped: {t.title} ({t.pet_name}) - {t.duration_minutes} min "
                f"did not fit in the remaining time."
            )
        return "\n".join(lines)
