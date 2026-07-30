from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from backend.codes import short_code_source
from backend.config import API_KEY_HEADER, get_settings


@pytest.fixture
def api_key() -> str:
    return "test-key-not-a-real-secret"


@pytest.fixture
def database_path(tmp_path) -> str:
    return str(tmp_path / "short_links.db")


@pytest.fixture
def build_client(monkeypatch, api_key, database_path):
    monkeypatch.setenv("SHORTENER_API_KEY", api_key)
    monkeypatch.setenv("SHORTENER_DATABASE_PATH", database_path)
    get_settings.cache_clear()

    from backend.main import create_app

    def build(authenticate: bool = True) -> TestClient:
        client = TestClient(create_app(), follow_redirects=False)
        if authenticate:
            client.headers.update({API_KEY_HEADER: api_key})
        return client

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


@pytest.fixture
def scripted_short_codes():
    def script(test_client: TestClient, codes: list[str]) -> None:
        remaining = iter(codes)
        test_client.app.dependency_overrides[short_code_source] = (
            lambda: lambda: next(remaining)
        )

    return script
