from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List, Set


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "demo.db"
MIGRATIONS_DIR = ROOT / "migrations"


def ensure_migration_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            migration_id TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def discover_migrations(directory: Path) -> List[Path]:
    if not directory.exists():
        raise FileNotFoundError(f"missing migrations directory: {directory}")
    return sorted(path for path in directory.iterdir() if path.suffix == ".sql")


def load_applied_migration_ids(connection: sqlite3.Connection) -> Set[str]:
    rows = connection.execute(
        "SELECT migration_id FROM schema_migrations ORDER BY migration_id"
    ).fetchall()
    return {row[0] for row in rows}


def split_sql_statements(script: str) -> Iterable[str]:
    buffer: List[str] = []

    for line in script.splitlines(keepends=True):
        buffer.append(line)
        candidate = "".join(buffer)
        if candidate.strip() and sqlite3.complete_statement(candidate):
            yield candidate.strip()
            buffer.clear()

    tail = "".join(buffer).strip()
    if tail:
        raise ValueError("migration contains an incomplete SQL statement")


def apply_migration(
    connection: sqlite3.Connection, migration_id: str, migration_path: Path
) -> None:
    statements = list(split_sql_statements(migration_path.read_text(encoding="utf-8")))
    if not statements:
        raise ValueError(f"migration is empty: {migration_path.name}")

    with connection:
        for statement in statements:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO schema_migrations (migration_id) VALUES (?)", (migration_id,)
        )


def main() -> int:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        ensure_migration_table(connection)

        migrations = discover_migrations(MIGRATIONS_DIR)
        applied_ids = load_applied_migration_ids(connection)
        pending = [path for path in migrations if path.stem not in applied_ids]

        if not pending:
            print("no pending migrations")
            return 0

        for path in pending:
            print(f"applying {path.name}")
            apply_migration(connection, path.stem, path)

    print(f"applied {len(pending)} migration(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
