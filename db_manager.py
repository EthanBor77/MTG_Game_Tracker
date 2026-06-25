import sqlite3
import os
from datetime import datetime

"""
Database manager for handling SQLite operations.
Currently supports:
1. Initializing the database schema from a .sql file.
2. Updating match history from a .sql file.
"""

DB_NAME = "mtg_stats.db"

def get_connection():
    """Returns a standard sqlite3 connection object."""
    return sqlite3.connect(DB_NAME)

def run_sql_script(db_name, sql_file):
    """Executes a .sql script against the specified SQLite database."""
    if not os.path.exists(sql_file):
        print(f"Error: The file '{sql_file}' was not found.")
        return

    try:
        # Connect to the database (it will be created if it doesn't exist)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        with open(sql_file, 'r') as f:
            sql_script = f.read()

        # executescript allows for multiple statements separated by semicolons
        cursor.executescript(sql_script)
        conn.commit()
        
        print(f"Successfully executed '{sql_file}' against '{db_name}'.")
    
    except sqlite3.Error as e:
        print(f"SQL Error: {e}")
    except Exception as e:
        print(f"General Error: {e}")
    finally:
        if conn:
            conn.close()

def create_database_backup():
    """Generates a SQL dump of the entire database for recovery."""
    backup_filename = f"backup_full_database_{datetime.now().strftime('%Y-%m-%d')}.sql"
    
    try:
        # Connect to your existing stats database
        with sqlite3.connect(DB_NAME) as conn:
            with open(backup_filename, 'w', encoding='utf-8') as f:
                # iterdump() creates the SQL commands to recreate the DB from scratch
                for line in conn.iterdump():
                    f.write(f'{line}\n')
                    
        print(f"✅ Success! Backup created: {backup_filename}")
        print(f"This file contains all players, 190+ decks, and 140 games in plain text.")
        
    except sqlite3.Error as e:
        print(f"❌ Backup failed: {e}")

def nuke_database():
    """Drops all tables from the database after multiple confirmations."""
    print("\n⚠️ WARNING: You are about to DELETE all data (Players, Decks, Games, Participants).")
    
    # First Check
    confirm1 = input("Are you absolutely sure? (y/n): ").lower()
    if confirm1 != 'y':
        print("Nuke cancelled.")
        return

    # Second Check (Manual Type)
    confirm2 = input("Type 'DELETE ALL' to confirm: ")
    if confirm2 != 'DELETE ALL':
        print("Confirmation failed. Nuke cancelled.")
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # 1. Turn off foreign keys to avoid 'Foreign Key Constraint' errors while dropping
        cursor.execute("PRAGMA foreign_keys = OFF;")

        # 2. Get the names of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            print(f"Dropped table: {table_name}")

        conn.commit()
        print("\n💥 Success: The database has been wiped clean.")

    except sqlite3.Error as e:
        print(f"❌ Error during nuke: {e}")
    finally:
        if conn:
            conn.close()

# One time alter function to add game_number column to games table
def migrate_game_numbers():
    """Adds game_number column and populates it for existing data."""
    conn = sqlite3.connect("mtg_stats.db")
    cursor = conn.cursor()

    try:
        # 1. Add the column to the games table
        print("Adding 'game_number' column...")
        cursor.execute("ALTER TABLE games ADD COLUMN game_number INTEGER;")
        conn.commit()
    except sqlite3.OperationalError:
        print("Column 'game_number' already exists. Skipping alter...")

    # 2. Fetch all games in the order they were created (by game_id)
    cursor.execute("SELECT game_id FROM games ORDER BY game_id ASC")
    games = cursor.fetchall()

    if not games:
        print("No existing games to number.")
        return

    # 3. Loop through and assign a sequential number
    print(f"Numbering {len(games)} existing games...")
    for index, (g_id,) in enumerate(games, start=1):
        cursor.execute("UPDATE games SET game_number = ? WHERE game_id = ?", (index, g_id))
    
    conn.commit()
    print("✅ Migration complete! All games now have a sequential Game Number.")
    conn.close()

def make_room_for_missing_games():
    """Shifts game numbers up to create a gap at 47-50."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # We start at 47 and move everything up by 4
        start_at = 47
        gap_size = 4
        
        print(f"Shifting games {start_at}+ up by {gap_size}...")
        
        cursor.execute("""
            UPDATE games 
            SET game_number = game_number + ? 
            WHERE game_number >= ?
        """, (gap_size, start_at))
        
        conn.commit()
        print("✅ Space created! Numbers 47, 48, 49, and 50 are now empty.")

def add_color_column():
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE decks ADD COLUMN deck_colors TEXT DEFAULT ''")
            conn.commit()
            print("✅ Successfully added deck_colors column to the decks table!")
        except sqlite3.OperationalError:
            print("Column 'deck_colors' already exists.")

def backfill_deck_colors():
    """Iterates through all decks missing color data and prompts for WUBRG input with undo/exit support."""
    print("\n=============================================")
    print("🔮 INTERACTIVE DECK COLOR BACKFILL TOOL")
    print("Commands: 'exit' to quit | 'undo' to revert last deck")
    print("=============================================\n")
    
    wubrg_order = {char: index for index, char in enumerate("WUBRG")}

    with sqlite3.connect("mtg_stats.db") as conn:
        cursor = conn.cursor()
        
        # Fetch all decks. If you already have some colored decks, 
        # this only targets unassigned ones (empty strings or NULLs)
        cursor.execute("""
            SELECT d.deck_id, d.deck_name, p.player_name 
            FROM decks d
            JOIN players p ON d.player_id = p.player_id
            WHERE d.deck_colors IS NULL OR d.deck_colors = ''
        """)
        decks = cursor.fetchall()
        
        if not decks:
            print("✅ All decks currently have color identities assigned!")
            return

        history = []  # Stack to track changes for the undo feature: (deck_id, old_val)
        idx = 0
        
        try:
            while idx < len(decks):
                deck_id, deck_name, player_name = decks[idx]
                
                print(f"[{idx + 1}/{len(decks)}] Deck: '{deck_name}' | Owner: {player_name}")
                user_input = input("Enter colors (e.g., 'wub', 'rg', 'c' for colorless): ").strip().lower()
                
                # --- Command handling ---
                if user_input == 'exit':
                    print("\nExiting tool. Saving progress made so far...")
                    break
                    
                if user_input == 'undo':
                    if not history:
                        print("❌ Nothing to undo!\n")
                        continue
                    # Pop the last modified deck state from our stack
                    idx, prev_deck_id, prev_name = history.pop()
                    print(f"↩️ Reverting changes for '{prev_name}'. Going back...\n")
                    continue

                # --- WUBRG Formatting Logic ---
                # Check for colorless decks explicitly
                if user_input == 'c':
                    clean_colors = ""
                else:
                    # Filter out garbage characters, keep uppercase WUBRG elements
                    upper_input = user_input.upper()
                    valid_chars = [c for c in upper_input if c in wubrg_order]
                    # Sort into strict standard WUBRG order
                    clean_colors = "".join(sorted(valid_chars, key=lambda c: wubrg_order[c]))

                # --- Update Memory Stack and Move Forward ---
                history.append((idx, deck_id, deck_name))
                
                # Stage the database update statement
                cursor.execute("UPDATE decks SET deck_colors = ? WHERE deck_id = ?", (clean_colors, deck_id))
                print(f"Saved: [{clean_colors if clean_colors else 'Colorless'}]\n")
                idx += 1
                
            # Commit the changes securely if the loop finishes or breaks via 'exit'
            conn.commit()
            print("💾 Progress successfully saved to the database!")
            
        except Exception as e:
            # Emergency fallback: if you close the terminal or an error occurs, save what you did
            conn.commit()
            print(f"\n⚠️ An unexpected error occurred: {e}")
            print("💾 Your partial progress has been safely saved.")

def main():
    db_name = "mtg_stats.db"
    
    print("\n--- MTG SQLite Database Manager ---")
    print("1. Initialize Database (Run createDatabase.sql)")
    print("2. Input Players and Their Decks (Run input_old_data.sql)")
    print("3. Check Games (Run checkGames.sql)")
    print("4. Create Database Backup")
    print("5. NUKE DATABASE (Reset Everything)")
    #print("6. Migrate Game Numbers")
    print("7. Make Room for Missing Games (Shift 47+ up by 4)")
    print("8. Add Color Column to Decks")
    print("9. Backfill Deck Colors (Interactive Tool)")
    print("10. Exit")

    choice = input("\nSelect an option (1-10): ")

    if choice == '1':
        run_sql_script(db_name, 'createDatabase.sql')
    elif choice == '2':
        run_sql_script(db_name, 'input_old_data.sql')
    elif choice == '3':
        run_sql_script(db_name, 'checkGames.sql')
    elif choice == '4':
        create_database_backup()
    elif choice == '5':
        nuke_database()
    elif choice == '6':
        #migrate_game_numbers()
        pass
    elif choice == '7':
        # make_room_for_missing_games()
        pass
    elif choice == '8':
        add_color_column()
    elif choice == '9':
        backfill_deck_colors()
    elif choice == '10':
        print("Exiting...")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()