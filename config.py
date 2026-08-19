import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "project_control.db")

DEFAULT_PHASE_WEIGHTS = {
    "Phase 1 — Requirements & Scope": 10.0,
    "Phase 2 — Hardware & Local AI Model Selection": 15.0,
    "Phase 3 — Knowledge Base": 15.0,
    "Phase 4 — Knowledge Processing": 5.0,
    "Phase 5 — Local Search / RAG": 15.0,
    "Phase 6 — Local LLM Implementation": 10.0,
    "Phase 7 — Prompt & Guardrails": 5.0,
    "Phase 8 — Troubleshooting Agent": 5.0,
    "Phase 9 — Telegram Integration": 10.0,
    "Phase 10 — Testing & Verification": 5.0,
    "Phase 11 — Performance Optimization": 2.5,
    "Phase 12 — Security": 2.5,
    "Phase 13 — Deployment": 0.0
}

SUPPORT_CONTACTS = {
    "phone": "18002672900",
    "email": "support@escanav.com"
}
