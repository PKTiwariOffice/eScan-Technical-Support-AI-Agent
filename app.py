import streamlit as st

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="eScan Streamlit Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cloud-Safe Responsive CSS
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
""", unsafe_allow_html=True)

# Application Title
st.title("eScan Technical Support Dashboard")
st.write("Welcome to the eScan Dashboard System.")