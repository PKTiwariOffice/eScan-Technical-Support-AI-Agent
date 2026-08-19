import streamlit as st

# यह कमांड कोड की सबसे पहली Streamlit कमांड होनी चाहिए
st.set_page_config(
    page_title="eScan Streamlit Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Responsive & Cloud-Safe CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 98% !important;
    }
    .escan-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)import streamlit as st
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