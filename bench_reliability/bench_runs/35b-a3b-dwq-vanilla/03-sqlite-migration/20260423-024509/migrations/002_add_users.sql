-- 002_add_users.sql: Add profile fields to users table

ALTER TABLE users ADD COLUMN display_name TEXT DEFAULT '';
ALTER TABLE users ADD COLUMN bio TEXT DEFAULT '';
