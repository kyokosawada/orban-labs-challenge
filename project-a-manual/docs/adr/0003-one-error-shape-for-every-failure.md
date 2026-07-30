# Every error response uses one shape

FastAPI returns validation failures as a 422 with a nested `detail` array, which does not
resemble the 401 and 404 responses the application raises itself. A frontend consuming that
needs a rendering path per status code. Instead, the app installs exception handlers so every
failure - validation, authentication, missing resource, and unhandled - returns the same
envelope: a stable machine-readable `code`, a human-readable `message`, and an optional
`fields` list carrying per-field validation detail.

The brief asks for meaningful error responses. Taking the framework's defaults would have
satisfied that on paper while leaving the frontend to special-case three shapes.

## Consequences

FastAPI's default `RequestValidationError` handler is overridden, so a reader expecting the
stock 422 body will not find it; the same information is preserved under `fields`. The
generated OpenAPI schema describes the custom shape, so the documented contract and the real
one stay in agreement. Any new endpoint raises through the same handlers rather than
returning its own ad-hoc body.

This is a candidate to apply to Project B as well, but that project has not been designed
yet and is not bound by this decision.
