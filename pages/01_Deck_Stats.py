import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Deck Stats", layout="wide")
st.title("🎴 Individual Deck Performance")

def get_deck_data(player_name):
    conn = sqlite3.connect("mtg_stats.db")
    query = """
        SELECT d.deck_name, 
               COUNT(part.participant_id) as games, 
               SUM(part.is_winner) as wins
        FROM decks d
        JOIN participants part ON d.deck_id = part.deck_id
        JOIN players p ON d.player_id = p.player_id
        WHERE p.player_name = ?
        GROUP BY d.deck_name
        HAVING games > 0
    """
    df = pd.read_sql(query, conn, params=(player_name,))
    conn.close()
    if not df.empty:
        df['win_rate'] = (df['wins'] / df['games'] * 100).round(1)
    return df

# Dropdown to select player
conn = sqlite3.connect("mtg_stats.db")
player_list = pd.read_sql("SELECT player_name FROM players", conn)['player_name'].tolist()
conn.close()

selected_player = st.selectbox("Select a Player to see their decks:", player_list)

if selected_player:
    deck_stats = get_deck_data(selected_player)
    if not deck_stats.empty:
        st.dataframe(deck_stats.sort_values('win_rate', ascending=False), 
                     use_container_width=True, hide_index=True)
    else:
        st.info(f"No game data found for decks owned by {selected_player}.")