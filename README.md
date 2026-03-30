🐾 PawPal+ — Smart Pet Care Management System

- PawPal+ helps pet owners manage daily routines for their furry friends — feedings, walks, medications, and appointments — using algorithmic scheduling logic and a clean Streamlit UI.

🚀 Getting Started
Prerequisites
bash
pip install streamlit pytest
Run the App
bash
streamlit run app.py
Run the CLI Demo
bash
python main.py

✨ Features
Add Pets & Tasks — Register multiple pets and schedule tasks with time, frequency, and due date
Sorting by Time — Tasks are automatically sorted chronologically using Python's sorted() with a lambda key
Filtering — View tasks by pet name or completion status
Conflict Detection — The Scheduler warns you when two tasks are scheduled at the same time
Recurring Tasks — Daily and weekly tasks automatically reschedule when marked complete using timedelta
Persistent UI State — Streamlit session_state keeps your data alive across interactions

🏗️ System Architecture
Class	Responsibility
Task	Single care activity with time, frequency, and completion state
Pet	Holds pet info and a list of Tasks
Owner	Manages multiple Pets and aggregates their tasks
Scheduler	Sorting, filtering, conflict detection, and recurrence logic

🧪 Testing PawPal+
bash
python -m pytest
The test suite covers:

Task completion toggling
Task count after additions
Chronological sort correctness
Conflict detection (same-time tasks)
Daily and weekly recurrence logic
Edge cases (no tasks, unique times, one-time tasks)
Confidence Level: All core behaviors are verified with dedicated tests and edge cases.


🤖 Smarter Scheduling
PawPal+'s Scheduler class goes beyond a simple task list:

Time-based sorting keeps your day organized automatically
Conflict warnings surface scheduling problems before they cause missed care
Recurrence automation removes the need to manually re-add repeating tasks
All logic lives in pawpal_system.py — fully testable and UI-independent
