from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

FRAMEWORK_VALIDATION_SCHEMAS = ("HTTPValidationError", "ValidationError")

_FRAMEWORK_VALIDATION_REF = f"#/components/schemas/{FRAMEWORK_VALIDATION_SCHEMAS[0]}"


def _is_the_framework_validation_shape(response: dict[str, Any]) -> bool:
    body = response.get("content", {}).get("application/json", {})
    return body.get("schema", {}).get("$ref") == _FRAMEWORK_VALIDATION_REF


def _without_the_framework_validation_shape(
    schema: dict[str, Any],
) -> dict[str, Any]:
    for operations in schema["paths"].values():
        for operation in operations.values():
            responses = operation["responses"]
            for status_code, response in list(responses.items()):
                if _is_the_framework_validation_shape(response):
                    del responses[status_code]
    for name in FRAMEWORK_VALIDATION_SCHEMAS:
        schema["components"]["schemas"].pop(name, None)
    return schema


def publish_schema(app: FastAPI) -> None:
    def openapi() -> dict[str, Any]:
        if app.openapi_schema is None:
            app.openapi_schema = _without_the_framework_validation_shape(
                get_openapi(
                    title=app.title,
                    version=app.version,
                    description=app.description,
                    routes=app.routes,
                )
            )
        return app.openapi_schema

    app.openapi = openapi
