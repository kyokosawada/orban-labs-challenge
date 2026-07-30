# The schema and the documentation pages need no key

`/openapi.json`, `/docs` and `/redoc` answer anyone. Creating a Short Link and listing Short
Links still require the `X-API-Key` header, and nothing else about the key changes.

The spec says the endpoints that touch data require the key, and the user stories ask for the
API to be documented and browsable. Those pull in opposite directions only if the schema is
treated as data. It is not: it is generated from the code, it names the shapes the service
accepts and answers with, and it contains no Short Code, no Destination and no Click count.
Nothing behind the key is reachable through it.

A key on these three addresses would also make the browsable part unbrowsable. Reading the
documentation would mean pasting the key into a browser before the first request, which is the
habit the rest of this project spends effort avoiding: the key belongs on a server, and a
browser is where it stops being a secret. The Authorize box on the documentation page is a
separate thing, used by a developer who already holds the key and wants to try creation from
that page.

## Considered Options

- **Require the key on all three.** Rejected. It hides a description of an interface whose
  shapes are already in this repository, so it protects nothing, and it costs the one thing the
  documentation exists for. It also answers `401` to anyone probing, which tells them the
  service exists just as loudly.
- **Serve no schema outside development.** Rejected. Deployment is out of scope here, so the
  switch would be a setting nobody ever exercises, and the project would ship with its
  documentation off by default.
- **Answer all three without a key.** Chosen.

## Consequences

Anyone who reaches the service can learn that it is a shortener and how creation is shaped.
That is accepted: creation is refused without the key, resolution is public by design, and the
schema exposes no Short Link anyone created. Tests assert both halves of that, so the openness
is a decision rather than a framework default nobody looked at.
