import sqlite3
from datetime import datetime
from database import init_db, execute_db, query_db
from config import DEFAULT_PHASE_WEIGHTS

def seed_database():
    init_db()

    if query_db("SELECT COUNT(*) as cnt FROM tasks", one=True)['cnt'] > 0:
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    metadata = [
        ("project_name", "eScan Technical Support AI Agent"),
        ("architecture_type", "Standalone Local AI Agent"),
        ("hardware_cpu", "Intel Core i3-1215U (6C/8T)"),
        ("hardware_ram", "7.69 GB Usable RAM"),
        ("hardware_gpu", "Intel UHD Graphics"),
        ("hardware_storage", "~300 GB Free Disk"),
        ("os_env", "Windows 11 + Docker + Ollama + Python"),
        ("target_users", "5-10 Internal Support Engineers"),
        ("telegram_status", "Telegram Bot Created (Token Existing), Integration Pending"),
        ("kb_initial_source", "~100 Page PDF / Google Docs Document"),
        ("kb_processing_status", "Not Started"),
        ("model_eval_status", "Candidates Selected (Qwen2.5 1.5B/3B, Coder), Unverified"),
        ("testing_status", "0 Test Cases Passed"),
        ("deployment_readiness", "0% (Pre-Alpha Infrastructure)")
    ]
    for k, v in metadata:
        execute_db("INSERT OR REPLACE INTO project_metadata (key, value) VALUES (?, ?)", (k, v))

    for phase, weight in DEFAULT_PHASE_WEIGHTS.items():
        execute_db("INSERT OR REPLACE INTO phase_weights (phase, weight) VALUES (?, ?)", (phase, weight))

    tasks = [
        ("TSK-P1-01", "Phase 1 — Requirements & Scope", "Establish Standalone Isolation Requirement", "Ensure zero modification to existing HANS project.", "P0", "Implemented", "Verified", "Lead Architect", "None", "Isolated codebase", "Inspection", "Project Isolation Directive in Decision Register", "Standalone project constraint enforced.", now, now),
        ("TSK-P1-02", "Phase 1 — Requirements & Scope", "Define Target Platform Constraints", "Target local execution on Intel i3-1215U, 7.69GB RAM, Windows 11.", "P0", "Implemented", "Verified", "SysAdmin", "TSK-P1-01", "System specifications documented", "Hardware Audit", "Hardware baseline logged in metadata", "Strict zero-cloud budget.", now, now),
        ("TSK-P1-03", "Phase 1 — Requirements & Scope", "Define Telegram Support Channels", "Support text, screenshot, and hybrid text+image queries.", "P1", "Implemented", "Verified", "PM", "TSK-P1-02", "Channel modalities agreed", "Sign-off", "Requirement Specification Doc", "Fallback: 18002672900 / support@escanav.com", now, now),

        ("TSK-P2-01", "Phase 2 — Hardware & Local AI Model Selection", "Provision Local Runtime (Ollama/Docker)", "Install and verify local LLM runner on Windows host.", "P0", "Implemented", "Verification Pending", "DevOps", "TSK-P1-02", "Ollama CLI active", "Execution Check", "Ollama CLI installed, awaiting memory benchmark", "Ollama active.", now, now),
        ("TSK-P2-02", "Phase 2 — Hardware & Local AI Model Selection", "Benchmark Qwen2.5 1.5B / 3B Models", "Benchmark response latency and RAM pressure on i3-1215U.", "P0", "Not Started", "Not Verified", "AI Engineer", "TSK-P2-01", "Benchmark report with real tokens/sec data", "Benchmark Test", "None", "No model verified for production yet.", now, now),

        ("TSK-P3-01", "Phase 3 — Knowledge Base", "Ingest ~100-page eScan Support Doc", "Extract text, diagrams, and logs from primary support PDF.", "P1", "Not Started", "Not Verified", "Data Eng", "TSK-P1-03", "Raw text extracted into corpus directory", "File Audit", "None", "Awaiting document file transfer.", now, now),
        ("TSK-P4-01", "Phase 4 — Knowledge Processing", "Implement Chunking & Metadata Extraction", "Split KB into semantic chunks; preserve Down.log error code maps.", "P1", "Not Started", "Not Verified", "Data Eng", "TSK-P3-01", "Chunk index produced", "Data Validation", "None", "Error codes must map directly to solutions.", now, now),

        ("TSK-P5-01", "Phase 5 — Local Search / RAG", "Setup SQLite-Vector / Local Vector DB", "Build zero-cost local retrieval pipeline.", "P1", "Not Started", "Not Verified", "AI Engineer", "TSK-P4-01", "Similarity search operational under 200ms", "Query Test", "None", "Must run completely offline.", now, now),
        ("TSK-P6-01", "Phase 6 — Local LLM Implementation", "Build RAG + LLM Inference Chain", "Connect retrieval engine to verified local model via Ollama API.", "P1", "Not Started", "Not Verified", "AI Engineer", "TSK-P2-02", "End-to-end local generation works", "Integration Test", "None", "Discussion != Implementation.", now, now),

        ("TSK-P7-01", "Phase 7 — Prompt & Guardrails", "Implement Anti-Hallucination Guardrails", "Enforce strict fallback to human support if KB confidence < 0.70.", "P0", "Not Started", "Not Verified", "AI Engineer", "TSK-P6-01", "System refuses unverified fixes", "Safety Test", "None", "Enforce: Never invent fixes.", now, now),
        ("TSK-P8-01", "Phase 8 — Troubleshooting Agent", "Build Log Analysis Engine (Down.log)", "Extract exact error codes from Down.log and match KB procedures.", "P1", "Not Started", "Not Verified", "AI Engineer", "TSK-P7-01", "Down.log parser accurately maps errors", "Unit Tests", "None", "Core support workflow.", now, now),

        ("TSK-P9-01", "Phase 9 — Telegram Integration", "Connect Telegram Bot Handler to Local Agent", "Wire existing Telegram Bot API token to Python backend.", "P1", "In Progress", "Not Verified", "Backend Dev", "TSK-P8-01", "Telegram user gets verified agent responses", "Live Bot Test", "Bot token registered in local secrets", "Bot exists; webhook/polling pending.", now, now),

        ("TSK-P10-01", "Phase 10 — Testing & Verification", "Execute End-to-End Troubleshooting Test Suite", "Validate 20 standard eScan support failure scenarios.", "P1", "Not Started", "Not Verified", "QA Eng", "TSK-P9-01", "100% pass on documented errors", "QA Execution", "None", "Pending agent completion.", now, now)
    ]

    for t in tasks:
        execute_db('''
            INSERT OR REPLACE INTO tasks 
            (id, phase, title, description, priority, impl_status, verif_status, owner, dependency, acceptance_criteria, verif_method, evidence, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', t)

    execute_db('''
        INSERT OR REPLACE INTO decisions 
        (id, decision, reason, alternatives, selected_option, impact, status, evidence, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        "DEC-001",
        "Maintain eScan Support Agent as a Fully Standalone Project",
        "Prevent accidental breakage or contamination of the existing production HANS project repository.",
        "Option A: Merge into HANS codebase; Option B: Build isolated standalone repository.",
        "Option B: Standalone Project",
        "Zero technical dependency on HANS. Independent deployment lifecycle.",
        "Approved",
        "Project Architecture Directive",
        "HANS codebase must remain untouched.",
        now
    ))

    risks = [
        ("RSK-001", "RAM Exhaustion on 7.69 GB Host", "High", "Critical", "Critical", "Enforce 1.5B/3B quantized models (Q4_K_M); limit batch sizes; avoid heavy vector DBs.", "Identified Risk", "AI Architect", "Strict RAM monitoring required during benchmarks.", now),
        ("RSK-002", "CPU Inference Latency Bottleneck", "High", "High", "High", "Use lightweight embeddings; limit context window length to 2048 tokens.", "Identified Risk", "AI Architect", "Host lacks dedicated GPU.", now),
        ("RSK-003", "KB Parsing / OCR Errors on PDF Scans", "Medium", "Medium", "Medium", "Validate text extraction accuracy before chunking; manually format tables.", "Identified Risk", "Data Eng", "100-page PDF quality to be evaluated.", now),
        ("RSK-004", "LLM Hallucination on Technical Troubleshooting", "Medium", "Critical", "High", "Hard prompt guardrails + strict fallback to 18002672900 / support@escanav.com.", "Identified Risk", "AI Engineer", "Unverified answers could damage customer systems.", now)
    ]
    for r in risks:
        execute_db('''
            INSERT OR REPLACE INTO risks 
            (id, risk, probability, impact, severity, mitigation, status, owner, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', r)

    execute_db('''
        INSERT OR REPLACE INTO change_log (id, date, change, reason, impact, author, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ("CHG-001", now, "Project Control Dashboard MVP Deployed", "Mandated project control and progress tracking system setup.", "Baseline dashboard active.", "Lead Systems Developer", "Approved"))

    docs = [
        ("Requirements", "# Project Requirements\n- **Target Platform:** Windows 11, Intel i3-1215U, 7.69GB RAM, ~300GB Disk.\n- **Budget:** Zero recurring cost. Strictly free/open-source.\n- **Users:** 5-10 internal support team members via Telegram.\n- **Inputs:** Text, Screenshots/Images, Combined Text+Images.\n- **Fallback:** Phone: 18002672900 | Email: support@escanav.com"),
        ("Architecture", "# Technical Architecture\n- **UI / Dashboard:** Streamlit + SQLite (Local-first, single-port).\n- **Inference Runtime:** Ollama / Docker container.\n- **Candidate Models:** Qwen2.5 1.5B / 3B (Quantized Q4_K_M).\n- **RAG Engine:** Local SQLite-Vector / FAISS + SentenceTransformers.\n- **Integration:** Telegram Bot API via Python Async Client."),
        ("Operations", "# Standard Operating Procedures\n- **Model Selection:** Must pass RAM benchmark (< 4.5 GB peak usage).\n- **Troubleshooting Logic:** Parse `Down.log` -> Lookup KB -> Formulate Fix -> Guardrail Check -> Output. If unknown, output fallback support phone/email."),
        ("Handover", "# Handover Master Checklist\n- Ensure `project_control.db` is backed up prior to structural updates.\n- Review 'IF I TAKE OVER THIS PROJECT TODAY' section on the Handover tab.")
    ]
    for doc_type, content in docs:
        execute_db("INSERT OR REPLACE INTO documentation (doc_type, content, last_updated) VALUES (?, ?, ?)", (doc_type, content, now))

if __name__ == "__main__":
    seed_database()
    print("Database seeded successfully.")
