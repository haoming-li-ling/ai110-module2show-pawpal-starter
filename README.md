# PawPal+ (Module 2 Project)

PawPal+ is a Streamlit app that helps a busy pet owner plan daily care for their pets. It tracks tasks (walks, feeding, meds, grooming and so on), respects the time the owner has available, and produces a prioritized daily plan with an explanation of why it was chosen.

## ✨ Features

- **Priority-based planning:** pending tasks are sorted high, then medium, then low. Ties go to the earlier preferred time, then the shorter task.
- **Time-budget fitting:** tasks are taken in priority order until the owner's available minutes run out. A task that doesn't fit is skipped so smaller, lower-priority tasks can still use the leftover time.
- **Sorting by time:** any task list can be ordered by preferred `HH:MM`, with tasks that have no preferred time placed last.
- **Filtering:** view tasks for one pet, only pending or only completed tasks, or both filters together.
- **Conflict warnings:** tasks with a preferred time are compared by start and end, and overlapping windows (including across different pets) produce a warning. Back-to-back tasks are not conflicts, and nothing is moved or removed automatically.
- **Daily and weekly recurrence:** completing a recurring task marks it done and creates the next occurrence 1 or 7 days after its due date. Future-dated tasks stay out of today's plan until due, and completing a task twice never creates duplicates.
- **Next available slot:** `find_next_available_slot()` finds the earliest time of day (07:00 to 21:00 by default) where a task of a given length fits without overlapping the timed tasks in the plan.
- **Plan explanation:** `explain_plan()` lists every scheduled task and every task that was skipped for lack of time.
- **Persistence:** the owner, pets and tasks are saved to `data.json` and reloaded on startup.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py   # the web app
python main.py         # command-line demo
python -m pytest       # tests
```

## 🛠️ Implementation Summary

The core logic lives in `pawpal_system.py` and is made of four classes:

- **`Task`** (dataclass) is one care activity: title, duration, priority (`high`/`medium`/`low`), an optional preferred time, the name of its pet, a completed flag, and optional `recurrence` (`daily`/`weekly`) and `due_date`.
- **`Pet`** (dataclass) owns a list of tasks. Adding a task stamps it with the pet's name; it can also be renamed, and completing a recurring task adds the next occurrence.
- **`Owner`** (dataclass) has a name, a daily time budget in minutes, and a list of pets. `get_all_tasks()` flattens every pet's tasks into one list, and `save_to_json()`/`load_from_json()` persist everything as JSON.
- **`Scheduler`** takes an `Owner` and produces the plan, plus sorting, filtering and conflict detection.

How they work together: an `Owner` holds `Pet`s, and each `Pet` holds `Task`s. When `Scheduler.generate_daily_plan()` runs, it collects the owner's pending tasks that are due, sorts them by priority (ties go to the earlier preferred time, then the shorter task), and keeps tasks in that order while they fit in the owner's available minutes. A task that doesn't fit is skipped so smaller ones can still be scheduled. The result is stored in `scheduler.plan`, `detect_conflicts()` checks it for overlapping times, and `explain_plan()` turns it into text that lists each scheduled task and each skipped one.

### Final UML

![PawPal+ final UML class diagram](diagrams/uml_final.png)

Source: [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd)

`main.py` is a command-line demo of this flow, and `tests/test_pawpal.py` holds the tests (run with `python -m pytest`).

## 🧪 Testing PawPal+

Run the full suite from the repo root:

```bash
python -m pytest
```

**What the tests cover** (`tests/`, 37 tests):

- **Sorting:** tasks come back in chronological order (untimed last), sorting doesn't mutate its input, and priority sort breaks ties by time.
- **Recurrence:** completing a daily/weekly task creates the next occurrence (correct date, across month boundaries, details preserved); non-recurring tasks create nothing; completing twice doesn't duplicate.
- **Conflict detection:** duplicate and overlapping times are flagged (same pet and across pets); back-to-back tasks, untimed tasks and malformed times are not.
- **Planning:** the plan respects the time budget, skips completed and future-dated tasks, and handles an owner with no pets.
- **Next available slot, priority validation, persistence and formatting:** gaps between timed tasks, rejecting unknown priorities, JSON round-trips including recurrence fields and corrupt files, and the display helpers.
- **Basics:** task completion, adding/renaming pets' tasks, filtering, and JSON save/load round-trip.

Test output:

```
============================= test session starts ==============================
collecting ... collected 37 items

tests/test_formatting.py::test_task_emoji_matches_keywords_and_falls_back PASSED [  2%]
tests/test_formatting.py::test_status_icon_and_priority_badge PASSED     [  5%]
tests/test_formatting.py::test_schedule_table_has_header_and_a_row_per_task PASSED [  8%]
tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 10%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 13%]
tests/test_pawpal.py::test_owner_save_and_load_round_trip PASSED         [ 16%]
tests/test_pawpal.py::test_rename_pet_updates_task_pet_names PASSED      [ 18%]
tests/test_pawpal.py::test_sort_by_time_puts_unset_last PASSED           [ 21%]
tests/test_pawpal.py::test_filter_by_pet_and_status PASSED               [ 24%]
tests/test_pawpal.py::test_daily_task_recurs_next_day PASSED             [ 27%]
tests/test_pawpal.py::test_weekly_task_recurs_in_seven_days PASSED       [ 29%]
tests/test_pawpal.py::test_non_recurring_task_returns_none PASSED        [ 32%]
tests/test_pawpal.py::test_future_recurrence_is_left_out_of_plan PASSED  [ 35%]
tests/test_pawpal.py::test_detect_conflicts_flags_overlap_only PASSED    [ 37%]
tests/test_pawpal.py::test_scheduler_mark_task_complete_adds_next_occurrence PASSED [ 40%]
tests/test_pawpal.py::test_completing_twice_does_not_duplicate PASSED    [ 43%]
tests/test_pawpal.py::test_detect_conflicts_ignores_malformed_time PASSED [ 45%]
tests/test_pawpal.py::test_sort_by_time_is_chronological_for_unsorted_input PASSED [ 48%]
tests/test_pawpal.py::test_sort_by_time_does_not_mutate_input PASSED     [ 51%]
tests/test_pawpal.py::test_sort_by_priority_orders_high_to_low_then_time PASSED [ 54%]
tests/test_pawpal.py::test_daily_recurrence_crosses_month_boundary PASSED [ 56%]
tests/test_pawpal.py::test_daily_recurrence_without_due_date_uses_today PASSED [ 59%]
tests/test_pawpal.py::test_recurring_copy_keeps_details_and_is_pending PASSED [ 62%]
tests/test_pawpal.py::test_detect_conflicts_flags_duplicate_times PASSED [ 64%]
tests/test_pawpal.py::test_detect_conflicts_flags_duplicate_times_across_pets PASSED [ 67%]
tests/test_pawpal.py::test_detect_conflicts_back_to_back_is_not_a_conflict PASSED [ 70%]
tests/test_pawpal.py::test_detect_conflicts_ignores_untimed_tasks_and_empty_input PASSED [ 72%]
tests/test_pawpal.py::test_plan_respects_time_budget_and_skips_completed PASSED [ 75%]
tests/test_pawpal.py::test_plan_for_owner_with_no_pets_is_empty PASSED   [ 78%]
tests/test_pawpal.py::test_next_slot_is_earliest_when_nothing_is_scheduled PASSED [ 81%]
tests/test_pawpal.py::test_next_slot_skips_past_a_busy_block PASSED      [ 83%]
tests/test_pawpal.py::test_next_slot_uses_a_gap_between_tasks PASSED     [ 86%]
tests/test_pawpal.py::test_next_slot_returns_none_when_day_is_full PASSED [ 89%]
tests/test_pawpal.py::test_next_slot_rejects_bad_input PASSED            [ 91%]
tests/test_pawpal.py::test_save_and_load_keep_recurrence_and_due_date PASSED [ 94%]
tests/test_pawpal.py::test_load_from_json_rejects_corrupt_file PASSED    [ 97%]
tests/test_pawpal.py::test_priority_is_normalized_and_validated PASSED   [100%]

============================== 37 passed in 0.03s ==============================
```

**Confidence Level: ⭐⭐⭐⭐ (4/5)** — all 37 tests pass and cover the core scheduling behaviors and edge cases. Not 5 because the Streamlit UI (`app.py`) is untested and conflict detection only compares tasks by their preferred times.

## 💾 Data Persistence

PawPal+ remembers your owner, pets and tasks between runs in `data.json` (next to `app.py`, ignored by git).

**Workflow**

1. On startup, `app.py` calls `Owner.load_from_json("data.json")`. If the file is missing, the app starts with a fresh owner. If it can't be read, the app starts fresh and shows a warning.
2. As you use the app, each change that matters (removing a pet or task, completing a task) calls `persist()`, and `persist()` also runs at the end of every page run, so edits are saved after each interaction.
3. `persist()` calls `Owner.save_to_json("data.json")`. If the file can't be written, the app shows a warning and keeps running.

**How objects become JSON.** I used custom dictionary conversion instead of a library like marshmallow, because the model is only three small dataclasses. `Task.to_dict()` uses `dataclasses.asdict`, `Pet.to_dict()` and `Owner.to_dict()` nest their children's dicts, and the matching `from_dict()` classmethods rebuild the objects. `Pet.from_dict()` re-adds each task through `add_task()`, so every task's `pet_name` is restored. Recurrence and due dates are plain strings, so they round-trip without special handling. A library would add a dependency and a schema to maintain for no real gain at this size.

**Files modified:** `pawpal_system.py` (renamed `save`/`load` to `save_to_json`/`load_from_json`), `app.py` (uses the new names and `data.json`), `tests/test_pawpal.py` (round-trip tests, including recurrence fields and a corrupt file), `.gitignore` (ignores `data.json`).

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting by priority | `Scheduler.sort_by_priority()` | High before medium before low; ties go to the earlier preferred time, then the shorter task |
| Sorting by time | `Scheduler.sort_by_time()` | Orders by preferred `HH:MM`; tasks with no time go last |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Limit to one pet, a status, or both; `None` means no filter |
| Time budget | `Scheduler.fits_in_time()` | Keeps tasks in order until the owner's minutes run out; skips one that doesn't fit so smaller ones can still use the time |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns about overlapping preferred-time windows |
| Next available slot | `Scheduler.find_next_available_slot(duration_minutes, earliest, latest)` | Sweeps the timed tasks in order and returns the first `HH:MM` gap that is long enough, or `None` |
| Recurring tasks | `Task.mark_complete()`, `Pet.complete_task()`, `Scheduler.mark_task_complete()` | Completing a daily or weekly task creates the next occurrence |

### Priority scheduling
Every `Task` has a `priority` of `high`, `medium` or `low`. It is lowercased and
validated when the task is created, so a typo such as `"hgih"` raises a
`ValueError` instead of silently sorting last. `Scheduler.sort_by_priority()`
orders by priority first, then preferred time, then duration, and
`generate_daily_plan()` uses that order to fill the owner's time.

Output from `python main.py` (the demo's seven tasks, ordered by priority and
then by time):

```text
Sorted by priority, then time:
  🔴 High    07:30 🦮 Morning walk (Mochi)
  🔴 High    07:45 🍽️ Breakfast (Kiki)
  🔴 High    12:00 💊 Give medication (Kiki)
  🔴 High    17:00 ✂️ Grooming appointment (Mochi)
  🟡 Medium  17:00 🎾 Play with feather toy (Kiki)
  🟡 Medium  --    🦮 Evening stroll (Mochi)
  🟢 Low     18:00 ✂️ Brush coat (Mochi)
```

When time is short, priority wins over the clock. Here the owner has 40 minutes
and four tasks. Sorting by time alone would put the low-priority task first, but
the plan keeps the two high-priority tasks and skips the rest:

```text
Time available: 40 min
By time only:
  07:00 low    Brush coat (25 min)
  07:30 medium Evening stroll (20 min)
  08:00 high   Morning walk (30 min)
  18:00 high   Give medication (5 min)
Plan (priority first, then time):
  high   08:00 Morning walk (30 min)
  high   18:00 Give medication (5 min)
Skipped: Brush coat (low, 25 min)
Skipped: Evening stroll (medium, 20 min)
```

### Sorting
`generate_daily_plan()` sorts pending tasks with `sort_by_priority()`. Use
`sort_by_time()` for a clock-order view, such as the task list in the app.

### Filtering
`filter_tasks(pet_name="Kiki", completed=False)` returns Kiki's pending tasks.
The app's "Show pet" and "Show status" controls use it. The planner also leaves
out completed tasks and tasks whose `due_date` is in the future.

### Conflict detection
`detect_conflicts()` checks the current plan, or a list you pass in. It sorts
tasks with a preferred time by start, then compares each task only with later
ones until one starts after it ends (O(n log n) plus the overlaps found). A
task that starts exactly when another ends is not a conflict. It returns
warning strings, which the app shows as warnings. It never removes or moves a
task. Tasks with no preferred time, or a malformed one, are ignored.

### Recurring tasks
A task has `recurrence` (`"daily"`, `"weekly"`, or empty) and an ISO
`due_date`. `Task.mark_complete()` marks the task done and, if it recurs,
returns a copy due 1 or 7 days after the old due date (or after today if it had
none). `Scheduler.mark_task_complete()` finds the owning pet and adds that copy
through `Pet.complete_task()`, so completing a recurring task automatically
creates the next one. Completing an already-completed task does nothing, so it
can't create duplicates. Call `Task.mark_complete()` directly and you get the
new task back but it is not added to a pet.

## 🎨 Output Formatting

The CLI demo and the Streamlit app share the helpers in `formatting.py`:

- **Structured tables:** `schedule_table()` renders the daily plan with the [`tabulate`](https://pypi.org/project/tabulate/) library (added to `requirements.txt`) instead of hand-padded strings.
- **Color-coded priority:** `priority_badge()` adds a colored circle to each priority (🔴 High, 🟡 Medium, 🟢 Low). `colorize()` also wraps the badge in ANSI color codes in the CLI, but only when output goes to a terminal and `NO_COLOR` is not set, so piped output and tests stay plain text.
- **Task-type emojis:** `task_emoji()` picks an emoji from keywords in the title (🦮 walks, 🍽️ meals, 💊 medication, ✂️ grooming, 🎾 play, 🐾 anything else).
- **Status indicators:** `status_icon()` shows ✅ for completed tasks and ⏳ for pending ones.
- **Where they appear:** `main.py` uses all of them in its task lists and schedule table, and `app.py` uses the emojis, priority badges and status icons in the task list and the plan tables, alongside `st.success`, `st.warning` and `st.metric`. Conflict warnings in the CLI are prefixed with ⚠️.

Emoji widths vary between terminals, so columns containing emoji can look slightly misaligned in some of them.

## 📸 Demo Walkthrough

### Main UI features
The Streamlit app (`streamlit run app.py`) lets you:

- **Owner:** set your name and the minutes you have available today.
- **Pets:** add a pet (name and species), rename it, or remove it. Duplicate names are rejected.
- **Tasks:** add a task with a title, duration, priority, optional preferred time (`HH:MM`) and repeat setting (none, daily or weekly). The task list can be filtered by pet and status and sorted by entered order or preferred time. Each row has **Done** and **Remove** buttons.
- **Today's Schedule:** click **Generate schedule** to see the plan, summary metrics, warnings and an explanation of the choices.

### Example workflow
1. Set the owner name to Jordan and available time to 90 minutes.
2. Add a pet, for example Mochi (dog), then another, Kiki (cat).
3. Add tasks such as "Morning walk" (30 min, high, 07:30, daily) for Mochi and "Breakfast" (10 min, high, 07:45) for Kiki.
4. Use "Sort by: Preferred time" and the pet and status filters to review the list. A warning appears right away if two pending tasks overlap.
5. Click **Done** on a daily task. It is marked complete and the next occurrence is added, due tomorrow.
6. Click **Generate schedule** to view today's plan, with minutes used, any conflict warnings and any skipped tasks.

### Scheduler behaviors shown
- **Sorting:** the plan is ordered by priority, and the time-sorted view shows the same tasks in clock order.
- **Conflict warnings:** overlapping preferred times are flagged with the tasks and pets involved, as `st.warning` messages in the UI.
- **Time budget:** tasks that don't fit are listed as skipped instead of being silently dropped.
- **Recurrence:** completing a daily or weekly task creates its next occurrence.

### Sample CLI output
Output of `python main.py`:

```text
Entered order:
  ⏳ 18:00 ✂️ Brush coat (Mochi)
  ⏳ 07:30 🦮 Morning walk (Mochi)
  ⏳ --    🦮 Evening stroll (Mochi)
  ⏳ 17:00 ✂️ Grooming appointment (Mochi)
  ⏳ 17:00 🎾 Play with feather toy (Kiki)
  ⏳ 12:00 💊 Give medication (Kiki)
  ⏳ 07:45 🍽️ Breakfast (Kiki)
Sorted by time:
  ⏳ 07:30 🦮 Morning walk (Mochi)
  ⏳ 07:45 🍽️ Breakfast (Kiki)
  ⏳ 12:00 💊 Give medication (Kiki)
  ⏳ 17:00 ✂️ Grooming appointment (Mochi)
  ⏳ 17:00 🎾 Play with feather toy (Kiki)
  ⏳ 18:00 ✂️ Brush coat (Mochi)
  ⏳ --    🦮 Evening stroll (Mochi)
Sorted by priority, then time:
  🔴 High    07:30 🦮 Morning walk (Mochi)
  🔴 High    07:45 🍽️ Breakfast (Kiki)
  🔴 High    12:00 💊 Give medication (Kiki)
  🔴 High    17:00 ✂️ Grooming appointment (Mochi)
  🟡 Medium  17:00 🎾 Play with feather toy (Kiki)
  🟡 Medium  --    🦮 Evening stroll (Mochi)
  🟢 Low     18:00 ✂️ Brush coat (Mochi)

Completed 'Give medication'; next due 2026-10-21
Kiki pending: ['Play with feather toy', 'Breakfast', 'Give medication']
Completed: ['Give medication']

⚠️  WARNING: Conflict (Mochi and Kiki): 'Morning walk' at 07:30 (30 min) overlaps 'Breakfast' at 07:45.
⚠️  WARNING: Conflict (Mochi and Kiki): 'Grooming appointment' at 17:00 (10 min) overlaps 'Play with feather toy' at 17:00.
================================================================
                   TODAY'S SCHEDULE - Jordan                    
================================================================
Pets: Mochi (dog), Kiki (cat)
Time available: 90 min
----------------------------------------------------------------
  #  Preferred    Task                      Pet      Min  Priority
---  -----------  ------------------------  -----  -----  ----------
  1  07:30        🦮 Morning walk           Mochi     30  🔴 High
  2  07:45        🍽️ Breakfast              Kiki      10  🔴 High
  3  17:00        ✂️ Grooming appointment   Mochi     10  🔴 High
  4  17:00        🎾 Play with feather toy  Kiki      20  🟡 Medium
  5  --           🦮 Evening stroll         Mochi     15  🟡 Medium
----------------------------------------------------------------
Total: 85 of 90 min scheduled

Why this plan:
Jordan has 90 minutes today; the plan uses 85.
1. Morning walk (Mochi) - 30 min, high priority, preferred 07:30
2. Breakfast (Kiki) - 10 min, high priority, preferred 07:45
3. Grooming appointment (Mochi) - 10 min, high priority, preferred 17:00
4. Play with feather toy (Kiki) - 20 min, medium priority, preferred 17:00
5. Evening stroll (Mochi) - 15 min, medium priority
Skipped: Brush coat (Mochi) - 40 min did not fit in the remaining time.

Next free 15-min slot: 07:00
Next free 45-min slot: 08:00
Next free 120-min slot: 08:00
```
