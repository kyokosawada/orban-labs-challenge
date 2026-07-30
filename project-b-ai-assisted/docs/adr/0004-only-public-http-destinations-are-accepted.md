# Only public http and https Destinations are accepted

A Destination must use the `http` or `https` scheme and must not resolve to a loopback,
link-local, or private-network address. Everything else is refused at creation.

A shortener is a redirector, and a redirector that accepts any input launders a hostile
Destination behind a link that appears to come from whoever runs it. `javascript:` and
`data:` can execute in a visitor's browser and have no legitimate use here. Private and
loopback addresses turn the service into a small window onto whatever else runs beside it.

Existence is deliberately not checked. Confirming a Destination resolves would mean issuing a
network request at creation time, which is slow, refuses perfectly good links that sit behind
authentication, and makes the API into something that can be aimed at arbitrary hosts on
someone else's behalf. A Destination is therefore validated for shape and address, never for
whether anything is actually there.

## Consequences

Anyone running this on their own machine cannot shorten a `localhost` link, which is
irritating in precisely the setting where it is first tried. That is the intended behaviour
rather than a defect, and the setup guide says so.
