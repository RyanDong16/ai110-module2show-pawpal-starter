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
