#!/usr/bin/env python3
"""
Minimal SQLite schema migration POC — stdlib only.

Usage:
    python poc.py                  # migrate <db> (default: app.db)
    python poc.py mydb.sqlite      # migrate a specific database

Migrations live in the migrations/ directory as .sql files,
named with a numeric prefix for ordering, e.g.:
    001_init.sql
    002_add_users.sql
"""

import os
import re
import sqlite3
import sys


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")
DB_PATH = sys.argv[1] if len(sys.argv) > 1 else "app.db"
MIGRATIONS_TABLE = "schema_migrations"

# Regex to extract the migration id from a filename like "001_init.sql"
MIGRATION_ID_RE = re.compile(r"^(\d+)_")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_db(db_path: str) -> sqlite3.Connection:
    """Return a connection with row_factory set for dict-like access."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_migrations_table(conn: sqlite3.Connection) -> None:
    """Create the schema_migrations tracking table if it doesn't exist."""
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {MIGRATIONS_TABLE} (
            id TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def get_applied_migrations(conn: sqlite3.Connection) -> set[str]:
    """Return the set of migration ids already applied."""
    rows = conn.execute(
        f"SELECT id FROM {MIGRATIONS_TABLE} ORDER BY id"
    ).fetchall()
    return {row["id"] for row in rows}


def discover_migrations(migrations_dir: str) -> list[str]:
    """
    Return a sorted list of migration ids from .sql files in *migrations_dir*.

    Only files matching the pattern <digits>_*.sql are considered.
    """
    migration_ids: list[str] = []
    if not os.path.isdir(migrations_dir):
        return migration_ids

    for filename in os.listdir(migrations_dir):
        if not filename.endswith(".sql"):
            continue
        match = MIGRATION_ID_RE.match(filename)
        if match:
            migration_ids.append(match.group(1))

    migration_ids.sort()
    return migration_ids


def read_migration(migrations_dir: str, migration_id: str) -> str:
    """Read and return the SQL content for a given migration id."""
    for filename in os.listdir(migrations_dir):
        if MIGRATION_ID_RE.match(filename) and filename.startswith(migration_id + "_"):
            filepath = os.path.join(migrations_dir, filename)
            with open(filepath, "r", encoding="utf-8") as fh:
                return fh.read()
    raise FileNotFoundError(f"Migration file for id {migration_id} not found")


def apply_migration(conn: sqlite3.Connection, migration_id: str) -> None:
    """Execute a single migration and record it in schema_migrations."""
    sql = read_migration(MIGRATIONS_DIR, migration_id)
    print(f"  Applying migration {migration_id} ...")
    conn.executescript(sql)
    conn.execute(
        f"INSERT INTO {MIGRATIONS_TABLE} (id) VALUES (?)",
        (migration_id,),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print(f"Database : {DB_PATH}")
    print(f"Migrations dir: {MIGRATIONS_DIR}")
    print()

    conn = get_db(DB_PATH)
    try:
        ensure_migrations_table(conn)

        applied = get_applied_migrations(conn)
        all_migrations = discover_migrations(MIGRATIONS_DIR)

        pending = [mid for mid in all_migrations if mid not in applied]

        if not pending:
            print("No pending migrations.")
            return

        print(f"Found {len(all_migrations)} migration(s) total, {len(pending)} pending:")
        for mid in pending:
            print(f"  - {mid}")
        print()

        for migration_id in pending:
            apply_migration(conn, migration_id)
            print(f"  ✓ Migration {migration_id} applied.")

        print()
        print("Done.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
