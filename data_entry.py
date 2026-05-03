import sqlite3
import os

"""
Data entry script for logging MTG Commander games into the SQLite database.
Features:
1. Add Players
2. Add Decks (linked to Players)
3. Log Games with validation for winners and turn order
4. View recent game history in a readable format
"""

DB_NAME = "mtg_stats.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def find_item(table, column, search_term):
    """Helper to find an ID by searching for a name string."""
    with get_connection() as conn:
        cursor = conn.cursor()
        # Uses SQL LIKE for flexible searching among your 190+ decks
        query = f"SELECT {table[:-1]}_id, {column} FROM {table} WHERE {column} LIKE ?"
        cursor.execute(query, (f'%{search_term}%',))
        results = cursor.fetchall()
        
        if not results:
            print(f"No {table} found matching '{search_term}'.")
            return None
        
        if len(results) == 1:
            return results[0][0] # Auto-selects if only one match
        
        print(f"\nMultiple {table} found. Please select an ID:")
        for r in results:
            print(f"{r[0]}: {r[1]}")
        choice = input(f"Enter ID (or press Enter to search again): ")
        return int(choice) if choice.isdigit() else None

def add_player():
    name = input("\nEnter player name: ").strip()
    if not name: return
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO players (player_name) VALUES (?)", (name,))
            print(f"Player '{name}' added.")
        except sqlite3.IntegrityError:
            print("Error: That player already exists.")

def add_deck():
    owner_search = input("\nSearch for the Owner's name: ")
    p_id = find_item("players", "player_name", owner_search)
    
    if p_id:
        deck_name = input("Enter Deck Name: ").strip()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO decks (deck_name, player_id) VALUES (?, ?)", (deck_name, p_id))
            print(f"Deck '{deck_name}' registered.")

def rename_deck():
    """Finds an existing deck and updates its name."""
    print("\n--- Rename an Existing Deck ---")
    deck_search = input("Search for the deck you want to rename: ")
    d_id = find_item("decks", "deck_name", deck_search)
    
    if d_id:
        # Fetch current name to show the user what they are changing
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deck_name FROM decks WHERE deck_id = ?", (d_id,))
            old_name = cursor.fetchone()[0]
            
            print(f"Current Name: {old_name}")
            new_name = input("Enter the new name for this deck: ").strip()
            
            if not new_name:
                print("Rename cancelled. Name cannot be empty.")
                return

            try:
                cursor.execute("UPDATE decks SET deck_name = ? WHERE deck_id = ?", (new_name, d_id))
                print(f"Success! '{old_name}' has been renamed to '{new_name}'.")
            except sqlite3.Error as e:
                print(f"An error occurred: {e}")

def log_game():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Game Details
        date = input("\nDate (YYYY-MM-DD): ")
        fb_turn = input("First Blood Turn: ")
        end_turn = input("End Turn: ")
        win_con = input("Win Condition: ")

        # 2. Collect Participant Data Locally
        participants_data = []
        winners_count = 0

        for i in range(1, 5):
            print(f"\n--- Logging Player {i} of 4 ---")
            p_id = None
            while not p_id:
                p_id = find_item("players", "player_name", input(f"Search Player {i}: "))

            d_id = None
            while not d_id:
                d_id = find_item("decks", "deck_name", input(f"Search Deck {i}: "))

            is_winner = input("Did they win? (y/n): ").lower() == 'y'
            winner_val = 1 if is_winner else 0
            if is_winner: winners_count += 1
            
            participants_data.append((p_id, d_id, winner_val, i))

        # 3. Validation Logic (Allowing 0 or 1 winners)
        if winners_count > 1:
            print(f"\n!!! ERROR: Found {winners_count} winners. Only 1 (or 0 for draws) allowed.")
            return 
        if winners_count == 0:
            if input("0 winners entered. Was this a draw? (y/n): ").lower() != 'y':
                return

        # 4. Commit to Database
        cursor.execute("INSERT INTO games (game_date, first_blood_turn, end_turn, win_condition) VALUES (?, ?, ?, ?)", 
                       (date, fb_turn, end_turn, win_con))
        game_id = cursor.lastrowid

        for p_id, d_id, win, turn in participants_data:
            cursor.execute("INSERT INTO participants (player_id, game_id, deck_id, is_winner, turn_order) VALUES (?, ?, ?, ?, ?)", 
                           (p_id, game_id, d_id, win, turn))
        print("\nMatch successfully logged!")

def view_recent_games():
    """Displays the last 5 games in a readable format."""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT g.game_id, g.game_date, p.player_name, d.deck_name, part.is_winner, g.win_condition
            FROM games g
            JOIN participants part ON g.game_id = part.game_id
            JOIN players p ON part.player_id = p.player_id
            JOIN decks d ON part.deck_id = d.deck_id
            ORDER BY g.game_id DESC, part.turn_order ASC
            LIMIT 20
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print("\nNo games found in the database.")
            return

        print("\n--- Recent Game History ---")
        current_id = None
        for r in rows:
            g_id, date, p_name, d_name, is_win, win_con = r
            if g_id != current_id:
                print(f"\nGame #{g_id} | Date: {date} | Method: {win_con}")
                current_id = g_id
            
            status = "[WINNER]" if is_win else "        "
            print(f"  {status} {p_name.ljust(10)} | {d_name}")

def export_full_log():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.game_id, g.game_date, p.player_name, d.deck_name, part.is_winner, g.win_condition
            FROM games g
            JOIN participants part ON g.game_id = part.game_id
            JOIN players p ON part.player_id = p.player_id
            JOIN decks d ON part.deck_id = d.deck_id
            ORDER BY g.game_id ASC, part.turn_order ASC
        """)
        rows = cursor.fetchall()
        
        if not rows:
            print("\nNo games found to display.")
            return

        print(f"\n{'ID':<4} | {'Date':<12} | {'Player':<12} | {'Result':<8} | {'Deck'}")
        print("=" * 80)
        
        current_game_id = None
        for r in rows:
            g_id, date, p_name, d_name, is_win, win_con = r
            
            # Print a newline and a divider when we hit a new game
            if current_game_id is not None and g_id != current_game_id:
                print("-" * 80) 
            
            current_game_id = g_id
            res = "WINNER" if is_win else "---"
            
            # Formatting the output
            print(f"{g_id:<4} | {date:<12} | {p_name:<12} | {res:<8} | {d_name}")

        print("=" * 80)
        print(f"Total rows displayed: {len(rows)}")

def main():
    while True:
        print("\n=== MTG STAT TRACKER ===")
        print("1. Add Player")
        print("2. Add Deck")
        print("3. Rename Deck")
        print("4. Log New Game")
        print("5. View Recent Games")
        print("6. Check ALL Games")
        print("7. Exit")
        
        choice = input("\nSelect an option: ")
        if choice == '1': add_player()
        elif choice == '2': add_deck()
        elif choice == '3': rename_deck()
        elif choice == '4': log_game()
        elif choice == '5': view_recent_games()
        elif choice == '6': export_full_log()
        elif choice == '7': break

if __name__ == "__main__":
    main()