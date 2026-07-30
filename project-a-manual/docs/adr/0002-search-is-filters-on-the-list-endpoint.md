# Search is filters on `GET /notes`, not a separate endpoint

The brief asks for a search endpoint filtering by tag or keyword. Rather than adding
`/notes/search` alongside `/notes`, the list endpoint takes optional `q` and `tag`
parameters and narrows its results. Unfiltered, it returns everything; with either or both
parameters, it is the search endpoint. A separate route would have duplicated the listing,
serialisation, and ordering logic to no benefit.

Filters combine with AND. The frontend offers a tag filter and a search box at the same time,
and a user who touches both means "notes tagged this, mentioning that". Treating them as OR
would widen the results as the user tries to narrow them.

Keyword matching is a case-insensitive substring test against title and body, so `invoice`
finds `Invoice` and `invoices`.

## Consequences

Anyone auditing this against the brief's requirement list will not find a route named
`search`. The capability is there; the URL is not. Recorded here so that reads as deliberate
rather than missed.
