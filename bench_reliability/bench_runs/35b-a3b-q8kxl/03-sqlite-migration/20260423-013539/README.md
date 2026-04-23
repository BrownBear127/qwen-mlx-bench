# SQLite Schema Migration POC

A minimal, zero-dependency SQLite schema migration system using only Python stdlib.

## Features

- Tracks applied migrations in a `schema_migrations` table
- Reads `.sql` migration files from the `migrations/` directory
- Applies pending migrations in numeric order
- Idempotent — safe to run multiple times

## Usage

```bash
# First run: creates the database and applies all migrations
python poc.py

# Second run: prints "no pending migrations"
python poc.py
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MIGRATE_DB` | `app.db` | Path to the SQLite database file |

## Migration File Naming

Migration files must be placed in the `migrations/` directory and follow this naming convention:

```
NNN_description.sql
```

Where `NNN` is a zero-padded numeric prefix that determines execution order.

Example:
```
migrations/
├── 001_init.sql
└── 002_add_users.sql
```

## How It Works

1. On startup, `poc.py` creates a `schema_migrations` table if it doesn't exist.
2. It scans the `migrations/` directory for `.sql` files matching the naming pattern.
3. It compares discovered migration IDs against already-applied ones.
4. Any pending migrations are executed in order, then recorded.
5. Running again finds no pending migrations and exits cleanly.

## Dependencies

None. Uses only Python standard library (`sqlite3`, `os`, `re`, `sys`).
