from formatting import priority_badge, schedule_table, status_icon, task_emoji
from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    """Demo the scheduler: sorting, filtering, recurrence, conflicts, and the plan."""
    owner = Owner(name="Jordan", available_minutes=90)

    mochi = Pet(name="Mochi", species="dog")
    kiki = Pet(name="Kiki", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(kiki)

    # Added deliberately out of time order, with a recurring task and an overlap.
    kiki.add_task(Task("Play with feather toy", 20, "medium", preferred_time="17:00"))
    mochi.add_task(Task("Brush coat", 40, "low", preferred_time="18:00"))
    kiki.add_task(Task("Give medication", 5, "high", preferred_time="12:00", recurrence="daily"))
    mochi.add_task(Task("Morning walk", 30, "high", preferred_time="07:30"))
    kiki.add_task(Task("Breakfast", 10, "high", preferred_time="07:45"))  # overlaps walk
    mochi.add_task(Task("Evening stroll", 15, "medium"))
    mochi.add_task(Task("Grooming appointment", 10, "high", preferred_time="17:00"))  # same time as play

    scheduler = Scheduler(owner)

    print("Entered order:")
    for t in owner.get_all_tasks():
        print(f"  {status_icon(t)} {t.preferred_time or '--':<6}{task_emoji(t)} {t.title} ({t.pet_name})")
    print("Sorted by time:")
    for t in scheduler.sort_by_time(owner.get_all_tasks()):
        print(f"  {status_icon(t)} {t.preferred_time or '--':<6}{task_emoji(t)} {t.title} ({t.pet_name})")

    print("Sorted by priority, then time:")
    for t in scheduler.sort_by_priority(owner.get_all_tasks()):
        print(f"  {priority_badge(t.priority):<10}{t.preferred_time or '--':<6}{task_emoji(t)} {t.title} ({t.pet_name})")

    meds = kiki.tasks[1]
    nxt = scheduler.mark_task_complete(meds)
    print(f"\nCompleted '{meds.title}'; next due {nxt.due_date}")
    print("Kiki pending:", [t.title for t in scheduler.filter_tasks("Kiki", False)])
    print("Completed:", [t.title for t in scheduler.filter_tasks(completed=True)])
    print()

    plan = scheduler.generate_daily_plan()
    for warning in scheduler.detect_conflicts():
        print("⚠️  WARNING:", warning)

    width = 64
    print("=" * width)
    print(f"TODAY'S SCHEDULE - {owner.name}".center(width))
    print("=" * width)
    print(f"Pets: {', '.join(f'{p.name} ({p.species})' for p in owner.pets)}")
    print(f"Time available: {owner.available_minutes} min")
    print("-" * width)
    print(schedule_table(plan))
    print("-" * width)
    used = sum(t.duration_minutes for t in plan)
    print(f"Total: {used} of {owner.available_minutes} min scheduled")
    print()
    print("Why this plan:")
    print(scheduler.explain_plan())

    print()
    for minutes in (15, 45, 120):
        slot = scheduler.find_next_available_slot(minutes)
        print(f"Next free {minutes}-min slot: {slot or 'none today'}")


if __name__ == "__main__":
    main()
