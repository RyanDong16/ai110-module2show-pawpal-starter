# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

The PawPal+ scheduler includes several core features:

- **Task Tracking**: Tasks track description, duration, priority, frequency (daily/weekly/monthly), deadline, and completion status
- **Pet Management**: Pets maintain a list of assigned tasks and expose their daily care needs
- **Owner Coordination**: Owners manage multiple pets and aggregate all tasks across them
- **Automated Scheduling**: The Scheduler organizes pending tasks into daily plans using a sequential assignment algorithm that respects task priorities and completion status
- **Constraint-Aware**: Plans can incorporate owner availability, preferences, and load limits (max tasks per day)
- **Interactive UI**: Streamlit app lets users add pets, manage tasks, and generate daily schedules on demand

**Key algorithm**: The scheduler uses a linear-time sequential assignment approach that prioritizes simplicity and clarity over NP-hard constraint optimization. This makes it fast to compute and easy to understand, while still producing functional daily schedules.

## Features & Algorithms

### 📅 Scheduling & Organization

**Sorting by Preferred Time** (`Scheduler.sort_by_time()`)
- Sorts all tasks chronologically by their start time in HH:MM format
- Uses lambda-based sorting with custom time parsing logic
- Tasks without explicit time windows are placed at the end of the schedule
- Handles invalid time formats gracefully

**Task Filtering** (`Scheduler.filter_tasks()`)
- Filters tasks by pet owner and/or completion status (pending/done)
- Supports single or combined filters using boolean predicates
- Returns aggregated task list across all pets

**Task Assignment** (`Scheduler.organize_tasks()`)
- Sequentially assigns all pending unassigned tasks to a specific date's schedule
- Marks tasks with `assigned=True` to prevent duplicates
- Maintains separation between task tracking and scheduling state

---

### ⚠️ Conflict Detection & Warnings

**Interval Overlap Detection** (`Scheduler.find_conflicts()`)
- Identifies all tasks that temporally overlap with a given task
- Uses mathematical interval comparison algorithm: `start₁ < end₂ AND start₂ < end₁`
- Computes both start time (from preferred window or deadline) and end time (from duration)
- Skips tasks without valid time intervals
- Returns conflicting task list for resolution

**Conflict Warnings** (`Schedule.get_conflict_warnings()`)
- Scans entire schedule for all overlapping task pairs (O(n²) nested comparison)
- Generates human-readable warning messages with task IDs and time windows
- Used to alert users before finalizing a schedule

---

### 🔄 Recurring Task Management

**Next Occurrence Calculation** (`Task.next_occurrence()`)
- Automatically generates the next instance of a recurring task
- Frequency-based deadline calculation:
  - **Daily**: adds 1 day to deadline
  - **Weekly**: adds 7 days to deadline
  - **Monthly**: adds 30 days to deadline (returns `None` if not daily/weekly)
- Creates new Task instance with unique ID suffix (`task_id_next`)

**Task Completion Tracking** (`Task.mark_done()`)
- Marks task status as "done"
- Automatically triggers generation of next recurring instance if applicable
- Returns the next Task object for re-scheduling

**Recurring Task Expansion** (`Scheduler.mark_task_complete()`)
- Marks a task complete across the system
- Locates the task and its associated pet
- Creates next recurring instance and adds to both pet's task list and active schedule
- Handles task lifecycle across multiple schedules seamlessly

**Bulk Recurrence Generation** (`Scheduler.add_recurring_task()`)
- Creates multiple instances of a single recurring task across a date range
- Supports configurable number of occurrences (default: 7)
- Generates unique task IDs with index suffix (`task_id_0`, `task_id_1`, etc.)
- Calculates incremental deadlines based on frequency

---

### 📊 Task Scoring & Analysis

**Priority Scoring** (`Task.score()`)
- Converts task priority to float for comparison operations
- Used to rank tasks during scheduling decisions

**Time Interval Parsing** (`Task.as_time_interval()`)
- Parses task into `(start_time, end_time)` tuple for conflict detection
- Extracts start time from preferred window (HH:MM-HH:MM format) or deadline
- Calculates end time from:
  - Explicit window end (if window is provided)
  - Start time + duration in minutes (if only start time exists)
- Handles parsing errors gracefully

**Start Time Extraction** (`Task.start_time()`)
- Returns task's preferred start time as HH:MM string
- Prioritizes: preferred time window → deadline HH:MM → None
- Used for sorting and scheduling display

---

### 📋 Plan Generation & Explanation

**Constraint-Based Planning** (`Schedule.generate_plan()`)
- Generates a daily schedule with optional constraint dictionary
- Records all constraints applied (time limits, priority thresholds, preferences)
- Stores human-readable explanation of generation decisions
- Supports flexible constraint keys for extensibility

**Plan Explanation** (`Schedule.explain()`)
- Returns stored explanation string describing why tasks were selected/ordered
- Appendable for additional constraint reasoning

**Overflow Adjustment** (`Schedule.adjust_for_overflow()`)
- Detects when total task duration exceeds owner's daily availability
- Updates schedule explanation if overflow is detected
- Supports time-based constraints

---

### ✅ Validation & Health Checks

**Overdue Task Detection** (`Task.is_overdue()`)
- Checks if task deadline has passed current time
- Returns boolean result

**Owner Capacity Validation** (`Owner.can_do_task()`)
- Validates that owner hasn't exceeded `max_daily_tasks` limit
- Prevents over-assignment of tasks

**Pet Risk Assessment** (`Pet.is_high_risk()`)
- Identifies pets with health conditions requiring special attention
- Returns boolean for conditional task prioritization

**Schedule Validation** (`Schedule.validate()`)
- Verifies schedule contains at least one task
- Returns boolean validity flag

## Testing PawPal+

### Running Tests

To run the complete test suite:

```bash
python -m pytest
```

For verbose output with detailed test names:

```bash
python -m pytest -v
```

### Test Coverage

The test suite includes **23 comprehensive tests** covering three critical areas:

#### **Sorting Correctness (5 tests)**
- Verifies tasks are sorted chronologically by start time (HH:MM)
- Validates handling of edge cases: missing time windows, identical times, boundary times (midnight, late evening)
- Confirms invalid time formats are gracefully handled (placed at end of schedule)
- Tests empty task lists return empty results without error

#### **Recurrence Logic (5 tests)**
- Confirms daily tasks create next-day instances when marked complete
- Validates weekly tasks create 7-day-ahead instances
- Ensures multiple daily recurring tasks at the same time are handled correctly
- Verifies recurring task series maintain consistent frequency across all instances
- Tests year boundary transitions for weekly recurring tasks (e.g., Dec 29 → Jan 5)

#### **Conflict Detection (5 tests)**
- Detects tasks scheduled at exact same time
- Identifies partial time overlaps between tasks
- Ensures adjacent non-overlapping tasks are not flagged as conflicts
- Validates conflict detection performs efficiently with large recurring task series (10+ instances)
- Confirms duration is properly factored into overlap calculations

#### **Core Functionality (8 tests)**
- Task completion and status updates
- Pet task management and counting
- Task filtering by pet and status
- Recurring task instance creation with unique IDs

### Test Results

✅ **23/23 tests passing** (all green)
- Execution time: < 0.1 seconds
- No failures or errors

### Confidence Level

⭐⭐⭐⭐ (4 out of 5 stars)

**Rationale:**
- **Strong coverage** of critical sorting, recurrence, and conflict-detection features
- **Comprehensive edge cases** tested (midnight times, year boundaries, large series)
- **All tests passing** with consistent, reliable results
- **Minor limitation**: Monthly recurring tasks return `None` from `next_occurrence()` (not yet fully implemented); edge cases involving duration extending past midnight not fully validated

The system is **production-ready** for daily and weekly task scheduling, with high confidence in sorting accuracy and conflict detection.


### 📸 Demo

<a href="/course_images/ai110/demo.png" target="_blank"><img src='/course_images/ai110/demo.png' title='PawPal+ App Screenshot' width='' alt='PawPal+ App' class='center-block' /></a>

**PawPal+ in action:** The Streamlit app displays the complete scheduling interface with:
- Owner and pet setup inputs
- Task management with duration and priority controls
- Real-time schedule generation with conflict detection
- Professional table views and timeline organization
- Explanations of scheduling decisions
