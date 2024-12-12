CREATE DATABASE villancicos_db;

\c villancicos_db;

CREATE TABLE villancicos (
    id SERIAL PRIMARY KEY,
    prompt TEXT NOT NULL,
    letra TEXT NOT NULL,
    image_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
