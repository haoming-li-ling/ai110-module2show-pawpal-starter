from datetime import datetime
from pathlib import Path

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

DATA_FILE = Path(__file__).parent / "pawpal_data.json"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


def persist() -> None:
    """Save the owner to disk so data survives page reloads and restarts."""
    try:
        st.session_state.owner.save(DATA_FILE)
    except OSError as e:
        st.warning(f"Could not save your data: {e}")


def load_or_create_owner() -> Owner:
    """Load the saved owner, or start fresh if there is none or it is unreadable."""
    if DATA_FILE.exists():
        try:
            return Owner.load(DATA_FILE)
        except (OSError, ValueError, KeyError, TypeError):
            st.session_state.load_error = (
                f"{DATA_FILE.name} could not be read, so you are starting fresh."
            )
    return Owner(name="Jordan", available_minutes=90)


st.title("🐾 PawPal+")
st.caption("Plan your pets' care tasks for the day based on priority and the time you have.")

# Streamlit reruns this script on every interaction, so the Owner (and the
# pets and tasks inside it) lives in session_state to survive reruns, and is
# also written to DATA_FILE to survive reloads and restarts.
if "owner" not in st.session_state:
    st.session_state.owner = load_or_create_owner()
    st.session_state.owner_name = st.session_state.owner.name
    st.session_state.owner_minutes = st.session_state.owner.available_minutes
    st.session_state.show_plan = False
owner: Owner = st.session_state.owner

if "load_error" in st.session_state:
    st.warning(st.session_state.load_error)

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    st.text_input("Owner name", key="owner_name")
with col2:
    st.number_input(
        "Time available today (minutes)",
        min_value=1,
        max_value=1440,
        key="owner_minutes",
    )
owner.name = st.session_state.owner_name
owner.available_minutes = int(st.session_state.owner_minutes)

st.divider()

st.subheader("Pets")
with st.form("add_pet", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        new_pet_name = st.text_input("Pet name")
    with col2:
        new_species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        name = new_pet_name.strip()
        if not name:
            st.error("Please enter a pet name.")
        elif any(p.name.lower() == name.lower() for p in owner.pets):
            st.error(f"You already have a pet named {name}.")
        else:
            owner.add_pet(Pet(name=name, species=new_species))

if owner.pets:
    for i, pet in enumerate(owner.pets):
        col1, col2 = st.columns([5, 1])
        col1.write(f"**{pet.name}** ({pet.species}), {len(pet.tasks)} task(s)")
        if col2.button("Remove", key=f"remove_pet_{i}"):
            owner.remove_pet(pet)
            persist()
            st.rerun()

    with st.form("rename_pet", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            old_name = st.selectbox("Rename pet", [p.name for p in owner.pets])
        with col2:
            renamed = st.text_input("New name")
        if st.form_submit_button("Rename"):
            renamed = renamed.strip()
            if not renamed:
                st.error("Please enter a new name.")
            elif any(
                p.name.lower() == renamed.lower() and p.name != old_name
                for p in owner.pets
            ):
                st.error(f"You already have a pet named {renamed}.")
            else:
                next(p for p in owner.pets if p.name == old_name).rename(renamed)
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Tasks")
if owner.pets:
    with st.form("add_task", clear_on_submit=True):
        pet_name = st.selectbox("Pet", [p.name for p in owner.pets])
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
        with col1:
            title = st.text_input("Task title", placeholder="Morning walk")
        with col2:
            duration = st.number_input("Minutes", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["high", "medium", "low"])
        with col4:
            preferred = st.text_input("Preferred time", placeholder="HH:MM (optional)")
        with col5:
            recurrence = st.selectbox("Repeats", ["none", "daily", "weekly"])
        if st.form_submit_button("Add task"):
            preferred = preferred.strip()
            try:
                if preferred:
                    preferred = datetime.strptime(preferred, "%H:%M").strftime("%H:%M")
            except ValueError:
                st.error("Preferred time must look like 07:30.")
            else:
                if not title.strip():
                    st.error("Please enter a task title.")
                else:
                    pet = next(p for p in owner.pets if p.name == pet_name)
                    pet.add_task(
                        Task(
                            title=title.strip(),
                            duration_minutes=int(duration),
                            priority=priority,
                            preferred_time=preferred,
                            recurrence="" if recurrence == "none" else recurrence,
                        )
                    )

    if owner.get_all_tasks():
        fcol1, fcol2, fcol3 = st.columns(3)
        pet_filter = fcol1.selectbox("Show pet", ["All"] + [p.name for p in owner.pets])
        status_filter = fcol2.selectbox("Show status", ["All", "Pending", "Completed"])
        sort_choice = fcol3.selectbox("Sort by", ["Entered order", "Preferred time"])
        view = Scheduler(owner)
        shown = view.filter_tasks(
            pet_name=None if pet_filter == "All" else pet_filter,
            completed={"All": None, "Pending": False, "Completed": True}[status_filter],
        )
        if sort_choice == "Preferred time":
            shown = view.sort_by_time(shown)

        pending_shown = [t for t in shown if not t.completed]
        st.caption(
            f"Showing {len(shown)} task(s), {len(pending_shown)} pending, "
            f"{sum(t.duration_minutes for t in pending_shown)} min total."
        )
        # Warn right away if the pending tasks on screen overlap in time.
        conflicts = view.detect_conflicts(pending_shown)
        if conflicts:
            st.warning(
                f"{len(conflicts)} scheduling conflict(s) found. "
                "Consider changing a preferred time:\n\n"
                + "\n".join(f"- {c}" for c in conflicts)
            )
        elif pending_shown:
            st.success("No time conflicts among the pending tasks shown.")
        if not shown:
            st.info("No tasks match these filters.")

        widths = [2, 3, 1, 2, 2, 2, 2, 2]
        header = st.columns(widths)
        for col, label in zip(
            header, ["Pet", "Task", "Min", "Priority", "Preferred", "Repeats", "", ""]
        ):
            col.markdown(f"**{label}**")
        for task in shown:
            pet = next(p for p in owner.pets if p.name == task.pet_name)
            key = f"{pet.name}_{id(task)}"
            cols = st.columns(widths)
            cols[0].write(pet.name)
            cols[1].write(("~~" + task.title + "~~") if task.completed else task.title)
            cols[2].write(task.duration_minutes)
            cols[3].write(task.priority)
            cols[4].write(task.preferred_time or "--")
            cols[5].write(
                (task.recurrence or "--")
                + (f" (due {task.due_date})" if task.due_date else "")
            )
            if not task.completed and cols[6].button("Done", key=f"done_{key}"):
                Scheduler(owner).mark_task_complete(task)
                persist()
                st.rerun()
            if cols[7].button("Remove", key=f"remove_task_{key}"):
                pet.remove_task(task)
                persist()
                st.rerun()
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet first, then you can give it tasks.")

st.divider()

st.subheader("Today's Schedule")
if st.button("Generate schedule"):
    st.session_state.show_plan = True

# The plan is rebuilt from current data on every rerun while it is shown, so
# it never goes stale and doesn't disappear when you edit something else.
if st.session_state.show_plan:
    if not owner.get_all_tasks():
        st.warning("Add at least one task to build a schedule.")
    else:
        scheduler = Scheduler(owner)
        plan = scheduler.generate_daily_plan()
        used = sum(t.duration_minutes for t in plan)
        scheduled_ids = {id(t) for t in plan}
        skipped = [t for t in scheduler._due_pending() if id(t) not in scheduled_ids]

        def rows(tasks):
            return [
                {
                    "Preferred": t.preferred_time or "--",
                    "Task": t.title,
                    "Pet": t.pet_name,
                    "Minutes": t.duration_minutes,
                    "Priority": t.priority.capitalize(),
                }
                for t in tasks
            ]

        if plan:
            m1, m2, m3 = st.columns(3)
            m1.metric("Tasks scheduled", len(plan))
            m2.metric("Minutes used", f"{used} / {owner.available_minutes}")
            m3.metric("Skipped", len(skipped))

            st.markdown("**Plan by priority**")
            st.table(
                [{"#": i, **r} for i, r in enumerate(rows(plan), 1)]
            )
            if any(t.preferred_time for t in plan):
                st.markdown("**Same plan by preferred time**")
                st.table(rows(scheduler.sort_by_time(plan)))

            conflicts = scheduler.detect_conflicts()
            for warning in conflicts:
                st.warning(warning)
            if not conflicts:
                st.success("No time conflicts in today's plan.")
            if skipped:
                st.warning(
                    f"{len(skipped)} task(s) did not fit in the time available: "
                    + ", ".join(f"{t.title} ({t.pet_name})" for t in skipped)
                )
            else:
                st.success(
                    f"All due tasks fit: {used} of {owner.available_minutes} "
                    "minutes scheduled."
                )
        else:
            st.warning("No task fits in the time available.")
            if skipped:
                st.table(rows(skipped))
        with st.expander("Why this plan?", expanded=True):
            st.text(scheduler.explain_plan())

persist()
