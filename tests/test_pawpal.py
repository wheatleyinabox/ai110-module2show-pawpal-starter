from datetime import time

import pytest

from pawpal_system import Pet, Schedule, Task, User


@pytest.fixture
def pets():
    return Pet(name="Max"), Pet(name="Luna")


@pytest.fixture
def user():
    return User(username="wheatley", email="w@email.com", password="pw")


def make_schedule(start=time(8, 0), end=time(20, 0)):
    return Schedule(title="Today", start_time=start, end_time=end)


# --- Task ---

def test_task_times_empty_by_default():
    task = Task(title="Walk", duration=30, priority=1)
    assert task.get_start_time() is None
    assert task.get_end_time() is None


def test_task_add_pet_ignores_duplicates(pets):
    max_dog, _ = pets
    task = Task(title="Walk")
    task.add_pet(max_dog)
    task.add_pet(max_dog)
    assert task.get_pets() == [max_dog]


def test_task_remove_pet(pets):
    max_dog, luna = pets
    task = Task(title="Play", pets=[max_dog, luna])
    task.remove_pet(max_dog)
    assert task.get_pets() == [luna]


def test_task_remove_missing_pet_is_safe(pets):
    max_dog, _ = pets
    task = Task(title="Walk")
    task.remove_pet(max_dog)
    assert task.get_pets() == []


def test_task_lists_not_shared_between_instances():
    a, b = Task(title="A"), Task(title="B")
    a.add_pet(Pet(name="Max"))
    assert b.get_pets() == []


def test_task_setters_update_getters():
    task = Task(title="Walk")
    task.set_title("Run")
    task.set_duration(45)
    task.set_priority(3)
    assert (task.get_title(), task.get_duration(), task.get_priority()) == ("Run", 45, 3)


# --- User ---

def test_user_add_and_remove_task(user):
    task = Task(title="Walk")
    user.add_task(task)
    user.add_task(task)
    assert user.get_tasks() == [task]
    user.remove_task(task)
    user.remove_task(task)
    assert user.get_tasks() == []


def test_user_add_and_remove_pet(user, pets):
    max_dog, luna = pets
    user.add_pet(max_dog)
    user.add_pet(luna)
    user.remove_pet(max_dog)
    assert user.get_pets() == [luna]


def test_user_add_and_remove_schedule(user):
    schedule = make_schedule()
    user.add_schedule(schedule)
    assert user.get_schedules() == [schedule]
    user.remove_schedule(schedule)
    assert user.get_schedules() == []


def test_user_setters_update_getters(user):
    user.set_username("new")
    user.set_email("new@email.com")
    assert (user.get_username(), user.get_email()) == ("new", "new@email.com")


# --- Schedule.generate_schedule ---

def test_tasks_scheduled_in_priority_order_back_to_back():
    low = Task(title="Low", duration=30, priority=3)
    high = Task(title="High", duration=15, priority=1)
    mid = Task(title="Mid", duration=10, priority=2)
    schedule = make_schedule()
    schedule.generate_schedule([low, high, mid])

    assert [t.get_title() for t in schedule.get_tasks()] == ["High", "Mid", "Low"]
    assert (high.get_start_time(), high.get_end_time()) == (time(8, 0), time(8, 15))
    assert (mid.get_start_time(), mid.get_end_time()) == (time(8, 15), time(8, 25))
    assert (low.get_start_time(), low.get_end_time()) == (time(8, 25), time(8, 55))


def test_scheduled_tasks_never_overlap():
    tasks = [Task(title=str(i), duration=20 + i, priority=i) for i in range(6)]
    schedule = make_schedule()
    schedule.generate_schedule(tasks)
    scheduled = schedule.get_tasks()
    for earlier, later in zip(scheduled, scheduled[1:]):
        assert earlier.get_end_time() <= later.get_start_time()


def test_task_that_does_not_fit_is_unscheduled():
    fits = Task(title="Fits", duration=30, priority=1)
    too_big = Task(title="Too big", duration=45, priority=2)
    schedule = make_schedule(end=time(8, 40))
    schedule.generate_schedule([fits, too_big])

    assert schedule.get_tasks() == [fits]
    assert schedule.get_unscheduled_tasks() == [too_big]
    assert too_big.get_start_time() is None
    assert too_big.get_end_time() is None


def test_short_task_after_a_skipped_task_still_fits():
    too_long = Task(title="Too long", duration=13 * 60, priority=1)
    short = Task(title="Short", duration=5, priority=2)
    schedule = make_schedule()
    schedule.generate_schedule([too_long, short])

    assert schedule.get_tasks() == [short]
    assert schedule.get_unscheduled_tasks() == [too_long]


def test_task_ending_exactly_at_window_end_fits():
    task = Task(title="Exact", duration=60, priority=1)
    schedule = make_schedule(end=time(9, 0))
    schedule.generate_schedule([task])
    assert schedule.get_tasks() == [task]
    assert task.get_end_time() == time(9, 0)


def test_equal_priority_keeps_entry_order():
    first = Task(title="First", duration=10, priority=1)
    second = Task(title="Second", duration=10, priority=1)
    schedule = make_schedule()
    schedule.generate_schedule([first, second])
    assert schedule.get_tasks() == [first, second]


def test_no_tasks():
    schedule = make_schedule()
    schedule.generate_schedule([])
    assert schedule.get_tasks() == []
    assert schedule.get_unscheduled_tasks() == []
    assert schedule.get_total_time() == 0
    assert schedule.get_available_time() == 720


def test_regenerating_resets_previous_results():
    a = Task(title="A", duration=30, priority=1)
    b = Task(title="B", duration=45, priority=2)
    schedule = make_schedule()
    schedule.generate_schedule([a, b])
    assert b.get_start_time() == time(8, 30)

    schedule.set_end_time(time(9, 0))
    schedule.generate_schedule([a, b])
    assert schedule.get_tasks() == [a]
    assert schedule.get_unscheduled_tasks() == [b]
    assert b.get_start_time() is None
    assert b.get_end_time() is None


def test_generate_does_not_modify_input_list_order():
    tasks = [Task(title="B", priority=2), Task(title="A", priority=1)]
    make_schedule().generate_schedule(tasks)
    assert [t.get_title() for t in tasks] == ["B", "A"]


# --- Schedule totals ---

def test_total_and_available_time():
    tasks = [Task(title="A", duration=30, priority=1), Task(title="B", duration=65, priority=2)]
    schedule = make_schedule()
    schedule.generate_schedule(tasks)
    assert schedule.get_total_time() == 95
    assert schedule.get_available_time() == 720 - 95


def test_totals_ignore_unscheduled_tasks():
    fits = Task(title="Fits", duration=30, priority=1)
    too_big = Task(title="Too big", duration=100, priority=2)
    schedule = make_schedule(end=time(9, 0))
    schedule.generate_schedule([fits, too_big])
    assert schedule.get_total_time() == 30
    assert schedule.get_available_time() == 30


def test_available_time_follows_window_changes():
    schedule = make_schedule()
    schedule.set_end_time(time(10, 0))
    assert schedule.get_available_time() == 120
