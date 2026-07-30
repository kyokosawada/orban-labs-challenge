# The redirect is temporary and is never cached

A resolved Short Code answers `302 Found` with the Destination in `Location` and
`Cache-Control: no-store`. A Short Code that does not resolve answers `404` with a plain
body rather than the error envelope the rest of the API uses.

## Considered Options

- **`301 Moved Permanently`.** The conventional choice for a shortener, and the fastest for a
  repeat visitor, because the browser stops asking. Rejected: it is a promise this service
  cannot keep. A Short Link may carry an expiry, so a link that resolves today may be gone
  tomorrow, and a cached 301 would keep sending people to a Destination the service has
  stopped serving. There is no way to withdraw one.
- **`307 Temporary Redirect`.** Correct, and it preserves the method. Rejected as the wrong
  emphasis: preserving a POST across a Short Link is not something this product does, and 302
  is what every client on the path already handles without thought.
- **`302 Found` with `no-store`.** Chosen.

Caching is refused separately from the status. A cached redirect is a Click the service never
sees, and a count that silently under-reports is worse than no count, because nobody can tell
it is wrong by looking at it.

## Consequences

Every follow costs a request to the service, which is the price of counting them and of
being able to stop serving a link. The redirect is the only latency-sensitive path in the
product, and ADR 0001 already removed the other hop on it.

The failure answers an ordinary `404`, not the envelope. A visitor following a link is not an
API caller: they are a browser that will render whatever comes back, and a JSON document
describing a machine-readable code is noise to them. The body says nothing about why, which
ADR 0003 requires anyway.
