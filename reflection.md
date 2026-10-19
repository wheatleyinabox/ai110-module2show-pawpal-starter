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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three things: the time window the user wants tasks scheduled in (a start and end time), how long each task takes (in minutes), and each task's priority. Priority decides the order and the time window decides what fits. I left out preferences like "meds at 9am sharp" to keep things simple, so every task is just placed in the next open spot.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler is greedy. It goes through tasks in priority order and puts each one right after the previous one, and if a task doesn't fit it gets skipped and listed as unscheduled. This won't always pack the day as tightly as possible, and a task can't be pinned to a specific time. It's reasonable here because it's easy to follow and explain, the result is a simple list, and the user can see exactly which tasks didn't fit.

---

## 3. AI Collaboration

Claude helped make everything exactly as is and suggested some changes based on the CRUD stuff I mentioned. So Claude helped add some add and remove object methods where apropriate. After reviewing it, I wanted to break up timeConstraint into two time variables instead. It did this in the attributes section, but it didn't update the methods part. When generating the skeleton and needing to review the diagram, it actually caught some mistakes I didn't see the first time. Like there still being placeholder setters and getters and the startTime and endTime setters and getters not having the appropriate parameters and return values. But at the same time, I caught that it didn't include the accessors and mutators so we're both catching each other on things.

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I checked the behavior with a guided demo script (`main.py`) instead of automated tests so far. It covers creating a user, pets and tasks, generating a schedule, a window too small for every task, and three edge cases: no tasks, a task longer than the whole window, and tasks with the same priority. These matter because they're the places where the scheduler decides what gets dropped or what order things come in.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
