import sqlite3
from datetime import datetime, timezone

from .codes import ShortCodeSource
from .schemas import ShortLink

_SHORT_LINK_COLUMNS = "short_code, destination, created_at"

_INSERT_SHORT_LINK = f"""
    INSERT INTO short_links (short_code, destination, created_at)
    VALUES (?, ?, ?)
    RETURNING {_SHORT_LINK_COLUMNS}
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_short_link(row: sqlite3.Row) -> ShortLink:
    return ShortLink(
        short_code=row["short_code"],
        destination=row["destination"],
        created_at=row["created_at"],
    )


def create_short_link(
    connection: sqlite3.Connection,
    destination: str,
    generate_code: ShortCodeSource,
) -> ShortLink:
    with connection:
        row = connection.execute(
            _INSERT_SHORT_LINK, (generate_code(), destination, _now())
        ).fetchone()
    return _to_short_link(row)
