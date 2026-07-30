from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

CODE_VALIDATION_ERROR = "validation_error"
CODE_UNAUTHORIZED = "unauthorized"
CODE_NOT_FOUND = "not_found"
CODE_METHOD_NOT_ALLOWED = "method_not_allowed"
CODE_INTERNAL_ERROR = "internal_error"

_STATUS_CODES = {
    status.HTTP_401_UNAUTHORIZED: CODE_UNAUTHORIZED,
    status.HTTP_404_NOT_FOUND: CODE_NOT_FOUND,
    status.HTTP_405_METHOD_NOT_ALLOWED: CODE_METHOD_NOT_ALLOWED,
}

_LOCATION_PREFIXES = {"body", "query", "path", "header", "cookie"}
_PYDANTIC_VALUE_ERROR_PREFIX = "Value error, "


class FieldError(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    fields: list[FieldError] | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "code": CODE_VALIDATION_ERROR,
                "message": "The request could not be accepted.",
                "fields": [
                    {"field": "title", "message": "Title must not be empty."}
                ],
            }
        }
    }


class ApiError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        fields: list[FieldError] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.fields = fields


def error_response(
    status_code: int,
    code: str,
    message: str,
    fields: list[FieldError] | None = None,
) -> JSONResponse:
    payload = ErrorResponse(code=code, message=message, fields=fields)
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(exclude_none=True),
    )


def _field_name(location: tuple[object, ...]) -> str:
    parts = [str(part) for part in location]
    if parts and parts[0] in _LOCATION_PREFIXES:
        parts = parts[1:]
    return ".".join(parts) if parts else "body"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(_: Request, exc: ApiError) -> JSONResponse:
        return error_response(exc.status_code, exc.code, exc.message, exc.fields)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        fields = [
            FieldError(
                field=_field_name(error["loc"]),
                message=error["msg"].removeprefix(_PYDANTIC_VALUE_ERROR_PREFIX),
            )
            for error in exc.errors()
        ]
        return error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            CODE_VALIDATION_ERROR,
            "The request could not be accepted.",
            fields,
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        _: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        code = _STATUS_CODES.get(exc.status_code, CODE_INTERNAL_ERROR)
        return error_response(exc.status_code, code, str(exc.detail))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        return error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            CODE_INTERNAL_ERROR,
            "The server could not complete the request.",
        )
