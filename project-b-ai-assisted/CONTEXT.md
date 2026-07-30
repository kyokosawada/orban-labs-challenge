# URL Shortening

A store that trades a long web address for a short one, resolves the short one back, and
reports how often each has been followed.

## Language

**Destination**:
The web address a Short Link sends someone to. Supplied by whoever creates the link and never
altered afterwards.
_Avoid_: Target, original URL, long URL

**Short Code**:
The short random string that identifies one Short Link. Two links to the same Destination
have different Short Codes.
_Avoid_: Slug, hash, alias, key, id

**Short Link**:
The pairing of one Short Code with one Destination, together with the count of times it has
been followed. It may carry a moment after which it stops resolving; without one it resolves
indefinitely.
_Avoid_: URL, entry, record, shortlink

**Expired Short Link**:
A Short Link whose expiry moment has passed. It no longer resolves and accrues no further
Clicks. From outside it is indistinguishable from a Short Code that was never created, which
is deliberate.
_Avoid_: Dead link, stale link, lapsed link

**Click**:
One request for a Short Code that resolved to its Destination. It counts requests, not
people: an automated preview fetch by a chat application counts, and one person following the
same link twice counts twice. Requests for a Short Code that does not exist are not Clicks,
because nothing was resolved.
_Avoid_: View, visit, hit, open
