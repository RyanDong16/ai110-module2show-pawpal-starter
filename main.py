from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import date

def main():
    # Create an Owner
    owner = Owner(name="John Doe", contact_info="john@example.com")

    # Create at least two Pets
    pet1 = Pet(name="Buddy", species="Dog", breed="Golden Retriever", age=3)
    pet2 = Pet(name="Whiskers", species="Cat", breed="Siamese", age=2)

    # Add pets to owner
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # Create tasks out-of-order with preferred time windows
    task1 = Task(task_id="feed_buddy", type="Feeding", duration_minutes=15, frequency="daily", priority=1, preferred_time_window="09:30-09:45")
    task2 = Task(task_id="walk_buddy", type="Walking", duration_minutes=30, frequency="daily", priority=2, preferred_time_window="08:00-08:30")
    task3 = Task(task_id="groom_whiskers", type="Grooming", duration_minutes=20, frequency="weekly", priority=1, preferred_time_window="10:00-10:20")
    task4 = Task(task_id="play_buddy", type="Play", duration_minutes=10, frequency="daily", priority=1, preferred_time_window="07:30-07:40", status="done")
    task5 = Task(task_id="feed_whiskers", type="Feeding", duration_minutes=15, frequency="daily", priority=1, preferred_time_window="09:30-09:45")

    # Add tasks to pets in non-chronological order
    pet1.add_task(task3)
    pet2.add_task(task2)
    pet2.add_task(task5)
    pet1.add_task(task4)
    pet1.add_task(task1)

    # Create Scheduler
    scheduler = Scheduler(owner)

    # Organize tasks for today
    today = date.today()
    scheduler.organize_tasks(today)

    # Get today's schedule
    schedule = scheduler.get_schedule(today)

    # Print Today's Schedule
    print("Today's Schedule:")
    if schedule:
        total_time = schedule.total_time
        print(f"Total estimated time: {total_time} minutes\n")

        # Print unsorted insertion sequence
        print("Unsorted insertion order:")
        for task in schedule.tasks:
            print(f"• {task.task_id}, {task.preferred_time_window}, status={task.status}")

        # Use the new sort_by_time method from Scheduler
        sorted_tasks = scheduler.sort_by_time(schedule.tasks)
        print("\nSorted by preferred time (HH:MM):")
        for task in sorted_tasks:
            print(f"• {task.task_id}, {task.preferred_time_window}, status={task.status}")

        # Use the new filter_tasks method from Scheduler
        pending_buddy = scheduler.filter_tasks(pet_name="Buddy", status="pending")
        print("\nFiltered (Buddy, pending):")
        for task in pending_buddy:
            print(f"• {task.task_id}, {task.preferred_time_window}, status={task.status}")

        all_done = scheduler.filter_tasks(status="done")
        print("\nFiltered (done):")
        for task in all_done:
            print(f"• {task.task_id}, {task.preferred_time_window}, status={task.status}")

        conflicts = schedule.get_conflict_warnings()
        if conflicts:
            print("\nConflict warnings:")
            for warning in conflicts:
                print(f"• {warning}")

        print(f"\nTasks completed: {len([t for t in schedule.tasks if t.status == 'done'])}/{len(schedule.tasks)}")
    else:
        print("No schedule found.")

if __name__ == "__main__":
    main()
