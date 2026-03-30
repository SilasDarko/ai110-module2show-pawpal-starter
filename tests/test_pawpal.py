import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler



@pytest.fixture
def sample_owner():
    """Create a fully wired Owner → Pet → Task structure for testing."""
    owner = Owner(name="TestOwner")
    dog = Pet(name="Rex", species="Dog")
    cat = Pet(name="Luna", species="Cat")

    dog.add_task(Task("Evening walk",    time="18:00", frequency="daily"))
    dog.add_task(Task("Morning walk",    time="07:00", frequency="daily"))
    dog.add_task(Task("Flea treatment",  time="09:00", frequency="weekly"))

    cat.add_task(Task("Feeding",         time="08:00", frequency="daily"))
    cat.add_task(Task("Vet checkup",     time="18:00", frequency="once"))  

    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner




def test_task_completion():
    """mark_complete() should set completed to True."""
    task = Task(description="Feed cat", time="08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_defaults():
    """Task should default to frequency='once' and completed=False."""
    task = Task(description="Walk dog", time="09:00")
    assert task.frequency == "once"
    assert task.completed is False




def test_add_task_increases_count():
    """Adding a task should increase the pet's task count by 1."""
    pet = Pet(name="Buddy", species="Dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Walk", time="08:00"))
    assert len(pet.get_tasks()) == 1
    pet.add_task(Task("Feed", time="09:00"))
    assert len(pet.get_tasks()) == 2


def test_pet_with_no_tasks():
    """A new pet should have an empty task list."""
    pet = Pet(name="Ghost", species="Cat")
    assert pet.get_tasks() == []




def test_sort_by_time(sample_owner):
    """Tasks should be returned in chronological HH:MM order."""
    scheduler = Scheduler(sample_owner)
    sorted_tasks = scheduler.sort_by_time()
    times = [task.time for _, task in sorted_tasks]
    assert times == sorted(times), "Tasks are not in chronological order"


def test_sort_handles_single_task():
    """Sorting with a single task should not raise an error."""
    owner = Owner(name="Solo")
    pet = Pet(name="Pip", species="Bird")
    pet.add_task(Task("Seed refill", time="10:00"))
    owner.add_pet(pet)
    result = Scheduler(owner).sort_by_time()
    assert len(result) == 1




def test_filter_by_pet_name(sample_owner):
    """Filtering by pet name should return only that pet's tasks."""
    scheduler = Scheduler(sample_owner)
    rex_tasks = scheduler.filter_tasks(pet_name="Rex")
    assert all(name == "Rex" for name, _ in rex_tasks)


def test_filter_by_completion(sample_owner):
    """Filtering by completed=False should return only incomplete tasks."""
    scheduler = Scheduler(sample_owner)
    # Mark one task complete
    sample_owner.pets[0].tasks[0].mark_complete()
    incomplete = scheduler.filter_tasks(completed=False)
    assert all(not task.completed for _, task in incomplete)




def test_detect_conflicts(sample_owner):
    """Scheduler should detect tasks at the same time (18:00 overlap)."""
    scheduler = Scheduler(sample_owner)
    warnings = scheduler.detect_conflicts()
    assert len(warnings) >= 1
    assert any("18:00" in w for w in warnings)


def test_no_conflicts_when_unique_times():
    """No conflicts should be reported when all task times are unique."""
    owner = Owner(name="CleanOwner")
    pet = Pet(name="Milo", species="Dog")
    pet.add_task(Task("Walk",    time="07:00"))
    pet.add_task(Task("Feed",    time="08:00"))
    pet.add_task(Task("Meds",    time="09:00"))
    owner.add_pet(pet)
    warnings = Scheduler(owner).detect_conflicts()
    assert warnings == []




def test_daily_recurrence_creates_new_task():
    """Completing a daily task should create a new task for the next day."""
    owner = Owner(name="RecurOwner")
    pet = Pet(name="Daisy", species="Dog")
    today = date.today()
    task = Task("Morning walk", time="07:00", frequency="daily", due_date=today)
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.handle_recurrence("Daisy", task)

    assert task.completed is True
    assert len(pet.tasks) == 2
    new_task = pet.tasks[-1]
    assert new_task.due_date == today + timedelta(days=1)
    assert new_task.completed is False


def test_weekly_recurrence_creates_new_task():
    """Completing a weekly task should create a new task 7 days later."""
    owner = Owner(name="WeeklyOwner")
    pet = Pet(name="Max", species="Dog")
    today = date.today()
    task = Task("Flea treatment", time="09:00", frequency="weekly", due_date=today)
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.handle_recurrence("Max", task)

    new_task = pet.tasks[-1]
    assert new_task.due_date == today + timedelta(weeks=1)


def test_once_task_does_not_recur():
    """A 'once' frequency task should not create a new task when completed."""
    owner = Owner(name="OnceOwner")
    pet = Pet(name="Zoe", species="Cat")
    task = Task("Vet visit", time="14:00", frequency="once")
    pet.add_task(task)
    owner.add_pet(pet)

    Scheduler(owner).handle_recurrence("Zoe", task)
    assert len(pet.tasks) == 1  