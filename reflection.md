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

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
