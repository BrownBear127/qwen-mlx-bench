# SQLite Schema Migration POC

A minimal, zero-dependency SQLite schema migration system using only the Python standard library.

## Files

```
poc.py              # Migration runner
migrations/         # Directory containing .sql migration files
  001_init.sql      # Example: creates categories table
  002_add_users.sql # Example: creates users table with FK to categories
README.md           # This file
```

## How It Works

1. **Discovery** — `poc.py` scans the `migrations/` directory for files matching the pattern `NNN_name.sql` (e.g. `001_init.sql`).
2. **Tracking** — A `schema_migrations` table in the SQLite database records which migration IDs have been applied.
3. **Application** — On each run, any pending migrations are applied in numerical order. Running again is a no-op (idempotent).

## Usage

```bash
# First run — creates app.db and applies both migrations
python poc.py

# Second run — nothing to do
python poc.py
```

### Expected output

**First run:**
```
Applying 2 migration(s)...
  Applied migration 001
  Applied migration 002
Done.
```

**Second run:**
```
No pending migrations.
```

## Adding a New Migration

1. Create a new file in `migrations/` with the next sequential number:
   ```
   migrations/003_add_posts.sql
   ```
2. Write your SQL (DDL/DML) in the file.
3. Run `python poc.py` to apply it.

## Dependencies

None. Uses only Python stdlib (`sqlite3`, `os`, `re`).
