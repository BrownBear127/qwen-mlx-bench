-- Migration 002: Add users table extras
-- Adds profile and status columns to users

ALTER TABLE users ADD COLUMN display_name TEXT;
ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1;
