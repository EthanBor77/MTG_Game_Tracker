-- 1. Disable foreign keys so we can drop tables without errors
PRAGMA foreign_keys = OFF;

-- 2. Drop existing tables if they exist
DROP TABLE IF EXISTS participants;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS decks;
DROP TABLE IF EXISTS players;

-- 3. Re-enable foreign keys
PRAGMA foreign_keys = ON;

-- 4. Now create your new, corrected tables
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decks (
    deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_name TEXT NOT NULL,
    player_id INTEGER, -- This represents the "Owner"
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_date DATE,
    first_blood_turn INTEGER,
    end_turn INTEGER,
    win_condition TEXT
);

CREATE TABLE IF NOT EXISTS participants (
    participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER,
    game_id INTEGER,
    deck_id INTEGER,
    is_winner INTEGER, -- Use 1 for True, 0 for False
    turn_order INTEGER, -- Added this so you can track turn order stats!
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (game_id) REFERENCES games(game_id),
    FOREIGN KEY (deck_id) REFERENCES decks(deck_id)
);
