import re
from datetime import datetime

from pydantic import AfterValidator, BaseModel, ConfigDict, Field
from typing_extensions import Annotated

TITLE_MAX_LENGTH = 200
BODY_MAX_LENGTH = 10_000
TAG_MAX_LENGTH = 50
TAGS_PER_NOTE_MAX = 20

_ALLOWED_TAG = re.compile(r"^[\w-]+$")


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


def validated_tag(value: str) -> str:
    tag = normalise_tag(value)
    if not tag:
        raise ValueError("A Tag must not be empty once surrounding spaces are removed.")
    if len(tag) > TAG_MAX_LENGTH:
        raise ValueError(
            f"A Tag must be at most {TAG_MAX_LENGTH} characters, so {value!r} "
            "cannot be one."
        )
    if not _ALLOWED_TAG.match(tag):
        raise ValueError(
            "A Tag may contain only letters, digits, hyphens and underscores, so "
            f"{value!r} cannot be one."
        )
    return tag


def _tag_filter(value: str | None) -> str | None:
    if value is None or not normalise_tag(value):
        return None
    return validated_tag(value)


TagFilter = Annotated[str | None, AfterValidator(_tag_filter)]


def _keyword_filter(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip() or None


KeywordFilter = Annotated[str | None, AfterValidator(_keyword_filter)]


def _normalised_tags(values: list[str]) -> list[str]:
    tags = sorted({validated_tag(value) for value in values})
    if len(tags) > TAGS_PER_NOTE_MAX:
        raise ValueError(f"A Note carries at most {TAGS_PER_NOTE_MAX} Tags.")
    return tags


class NoteContent(BaseModel):
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
