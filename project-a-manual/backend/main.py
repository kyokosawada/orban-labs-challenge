from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import initialise_database
from .errors import register_error_handlers
from .routes import router, tags_router

DESCRIPTION = """
A store for Notes. Every endpoint requires an `X-API-Key` header.

Every failure, whatever its cause, returns the same envelope: a machine-readable
`code`, a human-readable `message`, and an optional per-field `fields` list.
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
