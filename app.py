import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Initialize owner and pet list in session_state
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)

if "pets" not in st.session_state:
    st.session_state.pets = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Add Pet handling
st.markdown("### Add a Pet")
if st.button("Add pet"):
    new_pet = Pet(name=pet_name, species=species)
    st.session_state.owner.add_pet(new_pet)
    st.session_state.pets.append(new_pet)
    st.success(f"Pet {pet_name} added to owner {st.session_state.owner.name}")

if st.session_state.pets:
    st.write("Current pets:")
    st.table([{"name": p.name, "species": p.species} for p in st.session_state.pets])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority}
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    scheduler = Scheduler(st.session_state.owner)
    # link tasks added in UI mode into actual Task objects, for demo we map existing input list
    for t in st.session_state.tasks:
        # primitive conversion, avoid duplication
        if not any(pet_task.task_id == t.get("title") for pet in st.session_state.pets for pet_task in pet.get_tasks()):
            task = Task(task_id=t.get("title"), type=t.get("title"), duration_minutes=t.get("duration_minutes", 0), priority=1)
            # attach to first pet for demo if exists
            if st.session_state.pets:
                st.session_state.pets[0].add_task(task)

    scheduler.organize_tasks(date.today())
    schedule = scheduler.get_schedule(date.today())
    if schedule and schedule.tasks:
        st.success("Schedule generated")
        st.write("### Schedule")
        for task in schedule.tasks:
            st.write(f"- {task.to_display()}")
    else:
        st.info("No tasks found to schedule. Add tasks and pets before generating.")
