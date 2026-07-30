from datetime import datetime

from pydantic import AfterValidator, AwareDatetime, BaseModel, ConfigDict
from typing_extensions import Annotated

from .destinations import validate_destination

DESTINATION_MAX_LENGTH = 2048


def _trimmed_destination(value: str) -> str:
    trimmed = value.strip()
    if not trimmed:
        raise ValueError(
            "Destination must not be empty once surrounding spaces are removed."
        )
    if len(trimmed) > DESTINATION_MAX_LENGTH:
        raise ValueError(
            f"Destination must be at most {DESTINATION_MAX_LENGTH} characters once "
            "surrounding spaces are removed."
        )
    return trimmed


def _accepted_destination(value: str) -> str:
    return validate_destination(_trimmed_destination(value))


class ShortLinkCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    destination: Annotated[str, AfterValidator(_accepted_destination)]
    expires_at: AwareDatetime | None = None


class ShortLink(BaseModel):
    short_code: str
    destination: str
    created_at: datetime
    expires_at: datetime | None
