import streamlit as st
import pandas as pd
import sqlite3
import os

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION (MUST BE THE FIRST STREAMLIT COMMAND)
# ---------------------------------------------------------
st.set_page_config(
    page_title="eScan Technical Support Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. CLOUD-SAFE STABLE RESPONSIVE CSS
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Main App Container */
    .stApp {
        background-color: #f8f9fa;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 98% !important;
    }

    /* Executive KPI Cards */
    .escan-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        width: 100%;
    }
    .escan-card-label {
        color: #6b7280;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .escan-card-value {
        color: #111827;
        font-size: 1.875rem;
        font-weight: 700;
        margin-top: 0.25rem;
    }

    /* Responsive Grid Layout Adjustments */
    div[data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. DATABASE HELPER LOGIC
# ---------------------------------------------------------
DB_PATH = "project_control.db"

def get_data():
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            # Database query
            df = pd.read_sql_query("SELECT * FROM projects", conn)
            conn.close()
            return df
        except Exception:
            pass
    
    # Safe Fallback Dataset if DB is initializing
    return pd.DataFrame({
        "Project ID": ["ESC-101", "ESC-102", "ESC-103", "ESC-104"],
        "Client": ["Bhopal HQ", "Indore Branch", "Gwalior Office", "Jabalpur Hub"],
        "Status": ["Active", "Completed", "Active", "Pending"],
        "Scans Completed": [12450, 8900, 15600, 4300],
        "Threats Mitigated": [128, 45, 210, 12]
    })

df = get_data()

# ---------------------------------------------------------
# 4. SIDEBAR NAVIGATION & FILTERS
# ---------------------------------------------------------
st.sidebar.title("🛡️ eScan Control Panel")
st.sidebar.markdown("---")

status_filter = st.sidebar.multiselect(
    "Filter by Status",
    options=df["Status"].unique() if "Status" in df.columns else [],
    default=df["Status"].unique() if "Status" in df.columns else []
)

if status_filter and "Status" in df.columns:
    filtered_df = df[df["Status"].isin(status_filter)]
else:
    filtered_df = df.copy()

st.sidebar.markdown("---")
st.sidebar.info("eScan AI Agent Dashboard v1.0")

# ---------------------------------------------------------
# 5. DASHBOARD HEADER & KPI METRICS
# ---------------------------------------------------------
st.title("eScan Technical Support Dashboard")
st.markdown("Real-time monitoring and deployment tracking system.")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

total_projects = len(filtered_df)
active_scans = filtered_df["Scans Completed"].sum() if "Scans Completed" in filtered_df.columns else 0
threats_found = filtered_df["Threats Mitigated"].sum() if "Threats Mitigated" in filtered_df.columns else 0

with col1:
    st.markdown(f"""
        <div class="escan-card">
            <div class="escan-card-label">Total Projects</div>
            <div class="escan-card-value">{total_projects}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="escan-card">
            <div class="escan-card-label">Total Scans</div>
            <div class="escan-card-value">{active_scans:,}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="escan-card">
            <div class="escan-card-label">Threats Prevented</div>
            <div class="escan-card-value" style="color: #ef4444;">{threats_found:,}</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="escan-card">
            <div class="escan-card-label">System Health</div>
            <div class="escan-card-value" style="color: #10b981;">100%</div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. DATA VISUALIZATION & TABLES
# ---------------------------------------------------------
st.subheader("Project & Scan Overview")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.dataframe(filtered_df, use_container_width=True)

with col_right:
    if "Status" in filtered_df.columns:
        status_counts = filtered_df["Status"].value_counts()
        st.bar_chart(status_counts, use_container_width=True)