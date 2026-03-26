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

    # Create at least three Tasks with different times
    task1 = Task(task_id="feed_buddy", type="Feeding", duration_minutes=15, frequency="daily", priority=1)
    task2 = Task(task_id="walk_buddy", type="Walking", duration_minutes=30, frequency="daily", priority=2)
    task3 = Task(task_id="groom_whiskers", type="Grooming", duration_minutes=20, frequency="weekly", priority=1)

    # Add tasks to pets
    pet1.add_task(task1)
    pet1.add_task(task2)
    pet2.add_task(task3)

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
        for task in schedule.tasks:
            # Extract pet name from task_id (assuming format like "action_petname")
            pet_name = task.task_id.split('_', 1)[1].capitalize() if '_' in task.task_id else "Unknown"
            print(f"• {pet_name}: {task.to_display()}")
        print(f"\nTasks completed: {len([t for t in schedule.tasks if t.status == 'done'])}/{len(schedule.tasks)}")
    else:
        print("No schedule found.")

if __name__ == "__main__":
    main()
