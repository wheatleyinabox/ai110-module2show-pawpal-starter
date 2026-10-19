import streamlit as st
from datetime import time

from pawpal_system import Pet, Schedule, Task, User

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# Streamlit reruns this whole script on every interaction, so a plain variable would be
# recreated each time. Only create the User if the session "vault" doesn't have one yet.
if "user" not in st.session_state:
    st.session_state.user = User(username="Valen", email="valen123@email.com", password="pawpal123")

user = st.session_state.user  # the same object on every rerun

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

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=user.get_username())
if owner_name and owner_name != user.get_username():
    user.set_username(owner_name)

st.subheader("Pets")
with st.form("add_pet_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name")
    with col2:
        breed = st.text_input("Breed")
    with col3:
        age = st.text_input("Age")
    health_conditions = st.text_input("Health conditions (optional)")
    medications = st.text_input("Medications (optional)")
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            user.add_pet(
                Pet(
                    name=pet_name.strip(),
                    breed=breed.strip(),
                    age=age.strip(),
                    health_conditions=health_conditions.strip(),
                    medications=medications.strip(),
                )
            )
        else:
            st.warning("Please enter a pet name.")

if user.get_pets():
    st.table(
        [
            {
                "Name": p.get_name(),
                "Breed": p.get_breed(),
                "Age": p.get_age(),
                "Health conditions": p.get_health_conditions(),
                "Medications": p.get_medications(),
            }
            for p in user.get_pets()
        ]
    )
else:
    st.info("No pets yet. Add one above.")

if user.get_pets():
    with st.expander("Edit or remove a pet"):
        pet_idx = st.selectbox(
            "Pet", range(len(user.get_pets())), format_func=lambda i: user.get_pets()[i].get_name()
        )
        pet = user.get_pets()[pet_idx]
        with st.form(f"edit_pet_form_{pet_idx}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_name = st.text_input("Pet name", value=pet.get_name())
            with col2:
                new_breed = st.text_input("Breed", value=pet.get_breed())
            with col3:
                new_age = st.text_input("Age", value=pet.get_age())
            new_health = st.text_input("Health conditions", value=pet.get_health_conditions())
            new_meds = st.text_input("Medications", value=pet.get_medications())
            save_col, delete_col = st.columns(2)
            save_pet = save_col.form_submit_button("Save changes")
            delete_pet = delete_col.form_submit_button("Delete pet")
        if save_pet:
            if new_name.strip():
                pet.set_name(new_name.strip())
                pet.set_breed(new_breed.strip())
                pet.set_age(new_age.strip())
                pet.set_health_conditions(new_health.strip())
                pet.set_medications(new_meds.strip())
                st.rerun()
            else:
                st.warning("Pet name can't be empty.")
        if delete_pet:
            for task in user.get_tasks():
                task.remove_pet(pet)  # don't leave the deleted pet attached to tasks
            user.remove_pet(pet)
            st.rerun()

st.markdown("### Tasks")
st.caption("Tasks are scheduled in priority order, so high priority tasks get the earliest slots.")

PRIORITIES = {"high": 1, "medium": 2, "low": 3}  # lower number is scheduled first

with st.form("add_task_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority_label = st.selectbox("Priority", list(PRIORITIES), index=0)
    task_desc = st.text_input("Description (optional)")
    pet_options = list(range(len(user.get_pets())))  # indices, so duplicate names still work
    task_pet_indexes = st.multiselect(
        "Pets for this task", pet_options, format_func=lambda i: user.get_pets()[i].get_name()
    )
    if st.form_submit_button("Add task"):
        if task_title.strip():
            task = Task(
                title=task_title.strip(),
                desc=task_desc.strip(),
                duration=int(duration),
                priority=PRIORITIES[priority_label],
            )
            for i in task_pet_indexes:
                task.add_pet(user.get_pets()[i])
            user.add_task(task)
        else:
            st.warning("Please enter a task title.")

if user.get_tasks():
    st.write("Current tasks:")
    st.table(
        [
            {
                "Title": t.get_title(),
                "Duration (min)": t.get_duration(),
                "Priority": t.get_priority(),
                "Pets": ", ".join(p.get_name() for p in t.get_pets()),
            }
            for t in user.get_tasks()
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

if user.get_tasks():
    with st.expander("Edit or remove a task"):
        task_idx = st.selectbox(
            "Task", range(len(user.get_tasks())), format_func=lambda i: user.get_tasks()[i].get_title()
        )
        task = user.get_tasks()[task_idx]
        current_label = next(k for k, v in PRIORITIES.items() if v == task.get_priority()) \
            if task.get_priority() in PRIORITIES.values() else "high"
        with st.form(f"edit_task_form_{task_idx}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_title = st.text_input("Task title", value=task.get_title())
            with col2:
                new_duration = st.number_input(
                    "Duration (minutes)", min_value=1, max_value=240,
                    value=min(max(task.get_duration(), 1), 240),
                )
            with col3:
                new_label = st.selectbox(
                    "Priority", list(PRIORITIES), index=list(PRIORITIES).index(current_label)
                )
            new_desc = st.text_input("Description", value=task.get_desc())
            all_pets = user.get_pets()
            new_pet_idxs = st.multiselect(
                "Pets for this task",
                list(range(len(all_pets))),
                default=[i for i, p in enumerate(all_pets) if any(p is q for q in task.get_pets())],
                format_func=lambda i: all_pets[i].get_name(),
            )
            save_col, delete_col = st.columns(2)
            save_task = save_col.form_submit_button("Save changes")
            delete_task = delete_col.form_submit_button("Delete task")
        if save_task:
            if new_title.strip():
                task.set_title(new_title.strip())
                task.set_duration(int(new_duration))
                task.set_priority(PRIORITIES[new_label])
                task.set_desc(new_desc.strip())
                task.set_pets([all_pets[i] for i in new_pet_idxs])
                user.set_schedules([])  # the old schedule is out of date, so regenerate
                st.rerun()
            else:
                st.warning("Task title can't be empty.")
        if delete_task:
            user.remove_task(task)
            user.set_schedules([])
            st.rerun()

st.divider()

st.subheader("Build Schedule")
col1, col2 = st.columns(2)
with col1:
    window_start = st.time_input("Start time", value=time(8, 0))
with col2:
    window_end = st.time_input("End time", value=time(20, 0))

if st.button("Generate schedule"):
    if window_end <= window_start:
        st.error("End time must be after start time.")
    elif not user.get_tasks():
        st.warning("Add at least one task first.")
    else:
        schedule = Schedule(title="Today", start_time=window_start, end_time=window_end)
        schedule.generate_schedule(user.get_tasks())
        user.set_schedules([schedule])  # keep only the latest schedule

schedules = user.get_schedules()
if schedules:
    schedule = schedules[0]
    st.success(
        f"Schedule for {schedule.get_start_time():%H:%M} to {schedule.get_end_time():%H:%M}"
    )
    st.table(
        [
            {
                "Time": f"{t.get_start_time():%H:%M} - {t.get_end_time():%H:%M}",
                "Task": t.get_title(),
                "Pets": ", ".join(p.get_name() for p in t.get_pets()),
                "Priority": t.get_priority(),
            }
            for t in schedule.get_tasks()
        ]
    )
    col1, col2 = st.columns(2)
    col1.metric("Time planned", f"{schedule.get_total_time()} min")
    col2.metric("Time left", f"{schedule.get_available_time()} min")
    for t in schedule.get_unscheduled_tasks():
        st.warning(f"Couldn't fit '{t.get_title()}' ({t.get_duration()} min) in this time window.")
