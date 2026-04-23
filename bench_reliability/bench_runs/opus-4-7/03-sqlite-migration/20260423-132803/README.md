# SQLite Schema Migration POC

Minimal migration system using only Python stdlib (`sqlite3` + `glob` + `os`).

## Usage

```bash
python poc.py
```

First run creates `app.db` and applies all pending migrations:

```
applying 2 migration(s)...
  applied: 001_init.sql
  applied: 002_add_users.sql
done.
```

Second run is idempotent:

```
no pending migrations
```

## Adding migrations

Drop a new `.sql` file in `migrations/` with the next numeric prefix:

```
migrations/003_add_comments.sql
```

Then run `python poc.py` again.

## How it works

1. A `schema_migrations` table tracks which migration files have been applied (by filename).
2. On each run, the tool scans `migrations/*.sql`, sorts by filename, and applies any that aren't yet in `schema_migrations`.
3. Each migration runs inside `executescript` (supports multiple statements per file).
