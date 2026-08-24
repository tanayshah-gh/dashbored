import streamlit as st

# 1. Configure the main application settings
st.set_page_config(page_title="dashbored", page_icon="⚙️", layout="wide")

# 2. Define the individual pages (modules)
command_center = st.Page("pages/1_command_center.py", title="Command Center", icon="🧭")
finance_tracker = st.Page("pages/2_finance_tracker.py", title="Dashy", icon="💰")

# 3. Group and set up the sidebar navigation
pg = st.navigation([command_center, finance_tracker])

# 4. Run the selected page
pg.run()