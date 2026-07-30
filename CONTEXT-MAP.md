# Context Map

Two independent projects sharing a repository and nothing else. They are separate bounded
contexts: a term defined in one says nothing about the other, and no vocabulary carries
across.

## Contexts

- [Notes](./project-a-manual/CONTEXT.md) - a personal note store, written and found again by
  text or label.
- [URL Shortening](./project-b-ai-assisted/CONTEXT.md) - trades long web addresses for short
  ones, resolves them, and counts how often each is followed.

## Relationships

None. The two projects share no data, no vocabulary, and no running process. They are
deployed and tested independently, and the only thing they have in common is the
repository-wide decisions in [`docs/adr/`](./docs/adr/).
