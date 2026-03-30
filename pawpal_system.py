from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


@dataclass
class Task:
    """Represents a single pet care activity."""
    description: str
    time: str                        
    frequency: str = "once"          
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    """Represents a pet with its own list of care tasks."""
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks




@dataclass
class Owner:
    """Represents a pet owner who manages multiple pets."""
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's roster."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[tuple]:
        """Return all tasks across all pets as (pet_name, task) tuples."""
        all_tasks = []
        for pet in self.pets:
            for task in pet.get_tasks():
                all_tasks.append((pet.name, task))
        return all_tasks




class Scheduler:
    """The brain of PawPal+. Organizes, filters, and validates tasks."""

    def __init__(self, owner: Owner):
        """Initialize the scheduler with an owner instance."""
        self.owner = owner

    def sort_by_time(self) -> List[tuple]:
        """Return all tasks sorted chronologically by time (HH:MM)."""
        tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda x: x[1].time)

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None
    ) -> List[tuple]:
        """Filter tasks by pet name and/or completion status."""
        tasks = self.owner.get_all_tasks()
        if pet_name:
            tasks = [(n, t) for n, t in tasks if n == pet_name]
        if completed is not None:
            tasks = [(n, t) for n, t in tasks if t.completed == completed]
        return tasks

    def detect_conflicts(self) -> List[str]:
        """
        Detect tasks scheduled at the same time.
        Returns a list of warning strings for any conflicts found.
        """
        warnings = []
        tasks = self.owner.get_all_tasks()
        seen = {}
        for pet_name, task in tasks:
            key = task.time
            if key in seen:
                prev_pet, prev_task = seen[key]
                warnings.append(
                    f"⚠️ Conflict at {task.time}: "
                    f"'{prev_task.description}' ({prev_pet}) vs "
                    f"'{task.description}' ({pet_name})"
                )
            else:
                seen[key] = (pet_name, task)
        return warnings

    def handle_recurrence(self, pet_name: str, task: Task):
        """
        When a recurring task is completed, schedule the next occurrence.
        Adds a new Task to the correct pet's list.
        """
        task.mark_complete()
        if task.frequency == "daily":
            next_date = task.due_date + timedelta(days=1)
        elif task.frequency == "weekly":
            next_date = task.due_date + timedelta(weeks=1)
        else:
            return  

        new_task = Task(
            description=task.description,
            time=task.time,
            frequency=task.frequency,
            due_date=next_date
        )
        for pet in self.owner.pets:
            if pet.name == pet_name:
                pet.add_task(new_task)
                break