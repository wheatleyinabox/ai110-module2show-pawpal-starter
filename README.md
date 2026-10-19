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

## ✨ Features

- **Owner, pets and tasks:** create, edit and delete pets and tasks (title, description, duration in minutes, priority, one or more pets).
- **Priority scheduling:** tasks are placed in priority order, and a higher priority number is scheduled first. Ties keep the order they were entered in.
- **Fixed start times:** pin a task to an exact time (like a vet appointment). Fixed tasks are placed first, then flexible tasks fill the earliest gap that fits.
- **Conflict detection:** if two fixed tasks overlap, the higher-priority one keeps its slot and the other is dropped and reported as a conflict, naming both tasks. Back-to-back tasks don't conflict.
- **Recurring tasks:** a task can repeat daily or on specific weekdays, or happen once on a date. A schedule is built for a chosen date and only plans the tasks due that day.
- **Sorting and filtering:** view tasks and schedules sorted by start time and filtered by pet.
- **Plan explanations:** every schedule can explain itself. Each placed task gets a reason (pinned time, or its priority rank and the earliest free gap), each unscheduled task says why it was left out, and `explain()` turns it into a short summary. The app shows it under "Why this plan?".
- **Time totals and unscheduled tasks:** see how many minutes are planned and left, and which tasks didn't fit the window (or fall outside it, for fixed tasks).

## ▶️ Running it

```bash
streamlit run app.py   # the interactive app
python main.py         # the CLI demo script
pytest                 # the test suite
```

## 🖥️ Sample Output

Output from the CLI demo (`python main.py`), Step 4. Tasks are placed back to back from the start of the schedule window, with the highest priority number first:

```
Step 4: Schedule - Today (08:00-20:00)
  08:00-08:30  Morning walk
  08:30-08:35  Give joint supplement
  08:35-08:50  Clean litter box
  08:50-09:35  Playtime
  Total time:     95 min
  Available time: 625 min
  Unscheduled:    0
```

Each schedule can also explain itself (`schedule.explain()`), which the demo prints after Step 4:

```
Planned 08:00-20:00: 4 task(s) scheduled (95 min, 625 min left).
Tasks pinned to a time are placed first. The rest go in priority order (highest number first), each into the earliest free gap that fits.
- 08:00-08:30 Morning walk: Priority 4 (ranked 1 of 4 flexible task(s)), so it took the earliest free time.
- 08:30-08:35 Give joint supplement: Priority 3 (ranked 2 of 4 flexible task(s)), so it took the earliest free time.
...
```

Step 8 pins a Vet checkup at 9:00 and a Grooming at 9:30. They overlap, so the higher-priority Vet keeps its slot and Grooming is reported as a conflict:

```
Step 8: Fixed times and conflicts
  08:00-08:30  Morning walk
  08:30-08:35  Give joint supplement
  08:35-08:50  Clean litter box
  09:00-10:00  Vet checkup
  10:00-10:45  Playtime
  CONFLICT: Grooming (09:30) overlaps Vet checkup
  Unscheduled: Grooming
    Why: Pinned to 09:30, but that overlaps 'Vet checkup' (09:00-10:00), which has higher priority.
```

Step 9 builds a separate schedule for each day of the current week (the dates depend on when you run it). Here Grooming repeats on Wed and Fri, and a one-time Vet appointment is on Wednesday, so they only clash on Wednesday:

```
    Wed Oct 14: 08:00 Morning walk, 08:30 Give joint supplement, 08:35 Clean litter box, 08:50 Playtime, 10:00 Vet appointment
        CONFLICT: Grooming overlaps Vet appointment
    Thu Oct 15: 08:00 Morning walk, 08:30 Give joint supplement, 08:35 Clean litter box, 08:50 Bath time, 09:30 Playtime
    Fri Oct 16: 08:00 Morning walk, 08:30 Give joint supplement, 08:35 Clean litter box, 08:50 Playtime, 10:15 Grooming
```

## 🧪 Testing PawPal+

```
# Run the full test suite:
pytest

# Pytest Output
============================= test session starts ==============================
platform darwin -- Python 3.13.0, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/Wheatley/Desktop/AI110/ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 63 items

tests/test_pawpal.py ............................................................... [100%]

============================== 63 passed in 0.03s ==============================
```

The tests in `tests/test_pawpal.py` cover:

- **Basics:** tasks, pets, users and schedules (adding, removing, setters, no shared lists).
- **Scheduling:** priority order and ties, windows that are too small, exact fits, regenerating, and no tasks.
- **Placements:** they live on the schedule, so generating never changes a task and one task can have different times in different schedules.
- **Sorting and filtering:** by start time (unscheduled last) and by pet (matched by identity, so two pets with the same details stay separate).
- **Fixed times and conflicts:** gap filling, overlap resolution by priority, back-to-back tasks, tasks outside the window, and conflicts clearing on regenerate.
- **Recurring tasks:** daily, weekly, one-time and any-day tasks, per-day schedules, and conflicts that only happen on days both tasks occur.
- **Explanations:** reasons for pinned, flexible, and unscheduled tasks (overlap, outside the window, no gap long enough), a task going around a fixed task, reasons resetting on regenerate, tasks skipped as not due, and the `explain()` summary.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Priority ordering | `Schedule.generate_schedule` | Higher priority number is placed first. Ties keep the order they were entered in. |
| Sorting by time | `Schedule.get_tasks_by_time`, `Schedule.sort_tasks_by_time` | Placements in clock order, or any list of tasks ordered by their time in a schedule (tasks not in it go last). |
| Filtering by pet | `filter_by_pet`, `User.get_tasks_for_pet`, `Schedule.get_tasks_for_pet` | Matches the exact pet object. |
| Fixed start times | `Task.fixed_start`, `Schedule.generate_schedule` | Fixed tasks are placed first, then flexible tasks take the earliest gap that fits. |
| Conflict detection | `Schedule.get_conflicts` | Returns (dropped task, task it overlaps) pairs. The higher-priority fixed task wins and the other is also listed as unscheduled. |
| Unscheduled tasks | `Schedule.get_unscheduled_tasks` | Tasks that don't fit the window, fixed tasks outside it, and conflict losers. Shorter tasks after a skipped one can still fit. |
| Recurring tasks | `Task.repeat_days`, `Task.on_date`, `Task.occurs_on`, `Task.describe_repeat`, `User.get_tasks_for_date`, `Schedule.plan_date` | Daily or chosen weekdays, or a single date. A schedule with a `plan_date` only plans tasks due that day. |
| Plan explanations | `Schedule.explain`, `Schedule.get_reason`, `ScheduledTask.get_reason`, `Schedule.get_not_due_tasks` | Reasons are written at the moment each decision is made (no extra pass, no AI needed), so the summary is cheap and always matches what the scheduler really did. |
| Time totals | `Schedule.get_total_time`, `Schedule.get_available_time` | Calculated from the scheduled tasks (in minutes) instead of stored. |
| Placements | `ScheduledTask`, `Schedule.get_placement` | Start and end times are stored on the schedule, not on the task. |

## 📸 Demo Walkthrough

**CLI demo (`python main.py`):**

1. **User:** create a `User` with a username, email and password.
2. **Pets:** add pets to the user, each with a breed, age, health conditions and medications.
3. **Tasks:** create tasks with a duration in minutes and a priority (higher number first), and link each task to one or more pets.
4. **Schedule:** create a schedule (default window 8am to 8pm) and call `generate_schedule` with the user's tasks. Each task gets a start and end time, stored on the schedule.
5. **Tight window:** shrink the window to 8am to 9am and regenerate. A task that no longer fits goes to the unscheduled list.
6. **Edge cases:** no tasks, a task longer than the whole window, and equal priorities.
7. **Sorting and filtering:** sort tasks by start time with unscheduled ones last, filter by pet, and show one task at different times in two schedules.
8. **Fixed times and conflicts:** pin two overlapping tasks, see the conflict reported, and see a fixed task outside the window left unscheduled.
9. **Recurring tasks:** set tasks to repeat daily or on chosen weekdays, add a one-time task, and build a schedule for each day of the week.

Steps 4, 5, 8 and 9 also print the scheduler's reasons for what it did.

**Streamlit app (`streamlit run app.py`):**

1. Add the owner and pets.
2. Add tasks with a duration, priority, an optional fixed start time, and how they repeat (one-time, daily, or specific days). Filter the task list by pet or sort it by scheduled time.
3. In Build Schedule, choose the date and the time window, then generate. The schedule table, time totals, and any conflict or "couldn't fit" messages appear below, followed by a "Why this plan?" section explaining each decision.
4. Use "Week at a glance" to see which tasks are due each day.

## ⚠️ Known limitations

- Data lives in memory for the session only, so it resets when the app restarts.
- The scheduler doesn't reject zero or negative durations or an end time before the start time (the app form limits duration to 1-240 minutes).
- A conflict drops the lower-priority fixed task instead of suggesting a new time for it.
- Recurring tasks have no "done" state or end date yet.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
