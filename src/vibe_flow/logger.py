"""
Session logger — writes structured events to SQLite.

Database location:
    <project-root>/logs/vibe_flow.db

Schema:
    session — one row per app launch
    event   — one row per LLM interaction (request, response, user, assistant)
    tool    — one row per tool call, linked to the llm_response that triggered it

Event types and their data shape:
    user         {content}
    llm_request  {messages, tools}
    llm_response {message}
    assistant    {content}
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_DB_PATH: Path = (
    Path(__file__).parent.parent.parent / "logs" / "vibe_flow.db"
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default(obj: Any) -> Any:
    """JSON fallback for Pydantic models."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    raise TypeError(
        f"Object of type {type(obj)} is not JSON serializable"
    )


def _dump(data: dict[str, Any]) -> str:
    return json.dumps(data, default=_default)


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS session (
            id         TEXT PRIMARY KEY,
            cwd        TEXT NOT NULL,
            started_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS event (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL REFERENCES session(id),
            type       TEXT NOT NULL,
            data       TEXT NOT NULL,
            ts         TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tool (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL REFERENCES event(id),
            name     TEXT NOT NULL,
            input    TEXT NOT NULL,
            output   TEXT NOT NULL,
            ts       TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS event_session_idx
            ON event(session_id)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS tool_event_idx
            ON tool(event_id)
    """)
    conn.commit()


class SessionLogger:
    """
    Writes structured log events to SQLite for one session.

    Usage:
        logger = SessionLogger(session_id, cwd)
        logger.log_user("hello")
        ...
        logger.close()
    """

    def __init__(self, session_id: str, cwd: str) -> None:
        self._session_id: str = session_id
        self._conn: sqlite3.Connection = sqlite3.connect(_DB_PATH)
        self._conn.row_factory = sqlite3.Row
        _init_db(self._conn)
        self._conn.execute(
            "INSERT INTO session (id, cwd, started_at) VALUES (?, ?, ?)",
            (session_id, cwd, _now()),
        )
        self._conn.commit()

    def _write(self, type: str, data: dict[str, Any]) -> int:
        """Insert one event row and return its id."""
        cursor = self._conn.execute(
            """
            INSERT INTO event (session_id, type, data, ts)
            VALUES (?, ?, ?, ?)
            """,
            (self._session_id, type, _dump(data), _now()),
        )
        self._conn.commit()
        return cursor.lastrowid

    def log_user(self, content: str) -> None:
        self._write("user", {"content": content})

    def log_llm_request(
        self, messages: list[Any], tools: list[Any]
    ) -> None:
        self._write(
            "llm_request", {"messages": messages, "tools": tools}
        )

    def log_llm_response(self, message: Any) -> int:
        """Insert llm_response event and return its id."""
        return self._write("llm_response", {"message": message})

    def log_tool(
        self,
        event_id: int,
        name: str,
        input: dict[str, Any],
        output: str,
    ) -> None:
        """Insert one tool row linked to the llm_response event."""
        self._conn.execute(
            """
            INSERT INTO tool (event_id, name, input, output, ts)
            VALUES (?, ?, ?, ?, ?)
            """,
            (event_id, name, _dump(input), output, _now()),
        )
        self._conn.commit()

    def log_assistant(self, content: str) -> None:
        self._write("assistant", {"content": content})

    def close(self) -> None:
        self._conn.close()
