import pytest
from fastapi.testclient import TestClient

from backend.config import ConfigurationError, get_settings


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
