import sqlite3

def find_misnamed_entry():
    conn = sqlite3.connect("mtg_stats.db")
    cursor = conn.cursor()
    
    # We use a partial search (LIKE) to find that misnamed deck
    search_term = input("Enter the 'misnamed' deck name you see on the site: ")
    
    query = """
        SELECT g.game_id, g.game_date, p.player_name, d.deck_name
        FROM participants part
        JOIN games g ON part.game_id = g.game_id
        JOIN players p ON part.player_id = p.player_id
        JOIN decks d ON part.deck_id = d.deck_id
        WHERE d.deck_name LIKE ?
    """
    
    cursor.execute(query, (f'%{search_term}%',))
    results = cursor.fetchall()
    
    if results:
        print(f"\nFound {len(results)} matching entries:")
        print(f"{'Game ID':<8} | {'Date':<12} | {'Player':<12} | {'Deck Name'}")
        print("-" * 50)
        for row in results:
            print(f"{row[0]:<8} | {row[1]:<12} | {row[2]:<12} | {row[3]}")
    else:
        print("No games found with that deck name.")
    
    conn.close()

if __name__ == "__main__":
    find_misnamed_entry()