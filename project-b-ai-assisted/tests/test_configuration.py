import sqlite3
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from backend.config import ConfigurationError, get_settings

A_SHORT_LINK_PREDATING_CLICKS = (
    "Legacy1",
    "https://example.com/created-before-clicks-were-counted",
    "2026-01-01T00:00:00+00:00",
)

_SCHEMA_BEFORE_CLICKS_WERE_COUNTED = """
    CREATE TABLE short_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        short_code TEXT NOT NULL UNIQUE,
        destination TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
"""


def test_the_service_refuses_to_start_without_a_key(monkeypatch, database_path):
    monkeypatch.delenv("SHORTENER_API_KEY", raising=False)
    monkeypatch.setenv("SHORTENER_DATABASE_PATH", database_path)
    get_settings.cache_clear()

    from backend.main import create_app

    with pytest.raises(ConfigurationError, match="SHORTENER_API_KEY"):
        with TestClient(create_app()):
            pass

    get_settings.cache_clear()


def test_the_service_starts_again_over_a_database_it_already_created(build_client):
    with build_client():
        pass

    with build_client() as restarted:
        assert restarted.get("/").status_code == 404


def test_a_database_predating_clicks_keeps_its_short_links(build_client, database_path):
    connection = sqlite3.connect(database_path)
    with connection:
        connection.execute(_SCHEMA_BEFORE_CLICKS_WERE_COUNTED)
        connection.execute(
            "INSERT INTO short_links (short_code, destination, created_at) "
            "VALUES (?, ?, ?)",
            A_SHORT_LINK_PREDATING_CLICKS,
        )
    connection.close()

    short_code, destination, created_at = A_SHORT_LINK_PREDATING_CLICKS
    with build_client() as client:
        listed = client.get("/short-links").json()
        followed = client.get(f"/{short_code}")

    assert [link["short_code"] for link in listed] == [short_code]
    assert listed[0]["destination"] == destination
    assert listed[0]["clicks"] == 0
    assert datetime.fromisoformat(listed[0]["created_at"]) == datetime.fromisoformat(
        created_at
    )
    assert followed.status_code == 302
    assert followed.headers["location"] == destination
