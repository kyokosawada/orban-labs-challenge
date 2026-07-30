# A declared column is added to a database that predates it

Schema creation runs at startup as `CREATE TABLE IF NOT EXISTS`, which does nothing to a
database that already has the table. Adding `clicks` to that statement therefore left every
existing database one column short, and every request against it answering `no such column`.

Startup now also compares the declared columns against the ones the database has and runs the
`ALTER TABLE ADD COLUMN` for any that are missing. `expires_at` is declared there for the same
reason `clicks` is. Both statements are literal SQL in
`backend/db.py`; the column list is the only thing read from the database, through
`pragma_table_info` with a bound parameter.

This is not a migration tool. There is no version table, no ordering, and no way to express a
change that is not an added column with a default. It exists so that the guarantee the service
already made - that it starts over a database it created earlier - survives a column being
added.

## Considered Options

- **Leave it.** The service is unreleased, so the only databases that predate the column are on
  the machines of people who ran it while it was being built. Rejected: what they meet is a 500
  on every request, with the reason only in the log, and the fix is to know to delete a file
  nobody told them about.
- **Keep the count in its own table.** A new table is created by the existing idempotent
  statement, so nothing has to be added to an existing database. Rejected: the count belongs to
  a Short Link rather than beside it, and separating them costs the single statement that makes
  resolving and counting one operation.
- **Add the column at startup when it is absent.** Chosen.

## Consequences

A new column has to be declared twice: once in the `CREATE TABLE` that a fresh database gets,
and once as the `ALTER TABLE` that an existing one gets. They can disagree, and nothing checks
that they do not.

The test for this arranges a database in the older shape directly, which is the one place in
the suite that touches storage rather than driving the HTTP surface. There is no way to
produce a database from before a change through the API of the version after it, and the
alternative is leaving the branch untested.
