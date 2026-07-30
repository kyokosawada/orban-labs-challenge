import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, Path, Query, status
from typing_extensions import Annotated

from . import repository
from .auth import require_api_key
from .db import get_connection
from .errors import CODE_NOT_FOUND, ApiError, ErrorResponse
from .schemas import KeywordFilter, Note, NoteContent, TagFilter

Responses = dict[int | str, dict[str, Any]]

FAILURE_RESPONSES: Responses = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
    status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
}

NOT_FOUND_RESPONSE: Responses = {
    status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}
}

NO_SUCH_NOTE = "There is no Note with that identifier."


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


NoteId = Annotated[int, Path(description="The identifier of the Note.")]


def _no_such_note() -> ApiError:
    return ApiError(status.HTTP_404_NOT_FOUND, CODE_NOT_FOUND, NO_SUCH_NOTE)


@router.get(
    "/{note_id}",
    response_model=Note,
    summary="Read one Note",
    responses=NOT_FOUND_RESPONSE,
)
def read_note(note_id: NoteId, connection: Connection) -> Note:
    note = repository.read_note(connection, note_id)
    if note is None:
        raise _no_such_note()
    return note


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Note",
    responses=NOT_FOUND_RESPONSE,
)
def delete_note(note_id: NoteId, connection: Connection) -> None:
    if not repository.delete_note(connection, note_id):
        raise _no_such_note()


@tags_router.get(
    "",
    response_model=list[str],
    summary="List the Tags in use, alphabetically",
)
def list_tags_in_use(connection: Connection) -> list[str]:
    return repository.list_tags_in_use(connection)
