import sqlite3
from datetime import datetime, timezone

from .codes import ShortCodeSource
from .schemas import ShortLink

SHORT_CODE_ATTEMPTS = 5

_SHORT_LINK_COLUMNS = "short_code, destination, created_at, expires_at, clicks"

_INSERT_SHORT_LINK = f"""
    INSERT INTO short_links (short_code, destination, created_at, expires_at)
    VALUES (?, ?, ?, ?)
    RETURNING {_SHORT_LINK_COLUMNS}
"""


class ShortCodeUnavailable(RuntimeError):
    pass


_RESOLVE_BY_SHORT_CODE = f"""
    UPDATE short_links
    SET clicks = clicks + 1
    WHERE short_code = ?
      AND (expires_at IS NULL OR expires_at > ?)
    RETURNING {_SHORT_LINK_COLUMNS}
"""

_SELECT_ALL = f"""
    SELECT {_SHORT_LINK_COLUMNS}
    FROM short_links
    ORDER BY id DESC
"""


def _stored_moment(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _to_short_link(row: sqlite3.Row) -> ShortLink:
    return ShortLink(
        short_code=row["short_code"],
        destination=row["destination"],
        created_at=row["created_at"],
        expires_at=row["expires_at"],
        clicks=row["clicks"],
    )


def create_short_link(
    connection: sqlite3.Connection,
    destination: str,
    generate_code: ShortCodeSource,
    created_at: datetime,
    expires_at: datetime | None,
) -> ShortLink:
    for _ in range(SHORT_CODE_ATTEMPTS):
        try:
            with connection:
                row = connection.execute(
                    _INSERT_SHORT_LINK,
                    (
                        generate_code(),
                        destination,
                        _stored_moment(created_at),
                        _stored_moment(expires_at),
                    ),
                ).fetchone()
        except sqlite3.IntegrityError:
            continue
        return _to_short_link(row)
    raise ShortCodeUnavailable(
        f"No free Short Code was found in {SHORT_CODE_ATTEMPTS} attempts."
    )


def resolve_short_link(
    connection: sqlite3.Connection, short_code: str, now: datetime
) -> ShortLink | None:
    with connection:
        row = connection.execute(
            _RESOLVE_BY_SHORT_CODE, (short_code, _stored_moment(now))
        ).fetchone()
    return _to_short_link(row) if row is not None else None


def list_short_links(connection: sqlite3.Connection) -> list[ShortLink]:
    return [_to_short_link(row) for row in connection.execute(_SELECT_ALL)]
