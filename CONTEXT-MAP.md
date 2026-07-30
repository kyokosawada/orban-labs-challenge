# Context Map

Two independent projects sharing a repository and nothing else. They are separate bounded
contexts: a term defined in one says nothing about the other, and no vocabulary carries
across.

## Contexts

- [Notes](./project-a-manual/CONTEXT.md) - a personal note store, written and found again by
  text or label.

Project B, the URL shortener, has not been designed yet. Its context is added here when it
is.

## Relationships

None. The two projects share no data, no vocabulary, and no running process. They are
deployed and tested independently, and the only thing they have in common is the
repository-wide decisions in [`docs/adr/`](./docs/adr/).
