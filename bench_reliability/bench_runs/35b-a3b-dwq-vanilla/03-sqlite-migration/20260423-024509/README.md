# SQLite Schema Migration POC

A minimal, **stdlib-only** SQLite schema migration system. No third-party
libraries — just `sqlite3` and the Python standard library.

## How it works

1. A `schema_migrations` table is created in the database to track which
   migrations have been applied.
2. `.sql` files in the `migrations/` directory are discovered, sorted by
   their numeric prefix, and any that haven't been applied yet are executed
   in order.
3. Running the script a second time is a no-op — it prints
   `"No pending migrations."`

## Files

| File | Purpose |
|---|---|
| `poc.py` | Migration runner (stdlib only) |
| `migrations/001_init.sql` | Creates `users` and `posts` tables |
| `migrations/002_add_users.sql` | Adds `display_name` and `bio` columns |
| `README.md` | This file |

## Usage

```bash
# Migrate the default database (app.db)
python poc.py

# Migrate a specific database
python poc.py mydb.sqlite
```

### First run (creates DB + applies both migrations)

```
Database : app.db
Migrations dir: ./migrations

Found 2 migration(s) total, 2 pending:
  - 001
  - 002

  Applying migration 001 ...
  ✓ Migration 001 applied.
  Applying migration 002 ...
  ✓ Migration 002 applied.

Done.
```

### Second run (idempotent)

```
Database : app.db
Migrations dir: ./migrations

No pending migrations.
```

## Requirements

- Python 3.7+ (uses only stdlib)
- No `requirements.txt` needed — zero third-party dependencies.
