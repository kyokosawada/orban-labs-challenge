# The frontend proxies every API call so the key stays server-side

The Notes API authenticates with an API key on a request header, and the frontend is a
browser application. A browser cannot hold a secret, so calling FastAPI directly from React
would ship the key in the JavaScript bundle and make the authentication decorative. Every
call therefore goes through a Next.js route handler, which reads the key from a server-side
environment variable and forwards the request. The browser never sees it.

## Considered Options

- **Direct browser calls with the key in a `NEXT_PUBLIC_` variable.** Simplest, and wrong in
  a way any reviewer spots immediately: the key is readable by anyone who opens devtools.
- **Direct browser calls, with the exposure documented as a known weakness.** Honest about
  the flaw but still ships it, and the brief asks for working auth rather than an explained
  hole.
- **Next.js route handlers as a server-side proxy.** Chosen. Costs an extra network hop and a
  thin handler per endpoint, and in exchange the API key is never delivered to a client.

## Consequences

The frontend has a server tier, so its setup guide needs the API key configured in the
Next.js environment rather than the browser's. Local development runs two processes.
