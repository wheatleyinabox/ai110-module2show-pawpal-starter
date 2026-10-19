from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time


def _to_minutes(t: time) -> int:
    return t.hour * 60 + t.minute


def _from_minutes(minutes: int) -> time:
    return time(minutes // 60, minutes % 60)


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
    # Filled in by Schedule.generate_schedule; None means unscheduled.
    start_time: time | None = None
    end_time: time | None = None

    def get_title(self) -> str:
        return self.title

    def set_title(self, title: str) -> None:
        self.title = title

    def get_desc(self) -> str:
        return self.desc

    def set_desc(self, desc: str) -> None:
        self.desc = desc

    def get_start_time(self) -> time | None:
        return self.start_time

    def get_end_time(self) -> time | None:
        return self.end_time

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
class Schedule:
    title: str
    desc: str = ""
    start_time: time = time(8, 0)
    end_time: time = time(20, 0)
    tasks: list[Task] = field(default_factory=list)
    unscheduled_tasks: list[Task] = field(default_factory=list)

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
        return sum(t.duration for t in self.tasks)

    def get_available_time(self) -> int:
        """Minutes left in the window after the scheduled tasks."""
        window = _to_minutes(self.end_time) - _to_minutes(self.start_time)
        return max(window - self.get_total_time(), 0)

    def get_tasks(self) -> list[Task]:
        return self.tasks

    def get_unscheduled_tasks(self) -> list[Task]:
        return self.unscheduled_tasks

    def generate_schedule(self, tasks: list[Task]) -> None:
        """Place tasks back to back from start_time, highest priority first.

        Higher priority numbers are scheduled first. Tasks that don't fit
        before end_time keep start/end as None and go to unscheduled_tasks.
        """
        self.tasks = []
        self.unscheduled_tasks = []
        clock = _to_minutes(self.start_time)
        limit = _to_minutes(self.end_time)

        for task in sorted(tasks, key=lambda t: t.priority, reverse=False):
            task.start_time = None
            task.end_time = None
            finish = clock + task.duration
            if finish <= limit:
                task.start_time = _from_minutes(clock)
                task.end_time = _from_minutes(finish)
                self.tasks.append(task)
                clock = finish
            else:
                self.unscheduled_tasks.append(task)


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
