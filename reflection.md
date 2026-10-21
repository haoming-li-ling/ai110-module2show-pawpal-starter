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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

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

The tests are still thin. They cover simple state changes, not the sorting or time-fitting logic, so the scheduler's behavior is only verified by the demo run so far.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
