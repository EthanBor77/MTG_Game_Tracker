import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Deck Stats", layout="wide")
st.title("🎴 Individual Deck Performance")

def get_deck_data(player_name):
    conn = sqlite3.connect("mtg_stats.db")
    # We join participants to players to ensure we are looking at 
    # the person who actually sat in the seat for that game.
    query = """
        SELECT 
            d.deck_name, 
            COUNT(part.participant_id) as games, 
            SUM(part.is_winner) as wins
        FROM participants part
        JOIN players p ON part.player_id = p.player_id
        JOIN decks d ON part.deck_id = d.deck_id
        WHERE p.player_name = ?
        GROUP BY d.deck_name
        HAVING games > 0
    """
    df = pd.read_sql(query, conn, params=(player_name,))
    conn.close()
    
    if not df.empty:
        # Standardizing the win rate calculation
        df['win_rate'] = (df['wins'] / df['games'] * 100).round(1)
        # Rename columns for a cleaner Streamlit UI
        df.columns = ['Deck Name', 'Games Played', 'Total Wins', 'Win Rate %']
    return df

# Dropdown to select player
conn = sqlite3.connect("mtg_stats.db")
player_list = pd.read_sql("SELECT player_name FROM players", conn)['player_name'].tolist()
conn.close()

selected_player = st.selectbox("Select a Player to see their decks:", player_list)

if selected_player:
    deck_stats = get_deck_data(selected_player)
    if not deck_stats.empty:
        # 1. Change sort target to 'Games Played'
        # Set ascending=False to show the most played decks at the top
        sorted_stats = deck_stats.sort_values('Games Played', ascending=False)
        
        # 2. Apply the style for the Win Rate % column
        styled_stats = sorted_stats.style.format({
            'Win Rate %': '{:.2f}%'
        })
        
        # 3. Display the dataframe with the new width parameter
        st.dataframe(
            styled_stats, 
            width="stretch", 
            hide_index=True
        )
    else:
        st.info(f"No game data found for decks owned by {selected_player}.")