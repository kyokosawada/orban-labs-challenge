import sqlite3

from fastapi import APIRouter, Depends, Query, status
from typing_extensions import Annotated

from . import repository
from .auth import require_api_key
from .db import get_connection
from .errors import CODE_NOT_FOUND, ApiError, ErrorResponse
from .schemas import KeywordFilter, Note, NoteContent, TagFilter

FAILURE_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
    status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
}


def _authenticated_router(prefix: str, group: str) -> APIRouter:
    return APIRouter(
        prefix=prefix,
        tags=[group],
        dependencies=[Depends(require_api_key)],
        responses=FAILURE_RESPONSES,
    )


router = _authenticated_router("/notes", "notes")
tags_router = _authenticated_router("/tags", "tags")

Connection = Annotated[sqlite3.Connection, Depends(get_connection)]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Note,
    summary="Write a Note",
)
def create_note(payload: NoteContent, connection: Connection) -> Note:
    return repository.create_note(
        connection, payload.title, payload.body, payload.tags
    )


@router.put(
    "/{note_id}",
    response_model=Note,
    summary="Change a Note, replacing its Tags",
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
def replace_note(
    note_id: int, payload: NoteContent, connection: Connection
) -> Note:
    note = repository.replace_note(
        connection, note_id, payload.title, payload.body, payload.tags
    )
    if note is None:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            CODE_NOT_FOUND,
            f"There is no Note with id {note_id}.",
        )
    return note


TagQuery = Annotated[
    TagFilter,
    Query(description="Narrow the list to Notes carrying this Tag."),
]

KeywordQuery = Annotated[
    KeywordFilter,
    Query(
        description=(
            "Narrow the list to Notes whose title or body mentions this, "
            "wherever it appears and whatever the capitalisation."
        )
    ),
]


@router.get(
    "",
    response_model=list[Note],
    summary="List Notes, most recently changed first",
)
def list_notes(
    connection: Connection, q: KeywordQuery = None, tag: TagQuery = None
) -> list[Note]:
    return repository.list_notes(connection, tag=tag, keyword=q)


@tags_router.get(
    "",
    response_model=list[str],
    summary="List the Tags in use, alphabetically",
)
def list_tags_in_use(connection: Connection) -> list[str]:
    return repository.list_tags_in_use(connection)
