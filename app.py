import streamlit as st
import pandas as pd
import sqlite3

def get_connection():
    return sqlite3.connect("mtg_stats.db")

# --- PAGE 1: OVERALL LEADERBOARD ---
def show_leaderboard():
    st.title("🏆 Group Standings")
    conn = get_connection()
    query = """
    SELECT p.player_name, COUNT(part.participant_id) as games, SUM(part.is_winner) as wins
    FROM players p
    JOIN participants part ON p.player_id = part.player_id
    GROUP BY p.player_name
    """
    df = pd.read_sql(query, conn)
    df['win_rate'] = (df['wins'] / df['games'] * 100).round(1)
    conn.close()

    # Display Metrics
    cols = st.columns(len(df))
    for i, row in df.iterrows():
        cols[i].metric(row['player_name'], f"{row['win_rate']}%")
    
    st.dataframe(df.sort_values('win_rate', ascending=False), use_container_width=True)

# --- PAGE 2: DECK STATS ---
def show_deck_stats():
    st.title("🎴 Deck Performance")
    conn = get_connection()
    
    # 1. Let the user pick a player first
    players = pd.read_sql("SELECT player_name FROM players", conn)['player_name'].tolist()
    selected_player = st.selectbox("Select a Player", players)
    
    # 2. Query stats for that player's specific decks
    query = """
    SELECT d.deck_name, COUNT(part.participant_id) as games, SUM(part.is_winner) as wins
    FROM decks d
    JOIN participants part ON d.deck_id = part.deck_id
    JOIN players p ON d.player_id = p.player_id
    WHERE p.player_name = ?
    GROUP BY d.deck_name
    HAVING games > 0
    """
    deck_df = pd.read_sql(query, conn, params=(selected_player,))
    conn.close()
    
    if not deck_df.empty:
        deck_df['win_rate'] = (deck_df['wins'] / deck_df['games'] * 100).round(1)
        st.subheader(f"Decks played by {selected_player}")
        st.dataframe(deck_df.sort_values('win_rate', ascending=False), use_container_width=True)
    else:
        st.info("No decks found for this player.")

# --- SIDEBAR NAVIGATION ---
st.header.title("Navigation")
page = st.sidebar.radio("Go to", ["Leaderboard", "Deck Stats"])

if page == "Leaderboard":
    show_leaderboard()
else:
    show_deck_stats()