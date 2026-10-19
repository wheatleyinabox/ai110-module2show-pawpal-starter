from datetime import date, time, timedelta

from pawpal_system import ALL_DAYS, Pet, User, Task, Schedule


def main() -> None:
    # Step 1: create a user
    user = User(username="wheatleyinabox", email="wheatleyinabox123@email.com", password="pawpal123")

    print("Step 1: User")
    print(f"  Username:  {user.get_username()}")
    print(f"  Email:     {user.get_email()}")
    print(f"  Pets:      {len(user.get_pets())}")
    print(f"  Tasks:     {len(user.get_tasks())}")
    print(f"  Schedules: {len(user.get_schedules())}")

    # Step 2: add pets
    max_dog = Pet(name="Max", breed="Golden Retriever", age="4", medications="Joint supplement")
    luna = Pet(name="Luna", breed="Tabby Cat", age="2", health_conditions="Sensitive stomach")
    user.add_pet(max_dog)
    user.add_pet(luna)

    print("\nStep 2: Pets")
    for pet in user.get_pets():
        print(f"  {pet.get_name()} ({pet.get_breed()}, age {pet.get_age()})")
        print(f"    Health conditions: {pet.get_health_conditions() or 'none'}")
        print(f"    Medications:       {pet.get_medications() or 'none'}")

    # Step 3: create tasks (duration in minutes, higher priority number = scheduled earlier)
    walk = Task(title="Morning walk", desc="Around the block", duration=30, priority=4)
    walk.add_pet(max_dog)
    meds = Task(title="Give joint supplement", duration=5, priority=3)
    meds.add_pet(max_dog)
    litter = Task(title="Clean litter box", duration=15, priority=2)
    litter.add_pet(luna)
    play = Task(title="Playtime", desc="Feather wand and treats", duration=45, priority=1)
    play.add_pet(max_dog)
    play.add_pet(luna)

    for task in (walk, meds, litter, play):
        user.add_task(task)

    print("\nStep 3: Tasks")
    for task in user.get_tasks():
        pet_names = ", ".join(p.get_name() for p in task.get_pets())
        print(f"  [{task.get_priority()}] {task.get_title()} - {task.get_duration()} min ({pet_names})")

    # Step 4: generate a schedule (default window is 8am-8pm)
    schedule = Schedule(title="Today", desc="Daily pet care")
    user.add_schedule(schedule)
    schedule.generate_schedule(user.get_tasks())

    print(f"\nStep 4: Schedule - {schedule.get_title()} "
          f"({schedule.get_start_time():%H:%M}-{schedule.get_end_time():%H:%M})")
    for task in schedule.get_tasks():
        print(f"  {task.get_start_time():%H:%M}-{task.get_end_time():%H:%M}  {task.get_title()}")
    print(f"  Total time:     {schedule.get_total_time()} min")
    print(f"  Available time: {schedule.get_available_time()} min")
    print(f"  Unscheduled:    {len(schedule.get_unscheduled_tasks())}")
    print("  Why this plan:")
    for line in schedule.explain().splitlines():
        print(f"    {line}")

    # Step 5: shrink the window to 8am-9am and regenerate; Playtime (45 min) won't fit
    schedule.set_end_time(time(9, 0))
    schedule.generate_schedule(user.get_tasks())

    print(f"\nStep 5: Tight window ({schedule.get_start_time():%H:%M}-{schedule.get_end_time():%H:%M})")
    for task in schedule.get_tasks():
        print(f"  {task.get_start_time():%H:%M}-{task.get_end_time():%H:%M}  {task.get_title()}")
    print(f"  Total time:     {schedule.get_total_time()} min")
    print(f"  Available time: {schedule.get_available_time()} min")
    print("  Unscheduled:")
    for task in schedule.get_unscheduled_tasks():
        print(f"    {task.get_title()} - {task.get_duration()} min "
              f"(placed: {schedule.get_placement(task) is not None})")
        print(f"      Why: {schedule.get_reason(task)}")

    # Step 6: edge cases
    print("\nStep 6: Edge cases")

    empty = Schedule(title="Empty")
    empty.generate_schedule([])
    print(f"  No tasks: scheduled={len(empty.get_tasks())}, unscheduled={len(empty.get_unscheduled_tasks())}, "
          f"available={empty.get_available_time()} min")

    too_long = Task(title="All-day grooming", duration=13 * 60, priority=2)
    short = Task(title="Quick treat", duration=5, priority=1)
    edge = Schedule(title="Edge")  # 12-hour window
    edge.generate_schedule([too_long, short])
    print(f"  Task longer than window: scheduled={[t.get_title() for t in edge.get_tasks()]}, "
          f"unscheduled={[t.get_title() for t in edge.get_unscheduled_tasks()]}")

    first = Task(title="Feed (entered first)", duration=10, priority=1)
    second = Task(title="Water (entered second)", duration=10, priority=1)
    ties = Schedule(title="Ties")
    ties.generate_schedule([first, second])
    print(f"  Same priority order: {[t.get_title() for t in ties.get_tasks()]}")

    # Step 7: sorting and filtering
    print("\nStep 7: Sorting and filtering")
    schedule.set_end_time(time(20, 0))
    schedule.generate_schedule(user.get_tasks())
    vet_call = Task(title="Vet call (not in this schedule)", duration=10, priority=1)
    user.add_task(vet_call)

    print("  All tasks by start time (unscheduled last):")
    for task in schedule.sort_tasks_by_time(user.get_tasks()):
        placement = schedule.get_placement(task)
        print(f"    {placement.get_start_time():%H:%M}" if placement else "    --:--", task.get_title())

    for pet in user.get_pets():
        print(f"  Tasks for {pet.get_name()}:")
        for task in user.get_tasks_for_pet(pet):
            print(f"    {task.get_title()}")
        print(f"  Scheduled for {pet.get_name()}, in clock order:")
        for placement in schedule.get_tasks_for_pet(pet):
            print(f"    {placement.get_start_time():%H:%M} {placement.get_title()}")

    # A task can sit in several schedules at different times
    evening = Schedule(title="Evening", start_time=time(18, 0))
    evening.generate_schedule(user.get_tasks())
    walk_morning, walk_evening = schedule.get_placement(walk), evening.get_placement(walk)
    print(f"  '{walk.get_title()}' is {walk_morning.get_start_time():%H:%M} in '{schedule.get_title()}' "
          f"and {walk_evening.get_start_time():%H:%M} in '{evening.get_title()}'")

    # Step 8: fixed-time tasks and conflict detection
    print("\nStep 8: Fixed times and conflicts")
    user.remove_task(vet_call)
    vet = Task(title="Vet checkup", duration=60, priority=3, fixed_start=time(9, 0))
    vet.add_pet(max_dog)
    groom = Task(title="Grooming", duration=45, priority=2, fixed_start=time(9, 30))
    groom.add_pet(max_dog)
    for task in (vet, groom):
        user.add_task(task)
    fixed = Schedule(title="Fixed times")
    fixed.generate_schedule(user.get_tasks())
    for placement in fixed.get_tasks():
        print(f"  {placement.get_start_time():%H:%M}-{placement.get_end_time():%H:%M}  {placement.get_title()}")
    for dropped, blocker in fixed.get_conflicts():
        print(f"  CONFLICT: {dropped.get_title()} ({dropped.get_fixed_start():%H:%M}) overlaps {blocker.get_title()}")
    for task in fixed.get_unscheduled_tasks():
        print(f"  Unscheduled: {task.get_title()}")
        print(f"    Why: {fixed.get_reason(task)}")

    late = Task(title="Late-night vet", duration=30, priority=1, fixed_start=time(21, 0))
    outside = Schedule(title="Outside window")
    outside.generate_schedule([late])
    print(f"  Fixed at 21:00 but window ends at {outside.get_end_time():%H:%M}: "
          f"scheduled={len(outside.get_tasks())}, unscheduled={len(outside.get_unscheduled_tasks())}, "
          f"conflicts={len(outside.get_conflicts())}")

    # Step 9: recurring tasks and per-day schedules
    print("\nStep 9: Recurring tasks")
    for task in (vet, groom):
        user.remove_task(task)  # keep the weekly demo to the everyday tasks plus the new ones below
    walk.set_repeat_days(ALL_DAYS)
    meds.set_repeat_days(ALL_DAYS)
    bath = Task(title="Bath time", duration=40, priority=2, repeat_days=[0, 3])  # Mon and Thu
    bath.add_pet(max_dog)
    monday = date.today() - timedelta(days=date.today().weekday())
    wednesday = monday + timedelta(days=2)
    appointment = Task(title="Vet appointment", duration=30, priority=3,
                       fixed_start=time(10, 0), on_date=wednesday)  # one-time, pinned to Wednesday
    appointment.add_pet(luna)
    groom_wk = Task(title="Grooming", duration=45, priority=2,
                    fixed_start=time(10, 15), repeat_days=[2, 4])  # Wed and Fri
    groom_wk.add_pet(max_dog)
    for task in (bath, appointment, groom_wk):
        user.add_task(task)

    print("  Repeat settings:")
    for task in user.get_tasks():
        print(f"    {task.get_title():<24} {task.describe_repeat()}")

    print(f"  Week of {monday:%b %d} (a separate schedule for each day):")
    for offset in range(7):
        day = monday + timedelta(days=offset)
        day_plan = Schedule(title=f"{day:%a}", plan_date=day)
        day_plan.generate_schedule(user.get_tasks())
        items = ", ".join(f"{p.get_start_time():%H:%M} {p.get_title()}" for p in day_plan.get_tasks())
        print(f"    {day:%a %b %d}: {items}")
        for dropped, blocker in day_plan.get_conflicts():
            print(f"        CONFLICT: {dropped.get_title()} overlaps {blocker.get_title()}")
            print(f"        Why: {day_plan.get_reason(dropped)}")

    tuesday_plan = Schedule(title="Tue", plan_date=wednesday - timedelta(days=1))
    tuesday_plan.generate_schedule(user.get_tasks())
    print("  Explanation for Tuesday (tasks not due that day are mentioned too):")
    for line in tuesday_plan.explain().splitlines():
        print(f"    {line}")

    print(f"  Due on {wednesday:%a}: {[t.get_title() for t in user.get_tasks_for_date(wednesday)]}")
    print(f"  Due on {wednesday:%a} for Luna: "
          f"{[t.get_title() for t in user.get_tasks_for_date(wednesday) if luna in t.get_pets()]}")

if __name__ == "__main__":
    main()
