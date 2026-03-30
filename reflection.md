# PawPal+ Project Reflection

## 1. System Design
Three Core User Actions

- Add a pet: Register a named pet (with species) to the owner's profile
- Schedule a task: Assign a care activity (description, time, frequency) to a specific pet
- View today's schedule: See all tasks sorted by time, with filters for pet and completion status

**a. Initial design**
The system uses four classes with clearly separated responsibilities:

- Task is a Python dataclass representing a single care activity. It holds the what (description), when (time, due_date), how often (frequency), and whether it's done (completed). Keeping Task as a dataclass keeps it lightweight and easy to test.
- Pet is also a dataclass that groups a pet's identity (name, species) with its task list. It exposes simple add_task and get_tasks methods so the rest of the system never manipulates its list directly.
- Owner aggregates multiple pets and provides a single get_all_tasks() method that returns every task across every pet as (pet_name, task) tuples. This tuple design makes filtering and display straightforward without coupling pets to tasks at a data level.
- Scheduler is the only non-dataclass — it takes an Owner and provides all the intelligent behavior: sorting, filtering, conflict detection, and recurrence. Separating this logic into its own class means the other three classes stay simple and the Scheduler can be tested independently.

**b. Design changes**
After reviewing the initial skeleton, one change was made: get_all_tasks() was updated to return (pet_name, task) tuples instead of flat Task objects. This was necessary because the Scheduler needs to know which pet a task belongs to for filtering and conflict warnings. Without the pet name attached, every downstream method would have needed to re-trace the Owner → Pet → Task chain

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- Sorting uses Python's built-in sorted() with key=lambda x: x[1].time. Since times are stored in "HH:MM" string format, lexicographic sorting produces correct chronological order without parsing.
Filtering chains list comprehensions: first by pet name, then by completion status. This is readable and efficient for the small datasets typical of a household pet app.
Conflict detection uses a dictionary keyed by time string. The first task at a given time is stored; any subsequent task at the same time triggers a warning. This is O(n) and avoids nested loops.
Recurrence creates a brand-new Task dataclass instance with an incremented due_date using timedelta. This avoids mutating completed tasks and keeps history intact.



**b. Tradeoffs**

The conflict detection only flags exact time matches (e.g., both at "09:00"). It does not detect overlapping durations — for example, a 30-minute walk starting at "08:45" and a feeding at "09:00" would not be flagged. This is a deliberate simplification: tasks in PawPal+ don't have a duration field, so overlap detection isn't possible without a larger redesign. For a household scheduling app, exact-match conflicts are the most common and most actionable case.

---

## 3. AI Collaboration

**a. How you used AI**

AI tools were used at every stage of this project, but in different ways depending on the phase:

- Design brainstorming (Phase 1): I described the pet care scenario to Copilot and asked it to generate a Mermaid.js class diagram from my brainstormed attributes and methods. This was useful for quickly visualizing relationships between classes before writing any code.
- Scaffolding (Phase 2): I used Agent Mode with #file:pawpal_system.py to flesh out method bodies from the skeleton. Giving the AI direct file context produced much more relevant output than describing the code in plain text.
- Debugging and formatting (Phase 2): When main.py printed raw object representations, I used Inline Chat on the print statement and asked for a more readable terminal format. This was faster than figuring out __repr__ manually.
- Test generation (Phase 5): I used the Generate Tests smart action to draft the initial test functions, then reviewed each one to make sure it was testing real behavior and not just passing trivially.

The most helpful prompts were specific and file-referenced — for example: "Based on my skeletons in #file:pawpal_system.py, how should the Scheduler retrieve all tasks from the Owner's pets?" Vague prompts like "help me with scheduling" produced generic, unusable output.

**b. Judgment and verification**

- When generating get_all_tasks(), Copilot initially returned a flat list of Task objects with no pet name attached. I did not accept this because it would have broken every downstream method, the Scheduler needs to know which pet owns each task to filter by pet name and to generate meaningful conflict warnings.
- I evaluated the suggestion by mentally tracing it through filter_tasks(): if I only have a Task, I can't check pet_name == "Buddy" without re-searching the Owner's pet list on every call. Switching to (pet_name, task) tuples solved this in one place and made every other method simpler. I verified the fix by running main.py and confirming that pet names appeared correctly in the sorted and filtered output.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers these core behaviors:

- Task completion — that mark_complete() actually flips completed to True
- Task addition — that adding a task increases the pet's task count
- Sorting correctness — that sort_by_time() returns tasks in true chronological order
- Conflict detection — that the Scheduler flags two tasks at the same time, and stays silent when all times are unique
- Daily recurrence — that completing a daily task creates a new task dated tomorrow with completed=False
- Weekly recurrence — that the new task is dated 7 days later
- One-time tasks — that a "once" task does not create a new task when completed
- Edge cases — a pet with no tasks, a scheduler with only one task

- These tests matter because the scheduling logic is the core value of the app. If sorting is wrong, users see tasks out of order. If recurrence is wrong, tasks silently disappear after being marked done. If conflict detection has a false negative, a pet could miss a feeding or medication without any warning.

**b. Confidence**

The happy paths and the most important edge cases are all covered and passing. One star is withheld because the conflict detection only catches exact time matches, it doesn't handle overlapping durations, and there are no tests for what happens when two pets share the same name or when a task's due_date is in the past. Given more time, the next edge cases to test would be:

Two tasks at "09:00" and "09:01" — should these conflict if tasks have a 30-minute duration?
An owner with zero pets — does sort_by_time() return an empty list gracefully?
A due_date of yesterday — does recurrence produce sensible future dates?
Very large task lists — does sorting performance stay acceptable?

---

## 5. Reflection

**a. What went well**

The cleanest decision in this project was keeping all logic in pawpal_system.py and treating app.py purely as a display layer. Because of this separation, every algorithm could be developed and verified in the terminal through main.py before the UI existed at all. When bugs appeared, it was immediately obvious whether the problem was in the logic layer or the UI layer, there was no ambiguity. This made debugging significantly faster.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
If given another iteration, I would add a duration_minutes field to Task. The current conflict detection is limited to exact time matches because tasks have no length. With duration, the Scheduler could detect real overlaps (e.g., a 45-minute walk starting at 8:00 conflicts with a feeding at 8:30) and the UI could render a proper timeline view instead of a flat list. I would also add data persistence, right now all pets and tasks are lost when the Streamlit app restarts, which makes it impractical for real use.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
The most important thing I learned is that AI is a fast and capable executor but a poor architect. It can generate syntactically correct, plausible-looking code very quickly, but it has no awareness of your system's design intent, the tradeoffs you've already made, or how a change in one class ripples into another. The moment I stopped reviewing AI suggestions against the UML diagram and just accepted what looked reasonable, the design started to drift. The human's role isn't to write every line, it's to hold the blueprint and decide what belongs in the system and what doesn't.