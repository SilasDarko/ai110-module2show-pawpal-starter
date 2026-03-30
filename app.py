import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")


if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="My Household")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)


st.sidebar.title("🐾 PawPal+")
st.sidebar.subheader("Add a New Pet")

with st.sidebar:
    pet_name = st.text_input("Pet Name")
    pet_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
    if st.button("Add Pet"):
        if pet_name.strip():
            owner.add_pet(Pet(name=pet_name.strip(), species=pet_species))
            st.success(f"{pet_name} added!")
        else:
            st.warning("Please enter a pet name.")

    st.divider()

   
    st.subheader("Schedule a Task")
    pet_names = [p.name for p in owner.pets]

    if pet_names:
        selected_pet = st.selectbox("For which pet?", pet_names)
        task_desc = st.text_input("Task description")
        task_time = st.time_input("Time")
        task_freq = st.selectbox("Frequency", ["once", "daily", "weekly"])
        task_date = st.date_input("Due date", value=date.today())

        if st.button("Add Task"):
            if task_desc.strip():
                pet_obj = next(p for p in owner.pets if p.name == selected_pet)
                new_task = Task(
                    description=task_desc.strip(),
                    time=task_time.strftime("%H:%M"),
                    frequency=task_freq,
                    due_date=task_date
                )
                pet_obj.add_task(new_task)
                st.success(f"Task '{task_desc}' added for {selected_pet}!")
            else:
                st.warning("Please enter a task description.")
    else:
        st.info("Add a pet first to schedule tasks.")


st.title("🐾 PawPal+ Smart Pet Scheduler")

if not owner.pets:
    st.info("👈 Add a pet in the sidebar to get started!")
    st.stop()


conflicts = scheduler.detect_conflicts()
if conflicts:
    st.subheader("⚠️ Scheduling Conflicts")
    for c in conflicts:
        st.warning(c)


st.subheader("📅 Today's Schedule")

col1, col2, col3 = st.columns(3)
with col1:
    filter_pet = st.selectbox("Filter by pet", ["All"] + [p.name for p in owner.pets])
with col2:
    filter_status = st.selectbox("Filter by status", ["All", "Incomplete", "Complete"])
with col3:
    sort_mode = st.selectbox("Sort by", ["Time", "Pet Name"])


tasks = scheduler.sort_by_time()

if filter_pet != "All":
    tasks = [(n, t) for n, t in tasks if n == filter_pet]
if filter_status == "Incomplete":
    tasks = [(n, t) for n, t in tasks if not t.completed]
elif filter_status == "Complete":
    tasks = [(n, t) for n, t in tasks if t.completed]
if sort_mode == "Pet Name":
    tasks = sorted(tasks, key=lambda x: x[0])


if not tasks:
    st.info("No tasks match your filters.")
else:
    for i, (pet_name, task) in enumerate(tasks):
        col_status, col_info, col_action = st.columns([1, 6, 2])

        with col_status:
            if task.completed:
                st.markdown("✅")
            else:
                st.markdown("⬜")

        with col_info:
            freq_badge = f"`{task.frequency}`" if task.frequency != "once" else ""
            st.markdown(
                f"**{task.time}** — {task.description} &nbsp;&nbsp;"
                f"🐾 *{pet_name}* &nbsp;&nbsp; {freq_badge}"
            )

        with col_action:
            if not task.completed:
                btn_key = f"complete_{pet_name}_{i}_{task.description}"
                if st.button("Mark done", key=btn_key):
                    scheduler.handle_recurrence(pet_name, task)
                    st.rerun()


st.divider()
st.subheader("🐶 Your Pets")

cols = st.columns(max(len(owner.pets), 1))
for col, pet in zip(cols, owner.pets):
    total = len(pet.tasks)
    done = sum(1 for t in pet.tasks if t.completed)
    with col:
        st.metric(label=f"{pet.name} ({pet.species})", value=f"{done}/{total} done")