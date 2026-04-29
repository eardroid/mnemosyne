"""sqlite_memory.py — a memory store that survives restarts.

This is a drop-in replacement for SimpleMemory in guard.py. Same three
methods (add / search / get_all), but the data lives in a SQLite file
instead of RAM, so the agent still "remembers" after the program exits.

Why SQLite and not Mem0/Postgres? Because it needs zero setup, zero
keys, and zero server — just a file. That keeps the project student-level
while making the "the agent remembers" story real.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


class SqliteMemory:
    """A tiny persistent memory store backed by SQLite."""

    def __init__(self, db_path: str = "agent_memory.db") -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                memory  TEXT
            )
            """
        )
        self._conn.commit()

    def add(self, content: str) -> int:
        cur = self._conn.execute(
            "INSERT INTO memories (memory) VALUES (?)", (content,)
        )
        self._conn.commit()
        return cur.lastrowid

    def search(self, query: str) -> list[dict]:


        q_words = set(query.lower().split())
        rows = self._conn.execute("SELECT id, memory FROM memories").fetchall()
        return [
            {"id": r["id"], "memory": r["memory"]}
            for r in rows
            if q_words & set(r["memory"].lower().split())
        ]

    def get_all(self) -> list[dict]:
        rows = self._conn.execute("SELECT id, memory FROM memories").fetchall()
        return [{"id": r["id"], "memory": r["memory"]} for r in rows]

    def delete(self, mem_id: int) -> None:
        self._conn.execute("DELETE FROM memories WHERE id = ?", (mem_id,))
        self._conn.commit()

    def clear(self) -> None:
        self._conn.execute("DELETE FROM memories")
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
