# Notes are soft-deleted, and nothing restores them

Deleting a Note marks it deleted and retains the row rather than removing it. There is
deliberately no restore endpoint and no interface for reaching a deleted Note: this is
insurance for whoever runs the database, not a feature for the person using the app. A
mistaken delete is recoverable by hand; from the product's point of view the Note is gone.

## Consequences

Every read path must exclude deleted Notes - the list, the search filters, and fetching one
by id, which returns 404 for a deleted Note exactly as it would for one that never existed.

The Tag-in-use query must exclude them too. A Tag whose only Notes are deleted is not in use,
and failing to account for that would offer a filter that returns nothing, which is the
behaviour we specifically decided against.

A reviewer may reasonably ask what soft delete buys a user here. Nothing - and that is the
point of recording it. It buys recoverability for the operator, at the cost of a predicate on
every query.
