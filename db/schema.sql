-- db/schema.sql

-- One row per player. This is the "who."
CREATE TABLE players (
    id SERIAL PRIMARY KEY,           -- auto-incrementing unique ID (1, 2, 3, ...)
    name TEXT NOT NULL,              -- NOT NULL = this column can never be left empty
    team TEXT NOT NULL,
    position TEXT                    -- e.g. 'GK', 'DEF', 'MID', 'FWD' — nullable, we may not always know it
);

-- One row per match. This is the "when/where."
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    match_date DATE NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    home_score INT,
    away_score INT
);

-- One row per notable thing that happened to a player in a match.
-- This is the table that actually links players <-> matches.
CREATE TABLE match_events (
    id SERIAL PRIMARY KEY,
    match_id INT NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    player_id INT NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL CHECK (event_type IN ('goal', 'assist', 'yellow_card', 'red_card', 'rating',
    'shot', 'shot_on_target', 'tackle', 'foul',
    'substitution_in', 'substitution_out')),
    event_value NUMERIC,              -- e.g. 7.5 for a 'rating' event; NULL for goal/assist/card
    minute INT                        -- minute in the match this happened, nullable
);