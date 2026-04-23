# SQLite Schema Migration POC

A minimal, zero-dependency SQLite schema migration system built with only Python stdlib (`sqlite3` + `os` + `re`).

## Quick Start

```bash
# First run – creates the database and applies both migrations
python poc.py

# Second run – idempotent, nothing to do
python poc.py
```

## How It Works

1. **Discovery** – Scans the `migrations/` directory for `.sql` files matching the pattern `<digits>_<name>.sql` (e.g. `001_init.sql`, `002_add_users.sql`).

2. **Tracking** – Maintains a `schema_migrations` table inside the SQLite database that records which migration IDs have been applied.

3. **Application** – On each run, compares discovered migrations against applied ones and executes any pending migrations in numeric order, each within a transaction.

## File Structure

```
.
├── poc.py                  # Main migration runner
├── README.md               # This file
├── migrations/
│   ├── 001_init.sql        # Create categories + items tables
│   └── 002_add_users.sql   # Add users table + owner_id column
└── app.db                  # Created on first run
```

## Adding a New Migration

1. Create a new `.sql` file in `migrations/` with the next numeric prefix:
   ```
   migrations/003_add_orders.sql
   ```
2. Write your SQL statements (multiple statements are supported).
3. Run `python poc.py` to apply it.

## Design Decisions

- **No third-party dependencies** – Only `sqlite3`, `os`, and `re` from stdlib.
- **Idempotent** – Running the script multiple times is safe; already-applied migrations are skipped.
- **Numeric ordering** – Migration IDs are zero-padded numbers, ensuring correct sort order.
- **`executescript`** – Each migration file is executed via `executescript()`, which handles multiple statements and auto-commits. The migration ID is then recorded in the tracking table.
