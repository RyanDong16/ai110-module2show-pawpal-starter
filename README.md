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
