import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection

# --- 1. GLOBAL SETTINGS & CLOUD ENGINE ---
#st.set_page_config(page_title="2026 dashy", layout="wide")

# Establish connection once for the entire app
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. THE SPENDING PAGE MODULE ---
def show_spending_page():
    st.title("2026 spending")
    
    # Define loader inside the page scope to avoid NameErrors
    def load_spending_data():
        df =  conn.read(worksheet="Expenses", ttl="1m")
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df = df.sort_values(by='Date', ascending=False)
        return df

    df_all = load_spending_data()

    # Sidebar: Data Entry
    st.sidebar.markdown("---")
    st.sidebar.subheader("Log New Expense/Income")
    with st.sidebar.form("expense_form", clear_on_submit=True):
       
        # --- START DATE NAVIGATION CONTROLS ---
        # Initialize session state for date if it doesn't exist yet
        if 'expense_date' not in st.session_state:
            st.session_state.expense_date = datetime.now().date()

        # Create two small columns for the navigation buttons
        btn_col1, btn_col2 = st.sidebar.columns(2)
        
        # Note: forms require Form Buttons, but navigation needs to change state immediately.
        # If regular buttons act weird inside the form, place this block right above st.sidebar.form instead!
        if btn_col1.button("◀ Prev Day", use_container_width=True):
            st.session_state.expense_date -= timedelta(days=1)
            
        if btn_col2.button("Next Day ▶", use_container_width=True):
            st.session_state.expense_date += timedelta(days=1)

        # The actual date input now binds directly to the session state variable
        date_in = st.sidebar.date_input("Date", value=st.session_state.expense_date)
        # --- END DATE NAVIGATION CONTROLS ---

        name_in = st.text_input("Item Name")
        # min_value=None allows for negative income values
        amt_in = st.number_input("Amount (₹)", value=0.0, step=10.0, min_value=None)
        
        existing_cats = sorted(df_all['Category'].unique().tolist()) if not df_all.empty else []
        cat_select = st.selectbox("Category", existing_cats + ["+ Add New Category"])
        new_cat_name = st.text_input("New Category Name (if selected)")
        comm_in = st.text_input("Comment")
        
        if st.form_submit_button("Log Transaction"):
            final_cat = new_cat_name.strip().lower() if cat_select == "+ Add New Category" else cat_select
            if final_cat:
                new_row = pd.DataFrame([[str(date_in), name_in, amt_in, final_cat, comm_in]], 
                                       columns=['Date', 'Name', 'Amount', 'Category', 'Comment'])
                
                # 1. Combine data
                updated_df = pd.concat([df_all, new_row], ignore_index=True)
                
                # 2. THE FIX: Sort by Date to keep order consistent
                updated_df['Date'] = pd.to_datetime(updated_df['Date'])
                updated_df = updated_df.sort_values(by='Date', ascending=False)
                
                # 3. Sync to Cloud
                conn.update(worksheet="Expenses", data=updated_df)
                st.cache_data.clear()
                
                st.sidebar.success("Cloud Sync Successful!")
                st.rerun()

    # Dashboard Logic
    # --- UPDATED MONTHLY FILTER LOGIC ---
    if not df_all.empty:
        # 1. Convert Date column to datetime objects
        df_all['Date'] = pd.to_datetime(df_all['Date'])
        
        # 2. Extract unique Month-Year strings for the dropdown
        df_all['Month_Year'] = df_all['Date'].dt.strftime('%B %Y')
        available_months = df_all.sort_values('Date', ascending=False)['Month_Year'].unique().tolist()
        
        st.sidebar.markdown("---")
        selected_month = st.sidebar.selectbox("📅 Select Month to View", available_months)
        
        df_filtered = df_all[df_all['Month_Year'] == selected_month]
        df_personal = df_filtered[df_filtered['Category'] != 'sponsored']
        
        c1, c2, c3 = st.columns(3)
        today = datetime.now()
        weekly_sum = df_personal[df_personal['Date'] >= (today - timedelta(days=today.weekday()))]['Amount'].sum()
        
        c1.metric(f"Weekly (Current)", f"₹{weekly_sum:,.2f}")
        c2.metric(f"Total {selected_month}", f"₹{df_personal['Amount'].sum():,.2f}")
        
        sponsored_sum = df_filtered[df_filtered['Category'] == 'sponsored']['Amount'].sum()
        c3.metric("Sponsored Total", f"₹{sponsored_sum:,.2f}")
        
        st.markdown("---")
        st.subheader(f"Breakdown for {selected_month}")
        
        # Pie Chart automatically uses filtered data
        if not df_personal.empty:
            st.plotly_chart(px.pie(df_personal[df_personal['Amount'] > 0], 
                                   values='Amount', names='Category', hole=0.5), width='stretch')
        
        st.subheader(f"Log: {selected_month}")
        edited_df = st.data_editor(
            df_filtered, 
            num_rows="dynamic", 
            width='stretch',
            hide_index=True,
            key="spending_editor"
        )
        if st.button("Save Changes & Sync to Cloud"):
            # Get the rows that aren't currently being edited (sponsored/other months)
            # This prevents overwriting data from other months
            df_others = df_all[~df_all.index.isin(df_filtered.index)]
            final_df = pd.concat([edited_df, df_others], ignore_index=True)
            
            # Sync to Google Sheets
            conn.update(worksheet="Expenses", data=final_df)
            
            # Clear cache so the next view is fresh
            st.cache_data.clear() 
            
            st.success("Cloud Updated!")
            st.rerun()

# --- MAIN NAVIGATION ---
st.sidebar.title("navigation")
selection = st.sidebar.radio("Select Portal:", ["Spending Portal"])

if selection == "Spending Portal":
    show_spending_page()