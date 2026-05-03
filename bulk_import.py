import sqlite3
import csv
from datetime import datetime

DB_NAME = "mtg_stats.db"

def get_or_create_id(cursor, table, col, val, owner_id=None):
    if not val or str(val).strip() == "":
        return None
    
    val = val.strip()
    cursor.execute(f"SELECT {table[:-1]}_id FROM {table} WHERE {col} = ?", (val,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    if table == "players":
        cursor.execute("INSERT INTO players (player_name) VALUES (?)", (val,))
    elif table == "decks":
        cursor.execute("INSERT INTO decks (deck_name, player_id) VALUES (?, ?)", (val, owner_id))
    
    return cursor.lastrowid

def migrate_data(csv_file):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        with open(csv_file, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 1. Format the Date (Converts 11/15/2025 to 2025-11-15)
                raw_date = row['Post date']
                date_obj = datetime.strptime(raw_date, '%m/%d/%Y')
                formatted_date = date_obj.strftime('%Y-%m-%d')

                # 2. Insert the Game
                cursor.execute("""
                    INSERT INTO games (game_date, first_blood_turn, end_turn, win_condition)
                    VALUES (?, ?, ?, ?)
                """, (formatted_date, row['First Blood'], row['Ended On'], row['Win Con']))
                game_id = cursor.lastrowid

                # 3. Determine Winner Slot (e.g., "Player 1" -> index 1)
                winner_slot_str = row['Winner Player'].replace('Player ', '')
                winner_index = int(winner_slot_str) if winner_slot_str.isdigit() else 0

                # 4. Process all 5 possible player slots
                for i in range(1, 6):
                    p_name = row.get(f'Player {i}')
                    d_name = row.get(f'Deck {i}')
                    
                    if not p_name or p_name.strip() == "":
                        continue

                    p_id = get_or_create_id(cursor, "players", "player_name", p_name)
                    d_id = get_or_create_id(cursor, "decks", "deck_name", d_name, p_id)
                    
                    is_winner = 1 if i == winner_index else 0

                    cursor.execute("""
                        INSERT INTO participants (player_id, game_id, deck_id, is_winner, turn_order)
                        VALUES (?, ?, ?, ?, ?)
                    """, (p_id, game_id, d_id, is_winner, i))

        conn.commit()
        print(f"Successfully migrated {reader.line_num - 1} games!")
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_data('mtg_data.csv') # Ensure your file is named this 