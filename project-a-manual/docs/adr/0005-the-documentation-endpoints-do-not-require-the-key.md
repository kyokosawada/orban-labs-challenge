# The documentation endpoints do not require the key

The spec says every API endpoint requires the key, and it also says a developer picking this
up should find the API browsable. Those two read as a conflict for `/docs`, `/redoc` and
`/openapi.json`. They are left open, and every endpoint that touches a stored Note goes on
requiring the key.

The deciding fact is what those three addresses serve. They describe the shape of requests
and responses: field names, lengths, status codes, and the error envelope. No stored Note
reaches them, and no key of any kind is in them. Someone who reads the whole schema learns
what the API accepts, which is what the schema is for, and still cannot read or write a
single Note without the key.

Requiring it would also not have produced a browsable API. Swagger UI fetches
`/openapi.json` itself, from the browser, without a key: the Authorize button attaches the
key to the calls the page makes on your behalf, not to the schema fetch that draws the page.
Behind a key requirement the documentation page renders as an error, and the only way back
to it is a `curl` with a header, which is the source-reading the spec asked to make
unnecessary.

## Considered Options

- **Require the key everywhere, without exception.** The literal reading. It satisfies one
  spec line by deleting another: the page a developer would open stops rendering.
- **Serve the schema openly and put the documentation page behind the key.** Halfway, and
  incoherent: the page's only content is the schema that is already public.
- **Leave `/docs`, `/redoc` and `/openapi.json` open; require the key on everything that
  reads or writes a Note.** Chosen. A reader can browse the API and still cannot reach the
  data.

## Consequences

Anyone auditing "every endpoint requires a key" against the running service will find three
addresses that answer without one. The line is recorded here so that reads as decided rather
than missed, and the API's own description says it too, where a reader meets it first.

Publishing this API means publishing its shape. That is a real disclosure, and it is the
price of the browsable schema the spec asks for. If a deployment ever needs the shape hidden
as well, the fix is to stop serving the documentation there rather than to key it, because a
keyed documentation page is not a documentation page.

Project B answers the same question for itself. Consistency between the two would be good,
but this decision binds only Project A.
