from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from backend.config import API_KEY_HEADER, get_settings


@pytest.fixture
def api_key() -> str:
    return "test-key-not-a-real-secret"


@pytest.fixture
def authenticated(api_key):
    def apply(client: TestClient) -> TestClient:
        client.headers.update({API_KEY_HEADER: api_key})
        return client

    return apply


@pytest.fixture
def build_client(tmp_path, monkeypatch, api_key, authenticated):
    monkeypatch.setenv("NOTES_API_KEY", api_key)
    monkeypatch.setenv("NOTES_DATABASE_PATH", str(tmp_path / "notes.db"))
    get_settings.cache_clear()

    from backend.main import create_app

    def build(authenticate: bool = True) -> TestClient:
        client = TestClient(create_app())
        return authenticated(client) if authenticate else client

    yield build

    get_settings.cache_clear()


@pytest.fixture
def client(build_client) -> Iterator[TestClient]:
    with build_client() as test_client:
        yield test_client


@pytest.fixture
def anonymous_client(build_client) -> Iterator[TestClient]:
    with build_client(authenticate=False) as test_client:
        yield test_client
