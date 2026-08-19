import streamlit as st
import pandas as pd
import sqlite3

# Page Configuration
st.set_page_config(page_title="eScan Technical Support Dashboard", layout="wide")

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Compact Centered Login Form
if not st.session_state["logged_in"]:
    # 3 Columns ka use karke form ko center me fit kar rahe hain
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.subheader("🔒 Login - eScan Dashboard")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            if username == "admin" and password == "escan123":
                st.session_state["logged_in"] = True
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Invalid Username or Password")
    st.stop()

# --- MAIN DASHBOARD (After Login) ---
st.title("📊 eScan Project Control Dashboard")

# Fetch Data from SQLite
try:
    conn = sqlite3.connect("project_control.db")
    df_tasks = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    
    # Display Key Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", len(df_tasks))
    col2.metric("Verified Tasks", len(df_tasks[df_tasks['verif_status'] == 'Verified']) if 'verif_status' in df_tasks.columns else 0)
    col3.metric("Pending Tasks", len(df_tasks[df_tasks['verif_status'] != 'Verified']) if 'verif_status' in df_tasks.columns else 0)

    st.subheader("Task Details")
    st.dataframe(df_tasks, use_container_width=True)

except Exception as e:
    st.warning("Database file not found or empty. Please push `project_control.db` to GitHub or connect a cloud database.")
    st.info("System Ready.")