import pytest
from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import date, datetime, timedelta


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

    # ========== SORTING CORRECTNESS TESTS ==========

    def test_sort_by_time_with_none_windows(self):
        """Verify tasks without preferred_time_window are sorted to the end."""
        owner = Owner(name="Owner")
        schedule = Scheduler(owner)
        
        t1 = Task(task_id="t1", type="walk", duration_minutes=15, preferred_time_window="08:00-08:15")
        t2 = Task(task_id="t2", type="feed", duration_minutes=10)  # No time window
        t3 = Task(task_id="t3", type="play", duration_minutes=20, preferred_time_window="09:00-09:20")
        
        owner.add_pet(Pet(name="Fido", species="Dog", tasks=[t1, t2, t3]))
        sorted_tasks = schedule.sort_by_time()
        
        # Tasks with times should come first (in order), then tasks without
        assert sorted_tasks[0].task_id == "t1"
        assert sorted_tasks[1].task_id == "t3"
        assert sorted_tasks[2].task_id == "t2"

    def test_sort_by_time_with_identical_times(self):
        """Verify sorting behavior is consistent when multiple tasks have same start time."""
        owner = Owner(name="Owner")
        schedule = Scheduler(owner)
        
        t1 = Task(task_id="t1", type="walk", duration_minutes=15, preferred_time_window="09:00-09:15")
        t2 = Task(task_id="t2", type="feed", duration_minutes=10, preferred_time_window="09:00-09:10")
        t3 = Task(task_id="t3", type="play", duration_minutes=20, preferred_time_window="09:00-09:20")
        
        owner.add_pet(Pet(name="Fido", species="Dog", tasks=[t1, t2, t3]))
        sorted_tasks = schedule.sort_by_time()
        
        # All at 09:00; verify stable sort preserves insertion order
        assert sorted_tasks[0].task_id == "t1"
        assert sorted_tasks[1].task_id == "t2"
        assert sorted_tasks[2].task_id == "t3"

    def test_sort_by_time_boundary_times(self):
        """Verify sorting handles boundary times (midnight, late evening)."""
        owner = Owner(name="Owner")
        schedule = Scheduler(owner)
        
        t1 = Task(task_id="t1", type="evening_feed", duration_minutes=10, preferred_time_window="23:59-00:09")
        t2 = Task(task_id="t2", type="midnight_check", duration_minutes=10, preferred_time_window="00:00-00:10")
        t3 = Task(task_id="t3", type="morning_walk", duration_minutes=15, preferred_time_window="06:00-06:15")
        
        owner.add_pet(Pet(name="Fido", species="Dog", tasks=[t1, t2, t3]))
        sorted_tasks = schedule.sort_by_time()
        
        # 00:00 < 06:00 < 23:59
        assert sorted_tasks[0].task_id == "t2"  # 00:00
        assert sorted_tasks[1].task_id == "t3"  # 06:00
        assert sorted_tasks[2].task_id == "t1"  # 23:59

    def test_sort_by_time_with_invalid_format(self):
        """Verify tasks with invalid time formats are handled gracefully (placed at end)."""
        owner = Owner(name="Owner")
        schedule = Scheduler(owner)
        
        t1 = Task(task_id="t1", type="walk", duration_minutes=15, preferred_time_window="09:00-09:15")
        t2 = Task(task_id="t2", type="feed", duration_minutes=10, preferred_time_window="25:99-26:00")  # Invalid time
        t3 = Task(task_id="t3", type="play", duration_minutes=20, preferred_time_window="10:30-10:50")
        
        owner.add_pet(Pet(name="Fido", species="Dog", tasks=[t1, t2, t3]))
        sorted_tasks = schedule.sort_by_time()
        
        # Valid times first (08:00, 10:30), invalid time at end
        assert sorted_tasks[0].task_id == "t1"
        assert sorted_tasks[1].task_id == "t3"
        assert sorted_tasks[2].task_id == "t2"

    def test_sort_by_time_empty_task_list(self):
        """Verify sorting an empty task list returns empty list without error."""
        owner = Owner(name="Owner")
        schedule = Scheduler(owner)
        
        owner.add_pet(Pet(name="Fido", species="Dog", tasks=[]))
        sorted_tasks = schedule.sort_by_time()
        
        assert sorted_tasks == []

    # ========== RECURRENCE LOGIC TESTS ==========

    def test_mark_task_complete_daily_creates_next(self):
        """Verify that marking a daily task complete creates next occurrence for next day."""
        owner = Owner(name="Owner")
        pet = Pet(name="Fido", species="Dog")
        owner.add_pet(pet)
        
        today = datetime(2025, 3, 25, 8, 0)
        daily_task = Task(
            task_id="daily_feed",
            type="Feeding",
            duration_minutes=15,
            frequency="daily",
            deadline=today,
            preferred_time_window="08:00-08:15"
        )
        pet.add_task(daily_task)
        
        scheduler = Scheduler(owner)
        next_task = scheduler.mark_task_complete("daily_feed")
        
        assert daily_task.status == "done"
        assert next_task is not None
        assert next_task.frequency == "daily"
        assert next_task.deadline == today + timedelta(days=1)

    def test_mark_task_complete_weekly_creates_next(self):
        """Verify that marking a weekly task complete creates next occurrence for next week."""
        owner = Owner(name="Owner")
        pet = Pet(name="Fido", species="Dog")
        owner.add_pet(pet)
        
        today = datetime(2025, 3, 25, 10, 0)
        weekly_task = Task(
            task_id="weekly_bath",
            type="Bath",
            duration_minutes=60,
            frequency="weekly",
            deadline=today,
            preferred_time_window="10:00-11:00"
        )
        pet.add_task(weekly_task)
        
        scheduler = Scheduler(owner)
        next_task = scheduler.mark_task_complete("weekly_bath")
        
        assert weekly_task.status == "done"
        assert next_task is not None
        assert next_task.frequency == "weekly"
        assert next_task.deadline == today + timedelta(days=7)

    def test_multiple_daily_tasks_at_same_time(self):
        """Verify system handles multiple daily tasks scheduled at same time."""
        owner = Owner(name="Owner")
        pet = Pet(name="Fido", species="Dog")
        owner.add_pet(pet)
        
        t1 = Task(task_id="feed1", type="Feeding", duration_minutes=15, frequency="daily", preferred_time_window="09:00-09:15")
        t2 = Task(task_id="feed2", type="Feeding", duration_minutes=15, frequency="daily", preferred_time_window="09:00-09:15")
        
        pet.add_task(t1)
        pet.add_task(t2)
        
        scheduler = Scheduler(owner)
        conflicts = scheduler.find_conflicts(t1)
        
        assert len(conflicts) >= 1
        assert t2 in conflicts

    def test_recurring_task_series_with_consistent_frequency(self):
        """Verify recurring series maintains consistent frequency across all instances."""
        owner = Owner(name="Owner")
        scheduler = Scheduler(owner)
        
        base_task = Task(
            task_id="med",
            type="Medication",
            duration_minutes=5,
            frequency="daily",
            preferred_time_window="08:00-08:05"
        )
        
        recurrences = scheduler.add_recurring_task(base_task, occurrences=5)
        
        assert len(recurrences) == 5
        for recurring in recurrences:
            assert recurring.frequency == "daily"
            assert recurring.duration_minutes == 5
            assert recurring.type == "Medication"

    def test_mark_weekly_recurring_in_december_to_january(self):
        """Verify year boundary transitions correctly for weekly recurring tasks."""
        owner = Owner(name="Owner")
        pet = Pet(name="Fido", species="Dog")
        owner.add_pet(pet)
        
        # Task on Dec 29, 2024
        dec_date = datetime(2024, 12, 29, 10, 0)
        weekly_task = Task(
            task_id="weekly_vet",
            type="Vet Check",
            duration_minutes=30,
            frequency="weekly",
            deadline=dec_date,
            preferred_time_window="10:00-10:30"
        )
        pet.add_task(weekly_task)
        
        scheduler = Scheduler(owner)
        next_task = scheduler.mark_task_complete("weekly_vet")
        
        # Next occurrence should be Jan 5, 2025
        assert next_task is not None
        assert next_task.deadline.month == 1
        assert next_task.deadline.day == 5

    # ========== CONFLICT DETECTION TESTS ==========

    def test_find_conflicts_exact_time_match(self):
        """Verify scheduler detects conflicts when tasks are at exact same time."""
        owner = Owner(name="Owner")
        schedule = Scheduler(owner)
        
        task1 = Task(task_id="t1", type="walk", duration_minutes=30, preferred_time_window="09:00-09:30")
        task2 = Task(task_id="t2", type="feed", duration_minutes=15, preferred_time_window="09:00-09:15")
        
        owner.add_pet(Pet(name="Fido", species="Dog", tasks=[task1]))
        conflicts = schedule.find_conflicts(task2)
        
        assert len(conflicts) >= 1
        assert any(c.task_id == "t1" for c in conflicts)

    def test_find_conflicts_partial_overlap(self):
        """Verify scheduler detects partial time overlaps between tasks."""
        owner = Owner(name="Owner")
        schedule = Scheduler(owner)
        
        task1 = Task(task_id="t1", type="walk", duration_minutes=30, preferred_time_window="09:00-09:30")
        task2 = Task(task_id="t2", type="play", duration_minutes=30, preferred_time_window="09:20-09:50")
        
        owner.add_pet(Pet(name="Fido", species="Dog", tasks=[task1]))
        conflicts = schedule.find_conflicts(task2)
        
        assert len(conflicts) >= 1
        assert conflicts[0].task_id == "t1"

    def test_find_conflicts_no_overlap_adjacent_tasks(self):
        """Verify scheduler doesn't flag non-overlapping adjacent tasks as conflicts."""
        owner = Owner(name="Owner")
        schedule = Scheduler(owner)
        
        task1 = Task(task_id="t1", type="walk", duration_minutes=30, preferred_time_window="09:00-09:30")
        task2 = Task(task_id="t2", type="feed", duration_minutes=15, preferred_time_window="09:30-09:45")
        
        owner.add_pet(Pet(name="Fido", species="Dog", tasks=[task1]))
        conflicts = schedule.find_conflicts(task2)
        
        assert len(conflicts) == 0

    def test_conflict_detection_large_recurring_series(self):
        """Verify conflict detection performs correctly with many recurring task instances."""
        owner = Owner(name="Owner")
        schedule = Scheduler(owner)
        
        daily_task = Task(
            task_id="daily_feed",
            type="Feed",
            duration_minutes=15,
            frequency="daily",
            preferred_time_window="09:00-09:15"
        )
        
        # Create 10 daily instances
        recurrences = schedule.add_recurring_task(daily_task, occurrences=10)
        pet = Pet(name="Fido", species="Dog", tasks=recurrences)
        owner.add_pet(pet)
        
        # Add a conflicting task
        conflict_task = Task(
            task_id="conflict",
            type="Play",
            duration_minutes=30,
            preferred_time_window="09:10-09:40"
        )
        
        conflicts = schedule.find_conflicts(conflict_task)
        
        # All 10 daily instances at 09:00 should conflict with 09:10-09:40 window
        assert len(conflicts) == 10

    def test_conflict_detection_respects_duration(self):
        """Verify conflict detection accounts for task duration when checking overlaps."""
        owner = Owner(name="Owner")
        schedule = Scheduler(owner)
        
        # Task with duration extending the time interval
        task1 = Task(
            task_id="t1",
            type="walk",
            duration_minutes=45,
            preferred_time_window="09:00-09:45"
        )
        
        # Task that starts when first one ends
        task2 = Task(
            task_id="t2",
            type="feed",
            duration_minutes=15,
            preferred_time_window="09:45-10:00"
        )
        
        owner.add_pet(Pet(name="Fido", species="Dog", tasks=[task1]))
        conflicts = schedule.find_conflicts(task2)
        
        # No conflict if second task starts exactly when first ends
        assert len(conflicts) == 0
