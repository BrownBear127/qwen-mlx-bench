#!/usr/bin/env python3
"""
Minimal SQLite schema migration POC using only Python stdlib.

Usage:
    python poc.py

Migrations are .sql files in the migrations/ directory, named like:
    001_init.sql
    002_add_users.sql

The system tracks applied migrations in a `schema_migrations` table
and applies any pending ones in order. Running it twice is idempotent.
"""

import os
import re
import sqlite3
import sys


DB_PATH = os.environ.get("MIGRATE_DB", "app.db")
MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")

# Regex to extract the numeric prefix from migration filenames
MIGRATION_RE = re.compile(r"^(\d+)_")


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_migrations_table(conn: sqlite3.Connection) -> None:
    """Create the schema_migrations tracking table if it doesn't exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration_id TEXT NOT NULL UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def get_applied_migrations(conn: sqlite3.Connection) -> set[str]:
    """Return the set of migration IDs that have already been applied."""
    cursor = conn.execute("SELECT migration_id FROM schema_migrations")
    return {row[0] for row in cursor.fetchall()}


def discover_migrations(migrations_dir: str) -> list[tuple[str, str]]:
    """
    Discover migration files in the migrations directory.

    Returns a sorted list of (migration_id, file_path) tuples.
    Only files matching the expected naming pattern are included.
    """
    migrations = []
    if not os.path.isdir(migrations_dir):
        print(f"Warning: migrations directory not found: {migrations_dir}")
        return migrations

    for filename in os.listdir(migrations_dir):
        match = MIGRATION_RE.match(filename)
        if match:
            migration_id = match.group(1)
            file_path = os.path.join(migrations_dir, filename)
            migrations.append((migration_id, file_path))

    # Sort by the numeric prefix to ensure correct order
    migrations.sort(key=lambda x: int(x[0]))
    return migrations


def read_migration_sql(file_path: str) -> str:
    """Read and return the SQL content from a migration file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def apply_migration(conn: sqlite3.Connection, migration_id: str, sql: str) -> None:
    """Apply a single migration and record it in schema_migrations."""
    # Split on semicolons and execute each statement
    statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]
    for statement in statements:
        # Skip comments-only blocks
        lines = statement.split("\n")
        non_comment_lines = [
            l for l in lines if not l.strip().startswith("--")
        ]
        if not non_comment_lines:
            continue
        conn.execute(statement)

    # Record the migration as applied
    conn.execute(
        "INSERT INTO schema_migrations (migration_id) VALUES (?)",
        (migration_id,),
    )
    conn.commit()
    print(f"  Applied migration: {migration_id}")


def migrate(db_path: str, migrations_dir: str) -> None:
    """Run all pending migrations in order."""
    conn = get_connection(db_path)
    try:
        ensure_migrations_table(conn)
        applied = get_applied_migrations(conn)
        migrations = discover_migrations(migrations_dir)

        pending = [
            (mid, fpath) for mid, fpath in migrations if mid not in applied
        ]

        if not pending:
            print("no pending migrations")
            return

        print(f"Found {len(pending)} pending migration(s).")
        for migration_id, file_path in pending:
            sql = read_migration_sql(file_path)
            apply_migration(conn, migration_id, sql)

        print(f"Migration complete. {len(pending)} migration(s) applied.")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate(DB_PATH, MIGRATIONS_DIR)
