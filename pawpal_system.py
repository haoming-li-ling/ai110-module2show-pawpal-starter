from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    preferred_time: str = ""
    completed: bool = False

    def mark_complete(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_pending_tasks(self) -> List[Task]:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> List[Task]:
        pass


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def generate_daily_plan(self) -> List[Task]:
        pass

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        pass

    def fits_in_time(self, tasks: List[Task]) -> List[Task]:
        pass

    def explain_plan(self) -> str:
        pass
