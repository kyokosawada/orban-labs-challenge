# Prompts and AI usage - Notes API

This project was built with Claude Code. This folder is the record of that. There is one file
per session, and each one is converted from Claude Code's own session log rather than written
up afterwards from memory.

## The sessions

| Transcript | Ticket | Ran, 30 July, UTC | Prompts | Assistant replies |
|---|---|---|---|---|
| [01](./01-issue-2-write-a-note-and-see-it-listed.md) | #2 Write a Note and see it listed | 17:00 to 17:43 | 4 | 307 |
| [02](./02-issue-3-tag-a-note-and-filter-by-tag.md) | #3 Tag a Note and filter by Tag | 17:50 to 18:24 | 2 | 285 |
| [03](./03-issue-4-find-a-note-by-keyword.md) | #4 Find a Note by keyword | 18:26 to 18:42 | 1 | 164 |
| [04](./04-issue-5-edit-a-note.md) | #5 Edit a Note | 18:26 to 18:48 | 1 | 194 |
| [05](./05-issue-6-delete-a-note.md) | #6 Delete a Note | 18:26 to 19:00 | 1 | 310 |
| [06](./06-issue-7-setup-guide-and-api-documentation.md) | #7 Setup guide and API documentation | 19:04 to 19:36 | 1 | 275 |

One session took one ticket, in its own git worktree, from a fresh branch to a set of commits,
and stopped. Several ran at the same time on different tickets, which is why the times overlap
and why three sessions start at 18:26.

The prompt counts are low because that is what actually happened. Four of the six sessions
took a single instruction and ran to the end of the ticket without another word.

## Which model, and what it did

`claude-opus-5` did all of it. All 1535 assistant replies in the table above came from it.

Each session finished by running the repository's `/code-review`, which reads the session's
own diff twice over: once against the repository's coding standards, and once against the
ticket the work came from. Those two readers are separate sub-agents, so the six sessions
spawned twelve of them between them, adding another 256 replies. They ran on `claude-opus-5`
too. Their findings, and what each session did about each finding, are in the transcripts.

There was no split where one model planned and a cheaper one typed, and no part of this
project was reviewed by a different model from the one that wrote it.

Two earlier sessions prepared the repository before either project existed. The first ran on
`claude-opus-4-8` and produced the first commit: the root `README.md` with its disclosure, and
`resume.pdf`. It also noticed that the author's global git identity was a work email address
belonging to another company, and set a repository-local personal identity before anything was
committed. The second ran on `claude-opus-5` and wrote the agent configuration under
`docs/agents/`. Neither wrote a line of this project, and neither is reproduced here: they
contain personal material unrelated to either project, including that work address.

## How these files were made

Each file is generated from its session's JSONL log. Every user prompt and every visible
assistant reply is present, in order, unedited. That includes the wrong turns: where a session
took a bad approach and had to come back, both halves are in the file, because the correction
is the part worth reading.

Four categories were left out of every file, and each file states its own counts at the top:
the results of tool calls, the bodies of file writes and edits, the model's internal reasoning
blocks, and Claude Code's own bookkeeping records. The tool calls themselves are kept, one line
each, so the sequence of work stays visible. Absolute paths were rewritten: the worktree is
`<repo>` and the home directory is `~`.

Nothing was cut for being unflattering.

## The planning conversation is not here, and there is no transcript of it

Both projects were designed in one conversation that ran before any ticket was opened. That
conversation is not in this folder and no transcript of it exists anywhere in this repository.
It ran in a session that also carries unrelated client work, including live security details
belonging to other people, so it cannot be published. Summarising it is the honest option
available. Reproducing it is not an option at all.

What follows is a summary, and it is written from that conversation's output rather than from
the conversation itself. The output is in this repository, and it is what the summary should be
checked against:

- [`CONTEXT-MAP.md`](../../CONTEXT-MAP.md)
- [`CONTEXT.md`](../CONTEXT.md)
- [`docs/spec.md`](../docs/spec.md)
- [`docs/adr/0001-hand-written-sql-instead-of-an-orm.md`](../../docs/adr/0001-hand-written-sql-instead-of-an-orm.md), repository-wide
- [`docs/adr/`](../docs/adr/) 0001 to 0004

Those files were committed in one commit, `126ed35`, before any code existed.

### What that conversation settled

It fixed the vocabulary first. `CONTEXT.md` defines Note, Tag, Tag in use, and Deleted Note,
and each entry lists the words not to use for it. Those definitions carry real behaviour: a Tag
is identified by its normalised form, so `Work` and `work` are one Tag and the spelling as
typed is not kept; a Tag is only in use if a live Note carries it, because a filter that
returns nothing is not worth offering.

It separated the two projects. `CONTEXT-MAP.md` records that they share a repository and
nothing else: no data, no vocabulary, no running process. A term defined here says nothing
about the shortener.

It wrote the spec as a problem, a solution, and user stories, then a section of implementation
decisions and a section of testing decisions, and then what is out of scope. Finding a Note is
the centre of it, and every control narrows rather than widens.

It settled five decisions before any code, each recorded with the options that lost:

- SQL written by hand on Python's `sqlite3` rather than an ORM, repository-wide, because this
  is a backend exercise and the queries are part of what is being shown.
- The frontend proxies every API call through a Next.js route handler so the API key stays on
  the server. A browser cannot hold a secret.
- Search is optional filters on `GET /notes`, not a separate `/notes/search`. Filters combine
  with AND.
- One error envelope for every failure, including the validation errors FastAPI would
  otherwise return in its own shape.
- Notes are soft deleted with no restore path, which is insurance for whoever runs the
  database, not a feature for the person using the app.

It set the test seam: drive the real application through FastAPI's test client against a real
SQLite database created per test, with nothing mocked.

Then it cut the work into tickets #2 to #7, which are the six sessions above.

### What was decided later, in the ticket sessions

Not every decision came from that conversation, and the record should not suggest otherwise:

- ADR 0002 gained its paragraph on folding case in Python rather than in SQL during ticket #4,
  after `CAFÉ` was found not to match anything.
- ADR 0005, on the documentation endpoints not requiring the key, was decided during ticket #7.
  The spec asks for a browsable API and also says every endpoint requires the key, and that
  session had to resolve the two.

Both arguments are in the transcripts in this folder, in full.
