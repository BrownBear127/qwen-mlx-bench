-- 002_add_users.sql
-- Add a users table and a many-to-many link between users and projects.

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS user_projects (
    user_id INTEGER NOT NULL REFERENCES users(id),
    project_id INTEGER NOT NULL REFERENCES projects(id),
    PRIMARY KEY (user_id, project_id)
);
