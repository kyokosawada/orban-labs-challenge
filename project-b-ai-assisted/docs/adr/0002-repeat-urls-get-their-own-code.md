# Shortening the same URL twice produces two codes

Submitting a long URL that already has a short code mints a new one rather than returning the
existing code. The two links point at the same destination and count their clicks separately.

Reusing the code would look tidier and would keep one row per destination, but it silently
merges the click counts of two links the caller deliberately created as separate. Shortening
one page twice on purpose is the ordinary case for a shortener that reports clicks: one link
for one channel, one for another, so the numbers can be compared. Once merged there is no way
for the caller to ask for them apart again.

There is also no notion of ownership here. A single shared key creates everything, so the
system cannot distinguish one person's accidental resubmission from two deliberate links.

## Consequences

Nothing bounds the number of codes pointing at one destination, and there is no cleanup or
deduplication story. A caller in a loop can create links without limit. Accepted: this is a
demonstration store with an authenticated creation path, and rate limiting is out of scope.
