import sqlite3
from collections.abc import Iterator
from pathlib import Path

from .config import get_settings

SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS short_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        short_code TEXT NOT NULL UNIQUE,
        destination TEXT NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT,
        clicks INTEGER NOT NULL DEFAULT 0
    )
    """,
)

COLUMN_ADDITIONS = (
    (
        "short_links",
        "expires_at",
        "ALTER TABLE short_links ADD COLUMN expires_at TEXT",
    ),
    (
        "short_links",
        "clicks",
        "ALTER TABLE short_links ADD COLUMN clicks INTEGER NOT NULL DEFAULT 0",
    ),
)

_SELECT_COLUMN_NAMES = "SELECT name FROM pragma_table_info(?)"


def connect(database_path: str) -> sqlite3.Connection:
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _column_names(connection: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in connection.execute(_SELECT_COLUMN_NAMES, (table,))}


def create_schema(connection: sqlite3.Connection) -> None:
    with connection:
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)
        for table, column, statement in COLUMN_ADDITIONS:
            if column not in _column_names(connection, table):
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
