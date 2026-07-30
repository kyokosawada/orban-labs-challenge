# Spec: URL Shortener

## Problem Statement

Long web addresses are hostile to share. They break across lines, they get truncated by chat
applications, they cannot be read aloud, and they carry query strings nobody wants to look at.
Someone sharing a link needs a short stand-in that behaves exactly like the original when
followed.

Sharing the same page in two places creates a second problem: once it is out there, there is
no way to tell which posting anyone actually followed. The person sharing wants to know
whether the newsletter or the social post did the work, and the address itself is the only
thing they control.

Some links should also stop working. An address shared for a limited campaign, or one pointing
at something temporary, should not keep resolving indefinitely.

## Solution

A store that trades a Destination for a Short Code. Someone pastes a long address, optionally
says when it should stop working, and gets back a short link they can share. Following that
link sends the visitor to the Destination. A dashboard lists the links they have created with
the number of Clicks each has taken.

Shortening the same Destination twice deliberately produces two different Short Codes, so the
Clicks on each stay separate and can be compared.

Creating a link is protected; following one is not. Anyone with the short link can follow it,
which is the entire point of it. Only someone holding the key can create one.

An expired Short Link, and a Short Code that was never created, behave identically to anyone
asking. Neither resolves and neither explains itself.

## User Stories

1. As a sharer, I want to paste a long Destination and get a Short Link back, so that I have
   something I can actually share.
2. As a sharer, I want the Short Link to be genuinely short, so that it survives being pasted
   into a message or read aloud.
3. As a sharer, I want to copy the Short Link in one action, so that I do not have to select
   it by hand.
4. As a visitor, I want following a Short Link to take me to the Destination, so that it
   behaves like the address it replaced.
5. As a visitor, I want the redirect to be immediate, so that the short link costs me nothing
   over the original.
6. As a visitor, I want to follow a Short Link without any credential, so that a link shared
   publicly works for everyone.
7. As a sharer, I want to see every Short Link I have created, so that I can find one again
   later.
8. As a sharer, I want to see how many Clicks each Short Link has taken, so that I can tell
   which sharing worked.
9. As a sharer, I want to see the Destination beside each Short Link, so that I can tell them
   apart.
10. As a sharer, I want to see when each Short Link was created, so that I can put the numbers
    in context.
11. As a sharer, I want shortening the same Destination twice to give me two Short Codes, so
    that I can compare two channels pointing at one page.
12. As a sharer, I want to set a moment after which a Short Link stops working, so that a
    time-limited campaign does not outlive itself.
13. As a sharer, I want expiry to be optional, so that the ordinary case of a permanent link
    needs no thought.
14. As a visitor, I want an expired Short Link to fail cleanly, so that I am not sent
    somewhere unexpected.
15. As an operator, I want an expired Short Link to be indistinguishable from one that never
    existed, so that nobody can probe which Short Codes have been issued.
16. As an operator, I want Short Codes to be unguessable, so that Destinations cannot be
    discovered by walking the code space.
17. As an operator, I want creating a Short Link to require the key, so that the service
    cannot be used as an open redirector by anyone who finds it.
18. As an operator, I want that key never to reach a browser, so that publishing the interface
    does not publish the key.
19. As an operator, I want non-web schemes refused, so that the service cannot redirect into
    `javascript:` or `data:`.
20. As an operator, I want private and loopback Destinations refused, so that the service is
    not a window onto the network it runs in.
21. As a sharer, I want a malformed Destination rejected with a reason, so that I can correct
    it rather than guess.
22. As a sharer, I want to be told when something failed, so that a blank screen is never the
    only signal.
23. As a sharer, I want to see that something is happening while a link is created, so that I
    do not submit twice.
24. As a sharer, I want the dashboard to reflect a Click without me reloading the page myself,
    so that the numbers are not stale when I look.
25. As a developer picking this up, I want the API documented and browsable, so that I can
    call it without reading the source.
26. As a developer picking this up, I want a setup guide that works from a clean machine, so
    that I can run it without asking anyone.
27. As a reviewer, I want to see which models were used and why, so that the AI-assisted claim
    is verifiable rather than asserted.

## Implementation Decisions

**Two processes, arranged differently to Project A.** A FastAPI service owns the data, the
creation endpoint, the stats endpoint, and the redirect. A Next.js application serves the
creation form and the dashboard. The redirect does not pass through Next.js. Recorded as
ADR 0001 for this project, which also records why this is the opposite arrangement to Project
A's proxy-everything decision.

**The root namespace of the API belongs to Short Codes.** No page route shares it, so a Short
Code can never collide with an application path.

**The public base URL is configuration, not an assumption.** The frontend is told what prefix
to display, so a real deployment could sit behind a genuinely short domain without a code
change.

**Creation requires the key; resolution does not.** The stats endpoint requires it, since it
reports on what the key holder created. The key is read server-side by the Next.js
application and forwarded, never delivered to a browser.

**A Short Code is random**, drawn from an alphabet of digits and mixed-case letters at a length
that makes the space large enough not to be walked. Uniqueness is enforced by the storage
layer rather than by checking first and inserting after, and a collision is handled by
generating again. That retry path is tested rather than assumed unreachable.

Encoding a counter was rejected: it produces shorter codes and never collides, but it makes
every Short Link in the store readable by anyone who can count. There is no per-creator
separation to fall back on, so one enumeration would expose everything.

**Shortening a Destination that already has a Short Code mints a new one.** Recorded as
ADR 0002 for this project.

**Expiry is an optional moment recorded against the Short Link.** A Short Link past it stops
resolving and accrues no further Clicks. A request for an expired Short Code answers exactly
as a request for an unknown one. Recorded as ADR 0003 for this project.

**A Destination must be `http` or `https` and must not be a loopback, link-local, or
private-network address.** Existence is not checked, because confirming it would mean issuing
a network request at creation time on a caller's behalf. Recorded as ADR 0004 for this
project.

**A Click is one request for a Short Code that resolved.** Every resolving request counts,
including automated preview fetches by chat applications and repeat follows by the same
person. This is documented plainly rather than dressed up: the number counts requests, not
people. Identifying automated traffic by user agent was rejected as a guess that cannot be
tested and needs a list nobody maintains. Requests for an unknown or expired Short Code are
not Clicks.

**The Click count is recorded as part of resolving the request**, so a Click that is served is
a Click that is counted.

**Storage is SQLite through hand-written SQL**, with bound parameters throughout and idempotent
schema creation at startup. Repo-wide ADR 0001 owns this.

**Errors follow the same envelope Project A uses**: a machine-readable code, a human-readable
message, and an optional per-field list. The redirect is the exception, since a visitor
following a link is not an API caller and should meet an ordinary status rather than a
document describing one.

**The interface** offers a creation form with an optional expiry, and a dashboard listing
Short Links with their Destination, Click count and creation time. Both loading and failure
are visible states rather than silence.

## Testing Decisions

**A good test drives the API as a caller would**, asserting on responses and on what a later
request can observe. It does not reach into functions or inspect storage directly. A test that
would survive the storage layer being rewritten, and fail if the behaviour changed, is the
right shape.

**One seam: the HTTP surface.** Tests drive FastAPI's test client against the real
application over a real SQLite database created fresh per test, with nothing mocked. This
matches Project A's suite, which is the prior art.

**Redirects are never followed.** The test client chases a 3xx by default, which would make
the suite depend on the internet and assert on somebody else's website. Tests assert on the
status and the `Location` header and never leave the process.

**Address validation is tested with literal addresses, never hostnames.** Deciding whether a
Destination is private requires resolving it, so a test using a hostname would depend silently
on the network and on external DNS. Literal loopback and private addresses need no lookup and
cannot flake.

**One test watches below the seam on purpose.** Proving that creation makes no network request
cannot be done from the response alone, so a single test replaces the socket layer's lookup and
connect with something that fails loudly, then creates a Short Link. It stands in for nothing
the application uses; it only proves the application never leaves the process.

**What gets proven, at minimum:** that a created Short Link resolves to its Destination with
the right status and location; that creation without the key is refused while resolution
without it succeeds; that the same Destination submitted twice yields two different Short
Codes with independent counts; that a Click increments the count and that an unresolved
request does not; that an expired Short Link and an unknown Short Code are indistinguishable
in the response; that a non-web scheme and a private address are both refused with the
documented error shape; and that a Short Code collision is regenerated rather than failing.

## Out of Scope

- The Next.js route handlers and any frontend testing, consistent with Project A. The brief
  asks for backend tests.
- Accounts, per-creator Short Links, and any authorisation beyond the single shared key.
- Editing or deleting a Short Link once created.
- Custom or vanity Short Codes.
- Deduplicating Destinations, cleaning up unused Short Links, or bounding how many may point
  at one Destination.
- Rate limiting on creation.
- Analytics beyond a total count: no per-day breakdown, no referrer, no geography.
- Checking that a Destination is reachable, or scanning it for malware.
- Pagination of the dashboard.
- Deployment, containers, and hosting.

## Further Notes

Every decision in this project has a security dimension the Notes API did not: Short Code
enumeration, open redirection, and whether an error message leaks the existence of a code.
That is inherent to a redirector rather than a quality of this implementation, and the
decisions are recorded so the reasoning can be read rather than inferred.

Two consequences are deliberately weaker than they look. A visitor following a genuinely
expired link is told only that it was not found, which will sometimes confuse them, and is the
price of not confirming which Short Codes exist. And nothing bounds how many Short Links point
at one Destination, which is the cost of keeping their Click counts apart.

This project is required to document its AI usage, including the models used and why, with the
full prompt record. That is a deliverable of the project rather than a note about it.
