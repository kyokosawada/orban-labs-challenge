from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import initialise_database
from .errors import register_error_handlers
from .routes import router, tags_router

DESCRIPTION = """
A store for Notes. Every endpoint that reads or writes a Note requires an
`X-API-Key` header.

This documentation does not. `/docs`, `/redoc` and `/openapi.json` answer without a
key, because they describe the shape of the API and carry no stored Note. ADR 0005
records why.

Every failure, whatever its cause, returns the same envelope: a machine-readable
`code`, a human-readable `message`, and an optional per-field `fields` list. The
`ErrorResponse` schema lists every `code` and says what each one means.

Two failures belong to no single endpoint and so appear under none of them: an
address that exists nowhere answers 404 `not_found`, and an address that exists
but does not take the method you used answers 405 `method_not_allowed`. Both
arrive in the same envelope as the rest.

Listing and searching are the same endpoint: `GET /notes` takes an optional `q` and
an optional `tag`, and narrows by both together when both are given.
"""


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initialise_database()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Notes API",
        description=DESCRIPTION,
        version="0.1.0",
        lifespan=lifespan,
    )
    register_error_handlers(app)
    app.include_router(router)
    app.include_router(tags_router)
    return app


app = create_app()
