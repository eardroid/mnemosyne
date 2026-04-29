"""ledger.py — an append-only log of every memory write.

This is the "paper trail" part of the project. Every time the guard
looks at a piece of text (whether it ends up stored or blocked), we
write one row here. The rows are chained together with hashes so that,
if anyone went back and edited an old row, we would be able to tell.

You do NOT need any API keys or internet to use this file. It is just
plain SQLite, which comes built into Python.
"""

import hashlib
import sqlite3
from datetime import datetime, timezone


GENESIS = "GENESIS"


class Ledger:
    """Stores memory-write events in a small SQLite database."""

    def __init__(self, db_path: str = "mnemosyne.db"):


        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_log (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                content         TEXT,
                source          TEXT,
                trust_level     TEXT,
                status          TEXT,
                attack_type     TEXT,
                confidence      REAL,
                reason          TEXT,
                matched_patterns TEXT,
                timestamp       TEXT,
                content_hash    TEXT,
                prev_hash       TEXT
            )
            """
        )
        self._conn.commit()

    def log(
        self,
        content: str,
        source: str,
        trust_level: str,
        status: str,
        attack_type: str = "none",
        confidence: float = 0.0,
        reason: str = "",
        matched_patterns: list[str] | None = None,
    ) -> dict:
        """Add one event row. Returns the row that was written.

        The row also carries a SHA-256 hash of its own content plus the
        hash of the previous row, forming a chain.
        """
        matched_patterns = matched_patterns or []
        timestamp = datetime.now(timezone.utc).isoformat()

        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        prev_hash = self._last_hash()

        self._conn.execute(
            """
            INSERT INTO memory_log
                (content, source, trust_level, status, attack_type,
                 confidence, reason, matched_patterns, timestamp,
                 content_hash, prev_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                content,
                source,
                trust_level,
                status,
                attack_type,
                confidence,
                reason,
                ", ".join(matched_patterns),
                timestamp,
                content_hash,
                prev_hash,
            ),
        )
        self._conn.commit()

        row = self.get_recent(1)
        return row[0] if row else {}

    def _last_hash(self) -> str:
        """Return the content_hash of the most recent row (or GENESIS)."""
        cur = self._conn.execute(
            "SELECT content_hash FROM memory_log ORDER BY id DESC LIMIT 1"
        )
        row = cur.fetchone()
        return row["content_hash"] if row else GENESIS

    def get_recent(self, n: int = 20) -> list[dict]:
        """Return the last *n* rows, most recent first."""
        cur = self._conn.execute(
            "SELECT * FROM memory_log ORDER BY id DESC LIMIT ?", (n,)
        )
        return [dict(r) for r in cur.fetchall()]

    def get_stats(self) -> dict:
        """Count how many writes were stored vs blocked vs total."""
        cur = self._conn.execute
        total = cur("SELECT COUNT(*) FROM memory_log").fetchone()[0]
        stored = cur(
            "SELECT COUNT(*) FROM memory_log WHERE status = 'STORED'"
        ).fetchone()[0]
        blocked = cur(
            "SELECT COUNT(*) FROM memory_log WHERE status = 'BLOCKED'"
        ).fetchone()[0]
        return {"total": total, "stored": stored, "blocked": blocked}

    def verify_chain(self) -> bool:
        """Walk the chain and return True only if no row was tampered with.

        We recompute each row's expected content_hash from the stored
        content, and check that each row's prev_hash matches the actual
        hash of the row before it.
        """
        rows = self._conn.execute(
            "SELECT * FROM memory_log ORDER BY id ASC"
        ).fetchall()
        if not rows:
            return True

        expected_prev = GENESIS
        for row in rows:
            actual_content_hash = hashlib.sha256(
                row["content"].encode("utf-8")
            ).hexdigest()
            if actual_content_hash != row["content_hash"]:
                return False
            if row["prev_hash"] != expected_prev:
                return False
            expected_prev = row["content_hash"]
        return True

    def close(self) -> None:
        self._conn.close()
