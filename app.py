import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import date

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** is a pet care planning assistant. It helps you organize and prioritize 
pet care tasks with intelligent scheduling and conflict detection.
"""
)

st.divider()

st.subheader("👤 Owner & 🐱 Pet Setup")
col1, col2, col3 = st.columns(3)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
with col3:
    species = st.selectbox("Species", ["dog", "cat", "other"])

# Initialize owner and pet list in session_state
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)

if "pets" not in st.session_state:
    st.session_state.pets = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Add Pet handling
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("#### Add a Pet")
with col2:
    if st.button("➕ Add pet", key="add_pet_btn"):
        new_pet = Pet(name=pet_name, species=species)
        st.session_state.owner.add_pet(new_pet)
        st.session_state.pets.append(new_pet)
        st.success(f"✓ Pet '{pet_name}' added!", icon="🎉")

if st.session_state.pets:
    st.markdown("##### Current Pets")
    pet_table_data = [
        {
            "Name": p.name,
            "Species": p.species,
            "# Tasks": len(p.get_tasks())
        }
        for p in st.session_state.pets
    ]
    st.table(pet_table_data)
else:
    st.info("No pets added yet. Add one above to get started!", icon="ℹ️")

st.divider()

st.markdown("#### 📋 Tasks")
col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk", key="task_title_input")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20, key="task_duration_input")
with col3:
    priority_map = {"Low": 1, "Medium": 2, "High": 3}
    priority_label = st.selectbox("Priority", ["Low", "Medium", "High"], index=2, key="task_priority_select")
    priority = priority_map[priority_label]

if st.button("➕ Add task", key="add_task_btn"):
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority, "priority_label": priority_label}
    )
    st.success(f"✓ Task '{task_title}' added!", icon="✨")

if st.session_state.tasks:
    st.markdown("##### Current Tasks")
    task_table_data = [
        {
            "Task": t["title"],
            "Duration (min)": t["duration_minutes"],
            "Priority": t.get("priority_label", "Medium"),
            "Score": t["priority"]
        }
        for t in st.session_state.tasks
    ]
    st.table(task_table_data)
else:
    st.info("No tasks added yet. Create one above to get started!", icon="ℹ️")

st.divider()

st.markdown("#### 🗓️ Build & View Schedule")
st.caption("Generate a smart schedule that sorts tasks by priority and time window, and detects conflicts.")

if st.button("🚀 Generate Intelligent Schedule", key="generate_schedule_btn"):
    if not st.session_state.pets:
        st.error("⚠️ Please add at least one pet before generating a schedule.", icon="❌")
    elif not st.session_state.tasks:
        st.error("⚠️ Please add at least one task before generating a schedule.", icon="❌")
    else:
        scheduler = Scheduler(st.session_state.owner)
        
        # Convert UI tasks to Task objects and attach to first pet
        for t in st.session_state.tasks:
            task_id = t.get("title").replace(" ", "_").lower()
            if not any(pet_task.task_id == task_id for pet in st.session_state.pets for pet_task in pet.get_tasks()):
                task = Task(
                    task_id=task_id,
                    type=t.get("title"),
                    duration_minutes=t.get("duration_minutes", 0),
                    priority=t.get("priority", 1),
                    preferred_time_window="09:00-17:00"  # Default work hours
                )
                if st.session_state.pets:
                    st.session_state.pets[0].add_task(task)

        # Organize tasks into schedule
        scheduler.organize_tasks(date.today())
        schedule = scheduler.get_schedule(date.today())
        
        if schedule and schedule.tasks:
            st.success(f"✓ Schedule generated for {date.today().strftime('%A, %B %d, %Y')}", icon="🎯")
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["📅 Schedule Timeline", "⚠️ Conflicts", "📊 Summary"])
            
            with tab1:
                # Sort tasks by time using scheduler method
                sorted_tasks = scheduler.sort_by_time(schedule.tasks)
                timeline_data = []
                
                for task in sorted_tasks:
                    timeline_data.append({
                        "Task": task.type,
                        "Duration (min)": task.duration_minutes,
                        "Priority": task.priority,
                        "Start Time": task.start_time() or "Flexible",
                        "Status": task.status.capitalize()
                    })
                
                if timeline_data:
                    st.markdown("##### Sorted Task Timeline")
                    st.table(timeline_data)
                else:
                    st.info("No tasks in schedule.")
            
            with tab2:
                # Show conflict warnings
                warnings = schedule.get_conflict_warnings()
                if warnings:
                    st.markdown("##### ⚡ Task Conflicts Detected")
                    for warning in warnings:
                        st.warning(warning, icon="⚠️")
                else:
                    st.success("✓ No conflicts detected! Your schedule is conflict-free.", icon="✅")
            
            with tab3:
                # Show summary and explanation
                st.markdown("##### Schedule Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Tasks", len(schedule.tasks))
                with col2:
                    st.metric("Total Duration", f"{schedule.total_time} min")
                with col3:
                    st.metric("Owner", st.session_state.owner.name)
                
                st.markdown("##### Plan Details")
                st.info(schedule.explain(), icon="ℹ️")
                
                if schedule.constraints_applied:
                    st.markdown("**Constraints Applied:**")
                    for key, value in schedule.constraints_applied.items():
                        st.write(f"• {key}: {value}")
        else:
            st.warning("No tasks could be scheduled. Check your task and pet configuration.", icon="⚠️")
