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

Case is folded in Python rather than in SQL. SQLite's `LIKE`, and its `LOWER`, fold only the
26 unaccented letters, so searching `CAFÉ` would have found nothing while a Tag already counts
an accented letter as a letter. Both sides of the comparison go through `str.lower`,
registered on the connection as a SQL function. `str.casefold` would fold further and match
`Straße` for `strasse`, which is no longer a substring test, so `lower` is the one used.

## Consequences

Anyone auditing this against the brief's requirement list will not find a route named
`search`. The capability is there; the URL is not. Recorded here so that reads as deliberate
rather than missed.

Folding in Python means a keyword search reads every live Note rather than an index, and calls
back into Python twice per row. At the volume this store expects, that costs less than
explaining why a capital `É` stops matching.
