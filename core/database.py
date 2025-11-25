import sqlite3
from datetime import datetime

DB_NAME = "history.db"


# ---------------------------------------------------------
# INIT DATABASE
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS scans(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            ttfb INTEGER,
            load INTEGER,
            lcp INTEGER,
            size INTEGER,
            requests INTEGER,
            created_at TEXT,
            raw_json TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# SAVE SCAN RESULT
# ---------------------------------------------------------
def save_scan(data: dict):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        INSERT INTO scans (url, ttfb, load, lcp, size, requests, created_at, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["url"],
        data["metrics"]["ttfb"],
        data["metrics"]["load"],
        int(data["vitals"]["LCP"]),
        data["total_size"],
        data["total_requests"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        str(data)
    ))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# GET ALL HISTORY
# ---------------------------------------------------------
def get_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT id, url, ttfb, load, lcp, size, requests, created_at FROM scans ORDER BY id DESC")

    rows = c.fetchall()
    conn.close()

    return rows


# ---------------------------------------------------------
# GET ONE RECORD (FULL JSON)
# ---------------------------------------------------------
def get_scan(id: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT raw_json FROM scans WHERE id = ?", (id,))
    row = c.fetchone()

    conn.close()

    if row:
        return eval(row[0])     # vì raw_json là string of dict
    return None


# ---------------------------------------------------------
# DELETE ONE RECORD
# ---------------------------------------------------------
def delete_history(id: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("DELETE FROM scans WHERE id = ?", (id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------
# DELETE ALL
# ---------------------------------------------------------
def clear_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("DELETE FROM scans")
    conn.commit()
    conn.close()
