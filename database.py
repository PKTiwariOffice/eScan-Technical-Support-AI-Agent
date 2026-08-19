import sqlite3
import json
import os
from datetime import datetime
from config import DB_PATH, DEFAULT_PHASE_WEIGHTS

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            phase TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT CHECK(priority IN ('P0', 'P1', 'P2', 'P3')),
            impl_status TEXT CHECK(impl_status IN ('Not Started', 'Planned', 'In Progress', 'Implemented', 'Blocked', 'Deferred', 'Rejected')),
            verif_status TEXT CHECK(verif_status IN ('Not Verified', 'Verification Pending', 'Verified')),
            owner TEXT,
            dependency TEXT,
            acceptance_criteria TEXT,
            verif_method TEXT,
            evidence TEXT,
            notes TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phase_weights (
            phase TEXT PRIMARY KEY,
            weight REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decisions (
            id TEXT PRIMARY KEY,
            decision TEXT NOT NULL,
            reason TEXT NOT NULL,
            alternatives TEXT,
            selected_option TEXT NOT NULL,
            impact TEXT,
            status TEXT CHECK(status IN ('Approved', 'Under Evaluation', 'Rejected', 'Superseded')),
            evidence TEXT,
            notes TEXT,
            created_at TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS risks (
            id TEXT PRIMARY KEY,
            risk TEXT NOT NULL,
            probability TEXT CHECK(probability IN ('Low', 'Medium', 'High')),
            impact TEXT CHECK(impact IN ('Low', 'Medium', 'High', 'Critical')),
            severity TEXT CHECK(severity IN ('Low', 'Medium', 'High', 'Critical')),
            mitigation TEXT,
            status TEXT CHECK(status IN ('Identified Risk', 'Active Blocker', 'Mitigated', 'Closed')),
            owner TEXT,
            notes TEXT,
            created_at TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_evals (
            id TEXT PRIMARY KEY,
            model_name TEXT NOT NULL,
            quantization TEXT,
            ram_usage_mb REAL,
            cpu_usage_pct REAL,
            response_time_sec REAL,
            accuracy_score REAL,
            test_result TEXT,
            recommendation TEXT,
            evidence TEXT,
            created_at TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tests (
            id TEXT PRIMARY KEY,
            scenario TEXT NOT NULL,
            expected_result TEXT NOT NULL,
            actual_result TEXT,
            status TEXT CHECK(status IN ('Not Started', 'Pass', 'Fail', 'Blocked')),
            evidence TEXT,
            notes TEXT,
            updated_at TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS change_log (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            change TEXT NOT NULL,
            reason TEXT,
            impact TEXT,
            author TEXT,
            status TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documentation (
            doc_type TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    conn.close()

def compute_weighted_progress():
    conn = get_connection()
    cursor = conn.cursor()
    
    weights = dict(cursor.execute("SELECT phase, weight FROM phase_weights").fetchall())
    tasks = cursor.execute("SELECT phase, impl_status, verif_status FROM tasks").fetchall()
    conn.close()

    if not weights or not tasks:
        return {"planned": 0.0, "implemented": 0.0, "verified": 0.0}

    phase_totals = {p: 0 for p in weights}
    phase_impl = {p: 0 for p in weights}
    phase_verif = {p: 0 for p in weights}

    for t in tasks:
        p = t['phase']
        if p in phase_totals:
            phase_totals[p] += 1
            if t['impl_status'] in ('Implemented', 'Verified'):
                phase_impl[p] += 1
            if t['verif_status'] == 'Verified':
                phase_verif[p] += 1

    total_weight = sum(weights.values()) or 1.0
    impl_pct = 0.0
    verif_pct = 0.0

    for p, w in weights.items():
        tot = phase_totals[p]
        if tot > 0:
            impl_pct += (phase_impl[p] / tot) * w
            verif_pct += (phase_verif[p] / tot) * w

    return {
        "planned": 100.0,
        "implemented": round((impl_pct / total_weight) * 100, 1),
        "verified": round((verif_pct / total_weight) * 100, 1)
    }

def get_next_recommended_action():
    p0_blocked = query_db("SELECT * FROM tasks WHERE impl_status='Blocked' AND priority='P0'", one=True)
    if p0_blocked:
        return f"CRITICAL BLOCKER (P0): Resolve blockage on '{p0_blocked['title']}' ({p0_blocked['id']})."

    verif_pending = query_db("SELECT * FROM tasks WHERE verif_status='Verification Pending' AND priority IN ('P0', 'P1')", one=True)
    if verif_pending:
        return f"VERIFICATION REQUIRED: Audit evidence and verify '{verif_pending['title']}' ({verif_pending['id']})."

    p1_task = query_db("SELECT * FROM tasks WHERE impl_status IN ('Not Started', 'In Progress') AND priority='P1' ORDER BY id ASC", one=True)
    if p1_task:
        return f"NEXT ACTION: Execute P1 task '{p1_task['title']}' ({p1_task['id']}) in {p1_task['phase']}."

    any_task = query_db("SELECT * FROM tasks WHERE impl_status IN ('Not Started', 'In Progress') ORDER BY priority ASC, id ASC", one=True)
    if any_task:
        return f"NEXT ACTION: Work on '{any_task['title']}' ({any_task['id']})."

    return "NEXT ACTION: All current project tasks are fully implemented and verified."
