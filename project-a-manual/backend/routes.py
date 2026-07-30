import sqlite3

from fastapi import APIRouter, Depends, status
from typing_extensions import Annotated

from . import repository
from .auth import require_api_key
from .db import get_connection
from .errors import ErrorResponse
from .schemas import Note, NoteCreate

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    dependencies=[Depends(require_api_key)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)

Connection = Annotated[sqlite3.Connection, Depends(get_connection)]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Note,
    summary="Write a Note",
)
def create_note(payload: NoteCreate, connection: Connection) -> Note:
    return repository.create_note(
        connection, payload.title, payload.body or "", payload.tags
    )


@router.get(
    "",
    response_model=list[Note],
    summary="List Notes, most recently changed first",
)
def list_notes(connection: Connection) -> list[Note]:
    return repository.list_notes(connection)
