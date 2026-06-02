"""
auth.py
Authentication backend for NaijaCodeMix.
Stores users and their data in a local JSON file (users_db.json).
Lives at the project root, imported by both app.py and pages.
"""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path

# Always save users_db.json at the project root (one level up from auth.py)
DB_PATH = Path(__file__).parent / "users_db.json"


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load_db() -> dict:
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "r") as f:
        return json.load(f)


def _save_db(db: dict):
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ── Public API ────────────────────────────────────────────────────────────────

def register_user(full_name: str, username: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.
    Returns (success: bool, message: str).
    """
    db = _load_db()
    username = username.strip().lower()

    if not full_name.strip() or not username or not password:
        return False, "All fields are required."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if username in db:
        return False, "That username is already taken."

    db[username] = {
        "full_name":     full_name.strip(),
        "password_hash": _hash(password),
        "created_at":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "history":       [],   # auto-saved analyses (max 50)
        "saved":         [],   # bookmarked analyses (max 20)
    }
    _save_db(db)
    return True, "Account created successfully."


def login_user(username: str, password: str) -> tuple[bool, str, dict | None]:
    """
    Authenticate a user.
    Returns (success, message, user_data_without_hash | None).
    """
    db = _load_db()
    username = username.strip().lower()

    if username not in db:
        return False, "Username not found.", None
    if db[username]["password_hash"] != _hash(password):
        return False, "Incorrect password.", None

    user = {k: v for k, v in db[username].items() if k != "password_hash"}
    return True, "Login successful.", user


def get_user_data(username: str) -> dict | None:
    """Return full user record (without password hash), or None."""
    db = _load_db()
    username = username.strip().lower()
    if username not in db:
        return None
    return {k: v for k, v in db[username].items() if k != "password_hash"}


def save_to_history(username: str, analysis: dict):
    """Append an analysis to the user's history. Keeps the last 50."""
    db = _load_db()
    username = username.strip().lower()
    if username not in db:
        return

    entry = {
        "id":        f"h_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **analysis,
    }
    db[username]["history"].insert(0, entry)
    db[username]["history"] = db[username]["history"][:50]
    _save_db(db)


def save_bookmark(username: str, analysis: dict) -> tuple[bool, str]:
    """Bookmark a specific analysis. Max 20 per user."""
    db = _load_db()
    username = username.strip().lower()
    if username not in db:
        return False, "User not found."
    if len(db[username]["saved"]) >= 20:
        return False, "Maximum of 20 saved analyses reached. Delete one first."

    entry = {
        "id":       f"s_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **analysis,
    }
    db[username]["saved"].insert(0, entry)
    _save_db(db)
    return True, "Analysis saved successfully."


def delete_bookmark(username: str, entry_id: str) -> bool:
    """Delete a saved analysis by ID."""
    db = _load_db()
    username = username.strip().lower()
    if username not in db:
        return False
    db[username]["saved"] = [
        e for e in db[username]["saved"] if e.get("id") != entry_id
    ]
    _save_db(db)
    return True