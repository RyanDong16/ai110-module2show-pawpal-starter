import pytest
from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import date


class TestTask:
    def test_task_completion_changes_status(self):
        """Verify that calling mark_done() actually changes the task's status."""
        task = Task(task_id="test_task", type="Test", duration_minutes=10)
        assert task.status == "pending"
        task.mark_done()
        assert task.status == "done"


class TestPet:
    def test_adding_task_increases_pet_task_count(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        pet = Pet(name="TestPet", species="Dog")
        initial_count = len(pet.tasks)
        task = Task(task_id="test_task", type="Test", duration_minutes=10)
        pet.add_task(task)
        assert len(pet.tasks) == initial_count + 1


class TestScheduler:
    def test_sort_by_time_uses_hhmm_key(self):
        owner = Owner(name="Owner")
        schedule = Scheduler(owner)

        t1 = Task(task_id="t1", type="walk", duration_minutes=15, preferred_time_window="09:00-09:15")
        t2 = Task(task_id="t2", type="feed", duration_minutes=10, preferred_time_window="08:00-08:10")
        t3 = Task(task_id="t3", type="vet", duration_minutes=60, preferred_time_window="10:00-11:00")

        owner.add_pet(Pet(name="Fido", species="Dog", tasks=[t1, t2, t3]))
        sorted_tasks = schedule.sort_by_time()

        assert [t.task_id for t in sorted_tasks] == ["t2", "t1", "t3"]

    def test_filter_tasks_by_pet_and_status(self):
        owner = Owner(name="Owner")
        pet = Pet(name="Fido", species="Dog")
        pet.add_task(Task(task_id="t1", type="walk", duration_minutes=15, status="pending"))
        pet.add_task(Task(task_id="t2", type="med", duration_minutes=5, status="done"))
        owner.add_pet(pet)

        schedule = Scheduler(owner)
        filtered = schedule.filter_tasks(pet_name="Fido", status="pending")

        assert len(filtered) == 1
        assert filtered[0].task_id == "t1"

    def test_find_conflicts_with_overlapping_window(self):
        owner = Owner(name="Owner")
        schedule = Scheduler(owner)

        base = Task(task_id="t1", type="walk", duration_minutes=30, preferred_time_window="09:00-09:30")
        conflict = Task(task_id="t2", type="play", duration_minutes=15, preferred_time_window="09:15-09:30")
        no_conflict = Task(task_id="t3", type="feed", duration_minutes=10, preferred_time_window="10:00-10:10")

        owner.add_pet(Pet(name="Fido", species="Dog", tasks=[base, no_conflict]))
        conflicts = schedule.find_conflicts(conflict)

        assert len(conflicts) == 1
        assert conflicts[0].task_id == "t1"

    def test_add_recurring_task_creates_instances(self):
        owner = Owner(name="Owner")
        schedule = Scheduler(owner)

        base = Task(task_id="t1", type="med", duration_minutes=5, frequency="daily", preferred_time_window="08:00-08:05")
        recurrences = schedule.add_recurring_task(base, occurrences=3)

        assert len(recurrences) == 3
        assert recurrences[0].task_id == "t1_0"
        assert recurrences[1].task_id == "t1_1"

    def test_mark_task_complete_creates_next_occurrence(self):
        owner = Owner(name="Owner")
        pet = Pet(name="Fido", species="Dog")
        owner.add_pet(pet)

        daily_task = Task(task_id="feed_fido", type="Feeding", duration_minutes=15, frequency="daily", preferred_time_window="08:00-08:15")
        pet.add_task(daily_task)

        scheduler = Scheduler(owner)
        next_task = scheduler.mark_task_complete("feed_fido")

        assert daily_task.status == "done"
        assert next_task is not None
        assert next_task.task_id == "feed_fido_next"
        assert next_task.status == "pending"
        assert any(t.task_id == "feed_fido_next" for t in pet.tasks)

    def test_mark_task_complete_non_recurring_returns_none(self):
        owner = Owner(name="Owner")
        pet = Pet(name="Fido", species="Dog")
        owner.add_pet(pet)

        oneoff = Task(task_id="vet_fido", type="Vet", duration_minutes=60, frequency="once", preferred_time_window="14:00-15:00")
        pet.add_task(oneoff)

        scheduler = Scheduler(owner)
        new_task = scheduler.mark_task_complete("vet_fido")

        assert oneoff.status == "done"
        assert new_task is None
