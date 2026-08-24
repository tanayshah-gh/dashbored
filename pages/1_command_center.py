import streamlit as st
import pandas as pd
import datetime
from streamlit_gsheets import GSheetsConnection

# 1. Page Header & Date
today_str = datetime.date.today().strftime("%A, %d %B %Y")
st.title("work")
st.caption(f"**{today_str}**")

st.divider()

# 2. Establish Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Helper function to load initial data with caching
@st.cache_data(ttl=60)
def load_data(worksheet_name, default_cols):
    try:
        df = conn.read(worksheet=worksheet_name, ttl=60)
        if df is None or df.empty:
            return pd.DataFrame(columns=default_cols)
        return df.dropna(how="all")
    except Exception:
        return pd.DataFrame(columns=default_cols)

# 3. Initialize In-Memory Session State from Google Sheets (Runs only on cold start)
if "tasks_df" not in st.session_state:
    raw_tasks = load_data("work_tasks", ["id", "text", "done"])
    if not raw_tasks.empty:
        raw_tasks["done"] = raw_tasks["done"].astype(bool)
    st.session_state.tasks_df = raw_tasks

if "deadlines_df" not in st.session_state:
    raw_deadlines = load_data("work_deadlines", ["task", "subject", "due", "status"])
    if not raw_deadlines.empty:
        raw_deadlines = raw_deadlines.fillna("")
    st.session_state.deadlines_df = raw_deadlines

if "notes_df" not in st.session_state:
    st.session_state.notes_df = load_data("work_notes", ["note"])

# Background sync helper: Updates remote sheet silently while keeping local state responsive
def persist_sheet(worksheet_name, df):
    conn.update(worksheet=worksheet_name, data=df)

# ==================== SECTION 1: TODAY'S FOCUS ====================
h_col1, h_col2 = st.columns([6, 1])
with h_col1:
    st.subheader("Today")
with h_col2:
    with st.popover("Add"):
        new_task_text = st.text_input("New Focus Item", placeholder="e.g., Debug parser")
        if st.button("Add Task", width="stretch", key="add_focus_btn"):
            if new_task_text.strip():
                new_id = (
                    int(st.session_state.tasks_df["id"].max() + 1)
                    if not st.session_state.tasks_df.empty and st.session_state.tasks_df["id"].notna().any()
                    else 1
                )
                new_row = pd.DataFrame([{"id": new_id, "text": new_task_text.strip(), "done": False}])
                st.session_state.tasks_df = pd.concat([st.session_state.tasks_df, new_row], ignore_index=True)
                persist_sheet("work_tasks", st.session_state.tasks_df)
                st.rerun()

st.caption("quick focus")

if st.session_state.tasks_df.empty:
    st.info("No tasks left for today!")
else:
    # Auto-sort: Incomplete tasks at top, completed at bottom
    st.session_state.tasks_df = st.session_state.tasks_df.sort_values(by="done", ascending=True).reset_index(drop=True)
    
    for idx, row in st.session_state.tasks_df.iterrows():
        t_col1, t_col2 = st.columns([11, 1])
        with t_col1:
            label = f"~{row['text']}~" if row["done"] else row["text"]
            is_done = st.checkbox(label, value=bool(row["done"]), key=f"task_chk_{row['id']}")
            if is_done != row["done"]:
                st.session_state.tasks_df.at[idx, "done"] = is_done
                persist_sheet("work_tasks", st.session_state.tasks_df)
                st.rerun()

        with t_col2:
            if st.button("✕", key=f"del_task_{row['id']}", help="Delete task"):
                st.session_state.tasks_df = st.session_state.tasks_df.drop(idx).reset_index(drop=True)
                persist_sheet("work_tasks", st.session_state.tasks_df)
                st.rerun()

st.divider()

# ==================== SECTION 2: DEADLINES ====================
d_col1, d_col2 = st.columns([6, 1])
with d_col1:
    st.subheader("Deadlines")
with d_col2:
    with st.popover("Add"):
        with st.form("add_deadline_form", clear_on_submit=True):
            new_title = st.text_input("Assignment / Task", placeholder="e.g., C Pointers Lab")
            new_subject = st.text_input("Subject", placeholder="e.g., DSA / AIML")
            new_due = st.text_input("Due Date", placeholder="e.g., Friday or 28 Aug")
            new_status = st.selectbox("Status", ["🟡 pending", "🔵 in prog", "🟢 done"])
            submitted = st.form_submit_button("Add Deadline", width="stretch")
            
            if submitted and new_title.strip():
                new_row = pd.DataFrame([{
                    "task": new_title.strip(),
                    "subject": new_subject.strip() if new_subject.strip() else "General",
                    "due": new_due.strip() if new_due.strip() else "TBD",
                    "status": new_status
                }])
                st.session_state.deadlines_df = pd.concat([st.session_state.deadlines_df, new_row], ignore_index=True)
                persist_sheet("work_deadlines", st.session_state.deadlines_df)
                st.rerun()
if not st.session_state.deadlines_df.empty:
    edited_deadlines = st.data_editor(
        st.session_state.deadlines_df,
        column_config={
            "status": st.column_config.SelectboxColumn(
                "Status",
                help="Update task progress",
                options=["🟡 pending", "🔵 in prog", "🟢 done"],
                required=True,
            )
        },
        width="stretch",
        hide_index=True,
        num_rows="dynamic",
        key="deadlines_editor"
    )

    if not edited_deadlines.equals(st.session_state.deadlines_df):
        st.session_state.deadlines_df = edited_deadlines
        persist_sheet("work_deadlines", st.session_state.deadlines_df)
        st.rerun()

    if st.button("Clear Finished Deadlines", key="clear_deadlines"):
        st.session_state.deadlines_df = st.session_state.deadlines_df[
            ~st.session_state.deadlines_df["status"].str.contains("done", case=False, na=False)
        ].reset_index(drop=True)
        persist_sheet("work_deadlines", st.session_state.deadlines_df)
        st.rerun()
else:
    st.info("No upcoming deadlines.")

st.divider()

# ==================== SECTION 3: QUICK CAPTURE ====================
st.subheader("Quick Capture")

with st.form("quick_capture_form", clear_on_submit=True):
    quick_note = st.text_area(
        "quick capture input",
        placeholder="e.g., paid by cash, owe money etc... (Ctrl+Enter to save)",
        height=100,
        label_visibility="collapsed"
    )
    submitted = st.form_submit_button("Save", width="stretch")
    if submitted and quick_note.strip():
        new_row = pd.DataFrame([{"note": quick_note.strip()}])
        st.session_state.notes_df = pd.concat([st.session_state.notes_df, new_row], ignore_index=True)
        persist_sheet("work_notes", st.session_state.notes_df)
        st.rerun()

if not st.session_state.notes_df.empty:
    with st.expander("Saved Notes", expanded=False):
        for note in reversed(st.session_state.notes_df["note"].tolist()):
            st.write(f"• {note}")
        if st.button("Clear Notes", type="secondary"):
            empty_df = pd.DataFrame(columns=["note"])
            st.session_state.notes_df = empty_df
            persist_sheet("work_notes", empty_df)
            st.rerun()

st.divider()

# ==================== SECTION 4: links ====================
st.subheader("my links")
st.caption("favourited links")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.link_button("📂 C & DSA Practice", "https://github.com", width="stretch")
with c2:
    st.link_button("🛡️ Argus Scanner Repo", "https://github.com", width="stretch")
with c3:
    st.link_button("🔐 Bastion Vault Dev", "https://github.com", width="stretch")
with c4:
    st.link_button("🌐 Portfolio Config", "https://github.com", width="stretch")