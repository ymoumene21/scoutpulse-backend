-- A small set of real players from teams already in our matches table.
INSERT INTO players (name, team, position) VALUES
    ('Erling Haaland', 'Man City', 'FWD'),
    ('Rodri', 'Man City', 'MID'),
    ('Bukayo Saka', 'Arsenal', 'MID'),
    ('Martin Odegaard', 'Arsenal', 'MID'),
    ('Kai Havertz', 'Arsenal', 'MID');

-- Events tied to real matches, looked up by team + date rather than
-- hardcoded IDs -- this is the pattern real ingestion code uses too,
-- since you rarely know a row's auto-generated ID in advance.
INSERT INTO match_events (match_id, player_id, event_type, event_value, minute)
VALUES
    ((SELECT id FROM matches WHERE home_team = 'Burnley' AND away_team = 'Man City' AND match_date = '2023-08-11'),
     (SELECT id FROM players WHERE name = 'Erling Haaland'), 'goal', NULL, 10),

    ((SELECT id FROM matches WHERE home_team = 'Burnley' AND away_team = 'Man City' AND match_date = '2023-08-11'),
     (SELECT id FROM players WHERE name = 'Erling Haaland'), 'goal', NULL, 55),

    ((SELECT id FROM matches WHERE home_team = 'Burnley' AND away_team = 'Man City' AND match_date = '2023-08-11'),
     (SELECT id FROM players WHERE name = 'Rodri'), 'goal', NULL, 70),

    ((SELECT id FROM matches WHERE home_team = 'Burnley' AND away_team = 'Man City' AND match_date = '2023-08-11'),
     (SELECT id FROM players WHERE name = 'Erling Haaland'), 'rating', 8.5, NULL),

    ((SELECT id FROM matches WHERE home_team = 'Arsenal' AND away_team = 'Nott''m Forest' AND match_date = '2023-08-12'),
     (SELECT id FROM players WHERE name = 'Bukayo Saka'), 'goal', NULL, 25),

    ((SELECT id FROM matches WHERE home_team = 'Arsenal' AND away_team = 'Nott''m Forest' AND match_date = '2023-08-12'),
     (SELECT id FROM players WHERE name = 'Kai Havertz'), 'assist', NULL, 25),

    ((SELECT id FROM matches WHERE home_team = 'Arsenal' AND away_team = 'Nott''m Forest' AND match_date = '2023-08-12'),
     (SELECT id FROM players WHERE name = 'Martin Odegaard'), 'goal', NULL, 60),

    ((SELECT id FROM matches WHERE home_team = 'Arsenal' AND away_team = 'Nott''m Forest' AND match_date = '2023-08-12'),
     (SELECT id FROM players WHERE name = 'Bukayo Saka'), 'rating', 8.0, NULL);