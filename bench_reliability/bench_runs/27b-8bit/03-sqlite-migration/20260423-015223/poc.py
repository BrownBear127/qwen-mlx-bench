#!/usr/bin/env python3
"""Minimal SQLite schema migration system using only Python stdlib."""

import os
import re
import sqlite3


MIGRATIONS_DIR = "migrations"
SCHEMA_TABLE = "schema_migrations"


def get_connection(db_path: str = "app.db") -> sqlite3.Connection:
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def ensure_migrations_table(conn: sqlite3.Connection) -> None:
    """Create the schema_migrations tracking table if it doesn't exist."""
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA_TABLE} (
            id TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def get_applied_migrations(conn: sqlite3.Connection) -> set[str]:
    """Return the set of migration IDs that have already been applied."""
    cursor = conn.execute(f"SELECT id FROM {SCHEMA_TABLE}")
    return {row[0] for row in cursor.fetchall()}


def discover_migrations(migrations_dir: str) -> list[tuple[str, str]]:
    """
    Discover .sql migration files in the given directory.

    Returns a sorted list of (migration_id, filepath) tuples.
    Files must match the pattern: <digits>_<name>.sql
    """
    pattern = re.compile(r"^(\d+)_(.+)\.sql$")
    migrations = []

    if not os.path.isdir(migrations_dir):
        return migrations

    for filename in os.listdir(migrations_dir):
        match = pattern.match(filename)
        if match:
            migration_id = match.group(1)
            filepath = os.path.join(migrations_dir, filename)
            migrations.append((migration_id, filepath))

    # Sort by migration ID (numeric prefix)
    migrations.sort(key=lambda x: x[0])
    return migrations


def apply_migration(conn: sqlite3.Connection, migration_id: str, filepath: str) -> None:
    """Apply a single migration file within a transaction."""
    with open(filepath, "r") as f:
        sql = f.read()

    print(f"  Applying migration {migration_id}: {filepath}")

    # Execute all statements in the file
    conn.executescript(sql)

    # Record the migration as applied
    conn.execute(
        f"INSERT INTO {SCHEMA_TABLE} (id) VALUES (?)",
        (migration_id,),
    )
    conn.commit()


def run_migrations(db_path: str = "app.db", migrations_dir: str = MIGRATIONS_DIR) -> None:
    """Apply any pending migrations in order."""
    conn = get_connection(db_path)
    ensure_migrations_table(conn)

    applied = get_applied_migrations(conn)
    all_migrations = discover_migrations(migrations_dir)

    pending = [
        (mid, fpath)
        for mid, fpath in all_migrations
        if mid not in applied
    ]

    if not pending:
        print("no pending migrations")
        conn.close()
        return

    print(f"Found {len(pending)} pending migration(s):")
    for migration_id, filepath in pending:
        apply_migration(conn, migration_id, filepath)

    print(f"Successfully applied {len(pending)} migration(s).")
    conn.close()


if __name__ == "__main__":
    run_migrations()
