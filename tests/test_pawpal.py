from datetime import date, time

import pytest

from pawpal_system import ALL_DAYS, Pet, Schedule, ScheduledTask, Task, User, filter_by_pet


@pytest.fixture
def pets():
    return Pet(name="Max"), Pet(name="Luna")


@pytest.fixture
def user():
    return User(username="wheatley", email="w@email.com", password="pw")


def make_schedule(start=time(8, 0), end=time(20, 0)):
    return Schedule(title="Today", start_time=start, end_time=end)


def placed(schedule):
    """The Task objects in a schedule, in placement order."""
    return [p.task for p in schedule.get_tasks()]


def times(schedule, task):
    """(start, end) of a task in a schedule."""
    p = schedule.get_placement(task)
    return (p.get_start_time(), p.get_end_time())


# --- Task ---

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
    low = Task(title="Low", duration=30, priority=1)
    high = Task(title="High", duration=15, priority=3)
    mid = Task(title="Mid", duration=10, priority=2)
    schedule = make_schedule()
    schedule.generate_schedule([low, high, mid])

    assert [t.get_title() for t in schedule.get_tasks()] == ["High", "Mid", "Low"]
    assert times(schedule, high) == (time(8, 0), time(8, 15))
    assert times(schedule, mid) == (time(8, 15), time(8, 25))
    assert times(schedule, low) == (time(8, 25), time(8, 55))


def test_scheduled_tasks_never_overlap():
    tasks = [Task(title=str(i), duration=20 + i, priority=i) for i in range(6)]
    schedule = make_schedule()
    schedule.generate_schedule(tasks)
    scheduled = schedule.get_tasks()
    for earlier, later in zip(scheduled, scheduled[1:]):
        assert earlier.get_end_time() <= later.get_start_time()


def test_task_that_does_not_fit_is_unscheduled():
    fits = Task(title="Fits", duration=30, priority=2)
    too_big = Task(title="Too big", duration=45, priority=1)
    schedule = make_schedule(end=time(8, 40))
    schedule.generate_schedule([fits, too_big])

    assert placed(schedule) == [fits]
    assert schedule.get_unscheduled_tasks() == [too_big]
    assert schedule.get_placement(too_big) is None


def test_short_task_after_a_skipped_task_still_fits():
    too_long = Task(title="Too long", duration=13 * 60, priority=2)
    short = Task(title="Short", duration=5, priority=1)
    schedule = make_schedule()
    schedule.generate_schedule([too_long, short])

    assert placed(schedule) == [short]
    assert schedule.get_unscheduled_tasks() == [too_long]


def test_task_ending_exactly_at_window_end_fits():
    task = Task(title="Exact", duration=60, priority=1)
    schedule = make_schedule(end=time(9, 0))
    schedule.generate_schedule([task])
    assert placed(schedule) == [task]
    assert times(schedule, task)[1] == time(9, 0)


def test_equal_priority_keeps_entry_order():
    first = Task(title="First", duration=10, priority=1)
    second = Task(title="Second", duration=10, priority=1)
    schedule = make_schedule()
    schedule.generate_schedule([first, second])
    assert placed(schedule) == [first, second]


def test_no_tasks():
    schedule = make_schedule()
    schedule.generate_schedule([])
    assert schedule.get_tasks() == []
    assert schedule.get_unscheduled_tasks() == []
    assert schedule.get_total_time() == 0
    assert schedule.get_available_time() == 720


def test_regenerating_resets_previous_results():
    a = Task(title="A", duration=30, priority=2)
    b = Task(title="B", duration=45, priority=1)
    schedule = make_schedule()
    schedule.generate_schedule([a, b])
    assert times(schedule, b)[0] == time(8, 30)

    schedule.set_end_time(time(9, 0))
    schedule.generate_schedule([a, b])
    assert placed(schedule) == [a]
    assert schedule.get_unscheduled_tasks() == [b]
    assert schedule.get_placement(b) is None


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


# --- Placements live on the schedule, not the task ---

def test_generate_does_not_modify_tasks():
    task = Task(title="Walk", duration=30, priority=1)
    before = (task.title, task.duration, task.priority, list(task.pets))
    make_schedule().generate_schedule([task])
    assert (task.title, task.duration, task.priority, list(task.pets)) == before
    assert not hasattr(task, "start_time")


def test_same_task_in_two_schedules_keeps_separate_times():
    walk = Task(title="Walk", duration=30, priority=1)
    morning = make_schedule(start=time(8, 0))
    evening = make_schedule(start=time(18, 0))
    morning.generate_schedule([walk])
    evening.generate_schedule([walk])
    assert times(morning, walk) == (time(8, 0), time(8, 30))
    assert times(evening, walk) == (time(18, 0), time(18, 30))


def test_scheduled_task_exposes_task_details(pets):
    max_dog, _ = pets
    walk = Task(title="Walk", desc="Park", duration=30, priority=2, pets=[max_dog])
    schedule = make_schedule()
    schedule.generate_schedule([walk])
    p = schedule.get_tasks()[0]
    assert isinstance(p, ScheduledTask)
    assert p.get_task() is walk
    assert (p.get_title(), p.get_desc(), p.get_duration(), p.get_priority()) == ("Walk", "Park", 30, 2)
    assert p.get_pets() == [max_dog]


def test_get_placement_uses_identity_not_equality():
    a, b = Task(title="Same", duration=10), Task(title="Same", duration=10)
    schedule = make_schedule()
    schedule.generate_schedule([a])
    assert schedule.get_placement(a) is not None
    assert schedule.get_placement(b) is None


# --- Sorting and filtering ---

def test_schedule_get_tasks_by_time_is_chronological():
    tasks = [Task(title=str(i), duration=10, priority=i) for i in range(4)]
    schedule = make_schedule()
    schedule.generate_schedule(tasks)
    schedule.tasks.reverse()  # scramble stored order
    starts = [p.get_start_time() for p in schedule.get_tasks_by_time()]
    assert starts == sorted(starts)


def test_sort_tasks_by_time_puts_unplaced_last():
    a = Task(title="A", duration=10, priority=1)
    b = Task(title="B", duration=10, priority=2)
    c = Task(title="C", duration=10, priority=3)
    schedule = make_schedule(end=time(8, 20))
    schedule.generate_schedule([a, b])  # c is not in this schedule
    assert schedule.sort_tasks_by_time([a, c, b]) == [b, a, c]


def test_sort_tasks_by_time_does_not_modify_input():
    a, b = Task(title="A", priority=1), Task(title="B", priority=2)
    schedule = make_schedule()
    schedule.generate_schedule([a, b])
    tasks = [a, b]
    schedule.sort_tasks_by_time(tasks)
    assert tasks == [a, b]


def test_user_get_tasks_for_pet(user, pets):
    max_dog, luna = pets
    walk = Task(title="Walk", pets=[max_dog])
    litter = Task(title="Litter", pets=[luna])
    play = Task(title="Play", pets=[max_dog, luna])
    nobody = Task(title="Nobody")
    for t in (walk, litter, play, nobody):
        user.add_task(t)
    assert user.get_tasks_for_pet(max_dog) == [walk, play]
    assert user.get_tasks_for_pet(luna) == [litter, play]


def test_filter_by_pet_with_no_matches(pets):
    max_dog, luna = pets
    assert filter_by_pet([Task(title="Walk", pets=[max_dog])], luna) == []


def test_filter_by_pet_distinguishes_identical_pets():
    twin_a, twin_b = Pet(name="Rex"), Pet(name="Rex")
    walk = Task(title="Walk", pets=[twin_a])
    assert filter_by_pet([walk], twin_a) == [walk]
    assert filter_by_pet([walk], twin_b) == []


def test_schedule_get_tasks_for_pet_excludes_unscheduled(pets):
    max_dog, luna = pets
    fits = Task(title="Fits", duration=10, priority=2, pets=[max_dog])
    too_big = Task(title="Too big", duration=500, priority=1, pets=[max_dog])
    other = Task(title="Other", duration=10, priority=3, pets=[luna])
    schedule = make_schedule(end=time(9, 0))
    schedule.generate_schedule([fits, too_big, other])
    assert [p.task for p in schedule.get_tasks_for_pet(max_dog)] == [fits]


# --- Fixed-time tasks and conflicts ---

def test_fixed_task_keeps_its_start_time():
    vet = Task(title="Vet", duration=30, priority=1, fixed_start=time(10, 0))
    schedule = make_schedule()
    schedule.generate_schedule([vet])
    assert times(schedule, vet) == (time(10, 0), time(10, 30))


def test_flexible_tasks_fill_gap_before_fixed_task():
    vet = Task(title="Vet", duration=30, priority=1, fixed_start=time(9, 0))
    walk = Task(title="Walk", duration=30, priority=3)
    feed = Task(title="Feed", duration=10, priority=2)
    schedule = make_schedule()
    schedule.generate_schedule([vet, walk, feed])
    assert times(schedule, walk) == (time(8, 0), time(8, 30))
    assert times(schedule, feed) == (time(8, 30), time(8, 40))
    assert times(schedule, vet) == (time(9, 0), time(9, 30))


def test_flexible_task_that_does_not_fit_gap_goes_after_fixed_task():
    vet = Task(title="Vet", duration=30, priority=1, fixed_start=time(8, 30))
    walk = Task(title="Walk", duration=45, priority=3)
    schedule = make_schedule()
    schedule.generate_schedule([vet, walk])
    assert times(schedule, walk) == (time(9, 0), time(9, 45))


def test_tasks_returned_in_clock_order_with_fixed_tasks():
    vet = Task(title="Vet", duration=30, priority=1, fixed_start=time(12, 0))
    walk = Task(title="Walk", duration=30, priority=3)
    schedule = make_schedule()
    schedule.generate_schedule([vet, walk])
    assert [t.get_title() for t in schedule.get_tasks()] == ["Walk", "Vet"]


def test_overlapping_fixed_tasks_are_a_conflict_higher_priority_wins():
    groom = Task(title="Groom", duration=60, priority=1, fixed_start=time(9, 0))
    vet = Task(title="Vet", duration=30, priority=3, fixed_start=time(9, 30))
    schedule = make_schedule()
    schedule.generate_schedule([groom, vet])
    assert placed(schedule) == [vet]
    assert schedule.get_unscheduled_tasks() == [groom]
    assert schedule.get_conflicts() == [(groom, vet)]


def test_back_to_back_fixed_tasks_do_not_conflict():
    a = Task(title="A", duration=30, priority=1, fixed_start=time(9, 0))
    b = Task(title="B", duration=30, priority=1, fixed_start=time(9, 30))
    schedule = make_schedule()
    schedule.generate_schedule([a, b])
    assert placed(schedule) == [a, b]
    assert schedule.get_conflicts() == []


def test_fixed_task_outside_window_is_unscheduled_without_conflict():
    early = Task(title="Early", duration=30, fixed_start=time(7, 30))
    late = Task(title="Late", duration=30, fixed_start=time(19, 45))
    schedule = make_schedule()
    schedule.generate_schedule([early, late])
    assert schedule.get_tasks() == []
    assert schedule.get_unscheduled_tasks() == [early, late]
    assert schedule.get_conflicts() == []


def test_regenerating_clears_old_conflicts():
    a = Task(title="A", duration=60, priority=2, fixed_start=time(9, 0))
    b = Task(title="B", duration=60, priority=1, fixed_start=time(9, 30))
    schedule = make_schedule()
    schedule.generate_schedule([a, b])
    assert len(schedule.get_conflicts()) == 1
    b.set_fixed_start(time(11, 0))
    schedule.generate_schedule([a, b])
    assert schedule.get_conflicts() == []
    assert placed(schedule) == [a, b]


def test_no_overlaps_with_mixed_fixed_and_flexible_tasks():
    tasks = [Task(title=f"F{i}", duration=25, priority=i, fixed_start=time(8 + i, 10)) for i in range(4)]
    tasks += [Task(title=f"X{i}", duration=20 + i, priority=i) for i in range(6)]
    schedule = make_schedule()
    schedule.generate_schedule(tasks)
    scheduled = schedule.get_tasks()
    for earlier, later in zip(scheduled, scheduled[1:]):
        assert earlier.get_end_time() <= later.get_start_time()


# --- Recurring tasks ---

MON, TUE, WED, THU, FRI, SAT, SUN = (date(2024, 1, d) for d in range(1, 8))  # 2024-01-01 is a Monday


def test_daily_task_occurs_every_day():
    feed = Task(title="Feed", repeat_days=ALL_DAYS)
    assert all(feed.occurs_on(d) for d in (MON, TUE, WED, THU, FRI, SAT, SUN))
    assert feed.is_recurring()
    assert feed.describe_repeat() == "Daily"


def test_weekly_task_occurs_only_on_chosen_weekdays():
    bath = Task(title="Bath", repeat_days=[0, 3])
    assert bath.occurs_on(MON) and bath.occurs_on(THU)
    assert not bath.occurs_on(TUE) and not bath.occurs_on(SUN)
    assert bath.occurs_on(date(2024, 1, 8))  # the following Monday
    assert bath.describe_repeat() == "Mon, Thu"


def test_set_repeat_days_sorts_and_dedupes():
    task = Task(title="Walk")
    task.set_repeat_days([4, 0, 4, 2])
    assert task.get_repeat_days() == [0, 2, 4]


def test_one_time_task_occurs_only_on_its_date():
    vet = Task(title="Vet", on_date=WED)
    assert vet.occurs_on(WED)
    assert not vet.occurs_on(THU)
    assert not vet.is_recurring()
    assert vet.describe_repeat() == "Once on 2024-01-03"


def test_task_with_no_date_or_repeat_is_due_any_day():
    task = Task(title="Anytime")
    assert task.occurs_on(MON) and task.occurs_on(SAT)
    assert task.describe_repeat() == "Any day"


def test_repeat_days_take_priority_over_on_date():
    task = Task(title="Odd", repeat_days=[0], on_date=WED)
    assert task.occurs_on(MON)
    assert not task.occurs_on(WED)


def test_user_get_tasks_for_date(user):
    daily = Task(title="Feed", repeat_days=ALL_DAYS)
    mwf = Task(title="Walk", repeat_days=[0, 2, 4])
    vet = Task(title="Vet", on_date=WED)
    for t in (daily, mwf, vet):
        user.add_task(t)
    assert user.get_tasks_for_date(MON) == [daily, mwf]
    assert user.get_tasks_for_date(TUE) == [daily]
    assert user.get_tasks_for_date(WED) == [daily, mwf, vet]


def test_schedule_with_plan_date_only_plans_tasks_due_that_day():
    daily = Task(title="Feed", duration=10, priority=1, repeat_days=ALL_DAYS)
    tue_only = Task(title="Bath", duration=20, priority=2, repeat_days=[1])
    schedule = make_schedule()
    schedule.set_plan_date(MON)
    schedule.generate_schedule([daily, tue_only])
    assert placed(schedule) == [daily]
    assert schedule.get_unscheduled_tasks() == []  # not due is not the same as unscheduled

    schedule.set_plan_date(TUE)
    schedule.generate_schedule([daily, tue_only])
    assert placed(schedule) == [tue_only, daily]


def test_schedule_without_plan_date_plans_everything():
    a = Task(title="A", duration=10, repeat_days=[1])
    b = Task(title="B", duration=10, on_date=WED)
    schedule = make_schedule()
    schedule.generate_schedule([a, b])
    assert placed(schedule) == [a, b]


def test_recurring_task_gets_separate_placements_each_day():
    walk = Task(title="Walk", duration=30, priority=1, repeat_days=ALL_DAYS)
    monday = Schedule(title="Mon", plan_date=MON)
    tuesday = Schedule(title="Tue", plan_date=TUE, start_time=time(9, 0))
    monday.generate_schedule([walk])
    tuesday.generate_schedule([walk])
    assert times(monday, walk) == (time(8, 0), time(8, 30))
    assert times(tuesday, walk) == (time(9, 0), time(9, 30))


def test_recurring_fixed_task_conflicts_only_on_days_both_occur():
    groom = Task(title="Groom", duration=60, priority=1, fixed_start=time(9, 0), repeat_days=[0])
    vet = Task(title="Vet", duration=30, priority=2, fixed_start=time(9, 30), repeat_days=[0, 1])
    monday = Schedule(title="Mon", plan_date=MON)
    tuesday = Schedule(title="Tue", plan_date=TUE)
    monday.generate_schedule([groom, vet])
    tuesday.generate_schedule([groom, vet])
    assert monday.get_conflicts() == [(groom, vet)]
    assert tuesday.get_conflicts() == []
    assert placed(tuesday) == [vet]


# --- Explaining the schedule ---

def test_flexible_task_reason_mentions_priority_and_rank():
    walk = Task(title="Walk", duration=30, priority=3)
    feed = Task(title="Feed", duration=10, priority=1)
    schedule = make_schedule()
    schedule.generate_schedule([feed, walk])
    assert "Priority 3" in schedule.get_reason(walk)
    assert "ranked 1 of 2" in schedule.get_reason(walk)
    assert "ranked 2 of 2" in schedule.get_reason(feed)


def test_fixed_task_reason_says_it_was_pinned():
    vet = Task(title="Vet", duration=30, fixed_start=time(9, 0))
    schedule = make_schedule()
    schedule.generate_schedule([vet])
    assert "Pinned to 09:00" in schedule.get_reason(vet)
    assert schedule.get_tasks()[0].get_reason() == schedule.get_reason(vet)


def test_reason_says_when_a_task_goes_around_a_fixed_task():
    vet = Task(title="Vet", duration=30, priority=1, fixed_start=time(8, 30))
    walk = Task(title="Walk", duration=45, priority=3)
    schedule = make_schedule()
    schedule.generate_schedule([vet, walk])
    assert "gap before 'Vet' was too short" in schedule.get_reason(walk)


def test_no_detour_note_when_task_fits_before_fixed_task():
    vet = Task(title="Vet", duration=30, priority=1, fixed_start=time(9, 0))
    walk = Task(title="Walk", duration=30, priority=3)
    schedule = make_schedule()
    schedule.generate_schedule([vet, walk])
    assert "too short" not in schedule.get_reason(walk)


def test_unscheduled_reasons_for_each_kind():
    groom = Task(title="Groom", duration=60, priority=1, fixed_start=time(9, 0))
    vet = Task(title="Vet", duration=30, priority=3, fixed_start=time(9, 30))
    late = Task(title="Late", duration=30, fixed_start=time(19, 45))
    huge = Task(title="Huge", duration=13 * 60, priority=1)
    schedule = make_schedule()
    schedule.generate_schedule([groom, vet, late, huge])
    assert "overlaps 'Vet'" in schedule.get_reason(groom)
    assert "doesn't fit inside the 08:00-20:00 window" in schedule.get_reason(late)
    assert "Needs 780 min" in schedule.get_reason(huge)


def test_reasons_reset_when_regenerating():
    huge = Task(title="Huge", duration=13 * 60)
    schedule = make_schedule()
    schedule.generate_schedule([huge])
    assert schedule.get_reason(huge)
    schedule.set_end_time(time(23, 0))
    schedule.generate_schedule([huge])
    assert "Needs" not in schedule.get_reason(huge)
    assert schedule.unscheduled_reasons == {}


def test_get_reason_for_unknown_task_is_empty():
    assert make_schedule().get_reason(Task(title="Nope")) == ""


def test_not_due_tasks_are_listed_and_explained():
    daily = Task(title="Feed", duration=10, repeat_days=ALL_DAYS)
    bath = Task(title="Bath", duration=20, repeat_days=[1])
    schedule = make_schedule()
    schedule.set_plan_date(MON)
    schedule.generate_schedule([daily, bath])
    assert schedule.get_not_due_tasks() == [bath]
    assert "Skipped because they aren't due on this day: Bath." in schedule.explain()


def test_not_due_uses_identity_so_equal_tasks_are_not_both_dropped():
    a = Task(title="Same", duration=10, repeat_days=[0])
    b = Task(title="Same", duration=10, repeat_days=[0])
    schedule = make_schedule()
    schedule.set_plan_date(TUE)
    schedule.generate_schedule([a, b])
    assert schedule.get_not_due_tasks() == [a, b]
    schedule.set_plan_date(MON)
    schedule.generate_schedule([a, b])
    assert len(schedule.get_tasks()) == 2


def test_explain_summarises_schedule_in_clock_order():
    vet = Task(title="Vet", duration=30, priority=1, fixed_start=time(9, 0))
    walk = Task(title="Walk", duration=30, priority=3)
    huge = Task(title="Huge", duration=13 * 60, priority=2)
    schedule = make_schedule()
    schedule.set_plan_date(MON)
    schedule.generate_schedule([vet, walk, huge])
    text = schedule.explain()
    assert text.startswith("Planned Monday Jan 01, 08:00-20:00: 2 task(s) scheduled (60 min, 660 min left), 1 couldn't")
    assert text.index("08:00-08:30 Walk") < text.index("09:00-09:30 Vet")
    assert "Not scheduled: Huge" in text


def test_explain_with_no_tasks():
    schedule = make_schedule()
    schedule.generate_schedule([])
    assert "0 task(s) scheduled (0 min, 720 min left)." in schedule.explain()
