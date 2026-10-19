from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time


WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]  # index matches date.weekday()
ALL_DAYS = list(range(7))


def _to_minutes(t: time) -> int:
    return t.hour * 60 + t.minute


def _from_minutes(minutes: int) -> time:
    return time(minutes // 60, minutes % 60)


def filter_by_pet(tasks: list, pet: Pet) -> list:
    """Return the tasks (or scheduled tasks) that involve the given pet."""
    return [t for t in tasks if any(pet is p for p in t.pets)]


@dataclass
class Pet:
    name: str
    breed: str = ""
    age: str = ""
    health_conditions: str = ""
    medications: str = ""

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name

    def get_breed(self) -> str:
        return self.breed

    def set_breed(self, breed: str) -> None:
        self.breed = breed

    def get_age(self) -> str:
        return self.age

    def set_age(self, age: str) -> None:
        self.age = age

    def get_health_conditions(self) -> str:
        return self.health_conditions

    def set_health_conditions(self, health_conditions: str) -> None:
        self.health_conditions = health_conditions

    def get_medications(self) -> str:
        return self.medications

    def set_medications(self, medications: str) -> None:
        self.medications = medications


@dataclass
class Task:
    title: str
    desc: str = ""
    duration: int = 0  # minutes
    priority: int = 0
    pets: list[Pet] = field(default_factory=list)
    # When set, the task must start at exactly this time (e.g. a vet appointment).
    fixed_start: time | None = None
    # Weekdays the task repeats on (0=Mon .. 6=Sun); empty means it doesn't repeat.
    repeat_days: list[int] = field(default_factory=list)
    # For a one-time task: the only date it happens on. Ignored if repeat_days is set.
    # A task with neither is treated as due on any day.
    on_date: date | None = None

    def get_title(self) -> str:
        return self.title

    def set_title(self, title: str) -> None:
        self.title = title

    def get_desc(self) -> str:
        return self.desc

    def set_desc(self, desc: str) -> None:
        self.desc = desc

    def get_fixed_start(self) -> time | None:
        return self.fixed_start

    def set_fixed_start(self, fixed_start: time | None) -> None:
        self.fixed_start = fixed_start

    def get_repeat_days(self) -> list[int]:
        return self.repeat_days

    def set_repeat_days(self, repeat_days: list[int]) -> None:
        self.repeat_days = sorted(set(repeat_days))

    def get_on_date(self) -> date | None:
        return self.on_date

    def set_on_date(self, on_date: date | None) -> None:
        self.on_date = on_date

    def is_recurring(self) -> bool:
        return bool(self.repeat_days)

    def occurs_on(self, day: date) -> bool:
        """Whether this task is due on the given date."""
        if self.repeat_days:
            return day.weekday() in self.repeat_days
        if self.on_date is not None:
            return day == self.on_date
        return True

    def describe_repeat(self) -> str:
        """Short label such as 'Daily', 'Mon, Wed', 'Once on 2026-10-20' or 'Any day'."""
        if self.repeat_days:
            if sorted(set(self.repeat_days)) == ALL_DAYS:
                return "Daily"
            return ", ".join(WEEKDAY_NAMES[d] for d in sorted(set(self.repeat_days)))
        if self.on_date is not None:
            return f"Once on {self.on_date:%Y-%m-%d}"
        return "Any day"

    def get_duration(self) -> int:
        return self.duration

    def set_duration(self, duration: int) -> None:
        self.duration = duration

    def get_priority(self) -> int:
        return self.priority

    def set_priority(self, priority: int) -> None:
        self.priority = priority

    def get_pets(self) -> list[Pet]:
        return self.pets

    def set_pets(self, pets: list[Pet]) -> None:
        self.pets = pets

    def add_pet(self, pet: Pet) -> None:
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        if pet in self.pets:
            self.pets.remove(pet)


@dataclass
class ScheduledTask:
    """A task placed at a specific time in one Schedule.

    Placements live here, not on Task, so one Task can appear in several
    schedules (or on several days) without the placements overwriting each other.
    """
    task: Task
    start_time: time
    end_time: time

    def get_task(self) -> Task:
        return self.task

    def get_start_time(self) -> time:
        return self.start_time

    def get_end_time(self) -> time:
        return self.end_time

    # Read-only views of the underlying task, so callers can treat both alike.
    @property
    def title(self) -> str:
        return self.task.title

    @property
    def duration(self) -> int:
        return self.task.duration

    @property
    def priority(self) -> int:
        return self.task.priority

    @property
    def pets(self) -> list[Pet]:
        return self.task.pets

    def get_title(self) -> str:
        return self.task.title

    def get_desc(self) -> str:
        return self.task.desc

    def get_duration(self) -> int:
        return self.task.duration

    def get_priority(self) -> int:
        return self.task.priority

    def get_pets(self) -> list[Pet]:
        return self.task.pets


@dataclass
class Schedule:
    title: str
    desc: str = ""
    start_time: time = time(8, 0)
    end_time: time = time(20, 0)
    tasks: list[ScheduledTask] = field(default_factory=list)
    unscheduled_tasks: list[Task] = field(default_factory=list)
    # (task that was dropped, task it overlaps with) for fixed-time clashes.
    conflicts: list[tuple[Task, Task]] = field(default_factory=list)
    # The day this schedule is for. None means "plan every task I'm given".
    plan_date: date | None = None

    def get_title(self) -> str:
        return self.title

    def set_title(self, title: str) -> None:
        self.title = title

    def get_desc(self) -> str:
        return self.desc

    def set_desc(self, desc: str) -> None:
        self.desc = desc

    def get_start_time(self) -> time:
        return self.start_time

    def set_start_time(self, start_time: time) -> None:
        self.start_time = start_time

    def get_end_time(self) -> time:
        return self.end_time

    def set_end_time(self, end_time: time) -> None:
        self.end_time = end_time

    def get_total_time(self) -> int:
        """Total minutes taken by the scheduled tasks."""
        return sum(p.duration for p in self.tasks)

    def get_available_time(self) -> int:
        """Minutes left in the window after the scheduled tasks."""
        window = _to_minutes(self.end_time) - _to_minutes(self.start_time)
        return max(window - self.get_total_time(), 0)

    def get_tasks(self) -> list[ScheduledTask]:
        return self.tasks

    def get_unscheduled_tasks(self) -> list[Task]:
        return self.unscheduled_tasks

    def get_plan_date(self) -> date | None:
        return self.plan_date

    def set_plan_date(self, plan_date: date | None) -> None:
        self.plan_date = plan_date

    def get_conflicts(self) -> list[tuple[Task, Task]]:
        """Pairs of (dropped task, task it overlaps) from the last generate_schedule."""
        return self.conflicts

    def get_tasks_by_time(self) -> list[ScheduledTask]:
        """Placed tasks in clock order."""
        return sorted(self.tasks, key=lambda p: p.start_time)

    def get_tasks_for_pet(self, pet: Pet) -> list[ScheduledTask]:
        """Placed tasks that involve the given pet, in clock order."""
        return filter_by_pet(self.get_tasks_by_time(), pet)

    def get_placement(self, task: Task) -> ScheduledTask | None:
        """Where this task sits in this schedule, or None if it isn't placed."""
        return next((p for p in self.tasks if p.task is task), None)

    def sort_tasks_by_time(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by their time in this schedule; tasks not placed here go last."""
        def key(task: Task):
            placement = self.get_placement(task)
            return (placement is None, placement.start_time if placement else time.min)
        return sorted(tasks, key=key)

    def generate_schedule(self, tasks: list[Task]) -> None:
        """Place fixed-time tasks first, then fill the gaps with the rest by priority.

        If plan_date is set, only tasks due that day are considered; the others
        are neither scheduled nor reported as unscheduled.

        Higher priority numbers are placed first. A fixed-time task keeps its
        requested start; if it overlaps one already placed (the higher-priority
        one wins) or falls outside the window, it goes to unscheduled_tasks,
        and overlaps are recorded in conflicts. Flexible tasks take the earliest
        gap that fits, or go to unscheduled_tasks. The input tasks are never
        modified; placements are stored on this schedule.
        """
        self.tasks = []
        self.unscheduled_tasks = []
        self.conflicts = []
        window_start = _to_minutes(self.start_time)
        limit = _to_minutes(self.end_time)
        due = [t for t in tasks if self.plan_date is None or t.occurs_on(self.plan_date)]
        by_priority = sorted(due, key=lambda t: t.priority, reverse=True)
        busy: list[tuple[int, int, Task]] = []  # (start, end, task), kept sorted by start

        def place(task: Task, start: int) -> None:
            end = start + task.duration
            self.tasks.append(ScheduledTask(task, _from_minutes(start), _from_minutes(end)))
            busy.append((start, end, task))
            busy.sort(key=lambda b: b[0])

        for task in (t for t in by_priority if t.fixed_start is not None):
            start = _to_minutes(task.fixed_start)
            end = start + task.duration
            if start < window_start or end > limit:
                self.unscheduled_tasks.append(task)
                continue
            clash = next((b for b in busy if start < b[1] and b[0] < end), None)
            if clash:
                self.unscheduled_tasks.append(task)
                self.conflicts.append((task, clash[2]))
            else:
                place(task, start)

        for task in (t for t in by_priority if t.fixed_start is None):
            cursor = window_start
            for b_start, b_end, _ in busy:
                if cursor + task.duration <= b_start:
                    break
                cursor = max(cursor, b_end)
            if cursor + task.duration <= limit:
                place(task, cursor)
            else:
                self.unscheduled_tasks.append(task)

        self.tasks.sort(key=lambda p: p.start_time)


@dataclass
class User:
    username: str
    email: str
    password: str
    tasks: list[Task] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)
    schedules: list[Schedule] = field(default_factory=list)

    def get_username(self) -> str:
        return self.username

    def set_username(self, username: str) -> None:
        self.username = username

    def get_email(self) -> str:
        return self.email

    def set_email(self, email: str) -> None:
        self.email = email

    def get_password(self) -> str:
        return self.password

    def set_password(self, password: str) -> None:
        self.password = password

    def get_tasks(self) -> list[Task]:
        return self.tasks

    def set_tasks(self, tasks: list[Task]) -> None:
        self.tasks = tasks

    def get_tasks_for_date(self, day: date) -> list[Task]:
        """All tasks that are due on the given date."""
        return [t for t in self.tasks if t.occurs_on(day)]

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        """All tasks that involve the given pet."""
        return filter_by_pet(self.tasks, pet)

    def get_pets(self) -> list[Pet]:
        return self.pets

    def set_pets(self, pets: list[Pet]) -> None:
        self.pets = pets

    def get_schedules(self) -> list[Schedule]:
        return self.schedules

    def set_schedules(self, schedules: list[Schedule]) -> None:
        self.schedules = schedules

    def add_task(self, task: Task) -> None:
        if task not in self.tasks:
            self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        if task in self.tasks:
            self.tasks.remove(task)

    def add_pet(self, pet: Pet) -> None:
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        if pet in self.pets:
            self.pets.remove(pet)

    def add_schedule(self, schedule: Schedule) -> None:
        if schedule not in self.schedules:
            self.schedules.append(schedule)

    def remove_schedule(self, schedule: Schedule) -> None:
        if schedule in self.schedules:
            self.schedules.remove(schedule)
