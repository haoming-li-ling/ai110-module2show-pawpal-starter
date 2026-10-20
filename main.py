from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=90)

    mochi = Pet(name="Mochi", species="dog")
    kiki = Pet(name="Kiki", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(kiki)

    mochi.add_task(Task("Morning walk", 30, "high", preferred_time="07:30"))
    mochi.add_task(Task("Brush coat", 40, "low", preferred_time="18:00"))
    kiki.add_task(Task("Breakfast", 10, "high", preferred_time="08:00"))
    kiki.add_task(Task("Give medication", 5, "high", preferred_time="12:00"))
    kiki.add_task(Task("Play with feather toy", 20, "medium", preferred_time="17:00"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan()

    width = 64
    print("=" * width)
    print(f"TODAY'S SCHEDULE - {owner.name}".center(width))
    print("=" * width)
    print(f"Pets: {', '.join(f'{p.name} ({p.species})' for p in owner.pets)}")
    print(f"Time available: {owner.available_minutes} min")
    print("-" * width)
    print(f"{'#':<3}{'Preferred':<11}{'Task':<24}{'Pet':<8}{'Min':>4}  Priority")
    print("-" * width)
    for i, task in enumerate(plan, 1):
        print(
            f"{i:<3}{task.preferred_time or '--':<11}{task.title:<24}"
            f"{task.pet_name:<8}{task.duration_minutes:>4}  {task.priority}"
        )
    print("-" * width)
    used = sum(t.duration_minutes for t in plan)
    print(f"Total: {used} of {owner.available_minutes} min scheduled")
    print()
    print("Why this plan:")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
