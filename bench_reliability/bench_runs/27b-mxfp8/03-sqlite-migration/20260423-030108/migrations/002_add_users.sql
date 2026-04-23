-- 002_add_users.sql
-- Add a users table and a tags table for post categorisation.

CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT    NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role       TEXT    DEFAULT 'reader',
    created_at TEXT    DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS tags (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS post_tags (
    post_id  INTEGER NOT NULL,
    tag_id   INTEGER NOT NULL,
    PRIMARY KEY (post_id, tag_id),
    FOREIGN KEY (post_id)  REFERENCES posts(id),
    FOREIGN KEY (tag_id)   REFERENCES tags(id)
);
