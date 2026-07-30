# Notes

A store for Notes with a web interface. You write a Note with a title, a body and any Tags
you like, then find it again by typing a word from it or by picking a Tag.

Two processes run side by side. A FastAPI service owns the data and answers on port 8000. A
Next.js application serves the interface on port 3000 and is the only thing that talks to the
service. `docs/spec.md` is the full description of what it does, and `docs/adr/` records the
decisions behind it.

## What you need

- Python 3.12
- Node 20 or newer. Next 15.1.3 declares `^18.18.0 || ^19.8.0 || >= 20.0.0`, so an older
  major works if it is one of those.

This guide was walked through on Python 3.12.3 and Node 22.22.0.

    git clone https://github.com/kyokosawada/orban-labs-challenge.git
    cd orban-labs-challenge/project-a-manual

Everything below is run from `project-a-manual/`, unless a step says otherwise.

## Run the tests

    python3 -m venv .venv
    .venv/bin/pip install -r requirements-dev.txt
    .venv/bin/python -m pytest

The suite needs no configuration and no running service. Each test builds the application
against a SQLite database of its own and supplies its own key, so a clean checkout is enough.

## Environment variables

There are three, and one of them is set twice with the same value.

The service reads its two from the environment. Copy the example and fill it in:

    cp .env.example .env

| Variable | Where | Required | Default | What it does |
| --- | --- | --- | --- | --- |
| `NOTES_API_KEY` | `.env` | yes | none | The shared key. Every call that reads or writes a Note must present it as an `X-API-Key` header. |
| `NOTES_DATABASE_PATH` | `.env` | no | `notes.db` | The SQLite file, resolved against the directory you start the service from. |

The interface reads its two from `frontend/.env.local`:

    cp frontend/.env.example frontend/.env.local

| Variable | Where | Required | Default | What it does |
| --- | --- | --- | --- | --- |
| `NOTES_API_URL` | `frontend/.env.local` | no | `http://127.0.0.1:8000` | Where the interface's server finds the service. |
| `NOTES_API_KEY` | `frontend/.env.local` | yes | none | The same value as the service's. |

The two `NOTES_API_KEY` values must match, or every request is refused with a 401. Generate
one and paste it into both files:

    .venv/bin/python -c "import secrets; print(secrets.token_urlsafe(32))"

The service refuses to start without a key rather than accepting unauthenticated requests,
so a missing `NOTES_API_KEY` fails immediately and says so.

Neither `.env` nor `frontend/.env.local` is committed. Both are ignored, and only the
`.env.example` files are tracked.

### Why the key stays on the server

The browser never holds the key and never talks to the service.

A page you can open is a page whose JavaScript anyone can read, so a key delivered to it is a
key you have published. The interface therefore has a server tier of its own. The browser
calls `/api/notes` on the Next.js server; a route handler there reads `NOTES_API_KEY` from the
server-side environment, attaches it as `X-API-Key`, and forwards the call to the service. The
answer comes back the same way. This is ADR 0001 for this project, and it is why running the
interface takes an environment file rather than nothing.

The consequence for you as the person configuring it: put the key in `frontend/.env.local` as
`NOTES_API_KEY`, and never as `NEXT_PUBLIC_NOTES_API_KEY`. Next.js inlines any variable
prefixed `NEXT_PUBLIC_` into the JavaScript it sends to the browser, which is exactly the
exposure the design exists to prevent.

You can check it holds. With both processes running, this searches the page and every script
it loads for your key, and prints nothing if the key is not there:

    KEY=$(grep '^NOTES_API_KEY=' .env | cut -d= -f2-)
    PAGE=$(curl -s http://127.0.0.1:3000/)
    echo "$PAGE" | grep -q -- "$KEY" && echo "key found in the page"
    for src in $(echo "$PAGE" | grep -o '/_next/static/[^"]*\.js' | sort -u); do
        curl -s "http://127.0.0.1:3000$src" | grep -q -- "$KEY" && echo "key found in $src"
    done

## Start both applications

They are separate processes. Use two terminals and leave both running.

The service, from `project-a-manual/`:

    .venv/bin/python -m uvicorn backend.main:app --env-file .env --reload

It creates its tables on startup if they are not already there, so there is no migration step
and no database to set up by hand. The first start writes `notes.db`.

The interface, from `project-a-manual/frontend/`:

    npm install
    npm run dev

Open http://localhost:3000.

If port 8000 or 3000 is taken, both take a `--port`, and the service's address has to stay in
step with what the interface is told to call:

    .venv/bin/python -m uvicorn backend.main:app --env-file .env --port 8010
    npm run dev -- --port 3010

with `NOTES_API_URL=http://127.0.0.1:8010` in `frontend/.env.local`.

If the interface cannot reach the service it says so on the page rather than showing an empty
list, so a service you forgot to start looks like a stated problem and not like a store with
nothing in it.

## Read the API

With the service running:

- http://127.0.0.1:8000/docs is the browsable schema
- http://127.0.0.1:8000/redoc is the same content laid out for reading
- http://127.0.0.1:8000/openapi.json is the schema itself

Those three answer without a key. They describe the shape of the API and carry no stored Note,
and requiring a key would have stopped the documentation page rendering at all, since the page
fetches its own schema from the browser. ADR 0005 records the decision.

Everything else needs the key:

| Endpoint | What it does |
| --- | --- |
| `POST /notes` | Write a Note. |
| `GET /notes` | List Notes, most recently changed first. Takes an optional `q` and an optional `tag`. |
| `GET /notes/{note_id}` | Read one Note. |
| `PUT /notes/{note_id}` | Change a Note, replacing its Tags. |
| `DELETE /notes/{note_id}` | Delete a Note. |
| `GET /tags` | List the Tags in use, alphabetically. |

There is no route named `search`. Listing and searching are the same endpoint: `q` matches
anywhere in a title or body whatever the capitalisation, `tag` narrows to Notes carrying that
Tag, and given both it narrows by both. ADR 0002 says why.

Every failure returns one envelope, whatever caused it: a machine-readable `code`, a
human-readable `message`, and a `fields` list when a particular field was at fault. ADR 0003
says why.

The published schema is the authority on request shapes, status codes and that envelope. The
table above is orientation.

## Try it from the command line

    KEY=$(grep '^NOTES_API_KEY=' .env | cut -d= -f2-)

    curl -X POST http://127.0.0.1:8000/notes \
        -H "X-API-Key: $KEY" -H 'Content-Type: application/json' \
        -d '{"title":"Chase the Fenwick invoice","body":"Sent 3 March, still unpaid.","tags":["Work","invoices"]}'

    curl "http://127.0.0.1:8000/notes?q=INVOICE&tag=work" -H "X-API-Key: $KEY"

    curl http://127.0.0.1:8000/tags -H "X-API-Key: $KEY"

The Note comes back carrying `["invoices", "work"]`. `Work` and `work` are one Tag, the
spelling as typed is not kept, and a Tag stops being offered as a filter once no Note carries
it.

Without the key, or with the wrong one:

    curl -i http://127.0.0.1:8000/notes

answers 401 in the same envelope as every other failure.

## How it is laid out

    backend/          the service. An importable package: imports read `from backend.config import ...`
    tests/            the suite, beside the package rather than inside it
    frontend/app/     the interface, with its API route handlers under `app/api/`
    docs/spec.md      what this does and why, in full
    docs/adr/         the decisions binding on it

The repository-wide decisions live in `../docs/adr/`, and `CONTEXT.md` here is the glossary:
Note, Tag, Tag in use, Deleted Note. Those words mean something specific and the code uses them
deliberately.
