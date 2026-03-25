classDiagram
    class Owner {
        - name: str
        - contact_info: str
        - daily_availability: dict
        - preferences: dict
        - max_daily_tasks: int
        + set_availability(...)
        + update_preference(...)
        + can_do_task(task)
        + summary()
    }

    class Pet {
        - name: str
        - species: str
        - breed: str
        - age: int
        - health_conditions: list
        - daily_needs: dict
        - energy_level: str
        + needs()
        + is_high_risk()
        + describe()
    }

    class Task {
        - task_id: str
        - type: str
        - duration_minutes: int
        - priority: int
        - deadline: datetime
        - preferred_time_window: str
        - assigned: bool
        - notes: str
        - status: str
        + is_overdue(current_time)
        + mark_done()
        + reschedule(new_time)
        + score()
        + to_display()
    }

    class Schedule {
        - date: date
        - owner: Owner
        - pet: Pet
        - tasks: list~Task~
        - total_time: int
        - constraints_applied: dict
        - explanation: str
        + add_task(task)
        + remove_task(task_id)
        + generate_plan(constraints)
        + validate()
        + get_timeline()
        + explain()
        + adjust_for_overflow()
    }

    Owner "1" -- "1" Pet : owns
    Schedule "1" o-- "1" Owner
    Schedule "1" o-- "1" Pet
    Schedule "1" *-- "0..*" Task