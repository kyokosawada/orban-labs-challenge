import os
from dataclasses import dataclass
from functools import lru_cache

API_KEY_HEADER = "X-API-Key"


class ConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class Settings:
    api_key: str
    database_path: str


@lru_cache
def get_settings() -> Settings:
    api_key = os.environ.get("SHORTENER_API_KEY", "").strip()
    if not api_key:
        raise ConfigurationError(
            "SHORTENER_API_KEY is not set. The API refuses to start without a key "
            "rather than letting anyone turn it into an open redirector."
        )
    return Settings(
        api_key=api_key,
        database_path=os.environ.get("SHORTENER_DATABASE_PATH", "short_links.db"),
    )
