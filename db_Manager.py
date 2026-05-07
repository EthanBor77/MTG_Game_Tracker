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
    print("8. Exit")

    choice = input("\nSelect an option (1-8): ")

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
        print("Exiting...")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()