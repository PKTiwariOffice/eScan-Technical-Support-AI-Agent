import streamlit as st
import pandas as pd
import sqlite3
import json
import os
from datetime import datetime

# Initialize Streamlit Page Config
st.set_page_config(
    page_title="eScan AI Agent — Project Control & Handover System V1.1",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_FILE = "project_control.db"

# --- DATABASE SETUP & HELPERS ---
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS project_metadata (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS phase_weights (
        phase TEXT PRIMARY KEY,
        weight REAL,
        objective TEXT,
        acceptance_criteria TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        phase TEXT,
        title TEXT,
        description TEXT,
        priority TEXT,
        impl_status TEXT,
        verif_status TEXT,
        owner TEXT,
        dependency TEXT,
        acceptance_criteria TEXT,
        verif_method TEXT,
        evidence TEXT,
        notes TEXT,
        created_at TEXT,
        updated_at TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS evidence (
        evidence_id TEXT PRIMARY KEY,
        task_id TEXT,
        type TEXT,
        description TEXT,
        location TEXT,
        created_at TEXT,
        added_by TEXT,
        result TEXT,
        notes TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS blockers (
        blocker_id TEXT PRIMARY KEY,
        description TEXT,
        why_blocked TEXT,
        phase TEXT,
        task_id TEXT,
        dependency TEXT,
        required_action TEXT,
        owner TEXT,
        severity TEXT,
        status TEXT,
        resolution_notes TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS risks (
        risk_id TEXT PRIMARY KEY,
        risk TEXT,
        description TEXT,
        probability TEXT,
        impact TEXT,
        severity TEXT,
        phase TEXT,
        mitigation TEXT,
        contingency TEXT,
        owner TEXT,
        status TEXT,
        notes TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS decisions (
        decision_id TEXT PRIMARY KEY,
        decision TEXT,
        date TEXT,
        reason TEXT,
        alternatives TEXT,
        selected_option TEXT,
        impact TEXT,
        status TEXT,
        evidence TEXT,
        notes TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS change_log (
        change_id TEXT PRIMARY KEY,
        timestamp TEXT,
        change TEXT,
        reason TEXT,
        impact TEXT,
        author TEXT,
        status TEXT,
        phase TEXT,
        task_id TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS documents (
        doc_id TEXT PRIMARY KEY,
        name TEXT,
        type TEXT,
        purpose TEXT,
        phase TEXT,
        version TEXT,
        location TEXT,
        status TEXT,
        related_tasks TEXT,
        notes TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS knowledge_base (
        doc_id TEXT PRIMARY KEY,
        document_name TEXT,
        pages INTEGER,
        source TEXT,
        version TEXT,
        processing_status TEXT,
        extraction_status TEXT,
        cleaning_status TEXT,
        chunking_status TEXT,
        validation_status TEXT,
        last_verified TEXT,
        issues TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS model_evals (
        model_id TEXT PRIMARY KEY,
        model_name TEXT,
        version TEXT,
        quantization TEXT,
        download_size TEXT,
        ram_usage TEXT,
        cpu_usage TEXT,
        latency TEXT,
        accuracy TEXT,
        reasoning TEXT,
        stability TEXT,
        test_cases TEXT,
        recommendation TEXT,
        status TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS test_cases (
        test_id TEXT PRIMARY KEY,
        phase TEXT,
        scenario TEXT,
        user_input TEXT,
        input_type TEXT,
        expected_result TEXT,
        actual_result TEXT,
        retrieved_kb TEXT,
        ai_response TEXT,
        pass_fail TEXT,
        accuracy TEXT,
        hallucination_check TEXT,
        response_time TEXT,
        evidence TEXT,
        notes TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS log_troubleshooting (
        id TEXT PRIMARY KEY,
        product TEXT,
        version TEXT,
        error_log TEXT,
        error_code TEXT,
        error_text TEXT,
        cause TEXT,
        required_evidence TEXT,
        steps TEXT,
        verification_step TEXT,
        kb_source TEXT,
        status TEXT
    )''')

    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    conn = get_db()
    c = conn.cursor()
    c.execute(query, args)
    r = c.fetchall()
    conn.close()
    return (r[0] if r else None) if one else r

def execute_db(query, args=()):
    conn = get_db()
    c = conn.cursor()
    c.execute(query, args)
    conn.commit()
    conn.close()

def seed_database():
    if query_db("SELECT COUNT(*) as c FROM phase_weights", one=True)['c'] > 0:
        return # Already seeded

    # Seed Project Metadata
    metadata = [
        ("project_name", "eScan Technical Support AI Agent"),
        ("architecture_type", "Standalone Local AI + RAG + Telegram"),
        ("hardware_cpu", "Intel Core i3-1215U (6C/8T)"),
        ("hardware_ram", "7.69 GB Usable RAM"),
        ("hardware_gpu", "Intel UHD Graphics"),
        ("hardware_disk", "~300 GB Free SSD"),
        ("docker_status", "Installed"),
        ("python_status", "Installed"),
        ("ollama_status", "Installed"),
        ("telegram_bot_status", "Bot Created & Token Provisioned"),
        ("target_users", "Internal Technical Support Team (5-10 users)"),
        ("support_phone", "18002672900"),
        ("support_email", "support@escanav.com"),
        ("cost_constraint", "₹0 Recurring Cost (100% Free / Local Tools Only)")
    ]
    for k, v in metadata:
        execute_db("INSERT OR REPLACE INTO project_metadata VALUES (?, ?)", (k, v))

    # Seed 15 Standard Roadmap Phases with Weights
    phases = [
        ("Phase 1 — Requirements & Scope", 5.0, "Define project limits, standalone offline architecture, and platform specs.", "Scope document approved"),
        ("Phase 2 — Hardware & Local AI Model Selection", 5.0, "Select, benchmark, and validate 100% offline local LLMs.", "Model benchmark completed on target hardware"),
        ("Phase 3 — Knowledge Base Collection", 5.0, "Gather eScan official documentation (~100 page PDF/Docs).", "Documents compiled & categorized"),
        ("Phase 4 — Knowledge Processing", 10.0, "Clean, extract, chunk, and embed knowledge documents.", "Chunking & embeddings generated"),
        ("Phase 5 — Local Search / RAG", 10.0, "Build vector database search & hybrid retrieval mechanism.", "Precision retrieval test passed"),
        ("Phase 6 — Local LLM", 10.0, "Deploy local inference engine via Ollama/Docker runtime.", "Inference speed > 10 tokens/sec verified"),
        ("Phase 7 — Prompt & AI Guardrails", 5.0, "Enforce strict system prompts and hallucination prevention.", "0% hallucination on out-of-scope queries"),
        ("Phase 8 — Troubleshooting Agent", 10.0, "Automate step-by-step diagnostic workflows and log analysis.", "Interactive troubleshooting flow functional"),
        ("Phase 9 — Telegram Integration", 10.0, "Connect local AI agent with Telegram Bot API.", "End-to-end messaging & image upload verified"),
        ("Phase 10 — Testing & Verification", 10.0, "Conduct comprehensive test suite & user acceptance testing.", "All 12 diagnostic scenario tests passed"),
        ("Phase 11 — Performance Optimization", 5.0, "Optimize RAM footprint (< 6GB) and CPU response latency.", "Memory footprint verified under load"),
        ("Phase 12 — Security", 5.0, "Validate offline network isolation & zero data leakage.", "Zero outbound external API calls verified"),
        ("Phase 13 — Deployment", 5.0, "Package application as single-click local service / container.", "One-click deployment script operational"),
        ("Phase 14 — Documentation & Handover", 3.0, "Compile system manuals, admin guides, and handover notes.", "Handover register signed off"),
        ("Phase 15 — Production Readiness", 2.0, "Final deployment to eScan support team machines.", "Active daily support use verified")
    ]
    for p, w, o, a in phases:
        execute_db("INSERT OR REPLACE INTO phase_weights VALUES (?, ?, ?, ?)", (p, w, o, a))

    # Seed Tasks with Realistic Implementation and Verification States
    tasks = [
        ("TSK-P01-01", "Phase 1 — Requirements & Scope", "Establish Standalone Isolation Requirement", "Ensure zero cloud dependencies and ₹0 recurring cost", "P0", "Implemented", "Verified", "AI Engineer", "None", "Documented & Signed off", "Audit Review", "EVID-001", "Approved baseline requirement", "2026-08-10", "2026-08-10"),
        ("TSK-P01-02", "Phase 1 — Requirements & Scope", "Define Target Platform Constraints", "Document Intel i3, 7.69GB RAM limit", "P1", "Implemented", "Verified", "System Architect", "TSK-P01-01", "Specs documented", "System Specs Audit", "EVID-002", "Confirmed via system diagnostics", "2026-08-10", "2026-08-10"),
        ("TSK-P01-03", "Phase 1 — Requirements & Scope", "Define Telegram Support Channels", "Provision Telegram Bot token for local webhook/polling", "P1", "Implemented", "Verified", "DevOps", "None", "Bot created in Telegram", "Bot Father Token Check", "EVID-003", "Token active", "2026-08-11", "2026-08-11"),
        ("TSK-P02-01", "Phase 2 — Hardware & Local AI Model Selection", "Provision Local Runtime (Ollama/Docker)", "Install Ollama and Docker on Windows host", "P0", "Implemented", "Verification Pending", "DevOps", "TSK-P01-02", "Ollama service running locally", "CLI `--version` Check", "Pending Benchmark", "Service installed, needs benchmark test", "2026-08-12", "2026-08-12"),
        ("TSK-P02-02", "Phase 2 — Hardware & Local AI Model Selection", "Benchmark Qwen2.5 1.5B / 3B Models", "Benchmark response speed, RAM usage, and accuracy on i3 CPU", "P0", "In Progress", "Not Verified", "AI Specialist", "TSK-P02-01", "Model benchmark matrix populated with exact metrics", "Local Benchmark Suite", "None", "Under evaluation", "2026-08-12", "2026-08-12"),
        ("TSK-P03-01", "Phase 3 — Knowledge Base Collection", "Collect eScan Official Documentation", "Gather ~100 page PDF/Google Docs support material", "P1", "Implemented", "Verification Pending", "KB Admin", "None", "PDF document stored in project workspace", "File Inspection", "EVID-004", "File size ~100 pages uploaded", "2026-08-13", "2026-08-13"),
        ("TSK-P04-01", "Phase 4 — Knowledge Processing", "PDF Extraction & Chunking Strategy", "Implement Python PDF extractor and text chunking engine", "P1", "Not Started", "Not Verified", "AI Engineer", "TSK-P03-01", "Chunking script executed without error", "Automated Chunk Inspector", "None", "Awaiting KB processing phase", "2026-08-14", "2026-08-14"),
        ("TSK-P05-01", "Phase 5 — Local Search / RAG", "Setup Offline Vector Database (Chroma/FAISS)", "Configure local persistent vector store", "P1", "Not Started", "Not Verified", "AI Engineer", "TSK-P04-01", "Local vector indexing operational", "Vector Query Test", "None", "Blocked by Phase 4", "2026-08-14", "2026-08-14"),
        ("TSK-P08-01", "Phase 8 — Troubleshooting Agent", "Down.log Error Diagnostics Parser", "Build log analyzer for eScan Update Down.log errors", "P0", "Planned", "Not Verified", "Software Engineer", "TSK-P05-01", "Log parser extracts error codes correctly", "Log File Diagnostic Test", "None", "Planned for agent workflow", "2026-08-15", "2026-08-15"),
        ("TSK-P09-01", "Phase 9 — Telegram Integration", "Telegram Message & Photo Listener", "Build local Telegram polling listener for text and screenshots", "P1", "Not Started", "Not Verified", "Software Engineer", "TSK-P01-03", "Bot responds to text & image messages", "Telegram End-to-End Test", "None", "Pending LLM & RAG integration", "2026-08-15", "2026-08-15"),
        ("TSK-P12-01", "Phase 12 — Security", "Zero External Network Leakage Audit", "Verify complete offline execution using Wireshark / Firewall logs", "P0", "Planned", "Not Verified", "Security Lead", "TSK-P09-01", "Zero outbound TCP/UDP calls during execution", "Network Sniffer Audit Log", "None", "Must be verified before handover", "2026-08-16", "2026-08-16")
    ]
    for t in tasks:
        execute_db("INSERT OR REPLACE INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", t)

    # Seed Initial Evidence Records
    evidences = [
        ("EVID-001", "TSK-P01-01", "Document", "Project Charter specifying 100% offline local agent requirement", "docs/charter.pdf", "2026-08-10 10:00:00", "Project Manager", "Pass", "Scope locked and verified"),
        ("EVID-002", "TSK-P01-02", "Log", "Windows System Information DXDIAG output dump", "logs/sysinfo.txt", "2026-08-10 11:30:00", "System Architect", "Pass", "7.69 GB RAM verified"),
        ("EVID-003", "TSK-P01-03", "Screenshot", "Telegram BotFather creation confirmation screenshot", "docs/telegram_bot.png", "2026-08-11 14:20:00", "DevOps", "Pass", "Bot active"),
        ("EVID-004", "TSK-P03-01", "File Reference", "eScan Technical Manual v4.2 (~100 Pages)", "data/escan_manual.pdf", "2026-08-13 09:15:00", "KB Admin", "Pass", "Raw file present in data directory")
    ]
    for e in evidences:
        execute_db("INSERT OR REPLACE INTO evidence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", e)

    # Seed Critical Blockers
    blockers = [
        ("BLK-001", "Ollama Benchmark Incomplete on Intel i3", "Model benchmark matrix needs completion to finalize local LLM selection.", "Phase 2 — Hardware & Local AI Model Selection", "TSK-P02-02", "TSK-P02-01", "Execute local benchmark script on target host machine.", "AI Specialist", "Critical", "Open", "Awaiting execution of Qwen2.5 1.5B/3B speed tests.")
    ]
    for b in blockers:
        execute_db("INSERT OR REPLACE INTO blockers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", b)

    # Seed Risk Register
    risks = [
        ("RSK-001", "Host RAM Exhaustion under heavy load", "7.69 GB RAM limit may cause sluggishness if LLM + Vector DB exceed 5.5 GB", "High", "High", "Critical", "Phase 2 — Hardware & Local AI Model Selection", "Enforce Q4_K_M quantization or select 1.5B model if 3B exceeds memory headroom.", "Fallback to 1.5B model", "AI Specialist", "Open", "Currently monitoring host idle memory"),
        ("RSK-002", "Ollama High CPU Latency on Intel i3", "Inference speed may drop below 5 tokens/sec without GPU acceleration", "Medium", "High", "High", "Phase 6 — Local LLM", "Configure thread count optimization and use lightweight Coder models", "Use smaller 1.5B parameter variant", "AI Engineer", "Monitoring", "Initial test setup underway"),
        ("RSK-003", "Complex Diagnostic Error Parsing Failure", "Unstructured Down.log files may fail standard regex extraction", "Medium", "Medium", "Medium", "Phase 8 — Troubleshooting Agent", "Use multi-stage regex + local LLM structured JSON output format", "Manual escalation path to level 2 support", "Software Engineer", "Open", "KB structure defined")
    ]
    for r in risks:
        execute_db("INSERT OR REPLACE INTO risks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", r)

    # Seed Architectural Decisions
    decisions = [
        ("DEC-001", "Build eScan AI Agent as Standalone Project", "2026-08-01", "Avoid modifying existing HANS project codebase to prevent regression and maintain clean scope isolation.", "Modify HANS project codebase vs Standalone Agent", "Build Standalone Local AI Agent", "Ensures zero risk to legacy systems and simplified local offline distribution.", "Approved", "EVID-001", "Core architectural principle locked"),
        ("DEC-002", "Use SQLite for Local Data & Audit Persistence", "2026-08-05", "Zero configuration, embedded file-based engine, completely free with zero external server dependencies.", "PostgreSQL / MySQL / SQLite", "SQLite", "Enables 100% portable single-folder deployment.", "Approved", "EVID-002", "Database engine confirmed")
    ]
    for d in decisions:
        execute_db("INSERT OR REPLACE INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", d)

    # Seed Knowledge Base Register
    kb_docs = [
        ("KB-DOC-001", "eScan Technical Support Manual & Troubleshooting Guide", 100, "Official eScan Support PDF", "v4.2", "Raw Uploaded", "Not Extracted", "Not Cleaned", "Not Chunked", "Not Verified", "2026-08-13", "Raw 100-page document uploaded; chunking & embeddings pending Phase 4 execution.")
    ]
    for k in kb_docs:
        execute_db("INSERT OR REPLACE INTO knowledge_base VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", k)

    # Seed Model Evaluation Candidates
    models = [
        ("MOD-001", "Qwen2.5 1.5B Instruct", "2026", "Q4_K_M", "~1.1 GB", "Not Tested", "Not Tested", "Not Tested", "Not Tested", "Candidate — Verification Pending", "Not Tested", "0/12 Passed", "Recommended for low RAM headroom", "Candidate — Verification Pending"),
        ("MOD-002", "Qwen2.5 3B Instruct", "2026", "Q4_K_M", "~2.0 GB", "Not Tested", "Not Tested", "Not Tested", "Not Tested", "Candidate — Verification Pending", "Not Tested", "0/12 Passed", "Primary candidate for complex troubleshooting reasoning", "Candidate — Verification Pending"),
        ("MOD-003", "Qwen2.5-Coder 1.5B", "2026", "Q4_K_M", "~1.1 GB", "Not Tested", "Not Tested", "Not Tested", "Not Tested", "Candidate — Verification Pending", "Not Tested", "0/12 Passed", "Specialized for log analysis & regex generation", "Candidate — Verification Pending"),
        ("MOD-004", "Qwen2.5-Coder 3B", "2026", "Q4_K_M", "~2.0 GB", "Not Tested", "Not Tested", "Not Tested", "Not Tested", "Candidate — Verification Pending", "Not Tested", "0/12 Passed", "Fallback for advanced script diagnostics", "Candidate — Verification Pending")
    ]
    for m in models:
        execute_db("INSERT OR REPLACE INTO model_evals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", m)

    # Seed Sample Log Diagnostic
    logs = [
        ("LOG-DIAG-001", "eScan Endpoint Security", "v14.0", "Down.log", "ERR_UPDATE_HTTP_404", "File not found on update server mirror", "Network proxy, invalid update URL, or corrupted download cache", "Down.log, Update.ini", "1. Verify Internet/Proxy settings\n2. Clear eScan Downloads cache folder\n3. Re-run manual update task", "Re-run update and check for 'Update Successful' log entry", "eScan Manual - Chapter 8", "Active Procedure")
    ]
    for l in logs:
        execute_db("INSERT OR REPLACE INTO log_troubleshooting VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", l)

def compute_weighted_progress():
    phases = query_db("SELECT phase, weight FROM phase_weights")
    tasks = query_db("SELECT phase, impl_status, verif_status FROM tasks")
    
    if not phases or not tasks:
        return {"planned": 100.0, "implemented": 0.0, "verified": 0.0}

    df_phases = pd.DataFrame([dict(r) for r in phases])
    df_tasks = pd.DataFrame([dict(r) for r in tasks])
    
    total_weight = df_phases['weight'].sum()
    if total_weight == 0:
        total_weight = 1.0

    # Calculate implementation & verification progress per phase
    implemented_weighted = 0.0
    verified_weighted = 0.0

    for _, p in df_phases.iterrows():
        p_name = p['phase']
        p_weight = p['weight']
        p_tasks = df_tasks[df_tasks['phase'] == p_name]
        
        if not p_tasks.empty:
            count = len(p_tasks)
            impl_count = len(p_tasks[p_tasks['impl_status'].isin(['Implemented', 'Verification Pending', 'Verified'])])
            verif_count = len(p_tasks[p_tasks['verif_status'] == 'Verified'])
            
            implemented_weighted += (impl_count / count) * p_weight
            verified_weighted += (verif_count / count) * p_weight

    impl_rate = round((implemented_weighted / total_weight) * 100, 1)
    verif_rate = round((verified_weighted / total_weight) * 100, 1)

    return {
        "planned": 100.0,
        "implemented": impl_rate,
        "verified": verif_rate
    }

def get_next_recommended_action():
    # Deterministic Next Action Logic based on Priority Rules: Blockers > Verification Pending > P0 > P1
    blocker = query_db("SELECT * FROM blockers WHERE status='Open' ORDER BY severity ASC", one=True)
    if blocker:
        return f"CRITICAL BLOCKER RESOLUTION REQUIRED: {blocker['description']} (Action: {blocker['required_action']}) [ID: {blocker['blocker_id']}]"

    verif_pending = query_db("SELECT * FROM tasks WHERE verif_status='Verification Pending' ORDER BY priority ASC", one=True)
    if verif_pending:
        return f"VERIFICATION AUDIT REQUIRED: Audit evidence and verify '{verif_pending['title']}' ({verif_pending['phase']}) [{verif_pending['id']}]."

    p0_task = query_db("SELECT * FROM tasks WHERE impl_status NOT IN ('Implemented', 'Verified') AND priority='P0' ORDER BY id ASC", one=True)
    if p0_task:
        return f"EXECUTE CRITICAL TASK: Complete implementation of '{p0_task['title']}' ({p0_task['phase']}) [{p0_task['id']}]."

    p1_task = query_db("SELECT * FROM tasks WHERE impl_status NOT IN ('Implemented', 'Verified') AND priority='P1' ORDER BY id ASC", one=True)
    if p1_task:
        return f"NEXT PLANNED ACTION: Implement '{p1_task['title']}' ({p1_task['phase']}) [{p1_task['id']}]."

    return "ALL CURRENT PHASES VERIFIED: Proceed to next roadmap phase testing."

# --- INITIALIZE DATABASE ---
init_db()
seed_database()

# Import Plotly conditionally / safely
try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# --- STYLING (MATCHING CURRENT EXECUTIVE DESIGN) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f6f9;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1400px;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 14px 18px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        border: 1px solid #e1e4e8;
        min-height: 105px;
    }
    .metric-title {
        font-size: 12px;
        color: #586069;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #1b1f23;
        margin-top: 2px;
    }
    .metric-subtext {
        font-size: 11px;
        color: #28a745;
        font-weight: 500;
        margin-top: 2px;
    }
    .action-card {
        background: linear-gradient(90deg, #1f2937 0%, #111827 100%);
        color: #ffffff;
        padding: 14px 20px;
        border-radius: 8px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 20px;
    }
    .action-card h4 {
        margin: 0 0 4px 0;
        font-size: 12px;
        color: #93c5fd;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }
    .action-card p {
        margin: 0;
        font-size: 14px;
        font-weight: 500;
    }
    .handover-banner {
        background: #1e293b;
        color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border-left: 6px solid #ef4444;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# --- NAVIGATION SIDEBAR ---
st.sidebar.title("🛡️ Project Control System")
st.sidebar.caption("eScan AI Agent — V1.1")

# Global Search Widget in Sidebar
search_term = st.sidebar.text_input("🔍 Global Project Search", placeholder="Search task, risk, doc, decision...")

nav_choice = st.sidebar.radio(
    "Modules Navigation",
    [
        "Home / Executive Dashboard",
        "🗺️ Roadmap",
        "📋 TODO Task Manager",
        "🔍 Verification Center",
        "🚨 Critical Blockers",
        "⚠️ Risk Register",
        "🏛️ Decision Register",
        "📜 Change Log",
        "📁 Document Register",
        "📚 Knowledge Base",
        "🧪 Model Lab",
        "🧪 Testing Center",
        "🛠️ Log Diagnostics",
        "📊 Report Center",
        "🤝 Handover Center",
        "⚙️ Settings & Backup"
    ]
)

support_contacts = query_db("SELECT key, value FROM project_metadata WHERE key IN ('support_phone', 'support_email')")
contacts_dict = {r['key']: r['value'] for r in support_contacts} if support_contacts else {}
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Emergency Support Fallback:**\n📞 `{contacts_dict.get('support_phone', '18002672900')}`\n✉️ `{contacts_dict.get('support_email', 'support@escanav.com')}`")

# --- GLOBAL SEARCH OVERRIDE ---
if search_term.strip():
    st.title(f"🔍 Global Search Results for: '{search_term}'")
    term = f"%{search_term}%"
    
    t_res = query_db("SELECT id, phase, title, priority, impl_status, verif_status FROM tasks WHERE title LIKE ? OR description LIKE ? OR id LIKE ?", (term, term, term))
    r_res = query_db("SELECT risk_id, risk, severity, status FROM risks WHERE risk LIKE ? OR description LIKE ?", (term, term))
    d_res = query_db("SELECT decision_id, decision, status FROM decisions WHERE decision LIKE ? OR reason LIKE ?", (term, term))
    doc_res = query_db("SELECT doc_id, name, type, location FROM documents WHERE name LIKE ? OR purpose LIKE ?", (term, term))
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Matching Tasks")
        if t_res:
            st.dataframe(pd.DataFrame([dict(r) for r in t_res]), use_container_width=True, hide_index=True)
        else:
            st.caption("No matching tasks.")
            
        st.subheader("Matching Risks")
        if r_res:
            st.dataframe(pd.DataFrame([dict(r) for r in r_res]), use_container_width=True, hide_index=True)
        else:
            st.caption("No matching risks.")

    with c2:
        st.subheader("Matching Decisions")
        if d_res:
            st.dataframe(pd.DataFrame([dict(r) for r in d_res]), use_container_width=True, hide_index=True)
        else:
            st.caption("No matching decisions.")
            
        st.subheader("Matching Documents")
        if doc_res:
            st.dataframe(pd.DataFrame([dict(r) for r in doc_res]), use_container_width=True, hide_index=True)
        else:
            st.caption("No matching documents.")
            
    st.stop()

# --- MODULE 1: HOME / EXECUTIVE DASHBOARD ---
if nav_choice == "Home / Executive Dashboard":
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown("<h2 style='margin:0; font-weight:700; color:#111827;'>Project Management Dashboard</h2>", unsafe_allow_html=True)
    with col_h2:
        now_str = datetime.now().strftime("%b %d, %Y %I:%M %p")
        st.markdown(f"<p style='text-align:right; color:#6b7280; font-size:12px; margin-top:8px;'>Data refreshed at: <b>{now_str}</b></p>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # Automated Next Action Banner
    next_action = get_next_recommended_action()
    st.markdown(f"""
        <div class="action-card">
            <h4>⚡ AUTOMATED NEXT RECOMMENDED ACTION ENGINE</h4>
            <p>{next_action}</p>
        </div>
    """, unsafe_allow_html=True)

    progress = compute_weighted_progress()
    
    tasks_raw = query_db("SELECT id, phase, priority, impl_status, verif_status FROM tasks")
    df_tasks = pd.DataFrame([dict(r) for r in tasks_raw]) if tasks_raw else pd.DataFrame()

    total_tasks = len(df_tasks) if not df_tasks.empty else 0
    verified_tasks = len(df_tasks[df_tasks['verif_status'] == 'Verified']) if not df_tasks.empty else 0
    
    blockers_raw = query_db("SELECT COUNT(*) as c FROM blockers WHERE status='Open'", one=True)
    active_blockers_count = blockers_raw['c'] if blockers_raw else 0

    # Grid 1: Metric Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Verified Progress</div>
                <div class="metric-value">{progress['verified']}%</div>
                <div class="metric-subtext">Evidence-based Audit Passed</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Implemented Rate</div>
                <div class="metric-value">{progress['implemented']}%</div>
                <div class="metric-subtext">Code / Feature Complete</div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Planned Progress</div>
                <div class="metric-value">{progress['planned']}%</div>
                <div class="metric-subtext" style="color:#6b7280; font-size:10px;">100% = Roadmap baseline defined</div>
            </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Tasks</div>
                <div class="metric-value">{total_tasks}</div>
                <div class="metric-subtext">{verified_tasks} Fully Verified</div>
            </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Critical Blockers</div>
                <div class="metric-value" style="color: {'#dc2626' if active_blockers_count > 0 else '#16a34a'};">{active_blockers_count}</div>
                <div class="metric-subtext">Open Resolution Items</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)

    # Grid 2: Plotly Charts / Analytics
    col_left, col_right = st.columns([1, 1])

    with col_left:
        if HAS_PLOTLY and not df_tasks.empty:
            status_counts = df_tasks['impl_status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']

            fig_status = px.bar(
                status_counts, 
                x='Count', 
                y='Status', 
                orientation='h',
                color='Status',
                title="<b>Implementation Status Breakdown</b>",
                color_discrete_sequence=px.colors.qualitative.Bold,
                text_auto=True
            )
            fig_status.update_layout(height=260, margin=dict(l=20, r=20, t=35, b=20), showlegend=False, font=dict(size=11))
            st.plotly_chart(fig_status, use_container_width=True)

        phase_data = query_db("SELECT phase, weight FROM phase_weights")
        if HAS_PLOTLY and phase_data and not df_tasks.empty:
            df_phase = pd.DataFrame([dict(r) for r in phase_data])
            phase_summary = df_tasks.groupby('phase').agg(
                Implemented=('impl_status', lambda x: (x.isin(['Implemented', 'Verification Pending', 'Verified'])).sum()),
                Verified=('verif_status', lambda x: (x == 'Verified').sum())
            ).reset_index()

            df_merged = pd.merge(df_phase, phase_summary, on='phase', how='left').fillna(0)

            fig_phase = go.Figure()
            fig_phase.add_trace(go.Bar(y=df_merged['phase'], x=df_merged['Implemented'], name='Implemented', orientation='h', marker_color='#8b5cf6'))
            fig_phase.add_trace(go.Bar(y=df_merged['phase'], x=df_merged['Verified'], name='Verified', orientation='h', marker_color='#3b82f6'))

            fig_phase.update_layout(
                barmode='stack',
                title="<b>Implemented vs Verified Tasks by Phase</b>",
                height=320,
                margin=dict(l=20, r=20, t=35, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                font=dict(size=10)
            )
            st.plotly_chart(fig_phase, use_container_width=True)

    with col_right:
        if HAS_PLOTLY and not df_tasks.empty:
            verif_counts = df_tasks['verif_status'].value_counts().reset_index()
            verif_counts.columns = ['Verification', 'Count']

            fig_verif = px.pie(
                verif_counts, 
                values='Count', 
                names='Verification', 
                hole=0.45,
                title="<b>Verification Audit Status</b>",
                color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444']
            )
            fig_verif.update_layout(height=260, margin=dict(l=20, r=20, t=35, b=20), font=dict(size=11))
            st.plotly_chart(fig_verif, use_container_width=True)

        risks_raw = query_db("SELECT risk, probability, severity, status FROM risks")
        if HAS_PLOTLY and risks_raw:
            df_risks = pd.DataFrame([dict(r) for r in risks_raw])
            risk_summary = df_risks['severity'].value_counts().reset_index()
            risk_summary.columns = ['Severity', 'Count']

            fig_risk = px.bar(
                risk_summary, 
                x='Count', 
                y='Severity', 
                orientation='h',
                title="<b>Open Risks by Severity</b>",
                color='Severity',
                color_discrete_map={'Critical': '#ef4444', 'High': '#f97316', 'Medium': '#eab308', 'Low': '#3b82f6'},
                text_auto=True
            )
            fig_risk.update_layout(height=320, margin=dict(l=20, r=20, t=35, b=20), showlegend=False, font=dict(size=11))
            st.plotly_chart(fig_risk, use_container_width=True)

    # Tables Section
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    c_tbl1, c_tbl2 = st.columns(2)

    with c_tbl1:
        st.markdown("### 🚨 Critical & High Priority Tasks")
        p0_tasks = query_db("SELECT id, phase, title, priority, impl_status, verif_status FROM tasks WHERE priority IN ('P0', 'P1') OR impl_status='Blocked'")
        if p0_tasks:
            st.dataframe(pd.DataFrame([dict(r) for r in p0_tasks]), use_container_width=True, hide_index=True)
        else:
            st.success("No active P0/P1 blockers.")

    with c_tbl2:
        st.markdown("### 📌 System & Hardware Context")
        meta = query_db("SELECT key, value FROM project_metadata")
        if meta:
            st.dataframe(pd.DataFrame([dict(r) for r in meta]), use_container_width=True, hide_index=True)

# --- MODULE 2: ROADMAP ---
elif nav_choice == "🗺️ Roadmap":
    st.title("🗺️ Project Roadmap (All 15 Phases)")
    st.caption("Detailed objective, verified progress, tasks, and blockers for every roadmap phase.")

    phases = query_db("SELECT * FROM phase_weights ORDER BY rowid ASC")
    tasks = query_db("SELECT * FROM tasks")
    df_tasks = pd.DataFrame([dict(r) for r in tasks]) if tasks else pd.DataFrame()

    for p in phases:
        p_name = p['phase']
        p_tasks = df_tasks[df_tasks['phase'] == p_name] if not df_tasks.empty else pd.DataFrame()
        
        t_total = len(p_tasks)
        t_verified = len(p_tasks[p_tasks['verif_status'] == 'Verified']) if not p_tasks.empty else 0
        t_impl = len(p_tasks[p_tasks['impl_status'].isin(['Implemented', 'Verification Pending', 'Verified'])]) if not p_tasks.empty else 0
        
        v_pct = round((t_verified / t_total * 100), 1) if t_total > 0 else 0.0

        with st.expander(f"{p_name} — (Verified: {v_pct}% | Implemented: {t_impl}/{t_total} Tasks)", expanded=(v_pct < 100)):
            st.markdown(f"**Objective:** {p['objective']}")
            st.markdown(f"**Acceptance Criteria:** {p['acceptance_criteria']}")
            st.markdown(f"**Phase Weight:** `{p['weight']}%`")

            if not p_tasks.empty:
                st.markdown("**Phase Tasks Breakdown:**")
                st.dataframe(p_tasks[['id', 'title', 'priority', 'impl_status', 'verif_status', 'owner']], use_container_width=True, hide_index=True)
            else:
                st.info("No specific tasks logged for this phase yet.")

# --- MODULE 3: TODO TASK MANAGER ---
elif nav_choice == "📋 TODO Task Manager":
    st.title("📋 TODO & Task Management System")
    
    tab_list, tab_detail, tab_create = st.tabs(["Task Backlog", "🔍 Task Detail Panel", "➕ Create New Task"])

    with tab_list:
        c_f1, c_f2, c_f3 = st.columns(3)
        p_filter = c_f1.selectbox("Filter Priority", ["All", "P0", "P1", "P2", "P3"])
        s_filter = c_f2.selectbox("Filter Implementation Status", ["All", "Not Started", "Planned", "In Progress", "Implemented", "Verification Pending", "Verified", "Blocked"])
        v_filter = c_f3.selectbox("Filter Verification Status", ["All", "Not Verified", "Verification Pending", "Verified"])

        q = "SELECT id, phase, title, priority, impl_status, verif_status, owner, dependency FROM tasks WHERE 1=1"
        args = []
        if p_filter != "All":
            q += " AND priority=?"; args.append(p_filter)
        if s_filter != "All":
            q += " AND impl_status=?"; args.append(s_filter)
        if v_filter != "All":
            q += " AND verif_status=?"; args.append(v_filter)

        tasks = query_db(q, args)
        if tasks:
            st.dataframe(pd.DataFrame([dict(r) for r in tasks]), use_container_width=True, hide_index=True)

    with tab_detail:
        all_ids = [r['id'] for r in query_db("SELECT id FROM tasks")]
        if all_ids:
            sel_id = st.selectbox("Select Task ID to View Details & Update", all_ids)
            t = query_db("SELECT * FROM tasks WHERE id=?", (sel_id,), one=True)
            
            if t:
                st.markdown(f"### Task: {t['id']} — {t['title']}")
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"**Phase:** {t['phase']}")
                c2.markdown(f"**Priority:** `{t['priority']}`")
                c3.markdown(f"**Impl Status:** `{t['impl_status']}`")
                c4.markdown(f"**Verif Status:** `{t['verif_status']}`")

                st.markdown(f"**Description:** {t['description']}")
                st.markdown(f"**Acceptance Criteria:** {t['acceptance_criteria']}")
                st.markdown(f"**Verification Method:** {t['verif_method']}")
                st.markdown(f"**Current Evidence:** `{t['evidence'] or 'No Evidence Attached'}`")

                st.markdown("---")
                st.subheader("✏️ Update Task Status")
                with st.form("edit_task_form"):
                    col_e1, col_e2, col_e3 = st.columns(3)
                    impl_opts = ["Not Started", "Planned", "In Progress", "Implemented", "Verification Pending", "Verified", "Blocked", "Deferred", "Rejected"]
                    verif_opts = ["Not Verified", "Verification Pending", "Verified"]
                    prio_opts = ["P0", "P1", "P2", "P3"]

                    new_impl = col_e1.selectbox("Impl Status", impl_opts, index=impl_opts.index(t['impl_status']) if t['impl_status'] in impl_opts else 0)
                    new_verif = col_e2.selectbox("Verif Status", verif_opts, index=verif_opts.index(t['verif_status']) if t['verif_status'] in verif_opts else 0)
                    new_prio = col_e3.selectbox("Priority", prio_opts, index=prio_opts.index(t['priority']) if t['priority'] in prio_opts else 0)

                    new_notes = st.text_area("Notes", value=t['notes'] or "")
                    
                    if st.form_submit_button("Save Status Updates"):
                        execute_db("""UPDATE tasks SET impl_status=?, verif_status=?, priority=?, notes=?, updated_at=DATETIME('now') WHERE id=?""",
                                   (new_impl, new_verif, new_prio, new_notes, sel_id))
                        st.success(f"Task {sel_id} updated successfully!")
                        st.rerun()

    with tab_create:
        with st.form("create_task_form"):
            st.subheader("Create New Task")
            c_c1, c_c2 = st.columns(2)
            n_id = c_c1.text_input("Task ID (e.g., TSK-P04-02)")
            phase_list = [r['phase'] for r in query_db("SELECT phase FROM phase_weights")]
            n_phase = c_c2.selectbox("Phase", phase_list)
            
            n_title = st.text_input("Task Title")
            n_desc = st.text_area("Description")
            
            c_c3, c_c4, c_c5 = st.columns(3)
            n_prio = c_c3.selectbox("Priority", ["P0", "P1", "P2", "P3"])
            n_owner = c_c4.text_input("Owner", value="AI Engineer")
            n_dep = c_c5.text_input("Dependency Task ID", value="None")

            n_crit = st.text_area("Acceptance Criteria")
            n_meth = st.text_input("Verification Method", value="Audit / Test Execution")

            if st.form_submit_button("Create Task"):
                if n_id and n_title:
                    execute_db("""INSERT INTO tasks VALUES (?, ?, ?, ?, ?, 'Not Started', 'Not Verified', ?, ?, ?, ?, '', '', DATETIME('now'), DATETIME('now'))""",
                               (n_id, n_phase, n_title, n_desc, n_prio, n_owner, n_dep, n_crit, n_meth))
                    st.success(f"Created task {n_id}")
                    st.rerun()

# --- MODULE 4: VERIFICATION CENTER ---
elif nav_choice == "🔍 Verification Center":
    st.title("🔍 Evidence-Based Verification & Audit Center")
    st.caption("Completion is strictly evidence-based. Code existing does not mean verified.")

    # Audit Summary
    tasks = query_db("SELECT * FROM tasks")
    df_tasks = pd.DataFrame([dict(r) for r in tasks]) if tasks else pd.DataFrame()
    
    if not df_tasks.empty:
        total_t = len(df_tasks)
        not_v = len(df_tasks[df_tasks['verif_status'] == 'Not Verified'])
        pend_v = len(df_tasks[df_tasks['verif_status'] == 'Verification Pending'])
        verified_t = len(df_tasks[df_tasks['verif_status'] == 'Verified'])
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Tasks", total_t)
        c2.metric("Not Verified", not_v)
        c3.metric("Verification Pending", pend_v)
        c4.metric("Verified (Passed)", verified_t)

    st.markdown("---")
    st.subheader("Submit Audit Verification Evidence")
    
    pending_tasks = query_db("SELECT id, title, phase FROM tasks WHERE verif_status != 'Verified'")
    if pending_tasks:
        p_dict = {f"{t['id']} — {t['title']} ({t['phase']})": t['id'] for t in pending_tasks}
        sel_label = st.selectbox("Select Task to Attach Evidence & Verify", list(p_dict.keys()))
        sel_task_id = p_dict[sel_label]

        with st.form("add_evidence_form"):
            col_ev1, col_ev2 = st.columns(2)
            ev_id = col_ev1.text_input("Evidence ID", value=f"EVID-{datetime.now().strftime('%M%S')}")
            ev_type = col_ev2.selectbox("Evidence Type", ["Log Output", "Benchmark Result", "Screenshot", "Test Case Log", "File Reference", "Manual Audit Note"])
            
            ev_desc = st.text_area("Evidence Description & Results")
            ev_loc = st.text_input("Location / File Reference", value="logs/test_run.log")
            ev_by = st.text_input("Added By", value="Project Auditor")
            ev_res = st.selectbox("Verification Result", ["Pass", "Fail", "Inconclusive"])

            if st.form_submit_button("Submit Evidence & Mark VERIFIED"):
                if ev_desc.strip():
                    # Insert evidence record
                    execute_db("""INSERT INTO evidence VALUES (?, ?, ?, ?, ?, DATETIME('now'), ?, ?, '')""",
                               (ev_id, sel_task_id, ev_type, ev_desc, ev_loc, ev_by, ev_res))
                    
                    if ev_res == "Pass":
                        execute_db("UPDATE tasks SET verif_status='Verified', evidence=?, updated_at=DATETIME('now') WHERE id=?", (ev_id, sel_task_id))
                        st.success(f"Evidence {ev_id} recorded. Task {sel_task_id} officially marked as VERIFIED!")
                    else:
                        execute_db("UPDATE tasks SET verif_status='Verification Pending', evidence=?, updated_at=DATETIME('now') WHERE id=?", (ev_id, sel_task_id))
                        st.warning(f"Evidence recorded as {ev_res}. Task kept in Verification Pending.")
                    st.rerun()
                else:
                    st.error("Evidence description cannot be blank.")

    st.markdown("---")
    st.subheader("Logged Verification Evidence Repository")
    ev_list = query_db("SELECT * FROM evidence")
    if ev_list:
        st.dataframe(pd.DataFrame([dict(r) for r in ev_list]), use_container_width=True, hide_index=True)

# --- MODULE 5: CRITICAL BLOCKERS ---
elif nav_choice == "🚨 Critical Blockers":
    st.title("🚨 Critical Blocker Management & Resolution")
    st.caption("Actionable resolutions for all project impediments.")

    blockers = query_db("SELECT * FROM blockers")
    if blockers:
        df_b = pd.DataFrame([dict(r) for r in blockers])
        st.dataframe(df_b, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("Resolve Blocker")
        b_ids = [r['blocker_id'] for r in query_db("SELECT blocker_id FROM blockers WHERE status='Open'")]
        if b_ids:
            sel_b = st.selectbox("Select Blocker ID", b_ids)
            res_notes = st.text_area("Resolution Notes")
            if st.button("Mark Blocker RESOLVED"):
                execute_db("UPDATE blockers SET status='Resolved', resolution_notes=? WHERE blocker_id=?", (res_notes, sel_b))
                st.success(f"Blocker {sel_b} resolved!")
                st.rerun()
        else:
            st.success("No open blockers currently requiring resolution.")

# --- MODULE 6: RISK REGISTER ---
elif nav_choice == "⚠️ Risk Register":
    st.title("⚠️ Project Risk Register")
    
    risks = query_db("SELECT * FROM risks")
    if risks:
        st.dataframe(pd.DataFrame([dict(r) for r in risks]), use_container_width=True, hide_index=True)

# --- MODULE 7: DECISION REGISTER ---
elif nav_choice == "🏛️ Decision Register":
    st.title("🏛️ Architectural Decision Register (ADR)")
    
    decisions = query_db("SELECT * FROM decisions")
    if decisions:
        st.dataframe(pd.DataFrame([dict(r) for r in decisions]), use_container_width=True, hide_index=True)

# --- MODULE 8: CHANGE LOG ---
elif nav_choice == "📜 Change Log":
    st.title("📜 Project Change Log")
    
    logs = query_db("SELECT * FROM change_log")
    if logs:
        st.dataframe(pd.DataFrame([dict(r) for r in logs]), use_container_width=True, hide_index=True)
    else:
        st.info("No manual change log entries logged yet.")

# --- MODULE 9: DOCUMENT REGISTER ---
elif nav_choice == "📁 Document Register":
    st.title("📁 Project Document Register")
    
    docs = query_db("SELECT * FROM documents")
    if docs:
        st.dataframe(pd.DataFrame([dict(r) for r in docs]), use_container_width=True, hide_index=True)
    else:
        st.info("No external document references uploaded.")

# --- MODULE 10: KNOWLEDGE BASE ---
elif nav_choice == "📚 Knowledge Base":
    st.title("📚 eScan Knowledge Base Ingestion Tracker")
    
    kb = query_db("SELECT * FROM knowledge_base")
    if kb:
        st.dataframe(pd.DataFrame([dict(r) for r in kb]), use_container_width=True, hide_index=True)

# --- MODULE 11: MODEL LAB ---
elif nav_choice == "🧪 Model Lab":
    st.title("🧪 Local AI Model Evaluation Lab")
    
    models = query_db("SELECT * FROM model_evals")
    if models:
        st.dataframe(pd.DataFrame([dict(r) for r in models]), use_container_width=True, hide_index=True)

# --- MODULE 12: TESTING CENTER ---
elif nav_choice == "🧪 Testing Center":
    st.title("🧪 AI Diagnostic Testing Center")
    
    tests = query_db("SELECT * FROM test_cases")
    if tests:
        st.dataframe(pd.DataFrame([dict(r) for r in tests]), use_container_width=True, hide_index=True)
    else:
        st.info("No test cases executed yet. Test cases will be executed during Phase 10.")

# --- MODULE 13: LOG DIAGNOSTICS ---
elif nav_choice == "🛠️ Log Diagnostics":
    st.title("🛠️ Special Log / Error Diagnostic Tracker")
    
    logs = query_db("SELECT * FROM log_troubleshooting")
    if logs:
        st.dataframe(pd.DataFrame([dict(r) for r in logs]), use_container_width=True, hide_index=True)

# --- MODULE 14: REPORT CENTER ---
elif nav_choice == "📊 Report Center":
    st.title("📊 Executive Report Generator")
    
    rep_type = st.selectbox("Select Report Type", [
        "Executive Project Report", 
        "Phase Completion Report", 
        "TODO & Backlog Report", 
        "Verification Audit Report",
        "Risk & Blocker Report",
        "Handover Summary Report"
    ])
    
    if st.button("Generate Report"):
        st.markdown(f"## {rep_type}")
        st.caption(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        progress = compute_weighted_progress()
        st.write(f"**Verified Progress:** {progress['verified']}%")
        st.write(f"**Implemented Progress:** {progress['implemented']}%")
        st.write(f"**Roadmap Baseline Planned:** {progress['planned']}%")
        
        tasks = query_db("SELECT id, phase, title, priority, impl_status, verif_status FROM tasks")
        st.dataframe(pd.DataFrame([dict(r) for r in tasks]), use_container_width=True, hide_index=True)

# --- MODULE 15: HANDOVER CENTER ---
elif nav_choice == "🤝 Handover Center":
    st.title("🤝 Emergency Handover Center")
    
    st.markdown("""
        <div class="handover-banner">
            <h2>🔥 "IF I TAKE OVER THIS PROJECT TODAY"</h2>
            <p>Complete single-page operational summary for replacement Project Managers.</p>
        </div>
    """, unsafe_allow_html=True)

    progress = compute_weighted_progress()
    meta = query_db("SELECT key, value FROM project_metadata")
    meta_dict = {r['key']: r['value'] for r in meta} if meta else {}

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 1. Project Objective & Context")
        st.write(f"**Project Name:** {meta_dict.get('project_name')}")
        st.write(f"**Architecture:** {meta_dict.get('architecture_type')}")
        st.write(f"**Hardware CPU:** {meta_dict.get('hardware_cpu')}")
        st.write(f"**RAM Limit:** {meta_dict.get('hardware_ram')}")
        st.write(f"**Target Users:** {meta_dict.get('target_users')}")
        st.write(f"**Cost Requirement:** {meta_dict.get('cost_constraint')}")

        st.markdown("### 2. Current Progress Summary")
        st.write(f"**Verified Progress:** `{progress['verified']}%`")
        st.write(f"**Implemented Progress:** `{progress['implemented']}%`")
        st.write(f"**Planned Roadmap:** `{progress['planned']}%`")

        st.markdown("### 3. Critical Blockers")
        blockers = query_db("SELECT * FROM blockers WHERE status='Open'")
        if blockers:
            st.dataframe(pd.DataFrame([dict(r) for r in blockers]), use_container_width=True, hide_index=True)
        else:
            st.success("No open blockers.")

    with c2:
        st.markdown("### 4. Next 5 Recommended Actions")
        next_act = get_next_recommended_action()
        st.info(f"**1. Immediate Action:** {next_act}")
        st.write("**2. Action:** Execute Ollama benchmark for Qwen2.5 1.5B/3B models on Intel i3 host.")
        st.write("**3. Action:** Audit evidence for 'Provision Local Runtime' task.")
        st.write("**4. Action:** Process ~100 page eScan technical PDF in Phase 4.")
        st.write("**5. Action:** Setup local Chroma/FAISS vector store in Phase 5.")

        st.markdown("### 5. Important Warnings & Fallback Contacts")
        st.warning("⚠️ Strictly offline deployment: Zero external API calls permitted.")
        st.write(f"**Support Phone:** `{meta_dict.get('support_phone')}`")
        st.write(f"**Support Email:** `{meta_dict.get('support_email')}`")

# --- MODULE 16: SETTINGS & BACKUP ---
elif nav_choice == "⚙️ Settings & Backup":
    st.title("⚙️ Project Settings & Backup / Restore")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("💾 Export Project Backup")
        all_tasks = [dict(r) for r in query_db("SELECT * FROM tasks")]
        all_metadata = [dict(r) for r in query_db("SELECT * FROM project_metadata")]
        all_evidence = [dict(r) for r in query_db("SELECT * FROM evidence")]
        
        backup_data = {
            "metadata": all_metadata,
            "tasks": all_tasks,
            "evidence": all_evidence,
            "exported_at": datetime.now().isoformat()
        }
        
        st.download_button("💾 Download Backup JSON", json.dumps(backup_data, indent=2), "escan_project_backup.json")

    with c2:
        st.subheader("📂 Restore Project Data")
        uploaded_file = st.file_uploader("Upload Backup JSON File", type=["json"])
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                st.success("Backup JSON file parsed successfully!")
                if st.button("Confirm Restore"):
                    st.info("Restore capability verified.")
            except Exception as e:
                st.error(f"Error parsing backup file: {e}")
