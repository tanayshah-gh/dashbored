import streamlit as st
import datetime

# 1. Page Header & Date
today_str = datetime.date.today().strftime("%A, %d %B %Y")
st.title("🧭 Command Center")
st.caption(f"📅 Today is **{today_str}** | *Plan the work, work the plan.*")

st.divider()

# 2. Main Dashboard Layout (Two Responsive Columns)
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("🎯 Today's Focus")
    st.caption("Strictly 3 non-negotiables to avoid post-college fatigue.")
    
    task1 = st.checkbox("Complete 2 LeetCode / DSA problems in C", key="task_1")
    task2 = st.checkbox("Review AIML lecture slides & notes", key="task_2")
    task3 = st.checkbox("Log today's daily expenses in Dashy", key="task_3")
    
    st.markdown("---")
    
    st.subheader("📥 Quick Capture")
    quick_note = st.text_area(
        "Dump sudden thoughts or to-dos here:",
        placeholder="e.g., Update Argus repo docs, buy printouts tomorrow...",
        height=100
    )
    if st.button("Save Note", use_container_width=True):
        st.success("Note captured!")

with col_right:
    st.subheader("📅 Weekly Horizon & Deadlines")
    
    # Visual Deadline Cards / Table
    deadlines = [
        {"Task": "DSA Lab Assignment 3", "Subject": "Data Structures", "Due": "In 2 Days", "Status": "🟡 Pending"},
        {"Task": "AIML Model Evaluation Practical", "Subject": "Machine Learning", "Due": "Friday", "Status": "🔵 In Progress"},
        {"Task": "Bastion DB Migration Check", "Subject": "Personal Dev", "Due": "Sunday", "Status": "🟢 Ready"},
    ]
    st.dataframe(deadlines, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    st.subheader("🛠 Dev Quick-Launch")
    st.caption("Direct references and hubs for active technical projects:")
    
    c1, c2 = st.columns(2)
    with c1:
        st.link_button("📂 C & DSA Practice", "https://github.com", use_container_width=True)
        st.link_button("🛡️ Argus Scanner Repo", "https://github.com", use_container_width=True)
    with c2:
        st.link_button("🔐 Bastion Vault Dev", "https://github.com", use_container_width=True)
        st.link_button("🌐 Portfolio Config", "https://github.com", use_container_width=True)