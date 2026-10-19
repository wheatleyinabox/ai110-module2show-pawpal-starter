from datetime import time

from pawpal_system import Pet, User, Task, Schedule


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

    # Step 3: create tasks (duration in minutes, higher priority number = scheduled later,
    # since generate_schedule currently sorts ascending)
    walk = Task(title="Morning walk", desc="Around the block", duration=30, priority=1)
    walk.add_pet(max_dog)
    meds = Task(title="Give joint supplement", duration=5, priority=2)
    meds.add_pet(max_dog)
    litter = Task(title="Clean litter box", duration=15, priority=3)
    litter.add_pet(luna)
    play = Task(title="Playtime", desc="Feather wand and treats", duration=45, priority=4)
    play.add_pet(max_dog)
    play.add_pet(luna)

    for task in (walk, meds, litter, play):
        user.add_task(task)

    print("\nStep 3: Tasks")
    for task in user.get_tasks():
        pet_names = ", ".join(p.get_name() for p in task.get_pets())
        start = task.get_start_time()
        print(f"  [{task.get_priority()}] {task.get_title()} - {task.get_duration()} min ({pet_names})")
        print(f"      Scheduled: {start if start else 'not yet'}")

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
              f"(start: {task.get_start_time()}, end: {task.get_end_time()})")

    # Step 6: edge cases
    print("\nStep 6: Edge cases")

    empty = Schedule(title="Empty")
    empty.generate_schedule([])
    print(f"  No tasks: scheduled={len(empty.get_tasks())}, unscheduled={len(empty.get_unscheduled_tasks())}, "
          f"available={empty.get_available_time()} min")

    too_long = Task(title="All-day grooming", duration=13 * 60, priority=1)
    short = Task(title="Quick treat", duration=5, priority=2)
    edge = Schedule(title="Edge")  # 12-hour window
    edge.generate_schedule([too_long, short])
    print(f"  Task longer than window: scheduled={[t.get_title() for t in edge.get_tasks()]}, "
          f"unscheduled={[t.get_title() for t in edge.get_unscheduled_tasks()]}")

    first = Task(title="Feed (entered first)", duration=10, priority=1)
    second = Task(title="Water (entered second)", duration=10, priority=1)
    ties = Schedule(title="Ties")
    ties.generate_schedule([first, second])
    print(f"  Same priority order: {[t.get_title() for t in ties.get_tasks()]}")


if __name__ == "__main__":
    main()
