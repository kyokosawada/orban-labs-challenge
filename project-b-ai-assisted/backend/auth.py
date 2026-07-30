import secrets

from fastapi import Depends, status
from fastapi.security import APIKeyHeader
from typing_extensions import Annotated

from .config import API_KEY_HEADER, get_settings
from .errors import CODE_UNAUTHORIZED, ApiError

api_key_scheme = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


def require_api_key(
    presented_key: Annotated[str | None, Depends(api_key_scheme)],
) -> None:
    expected_key = get_settings().api_key
    if presented_key is None or not secrets.compare_digest(
        presented_key, expected_key
    ):
        raise ApiError(
            status.HTTP_401_UNAUTHORIZED,
            CODE_UNAUTHORIZED,
            f"A valid {API_KEY_HEADER} header is required.",
        )
