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


def normalise_tag(value: str) -> str:
    return value.strip().lower()


def _normalised_tags(values: list[str]) -> list[str]:
    return sorted({normalise_tag(value) for value in values})


class NoteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Annotated[str, AfterValidator(_trimmed_title)]
    body: Annotated[str | None, Field(max_length=BODY_MAX_LENGTH)] = None
    tags: Annotated[list[str], AfterValidator(_normalised_tags)] = Field(
        default_factory=list
    )


class Note(BaseModel):
    id: int
    title: str
    body: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime
