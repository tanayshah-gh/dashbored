import streamlit as st
import datetime

# 1. Page Header & Date
today_str = datetime.date.today().strftime("%A, %d %B %Y")
st.title("work")
st.caption(f"**{today_str}**")

st.divider()

# 2. Initialize Session State
if "today_tasks" not in st.session_state:
    st.session_state.today_tasks = [
        {"id": 1, "text": "Complete 2 LeetCode / DSA problems in C", "done": False},
        {"id": 2, "text": "Review AIML lecture slides & notes", "done": False},
        {"id": 3, "text": "Log today's daily expenses in Dashy", "done": False},
    ]

if "deadlines" not in st.session_state:
    st.session_state.deadlines = [
        {"Task": "DSA Lab Assignment 3", "Subject": "Data Structures", "Due": "In 2 Days", "Status": "🟡 pending"},
        {"Task": "AIML Model Evaluation Practical", "Subject": "Machine Learning", "Due": "Friday", "Status": "🔵 in prog"},
        {"Task": "Bastion DB Migration Check", "Subject": "Personal Dev", "Due": "Sunday", "Status": "🟢 done"},
    ]

if "quick_notes" not in st.session_state:
    st.session_state.quick_notes = []

# ==================== SECTION 1: TODAY'S FOCUS ====================
h_col1, h_col2 = st.columns([6, 1])
with h_col1:
    st.subheader("Today")
with h_col2:
    with st.popover("Add"):
        new_task_text = st.text_input("New Focus Item", placeholder="e.g., Debug parser")
        if st.button("Add Task", use_container_width=True, key="add_focus_btn"):
            if new_task_text.strip():
                st.session_state.today_tasks.append({
                    "id": len(st.session_state.today_tasks) + 1,
                    "text": new_task_text.strip(),
                    "done": False
                })
                st.rerun()

st.caption("quick focus")

# Auto-sort: pending tasks at the top, completed items at the bottom
st.session_state.today_tasks.sort(key=lambda x: x["done"])

if not st.session_state.today_tasks:
    st.info("No tasks left for today!")
else:
    for idx, task in enumerate(st.session_state.today_tasks):
        t_col1, t_col2 = st.columns([11, 1])
        with t_col1:
            label = f"~{task['text']}~" if task["done"] else task["text"]
            is_done = st.checkbox(
                label,
                value=task["done"],
                key=f"task_chk_{task['id']}"
            )
            if is_done != task["done"]:
                task["done"] = is_done
                st.rerun()

        with t_col2:
            if st.button("✕", key=f"del_task_{task['id']}", help="Delete task"):
                st.session_state.today_tasks.pop(idx)
                st.rerun()

st.divider()

# ==================== SECTION 2: DEADLINES ====================
d_col1, d_col2 = st.columns([6, 1])
with d_col1:
    st.subheader("Deadlines")
with d_col2:
    with st.popover("Add"):
        new_title = st.text_input("Assignment / Task", placeholder="e.g., C Pointers Lab")
        new_subject = st.text_input("Subject", placeholder="e.g., DSA / AIML")
        new_due = st.text_input("Due Date", placeholder="e.g., Friday or 28 Aug")
        new_status = st.selectbox("Status", ["🟡 pending", "🔵 in prog", "🟢 done"])
        if st.button("Add Deadline", use_container_width=True, key="add_deadline_btn"):
            if new_title.strip():
                st.session_state.deadlines.append({
                    "Task": new_title.strip(),
                    "Subject": new_subject.strip() if new_subject.strip() else "General",
                    "Due": new_due.strip() if new_due.strip() else "TBD",
                    "Status": new_status
                })
                st.rerun()

if st.session_state.deadlines:
    updated_deadlines = st.data_editor(
        st.session_state.deadlines,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                help="Update task progress",
                options=["🟡 pending", "🔵 in prog", "🟢 done"],
                required=True,
            )
        },
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key="deadlines_editor"
    )
    st.session_state.deadlines = updated_deadlines

    if st.button("Clear Finished Deadlines", key="clear_deadlines"):
        st.session_state.deadlines = [d for d in st.session_state.deadlines if "Ready" not in d["Status"]]
        st.rerun()
else:
    st.info("No upcoming deadlines.")

st.divider()

# ==================== SECTION 3: QUICK CAPTURE ====================
st.subheader("Quick Capture")
quick_note = st.text_area(
    "",
    placeholder="e.g., paid by cash, owe money etc...",
    height=100
)
if st.button("Save", use_container_width=True):
    if quick_note.strip():
        st.session_state.quick_notes.append(f"• {quick_note.strip()}")
        st.success("Note captured!")

if st.session_state.quick_notes:
    with st.expander("Saved Notes", expanded=False):
        for note in reversed(st.session_state.quick_notes):
            st.write(note)
        if st.button("Clear Notes", type="secondary"):
            st.session_state.quick_notes = []
            st.rerun()

st.divider()

# ==================== SECTION 4: links ====================
st.subheader("my links")
st.caption("favourited links")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.link_button("📂 C & DSA Practice", "https://github.com", use_container_width=True)
with c2:
    st.link_button("🛡️ Argus Scanner Repo", "https://github.com", use_container_width=True)
with c3:
    st.link_button("🔐 Bastion Vault Dev", "https://github.com", use_container_width=True)
with c4:
    st.link_button("🌐 Portfolio Config", "https://github.com", use_container_width=True)