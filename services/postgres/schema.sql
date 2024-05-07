SET max_parallel_maintenance_workers = 60;
SET max_parallel_workers = 60;
SET maintenance_work_mem TO '6GB';


-- Drop tables if they already exist
DROP TABLE IF EXISTS user_to_events;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS users;

-- Create the users table
CREATE TABLE users (
    id_users BIGINT SERIAL PRIMARY KEY,
    email TEXT,
    password TEXT
);

-- Create the events table
CREATE TABLE events (
    id_events BIGINT SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    location TEXT,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    organization TEXT,
    contact_information TEXT
);

-- Create the user_to_events table
CREATE TABLE user_to_events (
    id_favorites BIGINT SERIAL PRIMARY KEY,
    user_id BIGINT,
    event_id BIGINT,
    FOREIGN KEY (user_id) REFERENCES users (id_users) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events (id_events) ON DELETE CASCADE
);

-- Indexes for faster search
CREATE INDEX idx_users_email ON users USING btree (email);
CREATE INDEX idx_events_name ON events USING btree (name);

