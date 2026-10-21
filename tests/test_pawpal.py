from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Morning walk", 30, "high"))

    assert len(pet.tasks) == 1


def test_owner_save_and_load_round_trip(tmp_path):
    owner = Owner("Sam", 60)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, "high", preferred_time="07:30"))
    path = tmp_path / "data.json"

    owner.save_to_json(path)
    loaded = Owner.load_from_json(path)

    assert loaded == owner
    assert loaded.pets[0].tasks[0].pet_name == "Mochi"


def test_rename_pet_updates_task_pet_names():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, "high"))

    pet.rename("Moji")

    assert pet.tasks[0].pet_name == "Moji"


def _owner_with_tasks():
    owner = Owner("Sam", 120)
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("Walk", 30, "high", preferred_time="09:00"))
    mochi.add_task(Task("Feed", 10, "low", preferred_time="08:00"))
    luna.add_task(Task("Play", 20, "medium"))
    return owner, mochi, luna


def test_sort_by_time_puts_unset_last():
    owner, _, _ = _owner_with_tasks()
    ordered = Scheduler(owner).sort_by_time(owner.get_all_tasks())
    assert [t.title for t in ordered] == ["Feed", "Walk", "Play"]


def test_filter_by_pet_and_status():
    owner, mochi, luna = _owner_with_tasks()
    mochi.tasks[0].mark_complete()
    s = Scheduler(owner)
    assert [t.title for t in s.filter_tasks(pet_name="Luna")] == ["Play"]
    assert [t.title for t in s.filter_tasks(completed=True)] == ["Walk"]
    assert len(s.filter_tasks(pet_name="Mochi", completed=False)) == 1


def test_daily_task_recurs_next_day():
    pet = Pet("Mochi", "dog")
    task = Task("Meds", 5, "high", recurrence="daily", due_date="2026-01-01")
    pet.add_task(task)

    nxt = pet.complete_task(task)

    assert task.completed and nxt in pet.tasks
    assert nxt.due_date == "2026-01-02" and not nxt.completed


def test_weekly_task_recurs_in_seven_days():
    task = Task("Bath", 20, "low", recurrence="weekly", due_date="2026-01-01")
    assert task.mark_complete().due_date == "2026-01-08"


def test_non_recurring_task_returns_none():
    assert Task("Walk", 30, "high").mark_complete() is None


def test_future_recurrence_is_left_out_of_plan():
    owner = Owner("Sam", 60)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    task = Task("Meds", 5, "high", recurrence="daily")
    pet.add_task(task)
    pet.complete_task(task)

    assert Scheduler(owner).generate_daily_plan() == []


def test_detect_conflicts_flags_overlap_only():
    owner = Owner("Sam", 120)
    a, b = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(a)
    owner.add_pet(b)
    a.add_task(Task("Walk", 30, "high", preferred_time="09:00"))
    b.add_task(Task("Vet", 30, "high", preferred_time="09:15"))
    b.add_task(Task("Feed", 10, "low", preferred_time="09:45"))
    s = Scheduler(owner)
    s.generate_daily_plan()

    warnings = s.detect_conflicts()

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Vet" in warnings[0]


def test_scheduler_mark_task_complete_adds_next_occurrence():
    owner = Owner("Sam", 60)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    task = Task("Meds", 5, "high", recurrence="weekly", due_date="2026-01-01")
    pet.add_task(task)

    nxt = Scheduler(owner).mark_task_complete(task)

    assert len(pet.tasks) == 2
    assert nxt.pet_name == "Mochi" and nxt.due_date == "2026-01-08"


def test_completing_twice_does_not_duplicate():
    owner = Owner("Sam", 60)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    task = Task("Meds", 5, "high", recurrence="daily")
    pet.add_task(task)
    s = Scheduler(owner)

    s.mark_task_complete(task)
    s.mark_task_complete(task)

    assert len(pet.tasks) == 2


def test_detect_conflicts_ignores_malformed_time():
    owner = Owner("Sam", 60)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, "high", preferred_time="bogus"))
    pet.add_task(Task("Feed", 10, "low", preferred_time="09:00"))

    assert Scheduler(owner).detect_conflicts(owner.get_all_tasks()) == []


# --- Core behaviors: sorting, recurrence, conflicts, planning ---


def test_sort_by_time_is_chronological_for_unsorted_input():
    tasks = [
        Task("Evening", 10, "low", preferred_time="18:30"),
        Task("Noon", 10, "low", preferred_time="12:00"),
        Task("Early", 10, "low", preferred_time="06:05"),
        Task("Anytime", 10, "low"),
    ]
    ordered = Scheduler(Owner("Sam", 60)).sort_by_time(tasks)
    assert [t.title for t in ordered] == ["Early", "Noon", "Evening", "Anytime"]


def test_sort_by_time_does_not_mutate_input():
    tasks = [
        Task("B", 10, "low", preferred_time="10:00"),
        Task("A", 10, "low", preferred_time="08:00"),
    ]
    Scheduler(Owner("Sam", 60)).sort_by_time(tasks)
    assert [t.title for t in tasks] == ["B", "A"]


def test_sort_by_priority_orders_high_to_low_then_time():
    tasks = [
        Task("Low", 10, "low", preferred_time="07:00"),
        Task("HighLate", 10, "high", preferred_time="10:00"),
        Task("HighEarly", 10, "high", preferred_time="08:00"),
        Task("Med", 10, "medium"),
    ]
    ordered = Scheduler(Owner("Sam", 60)).sort_by_priority(tasks)
    assert [t.title for t in ordered] == ["HighEarly", "HighLate", "Med", "Low"]


def test_daily_recurrence_crosses_month_boundary():
    task = Task("Meds", 5, "high", recurrence="daily", due_date="2026-01-31")
    assert task.mark_complete().due_date == "2026-02-01"


def test_daily_recurrence_without_due_date_uses_today():
    from datetime import date, timedelta

    nxt = Task("Meds", 5, "high", recurrence="daily").mark_complete()
    assert nxt.due_date == (date.today() + timedelta(days=1)).isoformat()


def test_recurring_copy_keeps_details_and_is_pending():
    pet = Pet("Mochi", "dog")
    task = Task("Meds", 5, "high", "08:00", recurrence="daily", due_date="2026-01-01")
    pet.add_task(task)
    nxt = pet.complete_task(task)
    assert nxt is not task
    assert (nxt.title, nxt.duration_minutes, nxt.priority) == ("Meds", 5, "high")
    assert (nxt.preferred_time, nxt.pet_name, nxt.recurrence) == ("08:00", "Mochi", "daily")
    assert nxt.completed is False


def test_detect_conflicts_flags_duplicate_times():
    owner = Owner("Sam", 120)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, "high", preferred_time="09:00"))
    pet.add_task(Task("Groom", 20, "low", preferred_time="09:00"))

    warnings = Scheduler(owner).detect_conflicts(owner.get_all_tasks())

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Groom" in warnings[0]
    assert "09:00" in warnings[0]


def test_detect_conflicts_flags_duplicate_times_across_pets():
    owner = Owner("Sam", 120)
    a, b = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(a)
    owner.add_pet(b)
    a.add_task(Task("Walk", 30, "high", preferred_time="09:00"))
    b.add_task(Task("Feed", 10, "high", preferred_time="09:00"))

    warnings = Scheduler(owner).detect_conflicts(owner.get_all_tasks())

    assert len(warnings) == 1
    assert "Mochi" in warnings[0] and "Luna" in warnings[0]


def test_detect_conflicts_back_to_back_is_not_a_conflict():
    owner = Owner("Sam", 120)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, "high", preferred_time="09:00"))
    pet.add_task(Task("Feed", 10, "high", preferred_time="09:30"))

    assert Scheduler(owner).detect_conflicts(owner.get_all_tasks()) == []


def test_detect_conflicts_ignores_untimed_tasks_and_empty_input():
    owner = Owner("Sam", 60)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    assert Scheduler(owner).detect_conflicts() == []
    pet.add_task(Task("Walk", 30, "high"))
    pet.add_task(Task("Feed", 10, "high"))
    assert Scheduler(owner).detect_conflicts(owner.get_all_tasks()) == []


def test_plan_respects_time_budget_and_skips_completed():
    owner = Owner("Sam", 40)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    done = Task("Done", 5, "high")
    pet.add_task(done)
    done.mark_complete()
    pet.add_task(Task("Walk", 30, "high"))
    pet.add_task(Task("Bath", 30, "medium"))
    pet.add_task(Task("Treat", 10, "low"))

    plan = Scheduler(owner).generate_daily_plan()

    assert [t.title for t in plan] == ["Walk", "Treat"]


def test_plan_for_owner_with_no_pets_is_empty():
    s = Scheduler(Owner("Sam", 60))
    assert s.generate_daily_plan() == []
    assert s.explain_plan() == "No tasks scheduled."


def _timed_scheduler(*specs):
    """Scheduler whose plan holds (preferred_time, minutes) tasks."""
    owner = Owner(name="Jordan", available_minutes=2000)
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)
    for i, (when, minutes) in enumerate(specs):
        pet.add_task(Task(f"t{i}", minutes, "high", preferred_time=when))
    scheduler = Scheduler(owner)
    scheduler.generate_daily_plan()
    return scheduler


def test_next_slot_is_earliest_when_nothing_is_scheduled():
    assert _timed_scheduler().find_next_available_slot(30) == "07:00"


def test_next_slot_skips_past_a_busy_block():
    scheduler = _timed_scheduler(("07:00", 30), ("07:30", 30))
    assert scheduler.find_next_available_slot(15) == "08:00"


def test_next_slot_uses_a_gap_between_tasks():
    scheduler = _timed_scheduler(("07:00", 60), ("09:00", 30))
    assert scheduler.find_next_available_slot(45) == "08:00"
    assert scheduler.find_next_available_slot(90) == "09:30"


def test_next_slot_returns_none_when_day_is_full():
    scheduler = _timed_scheduler(("07:00", 840))
    assert scheduler.find_next_available_slot(15) is None


def test_next_slot_rejects_bad_input():
    scheduler = _timed_scheduler()
    assert scheduler.find_next_available_slot(0) is None
    assert scheduler.find_next_available_slot(10, earliest="nope") is None


def test_save_and_load_keep_recurrence_and_due_date(tmp_path):
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Kiki", species="cat")
    owner.add_pet(pet)
    pet.add_task(Task("Meds", 5, "high", recurrence="daily", due_date="2030-01-02"))
    path = tmp_path / "data.json"

    owner.save_to_json(path)
    loaded = Owner.load_from_json(path)

    task = loaded.pets[0].tasks[0]
    assert (task.recurrence, task.due_date) == ("daily", "2030-01-02")


def test_load_from_json_rejects_corrupt_file(tmp_path):
    path = tmp_path / "data.json"
    path.write_text("{not json")
    try:
        Owner.load_from_json(path)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for corrupt JSON")


def test_priority_is_normalized_and_validated():
    assert Task("Walk", 10, " High ").priority == "high"
    try:
        Task("Walk", 10, "hgih")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for an unknown priority")
