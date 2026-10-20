from dataclasses import dataclass, field
from typing import List

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    preferred_time: str = ""
    pet_name: str = ""
    completed: bool = False

    def mark_complete(self) -> None:
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        self.tasks.remove(task)

    def get_pending_tasks(self) -> List[Task]:
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        self.pets.remove(pet)

    def get_all_tasks(self) -> List[Task]:
        return [t for pet in self.pets for t in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.plan: List[Task] = []

    def generate_daily_plan(self) -> List[Task]:
        pending = [t for t in self.owner.get_all_tasks() if not t.completed]
        self.plan = self.fits_in_time(self.sort_by_priority(pending))
        return self.plan

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        # High priority first; ties go to the earlier preferred time (tasks
        # with no preference last), then to the shorter task.
        return sorted(
            tasks,
            key=lambda t: (
                PRIORITY_RANK.get(t.priority.lower(), len(PRIORITY_RANK)),
                t.preferred_time == "",
                t.preferred_time,
                t.duration_minutes,
            ),
        )

    def fits_in_time(self, tasks: List[Task]) -> List[Task]:
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
        skipped = [
            t for t in self.owner.get_all_tasks()
            if not t.completed and id(t) not in scheduled
        ]
        for t in skipped:
            lines.append(
                f"Skipped: {t.title} ({t.pet_name}) - {t.duration_minutes} min "
                f"did not fit in the remaining time."
            )
        return "\n".join(lines)
