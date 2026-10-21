# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

### Challenge 1: next available slot

**Files modified**

- `pawpal_system.py`: added `Scheduler.find_next_available_slot()`.
- `tests/test_pawpal.py`: added 5 tests (31 total).
- `main.py`: the demo now prints the next free 15, 45 and 120 minute slots.
- `app.py`: added a "Find a free time slot" expander under Today's Schedule.
- `README.md`: added the feature to the Features list and the Smarter Scheduling table.

**What task did you give the agent?**

Add a third algorithmic capability beyond sorting and conflict detection, and
document the work. The agent chose "next available slot": given a task length,
find the earliest time of day where it fits without overlapping a task that has
a preferred time.

**What did the agent do?**

- Added `find_next_available_slot(duration_minutes, earliest="07:00", latest="21:00", tasks=None)`.
  It sorts the timed tasks (the current plan by default) and sweeps forward
  from `earliest`. If the candidate window runs into a busy block it jumps to
  the end of that block. It returns an `HH:MM` string, or `None` if nothing
  fits before `latest`. Tasks with no preferred time take up no space, and bad
  input (zero length, malformed times) returns `None` instead of raising.
- Wrote tests for an empty day, skipping past a busy block, using a gap between
  two tasks, a full day, and bad input.
- Called the new method from the demo script and the Streamlit UI, and ran the
  full test suite (31 pass).

**What did you have to verify or fix manually?**

- The first version of the test helper gave the owner 600 available minutes, so
  the 840-minute task in the "day is full" test never entered the plan and the
  test failed. The helper's budget was raised to 2000 minutes. The scheduler
  code itself needed no change.
- <!-- Add anything you changed by hand here. -->

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
