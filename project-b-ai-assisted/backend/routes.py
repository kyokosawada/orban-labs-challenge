import sqlite3

from fastapi import APIRouter, Depends, status
from typing_extensions import Annotated

from . import repository
from .auth import require_api_key
from .codes import ShortCodeSource, short_code_source
from .db import get_connection
from .errors import CODE_SHORT_CODE_UNAVAILABLE, ApiError, ErrorResponse
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


@short_links_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ShortLink,
    summary="Mint a Short Link for a Destination",
)
def create_short_link(
    payload: ShortLinkCreate, connection: Connection, generate_code: CodeSource
) -> ShortLink:
    try:
        return repository.create_short_link(
            connection, payload.destination, generate_code
        )
    except repository.ShortCodeUnavailable as exhausted:
        raise ApiError(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            CODE_SHORT_CODE_UNAVAILABLE,
            "No Short Code could be minted just now. Try again.",
        ) from exhausted
