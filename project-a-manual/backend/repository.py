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
    WHERE {{conditions}}
    ORDER BY updated_at DESC, id DESC
"""

_NOT_DELETED = "deleted_at IS NULL"

_CARRIES_TAG = """
    id IN (
        SELECT note_tags.note_id
        FROM note_tags
        JOIN tags ON tags.id = note_tags.tag_id
        WHERE tags.name = ?
    )
"""

_INSERT_TAG = "INSERT INTO tags (name) VALUES (?) ON CONFLICT (name) DO NOTHING"

_ATTACH_TAG = """
    INSERT INTO note_tags (note_id, tag_id)
    SELECT ?, id FROM tags WHERE name = ?
"""

_SELECT_TAGS_OF_NOTES = """
    SELECT note_tags.note_id, tags.name
    FROM note_tags
    JOIN tags ON tags.id = note_tags.tag_id
    WHERE note_tags.note_id IN ({placeholders})
    ORDER BY tags.name
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_note(row: sqlite3.Row, tags: list[str]) -> Note:
    return Note(
        id=row["id"],
        title=row["title"],
        body=row["body"],
        tags=tags,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _tags_of_notes(
    connection: sqlite3.Connection, note_ids: list[int]
) -> dict[int, list[str]]:
    if not note_ids:
        return {}
    statement = _SELECT_TAGS_OF_NOTES.format(
        placeholders=", ".join("?" * len(note_ids))
    )
    tags: dict[int, list[str]] = {note_id: [] for note_id in note_ids}
    for row in connection.execute(statement, note_ids):
        tags[row["note_id"]].append(row["name"])
    return tags


def _attach_tags(connection: sqlite3.Connection, note_id: int, tags: list[str]) -> None:
    connection.executemany(_INSERT_TAG, [(tag,) for tag in tags])
    connection.executemany(_ATTACH_TAG, [(note_id, tag) for tag in tags])


def create_note(
    connection: sqlite3.Connection, title: str, body: str, tags: list[str]
) -> Note:
    timestamp = _now()
    with connection:
        row = connection.execute(
            _INSERT_NOTE, (title, body, timestamp, timestamp)
        ).fetchone()
        _attach_tags(connection, row["id"], tags)
    return _to_note(row, _tags_of_notes(connection, [row["id"]])[row["id"]])


def list_notes(
    connection: sqlite3.Connection, tag: str | None = None
) -> list[Note]:
    conditions = [_NOT_DELETED]
    parameters: list[str] = []
    if tag is not None:
        conditions.append(_CARRIES_TAG)
        parameters.append(tag)
    statement = _SELECT_LIVE_NOTES.format(conditions=" AND ".join(conditions))
    rows = connection.execute(statement, parameters).fetchall()
    tags = _tags_of_notes(connection, [row["id"] for row in rows])
    return [_to_note(row, tags[row["id"]]) for row in rows]
