from formatting import priority_badge, schedule_table, status_icon, task_emoji
from pawpal_system import Task


def test_task_emoji_matches_keywords_and_falls_back():
    assert task_emoji(Task("Morning walk", 10, "high")) == "🦮"
    assert task_emoji(Task("Give medication", 5, "high")) == "💊"
    assert task_emoji(Task("Cuddle time", 5, "low")) == "🐾"


def test_status_icon_and_priority_badge():
    task = Task("Walk", 10, "high")
    assert status_icon(task) == "⏳"
    task.mark_complete()
    assert status_icon(task) == "✅"
    assert priority_badge("medium") == "🟡 Medium"


def test_schedule_table_has_header_and_a_row_per_task():
    tasks = [Task("Walk", 10, "high", preferred_time="07:00", pet_name="Mochi")]
    table = schedule_table(tasks)
    assert "Priority" in table and "Walk" in table and "Mochi" in table
    assert len(table.splitlines()) == 3  # header, rule, one row
