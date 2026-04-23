# SQLite Schema Migration POC

A minimal, **stdlib-only** SQLite schema migration system. No third-party
dependencies — just `sqlite3` and the Python standard library.

## Quick start

```bash
# First run — creates the database and applies both migrations
python poc.py

# Second run — idempotent, nothing to do
python poc.py
```

## How it works

1. **Migration files** live in `migrations/` and are named with a numeric
   prefix, e.g. `001_init.sql`, `002_add_users.sql`.
2. On start, `poc.py` creates (or opens) `app.db` and ensures a
   `schema_migrations` table exists.
3. It discovers all `*.sql` files, sorts them, and compares their ids against
   what is already recorded in `schema_migrations`.
4. Any **pending** migrations are applied in order, one at a time.
5. Each applied migration is recorded with its id and a timestamp.

## File layout

```
.
├── poc.py                  # Migration runner (entry point)
├── README.md               # This file
├── migrations/
│   ├── 001_init.sql       # Creates authors + posts tables
│   └── 002_add_users.sql  # Adds users, tags, post_tags tables
└── app.db                  # Created on first run
```

## CLI options

| Flag           | Default          | Description                          |
|----------------|------------------|--------------------------------------|
| `--db`         | `app.db`         | Path to the SQLite database file     |
| `--migrations` | `migrations/`    | Directory containing `.sql` files    |

```bash
python poc.py --db myapp.db --migrations ./custom_migrations
```

## Adding a new migration

1. Create a new file in `migrations/` with the next numeric prefix:
   ```
   migrations/003_add_comments.sql
   ```
2. Write your `CREATE TABLE` / `ALTER TABLE` / `INSERT` statements inside.
3. Run `python poc.py` — it will detect and apply the new migration.

## Idempotency

- Each migration is applied **at most once**. The `schema_migrations` table
  tracks which ids have been run.
- Running `poc.py` multiple times is safe — it will simply report
  `✓ no pending migrations` when there is nothing left to do.

## Requirements

- Python 3.7+
- **No third-party packages** — only `sqlite3` (stdlib)
