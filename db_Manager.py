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

def main():
    db_name = "mtg_stats.db"
    
    print("--- MTG SQLite Database Manager ---")
    print("1. Initialize Database (Run createDatabase.sql)")
    print("2. Input Players and Their Decks (Run input_old_data.sql)")
    print("3. Check Games (Run checkGames.sql)")
    print("4. Create Database Backup")
    print("5. Exit")
    
    choice = input("\nSelect an option (1-5): ")

    if choice == '1':
        run_sql_script(db_name, 'createDatabase.sql')
    elif choice == '2':
        #print("That option is currently disabled")
        run_sql_script(db_name, 'input_old_data.sql')
    elif choice == '3':
        run_sql_script(db_name, 'checkGames.sql')
    elif choice == '4':
        create_database_backup()
    elif choice == '5':
        print("Exiting...")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()