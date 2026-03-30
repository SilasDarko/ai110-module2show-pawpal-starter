from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(title: str, tasks: list):
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")
    if not tasks:
        print("  (no tasks found)")
    for pet_name, task in tasks:
        status = "✅" if task.completed else "⬜"
        recur = f"[{task.frequency}]" if task.frequency != "once" else ""
        print(f"  {status} {task.time}  {pet_name:<10} {task.description} {recur}")
    print(f"{'─' * 50}")


def main():
    owner = Owner(name="Alex")

    buddy = Pet(name="Buddy", species="Dog")
    whiskers = Pet(name="Whiskers", species="Cat")

    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    buddy.add_task(Task("Evening walk",      time="18:00", frequency="daily"))
    buddy.add_task(Task("Morning walk",      time="07:30", frequency="daily"))
    buddy.add_task(Task("Flea medication",   time="09:00", frequency="weekly"))
    buddy.add_task(Task("Breakfast feeding", time="07:30", frequency="daily"))  

    whiskers.add_task(Task("Breakfast feeding", time="08:00", frequency="daily"))
    whiskers.add_task(Task("Vet appointment",   time="14:00", frequency="once"))
    whiskers.add_task(Task("Evening feeding",   time="18:00", frequency="daily"))

    scheduler = Scheduler(owner)

    print_schedule("📅 TODAY'S FULL SCHEDULE (sorted by time)",
                   scheduler.sort_by_time())

    print_schedule("🐶 BUDDY'S TASKS ONLY",
                   scheduler.filter_tasks(pet_name="Buddy"))

    print_schedule("⬜ INCOMPLETE TASKS",
                   scheduler.filter_tasks(completed=False))

    print("\n🔍 Checking for scheduling conflicts...")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts found!")

    print("\n🔁 Marking Buddy's morning walk complete (daily recurrence)...")
    morning_walk = buddy.tasks[1]  
    scheduler.handle_recurrence("Buddy", morning_walk)
    print(f"  '{morning_walk.description}' marked complete.")
    print(f"  New task created for: {buddy.tasks[-1].due_date}")

    print_schedule("📅 UPDATED SCHEDULE (after recurrence)",
                   scheduler.sort_by_time())


if __name__ == "__main__":
    main()