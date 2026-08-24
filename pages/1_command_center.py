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

# Helper function with 5-minute cache to prevent 429 quota exhaustion
@st.cache_data(ttl=300)
def load_data(worksheet_name, default_cols):
    try:
        df = conn.read(worksheet=worksheet_name, ttl=300)
        if df is None or df.empty:
            return pd.DataFrame(columns=default_cols)
        return df.dropna(how="all")
    except Exception:
        return pd.DataFrame(columns=default_cols)

# Load data from sheets
tasks_df = load_data("work_tasks", ["id", "text", "done"])
deadlines_df = load_data("work_deadlines", ["task", "subject", "due", "status"])
notes_df = load_data("work_notes", ["note"])

# Normalize data types
if not tasks_df.empty:
    tasks_df["done"] = tasks_df["done"].astype(bool)
if not deadlines_df.empty:
    deadlines_df = deadlines_df.fillna("")

# Helper to sync and clear cache instantly
def sync_update(worksheet_name, df):
    conn.update(worksheet=worksheet_name, data=df)
    st.cache_data.clear()
    st.rerun()

# ==================== SECTION 1: TODAY'S FOCUS ====================
h_col1, h_col2 = st.columns([6, 1])
with h_col1:
    st.subheader("Today")
with h_col2:
    with st.popover("Add"):
        new_task_text = st.text_input("New Focus Item", placeholder="e.g., Debug parser")
        if st.button("Add Task", width="stretch", key="add_focus_btn"):
            if new_task_text.strip():
                new_id = int(tasks_df["id"].max() + 1) if not tasks_df.empty and tasks_df["id"].notna().any() else 1
                new_row = pd.DataFrame([{"id": new_id, "text": new_task_text.strip(), "done": False}])
                tasks_df = pd.concat([tasks_df, new_row], ignore_index=True)
                sync_update("work_tasks", tasks_df)

st.caption("quick focus")

if tasks_df.empty:
    st.info("No tasks left for today!")
else:
    # Auto-sort: Incomplete tasks at top, completed at bottom
    tasks_df = tasks_df.sort_values(by="done", ascending=True).reset_index(drop=True)
    
    for idx, row in tasks_df.iterrows():
        t_col1, t_col2 = st.columns([11, 1])
        with t_col1:
            label = f"~{row['text']}~" if row["done"] else row["text"]
            is_done = st.checkbox(label, value=bool(row["done"]), key=f"task_chk_{row['id']}")
            if is_done != row["done"]:
                tasks_df.at[idx, "done"] = is_done
                sync_update("work_tasks", tasks_df)

        with t_col2:
            if st.button("✕", key=f"del_task_{row['id']}", help="Delete task"):
                tasks_df = tasks_df.drop(idx).reset_index(drop=True)
                sync_update("work_tasks", tasks_df)

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
        if st.button("Add Deadline", width="stretch", key="add_deadline_btn"):
            if new_title.strip():
                new_row = pd.DataFrame([{
                    "task": new_title.strip(),
                    "subject": new_subject.strip() if new_subject.strip() else "General",
                    "due": new_due.strip() if new_due.strip() else "TBD",
                    "status": new_status
                }])
                deadlines_df = pd.concat([deadlines_df, new_row], ignore_index=True)
                sync_update("work_deadlines", deadlines_df)

if not deadlines_df.empty:
    edited_deadlines = st.data_editor(
        deadlines_df,
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

    if not edited_deadlines.equals(deadlines_df):
        sync_update("work_deadlines", edited_deadlines)

    if st.button("Clear Finished Deadlines", key="clear_deadlines"):
        deadlines_df = deadlines_df[~deadlines_df["status"].str.contains("done", case=False, na=False)].reset_index(drop=True)
        sync_update("work_deadlines", deadlines_df)
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
        notes_df = pd.concat([notes_df, new_row], ignore_index=True)
        sync_update("work_notes", notes_df)

if not notes_df.empty:
    with st.expander("Saved Notes", expanded=False):
        for note in reversed(notes_df["note"].tolist()):
            st.write(f"• {note}")
        if st.button("Clear Notes", type="secondary"):
            empty_df = pd.DataFrame(columns=["note"])
            sync_update("work_notes", empty_df)

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