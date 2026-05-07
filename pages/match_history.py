import streamlit as st
import sqlite3
import pandas as pd

import streamlit as st
import sqlite3
import pandas as pd

def get_match_history():
    conn = sqlite3.connect("mtg_stats.db")
    query = """
        SELECT g.game_number, g.game_date, g.first_blood_turn, g.end_turn, g.win_condition,
               p.player_name, d.deck_name, part.is_winner, part.turn_order
        FROM games g
        JOIN participants part ON g.game_id = part.game_id
        JOIN players p ON part.player_id = p.player_id
        JOIN decks d ON part.deck_id = d.deck_id
        ORDER BY g.game_number DESC, part.turn_order ASC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def highlight_winner(row):
    if row['Result'] == "🏆 Winner":
        return ['background-color: rgba(255, 215, 0, 0.2); font-weight: bold'] * len(row)
    return [''] * len(row)

def run():
    st.title("📜 Complete Match History")
    
    df = get_match_history()
    if df.empty:
        st.warning("No games found.")
        return

    # Sidebar Filter (Kept this because it's handy for 140+ games)
    st.sidebar.header("Search")
    search_player = st.sidebar.text_input("Filter by Player Name")
    
    if search_player:
        valid_games = df[df['player_name'].str.contains(search_player, case=False)]['game_number'].unique()
        display_df = df[df['game_number'].isin(valid_games)]
    else:
        display_df = df

    unique_games = display_df['game_number'].unique()

    # --- THE FLAT LAYOUT ---
    for g_num in unique_games:
        game_data = display_df[display_df['game_number'] == g_num]
        meta = game_data.iloc[0]
        
        # Determine Winner Name for the header
        winner_row = game_data[game_data['is_winner'] == 1]
        winner_name = winner_row['player_name'].iloc[0] if not winner_row.empty else "Draw"

        # Game Header - No expander, just a bold sub-header
        st.subheader(f"Game #{g_num} — {meta['game_date']}")
        
        # Meta info in a single line to save vertical space
        st.markdown(f"**Winner:** {winner_name} | **FB Turn:** {meta['first_blood_turn']} | **End Turn:** {meta['end_turn']} | **Win Con:** {meta['win_condition']}")

        # Table Prep
        table_data = game_data[['turn_order', 'player_name', 'deck_name', 'is_winner']].copy()
        table_data['is_winner'] = table_data['is_winner'].apply(lambda x: "🏆 Winner" if x == 1 else "---")
        table_data.columns = ['Turn', 'Player', 'Deck', 'Result']

        # Apply Styling
        styled_table = table_data.style.apply(highlight_winner, axis=1)

        # Display full table (no scrolling/hiding)
        st.table(styled_table)
        
        # Strong visual break between matches
        st.markdown("---")

if __name__ == "__main__":
    run()