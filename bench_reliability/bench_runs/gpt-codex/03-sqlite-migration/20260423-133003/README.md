# SQLite Migration POC

This proof of concept uses only Python's standard library.

## Files

- `poc.py`: applies pending SQL migrations in order
- `migrations/001_init.sql`: creates a base table and seeds one row
- `migrations/002_add_users.sql`: creates a `users` table and seeds one row

## How it works

`poc.py` creates `demo.db` in the same directory, ensures a `schema_migrations` table exists, scans `migrations/*.sql`, and applies any file whose stem is not already recorded.

Applied migrations are tracked by migration id:

- `001_init`
- `002_add_users`

## Run

```bash
python poc.py
```

If your machine exposes Python 3 as `python3` instead of `python`, this same script works with:

```bash
python3 poc.py
```

## Expected behavior

First run:

```text
applying 001_init.sql
applying 002_add_users.sql
applied 2 migration(s)
```

Second run:

```text
no pending migrations
```
