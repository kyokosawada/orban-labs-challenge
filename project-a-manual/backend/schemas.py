from datetime import datetime

from pydantic import AfterValidator, BaseModel, ConfigDict, Field
from typing_extensions import Annotated

TITLE_MAX_LENGTH = 200
BODY_MAX_LENGTH = 10_000


def _trimmed_title(value: str) -> str:
    trimmed = value.strip()
    if not trimmed:
        raise ValueError("Title must not be empty once surrounding spaces are removed.")
    if len(trimmed) > TITLE_MAX_LENGTH:
        raise ValueError(
            f"Title must be at most {TITLE_MAX_LENGTH} characters once surrounding "
            "spaces are removed."
        )
    return trimmed


class NoteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Annotated[str, AfterValidator(_trimmed_title)]
    body: Annotated[str | None, Field(max_length=BODY_MAX_LENGTH)] = None


class Note(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    updated_at: datetime
