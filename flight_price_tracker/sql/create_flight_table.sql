-- DROP TABLE IF EXISTS meals;
-- CREATE TABLE meals (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     meal TEXT NOT NULL UNIQUE,
--     cuisine TEXT NOT NULL,
--     price REAL NOT NULL,
--     difficulty TEXT CHECK(difficulty IN ('HIGH', 'MED', 'LOW')),
--     battles INTEGER DEFAULT 0,
--     wins INTEGER DEFAULT 0,
--     deleted BOOLEAN DEFAULT FALSE
-- );

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    salt BLOB NOT NULL,
    hashed_password BLOB NOT NULL
);
