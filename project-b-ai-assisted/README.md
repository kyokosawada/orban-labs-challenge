# URL Shortener

Trade a long web address for a short one, follow the short one, and see how many Clicks each
has taken.

This is two processes, and the arrangement matters before you run anything.

| Process | Address | What it serves |
| --- | --- | --- |
| The API (FastAPI) | `http://127.0.0.1:8000` | Creating a Short Link, listing them, and the redirect |
| The interface (Next.js) | `http://localhost:3000` | The creation form and the dashboard |

**Short links point at the API, not at the interface.** A Short Link is
`http://127.0.0.1:8000/aB3xY9z`, and following it never touches Next.js. The interface only
calls the API to create a Short Link and to read the dashboard. This is the opposite
arrangement to the Notes API beside it, where everything is proxied through Next.js;
`docs/adr/0001-the-api-serves-the-redirect-directly.md` says why. If you assume the redirect
runs through port 3000, you will wire it wrong.

## Before you start

- Python 3.12. Everything below was run on 3.12.3.
- Node 18.18 or newer, which is what Next.js 15 asks for. Everything below was run on 22.22.0.

Everything below runs from `project-b-ai-assisted/`.

## 1. Run the API

    python3 -m venv .venv
    .venv/bin/pip install -r requirements-dev.txt

Run the tests before anything else, because they need no configuration and they tell you the
checkout is sound:

    .venv/bin/python -m pytest

That is the whole suite, 97 tests when this was written, and all of them should pass. If any
fail, stop here rather than configuring anything.

Now give the service a key. It refuses to start without one rather than letting anyone turn it
into an open redirector:

    cp .env.example .env
    python3 -c "import secrets; print(secrets.token_urlsafe(32))"

Put that string in `.env` as `SHORTENER_API_KEY`. The API reads its environment and does not
read `.env` itself, so load the file into the shell first:

    set -a; . ./.env; set +a
    .venv/bin/python -m uvicorn backend.main:app --reload

It comes up on `http://127.0.0.1:8000`. Leave it running.

## 2. Run the interface

In a second terminal, from `project-b-ai-assisted/frontend`:

    npm install
    cp .env.example .env.local

Put the same `SHORTENER_API_KEY` in `.env.local`. It has to match the one the API is running
with, or every creation comes back `401`. Next.js reads `.env.local` on its own, so there is
nothing to source here.

    npm run dev

It comes up on `http://localhost:3000`.

## 3. Follow it through once

Open `http://localhost:3000`, paste a real public address into Destination, and press Shorten.
You get back a short link on port 8000, a Copy button, and a row in the dashboard below. Open
the short link. You land on the Destination, and the Clicks column reaches 1 within a few
seconds without you reloading the page.

The same thing without the interface, with your key in place of `$KEY`:

    curl -s -X POST http://127.0.0.1:8000/short-links \
      -H "X-API-Key: $KEY" -H 'Content-Type: application/json' \
      -d '{"destination":"https://example.com/a/genuinely/long/address"}'

Then follow it, using the Short Code that came back, and read the count:

    curl -si http://127.0.0.1:8000/aB3xY9z | head -1
    curl -s http://127.0.0.1:8000/short-links -H "X-API-Key: $KEY"

The first answers `HTTP/1.1 302 Found` with the Destination in `Location`. The second shows
that Short Link with one Click.

## Environment variables

| Name | Read by | What it does |
| --- | --- | --- |
| `SHORTENER_API_KEY` | The API, and the Next.js server | The single shared key. Both processes need the same value. The API will not start without it |
| `SHORTENER_DATABASE_PATH` | The API | Where the SQLite file lives. Defaults to `short_links.db` in the working directory, and is created on startup |
| `SHORTENER_API_URL` | The Next.js server | Where the interface sends creation and listing. Defaults to `http://127.0.0.1:8000` |
| `SHORTENER_PUBLIC_BASE_URL` | The Next.js server | The prefix shown in front of a Short Code. Defaults to `SHORTENER_API_URL`. It has to be the API's address, because the API serves the redirect |

`.env.example` and `frontend/.env.example` list them. Never commit the filled-in copies.

### Why the key stays on the server

The browser never sees the key. It posts to `/api/short-links` on the Next.js server, and that
server attaches `X-API-Key` and forwards the call to the API. So the key is read by two server
processes and by nothing else.

That is why no key-related variable carries a `NEXT_PUBLIC_` prefix. Next.js inlines anything
with that prefix into the JavaScript it ships, which would publish the key to everyone who
opens the page and turn the service into an open redirector. If creation ever needs to happen
from a browser, it goes through the Next.js route, not through a variable renamed to reach the
client.

## Destinations that are refused

The service is a redirector, so it does not accept every address. Creation refuses:

- Anything that is not `http` or `https`. `javascript:` and `data:` execute in a visitor's
  browser and have no use here.
- Loopback, link-local and private-network addresses. That includes `localhost`,
  `127.0.0.1`, `::1`, `10.0.0.5`, `192.168.1.10` and the IPv4-mapped IPv6 spellings of them.

**So you cannot shorten your own development server.** This is the first thing most readers
try, and the service is not broken when it says:

    {"code":"validation_error","message":"The request could not be accepted.","fields":[{"field":"destination","message":"Destination must point at a public host, not a loopback, link-local or private-network address."}]}

Use a public address to try it. The reasoning, and the gap this leaves open, are in
`docs/adr/0004-only-public-http-destinations-are-accepted.md`: names are never resolved, so a
name that happens to point at a private address is accepted.

An expiry, if you set one, has to carry a timezone offset and be in the future. Leave it empty
and the Short Link resolves indefinitely.

## The API

With the service running, the documentation is at `http://127.0.0.1:8000/docs`, the same
thing rendered differently at `/redoc`, and the schema itself at `/openapi.json`. None of the
three needs a key: they describe shapes, not Short Links.
`docs/adr/0007-the-schema-and-the-documentation-pages-need-no-key.md` records that decision.
The Authorize box on `/docs` is for trying creation from the page, and takes the same key the
API is running with. The page loads Swagger UI from a CDN, so it wants network access.

| Endpoint | Key | Answers |
| --- | --- | --- |
| `POST /short-links` | Required | `201` with the Short Link. `422` if the Destination or expiry is refused |
| `GET /short-links` | Required | `200` with every Short Link, newest first, each with its Click count |
| `GET /{short_code}` | None | `302` to the Destination with `Cache-Control: no-store`, and the request counts as a Click. `404` in plain text if nothing resolves |

Every API failure carries the same envelope: a machine-readable `code`, a human-readable
`message`, and an optional per-field `fields` list. The redirect is the exception. A visitor
following a link is not an API caller, so a failure there is an ordinary `404` with a plain
body.

An expired Short Link and a Short Code that was never created answer identically, on purpose,
so nobody can probe which Short Codes exist. The interface cannot tell them apart either.

The root of the API belongs to Short Codes: `GET /{short_code}` matches any single path
segment. `/short-links` stays reachable because it carries a hyphen, which a Short Code drawn
from an alphanumeric alphabet never contains, so a new endpoint has to be hyphenated too. The
documentation paths are safe for a different reason: `/docs` and `/redoc` are shorter than a
Short Code and `/openapi.json` carries a dot, so none of them can ever be minted.

## If it does not work

- `ConfigurationError: SHORTENER_API_KEY is not set` at startup. The shell you started uvicorn
  from does not carry the variable. Run `set -a; . ./.env; set +a` in that terminal.
- The interface says the API did not answer. The API is not running, or `SHORTENER_API_URL`
  points somewhere it is not.
- Creation comes back `401`. The two processes are holding different keys.
- A short link answers `404`. The Short Code is unknown or the Short Link has expired, and the
  service deliberately will not say which.
- Port 3000 or 8000 is taken. Next.js moves to 3001 on its own and prints where it went;
  uvicorn takes `--port`. Move the API and you have to move `SHORTENER_API_URL` and
  `SHORTENER_PUBLIC_BASE_URL` with it, or the interface will show short links nothing serves.

## Where the reasoning lives

- `docs/spec.md` is the whole specification, including what is deliberately out of scope.
- `docs/adr/` holds the decisions, one per file, with what was rejected and why.
- `CONTEXT.md` is the glossary. Destination, Short Code, Short Link, Click.
