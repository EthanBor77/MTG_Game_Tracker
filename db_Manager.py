import sqlite3
import os

"""
Database manager for handling SQLite operations.
Currently supports:
1. Initializing the database schema from a .sql file.
2. Updating match history from a .sql file.
"""

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

def main():
    db_name = "mtg_stats.db"
    
    print("--- MTG SQLite Database Manager ---")
    print("1. Initialize Database (Run createDatabase.sql)")
    print("2. Update Match History (Run update_games.sql)")
    print("3. Check Games (Run checkGames.sql)")
    print("4. Exit")
    
    choice = input("\nSelect an option (1-4): ")

    if choice == '1':
        run_sql_script(db_name, 'createDatabase.sql')
    elif choice == '2':
        print("That option is currently disabled")
        #run_sql_script(db_name, 'update_games.sql')
    elif choice == '3':
        run_sql_script(db_name, 'checkGames.sql')
    elif choice == '4':
        print("Exiting...")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()