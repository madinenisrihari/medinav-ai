"""
db.py — SQLite persistence layer for MediNav AI.

Handles real user accounts (registration + login with salted/hashed
passwords) and appointment bookings. Uses only the Python standard
library, so no extra dependencies beyond Streamlit are required.

The database file (medinav.db) is created automatically next to this
file the first time the app runs, and data persists across restarts
as long as that file isn't deleted.
"""

import sqlite3
import hashlib
import os
import secrets
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medinav.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist yet. Safe to call every run."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            hospital TEXT,
            doctor TEXT,
            department TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------- #
# Password hashing (PBKDF2-HMAC-SHA256, per-user random salt)
# ---------------------------------------------------------------- #

def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    ).hex()


def create_user(name: str, email: str, phone: str, password: str):
    """Returns (True, user_dict) on success, (False, error_message) on failure."""
    email = email.strip().lower()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cur.fetchone():
        conn.close()
        return False, "An account with this email already exists. Try logging in instead."

    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)
    created_at = datetime.utcnow().isoformat()

    cur.execute(
        "INSERT INTO users (name, email, phone, salt, password_hash, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (name.strip(), email, phone.strip(), salt, password_hash, created_at),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return True, {"id": user_id, "name": name.strip(), "email": email, "phone": phone.strip()}


def verify_login(email: str, password: str):
    """Returns (True, user_dict) on success, (False, error_message) on failure."""
    email = email.strip().lower()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return False, "No account found with that email. Try creating one first."

    candidate_hash = _hash_password(password, row["salt"])
    if candidate_hash != row["password_hash"]:
        return False, "Incorrect password. Please try again."

    return True, {"id": row["id"], "name": row["name"], "email": row["email"], "phone": row["phone"]}


# ---------------------------------------------------------------- #
# Bookings
# ---------------------------------------------------------------- #

def create_booking(user_id: int, hospital: str = None, doctor: str = None, department: str = None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO bookings (user_id, hospital, doctor, department, status, created_at) VALUES (?, ?, ?, ?, 'Pending', ?)",
        (user_id, hospital, doctor, department, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_bookings_for_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bookings WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------- #
# Contact messages
# ---------------------------------------------------------------- #

def save_contact_message(name: str, email: str, phone: str, message: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO contact_messages (name, email, phone, message, created_at) VALUES (?, ?, ?, ?, ?)",
        (name, email, phone, message, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
