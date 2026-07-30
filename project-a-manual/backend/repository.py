import sqlite3
from datetime import datetime, timezone

from .schemas import Note

_NOTE_COLUMNS = "id, title, body, created_at, updated_at"

_INSERT_NOTE = f"""
    INSERT INTO notes (title, body, created_at, updated_at)
    VALUES (?, ?, ?, ?)
    RETURNING {_NOTE_COLUMNS}
"""

_SELECT_LIVE_NOTES = f"""
    SELECT {_NOTE_COLUMNS}
    FROM notes
    WHERE deleted_at IS NULL
    ORDER BY updated_at DESC, id DESC
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_note(row: sqlite3.Row) -> Note:
    return Note(
        id=row["id"],
        title=row["title"],
        body=row["body"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create_note(connection: sqlite3.Connection, title: str, body: str) -> Note:
    timestamp = _now()
    with connection:
        row = connection.execute(
            _INSERT_NOTE, (title, body, timestamp, timestamp)
        ).fetchone()
    return _to_note(row)


def list_notes(connection: sqlite3.Connection) -> list[Note]:
    rows = connection.execute(_SELECT_LIVE_NOTES).fetchall()
    return [_to_note(row) for row in rows]
