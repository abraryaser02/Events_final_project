SET max_parallel_maintenance_workers = 60;
SET max_parallel_workers = 60;
SET maintenance_work_mem TO '6GB';

-- Ensure the required extensions are installed
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS RUM;

-- Drop tables if they already exist
DROP TABLE IF EXISTS user_to_events;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS fts_word;


-- Create the users table
CREATE TABLE users (
    id_users BIGSERIAL PRIMARY KEY,
    email TEXT,
    password TEXT
);

-- Create the events table
CREATE TABLE events (
    id_events BIGSERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    location TEXT,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    organization TEXT,
    contact_information TEXT,
    registration_link TEXT,
    keywords TEXT[],
    tsv tsvector
);

-- Create the user_to_events table
CREATE TABLE user_to_events (
    id_favorites BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    event_id BIGINT,
    FOREIGN KEY (user_id) REFERENCES users (id_users) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events (id_events) ON DELETE CASCADE
);

CREATE TABLE fts_word (
    word TEXT PRIMARY KEY
);

COPY fts_word(word) FROM '/docker-entrypoint-initdb.d/words_alpha.txt' WITH (FORMAT text);

-- Indexes for faster search
CREATE INDEX idx_users_email ON users USING btree (email);
CREATE INDEX idx_events_name ON events USING rum (name);
CREATE INDEX idx_events_description ON events USING rum (description);
CREATE INDEX idx_events_start_time ON events USING btree (start_time);

-- Full-text search index
CREATE INDEX idx_events_fti ON events USING rum (tsv);
CREATE INDEX idx_fts_word ON fts_word USING rum (word);

-- Trigger to update tsvector
CREATE OR REPLACE FUNCTION update_tsvector() RETURNS trigger AS $$
BEGIN
    NEW.tsv := to_tsvector('english', NEW.name || ' ' || NEW.description);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_tsvector
BEFORE INSERT OR UPDATE ON events
FOR EACH ROW EXECUTE FUNCTION update_tsvector();

CREATE OR REPLACE FUNCTION get_spelling_suggestions(query TEXT)
RETURNS TABLE(suggestion TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT dictionary.word
    FROM (
        SELECT unnest(string_to_array(query, ' ')) AS my_word
    ) AS words
    JOIN fts_word AS dictionary
    ON similarity(words.my_word, dictionary.word) > 0.4
    ORDER BY similarity(words.my_word, dictionary.word) DESC
    LIMIT 5;
END;
$$ LANGUAGE plpgsql;


COMMIT;
