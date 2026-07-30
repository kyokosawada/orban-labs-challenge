import sqlite3
from collections.abc import Iterator
from pathlib import Path

from .config import get_settings

SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        deleted_at TEXT
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS notes_live_by_recency
        ON notes (deleted_at, updated_at DESC, id DESC)
    """,
)


def connect(database_path: str) -> sqlite3.Connection:
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_schema(connection: sqlite3.Connection) -> None:
    with connection:
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)


def initialise_database() -> None:
    connection = connect(get_settings().database_path)
    try:
        create_schema(connection)
    finally:
        connection.close()


def get_connection() -> Iterator[sqlite3.Connection]:
    connection = connect(get_settings().database_path)
    try:
        yield connection
    finally:
        connection.close()
