# The schema publishes only what the service answers

The generated schema described two things the service never does. FastAPI adds a `422` carrying
its own `HTTPValidationError` shape to every operation that takes a parameter, and this
application replaces that shape with the error envelope for every failure it returns. So the
redirect advertised a `422` it cannot reach at all, in a shape nothing here produces, and the
components section carried `HTTPValidationError` and `ValidationError` beside the envelope as
if a caller might meet either.

`backend/openapi.py` builds the schema and drops any response still referring to the
framework's validation shape, along with the two component schemas once nothing points at them.
Statuses the service can answer are declared on the routes themselves: the listing cannot fail
validation and cannot exhaust Short Codes, so it publishes neither `422` nor `503`, and both
belong to creation.

A schema that describes a response the caller will never meet is worse than a thin one. Someone
writing a client against it handles a shape that cannot arrive and does not handle the envelope
that will.

## Considered Options

- **Leave the framework's `422` in place.** Rejected: it contradicts the envelope the same
  document promises two paragraphs earlier.
- **Declare a `422` on the redirect so the framework leaves it alone.** Rejected: it suppresses
  the wrong shape by documenting a different response that also never happens. The redirect
  takes one path segment and there is nothing about it to reject.
- **Remove what the service cannot answer after the schema is built.** Chosen.

## Consequences

The schema is built through a hook rather than straight from the framework, so anything that
adds a response by default has to be reviewed here rather than trusted. The removal is keyed on
the framework's own reference, so an operation that genuinely returned that shape would lose
its documentation silently. Nothing returns it: the envelope handler is registered for every
validation failure in the application.
