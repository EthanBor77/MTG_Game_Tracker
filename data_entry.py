import sqlite3
import os

"""
Data entry script for logging MTG Commander games into the SQLite database.
Features:
1. Add Players and Decks (with search-to-select).
2. Log Games with dynamic player counts (3-6+ players).
3. View Game History with dual-ID display (Display # vs Database ID).
"""

DB_NAME = "mtg_stats.db"

def get_connection():
    """Returns a standard sqlite3 connection object."""
    return sqlite3.connect(DB_NAME)

def find_item(table, column, search_term):
    """Helper to find an ID by searching for a name string with SQL LIKE."""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = f"SELECT {table[:-1]}_id, {column} FROM {table} WHERE {column} LIKE ?"
        cursor.execute(query, (f'%{search_term}%',))
        results = cursor.fetchall()
        
        if not results:
            print(f"No {table} found matching '{search_term}'.")
            return None
        
        if len(results) == 1:
            return results[0][0] # Auto-select if unique
        
        print(f"\nMultiple {table} found. Please select an ID:")
        for r in results:
            print(f"{r[0]}: {r[1]}")
        choice = input(f"Enter ID (or press Enter to search again): ")
        return int(choice) if choice.isdigit() else None

def add_player():
    """Inserts a new player into the players table."""
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
    """Links a new deck name and color identity to an existing player ID."""
    owner_search = input("\nSearch for the Owner's name: ")
    p_id = find_item("players", "player_name", owner_search)
    
    if p_id:
        deck_name = input("Enter Deck Name: ").strip()
        
        # Capture raw color string (e.g., "rg" or "gru")
        raw_colors = input("Enter Deck Colors (WUBRG combo, e.g., 'GUB'): ").strip()
        # Clean and enforce WUBRG order
        clean_colors = format_wubrg(raw_colors)
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO decks (deck_name, player_id, deck_colors) 
                VALUES (?, ?, ?)
            """, (deck_name, p_id, clean_colors))
            print(f"Deck '{deck_name}' [{clean_colors}] registered successfully.")

def format_wubrg(color_string):
    """Sorts a string of colors into strict WUBRG order."""
    wubrg_order = {char: index for index, char in enumerate("WUBRG")}
    # Sort based on the character's position in WUBRG string
    sorted_colors = sorted(color_string.upper(), key=lambda char: wubrg_order.get(char, 99))
    return "".join(sorted_colors)

def rename_deck():
    """Finds an existing deck and updates its name string."""
    print("\n--- Rename an Existing Deck ---")
    deck_search = input("Search for the deck you want to rename: ")
    d_id = find_item("decks", "deck_name", deck_search)
    
    if d_id:
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
                print(f"Success! '{old_name}' renamed to '{new_name}'.")
            except sqlite3.Error as e:
                print(f"An error occurred: {e}")

def log_game():
    """Main function to log a match, its participants, and its result."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Game Details
        date = input("\nDate (YYYY-MM-DD): ")
        num_players_input = input("How many players (3-6+): ")
        if not num_players_input.isdigit(): return
        num_players = int(num_players_input)

        fb_turn = input("First Blood Turn: ")
        end_turn = input("End Turn: ")
        win_con = input("Win Condition: ")

        # 2. Local Participant Tracking
        participants_data = []
        winners_count = 0

        for i in range(1, num_players + 1):
            print(f"\n--- Logging Player {i} of {num_players} ---")
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

        # 3. Validation Logic (Prevent multiple winners)
        if winners_count > 1:
            print(f"\n!!! ERROR: Found {winners_count} winners. Only 1 allowed.")
            return 
        if winners_count == 0:
            if input("0 winners. Was this a draw? (y/n): ").lower() != 'y': return

        # 4. Database Insertion
        # Calculate the next display number (not the primary key)
        cursor.execute("SELECT MAX(game_number) FROM games")
        max_row = cursor.fetchone()[0]
        next_num = (max_row + 1) if max_row is not None else 1

        cursor.execute("""
            INSERT INTO games (game_number, game_date, first_blood_turn, end_turn, win_condition) 
            VALUES (?, ?, ?, ?, ?)
        """, (next_num, date, fb_turn, end_turn, win_con))
        
        game_id = cursor.lastrowid # Hidden Primary Key for foreign key links

        for p_id, d_id, win, turn in participants_data:
            cursor.execute("""
                INSERT INTO participants (player_id, game_id, deck_id, is_winner, turn_order) 
                VALUES (?, ?, ?, ?, ?)
            """, (p_id, game_id, d_id, win, turn))
        
        conn.commit()
        print(f"\nMatch successfully logged as Game #{next_num} (Internal ID: {game_id})!")

        # 5. Instant Summary View
        print("\n--- Summary of Logged Game ---")
        cursor.execute("""
            SELECT g.game_number, g.game_id, p.player_name, d.deck_name, part.is_winner
            FROM games g
            JOIN participants part ON g.game_id = part.game_id
            JOIN players p ON part.player_id = p.player_id
            JOIN decks d ON part.deck_id = d.deck_id
            WHERE g.game_id = ?
            ORDER BY part.turn_order ASC
        """, (game_id,))
        rows = cursor.fetchall()

        if rows:
            print(f"{'Game #':<8} | {'ID':<4} | {'Player':<12} | {'Result':<8} | {'Deck'}")
            print("-" * 80)
            for r in rows:
                g_num, g_internal_id, p_name, d_name, is_win = r
                res = "WINNER" if is_win else "---"
                print(f"{g_num:<8} | {g_internal_id:<4} | {p_name:<12} | {res:<8} | {d_name}")
            print("-" * 80)

def view_recent_games():
    """Displays the most recent games using the detailed header format."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # We fetch the last 20 rows (approx 4-5 games depending on pod size)
        query = """
            SELECT g.game_number, g.game_id, g.game_date, g.first_blood_turn, g.end_turn, g.win_condition,
                   p.player_name, d.deck_name, part.is_winner
            FROM games g
            JOIN participants part ON g.game_id = part.game_id
            JOIN players p ON part.player_id = p.player_id
            JOIN decks d ON part.deck_id = d.deck_id
            WHERE g.game_id IN (
                SELECT game_id FROM games ORDER BY game_number DESC LIMIT 5
            )
            ORDER BY g.game_number DESC, part.turn_order ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print("\nNo games found in the database.")
            return

        print("\n" + "=" * 95)
        print(f"{'RECENT META HISTORY':^95}")
        print("=" * 95)
        
        current_num = None
        for r in rows:
            g_num, g_id, date, fb_turn, end_turn, win_con, p_name, d_name, is_win = r
            
            if g_num != current_num:
                if current_num is not None:
                    print("-" * 95) 
                
                print(f"\n[ GAME #{g_num} ]  Date: {date}  |  FB Turn: {fb_turn}  |  End Turn: {end_turn}  |  Win Con: {win_con}")
                # print(f"{'-'*15}")
                print(f"{'ID':<4} | {'Player':<15} | {'Result':<10} | {'Deck'}\n")
                current_num = g_num
            
            res = "WINNER" if is_win else "---"
            print(f"{g_id:<4} | {p_name:<15} | {res:<10} | {d_name}")

        print("=" * 95)

def export_full_log():
    """Prints every game with a header for game-wide stats followed by participant details."""
    with get_connection() as conn:
        cursor = conn.cursor()
        # Fetching all relevant columns including turn data and win condition
        cursor.execute("""
            SELECT g.game_number, g.game_id, g.game_date, g.first_blood_turn, g.end_turn, g.win_condition,
                   p.player_name, d.deck_name, part.is_winner
            FROM games g
            JOIN participants part ON g.game_id = part.game_id
            JOIN players p ON part.player_id = p.player_id
            JOIN decks d ON part.deck_id = d.deck_id
            ORDER BY g.game_number ASC, part.turn_order ASC
        """)
        rows = cursor.fetchall()
        
        if not rows:
            print("\nNo games found to display.")
            return

        print("\n" + "=" * 95)
        print("FULL MTG META HISTORY LOG")
        print("=" * 95)
        
        current_num = None
        for r in rows:
            g_num, g_id, date, fb_turn, end_turn, win_con, p_name, d_name, is_win = r
            
            # If we hit a new game, print the Game Header
            if g_num != current_num:
                if current_num is not None:
                    print("-" * 95) # Divider between games
                
                print(f"\n[ GAME #{g_num} ]  Date: {date}  |  FB Turn: {fb_turn}  |  End Turn: {end_turn}  |  Win Con: {win_con}")
                # print(f"{'-'*15}")
                print(f"{'ID':<4} | {'Player':<15} | {'Result':<10} | {'Deck'}\n")
                current_num = g_num
            
            # Print the individual player rows for that game
            res = "WINNER" if is_win else "---"
            print(f"{g_id:<4} | {p_name:<15} | {res:<10} | {d_name}")

        print("=" * 95)
        print(f"Log Export Complete.")

def remove_game():
    """Removes a game and its participants using the internal Database ID."""
    print("\n--- Remove a Game Entry ---")
    game_id_str = input("Enter the internal Game ID (Check Option 5/6 for ID): ")
    if not game_id_str.isdigit(): return
    game_id = int(game_id_str)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT game_date, win_condition, game_number FROM games WHERE game_id = ?", (game_id,))
        game = cursor.fetchone()

        if not game:
            print(f"Error: ID {game_id} not found.")
            return

        print(f"\nTarget: Game #{game[2]} (ID: {game_id}) | Date: {game[0]}")
        if input(f"Confirm delete Game #{game[2]}? (y/n): ").lower() == 'y':
            try:
                # Remove dependencies first
                cursor.execute("DELETE FROM participants WHERE game_id = ?", (game_id,))
                cursor.execute("DELETE FROM games WHERE game_id = ?", (game_id,))
                print(f"Success: Game #{game[2]} removed.")
            except sqlite3.Error as e:
                print(f"An error occurred: {e}")
        else:
            print("Deletion cancelled.")

def main():
    """Main menu loop for the script."""
    while True:
        print("\n=== MTG STAT TRACKER ===")
        print("1. Add Player\n2. Add Deck\n3. Rename Deck\n4. Log New Game\n5. View Recent\n6. Check ALL\n7. Remove Game\n8. Exit")
        choice = input("\nSelect: ")
        if choice == '1': add_player()
        elif choice == '2': add_deck()
        elif choice == '3': rename_deck()
        elif choice == '4': log_game()
        elif choice == '5': view_recent_games()
        elif choice == '6': export_full_log()
        elif choice == '7': remove_game()
        elif choice == '8': break

if __name__ == "__main__":
    main()