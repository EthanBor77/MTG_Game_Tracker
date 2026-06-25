import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="MTG Stats - Decks", layout="wide")
st.title("🎴 Individual Deck Performance")

def get_player_overview_metrics(player_name):
    """Fetches high-level summary metrics for a given player."""
    conn = sqlite3.connect("mtg_stats.db")
    cursor = conn.cursor()
    
    # 1. Total Games Logged & Unique Decks Played
    cursor.execute("""
        SELECT COUNT(part.participant_id), COUNT(DISTINCT part.deck_id)
        FROM participants part
        JOIN players p ON part.player_id = p.player_id
        WHERE p.player_name = ?
    """, (player_name,))
    games_logged, decks_played = cursor.fetchone()
    
    # 2. Total Different Decks Owned (Registered in the decks table)
    cursor.execute("""
        SELECT COUNT(d.deck_id)
        FROM decks d
        JOIN players p ON d.player_id = p.player_id
        WHERE p.player_name = ?
    """, (player_name,))
    decks_owned = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "games_logged": games_logged if games_logged else 0,
        "decks_owned": decks_owned if decks_owned else 0,
        "decks_played": decks_played if decks_played else 0
    }

def get_deck_data(player_name):
    conn = sqlite3.connect("mtg_stats.db")
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
        df['win_rate'] = (df['wins'] / df['games'] * 100).round(1)
        df.columns = ['Deck Name', 'Games Played', 'Total Wins', 'Win Rate %']
    return df

# Dropdown to select player
conn = sqlite3.connect("mtg_stats.db")
player_list = pd.read_sql("SELECT player_name FROM players", conn)['player_name'].tolist()
conn.close()

selected_player = st.selectbox("Select a Player to see their decks:", player_list)

if selected_player:
    # Fetch and render the new high-level stat row
    metrics = get_player_overview_metrics(selected_player)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Games Logged", value=metrics["games_logged"])
    with col2:
        st.metric(label="Decks Owned", value=metrics["decks_owned"])
    with col3:
        st.metric(label="Decks Played", value=metrics["decks_played"])
        
    st.divider() # Clean separation line between metrics and the data table

    # Render Deck Breakdown Table
    deck_stats = get_deck_data(selected_player)
    if not deck_stats.empty:
        sorted_stats = deck_stats.sort_values('Games Played', ascending=False)
        
        styled_stats = sorted_stats.style.format({
            'Win Rate %': '{:.2f}%'
        })
        
        st.dataframe(
            styled_stats, 
            width="stretch", 
            hide_index=True
        )
    else:
        st.info(f"No game data found for decks owned by {selected_player}.")