"""Minimal SQLite schema migration system using only Python stdlib."""

import glob
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.db")
MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")


def ensure_migrations_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )


def get_applied(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT id FROM schema_migrations").fetchall()
    return {row[0] for row in rows}


def discover_migrations() -> list[tuple[str, str]]:
    """Return sorted list of (migration_id, filepath) pairs."""
    files = sorted(glob.glob(os.path.join(MIGRATIONS_DIR, "*.sql")))
    result = []
    for path in files:
        migration_id = os.path.basename(path)
        result.append((migration_id, path))
    return result


def apply_migration(conn: sqlite3.Connection, migration_id: str, path: str) -> None:
    sql = open(path).read()
    conn.executescript(sql)
    conn.execute("INSERT INTO schema_migrations (id) VALUES (?)", (migration_id,))
    conn.commit()
    print(f"  applied: {migration_id}")


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        ensure_migrations_table(conn)
        conn.commit()

        applied = get_applied(conn)
        pending = [
            (mid, path)
            for mid, path in discover_migrations()
            if mid not in applied
        ]

        if not pending:
            print("no pending migrations")
            return

        print(f"applying {len(pending)} migration(s)...")
        for migration_id, path in pending:
            apply_migration(conn, migration_id, path)
        print("done.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
