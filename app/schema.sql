CREATE TABLE IF NOT EXISTS "user" (
    id             SERIAL PRIMARY KEY,
    username       TEXT UNIQUE NOT NULL,
    password_hash  TEXT,
    email          TEXT,
    fullname       TEXT
);
