# Hand-written SQL on `sqlite3` instead of an ORM

Both projects persist to SQLite, and the conventional choice would be SQLAlchemy. We use
Python's built-in `sqlite3` and write the queries by hand instead. Each project has a handful
of tables and no migration story to speak of, so an ORM's main benefits do not apply, while
its cost is that the data access becomes framework configuration rather than something a
reader can evaluate. This is a backend challenge, so the SQL is part of what is being shown.

## Consequences

Query construction is manual, so every statement uses bound parameters rather than string
interpolation, and that discipline has to hold everywhere rather than being delegated to a
library. There is no migration tool: schema creation is an explicit idempotent step at
startup. If either project grew a real relational model, this decision would be worth
revisiting.
