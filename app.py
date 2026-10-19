import streamlit as st
from datetime import date, time

from pawpal_system import ALL_DAYS, WEEKDAY_NAMES, Pet, Schedule, Task, User, filter_by_pet

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
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
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

PRIORITIES = {"high": 3, "medium": 2, "low": 1}  # higher number is scheduled first
REPEATS = ["One-time", "Daily", "Specific days"]


def repeat_settings(choice: str, one_time_date: date, picked_days: list[int]):
    """Turn the form's repeat widgets into (repeat_days, on_date); None if days are missing."""
    if choice == "Daily":
        return list(ALL_DAYS), None
    if choice == "Specific days":
        return (picked_days, None) if picked_days else None
    return [], one_time_date

with st.form("add_task_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority_label = st.selectbox("Priority", list(PRIORITIES), index=0)
    task_desc = st.text_input("Description (optional)")
    col1, col2 = st.columns(2)
    with col1:
        has_fixed = st.checkbox("Fixed start time (e.g. a vet appointment)")
    with col2:
        fixed_value = st.time_input("Start at", value=time(9, 0))
    col1, col2, col3 = st.columns(3)
    with col1:
        repeat_choice = st.selectbox("Repeats", REPEATS)
    with col2:
        one_time_date = st.date_input("Date (one-time tasks)", value=date.today())
    with col3:
        picked_days = st.multiselect(
            "Days (specific days)", ALL_DAYS, format_func=lambda d: WEEKDAY_NAMES[d]
        )
    pet_options = list(range(len(user.get_pets())))  # indices, so duplicate names still work
    task_pet_indexes = st.multiselect(
        "Pets for this task", pet_options, format_func=lambda i: user.get_pets()[i].get_name()
    )
    if st.form_submit_button("Add task"):
        repeat = repeat_settings(repeat_choice, one_time_date, picked_days)
        if not task_title.strip():
            st.warning("Please enter a task title.")
        elif repeat is None:
            st.warning("Pick at least one day for a task that repeats on specific days.")
        else:
            task = Task(
                title=task_title.strip(),
                desc=task_desc.strip(),
                duration=int(duration),
                priority=PRIORITIES[priority_label],
                fixed_start=fixed_value if has_fixed else None,
                repeat_days=repeat[0],
                on_date=repeat[1],
            )
            for i in task_pet_indexes:
                task.add_pet(user.get_pets()[i])
            user.add_task(task)

def scheduled_label(schedule, task) -> str:
    """The task's time range in the current schedule, or a note if it isn't placed."""
    if schedule is None:
        return "not yet"
    if schedule.get_plan_date() and not task.occurs_on(schedule.get_plan_date()):
        return "not due that day"
    placement = schedule.get_placement(task)
    if placement is None:
        return "not yet"
    return f"{placement.get_start_time():%H:%M} - {placement.get_end_time():%H:%M}"


def pet_filter(key: str):
    """Selectbox for 'All pets' or one pet; returns the chosen Pet or None."""
    pets = user.get_pets()
    if not pets:
        return None
    idx = st.selectbox(
        "Filter by pet",
        [None] + list(range(len(pets))),
        format_func=lambda i: "All pets" if i is None else pets[i].get_name(),
        key=key,
    )
    return None if idx is None else pets[idx]


if user.get_tasks():
    st.write("Current tasks:")
    col1, col2 = st.columns(2)
    with col1:
        task_pet = pet_filter("task_pet_filter")
    with col2:
        task_sort = st.selectbox("Sort by", ["Order added", "Scheduled time"], key="task_sort")
    current = user.get_schedules()[0] if user.get_schedules() else None
    shown = user.get_tasks()
    if task_sort == "Scheduled time" and current:
        shown = current.sort_tasks_by_time(shown)
    if task_pet is not None:
        shown = filter_by_pet(shown, task_pet)
    if shown:
        st.table(
            [
                {
                    "Title": t.get_title(),
                    "Duration (min)": t.get_duration(),
                    "Priority": t.get_priority(),
                    "Pets": ", ".join(p.get_name() for p in t.get_pets()),
                    "Fixed start": f"{t.get_fixed_start():%H:%M}" if t.get_fixed_start() else "flexible",
                    "Repeats": t.describe_repeat(),
                    "Scheduled": scheduled_label(current, t),
                }
                for t in shown
            ]
        )
    else:
        st.info("No tasks for that pet.")
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
        if task.get_repeat_days():
            current_repeat = "Daily" if sorted(task.get_repeat_days()) == ALL_DAYS else "Specific days"
        else:
            current_repeat = "One-time"
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
            col1, col2 = st.columns(2)
            with col1:
                new_has_fixed = st.checkbox("Fixed start time", value=task.get_fixed_start() is not None)
            with col2:
                new_fixed = st.time_input("Start at", value=task.get_fixed_start() or time(9, 0))
            col1, col2, col3 = st.columns(3)
            with col1:
                new_repeat = st.selectbox("Repeats", REPEATS, index=REPEATS.index(current_repeat))
            with col2:
                new_one_time = st.date_input("Date (one-time tasks)", value=task.get_on_date() or date.today())
            with col3:
                new_days = st.multiselect(
                    "Days (specific days)", ALL_DAYS,
                    default=task.get_repeat_days() if current_repeat == "Specific days" else [],
                    format_func=lambda d: WEEKDAY_NAMES[d],
                )
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
            new_repeat_settings = repeat_settings(new_repeat, new_one_time, new_days)
            if new_repeat_settings is None:
                st.warning("Pick at least one day for a task that repeats on specific days.")
            elif new_title.strip():
                task.set_title(new_title.strip())
                task.set_repeat_days(new_repeat_settings[0])
                task.set_on_date(new_repeat_settings[1])
                task.set_duration(int(new_duration))
                task.set_priority(PRIORITIES[new_label])
                task.set_desc(new_desc.strip())
                task.set_fixed_start(new_fixed if new_has_fixed else None)
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
col1, col2, col3 = st.columns(3)
with col1:
    plan_day = st.date_input("Plan for", value=date.today())
with col2:
    window_start = st.time_input("Start time", value=time(8, 0))
with col3:
    window_end = st.time_input("End time", value=time(20, 0))

if st.button("Generate schedule"):
    if window_end <= window_start:
        st.error("End time must be after start time.")
    elif not user.get_tasks():
        st.warning("Add at least one task first.")
    else:
        schedule = Schedule(
            title=f"Plan for {plan_day:%a %b %d}",
            start_time=window_start,
            end_time=window_end,
            plan_date=plan_day,
        )
        schedule.generate_schedule(user.get_tasks())
        user.set_schedules([schedule])  # keep only the latest schedule
        st.rerun()  # the tasks table above was already drawn, so redraw it with this schedule

schedules = user.get_schedules()
if schedules:
    schedule = schedules[0]
    st.success(
        f"{schedule.get_title()}: {schedule.get_start_time():%H:%M} to {schedule.get_end_time():%H:%M}"
    )
    if not schedule.get_tasks() and not schedule.get_unscheduled_tasks():
        st.info("No tasks are due on that date.")
    sched_pet = pet_filter("schedule_pet_filter")
    sched_tasks = schedule.get_tasks_by_time()
    if sched_pet is not None:
        sched_tasks = filter_by_pet(sched_tasks, sched_pet)
    if sched_tasks:
        st.table(
            [
                {
                    "Time": f"{t.get_start_time():%H:%M} - {t.get_end_time():%H:%M}",
                    "Task": t.get_title(),
                    "Pets": ", ".join(p.get_name() for p in t.get_pets()),
                    "Priority": t.get_priority(),
                }
                for t in sched_tasks
            ]
        )
    elif sched_pet is not None:
        st.info("Nothing scheduled for that pet.")
    col1, col2 = st.columns(2)
    col1.metric("Time planned", f"{schedule.get_total_time()} min")
    col2.metric("Time left", f"{schedule.get_available_time()} min")
    clashes = dict((id(dropped), blocker) for dropped, blocker in schedule.get_conflicts())
    for t in schedule.get_unscheduled_tasks():
        if id(t) in clashes:
            blocker = schedule.get_placement(clashes[id(t)])
            st.error(
                f"Conflict: '{t.get_title()}' (fixed at {t.get_fixed_start():%H:%M}, {t.get_duration()} min) "
                f"overlaps '{blocker.get_title()}' ({blocker.get_start_time():%H:%M} - "
                f"{blocker.get_end_time():%H:%M}), which has higher priority. "
                "Change one of the times or priorities."
            )
        elif t.get_fixed_start() is not None:
            st.warning(
                f"'{t.get_title()}' is fixed at {t.get_fixed_start():%H:%M} for {t.get_duration()} min, "
                "which doesn't fit inside this time window."
            )
        else:
            st.warning(f"Couldn't fit '{t.get_title()}' ({t.get_duration()} min) in this time window.")
    with st.expander("Why this plan?", expanded=True):
        st.markdown(schedule.explain())

with st.expander("Week at a glance"):
    st.caption("Which tasks are due each day, starting from the 'Plan for' date.")
    st.table(
        [
            {
                "Day": f"{day:%a %b %d}",
                "Tasks due": ", ".join(t.get_title() for t in user.get_tasks_for_date(day)) or "none",
            }
            for day in (date.fromordinal(plan_day.toordinal() + i) for i in range(7))
        ]
    )
