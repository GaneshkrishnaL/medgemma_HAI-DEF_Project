import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path("medgemma_copilot.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            question TEXT NOT NULL,
            pasted_text TEXT,
            answer TEXT NOT NULL
        )
        """)
        conn.commit()

def add_record(user_id: str, created_at: int, question: str, pasted_text: str | None, answer: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO records (user_id, created_at, question, pasted_text, answer) VALUES (?, ?, ?, ?, ?)",
            (user_id, created_at, question, pasted_text, answer),
        )
        conn.commit()

def get_recent_records(user_id: str, limit: int = 20) -> list[dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT created_at, question, answer FROM records WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        )
        rows = cur.fetchall()
    return [{"created_at": r[0], "question": r[1], "answer": r[2]} for r in rows]
