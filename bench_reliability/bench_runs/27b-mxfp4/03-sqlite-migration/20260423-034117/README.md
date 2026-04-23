# SQLite Schema Migration POC

A minimal, stdlib-only SQLite schema migration system. No third-party
dependencies — just the built-in `sqlite3` module.

## Files

| File | Purpose |
|------|---------|
| `poc.py` | Migration runner (entry point) |
| `migrations/001_init.sql` | Creates the `projects` table |
| `migrations/002_add_users.sql` | Creates `users` and `user_projects` tables |
| `README.md` | This file |

## Usage

```bash
# First run — applies both pending migrations
python poc.py

# Second run — idempotent, nothing to do
python poc.py
# Output: no pending migrations
```

### Optional arguments

```bash
python poc.py --db my_database.db --migrations ./my_migrations
```

## How it works

1. **Discovery** — Scans `migrations/` for files matching `NNN_name.sql`.
2. **Tracking** — Maintains a `schema_migrations` table in the SQLite
   database, recording each applied migration id and timestamp.
3. **Execution** — Applies any pending migrations in numeric order,
   idempotently (already-applied migrations are skipped).

## Adding a new migration

Create a new `.sql` file in `migrations/` with the next numeric prefix:

```
migrations/003_add_roles.sql
```

Then run `python poc.py` again.
