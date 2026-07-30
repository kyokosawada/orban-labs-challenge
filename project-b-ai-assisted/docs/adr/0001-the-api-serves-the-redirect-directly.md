# The API serves the redirect directly, not the frontend

A short link resolves against the FastAPI service at its own address. The Next.js application
serves the creation form and the dashboard, and is told the public base URL so it can display
the links it creates, but no click passes through it.

This is deliberately the opposite arrangement to Project A, where every call goes through a
Next.js proxy. That decision existed to keep an API key out of the browser. The redirect
carries no key and is public by definition, so the proxy would buy nothing and cost
something.

## Considered Options

- **Next.js serves the redirect as well.** One hostname, and the short link is the
  application's own address, which is what a real shortener looks like. Rejected for three
  reasons: it puts a hop on the only latency-sensitive path in the product, it makes every
  link depend on the frontend being up, and it forces the code namespace to share the root
  with page routes, so a code of `dashboard` would collide with the dashboard page and every
  new page would quietly remove a possible code.
- **The API serves it.** Chosen. The root namespace belongs entirely to short codes.

## Consequences

Development runs two addresses, and the setup guide has to be explicit about which is which.
The public base URL is configuration rather than something the code assumes, so a real
deployment could put the redirect behind a genuinely short domain without a code change -
which is the only way a shortener is worth anything.
