#!/usr/bin/env python3
"""Minimal SQLite schema migration system (stdlib only).

Usage:
    python poc.py [--db DATABASE] [--migrations DIR]

Applies any pending migrations from the migrations/ directory in order.
Idempotent: running twice is safe.
"""

import argparse
import os
import re
import sqlite3
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_DB = "app.db"
DEFAULT_MIGRATIONS_DIR = "migrations"

# Regex to extract the numeric prefix and logical id from filenames like
# 001_init.sql -> id="001", name="init"
MIGRATION_FILENAME_RE = re.compile(r"^(\d+)_(.+)\.sql$")

# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------


def get_migration_files(migrations_dir: str) -> list[tuple[str, str]]:
    """Return sorted list of (id, filepath) for all .sql migrations."""
    if not os.path.isdir(migrations_dir):
        return []

    results: list[tuple[str, str]] = []
    for fname in os.listdir(migrations_dir):
        m = MIGRATION_FILENAME_RE.match(fname)
        if m:
            mid = m.group(1)
            path = os.path.join(migrations_dir, fname)
            results.append((mid, path))

    # Sort by numeric id so 001 < 002 < ... < 010
    results.sort(key=lambda t: t[0])
    return results


def ensure_migrations_table(conn: sqlite3.Connection) -> None:
    """Create schema_migrations table if it doesn't exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()


def get_applied_ids(conn: sqlite3.Connection) -> set[str]:
    """Return set of migration ids already applied."""
    cur = conn.execute("SELECT id FROM schema_migrations ORDER BY id")
    return {row[0] for row in cur}


def apply_migration(conn: sqlite3.Connection, mid: str, filepath: str) -> None:
    """Execute a single migration file and record it."""
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()

    # sqlite3.executescript handles multiple statements and ends with
    # an implicit commit, so we wrap in a transaction manually.
    conn.execute("BEGIN")
    try:
        conn.executescript(sql)
        conn.execute(f"INSERT INTO schema_migrations (id) VALUES (?)", (mid,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply pending SQLite schema migrations (stdlib only)."
    )
    parser.add_argument(
        "--db", default=DEFAULT_DB, help="SQLite database file (default: app.db)"
    )
    parser.add_argument(
        "--migrations",
        default=DEFAULT_MIGRATIONS_DIR,
        help="Directory containing .sql migration files (default: migrations/)",
    )
    args = parser.parse_args()

    # Discover migrations
    migration_files = get_migration_files(args.migrations)
    if not migration_files:
        print("No migration files found.")
        return

    # Open (or create) the database
    conn = sqlite3.connect(args.db)
    try:
        ensure_migrations_table(conn)
        applied = get_applied_ids(conn)

        # Determine pending migrations
        pending = [(mid, path) for mid, path in migration_files if mid not in applied]

        if not pending:
            print("no pending migrations")
            return

        # Apply each pending migration in order
        for mid, path in pending:
            print(f"Applying migration {mid} ({os.path.basename(path)})...")
            apply_migration(conn, mid, path)
            print(f"  -> applied successfully")

        print(f"Done. {len(pending)} migration(s) applied.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
