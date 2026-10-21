# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Running `python main.py` generates a plan for a sample owner with two pets:

```
================================================================
                   TODAY'S SCHEDULE - Jordan
================================================================
Pets: Mochi (dog), Kiki (cat)
Time available: 90 min
----------------------------------------------------------------
#  Preferred  Task                    Pet      Min  Priority
----------------------------------------------------------------
1  07:30      Morning walk            Mochi     30  high
2  08:00      Breakfast               Kiki      10  high
3  12:00      Give medication         Kiki       5  high
4  17:00      Play with feather toy   Kiki      20  medium
----------------------------------------------------------------
Total: 65 of 90 min scheduled

Why this plan:
Jordan has 90 minutes today; the plan uses 65.
1. Morning walk (Mochi) - 30 min, high priority, preferred 07:30
2. Breakfast (Kiki) - 10 min, high priority, preferred 08:00
3. Give medication (Kiki) - 5 min, high priority, preferred 12:00
4. Play with feather toy (Kiki) - 20 min, medium priority, preferred 17:00
Skipped: Brush coat (Mochi) - 40 min did not fit in the remaining time.
```

## 🛠️ Implementation Summary

The core logic lives in `pawpal_system.py` and is made of four classes:

- **`Task`** (dataclass) is one care activity: title, duration, priority (`high`/`medium`/`low`), an optional preferred time, the name of its pet, and a completed flag.
- **`Pet`** (dataclass) owns a list of tasks. Adding a task stamps it with the pet's name.
- **`Owner`** (dataclass) has a name, a daily time budget in minutes, and a list of pets. `get_all_tasks()` flattens every pet's tasks into one list.
- **`Scheduler`** takes an `Owner` and produces the plan.

How they work together: an `Owner` holds `Pet`s, and each `Pet` holds `Task`s. When `Scheduler.generate_daily_plan()` runs, it collects the owner's pending tasks, sorts them by priority (ties go to the earlier preferred time, then the shorter task), and keeps tasks in that order while they fit in the owner's available minutes. A task that doesn't fit is skipped so smaller ones can still be scheduled. The result is stored in `scheduler.plan`, and `explain_plan()` turns it into text that lists each scheduled task and each skipped one.

`main.py` is a command-line demo of this flow, and `tests/test_pawpal.py` holds the tests (run with `python -m pytest`).

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting by priority | `Scheduler.sort_by_priority()` | High before medium before low; ties go to the earlier preferred time, then the shorter task |
| Sorting by time | `Scheduler.sort_by_time()` | Orders by preferred `HH:MM`; tasks with no time go last |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Limit to one pet, a status, or both; `None` means no filter |
| Time budget | `Scheduler.fits_in_time()` | Keeps tasks in order until the owner's minutes run out; skips one that doesn't fit so smaller ones can still use the time |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns about overlapping preferred-time windows |
| Recurring tasks | `Task.mark_complete()`, `Pet.complete_task()`, `Scheduler.mark_task_complete()` | Completing a daily or weekly task creates the next occurrence |

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

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
