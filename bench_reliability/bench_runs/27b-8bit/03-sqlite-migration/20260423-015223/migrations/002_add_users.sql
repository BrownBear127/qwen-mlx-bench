-- 002_add_users.sql: Add users table and a foreign key to items
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE items ADD COLUMN owner_id INTEGER REFERENCES users(id);

CREATE INDEX IF NOT EXISTS idx_items_owner ON items(owner_id);
