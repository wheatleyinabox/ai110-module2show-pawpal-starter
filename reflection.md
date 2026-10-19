# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Users should be able to create, edit and delete tasks and pets as per CRUD design. They shuld be able to interact with the assistant to schedule a task. This can be a basic button display or a chat box with preselected actions available. They should also view their generated schedule, tasks, and pets through a dashboard where tasks and pets can be hidden or reveal as needed. They should also be able to see the schedule with daily, weekly, and monthly views.

- Briefly describe your initial UML design.
  The three big object needed are Task, Schedule, and Pet. All objects should be able to created, edited, and deleted. Attributes should be able to be edited. Many tasks should be allowed to attach to one Schedule Object. A Task should have a Title, Description, Time Duration (Maybe capping it at 4 hours), Priority (1-3) and be able to hold one or many Pet objects. A Pet object should have a Name, Breed, Age, Health Conditions, and Medications (some health stuff to keep track of as tasks are planned and scheduled). There should be a way for many Pets to be attached to a Task. Schedules should flow by a daily basis. So each Schedule object represents one day and a User can have one or many schedules. There should be a Title and Description, where these can be edited by the user. Since the assistant will be handling the scheduling, that will not be control by the user. However, a schedule can be regenerated at their request. There should be a time constraint attribute where a user can say between what times they'd like tasks to be scheduled, this becomes to the range. Based on that range: There should also be a time available attribute that has the total hours in a time constraint. A Schedule can have many tasks, as many as can fit. It should add a task to an avaiable time within the time constraint and let the user know when a task can't be schedule. Then of course, a User object where everything can be attached to and be saved in the system. A User should have a username, email, password, a list of pets, a list of tasks, and a list of schedules.

To write this out in a more structured way...
And using datetime library...

1. User
   - str : username
   - str : email
   - str : password
   - List[Task] : tasks
   - List[Pet] : pets
   - List[Schedule] : schedules
   - Accessors and mutators for attributes...
2. Task
   - str : title
   - str : desc
   - time : time duration
   - int : priority
   - List[Pet] : pets
   - Accessors and mutators for attributes...
3. Pet
   - str : name
   - str : breed
   - str : age
   - str : healthConditions
   - str : medications
   - Accessors and mutators for attributes...
4. Schedule
   - str : title
   - str : desc
   - arr[time : startTime, time : endTime] : timeConstraint
   - time : totalTime
   - time : availableTime
   - List[Task] ; tasks
   - Accessors and mutators for attributes...
   - time : calcTimeAvailable()
   - time : calcTotalTime()
   - ??? : generateSchedule()

- What classes did you include, and what responsibilities did you assign to each?
  See above and uml-draft.mmd!

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
  It also made the suggestion to use timedelta instead of the time object to make things easier for scheduling math. We ended up just using whole minutes instead. Frankly, I was lost on how I could hold the schedule in its entirety to then have the necessary information to display it. Like I had the time range but showing where tasks are placed and storing that wasn't making sense to me. It asked me what I wanted to help guide what kinds of attributes and data structures I might need. It helped me explore what building block would be needed for a Google Calendar type system but it felt too complex for the project so we reworked the diagram and skeleton to simplify the Schedule object class. At this stage the idea is to create a sorted list of tasks by priority and then given a time frame the user wants to use, to add tasks into the schedule. I also added start and end time attributes to Task just so they exists even if they're empty when a task is created by a User.

**Update (later iterations):** The design kept changing as features were added.

- Start and end times moved off `Task`. Storing them on the task meant a second schedule overwrote the first one's times, and a recurring task would only have had one time for every day. Now `generate_schedule` stores each placement in a `ScheduledTask` (task + start + end) on the schedule and never modifies the task.
- `Task` gained `fixed_start` (pin it to a time), `repeat_days` and `on_date` (recurrence). `Schedule` gained `plan_date` (the day it is for) and `conflicts`.
- Priority now means a higher number is scheduled first. The docstring already said that, but the code sorted the other way, so I fixed the code and flipped the priority numbers in the app, demo script and tests.
- The UML in `diagrams/uml-draft.mmd` still shows the original design and hasn't been updated to match yet.
- Schedules can now explain themselves. I wasn't sure there was an efficient way to do that, but the scheduler already knows why it makes each choice at the moment it makes it, so it writes a short reason down then (on each `ScheduledTask`, and for each unscheduled task) and `Schedule.explain()` strings them into a summary. That costs nothing extra and the explanation can't drift from what the scheduler actually did.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three things: the time window the user wants tasks scheduled in (a start and end time), how long each task takes (in minutes), and each task's priority. Priority decides the order and the time window decides what fits. I left out preferences like "meds at 9am sharp" to keep things simple, so every task is just placed in the next open spot.

**Update:** That changed. Tasks can now have a fixed start time (like a vet appointment at 9:00) and a date or repeating weekdays (daily, or specific days like Mon and Thu). So the scheduler now considers the day the schedule is for, fixed times, priority, and the time window. Owner preferences beyond a fixed time are still left out.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler is greedy. It goes through tasks in priority order and puts each one right after the previous one, and if a task doesn't fit it gets skipped and listed as unscheduled. This won't always pack the day as tightly as possible, and a task can't be pinned to a specific time. It's reasonable here because it's easy to follow and explain, the result is a simple list, and the user can see exactly which tasks didn't fit.

**Update:** It's still greedy, with a few more rules. Fixed-time tasks are placed first (highest priority first), then flexible tasks fill the earliest gap that fits. If two fixed tasks overlap, the higher-priority one keeps the slot and the other one is dropped and reported as a conflict, instead of being shifted or letting both overlap. I chose that because silently moving an appointment seemed worse than telling the owner to fix it. Two smaller tradeoffs: a task with no date and no repeat counts as "any day" so older tasks keep working (the UI defaults new tasks to one-time on today's date), and tasks that aren't due on the schedule's date are skipped instead of being listed as unscheduled, since they were never meant to happen that day.

---

## 3. AI Collaboration

Claude helped make everything exactly as is and suggested some changes based on the CRUD stuff I mentioned. So Claude helped add some add and remove object methods where apropriate. After reviewing it, I wanted to break up timeConstraint into two time variables instead. It did this in the attributes section, but it didn't update the methods part. When generating the skeleton and needing to review the diagram, it actually caught some mistakes I didn't see the first time. Like there still being placeholder setters and getters and the startTime and endTime setters and getters not having the appropriate parameters and return values. But at the same time, I caught that it didn't include the accessors and mutators so we're both catching each other on things.

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

Later in the project I had Claude read `main.py` and `pawpal_system.py` and suggest small algorithm improvements (sorting by time, filtering by pet, conflict detection, recurring tasks, and some fixes). I picked which ones to do and in what order, then we built them one at a time with tests added alongside each one. The prompts that worked best were specific and tied to the code ("based on this file, suggest...") and ones that set an order ("bug first, then filtering, then sorting"). At the end I also asked it to review `main.py` and `app.py` to make sure everything in the system was shown in the demo script and in the UI.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

A few times I pushed back on what came back. Filtering and sorting were first only added to the backend, so I asked about the terminal and Streamlit side and they were wired into `main.py` and `app.py`. When I asked whether sorting by time was visible in the UI, it turned out the schedule table was already in clock order, so the sort didn't visibly change anything until tasks can be pinned to a time. I also noticed there was no way to enter a start time in the UI, which meant conflict detection had nothing to detect, so fixed start times came first. And I caught a bug where tasks still said "not yet" after generating a schedule until I clicked again. It was a Streamlit rerun-order problem (the tasks table is drawn above the button that creates the schedule) and it was fixed with a `st.rerun()`. To verify, I tested the app by hand, and after each change Claude ran the pytest suite, ran `main.py`, and ran the Streamlit page headlessly with Streamlit's AppTest.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I checked the behavior with a guided demo script (`main.py`) instead of automated tests so far. It covers creating a user, pets and tasks, generating a schedule, a window too small for every task, and three edge cases: no tasks, a task longer than the whole window, and tasks with the same priority. These matter because they're the places where the scheduler decides what gets dropped or what order things come in.

**Update:** There are now automated tests too: 63 pytest tests in `tests/test_pawpal.py`. They cover tasks, users and schedules; priority order (higher number first) and ties; windows that are too small and exact fits; placements staying on the schedule without changing the tasks; the same task in two schedules; sorting by time and filtering by pet; fixed-time tasks, gap filling and conflicts (including back-to-back tasks not conflicting and tasks outside the window); and recurring tasks (daily, weekly, one-time, any-day, per-day schedules, and conflicts only on days both tasks occur). The demo script gained steps 7 to 9 for sorting and filtering, fixed times and conflicts, and recurring tasks, and I tested the Streamlit UI by hand. The explanations are tested too (reasons for each kind of placement and each kind of unscheduled task, reasons resetting when a schedule is regenerated, and the summary text).

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

For the general demo script, I didn't end up testing for 0 or negative values in duration or if tasks get a priority of 0. These would be good safeguards to test with more time!

**Update:** I'm more confident now that there are tests and the demo script and UI show the same behavior. The Streamlit form limits duration to 1-240 minutes, but the scheduler itself still doesn't reject zero or negative durations or an end time before the start time, so that is still untested. Other things I'd test next: tasks that cross midnight, very long fixed tasks, recurring tasks that stop after a certain date, and automated tests for the Streamlit page (I only checked it by hand and with throwaway headless runs).

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

Moving placements onto the schedule, then building fixed times, conflict detection and recurring tasks on top of it. Each feature was small, got tests, and showed up in both `main.py` and the app.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

Aadd validation (zero or negative durations, end before start), warn about conflicts as soon as a task is added instead of only after generating, add a way to mark recurring tasks as done, save data between sessions (everything lives in memory right now), and let the scheduler suggest a new time instead of just dropping a conflicting task.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

A feature isn't finished until it works in the demo script and the UI, not just in the backend. Order matters too: fixed times had to come before conflict detection, and moving placements off the task had to come before recurring tasks.
