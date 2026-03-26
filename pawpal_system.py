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
    frequency: str = "daily"  # e.g., "daily", "weekly", "monthly"
    priority: int = 0
    deadline: Optional[datetime] = None
    preferred_time_window: Optional[str] = None
    assigned: bool = False
    notes: Optional[str] = None
    status: str = "pending"

    def is_overdue(self, current_time: datetime) -> bool:
        """Check if the task is overdue based on current time."""
        if not self.deadline:
            return False
        return current_time > self.deadline

    def mark_done(self) -> None:
        """Mark the task as completed."""
        self.status = "done"

    def reschedule(self, new_deadline: datetime) -> None:
        """Reschedule the task to a new deadline."""
        self.deadline = new_deadline

    def score(self) -> float:
        """Calculate the task's priority score."""
        return float(self.priority)

    def to_display(self) -> str:
        """Return a display string for the task."""
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
    tasks: List[Task] = field(default_factory=list)

    def needs(self) -> Dict[str, str]:
        """Return the pet's daily needs."""
        return self.daily_needs

    def add_task(self, task: Task) -> None:
        """Add a task to the pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task from the pet's task list by ID."""
        self.tasks = [task for task in self.tasks if task.task_id != task_id]

    def get_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def get_pending_tasks(self) -> List[Task]:
        """Return only pending tasks for this pet."""
        return [task for task in self.tasks if task.status == "pending"]

    def is_high_risk(self) -> bool:
        """Check if the pet has health conditions."""
        return bool(self.health_conditions)

    def describe(self) -> str:
        """Return a description of the pet."""
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
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet from the owner's pet list by name."""
        self.pets = [pet for pet in self.pets if pet.name != pet_name]

    def get_pets(self) -> List[Pet]:
        """Return all pets owned by this owner."""
        return self.pets

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks from all pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def get_pending_tasks(self) -> List[Task]:
        """Return all pending tasks from all pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_pending_tasks())
        return tasks

    def set_availability(self, availability: Dict[str, int]) -> None:
        """Set the owner's daily availability."""
        self.daily_availability = availability

    def update_preference(self, key: str, value: str) -> None:
        """Update an owner preference."""
        self.preferences[key] = value

    def can_do_task(self, task: Task) -> bool:
        """Check if the owner can perform a task."""
        if self.max_daily_tasks is not None and self.max_daily_tasks <= 0:
            return False
        return True

    def summary(self) -> str:
        """Return a summary of the owner."""
        return f"Owner {self.name}: {len(self.pets)} pets, {len(self.get_all_tasks())} tasks"


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.schedules: Dict[date, Schedule] = {}

    def create_schedule(self, date_: date, pet: Optional[Pet] = None) -> Schedule:
        """Create a new schedule for the given date."""
        schedule = Schedule(date_=date_, owner=self.owner, pet=pet)
        self.schedules[date_] = schedule
        return schedule

    def get_schedule(self, date_: date) -> Optional[Schedule]:
        """Get the schedule for the given date."""
        return self.schedules.get(date_)

    def organize_tasks(self, date_: date) -> None:
        """Organize pending tasks into the schedule for the given date."""
        schedule = self.get_schedule(date_)
        if not schedule:
            schedule = self.create_schedule(date_)
        pending_tasks = self.owner.get_pending_tasks()
        # Simple logic: assign tasks to schedule
        for task in pending_tasks:
            if not task.assigned:
                schedule.add_task(task)
                task.assigned = True

    def manage_tasks(self) -> None:
        """Ensure all pets have necessary tasks based on their needs."""
        # Logic to manage tasks across pets
        for pet in self.owner.get_pets():
            # Ensure pets have necessary tasks based on needs
            for need, desc in pet.needs().items():
                # Create task if not exists
                task_id = f"{pet.name}_{need}"
                if not any(t.task_id == task_id for t in pet.get_tasks()):
                    task = Task(task_id=task_id, type=need, duration_minutes=30, notes=desc)
                    pet.add_task(task)

    def get_all_scheduled_tasks(self) -> List[Task]:
        """Return all tasks from all schedules."""
        tasks = []
        for schedule in self.schedules.values():
            tasks.extend(schedule.tasks)
        return tasks


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
        """Add a task to the schedule."""
        self.tasks.append(task)
        self.total_time += task.duration_minutes

    def remove_task(self, task_id: str) -> None:
        """Remove a task from the schedule by ID."""
        self.tasks = [task for task in self.tasks if task.task_id != task_id]
        self.total_time = sum(task.duration_minutes for task in self.tasks)

    def generate_plan(self, constraints: Optional[Dict] = None) -> None:
        """Generate a plan with given constraints."""
        self.constraints_applied = constraints or {}
        self.explanation = "Generated plan with the given constraints"

    def validate(self) -> bool:
        """Validate the schedule."""
        return bool(self.tasks)

    def get_timeline(self) -> List[str]:
        """Return a timeline of tasks."""
        return [task.to_display() for task in self.tasks]

    def explain(self) -> str:
        """Return the explanation for the schedule."""
        return self.explanation

    def adjust_for_overflow(self) -> None:
        """Adjust the schedule for time overflow."""
        if self.total_time > sum(self.owner.daily_availability.values()) if self.owner and self.owner.daily_availability else False:
            self.explanation += "\nAdjusted plan for overflow."
