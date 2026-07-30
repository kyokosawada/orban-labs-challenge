# Spec: Notes API

## Problem Statement

Someone who writes things down needs them back later. A note written three weeks ago is
worthless if the only way to reach it is scrolling. They half-remember a word from it, or
they remember it was to do with work, and they need that to be enough to find it again.

They also need writing to be cheap. If labelling a note is fiddly, or if capitalising a
label differently silently splits their notes into two groups, they stop labelling. And they
need to be able to throw a note away without fearing that a slip destroys something they
wanted.

## Solution

A store for Notes with a web interface. A person writes a Note with a title, a body, and any
Tags they like. They see their Notes listed, narrow that list by typing a word or picking a
Tag, and edit or delete any of them.

Finding is the centre of it. Typing a word matches anywhere in a Note's title or body,
regardless of case. Picking a Tag narrows to Notes carrying it. Doing both narrows further,
never wider - every control the person touches reduces what they are looking at.

Tags behave the way a person expects rather than the way storage would suggest. `Work` and
`work` are the same Tag. The Tag list offers only Tags that would actually find something.

Deleting removes a Note from the product entirely. It stops appearing, stops matching
searches, and cannot be fetched. Underneath, the record is retained so a mistake is
recoverable by hand, but nothing in the product exposes that.

## User Stories

1. As a writer, I want to create a Note with a title and a body, so that I can record
   something before I forget it.
2. As a writer, I want to create a Note with only a title, so that a one-line reminder does
   not force me to fill in a body.
3. As a writer, I want to attach several Tags to a Note as I write it, so that I do not have
   to organise it in a second step.
4. As a writer, I want to see all my Notes in one list, so that I can get an overview without
   searching for anything.
5. As a writer, I want the most recently changed Notes first, so that what I am working on is
   at the top.
6. As a writer, I want to open a single Note, so that I can read it in full.
7. As a writer, I want to edit a Note's title and body, so that I can correct or extend what
   I wrote.
8. As a writer, I want to change a Note's Tags after writing it, so that my organisation can
   improve as I learn how I use it.
9. As a writer, I want to remove every Tag from a Note, so that I can un-organise something I
   mis-filed.
10. As a writer, I want to delete a Note, so that things I no longer want stop cluttering my
    list.
11. As a writer, I want a deleted Note to disappear from every list and search, so that
    deleting means something.
12. As a writer, I want to search by a word, so that I can find a Note I only half remember.
13. As a writer, I want search to look at both the title and the body, so that I do not have
    to remember where in the Note the word was.
14. As a writer, I want search to ignore capitalisation, so that `invoice` finds a Note about
    `Invoices`.
15. As a writer, I want a partial word to match, so that `invoice` finds `invoices` without me
    guessing the exact form.
16. As a writer, I want to filter by a Tag, so that I can see everything on one topic.
17. As a writer, I want to search and filter at the same time, so that I can find the Note
    about invoices among everything tagged work.
18. As a writer, I want the Tag filter to list the Tags I have actually used, so that I do not
    have to remember what I typed.
19. As a writer, I want a Tag to stop being offered once no Note carries it, so that I am
    never given a filter that finds nothing.
20. As a writer, I want `Work` and `work` treated as one Tag, so that my Notes group together
    even when I type carelessly.
21. As a writer, I want stray spaces around a Tag ignored, so that a trailing space does not
    create a second Tag.
22. As a writer, I want to be told clearly when something I submitted is not acceptable, so
    that I can fix it rather than guess.
23. As a writer, I want to be told which field was wrong, so that a long form does not become
    a hunt.
24. As a writer, I want an empty search to return everything rather than nothing, so that
    clearing the box restores my list.
25. As a writer, I want to see when a Note was created and when it was last changed, so that I
    can tell old notes from fresh ones.
26. As a writer, I want the interface to tell me when something has gone wrong on the server,
    so that a blank screen is never the only signal.
27. As an operator, I want an accidentally deleted Note to still exist in storage, so that I
    can recover it by hand if the writer asks.
28. As an operator, I want the API to require a key, so that it is not open to anyone who
    finds the address.
29. As an operator, I want that key never to reach the browser, so that publishing the
    interface does not publish the key.
30. As a developer picking this up, I want the API documented and browsable, so that I can
    call it without reading the source.
31. As a developer picking this up, I want a setup guide that works from a clean machine, so
    that I can run it without asking anyone.

## Implementation Decisions

**Two processes.** A FastAPI service owning the data, and a Next.js application serving the
interface. They are started separately and developed separately.

**The interface never calls the API from the browser.** Next.js route handlers receive the
browser's requests, attach the API key from a server-side environment variable, and forward
them. The key is therefore never delivered to a client. Recorded as ADR 0001 for this project.

**Authentication is a single shared key on a request header.** There are no user accounts and
no per-user data; a Note belongs to whoever holds the key. Every API endpoint requires it.

**Storage is SQLite, addressed with hand-written SQL through Python's `sqlite3`.** No ORM.
Every statement uses bound parameters. Schema creation is an explicit idempotent step at
startup, since there is no migration tool. Recorded as repo-wide ADR 0001.

**Three tables.** Notes, Tags, and the association between them. A Tag is a row in its own
right rather than a string on a Note, which makes listing the Tags in use a single query and
makes filtering an exact match rather than a substring test.

**A Tag is identified by its normalised form**, trimmed and lowercased. The spelling as typed
is not retained. Attaching `Work` and `work` to the same Note is one Tag, not two.

**A Tag row is never deleted.** When the last Note carrying it stops doing so, the row
remains and simply stops being reported as in use. Nothing surfaces a Tag in use by nothing.

**Listing and searching are the same endpoint.** The Notes collection accepts an optional
keyword and an optional Tag. Absent both, it returns everything. Present together, they
combine with AND. There is no separate search route. Recorded as ADR 0002 for this project.

**Keyword matching is a case-insensitive substring test** against title and body.

**Deletion sets a flag and retains the row.** Every read path excludes deleted Notes: the
listing, both filters, the Tag-in-use query, and fetching one by id, which answers as though
the Note never existed. No endpoint lists or restores deleted Notes. Recorded as ADR 0004 for
this project.

**Every failure returns the same shape**: a stable machine-readable code, a human-readable
message, and an optional per-field list. FastAPI's default validation response is replaced so
that validation failures, authentication failures, missing Notes, and unhandled errors are
all rendered identically. The published API schema describes this shape. Recorded as ADR 0003
for this project.

**Validation rules.** A title is required and is between 1 and 200 characters once trimmed. A
body is optional and may be empty, with a ceiling of 10,000 characters. A Note carries at
most 20 Tags, each between 1 and 50 characters, made of letters, digits, hyphens and
underscores only. Duplicate Tags within one request collapse silently rather than failing.
Fields the API does not recognise are rejected rather than ignored, so that a typo in the
interface surfaces immediately instead of silently discarding data.

**A Note is identified by an integer.** Timestamps for creation and last change are set by the
service, not accepted from the caller.

**The interface** offers a list with a search box and a Tag filter, a form for creating and
editing, and a delete action. Failures from the API are rendered to the person rather than
logged and swallowed. Because every error shares one shape, this is one rendering path.

## Testing Decisions

**A good test here exercises the API as a caller would.** It sends a request and asserts on
the response and on what a subsequent request can observe. It does not reach into functions,
inspect the database directly, or assert on how a query was built. If a test would still pass
after the storage layer were rewritten, and fail if the behaviour changed, it is the right
shape.

**One seam: the HTTP surface.** Tests drive FastAPI's test client against the real
application, backed by a real SQLite database created fresh for each test. Nothing is mocked.
Mocking storage would be actively wrong here, because hand-written SQL is a substantial part
of what this project exists to demonstrate; a test that stubs it proves nothing about it.

**What gets proven, at minimum:** that a Note survives a create and can be read back; that
the keyword and Tag filters each narrow the list and narrow it further in combination; that
Tag normalisation collapses differently-capitalised spellings into one Tag; that a deleted
Note vanishes from listing, search and direct fetch; that a Tag whose only Notes are deleted
stops being offered as a filter; that an invalid submission returns the documented error
shape naming the offending field; and that a request without the key is refused.

**No prior art.** The repository is empty, so these tests establish the pattern rather than
following one.

## Out of Scope

- The Next.js route handlers and any frontend testing. The brief asks for backend tests, and
  four tests proving real behaviour are worth more than a suite padded to look thorough.
- User accounts, per-user Notes, and any authorisation beyond the single shared key.
- Restoring a deleted Note, or any interface that reaches one.
- Renaming or merging Tags.
- Pagination. The expected volume does not justify it, and adding it would complicate the
  filter behaviour that matters more.
- Migrations. The schema is created idempotently at startup.
- Deployment, containers, and hosting.

## Further Notes

Two decisions are deliberately weaker than they look and are recorded as such, so that
neither reads as an oversight. Soft delete gives the person using the product nothing at all;
it is insurance for whoever runs the database, bought at the cost of a predicate on every
read. And normalising Tags discards the capitalisation the writer chose, permanently, in
exchange for Tags that group reliably.

The absence of a route named `search` is deliberate and is the most likely thing to be read
as a missing requirement. The capability is present as filters on the Notes collection.
