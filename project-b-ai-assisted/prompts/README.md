# Prompts and AI usage - URL Shortener

This project was built with Claude Code. This folder is the record of that. There is one file
per session, and each one is converted from Claude Code's own session log rather than written
up afterwards from memory.

## The sessions

| Transcript | Ticket | Ran, 30 July, UTC | Prompts | Assistant replies |
|---|---|---|---|---|
| [01](./01-issue-9-shorten-a-url-and-follow-it.md) | #9 Shorten a URL and follow it | 17:50 to 18:16 | 2 | 310 |
| [02](./02-issue-10-see-your-links-and-their-clicks.md) | #10 See your links and how often they were followed | 18:26 to 19:01 | 1 | 324 |
| [03](./03-issue-11-refuse-unsafe-destinations.md) | #11 Refuse destinations that are not safe to redirect to | 18:26 to 18:53 | 1 | 222 |
| [04](./04-issue-12-let-a-short-link-expire.md) | #12 Let a Short Link expire | 18:26 to 18:46 | 1 | 160 |
| [05](./05-issue-13-setup-guide-and-api-documentation.md) | #13 Setup guide and API documentation | 19:01 to 19:39 | 2 | 228 |

One session took one ticket, in its own git worktree, from a fresh branch to a set of commits,
and stopped. Several ran at the same time on different tickets, which is why the times overlap
and why three sessions start at 18:26.

The prompt counts are low because that is what actually happened. Three of the five sessions
took a single instruction and ran to the end of the ticket without another word.

## Which model, and what it did

`claude-opus-5` did all of it. All 1244 assistant replies in the table above came from it.

Each session finished by running the repository's `/code-review`, which reads the session's
own diff twice over: once against the repository's coding standards, and once against the
ticket the work came from. Those two readers are separate sub-agents. The five sessions spawned
twelve of them, because ticket #11 ran the review twice, and they added another 289 replies.
They ran on `claude-opus-5` too. Their findings, and what each session did about each finding,
are in the transcripts.

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

This project's share of them, the glossary, the spec and ADRs 0001 to 0004, was committed in
one commit, `a242798`, before any code in this project existed. The context map and the
repository-wide ADR came earlier, in `126ed35`, alongside Project A's half of the same
conversation.

### What that conversation settled

It fixed the vocabulary first. `CONTEXT.md` defines Destination, Short Code, Short Link,
Expired Short Link, and Click, and each entry lists the words not to use for it. Those
definitions carry real behaviour: a Click counts resolved requests rather than people, so an
automated preview fetch counts and a request for a code that does not exist does not; an
expired Short Link is defined as indistinguishable from one that was never created.

It separated the two projects. `CONTEXT-MAP.md` records that they share a repository and
nothing else: no data, no vocabulary, no running process. A term defined here says nothing
about the Notes API. That separation is why this project reaches the opposite architectural
answer to Project A on the same question rather than inheriting it.

It wrote the spec as a problem, a solution, and user stories, then a section of implementation
decisions and a section of testing decisions, and then what is out of scope.

It settled five decisions before any code, each recorded with the options that lost:

- SQL written by hand on Python's `sqlite3` rather than an ORM, repository-wide, because this
  is a backend exercise and the queries are part of what is being shown.
- The API serves the redirect itself, and only creation and the dashboard go through Next.js.
  This is deliberately the reverse of Project A. Project A's proxy exists to keep an API key
  out of a browser, and a redirect carries no key, so here the hop would cost latency on the
  only latency-sensitive path and would hand the root namespace to page routes.
- Shortening the same URL twice mints a second Short Code rather than returning the first,
  because merging them merges Clicks the caller deliberately kept apart.
- Expiry is optional, and an expired Short Code answers exactly as an unknown one does. Saying
  "expired" would confirm that a code was once real and let anyone probe the space.
- Only public `http` and `https` destinations are accepted. A redirector that accepts anything
  launders a hostile destination behind a link that looks like yours.

It set the test seam: drive the real application through FastAPI's test client against a real
SQLite database created per test, with nothing mocked, and never let a test follow a redirect,
because a client that chases a 3xx makes the suite fetch someone else's website.

Then it cut the work into tickets #9 to #13, which are the five sessions above.

### What was decided later, in the ticket sessions

Not every decision came from that conversation, and the record should not suggest otherwise.
Four of this project's eight ADRs were argued out during the work:

- ADR 0005, the redirect is `302` and never cached, during ticket #9. A cached `301` would keep
  sending people to a destination the service has stopped serving, and a cached redirect is a
  Click the service never sees.
- ADR 0006, how a declared column reaches a database that predates it, during ticket #10, after
  adding `clicks` to the create statement left existing databases answering `no such column`.
  The same session then carried `expires_at` through that step, because ticket #12 had landed
  a second declared column with the same problem.
- ADR 0007, the schema and documentation pages need no key, during ticket #13.
- ADR 0008, the schema publishes only the responses the service can answer, also during ticket
  #13, after the generated schema was found to advertise a `422` the redirect cannot reach.

Two of the pre-code decisions were also amended during a ticket. ADR 0004 gained the paragraph
admitting what the address rules do not reach, in commit `5d97d5b` during ticket #11: no name
is resolved, so a hostname pointing at a private address is accepted, and closing that gap
would need the lookup the decision refuses to make. The spec was amended in the same session,
in commit `c815a73`, to close the address rules over the forms of an address a browser reads
the same way.

All of those arguments are in the transcripts in this folder, in full.
