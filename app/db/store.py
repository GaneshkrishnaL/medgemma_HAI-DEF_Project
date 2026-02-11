import sqlite3
from pathlib import Path
from typing import Any
import time

DB_PATH = Path("medgemma_copilot.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        # User table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
        """)
        
        # Chat sessions table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username)
        )
        """)
        
        # Chat messages table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL, -- 'user' or 'assistant'
            content TEXT NOT NULL,
            image_path TEXT,
            created_at INTEGER NOT NULL,
            FOREIGN KEY(session_id) REFERENCES chat_sessions(session_id)
        )
        """)

        # Health Vitals (BP/Sugar)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS health_vitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            vitals_type TEXT NOT NULL, -- 'blood_pressure' or 'sugar'
            value_main REAL NOT NULL, -- systolic or glucose level
            value_secondary REAL, -- diastolic (for BP)
            notes TEXT,
            created_at INTEGER NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username)
        )
        """)
        
        conn.commit()

# --- User Auth ---
def create_user(username, password):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(username, password):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT password FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if row and row[0] == password:
            return True
    return False

# --- Chat Sessions ---
def create_session(username, title):
    session_id = f"{username}_{int(time.time())}"
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO chat_sessions (session_id, username, title, created_at) VALUES (?, ?, ?, ?)",
            (session_id, username, title, int(time.time()))
        )
        conn.commit()
    return session_id

def get_user_sessions(username):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT session_id, title FROM chat_sessions WHERE username=? ORDER BY created_at DESC", (username,))
        return cur.fetchall()

def add_message(session_id, role, content, image_path=None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, image_path, created_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, content, image_path, int(time.time()))
        )
        conn.commit()

def get_session_messages(session_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT role, content, image_path FROM messages WHERE session_id=? ORDER BY created_at ASC", (session_id,))
        return cur.fetchall()

# --- Health Vitals ---
def add_vital(username, vitals_type, v1, v2=None, notes=None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO health_vitals (username, vitals_type, value_main, value_secondary, notes, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (username, vitals_type, v1, v2, notes, int(time.time()))
        )
        conn.commit()

def get_vitals_history(username, vitals_type):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT value_main, value_secondary, notes, created_at FROM health_vitals WHERE username=? AND vitals_type=? ORDER BY created_at ASC",
            (username, vitals_type)
        )
        return cur.fetchall()
