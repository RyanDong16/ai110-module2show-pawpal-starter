# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
++ The initial UML design consists of Owner, Pet, Task, and Scheduler. The UML design outlines the pet care scheduling app that makes pet care efficient and organized. The pet owner has the pets, the pets have tasks, and the task have time constraints leading to the daily plan.

- What classes did you include, and what responsibilities did you assign to each?
++ 1) Owner
Responsibility: represents the pet owner.
Holds owner info (name, contact_info), availability breakouts (daily_availability), preference rules (preferences), and load limits (max_daily_tasks).
Provides methods to update availability/preferences and simple eligibility check (can_do_task).

++ 2) Pet
Responsibility: represents the pet that needs care.
Holds pet profile fields (name, species, breed, age) and care metadata (health_conditions, daily_needs, energy_level).
Provides methods to expose what is needed (needs), risk assessment (is_high_risk), and readable summary (describe).
++ 3) Task
Responsibility: atomic care work item.
Holds task details (task_id, type, duration_minutes, priority, deadline, preferred_time_window, assigned, notes, status).
Provides lifecycle behavior (mark_done, reschedule), deadline check (is_overdue), scoring for scheduling (score), and display string (to_display).
++ 4) Schedule
Responsibility: the daily plan aggregator.
Holds date, owner/pet refs, scheduled task list, computed totals (total_time), constraints applied, and textual rationale (explanation).
Provides plan management and validation (add_task, remove_task, generate_plan, validate, get_timeline, explain, adjust_for_overflow).

**b. Design changes**

- Did your design change during implementation?
++ Yes

- If yes, describe at least one change and why you made it.
++ Missing explicit relationships: 
Schedule stores owner and pet, but Owner doesn’t have pets list (one-to-many) in this model.
Task doesn’t point to Pet or Owner directly; it’s implied via schedule. That’s okay, but if you later query tasks by pet, you'll need explicit linking.
Schedule doesn’t enforce that a task belongs to the pet or owner, so inconsistent associations could happen.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
++ time, priority, status, recurrence, preferences

- How did you decide which constraints mattered most?
++ Decided which constraints mattered most by prioritized constraints based on real pet-owner needs and what was already supported in the model. Time first because Pets need feeding/walks at times. Status second because pending vs done drives whether tasks are scheduled. Recurrence third because daily/weekly recurring tasks are real in pet care (repeating meds/food). Priority fourth because Task.priority lets you choose what to do first when time is tight. Lastly, Preferences last because a real owner system needs this for practical, human-aligned scheduling. So I kept “time + status + recurrence” as the highest urgency, with priority/preferences as supporting constraints for better scheduling decisions.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
++ The scheduler uses a simple sequential assignment approach in `organize_tasks()` that adds pending tasks to the schedule without checking for time conflicts or overlaps. This means if two tasks have overlapping preferred_time_windows, both will be added to the schedule anyway, leaving conflict resolution to the user.

- Why is that tradeoff reasonable for this scenario?
++ This is a Module 2 learning project, not a production system for critical pet care. Simple working logic is more valuable than perfect optimization at this stage.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
++ AI helped flesh out the four core classes (Task, Pet, Owner, Scheduler) with specific methods, attributes, and responsibilities. Instead of guessing, AI suggested logical method signatures (e.g., add_task, get_pending_tasks, organize_tasks).
++ AI generated the full method bodies for core functionality (marking tasks complete, adding pets to owners, filtering tasks by status). This accelerated the build phase.

- What kinds of prompts or questions were most helpful?
++ "Flesh out the core implementation of your four classes" and "Write a script that performs the following" were most helpful because they gave AI a specific, concrete task with clear scope. This avoided vague suggestions and generated directly usable code.
++ "If a user submits a form to add a new pet, which class method should handle that data?" forced alignment between UI design and backend logic. Very clarifying.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
++ I did not accept the AI's initial suggestion to use a complex constraint satisfaction algorithm for scheduling tasks. Instead, I opted for a simpler, sequential assignment approach that better fit the scope and requirements of this project.

- How did you evaluate or verify what the AI suggested?
++ I evaluated the AI's suggestion by:
I wrote two unit tests to verify (task completion, pet task addition) that both approaches would satisfy, but the simpler approach passed immediately without complexity.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
++ Called mark_done() on a Task and verified that the status changed from "pending" to "done". This tests the core task lifecycle behavior.
++ Added a Task to a Pet using add_task() and verified the pet's task count increased. This tests the pet-task relationship and data aggregation.

- Why were these tests important?
++ Task completion is the foundation of the scheduling workflow—if tasks don't mark complete correctly, recurring tasks won't be generated and the daily schedule stays stale. Pet task addition is critical because the entire scheduling logic depends on aggregating tasks from pets; if tasks don't properly attach to pets, the aggregate operations (get_pending_tasks, organize_tasks) would fail silently. These two tests verify the core data model relationships work before building more complex scheduling logic on top.

**b. Confidence**

- How confident are you that your scheduler works correctly?
++ I'm confident that the core scheduling logic works correctly. The task completion, pet task addition, and daily schedule generation all pass unit tests and manual testing through the Streamlit UI.


- What edge cases would you test next if you had more time?
++ Tasks with past deadlines should be marked overdue. Schedule should handle deadline < today gracefully.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
++ Using Copilot as a reference to help whenever I was having trouble with the instructions. Getting the Streamlit app to work overall was satisfying as well since it was a confusing project compared to the previous week's project.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
++ If I had the chance to redesign/ improve the code next time, I would not rely on using Copilot as much as I did. I understand that I'm learning to use AI, but I want to be more in control of the process.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
++ One thing I learned from this project is the UML diagram. The diagram helped with visualizing the connections/ roadmap of what and how the code should be implemented.
