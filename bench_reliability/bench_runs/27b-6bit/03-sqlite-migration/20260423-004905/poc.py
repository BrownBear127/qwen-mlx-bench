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
    """Return the set of migration ids that have already been applied."""
    cursor = conn.execute(f"SELECT id FROM {SCHEMA_TABLE}")
    return {row[0] for row in cursor.fetchall()}


def discover_migrations(migrations_dir: str = MIGRATIONS_DIR) -> list[str]:
    """
    Discover .sql migration files in the migrations directory.
    Returns a sorted list of migration ids (e.g. ['001', '002']).
    """
    if not os.path.isdir(migrations_dir):
        return []

    pattern = re.compile(r"^(\d+)_.*\.sql$")
    ids = []
    for filename in os.listdir(migrations_dir):
        match = pattern.match(filename)
        if match:
            ids.append(match.group(1))
    return sorted(ids)


def apply_migration(conn: sqlite3.Connection, migration_id: str, migrations_dir: str = MIGRATIONS_DIR) -> None:
    """Apply a single migration file."""
    # Find the corresponding .sql file
    pattern = re.compile(rf"^{re.escape(migration_id)}_(.+)\.sql$")
    sql_path = None
    for filename in os.listdir(migrations_dir):
        if pattern.match(filename):
            sql_path = os.path.join(migrations_dir, filename)
            break

    if sql_path is None:
        raise FileNotFoundError(f"Migration file for id '{migration_id}' not found in {migrations_dir}")

    with open(sql_path, "r") as f:
        sql = f.read()

    # Execute the migration inside a transaction
    conn.executescript(sql)

    # Record the migration as applied
    conn.execute(
        f"INSERT INTO {SCHEMA_TABLE} (id) VALUES (?)",
        (migration_id,),
    )
    conn.commit()
    print(f"  Applied migration {migration_id}")


def migrate(db_path: str = "app.db", migrations_dir: str = MIGRATIONS_DIR) -> None:
    """
    Run all pending migrations in order.
    Idempotent: running twice applies nothing on the second run.
    """
    conn = get_connection(db_path)
    try:
        ensure_migrations_table(conn)
        applied = get_applied_migrations(conn)
        all_migrations = discover_migrations(migrations_dir)
        pending = [mid for mid in all_migrations if mid not in applied]

        if not pending:
            print("No pending migrations.")
            return

        print(f"Applying {len(pending)} migration(s)...")
        for mid in pending:
            apply_migration(conn, mid, migrations_dir)
        print("Done.")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
