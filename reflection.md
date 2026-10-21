# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions a user should be able to perform:

1. **Add a pet (and owner info).** The user enters basic details about themselves and their pet, such as the pet's name and species, so the system knows who the care tasks are for.
2. **Schedule a care task.** The user adds a task for a pet, such as a walk, feeding, or medication. Each task has a duration and a priority, and can have a preferred time.
3. **See today's tasks.** The user generates and views a daily plan. The plan orders the tasks by priority and fits them into the time available. It also explains why each task was placed where it was.

My initial UML has four classes:

- **Owner:** holds the owner's name, the minutes available per day, and their list of pets. It adds and removes pets and can gather every task across all pets.
- **Pet:** holds the pet's name, species, and its own list of tasks. It adds and removes tasks and returns the ones not yet completed.
- **Task:** holds one care activity: title, duration, priority, preferred time, and a completed flag. It can mark itself complete.
- **Scheduler:** takes an Owner and builds the daily plan. It sorts tasks by priority, keeps only the ones that fit in the owner's available time, and explains why the plan looks the way it does.

An Owner has many Pets, and a Pet has many Tasks. The Scheduler depends on one Owner. I kept data in Owner, Pet and Task, which are dataclasses. I kept all scheduling decisions in the Scheduler.

**b. Design changes**

Yes. While reviewing the class skeleton against the UML, I made two changes:

- **Added `plan` to Scheduler.** `explain_plan()` had nothing to explain, because `generate_daily_plan()` only returned a list and kept no state. The Scheduler now stores the latest plan in `self.plan`.
- **Added `pet_name` to Task.** Once tasks from all pets are merged into one plan, a Task had no way to say which pet it belonged to. The plan couldn't show "walk Mochi", for example. `pet_name` fixes that without giving Task a reference back to Pet.

The UML draft was updated to match.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers five constraints, in this order of importance:

1. **Eligibility (completed and due date).** Completed tasks and tasks whose `due_date` is in the future are never planned (`_due_pending`).
2. **Time budget.** `fits_in_time` keeps tasks, in order, only while they fit in the owner's `available_minutes`. A task that doesn't fit is skipped, and smaller ones after it can still use the leftover time.
3. **Priority.** `sort_by_priority` orders tasks high, then medium, then low, so priority decides which tasks get the limited time first.
4. **Preferred time.** This only breaks ties between tasks of equal priority (earlier first, tasks with no time last). It is also used by `detect_conflicts` to warn about overlapping windows, but it never moves or removes a task.
5. **Duration.** This is the last tiebreaker, so a shorter task goes before a longer one of the same priority and time.

I ranked them by what goes wrong if they are ignored. Planning a done or not-yet-due task is simply wrong, so eligibility comes first. Going over the owner's available time makes the plan unusable, so the time budget is a hard limit. Within that limit, priority matters most because a skipped medication is worse than a skipped play session. Preferred times are wishes rather than appointments, and the owner usually has a few minutes of flexibility, so they only order and warn. Duration is a minor tiebreaker that fits more tasks into the day.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler chooses tasks by priority and the owner's time budget, and only
*warns* about time conflicts instead of resolving them. `generate_daily_plan`
picks tasks greedily (high priority first) until the minutes run out. It treats
`preferred_time` as a tiebreaker, not a fixed slot. `detect_conflicts` then
checks the chosen tasks and reports any whose preferred windows overlap, such
as a 07:30 walk (30 min) and a 07:45 breakfast. Both tasks stay in the plan.

What this costs: the plan is not a real timeline. Two tasks can be scheduled
for overlapping times, and the owner has to fix that by hand. A skipped task
never triggers a conflict, and tasks without a preferred time are ignored.
Greedy selection can also miss the best combination of tasks that fits in the
time, though it never skips a high-priority task for a lower-priority one that
would fit.

Why it is reasonable: preferred times are wishes, not appointments. Silently
moving or dropping a task to remove a clash could break something that matters,
like medication, and the owner knows which task can give way. A warning keeps
the owner in control. The algorithm stays simple and easy to explain in the
"Why this plan?" text, and detection is cheap (sorting plus an early-exit
scan). Automatic resolution, or searching for the best set of tasks that fits,
would be harder to explain and test, and not worth it for a few tasks a day.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code for the whole workflow: identifying the three core user actions, drafting the UML, generating the class skeleton, implementing the methods, writing the demo script and tests, and drafting documentation. The most helpful prompts were specific and sequential, with one artifact each: "generate UML with these four classes", then "create the skeleton from the UML", then "implement the classes". Each step built on a file the AI had already produced, which made the results easy to check against the previous step.

What the AI suggested, and what happened to it:

- **Accepted:** the four-class structure, with dataclasses for `Task`, `Pet` and `Owner` and a plain class for `Scheduler`. I accepted it because the data classes only hold data and all the scheduling behavior sits in one place.
- **Accepted:** a greedy scheduling approach: sort by priority, then keep tasks while they fit in the time budget.
- **Not adopted:** the AI left `priority` as a plain string instead of an enum. I kept that for now to keep the design simple. The cost is that a typo like `"hgih"` silently sorts last.
- **Not adopted:** the AI treats `preferred_time` only as a tie-breaker, not as a fixed slot on a clock, so the plan is an ordered list rather than a timetable.

**b. Judgment and verification**

I did not accept the first skeleton as-is. When I reviewed it against the UML, I saw two gaps that would have made the methods impossible to implement properly. `explain_plan()` had no stored plan to explain, and a `Task` could not say which pet it belonged to once tasks from all pets were merged. I added `Scheduler.plan` and `Task.pet_name`, then updated the UML to match (see 1b).

To verify the AI's work I did not rely on its description of what the code does:

- I ran `main.py` with two pets and five tasks, including one already completed and one too long to fit. I checked that the output order and the "Skipped" line matched what I expected from the rules.
- I wrote tests for task completion and for adding a task to a pet, and ran them with `python -m pytest`. Both pass.
- I checked that the UML, the skeleton and the implementation agree with each other.

At that stage the tests were still thin: they covered simple state changes, not the sorting or time-fitting logic, so the scheduler was only verified by the demo run. I later expanded them to 26 tests covering sorting, recurrence, conflict detection and planning (see section 4).

**c. AI strategy**

*Most effective features.* Three things worked best for building the scheduler:

- **Working from files the AI had already produced.** Generating the UML, then the skeleton from the UML, then the implementation from the skeleton meant every step could be checked against the one before it. That is how I caught the missing `plan` and `pet_name`.
- **Having the AI run the code.** Running `main.py` and `pytest` and reading real output was more reliable than reading the AI's description of what the code should do. The same habit caught problems later, such as a README sample output that no longer matched what `main.py` printed.
- **Applying one feature across several files at once.** When I added recurring tasks, sorting, filtering and conflict detection, the AI could update `pawpal_system.py`, `app.py`, `main.py`, the tests and the README together. I then reviewed the diff instead of typing each change myself.

*A suggestion I modified.* After the first skeleton, `Task` had no way to say which pet it belonged to once all tasks were merged into one plan. The obvious fix was to give `Task` a reference back to its `Pet`. I rejected that and added a plain `pet_name` string, which `Pet.add_task()` and `Pet.rename()` keep in sync. A back-reference would have made `Pet` and `Task` depend on each other, complicated JSON saving and loading, and made `Task` harder to test on its own. I also kept `priority` as a plain string rather than an enum, to keep the design small, and accepted the tradeoff that a typo sorts last.

*Separate chat sessions.* I kept each phase in its own session: design and UML, implementation, then the UI and documentation. Each session started with only the files that mattered, so it was not carrying earlier discussion that no longer applied, and an idea from one phase couldn't quietly overwrite a decision from another. When I came back to a phase, `reflection.md`, the UML and the commit history were enough to pick up where I left off. Splitting the work this way also gave me natural points to commit and to check that the code, the UML and the README still agreed.

*Being the lead architect.* The AI can write a lot of working code quickly, so my job was deciding what the system should be and checking that it stayed that way. I set the boundaries (data in `Owner`, `Pet` and `Task`; decisions in `Scheduler`) and I decided that conflicts should produce warnings rather than silent changes to the plan. What I learned is that the AI's first answer is usually plausible but not always right for my design. It works best when I give small, specific requests, review every diff against the UML, and verify with tests and real output. The speed only helps if I stay the person who decides what gets kept.

---

## 4. Testing and Verification

**a. What you tested**

I wrote 26 tests in `tests/test_pawpal.py`, grouped by behavior:

- **Sorting:** `sort_by_time` returns chronological order for unsorted input, puts tasks with no time last, and doesn't mutate its input. `sort_by_priority` orders high to low and breaks ties by time.
- **Recurrence:** completing a daily or weekly task creates the next occurrence on the right date, including across a month boundary and when the task has no due date. The copy keeps the original's details and starts out pending. Non-recurring tasks create nothing, and completing a task twice doesn't create a duplicate.
- **Conflict detection:** overlapping and duplicate times are flagged, both for one pet and across pets. Back-to-back tasks, tasks with no time, malformed times and empty input are not flagged.
- **Planning:** the plan stays within the time budget, skips completed and future-dated tasks, and is empty for an owner with no pets.
- **Basics:** marking a task complete, adding a task to a pet, renaming a pet, filtering by pet and status, and saving and loading JSON.

These mattered because the scheduler's rules are easy to get subtly wrong. The most likely mistakes are off-by-one overlap checks, a recurring task creating duplicates, and a bad date calculation at the end of a month. A plain demo run would not reveal any of these.

**b. Confidence**

I am fairly confident, about 4 out of 5. All 26 tests pass and they cover the core rules and their edge cases. I'm not at 5 because the Streamlit UI in `app.py` has no tests, and I only checked it by looking at it.

With more time I would test these next:

- **Same time conflicts:** two tasks with the same start time and one of them has zero duration, and a task that runs past midnight.
- **Invalid priority values:** a typo like `"hgih"` currently sorts last without any error.
- **Time budget edge cases:** a task that exactly equals the remaining time, and an owner with 0 minutes available.
- **Persistence:** loading a corrupted or partly missing `pawpal_data.json`.
- **Recurrence and duplicates:** completing a weekly task on a day other than its due date, and renaming a pet to a name an existing pet already has.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with how the scheduler is split up. The data classes only hold data, and every planning decision lives in `Scheduler`, so each rule can be tested on its own. Conflict warnings that never change the plan also worked out well, because the owner stays in control and the "Why this plan?" text stays easy to explain.

**b. What you would improve**

I would make three changes:

- Replace the `priority` and `recurrence` strings with enums, so a typo raises an error instead of silently sorting last.
- Turn the plan into a real timeline. Right now `preferred_time` is only a tiebreaker, so two tasks can overlap and the owner has to fix that by hand. I would assign actual start times and move tasks to avoid overlaps where possible.
- Add a public `Scheduler` method for the tasks that were skipped, so `app.py` doesn't call the private `_due_pending()`. I would also add tests for the UI logic.

**c. Key takeaway**

Design first, then check the AI's work against that design. Writing the UML and class responsibilities before any code made it easy to see when generated code drifted, such as a `Task` that couldn't say which pet it belonged to. AI can produce a lot of working code quickly, but it doesn't know which decisions matter to me, like warning about conflicts instead of silently rearranging tasks. Those decisions, and verifying the results with tests and real output, are my job.
