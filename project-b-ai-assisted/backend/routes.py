import sqlite3
from datetime import datetime

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import PlainTextResponse, RedirectResponse
from typing_extensions import Annotated

from . import repository
from .auth import require_api_key
from .clock import Clock, clock
from .codes import ShortCodeSource, short_code_source
from .db import get_connection
from .errors import (
    CODE_SHORT_CODE_UNAVAILABLE,
    CODE_VALIDATION_ERROR,
    VALIDATION_FAILED_MESSAGE,
    ApiError,
    ErrorResponse,
    FieldError,
)
from .schemas import ShortLink, ShortLinkCreate

short_links_router = APIRouter(
    prefix="/short-links",
    tags=["short links"],
    dependencies=[Depends(require_api_key)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    },
)

Connection = Annotated[sqlite3.Connection, Depends(get_connection)]
CodeSource = Annotated[ShortCodeSource, Depends(short_code_source)]
ClockSource = Annotated[Clock, Depends(clock)]


def _require_a_future_expiry(expires_at: datetime | None, now: datetime) -> None:
    if expires_at is not None and expires_at <= now:
        raise ApiError(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            CODE_VALIDATION_ERROR,
            VALIDATION_FAILED_MESSAGE,
            [
                FieldError(
                    field="expires_at",
                    message="Expiry must be a moment in the future.",
                )
            ],
        )


@short_links_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ShortLink,
    summary="Mint a Short Link for a Destination",
)
def create_short_link(
    payload: ShortLinkCreate,
    connection: Connection,
    generate_code: CodeSource,
    now: ClockSource,
) -> ShortLink:
    minted_at = now()
    _require_a_future_expiry(payload.expires_at, minted_at)
    try:
        return repository.create_short_link(
            connection,
            payload.destination,
            generate_code,
            minted_at,
            payload.expires_at,
        )
    except repository.ShortCodeUnavailable as exhausted:
        raise ApiError(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            CODE_SHORT_CODE_UNAVAILABLE,
            "No Short Code could be minted just now. Try again.",
        ) from exhausted


@short_links_router.get(
    "",
    response_model=list[ShortLink],
    summary="List every Short Link with the Clicks it has taken",
    description=(
        "Newest first. A Click is one request for a Short Code that resolved, so "
        "the counts report requests rather than people."
    ),
)
def list_short_links(connection: Connection) -> list[ShortLink]:
    return repository.list_short_links(connection)


redirect_router = APIRouter(tags=["redirect"])


@redirect_router.get(
    "/{short_code}",
    status_code=status.HTTP_302_FOUND,
    response_class=RedirectResponse,
    summary="Follow a Short Link to its Destination",
    responses={
        status.HTTP_302_FOUND: {
            "description": "The Destination is in the Location header.",
            "content": None,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "No Short Link resolves for that Short Code.",
            "content": {"text/plain": {}},
        },
    },
)
def follow_short_link(
    short_code: str, connection: Connection, now: ClockSource
) -> Response:
    short_link = repository.find_resolvable_short_link(connection, short_code, now())
    if short_link is None:
        return PlainTextResponse(
            "No Short Link here.", status_code=status.HTTP_404_NOT_FOUND
        )
    return RedirectResponse(
        short_link.destination,
        status_code=status.HTTP_302_FOUND,
        headers={"Cache-Control": "no-store"},
    )
