"""Persistent memory and learning storage for the conversation robot."""

import os
import sqlite3
from datetime import datetime


class Memory:
    """Stores conversation history, learned facts, and user preferences."""

    def __init__(self, db_path="data/memory.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp   TEXT NOT NULL,
                    user_input  TEXT NOT NULL,
                    robot_response TEXT NOT NULL,
                    sentiment   REAL DEFAULT 0.0
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS learned_facts (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic       TEXT NOT NULL,
                    fact        TEXT NOT NULL,
                    confidence  REAL DEFAULT 1.0,
                    created_at  TEXT NOT NULL,
                    updated_at  TEXT NOT NULL,
                    UNIQUE(topic, fact)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key         TEXT PRIMARY KEY,
                    value       TEXT NOT NULL,
                    updated_at  TEXT NOT NULL
                )
                """
            )

    # ------------------------------------------------------------------
    # Conversations
    # ------------------------------------------------------------------

    def store_conversation(self, user_input: str, robot_response: str, sentiment: float = 0.0):
        """Persist a conversation exchange."""
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO conversations (timestamp, user_input, robot_response, sentiment) VALUES (?, ?, ?, ?)",
                (datetime.now().isoformat(), user_input, robot_response, sentiment),
            )

    def get_recent_conversations(self, limit: int = 10):
        """Return the most recent conversations as (timestamp, user_input, robot_response) tuples."""
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT timestamp, user_input, robot_response FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            return cursor.fetchall()

    # ------------------------------------------------------------------
    # Learning
    # ------------------------------------------------------------------

    def learn_fact(self, topic: str, fact: str):
        """Store a new fact or strengthen confidence in an existing one."""
        now = datetime.now().isoformat()
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT id, confidence FROM learned_facts WHERE topic=? AND fact=?",
                (topic, fact),
            ).fetchone()
            if existing:
                new_confidence = min(existing[1] + 0.1, 1.0)
                conn.execute(
                    "UPDATE learned_facts SET confidence=?, updated_at=? WHERE id=?",
                    (new_confidence, now, existing[0]),
                )
            else:
                conn.execute(
                    "INSERT INTO learned_facts (topic, fact, confidence, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (topic, fact, 1.0, now, now),
                )

    def recall_facts(self, topic: str):
        """Return (fact, confidence) pairs related to *topic*, best first.

        Searches both the *topic* field and the *fact* content so that,
        e.g., recalling "sky" will find facts whose text mentions "sky".
        """
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT fact, confidence
                FROM learned_facts
                WHERE topic LIKE ? OR fact LIKE ?
                ORDER BY confidence DESC
                """,
                (f"%{topic}%", f"%{topic}%"),
            )
            return cursor.fetchall()

    # ------------------------------------------------------------------
    # User preferences
    # ------------------------------------------------------------------

    def set_preference(self, key: str, value: str):
        """Save or update a user preference."""
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO user_preferences (key, value, updated_at) VALUES (?, ?, ?)",
                (key, str(value), datetime.now().isoformat()),
            )

    def get_preference(self, key: str, default=None):
        """Retrieve a user preference, returning *default* if not found."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM user_preferences WHERE key=?", (key,)
            ).fetchone()
            return row[0] if row else default
