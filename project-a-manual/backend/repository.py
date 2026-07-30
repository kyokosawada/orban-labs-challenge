import sqlite3
from collections import defaultdict
from datetime import datetime, timezone

from .schemas import Note

_NOTE_COLUMNS = "id, title, body, created_at, updated_at"

_INSERT_NOTE = f"""
    INSERT INTO notes (title, body, created_at, updated_at)
    VALUES (?, ?, ?, ?)
    RETURNING {_NOTE_COLUMNS}
"""

_NOT_DELETED = "deleted_at IS NULL"

_IS_NOTE = "id = ?"

_UPDATE_NOTE = f"""
    UPDATE notes
    SET title = ?, body = ?, updated_at = ?
    WHERE {_IS_NOTE} AND {_NOT_DELETED}
    RETURNING {_NOTE_COLUMNS}
"""

_SELECT_NOTES = f"""
    SELECT {{columns}}
    FROM notes
    WHERE {_NOT_DELETED}{{narrowing}}
    ORDER BY updated_at DESC, id DESC
"""

_MARK_NOTE_DELETED = f"""
    UPDATE notes
    SET deleted_at = ?
    WHERE {_IS_NOTE} AND {_NOT_DELETED}
"""

_CARRIES_TAG = """
    id IN (
        SELECT note_tags.note_id
        FROM note_tags
        JOIN tags ON tags.id = note_tags.tag_id
        WHERE tags.name = ?
    )
"""

_MENTIONS_KEYWORD = """
    (lowercased(title) LIKE ? ESCAPE '\\' OR lowercased(body) LIKE ? ESCAPE '\\')
"""

_LIKE_SPECIAL_CHARACTERS = ("\\", "%", "_")

_INSERT_TAG = "INSERT INTO tags (name) VALUES (?) ON CONFLICT (name) DO NOTHING"

_ATTACH_TAG = """
    INSERT INTO note_tags (note_id, tag_id)
    SELECT ?, id FROM tags WHERE name = ?
"""

_DETACH_EVERY_TAG = "DELETE FROM note_tags WHERE note_id = ?"

_SELECT_TAGS_OF_NOTES = f"""
    SELECT note_tags.note_id, tags.name
    FROM note_tags
    JOIN tags ON tags.id = note_tags.tag_id
    WHERE note_tags.note_id IN (
        SELECT id FROM notes WHERE {_NOT_DELETED}{{narrowing}}
    )
    ORDER BY tags.name
"""

_SELECT_TAGS_IN_USE = """
    SELECT DISTINCT tags.name
    FROM tags
    JOIN note_tags ON note_tags.tag_id = tags.id
    JOIN notes ON notes.id = note_tags.note_id
    WHERE notes.deleted_at IS NULL
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
    connection: sqlite3.Connection, narrowing: str, parameters: list[object]
) -> defaultdict[int, list[str]]:
    statement = _SELECT_TAGS_OF_NOTES.format(narrowing=narrowing)
    tags: defaultdict[int, list[str]] = defaultdict(list)
    for row in connection.execute(statement, parameters):
        tags[row["note_id"]].append(row["name"])
    return tags


def _attach_tags(connection: sqlite3.Connection, note_id: int, tags: list[str]) -> None:
    connection.executemany(_INSERT_TAG, [(tag,) for tag in tags])
    connection.executemany(_ATTACH_TAG, [(note_id, tag) for tag in tags])


def _like_pattern(keyword: str) -> str:
    keyword = keyword.lower()
    for character in _LIKE_SPECIAL_CHARACTERS:
        keyword = keyword.replace(character, f"\\{character}")
    return f"%{keyword}%"


def _narrowed_by(*conditions: str) -> str:
    return "".join(f" AND {condition}" for condition in conditions)


def _selection(tag: str | None, keyword: str | None) -> tuple[str, list[object]]:
    conditions: list[str] = []
    parameters: list[object] = []
    if tag is not None:
        conditions.append(_CARRIES_TAG)
        parameters.append(tag)
    if keyword is not None:
        conditions.append(_MENTIONS_KEYWORD)
        parameters += [_like_pattern(keyword)] * 2
    return _narrowed_by(*conditions), parameters


def _with_its_tags(connection: sqlite3.Connection, row: sqlite3.Row) -> Note:
    written = _tags_of_notes(connection, _narrowed_by(_IS_NOTE), [row["id"]])
    return _to_note(row, written[row["id"]])


def create_note(
    connection: sqlite3.Connection, title: str, body: str, tags: list[str]
) -> Note:
    timestamp = _now()
    with connection:
        row = connection.execute(
            _INSERT_NOTE, (title, body, timestamp, timestamp)
        ).fetchone()
        _attach_tags(connection, row["id"], tags)
    return _with_its_tags(connection, row)


def replace_note(
    connection: sqlite3.Connection,
    note_id: int,
    title: str,
    body: str,
    tags: list[str],
) -> Note | None:
    with connection:
        row = connection.execute(
            _UPDATE_NOTE, (title, body, _now(), note_id)
        ).fetchone()
        if row is None:
            return None
        connection.execute(_DETACH_EVERY_TAG, (note_id,))
        _attach_tags(connection, note_id, tags)
    return _with_its_tags(connection, row)


def list_notes(
    connection: sqlite3.Connection,
    tag: str | None = None,
    keyword: str | None = None,
) -> list[Note]:
    narrowing, parameters = _selection(tag, keyword)
    statement = _SELECT_NOTES.format(columns=_NOTE_COLUMNS, narrowing=narrowing)
    rows = connection.execute(statement, parameters).fetchall()
    tags = _tags_of_notes(connection, narrowing, parameters)
    return [_to_note(row, tags[row["id"]]) for row in rows]


def read_note(connection: sqlite3.Connection, note_id: int) -> Note | None:
    narrowing = _narrowed_by(_IS_NOTE)
    statement = _SELECT_NOTES.format(columns=_NOTE_COLUMNS, narrowing=narrowing)
    row = connection.execute(statement, [note_id]).fetchone()
    if row is None:
        return None
    tags = _tags_of_notes(connection, narrowing, [note_id])
    return _to_note(row, tags[row["id"]])


def delete_note(connection: sqlite3.Connection, note_id: int) -> bool:
    with connection:
        return connection.execute(
            _MARK_NOTE_DELETED, (_now(), note_id)
        ).rowcount == 1


def list_tags_in_use(connection: sqlite3.Connection) -> list[str]:
    return [row["name"] for row in connection.execute(_SELECT_TAGS_IN_USE)]
