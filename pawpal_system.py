from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Optional

# logic layer where all your backend classes live

@dataclass
class Task:
    task_id: str
    type: str
    duration_minutes: int
    priority: int = 0
    deadline: Optional[datetime] = None
    preferred_time_window: Optional[str] = None
    assigned: bool = False
    notes: Optional[str] = None
    status: str = "pending"

    def is_overdue(self, current_time: datetime) -> bool:
        if not self.deadline:
            return False
        return current_time > self.deadline

    def mark_done(self) -> None:
        self.status = "done"

    def reschedule(self, new_deadline: datetime) -> None:
        self.deadline = new_deadline

    def score(self) -> float:
        return float(self.priority)

    def to_display(self) -> str:
        return f"{self.type} ({self.duration_minutes}m, priority={self.priority})"


@dataclass
class Pet:
    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[int] = None
    health_conditions: List[str] = field(default_factory=list)
    daily_needs: Dict[str, str] = field(default_factory=dict)
    energy_level: Optional[str] = None

    def needs(self) -> Dict[str, str]:
        return self.daily_needs

    def is_high_risk(self) -> bool:
        return bool(self.health_conditions)

    def describe(self) -> str:
        return f"{self.name} the {self.species} ({self.breed or 'mixed'})"


class Owner:
    def __init__(
        self,
        name: str,
        contact_info: Optional[str] = None,
        daily_availability: Optional[Dict[str, int]] = None,
        preferences: Optional[Dict[str, str]] = None,
        max_daily_tasks: Optional[int] = None,
    ) -> None:
        self.name = name
        self.contact_info = contact_info
        self.daily_availability = daily_availability or {}
        self.preferences = preferences or {}
        self.max_daily_tasks = max_daily_tasks

    def set_availability(self, availability: Dict[str, int]) -> None:
        self.daily_availability = availability

    def update_preference(self, key: str, value: str) -> None:
        self.preferences[key] = value

    def can_do_task(self, task: Task) -> bool:
        if self.max_daily_tasks is not None and self.max_daily_tasks <= 0:
            return False
        return True

    def summary(self) -> str:
        return f"Owner {self.name}: {len(self.preferences)} prefs"


class Schedule:
    def __init__(
        self,
        date_: Optional[date] = None,
        owner: Optional[Owner] = None,
        pet: Optional[Pet] = None,
        tasks: Optional[List[Task]] = None,
    ) -> None:
        self.date = date_ or date.today()
        self.owner = owner
        self.pet = pet
        self.tasks = tasks or []
        self.total_time = sum(task.duration_minutes for task in self.tasks)
        self.constraints_applied: Dict[str, str] = {}
        self.explanation: str = ""

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        self.total_time += task.duration_minutes

    def remove_task(self, task_id: str) -> None:
        self.tasks = [task for task in self.tasks if task.task_id != task_id]
        self.total_time = sum(task.duration_minutes for task in self.tasks)

    def generate_plan(self, constraints: Optional[Dict] = None) -> None:
        self.constraints_applied = constraints or {}
        self.explanation = "Generated plan with the given constraints"

    def validate(self) -> bool:
        return bool(self.tasks)

    def get_timeline(self) -> List[str]:
        return [task.to_display() for task in self.tasks]

    def explain(self) -> str:
        return self.explanation

    def adjust_for_overflow(self) -> None:
        if self.total_time > sum(self.owner.daily_availability.values()) if self.owner and self.owner.daily_availability else False:
            self.explanation += "\nAdjusted plan for overflow."
