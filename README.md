# Orban Labs Backend Developer Challenge

Giusippi Apa · giusippi.apaii@gmail.com · https://github.com/kyokosawada

## Note on Project A

The challenge asked for Project A to be built without AI tools. I used Claude Code on it anyway, and I want that stated plainly rather than discovered.

I don't hand-write code as my primary workflow anymore. My actual skill is the workflow itself: how I plan, decompose, direct, and review AI-assisted work. Submitting a hand-written Notes API would show you a version of me that doesn't exist and that you wouldn't be hiring.

So both projects were built with Claude Code, and both have full transcripts in their `/prompts/` folders, including Project A. The folder name `project-a-manual/` is kept only because the required structure specifies it.

I understand this may disqualify me. I'd rather be disqualified for something true.

## What's here

Two projects, built to the structure the brief specifies.

- `project-a-manual/` - Notes API. Write a Note with a title, a body and any Tags, see them listed, narrow the list by a keyword or a Tag or both, and edit or delete any of them. FastAPI over SQLite with the SQL written by hand, an API key required on every endpoint that touches a Note, and a Next.js interface that proxies every call so the key never reaches a browser.
- `project-b-ai-assisted/` - URL shortener. Mint a Short Code for a Destination, follow it, and see on a dashboard how many Clicks each has taken. Destinations that are not public `http` or `https` addresses are refused, and a Short Link can carry an expiry after which it stops resolving. Here the API serves the redirect itself and Next.js serves only the creation form and the dashboard, which is the opposite arrangement to Project A and is argued out in that project's ADR 0001.
- `resume.pdf`

Each project has its own `docs/` with the spec and the decisions behind it, `prompts/` with the session transcripts and the models used, and a `README.md` that takes you from a clean machine to both processes running.

The disclosure above was the first commit in this repo, before any code existed. That was deliberate.
