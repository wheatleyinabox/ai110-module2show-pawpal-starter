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

## 🖥️ Sample Output

Output from the CLI demo (`python main.py`), Step 4. Tasks are placed back to back from the start of the schedule window, in priority order (1 first):

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

## 🧪 Testing PawPal+

```
# Run the full test suite:
pytest
```

```bash
python main.py
```

It walks through creating a user, pets and tasks, generating a schedule, shrinking the window so a task no longer fits, and three edge cases (no tasks, a task longer than the whole window, and tasks with equal priority).

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Schedule.generate_schedule` | Sorted by priority, lowest number first. Ties keep the order they were entered in. |
| Filtering | `Schedule.generate_schedule`, `Schedule.get_unscheduled_tasks` | A task that would run past the end of the window is skipped and listed as unscheduled. Shorter tasks after it can still fit. |
| Conflict handling | `Schedule.generate_schedule` | Tasks are placed back to back, so time slots never overlap. |
| Time totals | `Schedule.get_total_time`, `Schedule.get_available_time` | Calculated from the scheduled tasks (in minutes) instead of stored. |
| Recurring tasks | | Not implemented. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. **User:** create a `User` with a username, email and password.
2. **Pets:** add pets to the user, each with a breed, age, health conditions and medications.
3. **Tasks:** create tasks with a duration in minutes and a priority, and link each task to one or more pets. Their start and end times stay empty until a schedule is generated.
4. **Schedule:** create a schedule (default window 8am to 8pm) and call `generate_schedule` with the user's tasks. Tasks get start and end times in priority order.
5. **Tight window:** shrink the window to 8am to 9am and regenerate. A task that no longer fits goes to the unscheduled list and its times reset to empty.
6. **Edge cases:** no tasks, a task longer than the whole window, and equal priorities.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
