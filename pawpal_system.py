from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, time
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

    def next_occurrence(self) -> Optional[Task]:
        """Create the next occurrence of a recurring task if applicable."""
        freq = self.frequency.lower()
        if freq not in {"daily", "weekly"}:
            return None

        delta = timedelta(days=1 if freq == "daily" else 7)
        next_deadline = self.deadline + delta if self.deadline else None

        next_task_id = f"{self.task_id}_next"

        return Task(
            task_id=next_task_id,
            type=self.type,
            duration_minutes=self.duration_minutes,
            frequency=self.frequency,
            priority=self.priority,
            deadline=next_deadline,
            preferred_time_window=self.preferred_time_window,
            assigned=False,
            notes=self.notes,
            status="pending",
        )

    def mark_done(self) -> Optional[Task]:
        """Mark the task as completed and return the next occurrence for recurring tasks."""
        self.status = "done"
        return self.next_occurrence()

    def reschedule(self, new_deadline: datetime) -> None:
        """Reschedule the task to a new deadline."""
        self.deadline = new_deadline

    def score(self) -> float:
        """
        Calculate the task's priority score for scheduling decisions.
        
        Algorithm: Returns the task's priority value as a float, used to rank tasks
        in the scheduler. Higher values indicate higher priority.
        
        Returns:
            float: The priority score (converted from int priority field).
        """
        return float(self.priority)

    def to_display(self) -> str:
        """Return a display string for the task."""
        return f"{self.type} ({self.duration_minutes}m, priority={self.priority})"

    def start_time(self) -> Optional[str]:
        """Return the preferred start time for sorting, as HH:MM."""
        if self.preferred_time_window:
            start_window = self.preferred_time_window.split("-")[0].strip()
            return start_window
        if self.deadline:
            return self.deadline.strftime("%H:%M")
        return None

    def as_time_interval(self) -> Optional[tuple[time, time]]:
        """Return a (start, end) time interval for conflict checks."""
        if not self.preferred_time_window and not self.deadline:
            return None

        time_str = self.start_time()
        if not time_str:
            return None

        try:
            start_dt = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return None

        end_dt: time
        if self.preferred_time_window and "-" in self.preferred_time_window:
            end_part = self.preferred_time_window.split("-")[1].strip()
            try:
                end_dt = datetime.strptime(end_part, "%H:%M").time()
            except ValueError:
                end_dt = (datetime.combine(date.today(), start_dt) + timedelta(minutes=self.duration_minutes)).time()
        else:
            end_dt = (datetime.combine(date.today(), start_dt) + timedelta(minutes=self.duration_minutes)).time()

        return (start_dt, end_dt)


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
        """
        Organize all pending tasks into the schedule for the given date.
        
        Algorithm: Retrieves all pending tasks from the owner's pets, iterates through them,
        and assigns unassigned tasks to the schedule for the given date. Uses a simple
        sequential assignment approach without conflict detection.
        
        Args:
            date_ (date): The date for which to organize tasks.
            
        Side effects: Marks assigned tasks with assigned=True and adds them to the schedule.
        """
        schedule = self.get_schedule(date_)
        if not schedule:
            schedule = self.create_schedule(date_)
        pending_tasks = self.owner.get_pending_tasks()
        # Simple logic: assign tasks to schedule
        for task in pending_tasks:
            if not task.assigned:
                schedule.add_task(task)
                task.assigned = True

    def find_task_and_pet(self, task_id: str) -> Optional[tuple[Task, Pet]]:
        """Locate a task and its associated pet."""
        for pet in self.owner.get_pets():
            for task in pet.get_tasks():
                if task.task_id == task_id:
                    return task, pet
        return None

    def mark_task_complete(self, task_id: str) -> Optional[Task]:
        """Mark a task complete and create the next recurring instance if needed."""
        lookup = self.find_task_and_pet(task_id)
        if not lookup:
            return None

        task, pet = lookup
        new_task = task.mark_done()

        if new_task is not None and new_task.frequency.lower() in {"daily", "weekly"}:
            pet.add_task(new_task)

            # Optionally, also add to today's schedule if it exists and the original is in schedule.
            for schedule in self.schedules.values():
                if any(t.task_id == task_id for t in schedule.tasks):
                    schedule.add_task(new_task)
                    break

        return new_task

    def manage_tasks(self) -> None:
        """
        Ensure all pets have necessary tasks based on their daily needs.
        
        Algorithm: Iterates through all owner pets and their defined daily needs.
        For each need, generates a task if one does not already exist. Task ID is
        derived from pet name and need type to ensure uniqueness.
        
        Side effects: Creates and adds new Task objects to pets' task lists if needed.
        """
        # Logic to manage tasks across pets
        for pet in self.owner.get_pets():
            # Ensure pets have necessary tasks based on needs
            for need, desc in pet.needs().items():
                # Create task if not exists
                task_id = f"{pet.name}_{need}"
                if not any(t.task_id == task_id for t in pet.get_tasks()):
                    task = Task(task_id=task_id, type=need, duration_minutes=30, notes=desc)
                    pet.add_task(task)

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted by start time (HH:MM), using lambda as key."""
        source_tasks = tasks if tasks is not None else self.owner.get_all_tasks()

        def parse_hhmm(value: Optional[str]) -> time:
            if value is None:
                return time.max
            try:
                return datetime.strptime(value, "%H:%M").time()
            except ValueError:
                return time.max

        return sorted(
            source_tasks,
            key=lambda task: parse_hhmm(task.start_time()),
        )

    def filter_tasks(self, pet_name: Optional[str] = None, status: Optional[str] = None) -> List[Task]:
        """Filter tasks by pet and/or status."""
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for pet in self.owner.get_pets() if pet.name == pet_name for t in pet.get_tasks()]
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    def find_conflicts(self, task: Task, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Detect overlapping tasks using time intervals."""
        check_tasks = tasks if tasks is not None else self.owner.get_all_tasks()
        origin_interval = task.as_time_interval()
        if origin_interval is None:
            return []

        conflicts: List[Task] = []
        s1, e1 = origin_interval

        for candidate in check_tasks:
            if candidate.task_id == task.task_id:
                continue
            candidate_interval = candidate.as_time_interval()
            if candidate_interval is None:
                continue
            s2, e2 = candidate_interval
            if s1 < e2 and s2 < e1:
                conflicts.append(candidate)

        return conflicts

    def add_recurring_task(self, task: Task, occurrences: int = 7) -> List[Task]:
        """Create recurring task instances based on task.frequency."""
        arrivals: List[Task] = []
        delta = timedelta(days=1)
        freq = task.frequency.lower()
        if freq == "weekly":
            delta = timedelta(weeks=1)
        elif freq == "monthly":
            delta = timedelta(days=30)

        current_date = date.today()
        for i in range(occurrences):
            instance = Task(
                task_id=f"{task.task_id}_{i}",
                type=task.type,
                duration_minutes=task.duration_minutes,
                frequency=task.frequency,
                priority=task.priority,
                deadline=(task.deadline + i * delta) if task.deadline else None,
                preferred_time_window=task.preferred_time_window,
                assigned=task.assigned,
                notes=task.notes,
                status=task.status,
            )
            arrivals.append(instance)
            current_date += delta
        return arrivals

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
        """
        Generate a plan with given constraints and record reasoning.
        
        Algorithm: Accepts optional constraint dictionary, stores constraints applied,
        and sets a default explanation message. Constraints can include time limits,
        priority thresholds, or owner preferences.
        
        Args:
            constraints (dict, optional): Dictionary of constraint keys and values.
            
        Side effects: Updates constraints_applied field and explanation message.
        """
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

    def get_conflict_warnings(self) -> List[str]:
        """Return lightweight conflict warnings for overlapping tasks in the schedule."""
        warnings: List[str] = []
        for i in range(len(self.tasks)):
            for j in range(i + 1, len(self.tasks)):
                t1 = self.tasks[i]
                t2 = self.tasks[j]
                int1 = t1.as_time_interval()
                int2 = t2.as_time_interval()
                if not int1 or not int2:
                    continue
                s1, e1 = int1
                s2, e2 = int2
                if s1 < e2 and s2 < e1:
                    warnings.append(
                        f"Conflict: {t1.task_id} ({t1.preferred_time_window}) "
                        f"and {t2.task_id} ({t2.preferred_time_window}) overlap"
                    )
        return warnings
