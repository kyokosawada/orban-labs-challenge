from datetime import datetime

from pydantic import AfterValidator, AwareDatetime, BaseModel, ConfigDict, Field
from typing_extensions import Annotated

from .destinations import validate_destination

DESTINATION_MAX_LENGTH = 2048

CLICKS_DESCRIPTION = (
    "How many requests for this Short Code resolved to its Destination. This "
    "counts requests, not people: an automated preview fetch by a chat "
    "application counts, and one person following the link twice counts twice."
)

DESTINATION_DESCRIPTION = (
    "The web address the Short Link sends someone to. It must use http or "
    "https and point at a public host: loopback, link-local and private-network "
    "addresses are refused, so a local address cannot be shortened. At most "
    f"{DESTINATION_MAX_LENGTH} characters once surrounding spaces are removed."
)

STORED_DESTINATION_DESCRIPTION = (
    "The web address this Short Link sends someone to, exactly as it was "
    "supplied. It is never altered after creation."
)

SUBMITTED_EXPIRES_AT_DESCRIPTION = (
    "Optional moment after which the Short Link stops resolving. It must carry "
    "a timezone offset and be in the future. Leave it out and the Short Link "
    "resolves indefinitely."
)

SHORT_CODE_DESCRIPTION = (
    "The random string identifying this Short Link. Append it to the public "
    "base address to get the Short Link itself."
)

CREATED_AT_DESCRIPTION = "When the Short Link was minted, in UTC."

EXPIRES_AT_DESCRIPTION = (
    "The moment this Short Link stops resolving, in UTC, or null if it never "
    "does. Past it, the Short Link answers exactly as a Short Code that was "
    "never created does."
)

AN_EXAMPLE_DESTINATION = "https://example.com/a/genuinely/long/address?utm_source=post"

CREATE_EXAMPLE = {
    "destination": AN_EXAMPLE_DESTINATION,
    "expires_at": "2030-01-31T09:00:00+00:00",
}

SHORT_LINK_EXAMPLE = {
    "short_code": "aB3xY9z",
    "destination": AN_EXAMPLE_DESTINATION,
    "created_at": "2030-01-01T09:00:00Z",
    "expires_at": "2030-01-31T09:00:00Z",
    "clicks": 12,
}


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
    model_config = ConfigDict(
        extra="forbid", json_schema_extra={"example": CREATE_EXAMPLE}
    )

    destination: Annotated[
        str,
        AfterValidator(_accepted_destination),
        Field(description=DESTINATION_DESCRIPTION),
    ]
    expires_at: Annotated[
        AwareDatetime | None, Field(description=SUBMITTED_EXPIRES_AT_DESCRIPTION)
    ] = None


class ShortLink(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": SHORT_LINK_EXAMPLE})

    short_code: Annotated[str, Field(description=SHORT_CODE_DESCRIPTION)]
    destination: Annotated[str, Field(description=STORED_DESTINATION_DESCRIPTION)]
    created_at: Annotated[datetime, Field(description=CREATED_AT_DESCRIPTION)]
    expires_at: Annotated[datetime | None, Field(description=EXPIRES_AT_DESCRIPTION)]
    clicks: Annotated[int, Field(description=CLICKS_DESCRIPTION)]
