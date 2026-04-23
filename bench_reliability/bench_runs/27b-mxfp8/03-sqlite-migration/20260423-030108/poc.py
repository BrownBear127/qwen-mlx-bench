#!/usr/bin/env python3
"""
Minimal SQLite schema migration system — stdlib only.

Usage:
    python poc.py [--db <path>] [--migrations <dir>]

Defaults:
    --db          →  app.db
    --migrations  →  migrations/
"""

import argparse
import glob
import os
import sqlite3
import sys


DEFAULT_DB = "app.db"
DEFAULT_MIGRATIONS_DIR = "migrations"


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open (or create) the SQLite database and return a connection."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def ensure_migrations_table(conn: sqlite3.Connection) -> None:
    """Create the schema_migrations table if it doesn't exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id   TEXT PRIMARY KEY,
            applied_at  TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        )
        """
    )
    conn.commit()


def get_applied_migration_ids(conn: sqlite3.Connection) -> set[str]:
    """Return the set of migration ids that have already been applied."""
    cur = conn.execute("SELECT id FROM schema_migrations")
    return {row[0] for row in cur.fetchall()}


def discover_migrations(migrations_dir: str) -> list[str]:
    """
    Return a sorted list of migration file paths.

    Files must be .sql and live in *migrations_dir*.
    """
    pattern = os.path.join(migrations_dir, "*.sql")
    return sorted(glob.glob(pattern))


def migration_id_from_path(path: str) -> str:
    """
    Derive the migration id from the file name.

    Example:  migrations/002_add_users.sql  →  002_add_users
    """
    return os.path.splitext(os.path.basename(path))[0]


def apply_migration(conn: sqlite3.Connection, path: str, mid: str) -> None:
    """Execute a single migration file and record it."""
    sql = open(path, "r", encoding="utf-8").read()
    conn.executescript(sql)
    conn.execute("INSERT INTO schema_migrations (id) VALUES (?)", (mid,))
    conn.commit()


def run(db_path: str = DEFAULT_DB, migrations_dir: str = DEFAULT_MIGRATIONS_DIR) -> None:
    """Main entry point — apply any pending migrations."""
    conn = get_connection(db_path)
    try:
        ensure_migrations_table(conn)
        applied = get_applied_migration_ids(conn)
        migration_files = discover_migrations(migrations_dir)

        pending = [
            (f, migration_id_from_path(f))
            for f in migration_files
            if migration_id_from_path(f) not in applied
        ]

        if not pending:
            print("✓ no pending migrations")
            return

        for path, mid in pending:
            print(f"→ applying migration {mid} …")
            apply_migration(conn, path, mid)
            print(f"  ✓ {mid} applied")

        print(f"\nDone. {len(pending)} migration(s) applied.")
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply pending SQLite schema migrations."
    )
    parser.add_argument(
        "--db",
        default=DEFAULT_DB,
        help=f"Path to the SQLite database (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--migrations",
        default=DEFAULT_MIGRATIONS_DIR,
        help=f"Directory containing .sql migration files (default: {DEFAULT_MIGRATIONS_DIR})",
    )
    args = parser.parse_args()
    run(db_path=args.db, migrations_dir=args.migrations)


if __name__ == "__main__":
    main()
