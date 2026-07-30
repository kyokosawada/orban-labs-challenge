# Orban Labs Backend Developer Challenge

## Agent skills

### Issue tracker

Issues live as GitHub issues in `kyokosawada/orban-labs-challenge`, managed via the
`gh` CLI. External PRs are not a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles use their default label strings: `needs-triage`,
`needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
See `docs/agents/triage-labels.md`.

### Domain docs

Multi-context: `CONTEXT-MAP.md` at the root points to one `CONTEXT.md` per project
(`project-a-manual/`, `project-b-ai-assisted/`). See `docs/agents/domain.md`.

## Project A (`project-a-manual/`)

`backend/` and `tests/` are named by the Orban submission form, which validates the
layout on submit. Do not rename either.

The spec is `docs/spec.md` and the decisions binding on it are `docs/adr/` plus the
repo-wide `docs/adr/`. Honour them rather than re-deciding; the ADRs record what was
already weighed.

Run from `project-a-manual/`:

    python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
    .venv/bin/python -m pytest
    NOTES_API_KEY=... .venv/bin/python -m uvicorn backend.main:app --reload

Environment variables are listed in `.env.example` here and in `frontend/.env.example`.
The API key is server-side only: no key-related value may be prefixed `NEXT_PUBLIC_`.

There is no migration tool and schema creation is `CREATE TABLE IF NOT EXISTS` at
startup, so a new column will not appear on an existing database. Adding a table is
safe; adding a column to `notes` needs a deliberate plan.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
