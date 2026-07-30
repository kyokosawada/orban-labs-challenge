# Expiry is optional, and an expired link is indistinguishable from one that never existed

A Short Link may be created with a moment after which it stops resolving. Most are created
without one and resolve indefinitely.

The brief lists expired Short Codes among the edge cases to handle but never asks for a way to
create one. Handling a state the system cannot produce would leave a branch no test can reach
and no reviewer can exercise, so the field exists in order to make the required handling real.

A request for an expired Short Code answers exactly as a request for a Short Code that was
never created does. The alternative - telling the caller the link has expired - is friendlier
and leaks information: it confirms that a given Short Code was once real, which lets anyone
probe the space and learn which codes have been issued. Given that codes are the only thing
protecting a Destination from being discovered, that is not worth a better error message.

## Consequences

Someone following a link that has genuinely expired is told only that it is not found, which
will occasionally be confusing and is accepted. The frontend cannot offer a "this link has
expired" message, because the API deliberately does not distinguish the two cases.
