from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import initialise_database
from .errors import register_error_handlers
from .openapi import publish_schema
from .routes import redirect_router, short_links_router

DESCRIPTION = """
A store that trades a Destination for a Short Code.

Creating a Short Link requires an `X-API-Key` header, and listing them requires
the same. Following one requires nothing, which is the entire point of it.

This page and the schema behind it need no key. They describe the shapes the
service accepts and answers with, and carry no Short Link anyone created.

Every API failure returns the same envelope: a machine-readable `code`, a
human-readable `message`, and an optional per-field `fields` list. The redirect
is the exception, because a visitor following a link is not an API caller and
meets an ordinary status rather than a document describing one.
"""


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initialise_database()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="URL Shortener API",
        description=DESCRIPTION,
        version="0.1.0",
        lifespan=lifespan,
    )
    register_error_handlers(app)
    app.include_router(short_links_router)
    app.include_router(redirect_router)
    publish_schema(app)
    return app


app = create_app()
